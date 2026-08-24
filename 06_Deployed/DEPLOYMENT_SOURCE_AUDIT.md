# Deployment Source Audit

## 1. Canonical hash verification (before any copy)

| File | Expected SHA-256 | Actual SHA-256 | Match |
|---|---|---|---|
| `test.parquet` | `96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72` (48,188,109 bytes) | `96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72` (48,188,109 bytes) | **YES** |
| `momaql_q_table_trained.json` | `9af13c33219f989e23a8ee9eca9e0cda3262996e34849bcc6dfab0cab5d64bdb` | `9af13c33219f989e23a8ee9eca9e0cda3262996e34849bcc6dfab0cab5d64bdb` | **YES** |
| `src/policies.py` | `fe9e95883cbfa494748ac7a2fc115eda3bfe095ea4f05c7f0b2f368b0732f5ac` | `fe9e95883cbfa494748ac7a2fc115eda3bfe095ea4f05c7f0b2f368b0732f5ac` | **YES** |
| `src/simulator.py` | `b2dbf2e927d622f38d86039bdb8e5ea81b0984f405781c73527716078890368d` | `b2dbf2e927d622f38d86039bdb8e5ea81b0984f405781c73527716078890368d` | **YES** |

No discrepancy. All 4 canonical hashes matched exactly before any file was
copied or read further. `test.parquet` found at
`D:\ProjectVSF\fairdispatch_v3_clean\data\test.parquet` (search order:
`03_Source_Code_Va_Ket_Qua\data\test.parquet` -- not present there --
then this path -- found).

## 2. `05_SanPham_Demo` integrity (immutable local backup)

16 files hashed (excluding `__pycache__/*.pyc`, which are Python-regenerated
bytecode caches, not source -- regenerating them by merely importing the
modules again is expected and is not a source edit; they are excluded from
the "must not change" contract for that reason, stated here explicitly
rather than silently).

| Stage | Files hashed | Diffs from before |
|---|---|---|
| Before any 06_Deployed work | 16 | -- |
| Mid-task (after building test_eval.parquet, before Docker) | 16 | **0** |
| Final (after Docker build/run/cleanup) | 16 | **0** |

**Result: PASS.** `05_SanPham_Demo` byte-identical at every checkpoint.
Full before/after hash sets available on request (computed via a one-off
script, not stored in the repo to avoid clutter).

## 3. Source engine hashes (bundled into `06_Deployed/engine/`)

| File | SHA-256 (bundled copy) | Matches canonical |
|---|---|---|
| `engine/src/policies.py` | `fe9e95883cbfa494748ac7a2fc115eda3bfe095ea4f05c7f0b2f368b0732f5ac` | YES |
| `engine/src/simulator.py` | `b2dbf2e927d622f38d86039bdb8e5ea81b0984f405781c73527716078890368d` | YES |
| `data/momaql_q_table_trained.json` | `9af13c33219f989e23a8ee9eca9e0cda3262996e34849bcc6dfab0cab5d64bdb` | YES |

Copied verbatim (`cp`, no edits) from `03_Source_Code_Va_Ket_Qua/src/` and
`03_Source_Code_Va_Ket_Qua/data/`. Verified identical to the pre-copy
canonical hashes in section 1.

## 4. Raw Test source

- Path: `D:\ProjectVSF\fairdispatch_v3_clean\data\test.parquet`
- Rows: 195,510
- SHA-256: `96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72`
- Never written to. `scripts/build_test_eval_parquet.py` only opens it for
  reading (`pq.read_table`), never `pq.write_table` to this path.

## 5. Final Test quality transform manifest used

- `03_Source_Code_Va_Ket_Qua/final_test/test_quality_transform_manifest.json`
  -- `boundary_epoch_second = 1374412620` (read from this file at build
  time, not hard-coded, then cross-checked against
  `03_Source_Code_Va_Ket_Qua/final_test/split_integrity.json`'s independent
  `val_max_epoch_seconds = 1374412620` -- both agree).
- Transform logic imported directly from
  `03_Source_Code_Va_Ket_Qua/scripts/final_test/quality_transform.py`
  (`load_requests_with_quality_transform`), not reimplemented.

## 6. Output of the build

`06_Deployed/data/test_eval.parquet` -- see
`06_Deployed/data/deployment_data_manifest.json` for the full, machine
-readable record (raw source hash, transform stats, output hash). Summary:

- rows: 195,506 (195,510 raw - 3 temporal-boundary - 1 duration-invalid + 32
  repaired-in-place)
- duration_repaired: 32, duration_excluded: 1, boundary_excluded: 3
- SHA-256 (this deploy-only artifact, not a "canonical" hash since it did
  not exist before this task): `2984be13d2c13a07ce4ff29ada928595ecd8079848b55d18a522dedd68c91b08`
