"""Shared filesystem paths. Two real data sources, kept separate on purpose:

- algorithm code (src/, small) + Q-table + reports CSVs: read from THIS
  submission bundle's own 03_Source_Code_Va_Ket_Qua/ copy (self-contained,
  same SHA-256 as the dev repo -- verified when the bundle was assembled).
- request parquet files: too large to ship in the bundle (hundreds of MB),
  so live simulation reads them straight from the sibling dev repo
  (fairdispatch_v3_clean/data/). Override with FAIRDISPATCH_DEV_REPO if
  that repo lives somewhere else.
"""
import os
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = BUNDLE_ROOT / "03_Source_Code_Va_Ket_Qua" / "src"
BUNDLE_DATA_DIR = BUNDLE_ROOT / "03_Source_Code_Va_Ket_Qua" / "data"
REPORTS_DIR = BUNDLE_ROOT / "03_Source_Code_Va_Ket_Qua" / "reports"

DEV_REPO = Path(os.environ.get("FAIRDISPATCH_DEV_REPO", str(BUNDLE_ROOT.parent / "fairdispatch_v3_clean")))
PARQUET_DATA_DIR = DEV_REPO / "data"
