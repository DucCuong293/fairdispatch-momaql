"""5 real dispatch policies for the lightweight DES: Greedy, Nearest, LAF,
Exact REASSIGN, MOMAQL. All 5 now share one reference frame -- every policy
solves a REAL joint M-to-N assignment via scipy's Hungarian algorithm
(linear_sum_assignment) over the whole window's (driver x request) matrix,
differing only in score_fn (see each class). This replaces an earlier setup
where Greedy/Nearest/LAF ran a sequential per-request scan (implicitly
serving every request they could) while Exact REASSIGN/MOMAQL alone solved
the joint Hungarian problem with a real "decline" option -- that mismatch
made completed-trip counts incomparable across policies for reasons having
nothing to do with each policy's actual definition.

Batch interface: select_batch(cands_map, now) -> {req_idx: (driver, dist,
eta) or None}, where cands_map = {req_idx: (req, [(driver, dist, eta), ...])}.
run_simulation_batched is the only entry point going forward."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

INFEASIBLE_COST = 1e9


def hungarian_batch_assign(cands_map, score_fn):
    """Real M-to-N joint assignment: maximizes total score_fn(driver, req,
    dist, eta) over the whole window via the Hungarian algorithm. Returns
    {req_idx: (driver, dist, eta) or None}.

    Uses the same dummy-row/dummy-column padding pattern as the project's
    own real p2_08a_r3_reassign_solver.py (Phase 2 Exact REASSIGN solver):
    a plain rectangular cost matrix FORCES exactly min(n_req, n_drv) pairs
    total, with no "decline"/"stay idle" option. Padding to a square
    (n_req+n_drv) x (n_req+n_drv) matrix gives every request/driver a real
    "decline" option, at a fixed cost of 0.0 -- the true opportunity cost
    of not matching (real paper arXiv:2407.17839v1's own formulation is
    max pi(M) - lambda*F(M) s.t. sum_v I_rv <= 1, an INEQUALITY: a request
    is matched to AT MOST one driver, never forced to =1). This makes the
    solve a real maximum-WEIGHT matching, not maximum-cardinality: a pair
    only gets matched when score_fn >= 0 for it, i.e. it is a genuine
    improvement over leaving both sides unmatched. Each score_fn below is
    written so 0 is that policy's real neutral/break-even point (a dynamic
    per-window decline cost was tried instead and forced every feasible
    pair to match regardless of value -- including near the 600s ETA
    cutoff on requests with a very long real duration_seconds -- which
    locks drivers out of the fleet for hours and collapses long-run
    throughput; not what the paper does)."""
    req_idxs = list(cands_map.keys())
    driver_ids = sorted({c[0].driver_id for _, cands in cands_map.values() for c in cands})
    if not req_idxs or not driver_ids:
        return {ri: None for ri in req_idxs}
    driver_pos = {did: i for i, did in enumerate(driver_ids)}

    n_req, n_drv = len(req_idxs), len(driver_ids)
    total = n_req + n_drv
    cost = np.full((total, total), INFEASIBLE_COST)  # real block, filled in below where actually feasible
    cost[:n_req, n_drv:] = 0.0  # request declines to be unmatched
    cost[n_req:, :n_drv] = 0.0  # driver stays idle
    cost[n_req:, n_drv:] = 0.0  # dummy-dummy, never meaningfully used

    cand_lookup = {}  # (req_row, drv_col) -> (driver, dist, eta)
    for row, req_idx in enumerate(req_idxs):
        req, cands = cands_map[req_idx]
        for d, dist, eta in cands:
            col = driver_pos[d.driver_id]
            score = score_fn(d, req, dist, eta)
            cost[row, col] = -score  # Hungarian minimizes; we want to maximize score
            cand_lookup[(row, col)] = (d, dist, eta)

    row_ind, col_ind = linear_sum_assignment(cost)
    assignments = {ri: None for ri in req_idxs}
    for row, col in zip(row_ind, col_ind):
        if row >= n_req or col >= n_drv:
            continue  # dummy row or dummy column -- this request/driver declined
        if cost[row, col] >= INFEASIBLE_COST:
            continue  # forced pairing that was never a real feasible candidate (shouldn't happen post-padding, kept as a guard)
        assignments[req_idxs[row]] = cand_lookup[(row, col)]
    return assignments


class GreedyPolicy:
    """score = fare_amount -- identical across candidates of one request, so
    within a request any feasible driver is equally good; across a window,
    joint Hungarian solve still maximizes how many (and which) requests get
    served, same reference frame as every other policy now."""
    name = "Greedy"

    def on_start(self, drivers):
        pass

    def select(self, req, cands, now):
        return min(cands, key=lambda c: c[0].driver_id)

    def select_batch(self, cands_map, now):
        return hungarian_batch_assign(cands_map, lambda d, req, dist, eta: req["fare_amount"])

    def on_committed(self, d, req, dist, eta, now):
        pass


class NearestPolicy:
    """score = (MAX_PICKUP_ETA_SECONDS - eta) * 0.0025 -- re-centered so 0 is
    the real break-even point (ETA at the feasibility cutoff itself); every
    feasible candidate (eta < cutoff) is strictly positive, so it always
    beats a fixed decline=0.0, and argmax(score) == argmin(ETA) still holds."""
    name = "Nearest"

    def on_start(self, drivers):
        pass

    def select(self, req, cands, now):
        return min(cands, key=lambda c: c[2])

    def select_batch(self, cands_map, now):
        return hungarian_batch_assign(
            cands_map, lambda d, req, dist, eta: (600.0 - eta) * 0.0025)

    def on_committed(self, d, req, dist, eta, now):
        pass


class LAFPolicy:
    """Lowest Accumulated Fare -- score = relative fairness gap * fare, a
    real fairness-first heuristic (argmax(score) == argmin(driver.income)),
    re-centered the same way as MOMAQL's fairness term so 0 is a genuine
    break-even (driver exactly at mean income) rather than an unbounded raw
    dollar gap that can swing arbitrarily negative for high-income drivers."""
    name = "LAF"

    def on_start(self, drivers):
        self._drivers = drivers

    def _mean_income(self):
        return sum(d.total_income for d in self._drivers) / len(self._drivers)

    def select(self, req, cands, now):
        return min(cands, key=lambda c: c[0].total_income)

    def select_batch(self, cands_map, now):
        mean_income = self._mean_income()

        def score_fn(d, req, dist, eta):
            rel_fairness = (mean_income - d.total_income) / max(mean_income, 1.0)
            return rel_fairness * req["fare_amount"]
        return hungarian_batch_assign(cands_map, score_fn)

    def on_committed(self, d, req, dist, eta, now):
        pass


class ExactReassignPolicy:
    """Real M-to-N exact solve: every WINDOW_SECONDS, maximizes total net
    utility (fare - deadhead_cost) across ALL requests and drivers in the
    window jointly via the Hungarian algorithm -- a genuine batched
    assignment, matching the paper's formulation (previously this was a
    disclosed 1xN simplification; see report for the earlier limitation
    this replaces)."""
    name = "Exact REASSIGN"

    def on_start(self, drivers):
        pass

    def select_batch(self, cands_map, now):
        def score_fn(d, req, dist, eta):
            return req["fare_amount"] - eta * 0.0025
        return hungarian_batch_assign(cands_map, score_fn)

    def on_committed(self, d, req, dist, eta, now):
        pass


class MOMAQLPolicy:
    """Multi-objective score with online TD(0) Q-learning over
    (zone, hour-of-day) states (Q[zone, hour] = value of a driver ending up
    in that zone at that hour, e.g. rush-hour Midtown vs. 3am Midtown):
        score = (1-lambda)*(fare - deadhead_cost + gamma*Q[D, D_hour]) + lambda*(mean_income - driver.income)
    Real M-to-N batching: within one window, different requests can have
    different destinations D_i, so Q(D_i, hour_i) now genuinely varies
    across the joint assignment problem and can change which request a
    driver is matched to -- fixing the earlier finding that Q_future was a
    no-op under strict one-request-at-a-time dispatch (see R2 ablation
    investigation report)."""
    name = "MOMAQL"

    def __init__(self, lam=0.5, gamma=0.9, alpha=0.1, q_table: dict | None = None, frozen: bool = False,
                ablation: str = "full"):
        """ablation: 'full' (default) | 'no_forecast' (Q_future term forced
        to 0, i.e. no future-demand lookahead) | 'no_fairness' (lambda
        forced to 0, i.e. pure efficiency scoring)."""
        self.lam = 0.0 if ablation == "no_fairness" else lam
        self.gamma = gamma
        self.alpha = alpha
        self.ablation = ablation
        self.Q: dict = self._parse_q_table(q_table) if q_table else {}
        self.frozen = frozen  # True during evaluation: use the trained Q-table, never update it
        self._drivers = None

    @staticmethod
    def _parse_q_table(q_table):
        """Q is keyed by (zone_id, hour_of_day) -- hour distinguishes rush
        hour from 3am demand for the same zone. Accepts either native tuple
        keys (in-process, e.g. tests) or 'zone:hour' string keys (JSON, whose
        keys must be strings)."""
        parsed = {}
        for k, v in q_table.items():
            key = k if isinstance(k, tuple) else tuple(int(x) for x in str(k).split(":"))
            parsed[key] = v
        return parsed

    def on_start(self, drivers):
        self._drivers = drivers

    def _mean_income(self):
        return sum(d.total_income for d in self._drivers) / len(self._drivers)

    def _score(self, d, req, dist, eta, mean_income):
        D_zone = req.get("dropoff_zone_id")
        D_hour = req.get("dropoff_hour")
        q_future = 0.0 if self.ablation == "no_forecast" else self.Q.get((D_zone, D_hour), 0.0)
        deadhead_cost = eta * 0.0025
        efficiency = req["fare_amount"] - deadhead_cost + self.gamma * q_future
        # Relative Fairness Scaling: raw (mean_income - d.income) grows to
        # thousands of USD over a long real horizon (accumulated driver
        # income), completely dominating the per-trip efficiency term
        # (~$10-80) and driving score negative for any above-average
        # driver -- collapsing completion rate once "decline" (cost 0) is
        # a real option. Normalize to a fraction of mean_income, then
        # rescale by THIS trip's fare so fairness stays on the same
        # per-trip USD footing as efficiency.
        rel_fairness = (mean_income - d.total_income) / max(mean_income, 1.0)
        fairness = rel_fairness * req["fare_amount"]
        return (1 - self.lam) * efficiency + self.lam * fairness

    def select_batch(self, cands_map, now):
        mean_income = self._mean_income()
        return hungarian_batch_assign(cands_map, lambda d, req, dist, eta: self._score(d, req, dist, eta, mean_income))

    def on_committed(self, d, req, dist, eta, now):
        if self.frozen:
            return  # evaluation mode: Q-table is fixed, already trained
        # Bellman TD(0), state = (zone, hour-of-day): Q(S) <- Q(S) +
        # alpha*(reward + gamma*Q(S') - Q(S)). S = (pickup_zone, pickup_hour)
        # -- where the driver was when taking this trip; S' =
        # (dropoff_zone, dropoff_hour) -- where/when they end up, matching
        # what _score's gamma*Q(D_zone, D_hour) looks up for a CANDIDATE
        # trip's destination. Hour comes from wall-clock (absolute epoch),
        # not the per-file-relative pickup_ts, so a given hour bucket means
        # the same real time-of-day whether learned in train.parquet or
        # looked up in val/test.parquet.
        P_zone = req.get("pickup_zone_id")
        D_zone = req.get("dropoff_zone_id")
        P_hour = req.get("pickup_hour")
        D_hour = req.get("dropoff_hour")
        if P_zone is None or P_hour is None:
            return
        reward = req["fare_amount"] - eta * 0.0025
        old_q = self.Q.get((P_zone, P_hour), 0.0)
        next_q = self.Q.get((D_zone, D_hour), 0.0) if D_zone is not None and D_hour is not None else 0.0
        self.Q[(P_zone, P_hour)] = old_q + self.alpha * (reward + self.gamma * next_q - old_q)


ALL_POLICIES = {
    "Greedy": GreedyPolicy,
    "Nearest": NearestPolicy,
    "LAF": LAFPolicy,
    "Exact REASSIGN": ExactReassignPolicy,
    "MOMAQL": MOMAQLPolicy,
}
