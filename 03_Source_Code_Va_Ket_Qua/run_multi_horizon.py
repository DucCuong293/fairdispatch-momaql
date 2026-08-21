"""Multi-horizon replication study: traces Full/No-Forecast/No-Fairness
fairness & utility as the evaluation horizon grows from day 1 to day 37
(the full val.parquet span), on ONE real trajectory per (config, seed) --
not independent reruns per checkpoint.
Also measures the policy disagreement rate D = P(pi_full != pi_no_forecast)
on identical candidate sets during the Full run.
Writes reports/multi_horizon_results.csv and reports/policy_disagreement.csv.
"""
import gc
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np

from simulator import run_simulation_with_horizon
from policies import MOMAQLPolicy
from common_loader import load_requests_fast, gini

N_DRIVERS = 200
SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
HORIZON_DAYS = [1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 37]


def variance(xs):
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def main():
    val_path = Path(__file__).parent / "data" / "val.parquet"
    print("[load] reading val.parquet...", flush=True)
    reqs_full = load_requests_fast(val_path)
    t0 = reqs_full[0]["pickup_ts"]
    max_seconds = HORIZON_DAYS[-1] * 86400.0 + 3600.0  # +1h buffer past day 7
    reqs = [r for r in reqs_full if (r["pickup_ts"] - t0) <= max_seconds]
    del reqs_full
    gc.collect()
    print(f"[load] {len(reqs):,} real requests within the first {HORIZON_DAYS[-1]} days "
          f"(full split has 195,508 requests over ~37 days)", flush=True)

    q_path = Path(__file__).parent / "data" / "momaql_q_table_trained.json"
    with q_path.open("r", encoding="utf-8") as f:
        q_table = json.load(f)
    print(f"[q] using {q_path.name}", flush=True)

    horizon_rows = []
    disagreement_rows = []

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
    out_dir = Path(__file__).parent / "reports"
    with (out_dir / "multi_horizon_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(horizon_rows[0].keys()))
        w.writeheader()
        w.writerows(horizon_rows)
    with (out_dir / "policy_disagreement.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["seed", "disagreement_rate"])
        w.writeheader()
        w.writerows(disagreement_rows)

    print(f"[done] wrote {len(horizon_rows)} rows to multi_horizon_results.csv, "
          f"{len(disagreement_rows)} rows to policy_disagreement.csv", flush=True)

    mean_d = sum(r["disagreement_rate"] for r in disagreement_rows) / len(disagreement_rows)
    print(f"[summary] mean policy disagreement rate (full vs no_forecast) = {mean_d:.4f}", flush=True)


if __name__ == "__main__":
    main()
