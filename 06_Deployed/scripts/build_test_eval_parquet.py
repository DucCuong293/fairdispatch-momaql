"""Builds 06_Deployed/data/test_eval.parquet -- the Final Test Evaluation
View -- from the real, immutable raw test.parquet, applying EXACTLY the
frozen quality transform already used by every Final Test script
(03_Source_Code_Va_Ket_Qua/scripts/final_test/quality_transform.py). This
script only READS the raw parquet and the frozen transform module; it never
writes to raw test.parquet, never reruns any policy/experiment, and never
retrains anything.

Run once, locally, before deploy:
    python scripts/build_test_eval_parquet.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication
DEPLOY_ROOT = Path(__file__).resolve().parents[1]  # .../06_Deployed
SOURCE_ROOT = REPO_ROOT / "03_Source_Code_Va_Ket_Qua"

sys.path.insert(0, str(SOURCE_ROOT))
sys.path.insert(0, str(SOURCE_ROOT / "scripts" / "final_test"))
from quality_transform import load_requests_with_quality_transform  # noqa: E402

EXPECTED_TEST_SHA256 = "96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72"
EXPECTED_TEST_SIZE = 48_188_109


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def find_raw_test_parquet() -> Path:
    """Search order per deploy prompt -- never hard-code before checking."""
    candidates = [
        SOURCE_ROOT / "data" / "test.parquet",
        Path("D:/ProjectVSF/fairdispatch_v3_clean/data/test.parquet"),
    ]
    for c in candidates:
        if c.exists():
            return c
    print("[search] not found at either canonical candidate, scanning D:/ProjectVSF ...", flush=True)
    for p in Path("D:/ProjectVSF").rglob("test.parquet"):
        return p
    raise FileNotFoundError(
        "test.parquet not found at any searched location: "
        + ", ".join(str(c) for c in candidates)
        + ", nor anywhere under D:/ProjectVSF. Deployment data build BLOCKED -- "
          "refusing to fabricate data."
    )


def main():
    raw_path = find_raw_test_parquet()
    print(f"[found] raw test.parquet: {raw_path}", flush=True)

    actual_sha = sha256_file(raw_path)
    actual_size = raw_path.stat().st_size
    hash_ok = actual_sha == EXPECTED_TEST_SHA256 and actual_size == EXPECTED_TEST_SIZE
    print(f"[hash] sha256={actual_sha} size={actual_size} expected_ok={hash_ok}", flush=True)
    if not hash_ok:
        print("[WARNING] raw test.parquet hash/size does NOT match canonical expected value. "
              "Continuing per instructions (not silently masking), but this MUST be reported.", flush=True)

    manifest_path = SOURCE_ROOT / "final_test" / "test_quality_transform_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    boundary_epoch = manifest["rule_1_temporal_boundary_hygiene"]["boundary_epoch_second"]
    print(f"[rule] boundary_epoch_second (from frozen manifest) = {boundary_epoch}", flush=True)

    requests, stats = load_requests_with_quality_transform(raw_path, boundary_exclude_epoch_second=boundary_epoch)
    print(f"[transform] original={stats['original_rows']} boundary_excluded={stats['temporal_boundary_excluded']} "
          f"duration_repaired={stats['duration_repaired']} duration_excluded={stats['duration_excluded']} "
          f"final={stats['final_evaluated_rows']}", flush=True)

    assert stats["final_evaluated_rows"] == 195506, stats["final_evaluated_rows"]
    assert stats["temporal_boundary_excluded"] == 3, stats["temporal_boundary_excluded"]
    assert stats["duration_repaired"] == 32, stats["duration_repaired"]
    assert stats["duration_excluded"] == 1, stats["duration_excluded"]

    # requests[j]["_idx"] is the ORIGINAL row index in raw test.parquet, in
    # the same kept order as `requests` -- use it to pull absolute
    # pickup_ts/dropoff_ts (quality_transform's own dict uses ts RELATIVE to
    # this view's t0, but the deploy parquet must keep absolute real
    # timestamps so the UI shows the real NYC date/time).
    kept_idx = [r["_idx"] for r in requests]
    raw_table = pq.read_table(raw_path, columns=["pickup_ts", "dropoff_ts"])
    abs_pickup = raw_table["pickup_ts"].to_numpy(zero_copy_only=False).astype("datetime64[us]")
    abs_dropoff = raw_table["dropoff_ts"].to_numpy(zero_copy_only=False).astype("datetime64[us]")
    pickup_ts_kept = abs_pickup[kept_idx]
    dropoff_ts_kept = abs_dropoff[kept_idx]
    pickup_epoch_kept = pickup_ts_kept.astype("datetime64[s]").astype("int64")
    # 1970-01-01 (epoch day 0) was a Thursday -> weekday index 3 in a
    # Monday=0..Sunday=6 convention -- same formula as engine_adapter.py's
    # live loader, so Live and Replay agree on what "weekday" means.
    pickup_weekday = ((pickup_epoch_kept // 86400 + 3) % 7).astype(np.int32)

    out_table = pa.table({
        "source_row_index": pa.array(kept_idx, type=pa.int64()),
        "pickup_ts": pa.array(pickup_ts_kept),
        "dropoff_ts": pa.array(dropoff_ts_kept),
        "pickup_latitude": pa.array([r["pickup_latitude"] for r in requests], type=pa.float64()),
        "pickup_longitude": pa.array([r["pickup_longitude"] for r in requests], type=pa.float64()),
        "dropoff_latitude": pa.array([r["dropoff_latitude"] for r in requests], type=pa.float64()),
        "dropoff_longitude": pa.array([r["dropoff_longitude"] for r in requests], type=pa.float64()),
        "fare_amount": pa.array([r["fare_amount"] for r in requests], type=pa.float64()),
        "duration_seconds": pa.array([r["duration_seconds"] for r in requests], type=pa.float64()),
        "duration_seconds_raw": pa.array([r["duration_seconds_raw"] for r in requests], type=pa.float64()),
        "quality_action": pa.array([r["quality_action"] for r in requests], type=pa.string()),
        "pickup_zone_id": pa.array([r["pickup_zone_id"] for r in requests], type=pa.int32()),
        "dropoff_zone_id": pa.array([r["dropoff_zone_id"] for r in requests], type=pa.int32()),
        "pickup_hour": pa.array([r["pickup_hour"] for r in requests], type=pa.int32()),
        "dropoff_hour": pa.array([r["dropoff_hour"] for r in requests], type=pa.int32()),
        "pickup_weekday": pa.array(pickup_weekday, type=pa.int32()),
    })

    durs = np.array(out_table["duration_seconds"].to_pylist())
    assert len(out_table) == 195506, len(out_table)
    assert (durs > 0).all()
    assert (durs <= 86400).all()

    out_path = DEPLOY_ROOT / "data" / "test_eval.parquet"
    pq.write_table(out_table, out_path)
    new_sha = sha256_file(out_path)
    new_size = out_path.stat().st_size
    print(f"[written] {out_path} rows={len(out_table)} sha256={new_sha} size={new_size}", flush=True)

    manifest_out = {
        "built_from_raw_test_parquet": {
            "path": str(raw_path), "sha256": actual_sha, "size_bytes": actual_size,
            "expected_sha256": EXPECTED_TEST_SHA256, "expected_size_bytes": EXPECTED_TEST_SIZE,
            "matches_canonical": hash_ok,
        },
        "quality_transform_manifest_used": str(manifest_path),
        "boundary_epoch_second": boundary_epoch,
        "stats": stats,
        "output": {
            "path": "data/test_eval.parquet", "rows": len(out_table),
            "sha256": new_sha, "size_bytes": new_size,
            "columns": out_table.column_names,
        },
    }
    (DEPLOY_ROOT / "data" / "deployment_data_manifest.json").write_text(
        json.dumps(manifest_out, indent=2), encoding="utf-8",
    )
    print("[done] wrote data/deployment_data_manifest.json", flush=True)


if __name__ == "__main__":
    main()
