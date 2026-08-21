"""Adapter around the REAL FairDispatch simulator/policy engine.

Imports simulator.py / policies.py directly from the bundle's own source
copy -- does not reimplement scoring or matching. `run_simulation_batched`
in simulator.py runs its whole `while` loop in one call with no way to
pause between windows, so SimulationSession below re-orchestrates that
SAME loop one window at a time (calling the real feasible_drivers(),
commit_trip(), policy.select_batch(), policy.on_committed() at each step)
so the product can expose a genuine Step control. The algorithm itself
(who gets matched to whom, and why) is untouched.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from collections import OrderedDict

import paths

sys.path.insert(0, str(paths.SRC_DIR))
from simulator import (  # noqa: E402
    SimResult, init_drivers, feasible_drivers, commit_trip,
    COST_PER_SECOND_DEADHEAD_USD, MAX_PICKUP_ETA_SECONDS,
)
from policies import ALL_POLICIES, MOMAQLPolicy  # noqa: E402

import pyarrow.parquet as pq  # noqa: E402


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


_REQUEST_CACHE: dict[str, list[dict]] = {}
_REQUEST_T0_CACHE: dict[str, int] = {}  # dataset -> real Unix epoch seconds of its first pickup_ts

VALID_DATASETS = {"val", "train", "test"}


def get_dataset_t0(dataset: str) -> int:
    """Real Unix epoch seconds that pickup_ts=0 (i.e. window_start_seconds=0)
    corresponds to for this dataset -- lets the frontend show the actual
    calendar date/time from the NYC TLC data instead of a relative
    "Day N" counter. Populated as a side effect of load_requests()."""
    if dataset not in _REQUEST_T0_CACHE:
        load_requests(dataset, None)
    return _REQUEST_T0_CACHE[dataset]


def load_requests(dataset: str, limit: int | None) -> list[dict]:
    """Same field extraction as common_loader.load_requests_fast, cached
    per dataset name per process (parquet parse is the expensive part)."""
    if dataset not in _REQUEST_CACHE:
        path = paths.PARQUET_DATA_DIR / f"{dataset}.parquet"
        if not path.exists():
            raise FileNotFoundError(
                f"Khong tim thay {path}. Live simulation can file parquet that tu repo dev "
                f"fairdispatch_v3_clean/data/ (khong copy vao goi nop vi qua lon ~50-225MB moi file). "
                f"Neu repo dev o vi tri khac, dat bien moi truong FAIRDISPATCH_DEV_REPO."
            )
        table = pq.read_table(path, columns=[
            "pickup_ts", "pickup_latitude", "pickup_longitude",
            "dropoff_latitude", "dropoff_longitude", "fare_amount",
            "duration_seconds", "pickup_zone_id", "dropoff_zone_id",
        ])
        p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
        abs_sec = p_ts.astype("datetime64[s]").astype("int64")
        t0 = abs_sec[0]
        _REQUEST_T0_CACHE[dataset] = int(t0)
        ts_rel = (abs_sec - t0).astype(float)
        p_lat = table["pickup_latitude"].to_numpy()
        p_lon = table["pickup_longitude"].to_numpy()
        d_lat = table["dropoff_latitude"].to_numpy()
        d_lon = table["dropoff_longitude"].to_numpy()
        fares = table["fare_amount"].to_numpy()
        durs = table["duration_seconds"].to_numpy()
        p_hours = ((abs_sec // 3600) % 24).astype(int)
        d_hours = (((abs_sec + durs.astype("int64")) // 3600) % 24).astype(int)
        # 1970-01-01 (epoch day 0) was a Thursday -- weekday index 3 in a
        # Monday=0..Sunday=6 convention, hence the "+3" offset. Real
        # timestamp-derived weekday, not a guessed/hard-coded row index.
        p_weekday = (((abs_sec // 86400) + 3) % 7).astype(int)
        p_zids = table["pickup_zone_id"].to_pylist()
        z_ids = table["dropoff_zone_id"].to_pylist()
        n = len(p_lat)
        _REQUEST_CACHE[dataset] = [
            {"_idx": i, "pickup_ts": float(ts_rel[i]), "pickup_latitude": float(p_lat[i]),
             "pickup_longitude": float(p_lon[i]), "dropoff_latitude": float(d_lat[i]),
             "dropoff_longitude": float(d_lon[i]), "fare_amount": float(fares[i]),
             "duration_seconds": float(durs[i]), "pickup_zone_id": p_zids[i], "dropoff_zone_id": z_ids[i],
             "pickup_hour": int(p_hours[i]), "dropoff_hour": int(d_hours[i]), "pickup_weekday": int(p_weekday[i])}
            for i in range(n)
        ]
    reqs = _REQUEST_CACHE[dataset]
    return reqs[:limit] if limit else reqs


def _hour_in_time_filter(hour: int, time_filter: dict | None) -> bool:
    if not time_filter or time_filter.get("mode", "all") == "all":
        return True
    start, end = time_filter.get("start_hour"), time_filter.get("end_hour")
    if start is None or end is None:
        return True
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end  # overnight wrap, e.g. 22..5


def _weekday_in_day_filter(weekday: int, day_filter: dict | None) -> bool:
    if not day_filter or day_filter.get("mode", "all") == "all":
        return True
    mode = day_filter.get("mode")
    if mode == "weekday":
        return weekday <= 4
    if mode == "weekend":
        return weekday >= 5
    days = day_filter.get("days")
    if days:
        return weekday in days
    return True


def apply_scenario_filters(requests: list[dict], time_filter: dict | None, day_filter: dict | None) -> list[dict]:
    """Filters the REAL cached request set by real pickup_hour/pickup_weekday.
    Order matters: must run BEFORE request_limit slicing (see SimulationSession
    -- otherwise a narrow time/day scenario could see almost no requests
    just because they all got cut off by an unrelated slice-first limit)."""
    if (not time_filter or time_filter.get("mode", "all") == "all") and \
       (not day_filter or day_filter.get("mode", "all") == "all"):
        return requests
    return [r for r in requests if _hour_in_time_filter(r["pickup_hour"], time_filter)
            and _weekday_in_day_filter(r["pickup_weekday"], day_filter)]


_Q_TABLE_CACHE: dict | None = None


def load_trained_q_table() -> dict:
    global _Q_TABLE_CACHE
    if _Q_TABLE_CACHE is None:
        path = paths.BUNDLE_DATA_DIR / "momaql_q_table_trained.json"
        with path.open("r", encoding="utf-8") as f:
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
        errors.append(f"policy '{policy}' khong hop le. Cac policy ho tro: {list(ALL_POLICIES)}")
    if dataset not in VALID_DATASETS:
        errors.append(f"dataset '{dataset}' khong hop le. Ho tro: {sorted(VALID_DATASETS)}")
    if n_drivers is None or n_drivers <= 0:
        errors.append("n_drivers phai > 0")
    if request_limit is not None and request_limit <= 0:
        errors.append("request_limit phai > 0")
    if lam is None or not (0.0 <= lam <= 1.0):
        errors.append("lambda phai trong [0, 1]")
    if gamma is None or not (0.0 <= gamma <= 1.0):
        errors.append("gamma phai trong [0, 1]")
    if alpha is None or not (0.0 < alpha <= 1.0):
        errors.append("alpha phai trong (0, 1]")
    return errors


def score_breakdown(policy, policy_name: str, d, req, dist, eta, mean_income, driver_income: float):
    """Real per-candidate score, taken verbatim from the exact score_fn each
    policy uses inside select_batch() -- not recomputed with a different
    formula. For MOMAQL, decomposes policy._score()'s own real return value
    into its three real weighted terms (they sum exactly to final_score).

    driver_income is passed in explicitly (a snapshot taken at the moment
    select_batch() actually scored this window) rather than read live off
    `d`, because `d` is the SAME mutable Driver object select_batch scored
    against -- if this driver was already committed to an EARLIER request
    within the same batch before the caller asks to explain a LATER one,
    `d.total_income` would already reflect that commit and silently show a
    score that was never the one actually computed at decision time."""
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
    using the real feasible_drivers/commit_trip/select_batch functions."""

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
        # Filter order matters (PHASE 3 requirement): load the FULL cached
        # dataset, apply day/time scenario filter, THEN slice request_limit
        # -- never slice-first, or a narrow scenario could see near-zero
        # requests just because they got cut off by an unrelated limit.
        all_requests = load_requests(dataset, None)
        self.available_request_count = len(all_requests)
        filtered = apply_scenario_filters(all_requests, time_filter, day_filter)
        self.filtered_request_count = len(filtered)
        if not filtered:
            raise ValueError("No requests match selected scenario (time/day filter qua hep).")
        self.requests = filtered[:request_limit] if request_limit else filtered
        if not self.requests:
            raise ValueError(f"Dataset '{dataset}' rong hoac request_limit=0.")
        self.n = len(self.requests)
        self._lock = threading.Lock()  # defense-in-depth: reject overlapping step() calls
        self._build()

    def _build(self):
        self.policy = make_policy(self.policy_name, self.lam, self.gamma, self.alpha, self.forecast_on)
        # init_drivers() itself caps to min(n_drivers, len(requests)) -- expose
        # the ACTUAL count used so the UI never silently shows a requested
        # number the engine did not really initialize.
        self.drivers = init_drivers(self.n_drivers_requested, self.requests, self.seed)
        self.n_drivers_actual = len(self.drivers)
        self.policy.on_start(self.drivers)
        self.result = SimResult(per_driver_income={d.driver_id: 0.0 for d in self.drivers},
                                 total_requests=self.n)
        self.i = 0
        self.batch_count = 0
        self.done = False
        # Ring buffer of recent windows -- the frontend now runs a continuous
        # playback clock and prefetches a few batches ahead, so "Why this
        # driver?" for a batch that is still visually playing (not the very
        # latest fetched one) must still be explainable. Keyed by batch
        # number; oldest evicted once beyond MAX_WINDOW_HISTORY.
        self.window_history: "OrderedDict[int, dict]" = OrderedDict()
        self.MAX_WINDOW_HISTORY = 32

    def reset(self):
        with self._lock:
            self._build()

    def step(self) -> dict:
        if not self._lock.acquire(blocking=False):
            raise RuntimeError("Mot step khac dang chay tren run nay -- doi step truoc hoan tat.")
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
        feasible_driver_ids = set()  # UNIQUE drivers, never the sum of per-request candidate edges
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
        # Snapshot BEFORE any commit_trip() in this window mutates driver
        # state -- see score_breakdown()'s docstring for why explain() must
        # not read live d.total_income after the batch has been committed.
        income_snapshot = {d.driver_id: d.total_income for d in self.drivers}

        assigned_out = []
        declined_out = []
        selected_by_req = {}  # req_idx -> driver_id or None -- the REAL Hungarian outcome
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
        # Sort by score for DISPLAY/ranking only -- this ranking is NOT what
        # picks the winner (see selected_driver_id below, which comes from
        # the real Hungarian joint solve and can legitimately differ from
        # the local top scorer, since Hungarian optimizes the WHOLE batch).
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
