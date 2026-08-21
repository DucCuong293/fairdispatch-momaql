"""Final Test Suite A -- Main Baseline Comparison. Mirrors run_r1.py exactly
(same engine, same policies, same seeds, same driver count) but on the
Final Test Evaluation View (test.parquet after the frozen quality
transform -- see FINAL_TEST_PROTOCOL.md) instead of val.parquet.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from simulator import run_simulation_batched as run_simulation
from policies import ALL_POLICIES, MOMAQLPolicy
from quality_transform import load_requests_with_quality_transform, gini, variance, std

ROOT = Path(__file__).resolve().parents[2]
DEV_DATA = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")
OUT_DIR = ROOT / "final_test" / "baseline"
SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
N_DRIVERS = 200
VAL_MAX_EPOCH = 1374412620


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[load] loading Final Test Evaluation View (test.parquet + frozen quality transform)...", flush=True)
    t0 = time.perf_counter()
    reqs, stats = load_requests_with_quality_transform(DEV_DATA / "test.parquet", boundary_exclude_epoch_second=VAL_MAX_EPOCH)
    print(f"[load] {len(reqs):,} evaluated requests loaded in {time.perf_counter()-t0:.2f}s "
          f"(original={stats['original_rows']}, boundary_excluded={stats['temporal_boundary_excluded']}, "
          f"repaired={stats['duration_repaired']}, duration_excluded={stats['duration_excluded']})", flush=True)

    q_table_path = ROOT / "data" / "momaql_q_table_trained.json"
    with q_table_path.open("r", encoding="utf-8") as f:
        raw_q = json.load(f)
    trained_q = {int(k) if k.isdigit() else k: float(v) for k, v in raw_q.items()}
    print(f"[momaql] loaded trained Q-table with {len(trained_q)} zone values", flush=True)

    results = []
    print("\n=== FINAL TEST SUITE A: MAIN BASELINE (5 Policies x 5 Seeds) ===", flush=True)
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
            sd = std(incomes)
            el = time.perf_counter() - t_start

            print(f"[{pol_name:14s}] seed={seed} -> Utility=${u:10.2f}, Gini={g:.4f}, "
                  f"Var={var:12.2f}, Trips={res.total_completed} ({el:.1f}s)", flush=True)

            results.append({
                "policy": pol_name, "seed": seed, "utility": u, "gini": g,
                "variance": var, "std": sd, "std_over_mean": (sd / (u / len(incomes))) if u != 0 else float("nan"),
                "served": res.total_completed, "avg_income": u / len(incomes),
                "avg_deadhead": (res.total_deadhead_cost / res.total_completed) if res.total_completed else 0.0,
                "runtime_seconds": el,
            })

    per_seed_df = pd.DataFrame(results)
    per_seed_df.to_csv(OUT_DIR / "test_baseline_per_seed.csv", index=False)

    summary = per_seed_df.groupby("policy").agg(
        utility_mean=("utility", "mean"), utility_std=("utility", "std"),
        gini_mean=("gini", "mean"), gini_std=("gini", "std"),
        variance_mean=("variance", "mean"), std_mean=("std", "mean"),
        served_mean=("served", "mean"), avg_income_mean=("avg_income", "mean"),
        avg_deadhead_mean=("avg_deadhead", "mean"),
    ).round(4)
    summary.to_csv(OUT_DIR / "test_baseline_summary.csv")

    print(f"\n[done] wrote {len(results)} runs to {OUT_DIR / 'test_baseline_per_seed.csv'}", flush=True)
    print(f"[done] wrote summary to {OUT_DIR / 'test_baseline_summary.csv'}", flush=True)


if __name__ == "__main__":
    main()
