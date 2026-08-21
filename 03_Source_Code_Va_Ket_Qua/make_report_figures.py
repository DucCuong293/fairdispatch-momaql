"""Generates the 3 comparison figures used in docs/ (LaTeX papers + docx
report) from the real CSV results in reports/. Run after any rerun of
run_r1.py / run_r2_ablation.py / run_pareto_frontier.py to refresh figures.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
OUT_DIRS = [
    ROOT / "docs" / "ride_hailing_fairness_report_en" / "figures",
    ROOT / "docs" / "ride_hailing_fairness_report_vi" / "figures",
    ROOT / "docs" / "docx_report" / "figures",
]

POLICY_ORDER = ["MOMAQL", "LAF", "Greedy", "Nearest", "Exact REASSIGN"]
COLORS = {"MOMAQL": "#1f77b4", "LAF": "#2ca02c", "Greedy": "#d62728",
          "Nearest": "#ff7f0e", "Exact REASSIGN": "#9467bd"}


def save_all(fig, name):
    for d in OUT_DIRS:
        fig.savefig(d / name, dpi=200, bbox_inches="tight")


def fig_r1():
    df = pd.read_csv(REPORTS / "r1_validation_results.csv")
    agg = df.groupby("policy").agg(
        utility_mean=("utility", "mean"), utility_std=("utility", "std"),
        gini_mean=("gini", "mean"),
    ).loc[POLICY_ORDER]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    colors = [COLORS[p] for p in POLICY_ORDER]

    ax1.bar(POLICY_ORDER, agg["utility_mean"] / 1000, yerr=agg["utility_std"] / 1000,
            color=colors, capsize=4)
    ax1.set_ylabel("Total Utility (thousand USD)")
    ax1.set_title("R1: Utility by Policy (5 seeds, val split)")
    ax1.tick_params(axis="x", rotation=25)

    ax2.bar(POLICY_ORDER, agg["gini_mean"], color=colors)
    ax2.set_ylabel("Gini coefficient (income inequality)")
    ax2.set_title("R1: Fairness by Policy")
    ax2.tick_params(axis="x", rotation=25)

    fig.tight_layout()
    save_all(fig, "r1_validation_unified_comparison.png")
    plt.close(fig)


def fig_r2():
    df = pd.read_csv(REPORTS / "r2_ablation_raw.csv") if (REPORTS / "r2_ablation_raw.csv").exists() \
        else pd.read_csv(REPORTS / "r2_ablation_results.csv")
    order = ["full", "no_forecast", "no_fairness"]
    labels = ["Full\n(Q(zone,hour)+Fairness)", "w/o Forecast\n(Q=0)", "w/o Fairness\n(lambda=0)"]
    agg = df.groupby("ablation").agg(utility_mean=("utility", "mean"), utility_std=("utility", "std"),
                                      gini_mean=("gini", "mean")).loc[order]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    colors = ["#1f77b4", "#7f7f7f", "#d62728"]
    ax1.bar(labels, agg["utility_mean"] / 1000, yerr=agg["utility_std"] / 1000, color=colors, capsize=4)
    ax1.set_ylabel("Total Utility (thousand USD)")
    ax1.set_title("R2 Ablation: Utility")

    ax2.bar(labels, agg["gini_mean"], color=colors)
    ax2.set_ylabel("Gini coefficient")
    ax2.set_title("R2 Ablation: Fairness")

    fig.tight_layout()
    save_all(fig, "r2_ablation_unified_comparison.png")
    plt.close(fig)


def fig_pareto():
    df = pd.read_csv(REPORTS / "pareto_frontier_summary.csv")
    df = df.sort_values("lambda")

    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.errorbar(df["utility_mean"] / 1000, df["gini_mean"], xerr=df["utility_std"] / 1000,
                yerr=df["gini_std"], fmt="o-", color="#1f77b4", capsize=3)
    for _, row in df.iterrows():
        ax.annotate(f"$\\lambda$={row['lambda']:.1f}", (row["utility_mean"] / 1000, row["gini_mean"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.set_xlabel("Total Utility (thousand USD)")
    ax.set_ylabel("Gini coefficient (income inequality)")
    ax.set_title("MOMAQL Pareto Frontier: Utility vs. Fairness")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    save_all(fig, "pareto_frontier_unified_curve.png")
    plt.close(fig)


def fig_horizon_2phase():
    df = pd.read_csv(REPORTS / "multi_horizon_results.csv")
    agg = df.groupby(["config", "horizon_day"]).agg(
        utility_mean=("utility", "mean")).reset_index()
    full = agg[agg["config"] == "full"].set_index("horizon_day")["utility_mean"]
    nf = agg[agg["config"] == "no_forecast"].set_index("horizon_day")["utility_mean"]
    days = sorted(set(full.index) & set(nf.index))
    pct = [(full[d] - nf[d]) / nf[d] * 100 for d in days]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2))

    phase1_days = [d for d in days if d <= 7]
    ax1.plot(phase1_days, [full[d] / 1000 for d in phase1_days], "o-", label="Full", color="#1f77b4")
    ax1.plot(phase1_days, [nf[d] / 1000 for d in phase1_days], "s--", label="w/o Forecast", color="#7f7f7f")
    ax1.set_xlabel("Day (1-7)")
    ax1.set_ylabel("Cumulative Utility (thousand USD)")
    ax1.set_title("Phase 1 (days 1-7): tied")
    ax1.legend(fontsize=8)

    ax2.plot(days, pct, "o-", color="#d62728")
    ax2.axhline(0, color="#999", linewidth=0.8)
    ax2.set_xlabel("Day (1-37)")
    ax2.set_ylabel("Full advantage over w/o-Forecast (%)")
    ax2.set_title("Phase 2 (days 8-37): divergence")
    for d, p in zip(days, pct):
        if d in (7, 14, 21, 28, 37):
            ax2.annotate(f"{p:.1f}%", (d, p), textcoords="offset points", xytext=(0, 6), fontsize=8, ha="center")

    fig.tight_layout()
    save_all(fig, "multi_horizon_2phase_breakthrough.png")
    plt.close(fig)


def fig_horizon():
    df = pd.read_csv(REPORTS / "multi_horizon_results.csv")
    agg = df.groupby(["config", "horizon_day"]).agg(
        utility_mean=("utility", "mean"), gini_mean=("gini", "mean")).reset_index()
    order = ["full", "no_forecast", "no_fairness"]
    labels = {"full": "Full", "no_forecast": "w/o Forecast", "no_fairness": "w/o Fairness"}
    colors = {"full": "#1f77b4", "no_forecast": "#7f7f7f", "no_fairness": "#d62728"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    for cfg in order:
        sub = agg[agg["config"] == cfg].sort_values("horizon_day")
        ax1.plot(sub["horizon_day"], sub["utility_mean"] / 1000, "o-", label=labels[cfg], color=colors[cfg])
        ax2.plot(sub["horizon_day"], sub["gini_mean"], "o-", label=labels[cfg], color=colors[cfg])
    ax1.set_xlabel("Evaluation horizon (days)")
    ax1.set_ylabel("Cumulative Utility (thousand USD)")
    ax1.set_title("Utility vs. Horizon")
    ax1.legend(fontsize=8)
    ax2.set_xlabel("Evaluation horizon (days)")
    ax2.set_ylabel("Gini coefficient")
    ax2.set_title("Fairness vs. Horizon")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    save_all(fig, "multi_horizon_unified_curve.png")
    plt.close(fig)


def fig_pipeline():
    stages = ["Real NYC TLC\n2013 trips", "Manhattan +\nquality filter", "67 TLC\ntaxi zones",
              "Tabular Q(zone,hour)\nBellman TD(0)", "60s-window\nbatched simulator",
              "Hungarian M-to-N\nassignment", "Utility / Gini /\nvariance metrics"]
    fig, ax = plt.subplots(figsize=(12, 2.2))
    ax.set_xlim(0, len(stages))
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, s in enumerate(stages):
        ax.add_patch(plt.Rectangle((i + 0.05, 0.25), 0.9, 0.5, fill=True,
                                    facecolor="#eaf1fb", edgecolor="#1f77b4", linewidth=1.3))
        ax.text(i + 0.5, 0.5, s, ha="center", va="center", fontsize=8.3)
        if i < len(stages) - 1:
            ax.annotate("", xy=(i + 1.05, 0.5), xytext=(i + 0.97, 0.5),
                        arrowprops=dict(arrowstyle="-|>", color="#444", lw=1.3))
    fig.tight_layout()
    save_all(fig, "replication_pipeline.png")
    plt.close(fig)


def fig_scale_and_convergence():
    fleet = pd.read_csv(REPORTS / "fleet_scale_results.csv")
    fagg = fleet.groupby(["n_drivers", "ablation"]).agg(utility_mean=("utility", "mean")).reset_index()
    conv = pd.read_csv(REPORTS / "q_table_convergence_daily.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2))

    for cfg, label, color in [("full", "Full", "#1f77b4"), ("no_forecast", "w/o Forecast", "#7f7f7f")]:
        sub = fagg[fagg["ablation"] == cfg].sort_values("n_drivers")
        ax1.plot(sub["n_drivers"], sub["utility_mean"] / 1000, "o-", label=label, color=color)
    ax1.set_xlabel("Fleet size (N drivers)")
    ax1.set_ylabel("Total Utility (thousand USD)")
    ax1.set_title("Scalability: Utility vs. Fleet Size")
    ax1.set_xticks([100, 200, 400])
    ax1.legend(fontsize=8)

    ax2b = ax2.twinx()
    l1, = ax2.plot(conv["day"], conv["mean_abs_delta_q_vs_prev_day"], "o-", color="#d62728", label="Mean |ΔQ|")
    l2, = ax2b.plot(conv["day"], conv["n_states_visited"], "s--", color="#1f77b4", label="States visited")
    ax2.set_xlabel("Training day")
    ax2.set_ylabel("Mean |ΔQ| (TD residual)", color="#d62728")
    ax2b.set_ylabel("Cumulative (zone,hour) states visited", color="#1f77b4")
    ax2.set_title("Training: Q-table Convergence (37 days)")
    ax2.legend(handles=[l1, l2], fontsize=8, loc="center right")

    fig.tight_layout()
    save_all(fig, "scale_and_convergence.png")
    plt.close(fig)


if __name__ == "__main__":
    for d in OUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    fig_r1()
    fig_r2()
    fig_pareto()
    fig_horizon()
    fig_horizon_2phase()
    fig_pipeline()
    fig_scale_and_convergence()
    print("wrote 7 figures to", *[str(d) for d in OUT_DIRS], sep="\n  ")
