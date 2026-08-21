# Final Test Mentor Summary — FairDispatch Held-out Temporal Verification

## 1. Why held-out test was run

To verify whether core research conclusions developed on Train+Validation
generalize to `test.parquet`, a temporal split never used during
implementation, hyperparameter selection, or ablation/long-horizon
development. Not a tuning round -- see `FINAL_TEST_PROTOCOL.md` (frozen
before any Test policy outcome was inspected).

## 2. Dataset integrity

- `test.parquet` checksum verified against `reports/dataset_checksums.json`
  (unchanged throughout this evaluation).
- Temporal split integrity: `train_max < val_min < test_min` holds strictly
  after a documented 1-second boundary-tie fix (3 rows) -- see
  `split_integrity.json`.
- Data quality gate: 33/195,510 test rows (0.017%) had a corrupted
  `duration_seconds` field (timestamps themselves were valid) -- 32 repaired
  from `dropoff_ts - pickup_ts`, 1 irrecoverable row excluded. Full audit:
  `DATA_QUALITY_GATE.md`. Final Test Evaluation View: **195,506 requests**.

## 3. Frozen protocol

MOMAQL canonical (λ=0.5, γ=0.9, α=0.1), 200 drivers, Hungarian joint
assignment, trained Q-table (frozen), 5 canonical seeds
`[20260721..20260725]`. Full details: `FINAL_TEST_PROTOCOL.md`.

## 4. Main baseline results

Validation ranking (Utility): MOMAQL > Greedy > Nearest > LAF > Exact REASSIGN
Test ranking (Utility): MOMAQL > Greedy > Nearest > LAF > Exact REASSIGN
Ranking MATCHES between Validation and Test.

See `baseline/test_baseline_summary.csv`, `figures/test_baseline_utility_gini.png`,
`figures/validation_vs_test_baseline.png`.

## 5. Ablation results

Full vs No Forecast Utility benefit: **Yes** generalized to Test.
No Forecast fairness advantage (lower Gini than Full): **Yes** generalized to Test.
No Fairness inequality increase: **Yes** generalized to Test.

See `ablation/test_ablation_per_seed.csv`, `figures/test_ablation.png`, `validation_vs_test.csv`.

## 6. Long-horizon result

Test span = 42 calendar days >= 37 -> full canonical checkpoint set [1,2,3,4,5,6,7,14,21,28,37] evaluated. Delayed long-horizon utility divergence: **Yes** generalized to Test.

## 7. Validation vs Test

13/13 findings generalized (same direction on Validation and Test). Full table: `validation_vs_test.csv`.

## 8. Claim-by-claim assessment

Two DISTINCT columns are reported per claim -- never merged into one verdict:
`heldout_generalization` (does the Validation-observed finding repeat in the
same direction on Test?) and `paper_replication_verdict` (does the finding
match arXiv:2407.17839's own qualitative claim?). A finding can generalize
(be temporally robust) while the underlying paper claim remains Not
Reproduced -- see C4 below.

| Claim | Held-out generalization | Paper replication verdict |
|---|---|---|
| C1: Utility-Fairness trade-off exists | Generalized | Reproduced |
| C2: MOMAQL provides a strong balanced point vs adapted baselines | Generalized | Reproduced within adapted-baseline scope |
| C3: Long-horizon behavior / delayed utility divergence | Generalized | Partially Reproduced / strengthened by held-out support |
| C4: Forecast improves long-term fairness | Generalized | Not Reproduced |
| C5: Forecast improves Utility + Fairness (joint) | Generalized | Partially Reproduced (Utility component reproduced/generalized; Fairness component NOT reproduced -- No Forecast is fairer on both Validation and Test) |
| C6: Removing fairness raises Utility + inequality | Generalized | Partially Reproduced (Inequality component reproduced/generalized; Utility component NOT reproduced -- removing fairness LOWERS Utility on both Validation and Test) |

Full table with evidence/caveats: `test_claim_assessment.csv`.

## 9. What generalized

- MOMAQL Utility > Greedy
- MOMAQL Gini < Greedy
- MOMAQL Utility > Nearest
- MOMAQL Gini < Nearest
- LAF is fairness extreme (lowest Gini among baselines)
- Full Utility > No Forecast
- No Forecast Gini < Full (fairer)
- No Fairness Gini > Full (less equal)
- No Fairness Utility direction vs Full
- Full vs No Forecast Utility gain at Day 7
- Full vs No Forecast Utility gain at Day 21
- Full vs No Forecast Utility gain at Day 37
- Long-horizon Day 37 fairness: No Forecast Gini vs Full

## 10. What did not generalize

(none -- all audited findings generalized)

## 11. Limitations

- Dataset is NYC TLC 2013 (not the paper's original dataset/year) -- this
  remains trend replication under a reconstructed implementation, not exact
  paper reproduction.
- Only 5 seeds -- effect size, mean/std, and paired seed-sign consistency
  are the primary evidence; no formal statistical significance is claimed.
- Canonical λ=0.5 operating point only -- no λ sweep run on Test (by design,
  per protocol Part E).
- 33/195,510 test rows required a documented, pre-specified data-quality
  repair (32) or exclusion (1) before evaluation -- see `DATA_QUALITY_GATE.md`.


## 12. Final scientific verdict

**Strong Partial Trend Replication with held-out temporal support**

To be explicit about what this verdict does and does not mean:

- **13/13 pre-specified Validation findings generalized directionally to Test.**
- This strengthens confidence that the reconstructed implementation's
  observed behavior is temporally robust.
- **It does NOT convert previously non-reproduced paper claims into
  reproduced claims.**
- **Forecast fairness improvement (C4) remains Not Reproduced** -- No
  Forecast is fairer than Full on both Validation and Test.
- **C5 and C6 remain Partial** -- each has one component that reproduces
  the paper's claim and one that does not (see section 8 table).

## 13. Files / reproducibility

Protocol: `FINAL_TEST_PROTOCOL.md`. Data quality: `DATA_QUALITY_GATE.md`,
`test_quality_transform_manifest.json`. Raw results:
`baseline/test_baseline_per_seed.csv`, `ablation/test_ablation_per_seed.csv`,
`long_horizon/test_long_horizon.csv`.
Engine source snapshot and environment recorded in `FINAL_TEST_PROTOCOL.md`.

---
**No Final Test outcome was used to choose or modify the data-quality
transform or model configuration.** The quality transform (`DATA_QUALITY_GATE.md`)
and protocol (`FINAL_TEST_PROTOCOL.md`) were frozen before any policy ran on
`test.parquet`.
