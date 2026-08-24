"""Shared filesystem paths for the DEPLOYED bundle. Fully self-contained --
no path here ever points outside 06_Deployed/ (no sibling dev repo, no
D:\\... dependency at runtime). Engine code, Q-table, Final Test evaluation
parquet, and Final Test artifacts are all bundled inside this folder.
"""
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[1]  # .../06_Deployed
SRC_DIR = BUNDLE_ROOT / "engine" / "src"
ENGINE_DIR = BUNDLE_ROOT / "engine"
BUNDLE_DATA_DIR = BUNDLE_ROOT / "data"
ARTIFACTS_DIR = BUNDLE_ROOT / "artifacts" / "final_test"

TEST_EVAL_PARQUET = BUNDLE_DATA_DIR / "test_eval.parquet"
Q_TABLE_PATH = BUNDLE_DATA_DIR / "momaql_q_table_trained.json"
DEPLOYMENT_DATA_MANIFEST = BUNDLE_DATA_DIR / "deployment_data_manifest.json"
