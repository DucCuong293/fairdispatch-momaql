# Research Report Update Changelog — Final Held-out Test Evaluation

No experiment rerun. No raw numerical result changed. Source: `docs/docx_report/build_research_report.py`
edited to read `final_test/*.csv` + `final_test/test_quality_transform_manifest.json` at build
time (same philosophy as the rest of the script — nothing hand-typed from memory), then rebuilt
with `python docs/docx_report/build_research_report.py`.

## Sections updated

- **Section 0 (Executive Summary)**: added a paragraph stating the story is
  "Validation-developed trend replication with held-out temporal test support" (not
  "reproduced completely"); flagged that the original C5 bullet conflated Utility and
  Fairness components (fixed properly in the new Section 10 dual-verdict table).
- **New Section 9 "Final Held-out Test Evaluation"** (inserted between old Results §8 and
  Replication Assessment, which shifted from §9 → §10): purpose, Test Data Quality Gate
  (195,510 → 3 boundary-excluded → 32 repaired / 1 excluded → 195,506 evaluated), frozen
  configuration, held-out baseline/ablation/long-horizon results side-by-side with
  Validation, and the 13/13 generalization headline with an explicit callout that
  generalization ≠ paper reproduction.
- **Section 10 "Replication Assessment"** (was §9): kept the original Validation-only
  claim table unchanged, added a NEW dual-column table (`heldout_generalization`,
  `paper_replication_verdict`) sourced directly from `final_test/test_claim_assessment.csv`
  — colored independently, never merged into one verdict.
- **Sections 11 (was §10) / 11.1-11.3**: renumbered only, content unchanged.
- **Section 12 "Conclusion"** (was §11): added a paragraph on held-out generalization
  strengthening confidence without converting non-reproduced claims into reproduced ones;
  final verdict sentence added verbatim: "Strong Partial Trend Replication with held-out
  temporal support."

## Figures added

None new (final_test/figures are referenced conceptually in prose per report style
guidance to avoid overloading; existing Validation figures 1-6 unchanged).

## Key result numbers used (all read live from final_test/*.csv, verify against source)

- Test Data Quality Gate: 195,510 → 3 → 32 repaired / 1 excluded → 195,506
- MOMAQL Test Utility ≈ 1,454,053 / Gini ≈ 0.2011 (Validation: 1,422,441 / 0.2037)
- Full vs No-Forecast Utility: Test +17.1% (Validation +22.4%)
- Long-horizon Day 21: Val +5.1%, Test +1.2%. Day 37: Val +20.2%, Test +13.4%.
- 13/13 findings generalized directionally.
- Claim matrix: C1 Reproduced, C2 Reproduced (adapted-baseline scope), C3 Partial, C4 Not
  Reproduced, C5 Partial (Utility yes / Fairness no), C6 Partial (Inequality yes / Utility no).

## Files read

`final_test/FINAL_TEST_PROTOCOL.md`, `DATA_QUALITY_GATE.md`, `FINAL_TEST_MENTOR_SUMMARY.md`,
`test_quality_transform_manifest.json`, `validation_vs_test.csv`, `test_claim_assessment.csv`,
`baseline/test_baseline_summary.csv`, `ablation/test_ablation_results.csv`,
`long_horizon/test_long_horizon.csv`; existing `reports/*.csv` (Validation, unchanged read path).

## No experiment rerun

Confirmed — this changelog only touches `docs/docx_report/build_research_report.py`
(report-generation code) and its regenerated `.docx` output. No policy, simulator, or
`final_test/` script was executed as part of this task.
