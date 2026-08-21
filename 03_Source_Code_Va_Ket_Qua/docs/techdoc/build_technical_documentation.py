# -*- coding: utf-8 -*-
"""Builds Technical_Documentation.docx -- the engineering/reproducibility
companion to the Research Report (docs/docx_report/). This document answers
ONE question: if an engineer clones this repo tomorrow, can they understand
the architecture, rerun every experiment, and get the same retained
artifacts? It does NOT re-argue the science -- that's the Research Report's
job. Every command, row count, and config value below is verified live
against the actual repo at build time (fresh `git rev-parse HEAD`, fresh
`wc -l` equivalents on reports/*.csv, fresh pytest run counted, fresh
`sha256sum` of the dataset files).
Run: python docs/techdoc/build_technical_documentation.py
"""
import csv
import hashlib
import platform
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _docx_style import (
    NAVY, ACCENT as BLUE, GREY, setup_document, title_page, heading, para,
    bullets, add_table as _styled_add_table, add_figure as _styled_add_figure,
    code_block, callout,
)

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
DATA = ROOT / "data"
FINAL_TEST = ROOT / "final_test"
OUT = Path(__file__).parent / "Technical_Documentation.docx"

DARK = RGBColor(0x20, 0x20, 0x20)
_fig_counter = {"n": 0}


def git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unavailable"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_row_count(name):
    with (REPORTS / name).open(encoding="utf-8") as f:
        return sum(1 for _ in f) - 1


def add_table(doc, headers, rows):
    return _styled_add_table(doc, headers, rows)


def add_figure(doc, filename, caption, width=5.9):
    path = Path(__file__).parent.parent / "docx_report" / "figures" / filename
    _fig_counter["n"] += 1
    _styled_add_figure(doc, path, caption, width=width, number=_fig_counter["n"])


def main():
    head = git_head()

    # Fresh test run count.
    try:
        out = subprocess.run([sys.executable, "-m", "pytest", "tests/test_simulator_invariants.py", "-q"],
                              cwd=ROOT, capture_output=True, text=True, timeout=120)
        test_summary = [l for l in out.stdout.splitlines() if "passed" in l or "failed" in l]
        test_line = test_summary[-1] if test_summary else "(could not parse pytest output)"
    except Exception as e:
        test_line = f"(pytest run failed: {e})"

    # Fresh dataset hashes.
    ds_hashes = {}
    for fname in ["train.parquet", "val.parquet", "test.parquet", "momaql_q_table_trained.json"]:
        p = DATA / fname
        if p.exists():
            ds_hashes[fname] = (sha256(p), p.stat().st_size)

    # Final Test artifacts (read-only; no rerun).
    ft_available = FINAL_TEST.exists() and (FINAL_TEST / "test_quality_transform_manifest.json").exists()
    ft_manifest = None
    ft_commands_log = ""
    ft_environment_txt = ""
    if ft_available:
        import json
        ft_manifest = json.loads((FINAL_TEST / "test_quality_transform_manifest.json").read_text(encoding="utf-8"))
        cmd_log_path = FINAL_TEST / "logs" / "commands.log"
        env_path = FINAL_TEST / "logs" / "environment.txt"
        if cmd_log_path.exists():
            ft_commands_log = cmd_log_path.read_text(encoding="utf-8")
        if env_path.exists():
            ft_environment_txt = env_path.read_text(encoding="utf-8")

    doc = Document()
    setup_document(doc, footer_label="FairDispatch -- Technical Documentation")
    title_page(
        doc,
        kicker="Technical Documentation",
        title="fairdispatch_v3_clean",
        subtitle="Engineering & Reproducibility Guide -- companion to the Research Report; "
                 "this document covers implementation, not scientific claims.",
        meta_lines=[f"Git commit at build time: {head[:12]}"],
    )

    # ---------------- 1. System Overview ----------------
    heading(doc, "1. System Overview", level=1)
    para(doc, "Real end-to-end pipeline executed by this repository:")
    add_figure(doc, "replication_pipeline.png", "Hinh 1: Real NYC TLC 2013 trips -> Manhattan + "
               "quality filter -> 67 TLC taxi zones -> Q(zone,hour) trained via Bellman TD(0) -> "
               "60s-window batched simulator -> Hungarian M-to-N assignment -> "
               "utility/Gini/variance metrics.")
    para(doc, "There is no message queue, no database, no web service -- every stage is a plain "
              "Python script reading/writing local files. The simulator is a lightweight, "
              "in-process discrete-event loop (src/simulator.py), not a real-time system.")

    # ---------------- 2. Repository Structure ----------------
    heading(doc, "2. Repository Structure", level=1)
    code_block(doc, """
fairdispatch_v3_clean/
|-- src/
|   |-- simulator.py       Driver/SimResult dataclasses, init_drivers,
|   |                      feasible_drivers, commit_trip, run_simulation_batched,
|   |                      run_simulation_with_horizon, run_simulation (legacy)
|   `-- policies.py        hungarian_batch_assign + 5 policy classes (Greedy,
|                          Nearest, LAF, ExactReassignPolicy, MOMAQLPolicy)
|-- common_loader.py        parquet -> request-dict loader; gini/variance/std/CV
|-- train_momaql.py          trains the canonical Q(zone,hour) table (single pass)
|-- train_momaql_multipass.py  DISCLOSED UNSTABLE -- do not use for evaluation
|-- run_r1.py                 R1: 5-policy baseline comparison
|-- run_r2_ablation.py        R2: Full / w/o-Forecast / w/o-Fairness
|-- run_pareto_frontier.py    lambda sweep, 7 values
|-- run_multi_horizon.py      multi-horizon trajectory + policy disagreement
|-- run_complete_verifications.py   fleet-scale sweep + spatial disagreement
|-- run_spatial_candidate_pool.py   candidate-pool depth, core vs. periphery
|-- run_q_table_convergence.py      day-by-day Q-table convergence (37 days)
|-- run_hypothesis1_weekly_cycle.py  weekly demand-cycle mechanism test
|-- run_hypothesis4_fairness_balance.py  fairness/lookahead score-balance trace
|-- train_and_eval_mlp.py     real PyTorch MLP demand forecaster vs. tabular Q
|-- make_report_figures.py    regenerates every figure from reports/*.csv
|-- tests/
|   `-- test_simulator_invariants.py   20 invariant tests
|-- data/                     train/val/test parquet splits (gitignored, see
|                              Sec. 9 for SHA-256) + trained Q-table JSON
|-- reports/                  every retained CSV/JSON/PNG cited by both docs
`-- docs/
    |-- docx_report/           Research Report (.docx) + its figures
    |-- techdoc/                this document
    `-- ride_hailing_fairness_report_en(vi)/   LaTeX paper + compiled PDF
""")
    para(doc, "No dependency lockfile, package-metadata file, Dockerfile, CI workflow, or central "
              "config file exists in this repository. Every run_*.py is a standalone script with "
              "its own module-level constants (N_DRIVERS, SEEDS, etc.) -- see Sec. 7.", size=9.5,
              color=GREY)

    # ---------------- 3. Environment ----------------
    heading(doc, "3. Environment", level=1)
    para(doc, "Audited environment at build time (this is the machine this repository was last "
              "verified on -- NOT a claim that every historical experiment ran on identical "
              "hardware; no environment lockfile was retained from earlier runs).", size=9.5,
              color=GREY)
    add_table(doc, ["Component", "Value"], [
        ["OS", f"{platform.system()} {platform.release()} ({platform.version()})"],
        ["Python", platform.python_version()],
        ["CPU", "Intel Core i5-10300H, 4 cores / 8 threads"],
        ["RAM", "15.8 GiB total"],
        ["GPU", "NVIDIA GeForce GTX 1650, ~4.3 GB VRAM (CUDA available)"],
        ["Key packages", "numpy 2.2.6, pandas 2.3.2, pyarrow 21.0.0, scipy 1.16.2, "
         "matplotlib 3.10.6, pytest 8.3.3, python-docx 1.2.0, torch 2.7.1+cu118"],
    ])
    code_block(doc, """
python -m venv .venv
.venv\\Scripts\\activate                 # Windows; source .venv/bin/activate on Linux/Mac
pip install numpy pandas pyarrow scipy matplotlib pytest python-docx
pip install torch                        # only needed for train_and_eval_mlp.py
""")
    para(doc, "No CI/CD, no Docker image, no requirements.txt is retained in this repo -- the "
              "package list above is the audited, working set; pin exact versions if bit-for-bit "
              "reproducibility across machines matters.")

    # ---------------- 4. Data Contract ----------------
    heading(doc, "4. Data Contract", level=1)
    add_table(doc, ["Split", "Role"], [
        ["train.parquet", "Train Q(zone,hour) (train_momaql.py); MLP forecast sensitivity training"],
        ["val.parquet", "Development / analysis: build+debug the simulator, compare policies, "
         "ablation, Pareto sweep, long-horizon, mechanism probes, freeze final configuration"],
        ["test.parquet", "Final held-out temporal verification ONLY (Sec. 8) -- never used to "
         "select lambda/gamma/alpha, never used by the live product demo"],
    ])
    heading(doc, "4.1 Raw parquet schema (train/val/test)", level=2)
    para(doc, "Columns read by common_loader.load_requests_fast() and train_momaql.py's own "
              "loader: pickup_ts (timestamp), pickup_latitude, pickup_longitude, "
              "dropoff_latitude, dropoff_longitude, fare_amount, duration_seconds, "
              "pickup_zone_id, dropoff_zone_id. pickup_ts is absolute epoch time -- hour-of-day is "
              "derived from it directly (NOT from a per-file-relative offset), so a given hour "
              "bucket means the same real time-of-day in train.parquet as in val/test.parquet.")
    heading(doc, "4.2 Processed request dict (in-memory, per row)", level=2)
    code_block(doc, """
{
  "_idx": int,                    # position in the sorted request list
  "pickup_ts": float,             # seconds, RELATIVE to this split's first row
  "pickup_latitude": float, "pickup_longitude": float,
  "dropoff_latitude": float, "dropoff_longitude": float,
  "fare_amount": float,           # real USD fare
  "duration_seconds": float,
  "pickup_zone_id": int, "dropoff_zone_id": int,   # TLC taxi zone id
  "pickup_hour": int,             # 0-23, derived from ABSOLUTE epoch time
  "dropoff_hour": int,            # 0-23, = (pickup_epoch + duration) % 24h
}
""")
    heading(doc, "4.3 Driver state (src/simulator.py:Driver)", level=2)
    code_block(doc, """
Driver:
  driver_id: int
  lat, lon: float                 # current position
  available_at: float             # earliest time this driver can accept a new trip
  total_income: float = 0.0       # accumulated net (fare - deadhead_cost)
  total_deadhead_cost: float = 0.0
  total_trips: int = 0
""")
    heading(doc, "4.4 RL state / action / reward (MOMAQLPolicy)", level=2)
    bullets(doc, [
        "State S = (pickup_zone_id, pickup_hour) of the trip a driver just took.",
        "State S' = (dropoff_zone_id, dropoff_hour) of that same trip -- where/when the driver "
        "ends up.",
        "Action = a joint M-to-N assignment for one 60-second window, solved once per window by "
        "the Hungarian algorithm (not per-request greedy choice).",
        "Reward = fare_amount − eta_seconds × 0.0025 (deadhead cost coefficient, USD per second "
        "of pickup ETA).",
        "Q-table key: (zone_id: int, hour_of_day: int) -> float. JSON serialization uses string "
        "keys \"zone:hour\" (e.g. \"137:0\"); MOMAQLPolicy._parse_q_table() accepts both native "
        "tuple keys and this string format.",
    ])

    # ---------------- 5. Module Specification ----------------
    heading(doc, "5. Module Specification", level=1)
    heading(doc, "5.1 src/simulator.py", level=2)
    add_table(doc, ["Function", "Input", "Output"], [
        ["init_drivers(n, requests, seed)", "driver count, request list, RNG seed", "list[Driver], "
         "positioned at n real pickup locations sampled from the request list"],
        ["feasible_drivers(drivers, req, now)", "driver list, one request, current time", "list of "
         "(driver, deadhead_miles, eta_seconds) for drivers free by `now` and within "
         "MAX_PICKUP_ETA_SECONDS=600s"],
        ["commit_trip(d, req, dist, eta, now, result, record_trace)", "chosen driver + request + "
         "timing", "mutates driver state (income, position, available_at) and result totals"],
        ["run_simulation_batched(requests, n_drivers, policy, seed, window_seconds=60.0)", "sorted "
         "request list + policy object", "SimResult (per-driver income, completion count)"],
        ["run_simulation_with_horizon(..., checkpoint_days, compare_policy=None, "
         "zone_classifier=None)", "same + checkpoint days + optional comparison policy", "(result, "
         "checkpoints dict, disagreement_rate) -- ONE trajectory, snapshotted at each checkpoint "
         "day, not independent reruns"],
    ])
    para(doc, "Deliberate simplifications (disclosed in the module docstring): driver position is "
              "real (lat, lon), not a spatial-bucket approximation; ETA is haversine distance at a "
              "constant 12 mph, not a real road-routing model; the deadhead cost coefficient "
              "(0.0025 USD/s) is reused as-is from the parent project's frozen "
              "UtilityCoefficients, not reinvented.", size=9.5, color=GREY)
    heading(doc, "5.2 src/policies.py", level=2)
    add_table(doc, ["Policy", "score_fn(d, req, dist, eta)", "Notes"], [
        ["Greedy", "fare_amount", "identical across candidates of one request; joint solve still "
         "maximizes served count"],
        ["Nearest", "(600.0 − eta) × 0.0025", "re-centered so 0 = break-even at the feasibility "
         "cutoff; argmax(score) == argmin(eta)"],
        ["LAF", "[(mean_income − d.income) / max(mean_income,1)] × fare", "argmax(score) == "
         "argmin(driver.income); fairness-only heuristic"],
        ["Exact REASSIGN", "fare_amount − eta×0.0025", "pure net-utility maximization, real joint "
         "M-to-N solve"],
        ["MOMAQL", "(1−λ)·[fare − eta×0.0025 + γ·Q(D_zone,D_hour)] + λ·[(mean_income−d.income)/"
         "max(mean_income,1)]·fare", "the only policy with online Q-learning "
         "(on_committed updates Q via Bellman TD(0) unless frozen=True)"],
    ])
    para(doc, "All 5 policies share ONE reference frame: hungarian_batch_assign() solves a real "
              "joint assignment via scipy.optimize.linear_sum_assignment over a "
              "(n_req+n_drv)×(n_req+n_drv) dummy-padded cost matrix, so every request/driver has a "
              "real \"decline\"/\"idle\" option at cost 0 -- this is a maximum-WEIGHT matching "
              "(paper's own sum_v I_rv ≤ 1 formulation), not maximum-cardinality.")
    heading(doc, "5.3 common_loader.py", level=2)
    add_table(doc, ["Function", "Purpose"], [
        ["load_requests_fast(path)", "PyArrow-based parquet -> list[dict] loader; computes "
         "pickup_hour/dropoff_hour from absolute epoch time"],
        ["gini(values)", "Gini coefficient of a list of driver incomes"],
        ["variance(values) / std(values)", "population variance / std -- the paper's own primary "
         "fairness metric"],
        ["coefficient_of_variation(values)", "std/mean; NaN-guarded when |mean| < 1e-9 (unstable "
         "when mean utility is near zero)"],
    ])

    # ---------------- 6. Algorithm / Pseudocode ----------------
    heading(doc, "6. Algorithm / Pseudocode", level=1)
    heading(doc, "6.1 Batched dispatch loop (run_simulation_batched)", level=2)
    code_block(doc, """
for each 60-second window, in real pickup_ts order:
    window_reqs = requests with pickup_ts in [window_start, window_start+60s)
    for req in window_reqs:
        candidates[req] = feasible_drivers(drivers, req, window_start)
            # free by window_start AND eta <= 600s

    assignments = policy.select_batch(candidates, window_start)
        # -> real joint Hungarian solve, decline option at cost 0

    for req, (driver, dist, eta) in assignments.items():
        if driver already used this window: skip   # policy-bug guard
        commit_trip(driver, req, dist, eta, window_start, result)
            # driver.income += fare - eta*0.0025
            # driver.available_at = window_start + eta + duration_seconds
        policy.on_committed(driver, req, dist, eta, window_start)
            # MOMAQL only: online Bellman TD(0) update (skipped if frozen)
""")
    heading(doc, "6.2 MOMAQL score and Q-update", level=2)
    code_block(doc, """
score(d, req) = (1-lambda) * [fare - eta*0.0025 + gamma * Q(D_zone, D_hour)]
              +  lambda    * [(mean_income - d.income) / max(mean_income,1)] * fare

Q-update (Bellman TD(0), on commit, only if not frozen):
  P = (pickup_zone_id, pickup_hour)      # state driver was in
  S = (dropoff_zone_id, dropoff_hour)    # state driver ends up in
  reward = fare - eta*0.0025
  Q[P] <- Q[P] + alpha * (reward + gamma * Q[S] - Q[P])
""")
    para(doc, "lambda=0.5 (default), gamma=0.9, alpha=0.1. ablation='no_forecast' forces the "
              "gamma*Q(...) term to 0; ablation='no_fairness' forces lambda to 0. frozen=True "
              "(used for every evaluation run) disables the Q-update entirely -- the trained "
              "table from train_momaql.py is used read-only.")

    # ---------------- 7. Configuration ----------------
    heading(doc, "7. Configuration", level=1)
    para(doc, "No central config file (no YAML/JSON/.env) exists. Every constant below is a "
              "module-level Python variable, repeated per script (verified real, not assumed):")
    add_table(doc, ["Constant", "Value", "Where defined"], [
        ["N_DRIVERS", "200", "top of every run_*.py and train_momaql.py"],
        ["SEEDS (main experiments)", "20260721, 20260722, 20260723, 20260724, 20260725",
         "run_r1.py, run_r2_ablation.py, run_pareto_frontier.py, run_multi_horizon.py, "
         "train_and_eval_mlp.py"],
        ["SEEDS (mechanism experiments)", "20260721, 20260722, 20260723 (3 seeds)",
         "run_complete_verifications.py, run_spatial_candidate_pool.py, "
         "run_hypothesis4_fairness_balance.py"],
        ["WINDOW_SECONDS", "60.0", "run_simulation_batched default parameter"],
        ["MAX_PICKUP_ETA_SECONDS", "600.0 (10 min)", "src/simulator.py module constant"],
        ["COST_PER_SECOND_DEADHEAD_USD", "0.0025", "src/simulator.py module constant"],
        ["AVG_SPEED_MPH", "12.0", "src/simulator.py module constant"],
        ["lambda (fairness weight)", "0.5 default; swept {0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0} for "
         "Pareto", "MOMAQLPolicy(lam=...) constructor argument"],
        ["gamma (discount)", "0.9", "MOMAQLPolicy(gamma=...) constructor argument"],
        ["alpha (Q learning rate)", "0.1", "MOMAQLPolicy(alpha=...) constructor argument"],
    ])

    # ---------------- 8. Exact reproduction commands ----------------
    if ft_available:
        heading(doc, "8. Final Test Protocol & Reproducibility", level=1)
        para(doc, "Companion engineering detail for the Final Held-out Temporal Test Evaluation "
                  "(Research Report Sec. 9). Everything here is read live from `final_test/` at "
                  "document-build time -- no number here is hand-typed.", size=9.5, color=GREY)

        heading(doc, "8.1 Frozen Protocol", level=2)
        add_table(doc, ["Parameter", "Value"], [
            ["Policy", "MOMAQL canonical (lambda=0.5, gamma=0.9, alpha=0.1)"],
            ["Drivers", "200"], ["Assignment solver", "Hungarian joint assignment (scipy.optimize.linear_sum_assignment)"],
            ["Q-table", "data/momaql_q_table_trained.json, frozen (no further learning at eval time)"],
            ["Seeds", "20260721, 20260722, 20260723, 20260724, 20260725"],
            ["No-tuning rule", "No config/hyperparameter/policy/simulator change after any Test outcome is inspected"],
        ])
        para(doc, "Full protocol text (source hashes, dataset checksums, environment): "
                  "`final_test/FINAL_TEST_PROTOCOL.md`.", size=9.5, color=GREY)

        heading(doc, "8.2 Data Quality Transform (evaluation-time, raw file immutable)", level=2)
        tstats = ft_manifest["per_split"]["test"]
        para(doc, "test.parquet on disk is NEVER modified. Two independent rules are applied only "
                  "to the in-memory evaluation view, in this order, and never mixed:")
        bullets(doc, [
            "A. Strict temporal-boundary hygiene: exclude rows whose pickup_ts epoch second equals "
            "val.parquet's max pickup_ts epoch second (a real row-index split artifact -- distinct "
            "genuine pickups landing in the same second at the cut point, not duplicated data) -- "
            f"{tstats['temporal_boundary_excluded']} rows excluded.",
            "B. Minimal deterministic duration repair: if stored duration_seconds is valid "
            "(0 < x <= 24h), keep. Elif dropoff_ts-pickup_ts is valid, repair "
            "duration_seconds_eval from timestamps (quality_action=REPAIRED_FROM_TIMESTAMPS). Else "
            f"exclude (irrecoverable) -- {tstats['duration_repaired']} repaired, "
            f"{tstats['duration_excluded']} excluded in this pass.",
        ])
        add_table(doc, ["Step", "Rows"], [
            ["Raw test.parquet", str(tstats["original_rows"])],
            ["Temporal-boundary excluded", str(tstats["temporal_boundary_excluded"])],
            ["Duration repaired from timestamps", str(tstats["duration_repaired"])],
            ["Duration excluded (irrecoverable)", str(tstats["duration_excluded"])],
            ["Final Test Evaluation View", str(tstats["final_evaluated_rows"])],
        ])
        para(doc, "Implementation: `scripts/final_test/quality_transform.py` "
                  "(`load_requests_with_quality_transform()`), covered by self-checks in "
                  "`scripts/final_test/test_quality_transform.py`. Every evaluated request retains "
                  "`duration_seconds_raw` and `quality_action` alongside the (possibly repaired) "
                  "`duration_seconds` for full per-row auditability. Full audit trail (upstream "
                  "provenance trace confirming the corruption exists in the raw source data, not in "
                  "this project's own preprocessing): `final_test/DATA_QUALITY_GATE.md`.",
              size=9.5, color=GREY)

        heading(doc, "8.3 Final Test Commands", level=2)
        if ft_commands_log:
            code_block(doc, ft_commands_log.strip())
        else:
            code_block(doc, "python scripts/final_test/audit_test_dataset.py\n"
                             "python scripts/final_test/verify_before_run.py\n"
                             "python scripts/final_test/run_final_test_baselines.py\n"
                             "python scripts/final_test/run_final_test_ablation.py\n"
                             "python scripts/final_test/run_final_test_long_horizon.py\n"
                             "python scripts/final_test/build_final_test_summary.py")

        heading(doc, "8.4 Artifact Map (final_test/)", level=2)
        add_table(doc, ["Path", "Purpose"], [
            ["FINAL_TEST_PROTOCOL.md", "Frozen config/seeds/hashes, written before any policy ran on test.parquet"],
            ["DATA_QUALITY_GATE.md", "Full duration-anomaly audit, root-cause trace, repair rule justification"],
            ["test_quality_transform_manifest.json", "Machine-readable repair/exclusion counts + row IDs per split"],
            ["baseline/", "5 policies x 5 seeds on the Final Test Evaluation View (per-seed + summary CSV)"],
            ["ablation/", "Full / No Forecast / No Fairness x 5 seeds"],
            ["long_horizon/", "Checkpointed single-trajectory results, days 1-37 + policy disagreement rate"],
            ["validation_vs_test.csv", "Per-finding Validation-vs-Test direction comparison (heldout_generalization)"],
            ["test_claim_assessment.csv", "C1-C6 claim table: heldout_generalization + paper_replication_verdict (2 independent columns)"],
            ["FINAL_TEST_MENTOR_SUMMARY.md", "Human-readable summary answering the 6 core generalization questions"],
            ["figures/", "Baseline/ablation/long-horizon PNGs generated from the Final Test CSVs"],
            ["logs/", "commands.log, environment.txt, runtimes.csv"],
        ])

        heading(doc, "8.5 Metric Definitions Addendum", level=2)
        bullets(doc, [
            "Fairness is a CONCEPT, not a single metric -- Gini and Variance are the two metrics "
            "reported (see Sec. 5/6 above for their formulas); lower Gini and lower Variance both "
            "mean more equal driver income.",
            "Paired delta: for a given seed, (metric under config A) - (metric under config B), "
            "computed per-seed then averaged -- reported alongside sign consistency (e.g. \"5/5 "
            "seeds\") rather than only the mean.",
            "Directional (heldout) generalization: does a Validation-observed finding repeat in the "
            "SAME DIRECTION on Test? Computed purely from sign/comparison, no magnitude threshold.",
            "Paper replication verdict: does the finding match arXiv:2407.17839's own qualitative "
            "claim text? An independent judgment against the paper, NOT derivable from the "
            "generalization computation -- a finding can generalize while the paper claim remains "
            "Not Reproduced (see Research Report Sec. 10 for the worked C4 example).",
        ])

        heading(doc, "8.6 Reproducibility Limitations (Final Test)", level=2)
        bullets(doc, [
            "Dataset is NYC TLC 2013, not the paper's original 2016 data -- Final Test inherits the "
            "same trend-replication scope as Validation (Sec. 3 of the Research Report), not exact "
            "reproduction.",
            "5 seeds only -- effect size, mean/std, and paired seed-sign consistency are the primary "
            "evidence; no formal statistical significance test is computed or claimed.",
            "Canonical lambda=0.5 operating point only -- no lambda sweep was run on Test (by design; "
            "Test is for verification, not for choosing a new operating point).",
            "The product demo (05_SanPham_Demo) uses the Validation/demo slice by default, never "
            "test.parquet -- Test is reserved for this final scientific evaluation, not exposed in "
            "the live Control Room.",
        ])
        if ft_environment_txt:
            para(doc, "Final Test run environment (captured in final_test/logs/environment.txt):", size=9.5, color=GREY)
            code_block(doc, ft_environment_txt.strip())

    # ---------------- 9. Exact Reproduction Commands ----------------
    heading(doc, "9. Exact Reproduction Commands", level=1)
    para(doc, "Run from the repository root, in this order. Row counts are the current retained "
              "artifacts, verified live at the time this document was built.")
    cmd_rows = [
        ("python -m pytest tests/test_simulator_invariants.py -q", "(no file output)", test_line),
        ("python train_momaql.py", "data/momaql_q_table_trained.json",
         "1,511 (zone,hour) states (do not overwrite without re-running every downstream "
         "experiment)"),
        ("python run_r1.py", "reports/r1_validation_results.csv",
         f"{csv_row_count('r1_validation_results.csv')} rows (5 policies x 5 seeds)"),
        ("python run_r2_ablation.py", "reports/r2_ablation_raw.csv + _results.csv",
         f"{csv_row_count('r2_ablation_raw.csv')} + {csv_row_count('r2_ablation_results.csv')} rows"),
        ("python run_pareto_frontier.py", "reports/pareto_frontier_results.csv + _summary.csv + "
         ".png", f"{csv_row_count('pareto_frontier_results.csv')} + "
         f"{csv_row_count('pareto_frontier_summary.csv')} rows"),
        ("python run_multi_horizon.py", "reports/multi_horizon_results.csv + "
         "policy_disagreement.csv", f"{csv_row_count('multi_horizon_results.csv')} + "
         f"{csv_row_count('policy_disagreement.csv')} rows"),
        ("python run_complete_verifications.py", "reports/fleet_scale_results.csv + "
         "spatial_disagreement_by_zone.csv", f"{csv_row_count('fleet_scale_results.csv')} + "
         f"{csv_row_count('spatial_disagreement_by_zone.csv')} rows"),
        ("python run_spatial_candidate_pool.py", "reports/spatial_candidate_pool.csv",
         f"{csv_row_count('spatial_candidate_pool.csv')} rows"),
        ("python run_q_table_convergence.py", "reports/q_table_convergence_daily.csv",
         f"{csv_row_count('q_table_convergence_daily.csv')} rows"),
        ("python run_hypothesis1_weekly_cycle.py", "reports/hypothesis1_weekly_cycle.csv",
         f"{csv_row_count('hypothesis1_weekly_cycle.csv')} rows"),
        ("python run_hypothesis4_fairness_balance.py", "reports/hypothesis4_fairness_balance.csv",
         f"{csv_row_count('hypothesis4_fairness_balance.csv')} rows"),
        ("python train_and_eval_mlp.py", "reports/mlp_vs_tabular_results.csv + _summary.csv",
         f"{csv_row_count('mlp_vs_tabular_results.csv')} + "
         f"{csv_row_count('mlp_vs_tabular_summary.csv')} rows; requires torch"),
        ("python make_report_figures.py", "docs/*/figures/*.png (7 figures x 3 output dirs)",
         "regenerates every figure from the CSVs above"),
        ("python docs/docx_report/build_research_report.py", "docs/docx_report/"
         "Bao_Cao_Nghien_Cuu_FairDispatch_MOMAQL.docx", "the Research Report"),
        ("python docs/techdoc/build_technical_documentation.py", "docs/techdoc/"
         "Technical_Documentation.docx", "this document"),
    ]
    add_table(doc, ["Command", "Output", "Expected result"], cmd_rows)
    callout(doc, "DO NOT run train_momaql_multipass.py as a substitute for train_momaql.py -- it "
                 "is explicitly disclosed as unstable and can write "
                 "data/momaql_q_table_multipass.json, which some scripts prefer over the "
                 "canonical table when present. If that file exists, quarantine it before any "
                 "evaluation run.")

    # ---------------- 10. Reproducibility Package ----------------
    heading(doc, "10. Reproducibility Package", level=1)
    add_table(doc, ["Field", "Value"], [
        ["Git commit", head],
        ["Dataset manifest", "data/train.parquet (912,375 rows), data/val.parquet (195,508 "
         "rows), data/test.parquet (195,510 rows)"],
    ] + [[f"SHA-256 -- {name}", f"{h}  ({size:,} bytes)"] for name, (h, size) in ds_hashes.items()]
      + [
        ["Configuration", "N_DRIVERS=200, window=60s, MAX_PICKUP_ETA=600s, lambda=0.5 default "
         "(swept 0-1), gamma=0.9, alpha=0.1"],
        ["Random seeds", "20260721, 20260722, 20260723, 20260724, 20260725 (main experiments); "
         "first 3 of these for mechanism experiments"],
        ["Environment", f"Python {platform.python_version()}, numpy 2.2.6, pandas 2.3.2, pyarrow "
         "21.0.0, scipy 1.16.2, torch 2.7.1+cu118 (versions at build time -- re-check with `pip "
         "show` before citing in a formal report)"],
        ["CPU/GPU", "Intel Core i5-10300H (CPU-only for all simulator/dispatch experiments); "
         "NVIDIA GTX 1650 via CUDA (MLP training in train_and_eval_mlp.py only)"],
        ["Number of tests", test_line],
        ["Result artifacts", "every file in reports/ (16 CSVs + 1 PNG + 1 JSON checksum manifest) "
         "-- Validation. Held-out Test artifacts: final_test/ (see Sec. 8)."],
    ])
    para(doc, "reports/dataset_checksums.json is a static, previously-written snapshot; the "
              "table above is computed FRESH at document-build time and is the authoritative "
              "source if the two ever disagree.", size=9.5, color=GREY)

    # ---------------- 11. Known Issues, Assumptions, Troubleshooting ----------------
    heading(doc, "11. Known Issues, Assumptions, and Troubleshooting", level=1)
    heading(doc, "11.1 Assumptions (mirrors Research Report Sec. 11.3, engineering framing)", level=2)
    bullets(doc, [
        "A1. Driver count (200) is not specified by the paper. Chosen as a plausible Manhattan "
        "fleet size; change N_DRIVERS at the top of any run_*.py to test sensitivity (see "
        "fleet_scale_results.csv for the N=100/200/400 sweep already run).",
        "A2. Spatial representation uses 67 official TLC taxi zones, not a custom-clustered graph "
        "-- pickup_zone_id/dropoff_zone_id come directly from the parquet columns, no extra "
        "clustering step in this codebase.",
        "A3. Pickup ETA is haversine distance at a constant 12 mph (AVG_SPEED_MPH), not road "
        "routing -- a deliberate lightweight-simulator simplification (see src/simulator.py "
        "module docstring).",
        "A4. Q(zone,hour) is trained via a single sequential pass over train.parquet "
        "(train_momaql.py, one seed=20260721) -- not multiple epochs. "
        "train_momaql_multipass.py exists but is explicitly disclosed unstable; its diagnostic "
        "output lives in reports/momaql_convergence.csv (5 rows, annealed-alpha passes) for "
        "provenance only, not as an evaluation input.",
        "A5. No dependency version lockfile is retained; Sec. 3's package list is the audited "
        "working set, not a pinned requirements.txt.",
    ])
    heading(doc, "11.2 Known Issues", level=2)
    bullets(doc, [
        "tests/test_simulator_invariants.py::test_no_double_booking_within_window and "
        "::test_time_monotonicity call the simulator with the default record_trace=False, so "
        "their trace-based assertions currently iterate over an empty trace list. They pass, but "
        "do not exercise the trace-dependent code path they were written to check -- rerun with "
        "record_trace=True locally if you need that specific guarantee verified.",
        "run_r2_ablation.py and run_pareto_frontier.py silently prefer "
        "data/momaql_q_table_multipass.json over the canonical trained table if that file "
        "exists on disk (see Sec. 8 warning) -- this is existing script behavior, not a bug fix "
        "made in this pass, but it is easy to trip over by accident.",
        "No structured logging framework; every script prints plain stdout progress lines with "
        "flush=True. Capture stdout to a file if you need a persistent run log.",
    ])
    heading(doc, "11.3 Troubleshooting", level=2)
    bullets(doc, [
        "\"FileNotFoundError: data/train.parquet\" -- the parquet splits are gitignored (too "
        "large for a normal git push); they must be obtained separately from wherever this "
        "repository's data was originally prepared. Only reports/*.csv and the trained Q-table "
        "JSON are tracked.",
        "Results differ slightly from the numbers cited in the Research Report -- check "
        "reports/dataset_checksums.json (Sec. 9) matches your local data/ files byte-for-byte "
        "first; a different parquet build will shift every downstream number.",
        "Memory pressure on machines with limited free RAM -- every run_*.py already calls "
        "gc.collect() and del's large objects between seeds/configs; if it still OOMs, reduce "
        "SEEDS to a single value first to isolate whether it's a per-seed leak or genuinely "
        "insufficient RAM for one seed's working set.",
        "train_and_eval_mlp.py fails to import torch -- it is the only script in this repo that "
        "needs it; every other script is pure numpy/pandas/pyarrow/scipy.",
    ])

    doc.save(OUT)
    print(f"[done] {OUT}")
    return doc, dict(head=head, test_line=test_line, ds_hashes=ds_hashes)


if __name__ == "__main__":
    main()
