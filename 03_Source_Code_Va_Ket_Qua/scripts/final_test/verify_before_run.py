"""Gate 3-equivalent: prints + asserts the frozen quality-transform state
and checksum BEFORE any Final Test policy is run. Exits non-zero (blocking
the runner scripts) if any assertion fails."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_transform import load_requests_with_quality_transform, MAX_DURATION_SECONDS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEV_DATA = Path("D:/ProjectVSF/fairdispatch_v3_clean/data")
EXPECTED_TEST_SHA256 = "96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72"
VAL_MAX_EPOCH = 1374412620


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=== Gate 3: verify before Final Test policy run ===", flush=True)

    actual_sha = sha256_file(DEV_DATA / "test.parquet")
    print(f"Original Test checksum : {actual_sha}")
    assert actual_sha == EXPECTED_TEST_SHA256, "test.parquet checksum changed -- raw file must remain immutable"
    print("  [OK] raw test.parquet unchanged")

    results = {}
    for name, path, boundary in (("train", DEV_DATA / "train.parquet", None),
                                  ("val", DEV_DATA / "val.parquet", None),
                                  ("test", DEV_DATA / "test.parquet", VAL_MAX_EPOCH)):
        reqs, stats = load_requests_with_quality_transform(path, boundary_exclude_epoch_second=boundary)
        results[name] = stats
        durs = [r["duration_seconds"] for r in reqs]
        assert all(d > 0 for d in durs), f"{name}: found duration_seconds_eval <= 0"
        assert all(d <= MAX_DURATION_SECONDS for d in durs), f"{name}: found duration_seconds_eval > 24h"
        print(f"{name.capitalize()} repair/exclusion counts: boundary_excluded={stats['temporal_boundary_excluded']} "
              f"repaired={stats['duration_repaired']} duration_excluded={stats['duration_excluded']} "
              f"final={stats['final_evaluated_rows']}")

    boundary_ids = set(results["test"]["excluded_row_ids"]["temporal_boundary"])
    dur_invalid_ids = set(results["test"]["excluded_row_ids"]["duration_invalid"])
    overlap = boundary_ids & dur_invalid_ids
    assert not overlap, f"boundary and duration exclusions overlap: {overlap}"
    print(f"  [OK] {len(boundary_ids)} boundary exclusions and {len(dur_invalid_ids)} duration exclusions do not overlap")

    print(f"\nOriginal rows              : {results['test']['original_rows']}")
    print(f"Temporal-boundary exclusions: {results['test']['temporal_boundary_excluded']}")
    print(f"Duration repairs            : {results['test']['duration_repaired']}")
    print(f"Duration exclusions         : {results['test']['duration_excluded']}")
    print(f"Final evaluated rows        : {results['test']['final_evaluated_rows']}")

    assert results["train"]["duration_repaired"] == 0 and results["train"]["duration_excluded"] == 0
    assert results["val"]["duration_repaired"] == 0 and results["val"]["duration_excluded"] == 0
    print("  [OK] train/val have zero duration repairs/exclusions (matches audit)")

    # strict temporal separation check (post-transform)
    train_reqs, _ = load_requests_with_quality_transform(DEV_DATA / "train.parquet", None)
    val_reqs, _ = load_requests_with_quality_transform(DEV_DATA / "val.parquet", None)
    test_reqs, _ = load_requests_with_quality_transform(DEV_DATA / "test.parquet", VAL_MAX_EPOCH)
    train_t0 = results["train"]["t0_epoch_seconds"]
    val_t0 = results["val"]["t0_epoch_seconds"]
    test_t0 = results["test"]["t0_epoch_seconds"]
    train_max = train_t0 + max(r["pickup_ts"] for r in train_reqs)
    val_max = val_t0 + max(r["pickup_ts"] for r in val_reqs)
    val_min = val_t0 + min(r["pickup_ts"] for r in val_reqs)
    test_min = test_t0 + min(r["pickup_ts"] for r in test_reqs)
    assert train_max < val_min, "train/val temporal overlap after transform"
    assert val_max < test_min, "val/test temporal overlap after transform"
    print(f"  [OK] strict temporal separation holds: train_max={train_max} < val_min={val_min}, "
          f"val_max={val_max} < test_min={test_min}")

    print("\nFinal config: MOMAQL lam=0.5 gamma=0.9 alpha=0.1, 200 drivers, Hungarian joint assignment")
    print("Seeds: [20260721, 20260722, 20260723, 20260724, 20260725]")
    print("\n=== Gate 3 PASSED -- safe to run Final Test policies ===")


if __name__ == "__main__":
    main()
