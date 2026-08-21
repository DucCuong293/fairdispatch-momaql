"""Reads REAL verified experiment artifacts (reports/*.csv) that already
back the Research Report and the presentation slides. Never computes or
fabricates numbers here -- every row returned is read straight off a CSV
file, unmodified."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import defaultdict

import paths


def _read_csv(name: str) -> list[dict]:
    path = paths.REPORTS_DIR / name
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main_comparison():
    rows = _read_csv("r1_validation_results.csv")
    agg = defaultdict(lambda: {"utility": [], "gini": []})
    for r in rows:
        agg[r["policy"]]["utility"].append(float(r["utility"]))
        agg[r["policy"]]["gini"].append(float(r["gini"]))
    summary = [
        {"policy": pol, "utility_mean": sum(v["utility"]) / len(v["utility"]),
         "gini_mean": sum(v["gini"]) / len(v["gini"]), "n_seeds": len(v["utility"])}
        for pol, v in agg.items()
    ]
    return {"source": "reports/r1_validation_results.csv", "summary": summary, "raw_rows": rows}


def ablation():
    return {"source": "reports/r2_ablation_results.csv", "rows": _read_csv("r2_ablation_results.csv")}


def ablation_raw():
    return {"source": "reports/r2_ablation_raw.csv", "rows": _read_csv("r2_ablation_raw.csv")}


def long_horizon():
    return {"source": "reports/multi_horizon_results.csv", "rows": _read_csv("multi_horizon_results.csv")}


def fleet_scale():
    return {"source": "reports/fleet_scale_results.csv", "rows": _read_csv("fleet_scale_results.csv")}


def lambda_sweep():
    return {"source": "reports/pareto_frontier_summary.csv", "rows": _read_csv("pareto_frontier_summary.csv")}


def mlp_vs_tabular():
    return {"source": "reports/mlp_vs_tabular_summary.csv", "rows": _read_csv("mlp_vs_tabular_summary.csv")}


PRESETS = {
    "main_comparison": main_comparison,
    "ablation": ablation,
    "ablation_raw": ablation_raw,
    "long_horizon": long_horizon,
    "fleet_scale": fleet_scale,
    "lambda_sweep": lambda_sweep,
    "mlp_vs_tabular": mlp_vs_tabular,
}


def _sha256_file(path):
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def provenance():
    """Two DISTINCT provenance concepts, kept separate on purpose (P1.7):

    - bundle_engine_source: the actual policies.py/simulator.py this
      backend is running RIGHT NOW (SHA-256 of the exact bytes imported,
      not a commit hash of some other repo -- this IS the engine).
    - dev_repo: the sibling dev repo used ONLY as a source of the large
      parquet request files, unrelated to which engine code is executing.
    Showing dev repo git HEAD as if it were "the engine's commit" would be
    misleading if the two ever diverge (e.g. bundle copied at an earlier
    commit than the dev repo's current HEAD)."""
    checksums_path = paths.REPORTS_DIR / "dataset_checksums.json"
    checksums = json.loads(checksums_path.read_text(encoding="utf-8")) if checksums_path.exists() else {}

    dev_head = None
    dev_dirty = None
    try:
        dev_head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(paths.DEV_REPO), text=True, timeout=5,
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=str(paths.DEV_REPO), text=True, timeout=5,
        )
        dev_dirty = bool(status.strip())
    except Exception:
        pass

    engine_files = {}
    for name in ("policies.py", "simulator.py"):
        p = paths.SRC_DIR / name
        engine_files[name] = {"sha256": _sha256_file(p), "path": str(p)}

    return {
        "dataset_checksums": checksums,
        "bundle_engine_source": {
            "note": "SHA-256 cua chinh policies.py/simulator.py dang duoc import va chay ngay luc nay "
                    "(khong phai commit hash cua repo khac).",
            "files": engine_files,
        },
        "dev_repo": {
            "note": "Repo dev CHI dung de doc file parquet (request data that qua lon de copy vao bundle). "
                    "Khong phai commit dang chay engine.",
            "path": str(paths.DEV_REPO),
            "git_head": dev_head,
            "working_tree_dirty": dev_dirty,
        },
        "bundle_root": str(paths.BUNDLE_ROOT),
    }
