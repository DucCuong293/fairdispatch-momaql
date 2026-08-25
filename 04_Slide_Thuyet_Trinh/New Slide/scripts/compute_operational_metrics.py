"""READ-ONLY aggregation of existing experiment artifacts into operational
numbers for the slide deck. Does not touch the simulator, policies, or any
experiment output -- reads reports/*.csv and final_test/*.csv that already
exist on disk and writes one JSON summary next to this script's output dir.

No policy rerun, no Final Test rerun, no training, no config change.
"""
import json
import statistics
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3] / "03_Source_Code_Va_Ket_Qua"
REPORTS = ROOT / "reports"
FINAL_TEST = ROOT / "final_test"
DATA_DIR = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")

VAL_TOTAL_ROWS = 195508
TEST_EVALUATED_ROWS = 195506


def validation_service_rate():
    df = pd.read_csv(REPORTS / "r1_validation_results.csv")
    grp = df.groupby("policy")["completed_trips"].mean()
    return {
        policy: {
            "completed_trips_mean": round(val, 1),
            "service_rate_pct": round(100 * val / VAL_TOTAL_ROWS, 1),
        }
        for policy, val in grp.items()
    }


def validation_income_percentiles():
    df = pd.read_csv(REPORTS / "r1_validation_results.csv")
    grp = df.groupby("policy")[["p10", "p50", "p90"]].mean()
    return {
        policy: {k: round(v, 1) for k, v in row.items()}
        for policy, row in grp.iterrows()
    }


def test_baseline_operational():
    df = pd.read_csv(FINAL_TEST / "baseline" / "test_baseline_summary.csv")
    out = {}
    for _, row in df.iterrows():
        out[row["policy"]] = {
            "served_mean": round(row["served_mean"], 1),
            "service_rate_pct": round(100 * row["served_mean"] / TEST_EVALUATED_ROWS, 1),
            "avg_income_mean": round(row["avg_income_mean"], 2),
            "avg_deadhead_cost_usd": round(row["avg_deadhead_mean"], 4),
        }
    return out


def dataset_scale():
    train = 912375
    val = 195508
    test = 195510
    return {
        "train_rows": train,
        "validation_rows": val,
        "test_rows_raw": test,
        "test_rows_evaluated": TEST_EVALUATED_ROWS,
        "total_trips_train_val_test": train + val + test,
        "zones": 67,  # NYC TLC zone set used throughout project; see docs/techdoc, docs/docx_report
        "canonical_drivers": 200,  # N_DRIVERS in scripts/final_test/run_final_test_baselines.py
        "batch_window_seconds": 60.0,  # default window_seconds in src/simulator.py:run_simulation_batched
        "max_pickup_eta_seconds": 600.0,  # MAX_PICKUP_ETA_SECONDS in src/simulator.py
    }


def dataset_date_ranges():
    out = {}
    for name, fname in [("train", "train.parquet"), ("validation", "val.parquet"), ("test", "test.parquet")]:
        df = pd.read_parquet(DATA_DIR / fname, columns=["pickup_ts"])
        out[name] = {
            "start": str(df["pickup_ts"].min()),
            "end": str(df["pickup_ts"].max()),
            "rows": len(df),
        }
    return out


def test_ablation_gini_delta():
    df = pd.read_csv(FINAL_TEST / "ablation" / "test_ablation_results.csv")
    full = df.loc[df["ablation"] == "full", "gini_mean"].iloc[0]
    nf = df.loc[df["ablation"] == "no_forecast", "gini_mean"].iloc[0]
    return {
        "full_gini": round(full, 4),
        "no_forecast_gini": round(nf, 4),
        "delta_no_forecast_minus_full": round(nf - full, 4),
    }


def fleet_scale_service_rate():
    df = pd.read_csv(REPORTS / "fleet_scale_results.csv")
    grp = df.groupby(["n_drivers", "ablation"])["completed"].mean()
    return {
        f"{n}_{ab}": {
            "completed_mean": round(val, 1),
            "service_rate_pct": round(100 * val / VAL_TOTAL_ROWS, 1),
        }
        for (n, ab), val in grp.items()
    }


def experiment_scale():
    r1 = pd.read_csv(REPORTS / "r1_validation_results.csv")
    r2 = pd.read_csv(REPORTS / "r2_ablation_raw.csv")
    mh = pd.read_csv(REPORTS / "multi_horizon_results.csv")
    fs = pd.read_csv(REPORTS / "fleet_scale_results.csv")
    return {
        "baseline_policies": r1["policy"].nunique(),
        "baseline_seeds": r1["seed"].nunique(),
        "baseline_runs": len(r1),
        "ablation_variants": r2["ablation"].nunique(),
        "ablation_seeds": r2["seed"].nunique(),
        "long_horizon_checkpoints": mh["horizon_day"].nunique(),
        "fleet_scale_sizes": sorted(fs["n_drivers"].unique().tolist()),
    }


def main():
    out = {
        "dataset_scale": dataset_scale(),
        "dataset_date_ranges": dataset_date_ranges(),
        "experiment_scale": experiment_scale(),
        "validation_service_rate_by_policy": validation_service_rate(),
        "validation_income_percentiles_by_policy": validation_income_percentiles(),
        "test_baseline_operational_by_policy": test_baseline_operational(),
        "fleet_scale_service_rate": fleet_scale_service_rate(),
        "test_ablation_gini_delta": test_ablation_gini_delta(),
    }
    out_path = Path(__file__).resolve().parent.parent / "assets" / "charts" / "operational_metrics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
