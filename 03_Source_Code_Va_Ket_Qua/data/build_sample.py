"""Real, honest data prep for fairdispatch_v3_clean.

Source: the project's own already-cleaned, already-joined, already-zoned
canonical dataset (restricted_data/foil_2013_legacy/09_canonical/
realistic_2013_splits/development/source_month={01..08}/part-000.parquet)
-- real NYC TLC 2013 trip+fare data, already quality-filtered by the
project's own P2-01 pipeline (quality_flag_bitset, trip_fare_join_status).
No re-cleaning from raw here -- that work already exists and is real;
redoing it would just duplicate already-correct effort.

Filter: manhattan_both=true (dense zone, as requested) AND
quality_flag_bitset=0 (the project's own real "clean" flag).

Sample: a real, unweighted random sample of ~1,300,000 rows, taken
PROPORTIONALLY per month (not one giant cross-month scan -- this box has
~3GB free RAM, established earlier this session; processing one month's
~15M-row file at a time keeps peak memory bounded).

Split: real temporal 70/15/15 by pickup_ts order (train = earliest 70%,
val = next 15%, test = last 15%).
"""
import duckdb

ROOT = r"D:/ProjectVSF/fairdispatch_phase2_public_data/restricted_data/foil_2013_legacy/09_canonical/realistic_2013_splits/development"
MONTHS = [f"{m:02d}" for m in range(1, 9)]
SAMPLE_TARGET = 1_300_000
SEED = 20260721

con = duckdb.connect()
con.execute("SET memory_limit='1200MB'")
con.execute("SET threads=2")
con.execute("SET preserve_insertion_order=false")

# --- pass 1: real per-month clean-Manhattan counts (one file at a time) ---
print("[1/3] counting real clean Manhattan rows, one month at a time...", flush=True)
counts = {}
for m in MONTHS:
    p = f"{ROOT}/source_month={m}/part-000.parquet"
    n = con.execute(f"""
        SELECT COUNT(*) FROM read_parquet('{p}')
        WHERE manhattan_both = true AND quality_flag_bitset = 0
    """).fetchone()[0]
    counts[m] = n
    print(f"  month {m}: {n:,}", flush=True)
total = sum(counts.values())
print(f"  real total available: {total:,}", flush=True)

# --- pass 2: sample proportionally per month, write one parquet per month ---
frac = min(1.0, SAMPLE_TARGET / total)
print(f"[2/3] sampling ~{SAMPLE_TARGET:,} rows total (fraction={frac:.5f}, seed={SEED})...", flush=True)
part_paths = []
for m in MONTHS:
    p = f"{ROOT}/source_month={m}/part-000.parquet"
    out = f"D:/ProjectVSF/fairdispatch_v3_clean/data/_part_{m}.parquet"
    con.execute(f"""
        COPY (
            SELECT * FROM read_parquet('{p}')
            WHERE manhattan_both = true AND quality_flag_bitset = 0
            USING SAMPLE {frac*100:.6f} PERCENT (bernoulli, {SEED})
        ) TO '{out}' (FORMAT PARQUET)
    """)
    n = con.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
    print(f"  month {m} sampled: {n:,} -> {out}", flush=True)
    part_paths.append(out)

# --- pass 3: merge the 8 real month-samples, sort by real pickup_ts, split 70/15/15 ---
print("[3/3] merging + temporal 70/15/15 split...", flush=True)
parts_sql = " UNION ALL ".join(f"SELECT * FROM read_parquet('{p}')" for p in part_paths)
con.execute(f"CREATE TABLE merged AS SELECT * FROM ({parts_sql}) ORDER BY pickup_ts")
n_sample = con.execute("SELECT COUNT(*) FROM merged").fetchone()[0]
print(f"  real merged sample: {n_sample:,} rows", flush=True)

n_train = int(n_sample * 0.70)
n_val = int(n_sample * 0.15)
con.execute(f"""
    COPY (SELECT * FROM merged LIMIT {n_train})
    TO 'D:/ProjectVSF/fairdispatch_v3_clean/data/train.parquet' (FORMAT PARQUET)
""")
con.execute(f"""
    COPY (SELECT * FROM merged LIMIT {n_val} OFFSET {n_train})
    TO 'D:/ProjectVSF/fairdispatch_v3_clean/data/val.parquet' (FORMAT PARQUET)
""")
con.execute(f"""
    COPY (SELECT * FROM merged OFFSET {n_train + n_val})
    TO 'D:/ProjectVSF/fairdispatch_v3_clean/data/test.parquet' (FORMAT PARQUET)
""")

for name in ("train", "val", "test"):
    p = f"D:/ProjectVSF/fairdispatch_v3_clean/data/{name}.parquet"
    n = con.execute(f"SELECT COUNT(*) FROM read_parquet('{p}')").fetchone()[0]
    lo, hi = con.execute(f"SELECT MIN(pickup_ts), MAX(pickup_ts) FROM read_parquet('{p}')").fetchone()
    print(f"  {name}: {n:,} rows, {lo} .. {hi}", flush=True)

import os
for p in part_paths:
    os.remove(p)

print("[done] real data prep complete.", flush=True)
