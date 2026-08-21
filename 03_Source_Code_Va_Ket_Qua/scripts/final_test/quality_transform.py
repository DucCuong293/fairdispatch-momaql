"""Shared, deterministic quality transform used by every Final Test script
(audit, verify, baseline, ablation, long-horizon). Defined and frozen BEFORE
any policy touches test.parquet -- see final_test/FINAL_TEST_PROTOCOL.md.

Two INDEPENDENT rules, applied in this exact order, never mixed:

1. Temporal-boundary hygiene (split integrity, not a data-quality rule):
   val.parquet's last row and test.parquet's first N rows share the exact
   same epoch second (real distinct NYC pickups landed in the same second
   at the row-index split cut -- not duplicated rows). Those test-side rows
   are excluded from the evaluation view so max(val) < min(test) holds
   strictly. Train/val are never affected by this rule.

2. Duration-quality minimal deterministic repair (see
   final_test/DATA_QUALITY_GATE.md for the full audit): `duration_seconds`
   is a derived field that is corrupted for a handful of test.parquet rows;
   pickup_ts/dropoff_ts are authoritative and, for all but one of those
   rows, recover a valid 0 < duration <= 24h. Only the one row where the
   recovered duration is ALSO invalid (pickup_ts == dropoff_ts, i.e. a
   computed duration of exactly 0) is excluded -- everything else is
   repaired from timestamps, never discarded.

Applied identically (uniform code path) to train/val/test; train/val are
expected (and asserted) to have zero repairs/exclusions from rule 2, since
the duration audit found the corruption only in test.parquet.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import pyarrow.parquet as pq

from common_loader import gini, variance, std, coefficient_of_variation  # noqa: F401 (re-exported for run scripts)

MAX_DURATION_SECONDS = 24 * 3600


def load_requests_with_quality_transform(path: Path, boundary_exclude_epoch_second: int | None = None) -> tuple[list[dict], dict]:
    """Loads a parquet split (train/val/test) and returns
    (requests_ready_for_simulator, stats) where stats records exactly what
    the transform did -- nothing here is silent.

    requests_ready_for_simulator uses the SAME dict shape as
    common_loader.load_requests_fast (pickup_ts relative to this filtered
    view's own first real row, pickup_hour/dropoff_hour from real absolute
    time), except duration_seconds is duration_seconds_eval (repaired where
    needed) and each dict also carries duration_seconds_raw + quality_action
    for full auditability.
    """
    table = pq.read_table(path, columns=[
        "pickup_ts", "dropoff_ts", "pickup_latitude", "pickup_longitude",
        "dropoff_latitude", "dropoff_longitude", "fare_amount",
        "duration_seconds", "pickup_zone_id", "dropoff_zone_id",
    ])
    p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
    d_ts = table["dropoff_ts"].to_numpy(zero_copy_only=False)
    abs_sec = p_ts.astype("datetime64[s]").astype("int64")
    dropoff_abs_sec = d_ts.astype("datetime64[s]").astype("int64")
    computed_duration = (dropoff_abs_sec - abs_sec).astype("int64")
    raw_duration = table["duration_seconds"].to_numpy(zero_copy_only=False)

    p_lat = table["pickup_latitude"].to_numpy()
    p_lon = table["pickup_longitude"].to_numpy()
    d_lat = table["dropoff_latitude"].to_numpy()
    d_lon = table["dropoff_longitude"].to_numpy()
    fares = table["fare_amount"].to_numpy()
    p_zids = table["pickup_zone_id"].to_pylist()
    z_ids = table["dropoff_zone_id"].to_pylist()
    n = len(p_lat)

    # ---- rule 1: temporal-boundary hygiene ----
    boundary_mask = np.zeros(n, dtype=bool)
    n_boundary_excluded = 0
    if boundary_exclude_epoch_second is not None:
        boundary_mask = abs_sec == boundary_exclude_epoch_second
        n_boundary_excluded = int(boundary_mask.sum())

    # ---- rule 2: duration-quality minimal deterministic repair ----
    raw_valid = (raw_duration > 0) & (raw_duration <= MAX_DURATION_SECONDS)
    computed_valid = (computed_duration > 0) & (computed_duration <= MAX_DURATION_SECONDS)
    repaired_mask = (~raw_valid) & computed_valid
    duration_invalid_mask = (~raw_valid) & (~computed_valid)  # irrecoverable -> excluded

    duration_eval = np.where(raw_valid, raw_duration, np.where(repaired_mask, computed_duration, raw_duration)).astype(float)

    keep_mask = (~boundary_mask) & (~duration_invalid_mask)

    quality_action = np.full(n, "KEPT_RAW", dtype=object)
    quality_action[repaired_mask] = "REPAIRED_FROM_TIMESTAMPS"
    quality_action[duration_invalid_mask] = "EXCLUDED_INVALID_DURATION"
    quality_action[boundary_mask] = "EXCLUDED_TEMPORAL_BOUNDARY"

    kept_idx = np.nonzero(keep_mask)[0]
    if len(kept_idx) == 0:
        raise ValueError(f"quality transform excluded ALL rows of {path} -- refusing to return an empty evaluation view")
    t0 = int(abs_sec[kept_idx].min())
    ts_rel = (abs_sec[kept_idx] - t0).astype(float)
    p_hours = ((abs_sec[kept_idx] // 3600) % 24).astype(int)
    dur_kept = duration_eval[kept_idx]
    d_hours = (((abs_sec[kept_idx] + dur_kept.astype("int64")) // 3600) % 24).astype(int)

    requests = [
        {
            "_idx": i, "pickup_ts": float(ts_rel[j]),
            "pickup_latitude": float(p_lat[i]), "pickup_longitude": float(p_lon[i]),
            "dropoff_latitude": float(d_lat[i]), "dropoff_longitude": float(d_lon[i]),
            "fare_amount": float(fares[i]),
            "duration_seconds": float(dur_kept[j]),
            "duration_seconds_raw": float(raw_duration[i]), "quality_action": str(quality_action[i]),
            "pickup_zone_id": p_zids[i], "dropoff_zone_id": z_ids[i],
            "pickup_hour": int(p_hours[j]), "dropoff_hour": int(d_hours[j]),
        }
        for j, i in enumerate(kept_idx)
    ]

    stats = {
        "path": str(path), "original_rows": int(n),
        "temporal_boundary_excluded": n_boundary_excluded,
        "duration_repaired": int(repaired_mask.sum()),
        "duration_excluded": int(duration_invalid_mask.sum()),
        "final_evaluated_rows": len(requests),
        "excluded_row_ids": {
            "temporal_boundary": [int(i) for i in np.nonzero(boundary_mask)[0]],
            "duration_invalid": [int(i) for i in np.nonzero(duration_invalid_mask)[0]],
        },
        "repaired_row_ids": [int(i) for i in np.nonzero(repaired_mask)[0]],
        "t0_epoch_seconds": t0,
    }
    return requests, stats


if __name__ == "__main__":
    import json
    ROOT = Path(__file__).resolve().parents[2]
    DEV_DATA = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")
    val_max_epoch = 1374412620  # frozen from final_test/split_integrity.json (val.parquet's real max pickup_ts)

    results = {}
    for name, path, boundary in (("train", DEV_DATA / "train.parquet", None),
                                  ("val", DEV_DATA / "val.parquet", None),
                                  ("test", DEV_DATA / "test.parquet", val_max_epoch)):
        reqs, stats = load_requests_with_quality_transform(path, boundary_exclude_epoch_second=boundary)
        # assertions -- fail loudly, never silently pass bad data downstream
        durs = np.array([r["duration_seconds"] for r in reqs])
        assert (durs > 0).all(), f"{name}: found duration_seconds_eval <= 0 in evaluation view"
        assert (durs <= MAX_DURATION_SECONDS).all(), f"{name}: found duration_seconds_eval > 24h in evaluation view"
        results[name] = stats
        print(f"[{name}] original={stats['original_rows']} boundary_excluded={stats['temporal_boundary_excluded']} "
              f"repaired={stats['duration_repaired']} duration_excluded={stats['duration_excluded']} "
              f"final={stats['final_evaluated_rows']}", flush=True)

    # cross-check: boundary rows and duration-invalid rows must not overlap
    test_boundary = set(results["test"]["excluded_row_ids"]["temporal_boundary"])
    test_dur_invalid = set(results["test"]["excluded_row_ids"]["duration_invalid"])
    overlap = test_boundary & test_dur_invalid
    assert not overlap, f"boundary and duration-invalid exclusions overlap unexpectedly: {overlap}"
    print(f"[assert] boundary exclusions ({len(test_boundary)}) and duration-invalid exclusions "
          f"({len(test_dur_invalid)}) do not overlap: OK", flush=True)

    # expectation check (computed, not hard-coded): train/val must have zero
    # duration repairs/exclusions per the audit
    assert results["train"]["duration_repaired"] == 0 and results["train"]["duration_excluded"] == 0, \
        "unexpected duration repair/exclusion in train.parquet -- audit assumption violated"
    assert results["val"]["duration_repaired"] == 0 and results["val"]["duration_excluded"] == 0, \
        "unexpected duration repair/exclusion in val.parquet -- audit assumption violated"

    out_dir = ROOT / "final_test"
    (out_dir / "test_quality_transform_manifest.json").write_text(json.dumps({
        "rule_1_temporal_boundary_hygiene": {
            "definition": "exclude test.parquet rows whose pickup_ts epoch second equals val.parquet's max pickup_ts epoch second",
            "boundary_epoch_second": val_max_epoch,
        },
        "rule_2_duration_quality_repair": {
            "definition": "if 0 < duration_seconds <= 24h keep as-is; elif 0 < (dropoff_ts-pickup_ts) <= 24h repair "
                           "duration_seconds_eval from timestamps (quality_action=REPAIRED_FROM_TIMESTAMPS); "
                           "else exclude (quality_action=EXCLUDED_INVALID_DURATION)",
            "max_duration_seconds": MAX_DURATION_SECONDS,
        },
        "per_split": results,
        "final_evaluated_rows": {k: v["final_evaluated_rows"] for k, v in results.items()},
        "raw_test_parquet_immutable": True,
        "applied_at": __import__("datetime").datetime.now().isoformat(),
    }, indent=2), encoding="utf-8")
    print(f"[done] wrote {out_dir / 'test_quality_transform_manifest.json'}", flush=True)
