"""Real R1 run: 5 policies on val.parquet (195,508 real requests), S200
(200 drivers), 5 seeds each, using pre-trained MOMAQL Q-table.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pyarrow.parquet as pq
import numpy as np

from simulator import run_simulation_batched as run_simulation
from policies import ALL_POLICIES, MOMAQLPolicy

SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
N_DRIVERS = 200


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


def load_requests_fast(path: Path):
    table = pq.read_table(path, columns=[
        "pickup_ts", "pickup_latitude", "pickup_longitude",
        "dropoff_latitude", "dropoff_longitude", "fare_amount",
        "duration_seconds", "pickup_zone_id", "dropoff_zone_id"
    ])
    p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
    abs_sec = p_ts.astype("datetime64[s]").astype("int64")  # real epoch seconds -- wall-clock hour derives from this, not the per-file-relative t0 below
    t0 = abs_sec[0]
    ts_rel = (abs_sec - t0).astype(float)
    p_lat = table["pickup_latitude"].to_numpy()
    p_lon = table["pickup_longitude"].to_numpy()
    d_lat = table["dropoff_latitude"].to_numpy()
    d_lon = table["dropoff_longitude"].to_numpy()
    fares = table["fare_amount"].to_numpy()
    durs = table["duration_seconds"].to_numpy()
    p_hours = ((abs_sec // 3600) % 24).astype(int)
    d_hours = (((abs_sec + durs.astype("int64")) // 3600) % 24).astype(int)
    p_zids = table["pickup_zone_id"].to_pylist()
    z_ids = table["dropoff_zone_id"].to_pylist()

    n = len(p_lat)
    reqs = [
        {
            "_idx": i,
            "pickup_ts": float(ts_rel[i]),
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
        for i in range(n)
    ]
    return reqs


def main():
    val_path = Path(__file__).parent / "data" / "val.parquet"
    print(f"[load] loading {val_path}...", flush=True)
    t0 = time.perf_counter()
    reqs = load_requests_fast(val_path)
    print(f"[load] {len(reqs):,} validation requests loaded in {time.perf_counter()-t0:.2f}s", flush=True)

    # Check for trained Q-table
    q_table_path = Path(__file__).parent / "data" / "momaql_q_table_trained.json"
    trained_q = {}
    if q_table_path.exists():
        with q_table_path.open("r", encoding="utf-8") as f:
            raw_q = json.load(f)
            trained_q = {int(k) if k.isdigit() else k: float(v) for k, v in raw_q.items()}
        print(f"[momaql] loaded trained Q-table with {len(trained_q)} zone values", flush=True)

    results = []
    print("\n=== STARTING R1 VALIDATION SWEEP (5 Policies x 5 Seeds) ===", flush=True)
    for pol_name in ["Greedy", "Nearest", "LAF", "Exact REASSIGN", "MOMAQL"]:
        for seed in SEEDS:
            t_start = time.perf_counter()
            if pol_name == "MOMAQL":
                policy = MOMAQLPolicy(q_table=trained_q, frozen=True)
            else:
                policy = ALL_POLICIES[pol_name]()

            res = run_simulation(reqs, n_drivers=N_DRIVERS, policy=policy, seed=seed)
            incomes = list(res.per_driver_income.values())
            g = gini(incomes)
            u = sum(incomes)
            var = variance(incomes)
            p10 = float(np.percentile(incomes, 10))
            p50 = float(np.percentile(incomes, 50))
            p90 = float(np.percentile(incomes, 90))
            el = time.perf_counter() - t_start

            print(f"[{pol_name:14s}] seed={seed} -> Utility=${u:10.2f}, Gini={g:.4f}, "
                  f"Var={var:12.2f}, P10=${p10:6.2f}, P50=${p50:6.2f}, P90=${p90:6.2f}, Trips={res.total_completed} ({el:.1f}s)", flush=True)

            results.append({
                "policy": pol_name,
                "seed": seed,
                "utility": u,
                "gini": g,
                "variance": var,
                "std": var ** 0.5,
                "std_over_mean": (var ** 0.5 / (u / len(incomes))) if u != 0 else float("nan"),
                "p10": p10,
                "p50": p50,
                "p90": p90,
                "completed_trips": res.total_completed,
                "runtime_seconds": el
            })

    out_csv = Path(__file__).parent / "reports" / "r1_validation_results.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"\n[done] wrote all 25 runs to {out_csv}", flush=True)


if __name__ == "__main__":
    main()
