"""Real R2 ablation: Full MOMAQL vs w/o Future Demand (Q_future=0) vs w/o
Fairness Reward (lambda=0), on val.parquet, 5 seeds each, using the
trained Q-table (frozen -- evaluation mode, no further learning)."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

from simulator import run_simulation_batched as run_simulation
from policies import MOMAQLPolicy
from common_loader import load_requests_fast, gini, variance, std, coefficient_of_variation

SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
N_DRIVERS = 200
ABLATIONS = ["full", "no_forecast", "no_fairness"]


def main():
    q_path = Path(__file__).parent / "data" / "momaql_q_table_multipass.json"
    if not q_path.exists():
        q_path = Path(__file__).parent / "data" / "momaql_q_table_trained.json"
    with q_path.open("r", encoding="utf-8") as f:
        q_table = json.load(f)
    print(f"[q] using {q_path.name}", flush=True)

    reqs = load_requests_fast(Path(__file__).parent / "data" / "val.parquet")
    print(f"[load] {len(reqs):,} real validation requests", flush=True)

    rows = []
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
                        "variance": var, "std": sd, "std_over_mean": cv})

    df = pd.DataFrame(rows)
    df.to_csv(Path(__file__).parent / "reports" / "r2_ablation_raw.csv", index=False)
    summary = df.groupby("ablation").agg(utility_mean=("utility", "mean"), utility_std=("utility", "std"),
                                         gini_mean=("gini", "mean"), gini_std=("gini", "std"),
                                         variance_mean=("variance", "mean"), std_mean=("std", "mean"),
                                         std_over_mean_mean=("std_over_mean", "mean")).round(4)
    print("\n=== R2 ABLATION SUMMARY ===")
    print(summary.loc[["full", "no_forecast", "no_fairness"]])
    summary.to_csv(Path(__file__).parent / "reports" / "r2_ablation_results.csv")
    print("[done]", flush=True)


if __name__ == "__main__":
    main()
