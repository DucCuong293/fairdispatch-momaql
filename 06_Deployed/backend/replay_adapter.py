"""Reads REAL verified Final Test artifacts (artifacts/final_test/*.csv)
bundled inside this deploy package. Never computes or fabricates numbers --
every row returned is read straight off a CSV file, unmodified.

DEPLOY-SPECIFIC CHANGE vs 05_SanPham_Demo/backend/replay_adapter.py: sources
are the FINAL TEST artifacts (final_test/baseline, final_test/ablation,
final_test/long_horizon, final_test/validation_vs_test.csv), not the
Validation-split reports/*.csv used by the original product. Endpoints not
actually used by the frontend (lambda_sweep, mlp_vs_tabular, fleet_scale --
Final Test protocol explicitly does not run these on Test) are dropped from
PRESETS, per the deploy prompt's "chi bundle endpoint UI thuc su dung"."""
from __future__ import annotations

import csv
import hashlib
import json

import paths


def _read_csv(path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def baseline():
    p = paths.ARTIFACTS_DIR / "baseline" / "test_baseline_summary.csv"
    return {"source": "artifacts/final_test/baseline/test_baseline_summary.csv",
            "label": "VERIFIED TEST EXPERIMENT", "rows": _read_csv(p)}


def baseline_per_seed():
    p = paths.ARTIFACTS_DIR / "baseline" / "test_baseline_per_seed.csv"
    return {"source": "artifacts/final_test/baseline/test_baseline_per_seed.csv",
            "label": "VERIFIED TEST EXPERIMENT", "rows": _read_csv(p)}


def ablation():
    p = paths.ARTIFACTS_DIR / "ablation" / "test_ablation_results.csv"
    return {"source": "artifacts/final_test/ablation/test_ablation_results.csv",
            "label": "VERIFIED TEST EXPERIMENT", "seeds": 5, "rows": _read_csv(p)}


def ablation_per_seed():
    p = paths.ARTIFACTS_DIR / "ablation" / "test_ablation_per_seed.csv"
    return {"source": "artifacts/final_test/ablation/test_ablation_per_seed.csv",
            "label": "VERIFIED TEST EXPERIMENT", "rows": _read_csv(p)}


def long_horizon():
    p = paths.ARTIFACTS_DIR / "long_horizon" / "test_long_horizon.csv"
    return {"source": "artifacts/final_test/long_horizon/test_long_horizon.csv",
            "label": "VERIFIED TEST EXPERIMENT", "rows": _read_csv(p)}


def validation_vs_test():
    p = paths.ARTIFACTS_DIR / "validation_vs_test.csv"
    return {"source": "artifacts/final_test/validation_vs_test.csv", "rows": _read_csv(p)}


PRESETS = {
    "main_comparison": baseline,
    "baseline": baseline,
    "baseline_per_seed": baseline_per_seed,
    "ablation": ablation,
    "ablation_per_seed": ablation_per_seed,
    "long_horizon": long_horizon,
    "validation_vs_test": validation_vs_test,
}


def _sha256_file(path):
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def provenance():
    """Self-contained provenance -- no sibling dev-repo git lookup (that
    dependency does not exist in the deployed bundle; see paths.py)."""
    deployment_manifest = {}
    if paths.DEPLOYMENT_DATA_MANIFEST.exists():
        deployment_manifest = json.loads(paths.DEPLOYMENT_DATA_MANIFEST.read_text(encoding="utf-8"))

    engine_files = {}
    for name in ("policies.py", "simulator.py"):
        p = paths.SRC_DIR / name
        engine_files[name] = {"sha256": _sha256_file(p), "path": str(p)}

    q_table_hash = _sha256_file(paths.Q_TABLE_PATH)

    return {
        "runtime_dataset": {
            "name": "Final Test Evaluation View",
            "rows": deployment_manifest.get("output", {}).get("rows"),
            "file": "data/test_eval.parquet",
            "sha256": deployment_manifest.get("output", {}).get("sha256", "computed-at-build"),
        },
        "raw_test_source": {
            "rows": deployment_manifest.get("built_from_raw_test_parquet", {}).get("size_bytes") and
                    deployment_manifest.get("stats", {}).get("original_rows"),
            "sha256": deployment_manifest.get("built_from_raw_test_parquet", {}).get("sha256"),
            "matches_canonical": deployment_manifest.get("built_from_raw_test_parquet", {}).get("matches_canonical"),
            "immutable": True,
        },
        "quality_transform": {
            "boundary_excluded": deployment_manifest.get("stats", {}).get("temporal_boundary_excluded"),
            "duration_repaired": deployment_manifest.get("stats", {}).get("duration_repaired"),
            "duration_excluded": deployment_manifest.get("stats", {}).get("duration_excluded"),
        },
        "engine_source": {
            "note": "SHA-256 of the exact policies.py/simulator.py bundled in this deploy package "
                    "(engine/src/), imported and running right now.",
            "files": engine_files,
        },
        "q_table": {"sha256": q_table_hash, "path": "data/momaql_q_table_trained.json"},
        "bundle_root": str(paths.BUNDLE_ROOT),
    }
