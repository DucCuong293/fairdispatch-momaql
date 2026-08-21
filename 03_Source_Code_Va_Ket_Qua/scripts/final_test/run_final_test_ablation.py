"""Final Test Suite B -- Key Ablation. Mirrors run_r2_ablation.py exactly
(same engine, same Full/No Forecast/No Fairness variants, same seeds, same
driver count, same trained Q-table) but on the Final Test Evaluation View.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from simulator import run_simulation_batched as run_simulation
from policies import MOMAQLPolicy
from quality_transform import load_requests_with_quality_transform, gini, variance, std, coefficient_of_variation

ROOT = Path(__file__).resolve().parents[2]
DEV_DATA = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")
OUT_DIR = ROOT / "final_test" / "ablation"
SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
N_DRIVERS = 200
ABLATIONS = ["full", "no_forecast", "no_fairness"]
VAL_MAX_EPOCH = 1374412620


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    q_path = ROOT / "data" / "momaql_q_table_trained.json"
    with q_path.open("r", encoding="utf-8") as f:
        q_table = json.load(f)
    print(f"[q] using {q_path.name}", flush=True)

    reqs, stats = load_requests_with_quality_transform(DEV_DATA / "test.parquet", boundary_exclude_epoch_second=VAL_MAX_EPOCH)
    print(f"[load] {len(reqs):,} evaluated Test requests (Final Test Evaluation View)", flush=True)

    rows = []
    print("\n=== FINAL TEST SUITE B: KEY ABLATION ===", flush=True)
    for ablation in ABLATIONS:
        for seed in SEEDS:
            t0 = time.perf_counter()
            policy = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation=ablation)
            res = run_simulation(reqs, n_drivers=N_DRIVERS, policy=policy, seed=seed)
            incomes = list(res.per_driver_income.values())
            g = gini(incomes)
            u = sum(incomes)
            var = variance(incomes)
            sd = std(incomes)
            cv = coefficient_of_variation(incomes)
            el = time.perf_counter() - t0
            print(f"[{ablation:12s} seed={seed}] Utility=${u:,.1f} Gini={g:.4f} Var={var:,.1f} ({el:.1f}s)", flush=True)
            rows.append({"ablation": ablation, "seed": seed, "utility": u, "gini": g,
                        "variance": var, "std": sd, "std_over_mean": cv, "served": res.total_completed,
                        "runtime_seconds": el})

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "test_ablation_per_seed.csv", index=False)
    summary = df.groupby("ablation").agg(utility_mean=("utility", "mean"), utility_std=("utility", "std"),
                                         gini_mean=("gini", "mean"), gini_std=("gini", "std"),
                                         variance_mean=("variance", "mean"), std_mean=("std", "mean"),
                                         served_mean=("served", "mean")).round(4)
    print("\n=== FINAL TEST ABLATION SUMMARY ===")
    print(summary.loc[["full", "no_forecast", "no_fairness"]])
    summary.to_csv(OUT_DIR / "test_ablation_results.csv")
    print("[done]", flush=True)


if __name__ == "__main__":
    main()
