"""Gate 2 (dataset integrity): audits train/val/test.parquet BEFORE any
policy is run on test.parquet. Verifies temporal non-overlap, checksum
match against reports/dataset_checksums.json, and profiles test.parquet
(row count, schema, time range, days, zones, missing/invalid values, fare/
duration distribution, per-day/per-hour counts, weekday/weekend split).

Writes final_test/test_dataset_audit.json and final_test/split_integrity.json.
Run BEFORE FINAL_TEST_PROTOCOL.md is frozen -- this is data audit, not
policy-outcome inspection (per protocol section 12/72/73).
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
DEV_DATA = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")
FINAL_TEST_DIR = ROOT / "final_test"
CHECKSUM_MANIFEST = ROOT / "reports" / "dataset_checksums.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pickup_ts(path: Path) -> np.ndarray:
    table = pq.read_table(path, columns=["pickup_ts"])
    p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
    return p_ts.astype("datetime64[s]").astype("int64")


def audit_dataset(name: str, path: Path) -> dict:
    table = pq.read_table(path)
    n = table.num_rows
    schema = [f"{f.name}:{f.type}" for f in table.schema]

    abs_sec = load_pickup_ts(path)
    days_since_epoch = abs_sec // 86400
    weekday = (days_since_epoch + 3) % 7  # 1970-01-01=Thu; Mon=0..Sun=6

    p_lat = table["pickup_latitude"].to_numpy()
    p_lon = table["pickup_longitude"].to_numpy()
    d_lat = table["dropoff_latitude"].to_numpy()
    d_lon = table["dropoff_longitude"].to_numpy()
    fares = table["fare_amount"].to_numpy()
    durs = table["duration_seconds"].to_numpy()
    p_zids = table["pickup_zone_id"].to_pylist()
    d_zids = table["dropoff_zone_id"].to_pylist()

    def missing_count(col):
        arr = table[col]
        return int(arr.null_count)

    invalid_coords = int(np.sum(
        (p_lat < 40.0) | (p_lat > 41.5) | (p_lon < -75.0) | (p_lon > -73.0) |
        (d_lat < 40.0) | (d_lat > 41.5) | (d_lon < -75.0) | (d_lon > -73.0)
    ))

    t0, t1 = int(abs_sec.min()), int(abs_sec.max())
    n_days = int((t1 - t0) // 86400) + 1

    hour = (abs_sec // 3600) % 24
    per_hour = Counter(int(h) for h in hour)
    per_day_idx = (abs_sec - t0) // 86400
    per_day = Counter(int(d) for d in per_day_idx)
    weekday_counts = Counter(int(w) for w in weekday)
    n_weekday = sum(c for wd, c in weekday_counts.items() if wd <= 4)
    n_weekend = sum(c for wd, c in weekday_counts.items() if wd >= 5)

    return {
        "dataset": name, "path": str(path), "row_count": n,
        "schema": schema,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "time_range": {
            "min_epoch_seconds": t0, "max_epoch_seconds": t1,
            "min_iso": np.datetime64(t0, "s").astype(str),
            "max_iso": np.datetime64(t1, "s").astype(str),
            "n_calendar_days_spanned": n_days,
        },
        "unique_pickup_zones": len(set(p_zids)),
        "unique_dropoff_zones": len(set(d_zids)),
        "missing_value_counts": {
            "pickup_ts": missing_count("pickup_ts"),
            "pickup_zone_id": missing_count("pickup_zone_id"),
            "dropoff_zone_id": missing_count("dropoff_zone_id"),
            "fare_amount": missing_count("fare_amount"),
            "duration_seconds": missing_count("duration_seconds"),
        },
        "invalid_coordinate_count": invalid_coords,
        "fare_distribution": {
            "mean": float(np.mean(fares)), "median": float(np.median(fares)),
            "std": float(np.std(fares)), "min": float(np.min(fares)), "max": float(np.max(fares)),
        },
        "duration_distribution": {
            "mean": float(np.mean(durs)), "median": float(np.median(durs)),
            "std": float(np.std(durs)), "min": float(np.min(durs)), "max": float(np.max(durs)),
        },
        "requests_per_day": dict(sorted(per_day.items())),
        "requests_per_hour": dict(sorted(per_hour.items())),
        "weekday_weekend": {"weekday": n_weekday, "weekend": n_weekend,
                             "weekday_pct": round(100 * n_weekday / n, 2), "weekend_pct": round(100 * n_weekend / n, 2)},
    }


def main():
    FINAL_TEST_DIR.mkdir(parents=True, exist_ok=True)

    with CHECKSUM_MANIFEST.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("[audit] profiling train/val/test.parquet...", flush=True)
    train_audit = audit_dataset("train", DEV_DATA / "train.parquet")
    val_audit = audit_dataset("val", DEV_DATA / "val.parquet")
    test_audit = audit_dataset("test", DEV_DATA / "test.parquet")

    checksum_status = {}
    for name, audit in (("train.parquet", train_audit), ("val.parquet", val_audit), ("test.parquet", test_audit)):
        expected = manifest.get(name, {}).get("sha256")
        actual = audit["sha256"]
        checksum_status[name] = {"expected": expected, "actual": actual, "match": expected == actual}
        print(f"[checksum] {name}: {'OK' if expected == actual else 'MISMATCH'}", flush=True)

    train_max = train_audit["time_range"]["max_epoch_seconds"]
    val_min = val_audit["time_range"]["min_epoch_seconds"]
    val_max = val_audit["time_range"]["max_epoch_seconds"]
    test_min = test_audit["time_range"]["min_epoch_seconds"]

    train_before_val = train_max < val_min
    val_before_test_raw = val_max < test_min

    # Real finding (documented + user-confirmed decision): val.parquet's LAST
    # request and test.parquet's FIRST 3 requests share the exact same
    # boundary second (val_max == test_min). This is a genuine row-index
    # split artifact (multiple real NYC pickups landed in the same second at
    # the cut point) -- NOT duplicated rows. Per explicit decision, the tied
    # rows on the test side are excluded so the boundary becomes strictly
    # val_max < test_min_filtered before ANY policy touches test.parquet.
    test_table = pq.read_table(DEV_DATA / "test.parquet", columns=["pickup_ts"])
    test_abs_sec = test_table["pickup_ts"].to_numpy(zero_copy_only=False).astype("datetime64[s]").astype("int64")
    boundary_tie_mask = test_abs_sec == val_max
    n_excluded = int(boundary_tie_mask.sum())
    test_min_filtered = int(test_abs_sec[~boundary_tie_mask].min()) if n_excluded < len(test_abs_sec) else None
    val_before_test_filtered = (test_min_filtered is not None) and (val_max < test_min_filtered)

    split_integrity = {
        "train_max_epoch_seconds": train_max, "val_min_epoch_seconds": val_min,
        "val_max_epoch_seconds": val_max, "test_min_epoch_seconds": test_min,
        "train_before_val": train_before_val,
        "val_before_test_raw": val_before_test_raw,
        "boundary_tie": {
            "note": "val's last row and test's first N rows share epoch second val_max==test_min "
                    "(distinct real NYC pickups in the same second at the row-index split cut, not duplicated data). "
                    "Excluded from test.parquet's LOADED view (file on disk unmodified) for all Final Test runs.",
            "boundary_epoch_second": int(val_max),
            "test_rows_excluded": n_excluded,
            "test_min_epoch_seconds_after_exclusion": test_min_filtered,
        },
        "val_before_test_after_boundary_fix": val_before_test_filtered,
        "no_temporal_overlap": train_before_val and val_before_test_filtered,
        "test_n_days": test_audit["time_range"]["n_calendar_days_spanned"],
    }
    print(f"[split] train < val: {train_before_val}  |  val < test (raw): {val_before_test_raw}  |  "
          f"val < test (after excluding {n_excluded} boundary-tied test rows): {val_before_test_filtered}", flush=True)

    all_checksums_ok = all(v["match"] for v in checksum_status.values())
    blocker = None
    if not split_integrity["no_temporal_overlap"]:
        blocker = "TEMPORAL_OVERLAP"
    elif not all_checksums_ok:
        blocker = "CHECKSUM_MISMATCH"

    (FINAL_TEST_DIR / "test_dataset_audit.json").write_text(
        json.dumps({"train": train_audit, "val": val_audit, "test": test_audit}, indent=2), encoding="utf-8")
    (FINAL_TEST_DIR / "split_integrity.json").write_text(
        json.dumps({"split_integrity": split_integrity, "checksums": checksum_status, "blocker": blocker}, indent=2),
        encoding="utf-8")

    print(f"[done] wrote test_dataset_audit.json + split_integrity.json. blocker={blocker}", flush=True)
    if blocker:
        raise SystemExit(f"GATE 2 BLOCKED: {blocker}")


if __name__ == "__main__":
    main()
