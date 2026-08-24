"""Lightweight Discrete-Event Simulator (DES) for fairdispatch_v3_clean.

Deliberate simplifications vs. the frozen P2-06 Simulator (disclosed, not
hidden):
  - Driver position tracked as real (lat, lon) instead of a 64-bucket
    spatial partition -- more physically direct, no zone-centroid
    approximation needed.
  - ETA/deadhead computed from real haversine distance between real
    pickup/dropoff coordinates, converted via a constant assumed speed
    (12 mph, a plausible Manhattan average) -- not the project's full
    travel-time model (which depends on tightly-coupled P2-05 infra we
    are deliberately not reusing here, per the "lightweight, standalone"
    scope of this experiment).
  - Deadhead cost coefficient reused as-is from the project's real, frozen
    P2-07 UtilityCoefficients (cost_per_second_deadhead_usd=0.0025) --
    not reinvented.

Real invariants enforced and checked in tests/test_simulator_invariants.py.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

COST_PER_SECOND_DEADHEAD_USD = 0.0025  # from p2_07_metrics.UtilityCoefficients (frozen, real)
AVG_SPEED_MPH = 12.0  # constant-speed simplification, disclosed above
MAX_PICKUP_ETA_SECONDS = 600.0  # feasibility cutoff (10 min), matches project convention


def haversine_miles(lat1, lon1, lat2, lon2) -> float:
    R = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def eta_seconds(dist_miles: float) -> float:
    return (dist_miles / AVG_SPEED_MPH) * 3600.0


@dataclass
class Driver:
    driver_id: int
    lat: float
    lon: float
    available_at: float
    total_income: float = 0.0
    total_deadhead_cost: float = 0.0
    total_trips: int = 0


@dataclass
class SimResult:
    per_driver_income: dict
    total_fares_served: float = 0.0
    total_deadhead_cost: float = 0.0
    total_completed: int = 0
    total_requests: int = 0
    trace: list = field(default_factory=list)  # (req_idx, driver_id, fare, deadhead_cost)


def init_drivers(n_drivers: int, requests, seed: int) -> list[Driver]:
    """Real init: drivers start at real pickup locations of the first
    n_drivers requests (a real, non-fabricated way to seed plausible
    starting positions), available from t=0."""
    import random
    rng = random.Random(seed)
    idxs = rng.sample(range(len(requests)), min(n_drivers, len(requests)))
    drivers = []
    for i, ridx in enumerate(idxs):
        r = requests[ridx]
        drivers.append(Driver(driver_id=i, lat=r["pickup_latitude"], lon=r["pickup_longitude"],
                              available_at=0.0))
    return drivers


def feasible_drivers(drivers: list[Driver], req, now: float) -> list[tuple[Driver, float, float]]:
    """Returns [(driver, deadhead_miles, eta_seconds), ...] for drivers that
    are free by `now` and within MAX_PICKUP_ETA_SECONDS of the pickup."""
    out = []
    for d in drivers:
        if d.available_at > now:
            continue
        dist = haversine_miles(d.lat, d.lon, req["pickup_latitude"], req["pickup_longitude"])
        eta = eta_seconds(dist)
        if eta <= MAX_PICKUP_ETA_SECONDS:
            out.append((d, dist, eta))
    return out


def commit_trip(d: Driver, req, deadhead_miles: float, eta: float, now: float, result: SimResult, record_trace: bool = True):
    fare = req["fare_amount"]
    deadhead_cost = eta * COST_PER_SECOND_DEADHEAD_USD  # coefficient is per SECOND of deadhead time
    net = fare - deadhead_cost
    d.total_income += net
    d.total_deadhead_cost += deadhead_cost
    d.total_trips += 1
    d.lat, d.lon = req["dropoff_latitude"], req["dropoff_longitude"]
    d.available_at = now + eta + req["duration_seconds"]
    result.total_fares_served += fare
    result.total_deadhead_cost += deadhead_cost
    result.total_completed += 1
    if record_trace:
        result.trace.append((req["_idx"], d.driver_id, fare, deadhead_cost, req.get("dropoff_zone_id")))


def run_simulation_batched(requests: list[dict], n_drivers: int, policy, seed: int,
                          window_seconds: float = 60.0, record_trace: bool = False) -> SimResult:
    """Real M-to-N batched dispatch, matching the paper's window formulation:
    every WINDOW_SECONDS, gather all requests that fired in that window,
    compute each request's feasible candidates as of the window's START
    time (uniform decision instant for the whole batch -- required for a
    joint solve to be well-defined), hand the whole batch to
    policy.select_batch(), then commit whatever it returns. A driver can
    never be double-booked within one window (feasible_drivers() already
    excludes drivers busy from an EARLIER commit in this same window,
    since commit_trip() updates d.available_at before the next window's
    candidates are computed; policies are additionally responsible for
    never returning the same driver twice within one batch)."""
    drivers = init_drivers(n_drivers, requests, seed)
    result = SimResult(per_driver_income={d.driver_id: 0.0 for d in drivers},
                       total_requests=len(requests))
    policy.on_start(drivers)
    i, n = 0, len(requests)
    while i < n:
        window_start = requests[i]["pickup_ts"]
        window_end = window_start + window_seconds
        window_reqs = []
        while i < n and requests[i]["pickup_ts"] < window_end:
            window_reqs.append(requests[i])
            i += 1

        cands_map = {}
        for req in window_reqs:
            cands = feasible_drivers(drivers, req, window_start)
            if cands:
                cands_map[req["_idx"]] = (req, cands)
        if not cands_map:
            continue

        assignments = policy.select_batch(cands_map, window_start)
        used_drivers = set()
        for req_idx, chosen in assignments.items():
            if chosen is None:
                continue
            d, dist, eta = chosen
            if d.driver_id in used_drivers:
                continue  # policy bug guard: never double-book a driver within one window
            used_drivers.add(d.driver_id)
            req, _ = cands_map[req_idx]
            commit_trip(d, req, dist, eta, window_start, result, record_trace=record_trace)
            policy.on_committed(d, req, dist, eta, window_start)

    for d in drivers:
        result.per_driver_income[d.driver_id] = d.total_income
    return result


def run_simulation_with_horizon(requests: list[dict], n_drivers: int, policy, seed: int,
                                checkpoint_days: list[float], window_seconds: float = 60.0,
                                compare_policy=None, zone_classifier: dict | None = None):
    """Same batched dispatch as run_simulation_batched, extended for the
    multi-horizon study:
    (1) snapshots per-driver income + completed count at each real calendar-
        day boundary in checkpoint_days, tracing how fairness evolves as the
        evaluation horizon grows -- one real trajectory, not independent
        reruns per horizon (matches the paper's own horizon-1..7 evaluation
        concept: a growing window over the SAME run, not fresh restarts).
    (2) if compare_policy is given, also queries it (read-only, its
        on_committed is never called, so it never actually acts) on the SAME
        cands_map each window as `policy`, to measure the policy
        disagreement rate D = P(assignment_policy != assignment_compare) on
        identical candidate sets and identical driver state. Cumulative
        (disagree, compared) counts are ALSO snapshotted at each checkpoint,
        so a caller can diff between two checkpoints to get a phase-specific
        rate (e.g. day 1-7 vs day 8-37) without a second run.
    (3) if zone_classifier ({zone_id: class_label}) is given alongside
        compare_policy, disagreement is additionally broken down per class
        label (e.g. "core" vs "periphery"), keyed on the request's pickup
        zone, again both cumulative-at-checkpoint and final-total.
    Returns (SimResult, checkpoints, disagreement_rate) where checkpoints[day]
    is {"incomes": [...], "completed": int, "disagreement": {...} or None}.
    disagreement_rate is the final overall rate (unchanged from before)."""
    drivers = init_drivers(n_drivers, requests, seed)
    result = SimResult(per_driver_income={d.driver_id: 0.0 for d in drivers},
                       total_requests=len(requests))
    policy.on_start(drivers)
    if compare_policy is not None:
        compare_policy.on_start(drivers)

    checkpoints = {}
    cp_days = sorted(checkpoint_days)
    cp_idx = 0
    t0 = requests[0]["pickup_ts"]
    max_horizon_seconds = cp_days[-1] * 86400.0
    disagree_count = 0
    compared_count = 0
    class_labels = sorted(set(zone_classifier.values())) if zone_classifier else []
    class_counts = {lbl: [0, 0] for lbl in class_labels}  # label -> [disagree, compared]

    def snapshot_disagreement():
        if compare_policy is None:
            return None
        snap = {"total": (disagree_count, compared_count)}
        for lbl in class_labels:
            snap[lbl] = tuple(class_counts[lbl])
        return snap

    i, n = 0, len(requests)
    while i < n:
        window_start = requests[i]["pickup_ts"]
        if window_start - t0 > max_horizon_seconds:
            break  # nothing past the last requested checkpoint matters
        window_end = window_start + window_seconds
        window_reqs = []
        while i < n and requests[i]["pickup_ts"] < window_end:
            window_reqs.append(requests[i])
            i += 1

        while cp_idx < len(cp_days) and (window_start - t0) >= cp_days[cp_idx] * 86400.0:
            checkpoints[cp_days[cp_idx]] = {
                "incomes": [d.total_income for d in drivers],
                "completed": result.total_completed,
                "disagreement": snapshot_disagreement(),
            }
            cp_idx += 1

        cands_map = {}
        for req in window_reqs:
            cands = feasible_drivers(drivers, req, window_start)
            if cands:
                cands_map[req["_idx"]] = (req, cands)
        if not cands_map:
            continue

        assignments = policy.select_batch(cands_map, window_start)

        if compare_policy is not None:
            alt_assignments = compare_policy.select_batch(cands_map, window_start)
            for req_idx in cands_map:
                a = assignments.get(req_idx)
                b = alt_assignments.get(req_idx)
                a_id = a[0].driver_id if a is not None else None
                b_id = b[0].driver_id if b is not None else None
                compared_count += 1
                disagreed = a_id != b_id
                if disagreed:
                    disagree_count += 1
                if zone_classifier is not None:
                    req_zone = cands_map[req_idx][0].get("pickup_zone_id")
                    lbl = zone_classifier.get(req_zone)
                    if lbl is not None:
                        class_counts[lbl][1] += 1
                        if disagreed:
                            class_counts[lbl][0] += 1

        used_drivers = set()
        for req_idx, chosen in assignments.items():
            if chosen is None:
                continue
            d, dist, eta = chosen
            if d.driver_id in used_drivers:
                continue
            used_drivers.add(d.driver_id)
            req, _ = cands_map[req_idx]
            commit_trip(d, req, dist, eta, window_start, result, record_trace=False)
            policy.on_committed(d, req, dist, eta, window_start)

    while cp_idx < len(cp_days):
        checkpoints[cp_days[cp_idx]] = {
            "incomes": [d.total_income for d in drivers],
            "completed": result.total_completed,
            "disagreement": snapshot_disagreement(),
        }
        cp_idx += 1

    for d in drivers:
        result.per_driver_income[d.driver_id] = d.total_income

    disagreement_rate = (disagree_count / compared_count) if compared_count else None
    return result, checkpoints, disagreement_rate


def run_simulation(requests: list[dict], n_drivers: int, policy, seed: int, record_trace: bool = False) -> SimResult:
    """requests must be sorted by pickup_ts already, each a dict with real
    fields: pickup_ts (float seconds since epoch/start), pickup_latitude,
    pickup_longitude, dropoff_latitude, dropoff_longitude, fare_amount,
    duration_seconds, dropoff_zone_id, _idx."""
    drivers = init_drivers(n_drivers, requests, seed)
    result = SimResult(per_driver_income={d.driver_id: 0.0 for d in drivers},
                       total_requests=len(requests))
    policy.on_start(drivers)
    for req in requests:
        now = req["pickup_ts"]
        cands = feasible_drivers(drivers, req, now)
        if not cands:
            continue
        chosen = policy.select(req, cands, now)
        if chosen is None:
            continue
        d, dist, eta = chosen
        commit_trip(d, req, dist, eta, now, result, record_trace=record_trace)
        policy.on_committed(d, req, dist, eta, now)
    for d in drivers:
        result.per_driver_income[d.driver_id] = d.total_income
    return result
