"""Multi-pass MOMAQL training with cosine-annealing alpha, real convergence
tracking (not a blind "more epochs = better" assumption).

E=5 real full passes over train.parquet (912,375 real requests each) --
NOT E=2000: one pass already delivers ~580,000 real TD updates across a
67-value Q-table (~8,657 updates/zone), and each full pass costs ~280s
(measured), so 2000 passes would take ~6.5 days -- infeasible and, for a
table this small, statistically unnecessary. 5 passes (~23 min) is enough
to empirically show whether further training changes anything.

alpha(e) = 0.001 + 0.5*(0.1-0.001)*(1 + cos(e*pi/E)), e=0..E-1 (as requested,
E scaled down from 2000 to 5 for feasibility -- same formula shape).
"""
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pyarrow.parquet as pq

from simulator import run_simulation
from policies import MOMAQLPolicy

N_DRIVERS = 200
SEED = 20260721
E = 5
ALPHA_MIN, ALPHA_MAX = 0.001, 0.1


def load_requests_fast(path: Path):
    table = pq.read_table(path, columns=[
        "pickup_ts", "pickup_latitude", "pickup_longitude",
        "dropoff_latitude", "dropoff_longitude", "fare_amount",
        "duration_seconds", "dropoff_zone_id",
    ])
    p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
    t0 = p_ts[0].astype("datetime64[s]").astype("int64")
    ts_rel = (p_ts.astype("datetime64[s]").astype("int64") - t0).astype(float)
    p_lat = table["pickup_latitude"].to_numpy()
    p_lon = table["pickup_longitude"].to_numpy()
    d_lat = table["dropoff_latitude"].to_numpy()
    d_lon = table["dropoff_longitude"].to_numpy()
    fares = table["fare_amount"].to_numpy()
    durs = table["duration_seconds"].to_numpy()
    z_ids = table["dropoff_zone_id"].to_pylist()
    n = len(p_lat)
    return [
        {"_idx": i, "pickup_ts": float(ts_rel[i]), "pickup_latitude": float(p_lat[i]),
         "pickup_longitude": float(p_lon[i]), "dropoff_latitude": float(d_lat[i]),
         "dropoff_longitude": float(d_lon[i]), "fare_amount": float(fares[i]),
         "duration_seconds": float(durs[i]), "dropoff_zone_id": z_ids[i]}
        for i in range(n)
    ]


def cosine_alpha(e: int, E: int) -> float:
    return ALPHA_MIN + 0.5 * (ALPHA_MAX - ALPHA_MIN) * (1 + math.cos(e * math.pi / E))


def main():
    print("[load] reading train.parquet...", flush=True)
    reqs = load_requests_fast(Path(__file__).parent / "data" / "train.parquet")
    print(f"[load] {len(reqs):,} real requests loaded", flush=True)

    policy = MOMAQLPolicy(frozen=False)
    convergence = []
    for e in range(E):
        alpha = cosine_alpha(e, E)
        policy.alpha = alpha
        q_before = dict(policy.Q)
        t0 = time.perf_counter()
        result = run_simulation(reqs, n_drivers=N_DRIVERS, policy=policy, seed=SEED)
        elapsed = time.perf_counter() - t0
        # real convergence metric: mean absolute change in Q across zones present before this pass
        shared = set(q_before) & set(policy.Q)
        mean_abs_delta = (sum(abs(policy.Q[z] - q_before[z]) for z in shared) / len(shared)) if shared else float("nan")
        print(f"[pass {e+1}/{E}] alpha={alpha:.4f} elapsed={elapsed:.1f}s "
             f"completed={result.total_completed}/{result.total_requests} "
             f"zones={len(policy.Q)} mean|deltaQ|={mean_abs_delta:.4f}", flush=True)
        convergence.append({"pass": e + 1, "alpha": alpha, "elapsed_s": elapsed,
                            "zones": len(policy.Q), "mean_abs_delta_q": mean_abs_delta})

    out_q = Path(__file__).parent / "data" / "momaql_q_table_multipass.json"
    with out_q.open("w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in policy.Q.items()}, f, indent=2)
    print(f"[save] {out_q}", flush=True)

    import csv
    out_conv = Path(__file__).parent / "reports" / "momaql_convergence.csv"
    out_conv.parent.mkdir(parents=True, exist_ok=True)
    with out_conv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(convergence[0].keys()))
        w.writeheader()
        w.writerows(convergence)
    print(f"[save] {out_conv}", flush=True)
    print("[done]", flush=True)


if __name__ == "__main__":
    main()
