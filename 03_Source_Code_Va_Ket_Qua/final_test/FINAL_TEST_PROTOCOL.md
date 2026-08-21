# Final Test Protocol — FairDispatch Held-out Temporal Test Evaluation

**Frozen before any policy touches `test.parquet`. After this document is
written, criteria are NOT modified based on test results — see Absolute
Rule at the end.**

- `created_at`: 2026-08-21 (Asia/Ho_Chi_Minh)
- `resolved_project_path`: `D:\ProjectVSF\FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\03_Source_Code_Va_Ket_Qua`
- `working_tree_status`: this repo is a fresh standalone git repo (see `git log -1`), no prior commits touched `final_test/`

## Purpose

Verify whether the core research conclusions developed on Train+Validation
(implementation frozen, hyperparameters frozen, ablation/long-horizon
findings established) generalize to `test.parquet`, a temporal split never
used during development. Not a tuning round.

## Evaluation-view data quality transform (frozen, defined before any Test
policy outcome was inspected — see `DATA_QUALITY_GATE.md` for the full audit)

1. **Temporal-boundary hygiene**: exclude `test.parquet` rows whose
   `pickup_ts` epoch second equals `val.parquet`'s max `pickup_ts` epoch
   second (`1374412620`) — 3 rows excluded.
2. **Duration-quality minimal deterministic repair**: if
   `0 < duration_seconds <= 24h` keep as-is; elif
   `0 < (dropoff_ts - pickup_ts) <= 24h` repair `duration_seconds` from
   timestamps; else exclude. Result: 32 rows repaired, 1 row excluded
   (`row_idx=164421`, zero-duration, unrecoverable).
3. Applied uniformly to train/val/test via `scripts/final_test/quality_transform.py`;
   train/val verified programmatically to have 0 repairs/exclusions.
4. `test.parquet` on disk is untouched: sha256 `96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72`
   (matches `reports/dataset_checksums.json`), verified again after transform.
5. **Final Test Evaluation View**: 195,510 − 3 − 1 = **195,506 requests**.

Full manifest: `final_test/test_quality_transform_manifest.json`.

## Frozen configuration (resolved from repository source, not invented)

| Parameter | Value | Source |
|---|---|---|
| Policy (primary) | MOMAQL canonical | `src/policies.py:MOMAQLPolicy` |
| Drivers | 200 | `N_DRIVERS` in `run_r1.py`/`run_r2_ablation.py`/`run_multi_horizon.py` |
| λ | 0.5 | `MOMAQLPolicy.__init__` default + explicit in `run_r2_ablation.py` |
| γ | 0.9 | `MOMAQLPolicy.__init__` default |
| α | 0.1 | `MOMAQLPolicy.__init__` default (unused at eval time — Q-table is frozen, no further learning) |
| Batch window | 60 sec | `simulator.py` (`WINDOW_SECONDS` convention, matches product backend `SimulationSession.WINDOW_SECONDS`) |
| Pickup ETA threshold | 600 sec | `simulator.py:MAX_PICKUP_ETA_SECONDS` |
| Deadhead cost | $0.0025/sec | `simulator.py:COST_PER_SECOND_DEADHEAD_USD` |
| Assignment solver | Hungarian joint assignment | `policies.py:hungarian_batch_assign` (scipy `linear_sum_assignment`) |
| Q-table checkpoint | `data/momaql_q_table_trained.json` | sha256 `9af13c33219f989e23a8ee9eca9e0cda3262996e34849bcc6dfab0cab5d64bdb` (matches manifest); frozen (no further learning at eval) |
| Dataset | `test.parquet` (post quality-transform) | sha256 `96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72` (raw, unmodified) |

## Seeds (canonical, from `run_r1.py`/`run_r2_ablation.py`/`run_multi_horizon.py`)

```text
[20260721, 20260722, 20260723, 20260724, 20260725]
```

## Engine source snapshot

```text
src/policies.py    sha256 fe9e95883cbfa494748ac7a2fc115eda3bfe095ea4f05c7f0b2f368b0732f5ac
src/simulator.py   sha256 b2dbf2e927d622f38d86039bdb8e5ea81b0984f405781c73527716078890368d
Python 3.12.10, numpy 2.2.6, scipy 1.16.2, pandas 2.3.2, pyarrow 21.0.0
Windows (MINGW64_NT-10.0-26200)
```

## Metrics (same as canonical validation)

Total Utility, Gini, Variance, Std, Served Requests, Average Driver Income,
Average Deadhead. No invented metric.

## Experiments

### A. Main Baseline
5 policies (MOMAQL, Greedy, Nearest, LAF, Exact REASSIGN) × 5 canonical
seeds, 200 drivers, on the Final Test Evaluation View.

### B. Key Ablation
MOMAQL Full / No Forecast / No Fairness × 5 canonical seeds, same Q-table,
same config as `run_r2_ablation.py`.

### C. Long-Horizon
Test span = 42 calendar days (audited, `final_test/test_dataset_audit.json`)
→ **sufficient for the full canonical checkpoint set through Day 37**.
Checkpoints: `[1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 37]`, single trajectory per
(config, seed) with checkpoints — same methodology as
`run_multi_horizon.py` (not independent reruns per checkpoint). Matches
`run_multi_horizon.py` exactly: all 3 configs (full/no_forecast/no_fairness)
recorded per checkpoint, plus the full-vs-no_forecast policy disagreement
rate (corrected from an earlier draft of this protocol that said "Full vs
No Forecast only" -- the actual canonical validation script runs all 3).

### Explicitly NOT run on Test (per master plan Part E)
λ sweep, exploratory mechanism probes (weekly-cycle, candidate-depth,
core/periphery, Q-state discovery, fairness-score-share), fleet sensitivity
(100/200/400 driver comparison), MLP sensitivity benchmark.

## Absolute rule — no test-driven tuning

After any Test result becomes visible, λ/γ/α, policy score, Q initialization,
driver count, seed list, thresholds, metric definitions, and simulator
behavior are **not** modified for the purpose of improving Test results. If
a genuine implementation bug is found post-hoc: document it, fix only if
objectively a bug, rerun all affected Test experiments, document both the
invalidated and corrected run, never cherry-pick.

## Output paths

```text
final_test/baseline/test_baseline_per_seed.csv
final_test/baseline/test_baseline_summary.csv
final_test/ablation/test_ablation_per_seed.csv
final_test/ablation/test_ablation_summary.csv
final_test/long_horizon/test_long_horizon.csv
final_test/validation_vs_test.csv
final_test/test_claim_assessment.csv
final_test/FINAL_TEST_MENTOR_SUMMARY.md
final_test/figures/*.png
final_test/logs/commands.log, environment.txt, runtimes.csv
```
