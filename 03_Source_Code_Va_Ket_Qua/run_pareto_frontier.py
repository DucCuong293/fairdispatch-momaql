"""Real Pareto frontier sweep: MOMAQL with lambda in {0.0,0.2,0.4,0.5,0.6,
0.8,1.0} on val.parquet (195,508 real requests), 5 seeds each, using the
multi-pass trained Q-table (falls back to the single-pass one if the
multi-pass run hasn't finished yet)."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd

from simulator import run_simulation_batched as run_simulation
from policies import MOMAQLPolicy
from common_loader import load_requests_fast, gini, variance, std

LAMBDAS = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
N_DRIVERS = 200


def main():
    q_path = Path(__file__).parent / "data" / "momaql_q_table_multipass.json"
    if not q_path.exists():
        q_path = Path(__file__).parent / "data" / "momaql_q_table_trained.json"
    with q_path.open("r", encoding="utf-8") as f:
        q_table = json.load(f)
    print(f"[q] using {q_path.name} ({len(q_table)} zones)", flush=True)

    reqs = load_requests_fast(Path(__file__).parent / "data" / "val.parquet")
    print(f"[load] {len(reqs):,} real validation requests", flush=True)

    rows = []
    for lam in LAMBDAS:
        for seed in SEEDS:
            t0 = time.perf_counter()
            policy = MOMAQLPolicy(lam=lam, q_table=q_table, frozen=True)
            res = run_simulation(reqs, n_drivers=N_DRIVERS, policy=policy, seed=seed)
            incomes = list(res.per_driver_income.values())
            g = gini(incomes)
            u = sum(incomes)
            var = variance(incomes)
            sd = std(incomes)
            el = time.perf_counter() - t0
            print(f"[lambda={lam:.1f} seed={seed}] Utility=${u:,.1f} Gini={g:.4f} Var={var:,.1f} "
                 f"trips={res.total_completed} ({el:.1f}s)", flush=True)
            rows.append({"lambda": lam, "seed": seed, "utility": u, "gini": g,
                        "variance": var, "std": sd, "n_completed": res.total_completed})

    df = pd.DataFrame(rows)
    out_csv = Path(__file__).parent / "reports" / "pareto_frontier_results.csv"
    df.to_csv(out_csv, index=False)
    summary = df.groupby("lambda").agg(utility_mean=("utility", "mean"), utility_std=("utility", "std"),
                                       gini_mean=("gini", "mean"), gini_std=("gini", "std"),
                                       variance_mean=("variance", "mean"), std_mean=("std", "mean")).round(4)
    print("\n=== PARETO SUMMARY ===")
    print(summary)
    summary.to_csv(Path(__file__).parent / "reports" / "pareto_frontier_summary.csv")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.errorbar(summary["utility_mean"], summary["gini_mean"],
                   xerr=summary["utility_std"], yerr=summary["gini_std"],
                   marker="o", linestyle="-", color="#0072B2")
        for lam, row in summary.iterrows():
            ax.annotate(f"λ={lam}", (row["utility_mean"], row["gini_mean"]),
                       textcoords="offset points", xytext=(6, 4), fontsize=8)
        ax.set_xlabel("Utility (tổng thu nhập, $)")
        ax.set_ylabel("Gini (thấp hơn = công bằng hơn)")
        ax.set_title("Đường biên Pareto MOMAQL — quét λ (dữ liệu thật, val.parquet)")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(Path(__file__).parent / "reports" / "pareto_frontier.png", dpi=150)
        print("[fig] wrote reports/pareto_frontier.png", flush=True)
    except ImportError:
        print("[skip] matplotlib not available, skipping PNG", flush=True)

    print("[done]", flush=True)


if __name__ == "__main__":
    main()
