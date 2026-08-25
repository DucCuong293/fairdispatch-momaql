"""READ-ONLY profile of the real train/val/test parquet files used by
FairDispatch. Does not modify any parquet, does not rerun any policy
experiment -- reads columns and computes aggregates only, writes one JSON
summary.
"""
import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")
OUT_PATH = Path(__file__).resolve().parent.parent / "assets" / "charts" / "dataset_profile.json"

COLUMNS = [
    "pickup_ts", "duration_seconds", "fare_amount", "trip_distance_miles",
    "pickup_zone_id", "dropoff_zone_id",
]


def load_all():
    frames = []
    for name in ("train", "val", "test"):
        df = pd.read_parquet(DATA_DIR / f"{name}.parquet", columns=COLUMNS)
        df["split"] = name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def main():
    df = load_all()
    df["pickup_hour"] = df["pickup_ts"].dt.hour
    df["pickup_date"] = df["pickup_ts"].dt.date

    trips_by_hour = df.groupby("pickup_hour").size()
    trips_by_hour_pct = (trips_by_hour / len(df) * 100).round(2)

    trips_by_day = df.groupby("pickup_date").size()

    top_pickup_zones = df["pickup_zone_id"].value_counts().head(10)

    out = {
        "total_trips": int(len(df)),
        "date_range": {
            "start": str(df["pickup_ts"].min()),
            "end": str(df["pickup_ts"].max()),
        },
        "days_observed": int(df["pickup_date"].nunique()),
        "pickup_zones_seen": int(df["pickup_zone_id"].nunique()),
        "dropoff_zones_seen": int(df["dropoff_zone_id"].nunique()),
        "trips_per_day": {
            "mean": round(float(trips_by_day.mean()), 1),
            "median": round(float(trips_by_day.median()), 1),
            "min": int(trips_by_day.min()),
            "max": int(trips_by_day.max()),
        },
        "trips_by_hour_count": {int(h): int(v) for h, v in trips_by_hour.items()},
        "trips_by_hour_pct": {int(h): float(v) for h, v in trips_by_hour_pct.items()},
        "peak_hour": {
            "hour": int(trips_by_hour.idxmax()),
            "pct": float(trips_by_hour_pct.max()),
        },
        "trough_hour": {
            "hour": int(trips_by_hour.idxmin()),
            "pct": float(trips_by_hour_pct.min()),
        },
        "top_pickup_zones": {int(z): int(c) for z, c in top_pickup_zones.items()},
        "fare_amount_usd": {
            "median": round(float(df["fare_amount"].median()), 2),
            "p25": round(float(df["fare_amount"].quantile(0.25)), 2),
            "p75": round(float(df["fare_amount"].quantile(0.75)), 2),
            "p90": round(float(df["fare_amount"].quantile(0.90)), 2),
        },
        "duration_seconds": {
            "median": round(float(df["duration_seconds"].median()), 1),
            "p90": round(float(df["duration_seconds"].quantile(0.90)), 1),
        },
        "trip_distance_miles": {
            "median": round(float(df["trip_distance_miles"].median()), 2),
            "p90": round(float(df["trip_distance_miles"].quantile(0.90)), 2),
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
