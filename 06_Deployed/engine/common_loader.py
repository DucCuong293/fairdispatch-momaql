import pyarrow.parquet as pq
from pathlib import Path


def load_requests_fast(path: Path):
    table = pq.read_table(path, columns=[
        "pickup_ts", "pickup_latitude", "pickup_longitude",
        "dropoff_latitude", "dropoff_longitude", "fare_amount",
        "duration_seconds", "pickup_zone_id", "dropoff_zone_id",
    ])
    p_ts = table["pickup_ts"].to_numpy(zero_copy_only=False)
    abs_sec = p_ts.astype("datetime64[s]").astype("int64")  # real epoch seconds, wall-clock hour derived from this (not from the per-file-relative t0 offset below, which differs between train/val/test and would misalign hour buckets)
    t0 = abs_sec[0]
    ts_rel = (abs_sec - t0).astype(float)
    p_lat = table["pickup_latitude"].to_numpy()
    p_lon = table["pickup_longitude"].to_numpy()
    d_lat = table["dropoff_latitude"].to_numpy()
    d_lon = table["dropoff_longitude"].to_numpy()
    fares = table["fare_amount"].to_numpy()
    durs = table["duration_seconds"].to_numpy()
    p_hours = ((abs_sec // 3600) % 24).astype(int)
    d_hours = (((abs_sec + durs.astype("int64")) // 3600) % 24).astype(int)
    p_zids = table["pickup_zone_id"].to_pylist()
    z_ids = table["dropoff_zone_id"].to_pylist()
    n = len(p_lat)
    return [
        {"_idx": i, "pickup_ts": float(ts_rel[i]), "pickup_latitude": float(p_lat[i]),
         "pickup_longitude": float(p_lon[i]), "dropoff_latitude": float(d_lat[i]),
         "dropoff_longitude": float(d_lon[i]), "fare_amount": float(fares[i]),
         "duration_seconds": float(durs[i]), "pickup_zone_id": p_zids[i], "dropoff_zone_id": z_ids[i],
         "pickup_hour": int(p_hours[i]), "dropoff_hour": int(d_hours[i])}
        for i in range(n)
    ]


def gini(values):
    xs = sorted(v for v in values if v >= 0)
    n = len(xs)
    if n == 0:
        return 0.0
    s = sum(xs)
    if s == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * s) - (n + 1) / n


def variance(values):
    """Population variance of driver accumulated utility, Var(U_1..U_n) --
    the paper's own primary fairness metric (arXiv:2407.17839), reported
    alongside Gini rather than replacing it."""
    m = sum(values) / len(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def std(values):
    return variance(values) ** 0.5


def coefficient_of_variation(values):
    """sigma(U)/mean(U), the paper's own normalized-fairness metric.
    Undefined/unstable when mean(U) is at or near zero -- the paper's own
    Table 1 has this problem for Greedy (negative mean utility); callers
    should also report raw variance/std alongside this, never CV alone."""
    m = sum(values) / len(values)
    if abs(m) < 1e-9:
        return float("nan")
    return std(values) / m
