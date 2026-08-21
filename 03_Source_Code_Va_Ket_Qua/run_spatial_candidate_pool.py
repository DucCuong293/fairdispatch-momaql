"""Real measurement: average candidate-pool size (drivers within the 600s
ETA feasibility radius) per request, split core vs periphery zones, on the
full 195,508-request validation split. Tests whether candidate-pool depth
(not just disagreement rate) differs by zone class -- a real, disclosed
measurement, not assumed in advance.
Writes reports/spatial_candidate_pool.csv.
"""
import csv
import gc
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulator import init_drivers, feasible_drivers
from policies import MOMAQLPolicy
from common_loader import load_requests_fast

N_DRIVERS = 200
SEEDS = [20260721, 20260722, 20260723]
WINDOW_SECONDS = 60.0

ZONE_LOOKUP = Path(
    "D:/ProjectVSF/fairdispatch_phase2_public_data/data_sources/official_tlc/"
    "metadata/taxi_zones/taxi_zone_lookup.csv"
)
PERIPHERY_KEYWORDS = ["Harlem", "Inwood", "Washington Heights", "Morningside",
                      "Manhattanville", "Hamilton Heights", "Marble Hill"]


def build_zone_classifier(zone_ids):
    id_to_name = {}
    with ZONE_LOOKUP.open("r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            id_to_name[int(row["LocationID"])] = row["Zone"]
    return {z: ("periphery" if any(k in id_to_name.get(z, "") for k in PERIPHERY_KEYWORDS) else "core")
            for z in zone_ids}


def main():
    reqs = load_requests_fast(Path(__file__).parent / "data" / "val.parquet")
    print(f"[load] {len(reqs):,} real requests", flush=True)
    zone_ids = sorted({r["pickup_zone_id"] for r in reqs})
    classifier = build_zone_classifier(zone_ids)

    rows = []
    for seed in SEEDS:
        t0 = time.perf_counter()
        drivers = init_drivers(N_DRIVERS, reqs, seed)
        pool_sizes = {"core": [], "periphery": []}

        i, n = 0, len(reqs)
        windows_done = 0
        while i < n:
            window_start = reqs[i]["pickup_ts"]
            window_end = window_start + WINDOW_SECONDS
            window_reqs = []
            while i < n and reqs[i]["pickup_ts"] < window_end:
                window_reqs.append(reqs[i])
                i += 1
            for req in window_reqs:
                cands = feasible_drivers(drivers, req, window_start)
                lbl = classifier.get(req["pickup_zone_id"])
                if lbl is not None:
                    pool_sizes[lbl].append(len(cands))
            del window_reqs
            # NOTE: this pass does not commit trips (read-only candidate-pool
            # measurement) -- drivers stay at their initial positions/free
            # the whole run. This intentionally measures the STATIC spatial
            # density of the fleet relative to demand, not a dynamic
            # dispatch trajectory (that's what run_complete_verifications.py
            # already covers for disagreement rate).
            windows_done += 1
            if windows_done % 500 == 0:
                gc.collect()
                print(f"  [seed={seed}] {i}/{n} requests processed ({time.perf_counter()-t0:.1f}s)", flush=True)

        for lbl in ["core", "periphery"]:
            sizes = pool_sizes[lbl]
            mean_pool = sum(sizes) / len(sizes) if sizes else 0.0
            zero_pool = sum(1 for s in sizes if s == 0) / len(sizes) if sizes else 0.0
            rows.append({
                "seed": seed, "zone_class": lbl, "n_requests": len(sizes),
                "mean_candidate_pool": mean_pool,
                "pct_zero_candidates": zero_pool * 100,
            })
        print(f"[seed={seed}] core mean_pool={rows[-2]['mean_candidate_pool']:.2f} "
              f"periphery mean_pool={rows[-1]['mean_candidate_pool']:.2f} "
              f"({time.perf_counter()-t0:.1f}s)", flush=True)
        del drivers, pool_sizes
        gc.collect()

    with (Path(__file__).parent / "reports" / "spatial_candidate_pool.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[done] wrote {len(rows)} rows to spatial_candidate_pool.csv", flush=True)


if __name__ == "__main__":
    main()
