# Preprocessing Duration Audit — code citations

## 1. This repo's own preprocessing does NOT compute or clean `duration_seconds`

File: `03_Source_Code_Va_Ket_Qua/data/build_sample.py` (lines 38–46, the sampling query):

```sql
SELECT * FROM read_parquet('{p}')
WHERE manhattan_both = true AND quality_flag_bitset = 0
USING SAMPLE {frac*100:.6f} PERCENT (bernoulli, {SEED})
```

and `03_Source_Code_Va_Ket_Qua/data/merge_split.py` (lines 13–29, the split query):

```sql
COPY (SELECT * FROM ({parts_sql}) ORDER BY pickup_ts LIMIT {n_train})
TO 'D:/ProjectVSF/fairdispatch_v3_clean/data/train.parquet' (FORMAT PARQUET)
```//identical pattern for val/test, only LIMIT/OFFSET differ

Both scripts do `SELECT *` — every column, including `duration_seconds`, is passed
through byte-for-byte from the upstream canonical source. **Neither script computes,
derives, recomputes, or filters `duration_seconds` in any way.** The only filter
applied by either script is `manhattan_both = true AND quality_flag_bitset = 0`
(row selection before sampling), and a temporal `ORDER BY pickup_ts` + `LIMIT/OFFSET`
split. There is no duration-specific cleaning rule anywhere in this repository's
own data-prep code.

## 2. Upstream trace: the corruption already exists in the canonical source

Docstring of `build_sample.py` (lines 3–8) names the exact upstream source:

```text
restricted_data/foil_2013_legacy/09_canonical/realistic_2013_splits/
development/source_month={01..08}/part-000.parquet
```

Traced `test.parquet` row `row_idx=164421` (`trip_key=522975df...`,
`source_month=8`, `source_row_number=10607937`) directly against that upstream
file:

| | pickup_ts | dropoff_ts | duration_seconds | quality_flag_bitset |
|---|---|---|---|---|
| Upstream canonical (`source_month=08/part-000.parquet`) | 2013-08-25 14:25:51 | 2013-08-25 14:25:51 | **4294815** | 0 |
| `test.parquet` (this repo, after `SELECT *` passthrough) | 2013-08-25 14:25:51 | 2013-08-25 14:25:51 | **4294815** | 0 |

Identical in both — **the bad `duration_seconds` value was already present in the
upstream canonical dataset**, before this repo's `build_sample.py`/`merge_split.py`
ever touched it. `build_sample.py`/`merge_split.py` are therefore cleared of
introducing this bug: they passed the value through unchanged.

## 3. Conclusion for section 5 (A vs B vs C)

**C — all three splits (train/val/test) go through the exact same preprocessing**
(same two scripts, same `SELECT *` passthrough, same `quality_flag_bitset=0` filter,
same temporal-order split logic). The 33 anomalies are not a split-specific
preprocessing gap — **they come from the upstream source data itself**, and
`quality_flag_bitset=0` (the upstream pipeline's own existing "clean" flag) does
**not** catch this particular duration-field corruption — all 33 anomalous rows
carry `quality_flag_bitset=0`, i.e. the upstream P2-01 pipeline itself considers
them "clean" despite the bad `duration_seconds` value.
