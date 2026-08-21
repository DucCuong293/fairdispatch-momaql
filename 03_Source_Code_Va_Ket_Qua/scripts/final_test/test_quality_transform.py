"""Self-check for the Final Test quality transform logic (metric calc, the
repair/exclude decision, and failure handling) using tiny synthetic parquet
files -- no dependency on the real 195k-row dataset. Run: `python
scripts/final_test/test_quality_transform.py`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pyarrow as pa
import pyarrow.parquet as pq

from quality_transform import load_requests_with_quality_transform, MAX_DURATION_SECONDS
from common_loader import gini, variance, std, coefficient_of_variation


def _make_parquet(tmp_path, rows):
    import pandas as pd
    table = pa.table({
        "pickup_ts": pa.array(pd.to_datetime([r["pickup_ts"] for r in rows]), type=pa.timestamp("s")),
        "dropoff_ts": pa.array(pd.to_datetime([r["dropoff_ts"] for r in rows]), type=pa.timestamp("s")),
        "pickup_latitude": [40.75] * len(rows), "pickup_longitude": [-73.98] * len(rows),
        "dropoff_latitude": [40.76] * len(rows), "dropoff_longitude": [-73.97] * len(rows),
        "fare_amount": [8.5] * len(rows),
        "duration_seconds": [float(r["duration_seconds"]) for r in rows],
        "pickup_zone_id": [1] * len(rows), "dropoff_zone_id": [2] * len(rows),
    })
    pq.write_table(table, tmp_path)


def test_kept_raw_valid_duration():
    p = Path("_test_kept.parquet")
    _make_parquet(p, [{"pickup_ts": "2013-08-01 10:00:00", "dropoff_ts": "2013-08-01 10:20:00", "duration_seconds": 1200}])
    reqs, stats = load_requests_with_quality_transform(p)
    assert stats["duration_repaired"] == 0 and stats["duration_excluded"] == 0
    assert reqs[0]["duration_seconds"] == 1200
    assert reqs[0]["quality_action"] == "KEPT_RAW"
    p.unlink()
    print("[PASS] kept_raw_valid_duration")


def test_repaired_from_timestamps():
    p = Path("_test_repair.parquet")
    # duration_seconds corrupted (huge), but dropoff-pickup is a valid 15min trip
    _make_parquet(p, [{"pickup_ts": "2013-08-01 10:00:00", "dropoff_ts": "2013-08-01 10:15:00", "duration_seconds": 4294815}])
    reqs, stats = load_requests_with_quality_transform(p)
    assert stats["duration_repaired"] == 1 and stats["duration_excluded"] == 0
    assert reqs[0]["duration_seconds"] == 900  # 15 min, repaired
    assert reqs[0]["duration_seconds_raw"] == 4294815
    assert reqs[0]["quality_action"] == "REPAIRED_FROM_TIMESTAMPS"
    p.unlink()
    print("[PASS] repaired_from_timestamps")


def test_excluded_irrecoverable():
    p = Path("_test_exclude.parquet")
    # both raw and computed duration invalid (pickup==dropoff -> computed=0)
    _make_parquet(p, [
        {"pickup_ts": "2013-08-01 10:00:00", "dropoff_ts": "2013-08-01 10:00:00", "duration_seconds": 4294815},
        {"pickup_ts": "2013-08-01 11:00:00", "dropoff_ts": "2013-08-01 11:10:00", "duration_seconds": 600},  # normal, kept
    ])
    reqs, stats = load_requests_with_quality_transform(p)
    assert stats["duration_excluded"] == 1 and stats["final_evaluated_rows"] == 1
    assert reqs[0]["duration_seconds"] == 600
    p.unlink()
    print("[PASS] excluded_irrecoverable")


def test_temporal_boundary_exclusion():
    p = Path("_test_boundary.parquet")
    _make_parquet(p, [
        {"pickup_ts": "2013-08-01 10:00:00", "dropoff_ts": "2013-08-01 10:10:00", "duration_seconds": 600},
        {"pickup_ts": "2013-08-01 11:00:00", "dropoff_ts": "2013-08-01 11:10:00", "duration_seconds": 600},
    ])
    import numpy as np
    boundary_epoch = int(np.datetime64("2013-08-01T10:00:00").astype("datetime64[s]").astype("int64"))
    reqs, stats = load_requests_with_quality_transform(p, boundary_exclude_epoch_second=boundary_epoch)
    assert stats["temporal_boundary_excluded"] == 1 and stats["final_evaluated_rows"] == 1
    p.unlink()
    print("[PASS] temporal_boundary_exclusion")


def test_metric_calculations():
    assert gini([10.0, 10.0, 10.0]) == 0.0  # perfectly equal
    assert gini([0.0, 0.0, 100.0]) > 0.5  # highly unequal
    assert variance([1.0, 1.0, 1.0]) == 0.0
    assert std([2.0, 4.0]) == variance([2.0, 4.0]) ** 0.5
    import math
    assert math.isnan(coefficient_of_variation([0.0, 0.0]))  # undefined at zero mean
    print("[PASS] metric_calculations")


def test_all_rows_excluded_raises():
    p = Path("_test_allbad.parquet")
    _make_parquet(p, [{"pickup_ts": "2013-08-01 10:00:00", "dropoff_ts": "2013-08-01 10:00:00", "duration_seconds": 4294815}])
    try:
        load_requests_with_quality_transform(p)
        raised = False
    except ValueError:
        raised = True
    assert raised, "expected ValueError when transform would exclude every row"
    p.unlink()
    print("[PASS] all_rows_excluded_raises")


if __name__ == "__main__":
    test_kept_raw_valid_duration()
    test_repaired_from_timestamps()
    test_excluded_irrecoverable()
    test_temporal_boundary_exclusion()
    test_metric_calculations()
    test_all_rows_excluded_raises()
    print("\nALL SELF-CHECKS PASSED")
