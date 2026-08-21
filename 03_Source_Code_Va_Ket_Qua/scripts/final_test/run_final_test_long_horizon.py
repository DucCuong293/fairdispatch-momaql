"""Final Test Suite C -- Long-Horizon Verification. Mirrors
run_multi_horizon.py exactly (single trajectory per (config, seed) with
checkpoints, not independent reruns) but on the Final Test Evaluation View.
Test span = 42 calendar days (audited) >= 37 -> full canonical checkpoint
set is used, no truncation needed.
"""
import gc
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from simulator import run_simulation_with_horizon
from policies import MOMAQLPolicy
from quality_transform import load_requests_with_quality_transform, gini, variance

ROOT = Path(__file__).resolve().parents[2]
DEV_DATA = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")
OUT_DIR = ROOT / "final_test" / "long_horizon"
N_DRIVERS = 200
SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
HORIZON_DAYS = [1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 37]
VAL_MAX_EPOCH = 1374412620


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[load] loading Final Test Evaluation View...", flush=True)
    reqs_full, stats = load_requests_with_quality_transform(DEV_DATA / "test.parquet", boundary_exclude_epoch_second=VAL_MAX_EPOCH)
    t0 = min(r["pickup_ts"] for r in reqs_full)
    max_seconds = HORIZON_DAYS[-1] * 86400.0 + 3600.0
    reqs = [r for r in reqs_full if (r["pickup_ts"] - t0) <= max_seconds]
    del reqs_full
    gc.collect()
    print(f"[load] {len(reqs):,} evaluated requests within the first {HORIZON_DAYS[-1]} days "
          f"(evaluation view spans test's audited 42-day span)", flush=True)

    q_path = ROOT / "data" / "momaql_q_table_trained.json"
    with q_path.open("r", encoding="utf-8") as f:
        q_table = json.load(f)
    print(f"[q] using {q_path.name}", flush=True)

    horizon_rows = []
    disagreement_rows = []

    print("\n=== FINAL TEST SUITE C: LONG-HORIZON ===", flush=True)
    for seed in SEEDS:
        t_seed = time.perf_counter()

        full = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation="full")
        no_forecast_cmp = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation="no_forecast")
        res, checkpoints, disagreement = run_simulation_with_horizon(
            reqs, n_drivers=N_DRIVERS, policy=full, seed=seed,
            checkpoint_days=HORIZON_DAYS, compare_policy=no_forecast_cmp)
        for day in HORIZON_DAYS:
            incomes = checkpoints[day]["incomes"]
            horizon_rows.append({
                "config": "full", "seed": seed, "horizon_day": day,
                "utility": sum(incomes), "gini": gini(incomes),
                "variance": variance(incomes), "std": variance(incomes) ** 0.5,
                "completed": checkpoints[day]["completed"],
            })
        disagreement_rows.append({"seed": seed, "disagreement_rate": disagreement})
        print(f"[full         seed={seed}] disagreement_vs_no_forecast={disagreement:.4f} "
              f"({time.perf_counter()-t_seed:.1f}s)", flush=True)
        del full, no_forecast_cmp, res, checkpoints
        gc.collect()

        for ablation in ["no_forecast", "no_fairness"]:
            t_cfg = time.perf_counter()
            policy = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation=ablation)
            res, checkpoints, _ = run_simulation_with_horizon(
                reqs, n_drivers=N_DRIVERS, policy=policy, seed=seed,
                checkpoint_days=HORIZON_DAYS)
            for day in HORIZON_DAYS:
                incomes = checkpoints[day]["incomes"]
                horizon_rows.append({
                    "config": ablation, "seed": seed, "horizon_day": day,
                    "utility": sum(incomes), "gini": gini(incomes),
                    "variance": variance(incomes), "std": variance(incomes) ** 0.5,
                    "completed": checkpoints[day]["completed"],
                })
            print(f"[{ablation:12s} seed={seed}] done ({time.perf_counter()-t_cfg:.1f}s)", flush=True)
            del policy, res, checkpoints
            gc.collect()

    import csv
    with (OUT_DIR / "test_long_horizon.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(horizon_rows[0].keys()))
        w.writeheader()
        w.writerows(horizon_rows)
    with (OUT_DIR / "test_policy_disagreement.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["seed", "disagreement_rate"])
        w.writeheader()
        w.writerows(disagreement_rows)

    print(f"[done] wrote {len(horizon_rows)} rows to test_long_horizon.csv, "
          f"{len(disagreement_rows)} rows to test_policy_disagreement.csv", flush=True)
    mean_d = sum(r["disagreement_rate"] for r in disagreement_rows) / len(disagreement_rows)
    print(f"[summary] mean policy disagreement rate (full vs no_forecast) = {mean_d:.4f}", flush=True)


if __name__ == "__main__":
    main()
