"""Fleet-scale sensitivity sweep + spatial/phase-separated policy disagreement.
Real TLC zone lookup used to classify zones (core Midtown/Downtown vs.
periphery Upper Manhattan/Inwood) -- not an arbitrary split, see
classify_zone() for the exact keyword rule, disclosed in the report.
Writes reports/fleet_scale_results.csv and reports/spatial_disagreement_by_zone.csv.
"""
import csv
import gc
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulator import run_simulation_batched, run_simulation_with_horizon
from policies import MOMAQLPolicy
from common_loader import load_requests_fast, gini, variance, std

N_DRIVERS_SWEEP = [100, 200, 400]
SEEDS = [20260721, 20260722, 20260723]
HORIZON_DAYS = [7, 37]  # just the 2 phase boundaries we need to diff

ZONE_LOOKUP = Path(
    "D:/ProjectVSF/fairdispatch_phase2_public_data/data_sources/official_tlc/"
    "metadata/taxi_zones/taxi_zone_lookup.csv"
)
PERIPHERY_KEYWORDS = ["Harlem", "Inwood", "Washington Heights", "Morningside",
                      "Manhattanville", "Hamilton Heights", "Marble Hill"]


def build_zone_classifier(zone_ids_in_data):
    """Real TLC zone names -> core (Midtown/Downtown/etc.) vs periphery
    (Upper Manhattan). Classification rule: any zone whose official TLC name
    contains one of PERIPHERY_KEYWORDS is periphery; every other zone present
    in our own data is core. Disclosed, not a hidden/arbitrary split."""
    import csv as _csv
    id_to_name = {}
    with ZONE_LOOKUP.open("r", encoding="utf-8-sig") as f:
        for row in _csv.DictReader(f):
            id_to_name[int(row["LocationID"])] = row["Zone"]
    classifier = {}
    for zid in zone_ids_in_data:
        name = id_to_name.get(zid, "")
        classifier[zid] = "periphery" if any(k in name for k in PERIPHERY_KEYWORDS) else "core"
    return classifier, id_to_name


def main():
    val_path = Path(__file__).parent / "data" / "val.parquet"
    print("[load] reading val.parquet...", flush=True)
    reqs = load_requests_fast(val_path)
    print(f"[load] {len(reqs):,} real requests", flush=True)

    q_path = Path(__file__).parent / "data" / "momaql_q_table_trained.json"
    with q_path.open("r", encoding="utf-8") as f:
        q_table = json.load(f)

    zone_ids = sorted({r["pickup_zone_id"] for r in reqs})
    zone_classifier, id_to_name = build_zone_classifier(zone_ids)
    n_core = sum(1 for v in zone_classifier.values() if v == "core")
    n_periph = sum(1 for v in zone_classifier.values() if v == "periphery")
    print(f"[zones] {len(zone_ids)} real zones in data: {n_core} core, {n_periph} periphery", flush=True)
    print(f"[zones] periphery zone names: "
          f"{[id_to_name.get(z) for z, c in zone_classifier.items() if c == 'periphery']}", flush=True)

    # ---------------- Part A: Fleet scale sweep ----------------
    fleet_rows = []
    for n_drivers in N_DRIVERS_SWEEP:
        for ablation in ["full", "no_forecast"]:
            for seed in SEEDS:
                t0 = time.perf_counter()
                policy = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation=ablation)
                res = run_simulation_batched(reqs, n_drivers=n_drivers, policy=policy, seed=seed)
                incomes = list(res.per_driver_income.values())
                fleet_rows.append({
                    "n_drivers": n_drivers, "ablation": ablation, "seed": seed,
                    "utility": sum(incomes), "gini": gini(incomes),
                    "variance": variance(incomes), "std": std(incomes),
                    "completed": res.total_completed,
                })
                print(f"[fleet N={n_drivers:3d} {ablation:12s} seed={seed}] "
                      f"utility={sum(incomes):,.0f} gini={gini(incomes):.4f} "
                      f"completed={res.total_completed} ({time.perf_counter()-t0:.1f}s)", flush=True)
                del policy, res, incomes
                gc.collect()

    with (Path(__file__).parent / "reports" / "fleet_scale_results.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fleet_rows[0].keys()))
        w.writeheader()
        w.writerows(fleet_rows)
    print(f"[done] wrote {len(fleet_rows)} rows to fleet_scale_results.csv", flush=True)

    # ---------------- Part B: spatial + phase disagreement (N=200, reused seeds) ----------------
    spatial_rows = []
    for seed in SEEDS:
        t0 = time.perf_counter()
        full = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation="full")
        no_forecast = MOMAQLPolicy(lam=0.5, q_table=q_table, frozen=True, ablation="no_forecast")
        _, checkpoints, overall_rate = run_simulation_with_horizon(
            reqs, n_drivers=200, policy=full, seed=seed,
            checkpoint_days=HORIZON_DAYS, compare_policy=no_forecast,
            zone_classifier=zone_classifier)

        d7 = checkpoints[7]["disagreement"]
        d37 = checkpoints[37]["disagreement"]

        def phase_rate(lbl):
            d1, c1 = d7[lbl]
            d2, c2 = d37[lbl]
            phase1 = (d1 / c1) if c1 else None
            phase2 = ((d2 - d1) / (c2 - c1)) if (c2 - c1) else None
            full_run = (d2 / c2) if c2 else None
            return phase1, phase2, full_run

        for lbl in ["total", "core", "periphery"]:
            p1, p2, full_r = phase_rate(lbl)
            spatial_rows.append({
                "seed": seed, "zone_class": lbl,
                "disagreement_day1_7": p1, "disagreement_day8_37": p2,
                "disagreement_full_37day": full_r,
            })
        print(f"[spatial seed={seed}] total(1-7)={phase_rate('total')[0]:.4f} "
              f"total(8-37)={phase_rate('total')[1]:.4f} "
              f"core(8-37)={phase_rate('core')[1]:.4f} "
              f"periphery(8-37)={phase_rate('periphery')[1]:.4f} "
              f"({time.perf_counter()-t0:.1f}s)", flush=True)
        del full, no_forecast, checkpoints
        gc.collect()

    with (Path(__file__).parent / "reports" / "spatial_disagreement_by_zone.csv").open(
            "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(spatial_rows[0].keys()))
        w.writeheader()
        w.writerows(spatial_rows)
    print(f"[done] wrote {len(spatial_rows)} rows to spatial_disagreement_by_zone.csv", flush=True)


if __name__ == "__main__":
    main()
