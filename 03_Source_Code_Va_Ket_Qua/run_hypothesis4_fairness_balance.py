"""Real test of hypothesis (4): "as accumulated driver income grows over
weeks, the relative-fairness term's magnitude (scaled by income spread)
may shift relative to the lookahead term's, changing which one dominates
dispatch decisions."

Runs ONE real Full-MOMAQL (frozen, trained Q-table) trajectory over
val.parquet's full 37-day span per seed (3 seeds), and for every ACTUALLY
COMMITTED trip recomputes the two score components -- (1-lambda)*efficiency
and lambda*fairness -- using the exact formula in policies.py's
MOMAQLPolicy._score (duplicated here only for instrumentation; the real
formula still drives the actual dispatch decision via policy.select_batch).
Aggregates mean |term| per real calendar day and the fairness term's SHARE
of total |score| magnitude, to see whether the balance actually shifts
over the horizon -- measured, not assumed.
Writes reports/hypothesis4_fairness_balance.csv.
"""
import csv
import gc
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulator import init_drivers, feasible_drivers, commit_trip, SimResult
from policies import MOMAQLPolicy
from common_loader import load_requests_fast

N_DRIVERS = 200
SEEDS = [20260721, 20260722, 20260723]
WINDOW_SECONDS = 60.0
MAX_DAY = 37


def main():
    reqs = load_requests_fast(Path(__file__).parent / "data" / "val.parquet")
    print(f"[load] {len(reqs):,} real validation requests", flush=True)

    with (Path(__file__).parent / "data" / "momaql_q_table_trained.json").open("r", encoding="utf-8") as f:
        q_table = json.load(f)

    day_stats = {d: {"eff": [], "fair": []} for d in range(1, MAX_DAY + 1)}

    for seed in SEEDS:
        t_seed = time.perf_counter()
        policy = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation="full")
        drivers = init_drivers(N_DRIVERS, reqs, seed)
        result = SimResult(per_driver_income={d.driver_id: 0.0 for d in drivers}, total_requests=len(reqs))
        policy.on_start(drivers)

        t0 = reqs[0]["pickup_ts"]
        max_seconds = MAX_DAY * 86400.0
        i, n = 0, len(reqs)
        while i < n:
            window_start = reqs[i]["pickup_ts"]
            if window_start - t0 > max_seconds:
                break
            window_end = window_start + WINDOW_SECONDS
            window_reqs = []
            while i < n and reqs[i]["pickup_ts"] < window_end:
                window_reqs.append(reqs[i])
                i += 1

            cands_map = {}
            for req in window_reqs:
                cands = feasible_drivers(drivers, req, window_start)
                if cands:
                    cands_map[req["_idx"]] = (req, cands)
            del window_reqs
            if not cands_map:
                continue

            mean_income = sum(d.total_income for d in drivers) / len(drivers)
            assignments = policy.select_batch(cands_map, window_start)
            day = min(int((window_start - t0) // 86400.0) + 1, MAX_DAY)
            used = set()
            for req_idx, chosen in assignments.items():
                if chosen is None:
                    continue
                d, dist, eta = chosen
                if d.driver_id in used:
                    continue
                used.add(d.driver_id)
                req, _ = cands_map[req_idx]

                # Mirrors policies.py MOMAQLPolicy._score's two-term split
                # (instrumentation only -- select_batch already made the
                # real decision above using the identical formula).
                D_zone = req.get("dropoff_zone_id")
                D_hour = req.get("dropoff_hour")
                q_future = policy.Q.get((D_zone, D_hour), 0.0)
                deadhead_cost = eta * 0.0025
                efficiency = req["fare_amount"] - deadhead_cost + policy.gamma * q_future
                rel_fairness = (mean_income - d.total_income) / max(mean_income, 1.0)
                fairness = rel_fairness * req["fare_amount"]
                eff_term = (1 - policy.lam) * efficiency
                fair_term = policy.lam * fairness
                day_stats[day]["eff"].append(abs(eff_term))
                day_stats[day]["fair"].append(abs(fair_term))

                commit_trip(d, req, dist, eta, window_start, result, record_trace=False)
                policy.on_committed(d, req, dist, eta, window_start)

        print(f"[seed={seed}] completed={result.total_completed}/{result.total_requests} "
              f"({time.perf_counter()-t_seed:.1f}s)", flush=True)
        del policy, drivers, result
        gc.collect()

    rows = []
    for day in range(1, MAX_DAY + 1):
        eff_vals = day_stats[day]["eff"]
        fair_vals = day_stats[day]["fair"]
        if not eff_vals:
            continue
        mean_eff = sum(eff_vals) / len(eff_vals)
        mean_fair = sum(fair_vals) / len(fair_vals)
        fairness_share = mean_fair / (mean_eff + mean_fair) if (mean_eff + mean_fair) > 0 else float("nan")
        rows.append({
            "day": day, "n_commits": len(eff_vals),
            "mean_abs_efficiency_term": round(mean_eff, 4),
            "mean_abs_fairness_term": round(mean_fair, 4),
            "fairness_share": round(fairness_share, 4),
        })

    out_csv = Path(__file__).parent / "reports" / "hypothesis4_fairness_balance.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[done] wrote {len(rows)} rows to {out_csv.name}", flush=True)
    for r in rows:
        if r["day"] in (1, 7, 14, 21, 28, 37):
            print(f"  day={r['day']:2d} eff={r['mean_abs_efficiency_term']:.3f} "
                  f"fair={r['mean_abs_fairness_term']:.3f} fair_share={r['fairness_share']:.3f}", flush=True)


if __name__ == "__main__":
    main()
