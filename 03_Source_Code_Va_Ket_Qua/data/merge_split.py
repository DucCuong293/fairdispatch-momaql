"""Step 3 only, fresh process: merge the 8 real month-sample parquet files,
sort by real pickup_ts, split 70/15/15."""
import duckdb
import glob

con = duckdb.connect()
con.execute("SET memory_limit='1200MB'")
con.execute("SET threads=1")
con.execute("PRAGMA temp_directory='D:/ProjectVSF/fairdispatch_v3_clean/data/_tmp_spill'")

parts = sorted(glob.glob("D:/ProjectVSF/fairdispatch_v3_clean/data/_part_*.parquet"))
print("parts found:", parts, flush=True)
parts_sql = " UNION ALL ".join(f"SELECT * FROM read_parquet('{p}')" for p in parts)

n_sample = con.execute(f"SELECT COUNT(*) FROM ({parts_sql})").fetchone()[0]
print(f"real merged sample: {n_sample:,} rows", flush=True)

n_train = int(n_sample * 0.70)
n_val = int(n_sample * 0.15)

con.execute(f"""
    COPY (SELECT * FROM ({parts_sql}) ORDER BY pickup_ts LIMIT {n_train})
    TO 'D:/ProjectVSF/fairdispatch_v3_clean/data/train.parquet' (FORMAT PARQUET)
""")
print("train written", flush=True)
con.execute(f"""
    COPY (SELECT * FROM ({parts_sql}) ORDER BY pickup_ts LIMIT {n_val} OFFSET {n_train})
    TO 'D:/ProjectVSF/fairdispatch_v3_clean/data/val.parquet' (FORMAT PARQUET)
""")
print("val written", flush=True)
con.execute(f"""
    COPY (SELECT * FROM ({parts_sql}) ORDER BY pickup_ts OFFSET {n_train + n_val})
    TO 'D:/ProjectVSF/fairdispatch_v3_clean/data/test.parquet' (FORMAT PARQUET)
""")
print("test written", flush=True)

for name in ("train", "val", "test"):
    p = f"D:/ProjectVSF/fairdispatch_v3_clean/data/{name}.parquet"
    n = con.execute(f"SELECT COUNT(*) FROM read_parquet('{p}')").fetchone()[0]
    lo, hi = con.execute(f"SELECT MIN(pickup_ts), MAX(pickup_ts) FROM read_parquet('{p}')").fetchone()
    print(f"  {name}: {n:,} rows, {lo} .. {hi}", flush=True)

print("[done]", flush=True)
