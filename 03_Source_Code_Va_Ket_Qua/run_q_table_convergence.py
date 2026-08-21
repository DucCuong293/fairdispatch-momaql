"""Real measurement: how the Q(zone,hour) table's day-to-day change
(mean |delta Q| between consecutive daily snapshots) and cumulative
(zone,hour) visit counts evolve from day 1 to day 37 of training on
train.parquet. Tests whether the table empirically stabilizes around
day ~14 (as hypothesized) or not -- measured, not assumed.
Writes reports/q_table_convergence_daily.csv.
"""
import copy
import csv
import gc
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pyarrow.parquet as pq
import numpy as np

from simulator import init_drivers, feasible_drivers, commit_trip, SimResult
from policies import MOMAQLPolicy

N_DRIVERS = 200
WINDOW_SECONDS = 60.0
CHECKPOINT_DAYS = list(range(1, 38))  # 1..37


def load_37day_requests(path: Path):
    table = pq.read_table(path, columns=[
        "pickup_ts", "pickup_latitude", "pickup_longitude",
        "dropoff_latitude", "dropoff_longitude", "fare_amount",
        "duration_seconds", "pickup_zone_id", "dropoff_zone_id"
    ])
    p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
    abs_sec = p_ts.astype("datetime64[s]").astype("int64")
    t0 = abs_sec[0]
    ts_rel = (abs_sec - t0).astype(float)
    
    # Filter only up to 37.5 days
    mask = ts_rel <= (37.5 * 86400.0)
    indices = np.where(mask)[0]
    
    p_lat = table["pickup_latitude"].to_numpy()[mask]
    p_lon = table["pickup_longitude"].to_numpy()[mask]
    d_lat = table["dropoff_latitude"].to_numpy()[mask]
    d_lon = table["dropoff_longitude"].to_numpy()[mask]
    fares = table["fare_amount"].to_numpy()[mask]
    durs = table["duration_seconds"].to_numpy()[mask]
    abs_sec_sub = abs_sec[mask]
    ts_rel_sub = ts_rel[mask]

    # to_pylist() is a vectorized C-level pull, not a per-row as_py() Python loop --
    # avoids holding `table` alive through a slow row-by-row scan.
    p_zids_full = table["pickup_zone_id"].to_pylist()
    z_ids_full = table["dropoff_zone_id"].to_pylist()
    del table, p_ts, abs_sec, ts_rel
    gc.collect()

    p_hours = ((abs_sec_sub // 3600) % 24).astype(int)
    d_hours = (((abs_sec_sub + durs.astype("int64")) // 3600) % 24).astype(int)

    p_zids = [p_zids_full[int(idx)] for idx in indices]
    z_ids = [z_ids_full[int(idx)] for idx in indices]
    del p_zids_full, z_ids_full, mask
    gc.collect()

    reqs = [
        {
            "_idx": i,
            "pickup_ts": float(ts_rel_sub[i]),
            "pickup_latitude": float(p_lat[i]),
            "pickup_longitude": float(p_lon[i]),
            "dropoff_latitude": float(d_lat[i]),
            "dropoff_longitude": float(d_lon[i]),
            "fare_amount": float(fares[i]),
            "duration_seconds": float(durs[i]),
            "pickup_zone_id": p_zids[i],
            "dropoff_zone_id": z_ids[i],
            "pickup_hour": int(p_hours[i]),
            "dropoff_hour": int(d_hours[i]),
        }
        for i in range(len(indices))
    ]
    return reqs


def main():
    reqs = load_37day_requests(Path(__file__).parent / "data" / "train.parquet")
    print(f"[load] {len(reqs):,} real training requests across 37 days", flush=True)

    policy = MOMAQLPolicy(lam=0.5, frozen=False)
    drivers = init_drivers(N_DRIVERS, reqs, seed=20260721)
    result = SimResult(per_driver_income={d.driver_id: 0.0 for d in drivers}, total_requests=len(reqs))
    policy.on_start(drivers)

    visits = {}  # (zone, hour) -> cumulative visit count
    t0 = reqs[0]["pickup_ts"]
    max_seconds = CHECKPOINT_DAYS[-1] * 86400.0
    cp_idx = 0
    snapshots = {}  # day -> (Q copy, visits copy, total_visits)

    t_start = time.perf_counter()
    i, n = 0, len(reqs)
    while i < n:
        window_start = reqs[i]["pickup_ts"]
        if window_start - t0 > max_seconds:
            break
        window_end = window_start + WINDOW_SECONDS
        window_reqs = []
        while i < n and reqs[i]["pickup_ts"] < window_end:
            window_reqs.append(reqs[i])
            i += 1

        while cp_idx < len(CHECKPOINT_DAYS) and (window_start - t0) >= CHECKPOINT_DAYS[cp_idx] * 86400.0:
            day = CHECKPOINT_DAYS[cp_idx]
            snapshots[day] = (dict(policy.Q), sum(visits.values()), len(visits))
            cp_idx += 1
            if day % 7 == 0 or day == 14 or day == 21:
                print(f"[day {day:2d}] states={len(policy.Q)} total_visits={sum(visits.values())} "
                      f"({time.perf_counter()-t_start:.1f}s)", flush=True)

        cands_map = {}
        for req in window_reqs:
            cands = feasible_drivers(drivers, req, window_start)
            if cands:
                cands_map[req["_idx"]] = (req, cands)
        if not cands_map:
            continue

        assignments = policy.select_batch(cands_map, window_start)
        used = set()
        for req_idx, chosen in assignments.items():
            if chosen is None:
                continue
            d, dist, eta = chosen
            if d.driver_id in used:
                continue
            used.add(d.driver_id)
            req, _ = cands_map[req_idx]
            commit_trip(d, req, dist, eta, window_start, result, record_trace=False)
            key = (req.get("pickup_zone_id"), req.get("pickup_hour"))
            visits[key] = visits.get(key, 0) + 1
            policy.on_committed(d, req, dist, eta, window_start)

    while cp_idx < len(CHECKPOINT_DAYS):
        day = CHECKPOINT_DAYS[cp_idx]
        snapshots[day] = (dict(policy.Q), sum(visits.values()), len(visits))
        cp_idx += 1

    print(f"[done training] completed={result.total_completed}/{result.total_requests} "
          f"({time.perf_counter()-t_start:.1f}s)", flush=True)
    del drivers, result
    gc.collect()

    rows = []
    prev_q = None
    for day in CHECKPOINT_DAYS:
        q_snap, total_visits, n_states = snapshots[day]
        if prev_q is not None:
            common_keys = set(q_snap.keys()) & set(prev_q.keys())
            if common_keys:
                mean_abs_delta = sum(abs(q_snap[k] - prev_q[k]) for k in common_keys) / len(common_keys)
            else:
                mean_abs_delta = float("nan")
        else:
            mean_abs_delta = float("nan")
        rows.append({
            "day": day,
            "n_states_visited": n_states,
            "cumulative_visits": total_visits,
            "mean_abs_delta_q_vs_prev_day": round(mean_abs_delta, 4),
        })
        prev_q = q_snap

    out_csv = Path(__file__).parent / "reports" / "q_table_convergence_daily.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[done] wrote {len(rows)} rows to {out_csv.name}", flush=True)
    for r in rows:
        if r["day"] in [1, 7, 14, 21, 28, 37]:
            print(f"  day={r['day']:2d} states={r['n_states_visited']:4d} "
                  f"visits={r['cumulative_visits']:6d} delta_Q={r['mean_abs_delta_q_vs_prev_day']}")


if __name__ == "__main__":
    main()
