"""Real test of hypothesis (1): "a full week (weekday vs weekend) may be
needed to expose the system to Manhattan's full demand-pattern variation
before a positioning strategy can show a consistent edge."

Reuses run_simulation_with_horizon (same infrastructure as the existing
2-phase multi-horizon table) with DAILY checkpoints (day 1..37) for Full
and No-Forecast MOMAQL, on ONE real trajectory per (config, seed), 5 seeds.
Computes the per-day INCREMENTAL utility gap (not cumulative) and checks it
against the real calendar weekday of each day (anchored to val.parquet's
real first timestamp, 2013-06-13 = Thursday) -- measured, not assumed.
Writes reports/hypothesis1_weekly_cycle.csv.
"""
import csv
import gc
import json
import sys
import time
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pyarrow.parquet as pq

from simulator import run_simulation_with_horizon
from policies import MOMAQLPolicy
from common_loader import load_requests_fast

N_DRIVERS = 200
SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
HORIZON_DAYS = list(range(1, 38))


def main():
    val_path = Path(__file__).parent / "data" / "val.parquet"
    anchor_date = pq.read_table(val_path, columns=["pickup_ts"])["pickup_ts"][0].as_py()
    print(f"[anchor] val.parquet's first request is real {anchor_date} ({anchor_date.strftime('%A')})", flush=True)

    reqs = load_requests_fast(val_path)
    print(f"[load] {len(reqs):,} real requests", flush=True)

    q_path = Path(__file__).parent / "data" / "momaql_q_table_trained.json"
    with q_path.open("r", encoding="utf-8") as f:
        q_table = json.load(f)

    per_day = {day: {"full": [], "no_forecast": []} for day in HORIZON_DAYS}

    for seed in SEEDS:
        t0 = time.perf_counter()
        for config in ["full", "no_forecast"]:
            policy = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation=config)
            res, checkpoints, _ = run_simulation_with_horizon(
                reqs, n_drivers=N_DRIVERS, policy=policy, seed=seed,
                checkpoint_days=HORIZON_DAYS)
            for day in HORIZON_DAYS:
                per_day[day][config].append(sum(checkpoints[day]["incomes"]))
            del policy, res, checkpoints
            gc.collect()
        print(f"[seed={seed}] done ({time.perf_counter()-t0:.1f}s)", flush=True)

    rows = []
    prev_full = {s: 0.0 for s in SEEDS}
    prev_nf = {s: 0.0 for s in SEEDS}
    for day in HORIZON_DAYS:
        weekday_name = (anchor_date + timedelta(days=day - 1)).strftime("%A")
        is_weekend = weekday_name in ("Saturday", "Sunday")
        incr_full = [per_day[day]["full"][i] - prev_full[SEEDS[i]] for i in range(len(SEEDS))]
        incr_nf = [per_day[day]["no_forecast"][i] - prev_nf[SEEDS[i]] for i in range(len(SEEDS))]
        for i, s in enumerate(SEEDS):
            prev_full[s] = per_day[day]["full"][i]
            prev_nf[s] = per_day[day]["no_forecast"][i]
        mean_incr_full = sum(incr_full) / len(incr_full)
        mean_incr_nf = sum(incr_nf) / len(incr_nf)
        rows.append({
            "day": day, "weekday": weekday_name, "is_weekend": is_weekend,
            "incremental_full_utility": round(mean_incr_full, 2),
            "incremental_no_forecast_utility": round(mean_incr_nf, 2),
            "incremental_gap": round(mean_incr_full - mean_incr_nf, 2),
        })

    out_csv = Path(__file__).parent / "reports" / "hypothesis1_weekly_cycle.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[done] wrote {len(rows)} rows to {out_csv.name}", flush=True)
    for r in rows:
        print(f"  day={r['day']:2d} {r['weekday']:9s} weekend={r['is_weekend']!s:5s} "
              f"gap={r['incremental_gap']:>10,.1f}", flush=True)

    weekday_gaps = [r["incremental_gap"] for r in rows if not r["is_weekend"]]
    weekend_gaps = [r["incremental_gap"] for r in rows if r["is_weekend"]]
    print(f"\n[summary] mean incremental gap: weekday={sum(weekday_gaps)/len(weekday_gaps):,.1f} "
          f"(n={len(weekday_gaps)}) vs weekend={sum(weekend_gaps)/len(weekend_gaps):,.1f} "
          f"(n={len(weekend_gaps)})", flush=True)


if __name__ == "__main__":
    main()
