# TechDoc Update Changelog — Final Held-out Test Evaluation

No experiment rerun. No raw numerical result changed. Source:
`docs/techdoc/build_technical_documentation.py` edited to read `final_test/*` at build time
(same live-verification philosophy as the rest of the script), then rebuilt with
`python docs/techdoc/build_technical_documentation.py`.

## TechDoc updated

New Section 8 "Final Test Protocol & Reproducibility" inserted between the old Section 7
(Configuration) and old Section 8 (Exact Reproduction Commands, now shifted to Section 9).
Old Section 9 "Reproducibility Package" → 10. Old Section 10 "Known Issues" → 11 (with
11.1-11.3 shifted accordingly). Section 4 "Data Contract" gained a Train/Val/Test role table
at the top (Train → learn Q; Validation → development/analysis/freeze; Test → final held-out
verification only, never used by the live product demo).

## New reproducibility sections

- **8.1 Frozen Protocol** — policy/drivers/solver/Q-table/seeds/no-tuning rule table.
- **8.2 Data Quality Transform** — the two independent rules (temporal-boundary hygiene,
  minimal deterministic duration repair), exact row counts read from
  `test_quality_transform_manifest.json`, pointer to the self-check tests.
- **8.3 Final Test Commands** — verbatim from `final_test/logs/commands.log`.
- **8.4 Artifact Map** — one sentence per `final_test/` path.
- **8.5 Metric Definitions Addendum** — Fairness-as-concept vs Gini/Variance-as-metrics, paired
  delta, and the explicit distinction between `heldout_generalization` (directional repeat) and
  `paper_replication_verdict` (matches the paper's claim) — never conflated.
- **8.6 Reproducibility Limitations (Final Test)** — NYC TLC 2013 scope, 5-seed-only, no
  test-time lambda sweep, product demo never uses test.parquet.

## Artifact map

Table added at 8.4 covering all of `final_test/`'s top-level paths (protocol, data-quality
files, baseline/ablation/long_horizon, validation_vs_test.csv, test_claim_assessment.csv,
mentor summary, figures, logs) — one purpose sentence each, sourced from the actual directory
contents, not invented.

## Commands verified

`final_test/logs/commands.log` read and embedded verbatim in Section 8.3 (audit → verify →
baseline → ablation → long-horizon → summary, in that exact order — matches the frozen
protocol's no-tuning-between-steps requirement).

## No rerun

Yes — confirmed. This changelog only touches `docs/techdoc/build_technical_documentation.py`
(doc-generation code) and its regenerated `.docx` output.
