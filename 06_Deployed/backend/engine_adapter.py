"""Adapter around the REAL FairDispatch simulator/policy engine (deployed
bundle). Imports simulator.py / policies.py directly from this bundle's own
engine/src copy -- does not reimplement scoring or matching. Same
window-by-window re-orchestration of run_simulation_batched's loop as the
original product (05_SanPham_Demo) so Step still works; the algorithm itself
is untouched.

DEPLOY-SPECIFIC CHANGES vs 05_SanPham_Demo/backend/engine_adapter.py:
  1. Dataset is the bundled Final Test Evaluation View (data/test_eval.parquet,
     195,506 rows, frozen quality transform already applied) -- not
     val.parquet from a sibling dev repo. Only "test" is a valid dataset name.
  2. Loader is columnar/vectorized (numpy arrays cached once per process).
     Scenario (time/day) filtering is a vectorized boolean mask over those
     arrays; request_limit slicing happens on the resulting eligible index
     array; per-row Python dicts are built ONLY for the selected rows -- never
     195,506 dicts just to serve a 3,000-request live slice.
  3. duration_seconds read from test_eval.parquet is already the frozen
     quality-transform-evaluated value (repaired-from-timestamps where
     needed); pickup_hour/dropoff_hour/pickup_weekday are already columns in
     that parquet (computed once, at build time, by
     scripts/build_test_eval_parquet.py), not recomputed here.
  4. `_idx` keeps the exact same MEANING as the original product: the
     position of a request within the full loaded (pre-filter) array for
     this process, stable for the lifetime of the process -- required for
     cands_map / explain() to keep working unchanged.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from collections import OrderedDict

import numpy as np
import pyarrow.parquet as pq

import paths

sys.path.insert(0, str(paths.SRC_DIR))
from simulator import (  # noqa: E402
    SimResult, init_drivers, feasible_drivers, commit_trip,
    COST_PER_SECOND_DEADHEAD_USD, MAX_PICKUP_ETA_SECONDS,
)
from policies import ALL_POLICIES, MOMAQLPolicy  # noqa: E402


def gini(values):
    xs = sorted(v for v in values if v >= 0)
    n = len(xs)
    if n == 0:
        return 0.0
    s = sum(xs)
    if s == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * s) - (n + 1) / n


def variance(values):
    m = sum(values) / len(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def lorenz_points(values):
    """Standard Lorenz curve: cumulative share of population (x) vs
    cumulative share of income (y), computed from real driver incomes.
    Generic textbook formula, no borrowed logic/data."""
    xs = sorted(v for v in values if v >= 0)
    n = len(xs)
    if n == 0:
        return [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 1.0}]
    total = sum(xs)
    pts = [{"x": 0.0, "y": 0.0}]
    cum = 0.0
    for i, v in enumerate(xs):
        cum += v
        pts.append({"x": (i + 1) / n, "y": (cum / total) if total > 0 else (i + 1) / n})
    return pts


VALID_DATASETS = {"test"}  # deployed bundle ships ONLY the Final Test Evaluation View

_COLUMN_CACHE: dict | None = None


def _load_columns() -> dict:
    """Reads data/test_eval.parquet ONCE per process into compact numpy
    columns (no per-row Python dicts here). ~195k rows x 13 numeric/short
    columns is a few tens of MB as numpy arrays -- far cheaper than 195,506
    Python dict objects."""
    global _COLUMN_CACHE
    if _COLUMN_CACHE is None:
        path = paths.TEST_EVAL_PARQUET
        if not path.exists():
            raise FileNotFoundError(
                f"Khong tim thay {path}. Chay scripts/build_test_eval_parquet.py truoc khi start server."
            )
        table = pq.read_table(path)
        abs_pickup = table["pickup_ts"].to_numpy(zero_copy_only=False).astype("datetime64[s]").astype("int64")
        t0 = int(abs_pickup[0])
        cols = {
            "pickup_ts_rel": (abs_pickup - t0).astype(float),
            "pickup_latitude": table["pickup_latitude"].to_numpy(),
            "pickup_longitude": table["pickup_longitude"].to_numpy(),
            "dropoff_latitude": table["dropoff_latitude"].to_numpy(),
            "dropoff_longitude": table["dropoff_longitude"].to_numpy(),
            "fare_amount": table["fare_amount"].to_numpy(),
            "duration_seconds": table["duration_seconds"].to_numpy(),
            "pickup_zone_id": table["pickup_zone_id"].to_numpy(),
            "dropoff_zone_id": table["dropoff_zone_id"].to_numpy(),
            "pickup_hour": table["pickup_hour"].to_numpy(),
            "dropoff_hour": table["dropoff_hour"].to_numpy(),
            "pickup_weekday": table["pickup_weekday"].to_numpy(),
        }
        _COLUMN_CACHE = {"t0": t0, "n": len(abs_pickup), "cols": cols}
    return _COLUMN_CACHE


def get_dataset_t0(dataset: str) -> int:
    """Real Unix epoch seconds that pickup_ts=0 corresponds to -- lets the
    frontend show the actual calendar date/time from the NYC TLC data."""
    return _load_columns()["t0"]


def _eligible_indices(time_filter: dict | None, day_filter: dict | None) -> np.ndarray:
    """Vectorized boolean-mask filter over the cached numpy columns. Same
    semantics as engine_adapter.py's _hour_in_time_filter/_weekday_in_day_filter
    (overnight wrap, weekday<=4, weekend>=5, custom days list) -- just
    computed as array ops instead of a per-row Python loop."""
    d = _load_columns()
    n = d["n"]
    mask = np.ones(n, dtype=bool)

    if time_filter and time_filter.get("mode", "all") != "all":
        start, end = time_filter.get("start_hour"), time_filter.get("end_hour")
        if start is not None and end is not None:
            hours = d["cols"]["pickup_hour"]
            if start <= end:
                mask &= (hours >= start) & (hours < end)
            else:  # overnight wrap, e.g. 22..5
                mask &= (hours >= start) | (hours < end)

    if day_filter and day_filter.get("mode", "all") != "all":
        wd = d["cols"]["pickup_weekday"]
        mode = day_filter.get("mode")
        if mode == "weekday":
            mask &= wd <= 4
        elif mode == "weekend":
            mask &= wd >= 5
        else:
            days = day_filter.get("days")
            if days:
                mask &= np.isin(wd, days)

    return np.nonzero(mask)[0]


def _rows_from_indices(indices) -> list[dict]:
    """Builds per-row Python dicts ONLY for the given positional indices --
    the expensive dict-per-row step is deferred until after filter+limit."""
    cols = _load_columns()["cols"]
    return [
        {"_idx": int(i), "pickup_ts": float(cols["pickup_ts_rel"][i]),
         "pickup_latitude": float(cols["pickup_latitude"][i]),
         "pickup_longitude": float(cols["pickup_longitude"][i]),
         "dropoff_latitude": float(cols["dropoff_latitude"][i]),
         "dropoff_longitude": float(cols["dropoff_longitude"][i]),
         "fare_amount": float(cols["fare_amount"][i]),
         "duration_seconds": float(cols["duration_seconds"][i]),
         "pickup_zone_id": int(cols["pickup_zone_id"][i]),
         "dropoff_zone_id": int(cols["dropoff_zone_id"][i]),
         "pickup_hour": int(cols["pickup_hour"][i]), "dropoff_hour": int(cols["dropoff_hour"][i]),
         "pickup_weekday": int(cols["pickup_weekday"][i])}
        for i in indices
    ]


_Q_TABLE_CACHE: dict | None = None


def load_trained_q_table() -> dict:
    global _Q_TABLE_CACHE
    if _Q_TABLE_CACHE is None:
        with paths.Q_TABLE_PATH.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        _Q_TABLE_CACHE = {int(k) if k.isdigit() else k: float(v) for k, v in raw.items()}
    return _Q_TABLE_CACHE


def make_policy(name: str, lam: float, gamma: float, alpha: float, forecast_on: bool):
    if name == "MOMAQL":
        q = load_trained_q_table() if forecast_on else {}
        ablation = "full" if forecast_on else "no_forecast"
        return MOMAQLPolicy(lam=lam, gamma=gamma, alpha=alpha, q_table=q, frozen=True, ablation=ablation)
    cls = ALL_POLICIES.get(name)
    if cls is None:
        raise ValueError(f"Unknown policy: {name}. Available: {list(ALL_POLICIES)}")
    return cls()


def validate_config(policy, n_drivers, lam, gamma, alpha, request_limit, dataset):
    errors = []
    if policy not in ALL_POLICIES:
        errors.append(f"policy '{policy}' không hợp lệ. Các policy hỗ trợ: {list(ALL_POLICIES)}")
    if dataset not in VALID_DATASETS:
        errors.append(f"dataset '{dataset}' không hợp lệ. Bản deploy này chỉ hỗ trợ: {sorted(VALID_DATASETS)} "
                       f"(Tập kiểm thử cuối đã chuẩn hóa).")
    if n_drivers is None or n_drivers <= 0:
        errors.append("n_drivers phải > 0")
    if request_limit is not None and request_limit <= 0:
        errors.append("request_limit phải > 0")
    if lam is None or not (0.0 <= lam <= 1.0):
        errors.append("lambda phải trong [0, 1]")
    if gamma is None or not (0.0 <= gamma <= 1.0):
        errors.append("gamma phải trong [0, 1]")
    if alpha is None or not (0.0 < alpha <= 1.0):
        errors.append("alpha phải trong (0, 1]")
    return errors


def score_breakdown(policy, policy_name: str, d, req, dist, eta, mean_income, driver_income: float):
    """Real per-candidate score, taken verbatim from the exact score_fn each
    policy uses inside select_batch() -- not recomputed with a different
    formula. Identical to 05_SanPham_Demo's version (no engine change)."""
    fare = req["fare_amount"]
    deadhead_cost = eta * COST_PER_SECOND_DEADHEAD_USD
    if policy_name == "MOMAQL":
        D_zone = req.get("dropoff_zone_id")
        D_hour = req.get("dropoff_hour")
        q_future = 0.0 if policy.ablation == "no_forecast" else policy.Q.get((D_zone, D_hour), 0.0)
        rel_fairness = (mean_income - driver_income) / max(mean_income, 1.0)
        fairness = rel_fairness * fare
        immediate = (1 - policy.lam) * (fare - deadhead_cost)
        future = (1 - policy.lam) * policy.gamma * q_future
        fair_adj = policy.lam * fairness
        return {
            "immediate_utility": immediate, "future_zone_value": future,
            "fairness_adjustment": fair_adj, "final_score": immediate + future + fair_adj,
            "q_future_raw": q_future, "rel_fairness": rel_fairness,
        }
    if policy_name == "Greedy":
        return {"final_score": fare, "formula": "score = fare_amount"}
    if policy_name == "Nearest":
        score = (MAX_PICKUP_ETA_SECONDS - eta) * COST_PER_SECOND_DEADHEAD_USD
        return {"final_score": score, "formula": "score = (600 - eta_seconds) * 0.0025"}
    if policy_name == "LAF":
        rel_fairness = (mean_income - driver_income) / max(mean_income, 1.0)
        return {"final_score": rel_fairness * fare, "rel_fairness": rel_fairness,
                "formula": "score = rel_fairness * fare"}
    if policy_name == "Exact REASSIGN":
        return {"final_score": fare - deadhead_cost, "formula": "score = fare - deadhead_cost"}
    return {"final_score": None}


class SimulationSession:
    """One live, step-able run. Holds real Driver objects and a real
    policy instance; step() advances exactly one WINDOW_SECONDS batch
    using the real feasible_drivers/commit_trip/select_batch functions.
    Unchanged from 05_SanPham_Demo except how self.requests is built (see
    module docstring)."""

    WINDOW_SECONDS = 60.0

    def __init__(self, run_id, dataset, n_drivers, seed, policy_name, lam, gamma, alpha,
                 forecast_on, request_limit, time_filter=None, day_filter=None):
        errors = validate_config(policy_name, n_drivers, lam, gamma, alpha, request_limit, dataset)
        if errors:
            raise ValueError("; ".join(errors))
        self.run_id = run_id
        self.dataset = dataset
        self.n_drivers_requested = n_drivers
        self.seed = seed
        self.policy_name = policy_name
        self.lam = lam
        self.gamma = gamma
        self.alpha = alpha
        self.forecast_on = forecast_on
        self.request_limit = request_limit
        self.time_filter = time_filter
        self.day_filter = day_filter
        self.created_at = time.time()
        self.t0_epoch_seconds = get_dataset_t0(dataset)

        d = _load_columns()
        self.available_request_count = d["n"]
        # Filter order matters (unchanged requirement): eligible mask THEN
        # request_limit slice -- never slice-first, or a narrow scenario
        # could see near-zero requests just because they got cut off by an
        # unrelated slice-first limit.
        eligible = _eligible_indices(time_filter, day_filter)
        self.filtered_request_count = len(eligible)
        if len(eligible) == 0:
            raise ValueError("Không có yêu cầu chuyến nào khớp với kịch bản đã chọn (bộ lọc giờ/ngày quá hẹp).")
        selected = eligible[:request_limit] if request_limit else eligible
        if len(selected) == 0:
            raise ValueError(f"Dataset '{dataset}' rỗng hoặc request_limit=0.")
        self.requests = _rows_from_indices(selected)  # dicts built ONLY for selected rows
        self.n = len(self.requests)
        self._lock = threading.Lock()  # defense-in-depth: reject overlapping step() calls
        self._build()

    def _build(self):
        self.policy = make_policy(self.policy_name, self.lam, self.gamma, self.alpha, self.forecast_on)
        self.drivers = init_drivers(self.n_drivers_requested, self.requests, self.seed)
        self.n_drivers_actual = len(self.drivers)
        self.policy.on_start(self.drivers)
        self.result = SimResult(per_driver_income={d.driver_id: 0.0 for d in self.drivers},
                                 total_requests=self.n)
        self.i = 0
        self.batch_count = 0
        self.done = False
        self.window_history: "OrderedDict[int, dict]" = OrderedDict()
        self.MAX_WINDOW_HISTORY = 32

    def reset(self):
        with self._lock:
            self._build()

    def step(self) -> dict:
        if not self._lock.acquire(blocking=False):
            raise RuntimeError("Một bước khác đang chạy trên lần chạy này -- đợi bước trước hoàn tất.")
        try:
            return self._step_locked()
        finally:
            self._lock.release()

    def _step_locked(self) -> dict:
        if self.done or self.i >= self.n:
            self.done = True
            return {"done": True, "batch": self.batch_count}

        window_start = self.requests[self.i]["pickup_ts"]
        window_end = window_start + self.WINDOW_SECONDS
        window_reqs = []
        while self.i < self.n and self.requests[self.i]["pickup_ts"] < window_end:
            window_reqs.append(self.requests[self.i])
            self.i += 1

        cands_map = {}
        feasible_driver_ids = set()
        for req in window_reqs:
            cands = feasible_drivers(self.drivers, req, window_start)
            if cands:
                cands_map[req["_idx"]] = (req, cands)
                for d, _dist, _eta in cands:
                    feasible_driver_ids.add(d.driver_id)
        infeasible_out = [
            {"req_idx": r["_idx"], "pickup_lat": r["pickup_latitude"], "pickup_lon": r["pickup_longitude"],
             "pickup_zone": r.get("pickup_zone_id")}
            for r in window_reqs if r["_idx"] not in cands_map
        ]

        mean_income = self.policy._mean_income() if hasattr(self.policy, "_mean_income") else None
        income_snapshot = {d.driver_id: d.total_income for d in self.drivers}

        assigned_out = []
        declined_out = []
        selected_by_req = {}
        if cands_map:
            assignments = self.policy.select_batch(cands_map, window_start)
            used_drivers = set()
            for req_idx, chosen in assignments.items():
                if chosen is None:
                    selected_by_req[req_idx] = None
                    req, _ = cands_map[req_idx]
                    declined_out.append({
                        "req_idx": req_idx, "pickup_lat": req["pickup_latitude"],
                        "pickup_lon": req["pickup_longitude"], "pickup_zone": req.get("pickup_zone_id"),
                    })
                    continue
                d, dist, eta = chosen
                if d.driver_id in used_drivers:
                    continue
                used_drivers.add(d.driver_id)
                selected_by_req[req_idx] = d.driver_id
                driver_start_lat, driver_start_lon = d.lat, d.lon
                req, _ = cands_map[req_idx]
                commit_trip(d, req, dist, eta, window_start, self.result, record_trace=False)
                self.policy.on_committed(d, req, dist, eta, window_start)
                assigned_out.append({
                    "req_idx": req_idx, "driver_id": d.driver_id, "fare": req["fare_amount"],
                    "pickup_zone": req.get("pickup_zone_id"), "dropoff_zone": req.get("dropoff_zone_id"),
                    "driver_start_lat": driver_start_lat, "driver_start_lon": driver_start_lon,
                    "pickup_lat": req["pickup_latitude"], "pickup_lon": req["pickup_longitude"],
                    "dropoff_lat": req["dropoff_latitude"], "dropoff_lon": req["dropoff_longitude"],
                    "deadhead_miles": dist, "pickup_eta_seconds": eta,
                    "duration_seconds": req["duration_seconds"],
                })

        self.batch_count += 1
        incomes = [d.total_income for d in self.drivers]
        self.done = self.i >= self.n
        self.window_history[self.batch_count] = {
            "cands_map": cands_map, "mean_income": mean_income, "income_snapshot": income_snapshot,
            "selected_by_req": selected_by_req, "window_start": window_start,
        }
        if len(self.window_history) > self.MAX_WINDOW_HISTORY:
            self.window_history.popitem(last=False)

        return {
            "done": self.done,
            "batch": self.batch_count,
            "window_start_seconds": window_start,
            "day": window_start / 86400.0,
            "requests_arrived": len(window_reqs),
            "feasible_requests": len(cands_map),
            "feasible_drivers_unique": len(feasible_driver_ids),
            "infeasible_requests": infeasible_out,
            "assigned": len(assigned_out),
            "declined": len(declined_out),
            "assignments": assigned_out,
            "declined_requests": declined_out,
            "drivers": [
                {"driver_id": d.driver_id, "lat": d.lat, "lon": d.lon, "income": d.total_income,
                 "trips": d.total_trips, "busy": d.available_at > window_start}
                for d in self.drivers
            ],
            "metrics": {
                "utility": sum(incomes),
                "gini": gini(incomes),
                "variance": variance(incomes),
                "served_total": self.result.total_completed,
                "avg_income": sum(incomes) / len(incomes) if incomes else 0.0,
                "avg_deadhead_cost": (self.result.total_deadhead_cost / self.result.total_completed)
                                      if self.result.total_completed else 0.0,
                "requests_consumed": self.i,
                "requests_total": self.n,
            },
            "income_histogram": _histogram(incomes),
            "lorenz": lorenz_points(incomes),
        }

    def explain(self, req_idx: int, batch: int | None = None):
        key = batch if batch is not None else next(reversed(self.window_history), None)
        window = self.window_history.get(key) if key is not None else None
        if not window or req_idx not in window["cands_map"]:
            return None
        req, cands = window["cands_map"][req_idx]
        mean_income = window["mean_income"]
        income_snapshot = window["income_snapshot"]
        selected_driver_id = window["selected_by_req"].get(req_idx)
        scored = []
        for d, dist, eta in cands:
            driver_income = income_snapshot.get(d.driver_id, d.total_income)
            breakdown = score_breakdown(self.policy, self.policy_name, d, req, dist, eta, mean_income, driver_income)
            scored.append({
                "driver_id": d.driver_id, "eta_seconds": eta, "deadhead_miles": dist,
                "driver_income": driver_income, **breakdown,
            })
        scored.sort(key=lambda x: (x["final_score"] if x["final_score"] is not None else -1e18), reverse=True)
        for rank, c in enumerate(scored, start=1):
            c["local_rank"] = rank
            c["is_selected"] = (c["driver_id"] == selected_driver_id)
        return {
            "request": {"req_idx": req_idx, "pickup_zone": req.get("pickup_zone_id"),
                        "dropoff_zone": req.get("dropoff_zone_id"), "fare": req["fare_amount"]},
            "selected_driver_id": selected_driver_id,
            "selected_local_rank": next((c["local_rank"] for c in scored if c["is_selected"]), None),
            "candidates": scored,
        }


def _histogram(values, n_bins=8):
    if not values:
        return {"bins": [], "counts": []}
    lo, hi = min(values), max(values)
    if hi <= lo:
        return {"bins": [lo], "counts": [len(values)]}
    width = (hi - lo) / n_bins
    counts = [0] * n_bins
    for v in values:
        idx = min(n_bins - 1, int((v - lo) / width))
        counts[idx] += 1
    bins = [lo + i * width for i in range(n_bins + 1)]
    return {"bins": bins, "counts": counts}
