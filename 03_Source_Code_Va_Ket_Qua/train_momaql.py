"""Trains MOMAQL's Q(zone) table on the real train.parquet split (912k requests)
with high-speed, low-memory PyArrow loader.
Saves data/momaql_q_table_trained.json.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pyarrow.parquet as pq
import numpy as np

from simulator import run_simulation_batched as run_simulation
from policies import MOMAQLPolicy

N_DRIVERS = 200
SEED = 20260721


def load_requests_fast(path: Path):
    table = pq.read_table(path, columns=[
        "pickup_ts", "pickup_latitude", "pickup_longitude",
        "dropoff_latitude", "dropoff_longitude", "fare_amount",
        "duration_seconds", "pickup_zone_id", "dropoff_zone_id"
    ])
    p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
    abs_sec = p_ts.astype("datetime64[s]").astype("int64")  # real epoch seconds -- wall-clock hour must derive from this, not from the per-file-relative t0 below (train/val/test each have a different t0, which would misalign hour buckets learned in training vs looked up at eval)
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
    train_path = Path(__file__).parent / "data" / "train.parquet"
    print("[load] reading train.parquet via PyArrow (zero OOM)...", flush=True)
    t0 = time.perf_counter()
    reqs = load_requests_fast(train_path)
    print(f"[load] {len(reqs):,} real training requests loaded in {time.perf_counter()-t0:.2f}s", flush=True)

    policy = MOMAQLPolicy(frozen=False)
    t1 = time.perf_counter()
    print("[train] starting MOMAQL training simulation...", flush=True)
    result = run_simulation(reqs, n_drivers=N_DRIVERS, policy=policy, seed=SEED)
    elapsed = time.perf_counter() - t1
    print(f"[train] done in {elapsed:.1f}s -- completed={result.total_completed}/{result.total_requests} "
          f"states_learned={len(policy.Q)} (zone,hour) pairs", flush=True)

    out_path = Path(__file__).parent / "data" / "momaql_q_table_trained.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({f"{z}:{h}": v for (z, h), v in policy.Q.items()}, f, indent=2)
    print(f"[save] wrote {out_path} ({len(policy.Q)} (zone,hour) states)", flush=True)

    vals = sorted(policy.Q.values())
    if vals:
        print(f"[stats] Q value range: min={vals[0]:.2f} max={vals[-1]:.2f} "
              f"median={vals[len(vals)//2]:.2f}", flush=True)


if __name__ == "__main__":
    main()
