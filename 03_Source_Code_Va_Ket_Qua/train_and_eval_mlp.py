"""Real MLP Demand Predictor vs Tabular Q head-to-head comparison.

A 3-layer PyTorch MLP is trained on train.parquet to predict a real,
disclosed target: OD-pair+hour -> demand count (how many pickups
historically went from zone A to zone B during hour h) -- matching the
source paper's demand-forecasting mechanism, NOT a value estimator like
tabular Q.

Design decision (disclosed, not the only valid choice): to plug this into
MOMAQL's scoring slot, which expects a scalar "value of ending up in zone Z
at hour H" at the exact spot tabular Q(Z,H) occupies, we (a) sum the MLP's
predicted OD counts over all destination zones for a fixed (Z,H) to get a
per-zone-hour "expected outbound demand" scalar, then (b) min-max rescale
that scalar onto the trained tabular Q table's own [min,max] range so both
forecasters feed comparable magnitudes into the identical score formula.
This is one specific, disclosed rescaling -- not a claim that MLP output and
tabular Q measure the same physical quantity.

5-seed validation comparison: MOMAQL(Tabular Q) vs MOMAQL(MLP) vs
No-Forecast, on Utility / Gini / Variance / mean per-batch latency (ms).
Writes reports/mlp_vs_tabular_results.csv and _summary.csv.
"""
import gc
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import torch
import torch.nn as nn
import torch.optim as optim

from common_loader import load_requests_fast, gini, variance, std
from simulator import run_simulation_batched
from policies import MOMAQLPolicy

SEEDS = [20260721, 20260722, 20260723, 20260724, 20260725]
N_DRIVERS = 200
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class MLPDemandPredictor(nn.Module):
    def __init__(self, num_zones, emb_dim=16, hidden_dim=64):
        super().__init__()
        self.zone_emb = nn.Embedding(num_zones, emb_dim)
        self.fc = nn.Sequential(
            nn.Linear(emb_dim * 2 + 24, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, p_zone, d_zone, hour_onehot):
        pz = self.zone_emb(p_zone)
        dz = self.zone_emb(d_zone)
        x = torch.cat([pz, dz, hour_onehot], dim=-1)
        return self.fc(x).squeeze(-1)  # log1p(count) space


def build_od_hour_counts(path: Path) -> pd.DataFrame:
    """Real, disclosed target: count of pickups per (pickup_zone,
    dropoff_zone, hour-of-day) triple in train.parquet. Same wall-clock
    hour formula as common_loader.load_requests_fast (absolute epoch, not
    per-file-relative)."""
    table = pq.read_table(path, columns=["pickup_ts", "pickup_zone_id", "dropoff_zone_id"])
    abs_sec = table["pickup_ts"].to_numpy(zero_copy_only=False).astype("datetime64[s]").astype("int64")
    hours = ((abs_sec // 3600) % 24).astype(int)
    p_zones = np.array(table["pickup_zone_id"].to_pylist())
    d_zones = np.array(table["dropoff_zone_id"].to_pylist())
    del table, abs_sec
    gc.collect()
    df = pd.DataFrame({"p_zone": p_zones, "d_zone": d_zones, "hour": hours})
    counts = df.groupby(["p_zone", "d_zone", "hour"], as_index=False).size()
    counts = counts.rename(columns={"size": "count"})
    del df
    gc.collect()
    return counts


def train_mlp(counts: pd.DataFrame):
    all_zones = sorted(set(counts["p_zone"]) | set(counts["d_zone"]))
    zone_to_idx = {z: i for i, z in enumerate(all_zones)}

    p_idx = torch.tensor(counts["p_zone"].map(zone_to_idx).values, dtype=torch.long, device=DEVICE)
    d_idx = torch.tensor(counts["d_zone"].map(zone_to_idx).values, dtype=torch.long, device=DEVICE)
    hour_t = torch.zeros((len(counts), 24), dtype=torch.float32, device=DEVICE)
    hour_t.scatter_(1, torch.tensor(counts["hour"].values, dtype=torch.long, device=DEVICE).unsqueeze(1), 1.0)
    target_t = torch.tensor(np.log1p(counts["count"].values.astype(np.float32)), dtype=torch.float32, device=DEVICE)

    model = MLPDemandPredictor(num_zones=len(all_zones)).to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    criterion = nn.MSELoss()

    n = len(counts)
    print(f"[mlp] training on {n:,} real (OD-pair, hour) combinations, {len(all_zones)} zones, device={DEVICE}", flush=True)
    model.train()
    batch_size = 2048
    for epoch in range(30):
        perm = torch.randperm(n, device=DEVICE)
        total_loss = 0.0
        for b_start in range(0, n, batch_size):
            b_idx = perm[b_start:b_start + batch_size]
            optimizer.zero_grad()
            pred = model(p_idx[b_idx], d_idx[b_idx], hour_t[b_idx])
            loss = criterion(pred, target_t[b_idx])
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(b_idx)
        if epoch % 10 == 0 or epoch == 29:
            print(f"  [mlp] epoch={epoch:2d} mse_loss(log1p space)={total_loss / n:.4f}", flush=True)

    model.eval()
    return model, all_zones, zone_to_idx


def build_mlp_zone_hour_values(model, all_zones, zone_to_idx, tabular_q: dict) -> dict:
    """Sum predicted demand over all destination zones for each (zone, hour)
    -> 'expected outbound demand' scalar, then min-max rescale onto the
    trained tabular Q table's own value range so both forecasters occupy
    comparable magnitudes in the identical score formula."""
    n_zones = len(all_zones)
    zone_hour_demand = {}
    with torch.no_grad():
        for z in all_zones:
            z_t = torch.full((n_zones,), zone_to_idx[z], dtype=torch.long, device=DEVICE)
            all_dest_t = torch.tensor(range(n_zones), dtype=torch.long, device=DEVICE)
            for h in range(24):
                h_vec = torch.zeros((n_zones, 24), dtype=torch.float32, device=DEVICE)
                h_vec[:, h] = 1.0
                pred_log_counts = model(z_t, all_dest_t, h_vec)
                total_demand = torch.expm1(pred_log_counts).clamp(min=0).sum().item()
                zone_hour_demand[(z, h)] = total_demand

    raw_vals = np.array(list(zone_hour_demand.values()))
    q_vals = np.array(list(tabular_q.values()))
    lo, hi = raw_vals.min(), raw_vals.max()
    qlo, qhi = q_vals.min(), q_vals.max()
    print(f"[mlp] raw predicted zone-hour demand range=[{lo:.1f},{hi:.1f}] "
          f"-> rescaled onto tabular Q range=[{qlo:.2f},{qhi:.2f}]", flush=True)

    def rescale(x):
        if hi - lo < 1e-9:
            return (qlo + qhi) / 2
        return qlo + (x - lo) / (hi - lo) * (qhi - qlo)

    return {f"{z}:{h}": rescale(v) for (z, h), v in zone_hour_demand.items()}


def main():
    counts = build_od_hour_counts(Path(__file__).parent / "data" / "train.parquet")
    print(f"[load] {len(counts):,} real (OD-pair, hour) combinations from train.parquet", flush=True)

    with (Path(__file__).parent / "data" / "momaql_q_table_trained.json").open("r", encoding="utf-8") as f:
        tabular_q = json.load(f)

    model, all_zones, zone_to_idx = train_mlp(counts)
    del counts
    gc.collect()

    mlp_q = build_mlp_zone_hour_values(model, all_zones, zone_to_idx, tabular_q)
    del model
    gc.collect()

    reqs = load_requests_fast(Path(__file__).parent / "data" / "val.parquet")
    print(f"[load] {len(reqs):,} real validation requests", flush=True)

    rows = []
    configs = [
        ("MOMAQL (Tabular Q)", tabular_q),
        ("MOMAQL (MLP Demand Forecast)", mlp_q),
        ("No-Forecast", None),
    ]

    for name, q_tbl in configs:
        for seed in SEEDS:
            t0 = time.perf_counter()
            policy = MOMAQLPolicy(lam=0.5, q_table=(q_tbl if q_tbl else None), frozen=True)

            batch_times = []
            orig_select_batch = policy.select_batch

            def timed_select_batch(cands_map, now, _orig=orig_select_batch):
                bt0 = time.perf_counter()
                result = _orig(cands_map, now)
                batch_times.append(time.perf_counter() - bt0)
                return result

            policy.select_batch = timed_select_batch

            res = run_simulation_batched(reqs, n_drivers=N_DRIVERS, policy=policy, seed=seed)
            incomes = list(res.per_driver_income.values())
            el = time.perf_counter() - t0
            u = sum(incomes)
            g = gini(incomes)
            v = variance(incomes)
            sd = std(incomes)
            mean_batch_ms = (sum(batch_times) / len(batch_times) * 1000) if batch_times else float("nan")
            print(f"[{name:28s} seed={seed}] Utility=${u:,.1f} Gini={g:.4f} Var={v:,.1f} "
                  f"batch={mean_batch_ms:.2f}ms ({el:.1f}s total)", flush=True)
            rows.append({
                "model": name, "seed": seed, "utility": u, "gini": g,
                "variance": v, "std": sd, "completed_trips": res.total_completed,
                "mean_batch_latency_ms": round(mean_batch_ms, 3),
                "runtime_seconds": round(el, 2),
            })
            del res, incomes, batch_times
            gc.collect()

    df = pd.DataFrame(rows)
    out_csv = Path(__file__).parent / "reports" / "mlp_vs_tabular_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n=== SUMMARY ===", flush=True)
    summary = df.groupby("model").agg(
        utility_mean=("utility", "mean"), utility_std=("utility", "std"),
        gini_mean=("gini", "mean"), gini_std=("gini", "std"),
        variance_mean=("variance", "mean"),
        trips_mean=("completed_trips", "mean"),
        batch_latency_ms_mean=("mean_batch_latency_ms", "mean"),
    ).round(3)
    print(summary, flush=True)
    summary.to_csv(Path(__file__).parent / "reports" / "mlp_vs_tabular_summary.csv")
    print(f"[done] wrote {out_csv.name} and mlp_vs_tabular_summary.csv", flush=True)


if __name__ == "__main__":
    main()
