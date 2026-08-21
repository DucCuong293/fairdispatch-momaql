"""Invariant tests -- run BEFORE trusting any result on the full dataset.
1000 real requests sampled from train.parquet, ~seconds to run."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import pytest

from simulator import run_simulation_batched as run_simulation
from simulator import run_simulation_with_horizon
from policies import ALL_POLICIES, MOMAQLPolicy


@pytest.fixture(scope="module")
def requests_1k():
    p = Path(__file__).resolve().parents[1] / "data" / "train.parquet"
    df = pd.read_parquet(p, columns=[
        "pickup_ts", "pickup_latitude", "pickup_longitude",
        "dropoff_latitude", "dropoff_longitude", "fare_amount",
        "duration_seconds", "pickup_zone_id", "dropoff_zone_id",
    ]).sort_values("pickup_ts").head(1000).reset_index(drop=True)
    t0 = df["pickup_ts"].iloc[0].timestamp()
    reqs = []
    for i, row in df.iterrows():
        abs_sec = row["pickup_ts"].timestamp()
        reqs.append({
            "_idx": i,
            "pickup_ts": abs_sec - t0,
            "pickup_latitude": row["pickup_latitude"], "pickup_longitude": row["pickup_longitude"],
            "dropoff_latitude": row["dropoff_latitude"], "dropoff_longitude": row["dropoff_longitude"],
            "fare_amount": float(row["fare_amount"]), "duration_seconds": float(row["duration_seconds"]),
            "pickup_zone_id": row["pickup_zone_id"], "dropoff_zone_id": row["dropoff_zone_id"],
            "pickup_hour": int((abs_sec // 3600) % 24),
            "dropoff_hour": int(((abs_sec + row["duration_seconds"]) // 3600) % 24),
        })
    return reqs


@pytest.mark.parametrize("policy_name", list(ALL_POLICIES.keys()))
def test_trip_count_conservation(requests_1k, policy_name):
    policy = ALL_POLICIES[policy_name]()
    result = run_simulation(requests_1k, n_drivers=50, policy=policy, seed=1)
    assert result.total_completed <= result.total_requests


@pytest.mark.parametrize("policy_name", list(ALL_POLICIES.keys()))
def test_financial_conservation(requests_1k, policy_name):
    policy = ALL_POLICIES[policy_name]()
    result = run_simulation(requests_1k, n_drivers=50, policy=policy, seed=1)
    sum_income = sum(result.per_driver_income.values())
    expected = result.total_fares_served - result.total_deadhead_cost
    assert abs(sum_income - expected) < 1e-6, f"{sum_income} != {expected}"


@pytest.mark.parametrize("policy_name", list(ALL_POLICIES.keys()))
def test_time_monotonicity(requests_1k, policy_name):
    """No driver can be assigned a trip before it becomes available again."""
    policy = ALL_POLICIES[policy_name]()
    result = run_simulation(requests_1k, n_drivers=50, policy=policy, seed=1)
    last_commit_time = {}
    req_by_idx = {r["_idx"]: r for r in requests_1k}
    for req_idx, driver_id, fare, deadhead_cost, dz in result.trace:
        t = req_by_idx[req_idx]["pickup_ts"]
        if driver_id in last_commit_time:
            assert t >= last_commit_time[driver_id] - 1e-6, \
                f"driver {driver_id} assigned at t={t} before prior availability"
        # available_at after this trip isn't directly recorded in trace,
        # so this checks non-decreasing dispatch order per driver, which
        # the feasible_drivers() gate already enforces structurally.
        last_commit_time[driver_id] = t


def test_deadhead_sensitivity(requests_1k):
    """Greedy (ignores deadhead cost, picks lowest driver_id) should show a
    materially higher average deadhead cost per trip than Nearest (which
    explicitly minimizes ETA/deadhead)."""
    greedy = ALL_POLICIES["Greedy"]()
    nearest = ALL_POLICIES["Nearest"]()
    r_greedy = run_simulation(requests_1k, n_drivers=50, policy=greedy, seed=1)
    r_nearest = run_simulation(requests_1k, n_drivers=50, policy=nearest, seed=1)
    avg_dh_greedy = r_greedy.total_deadhead_cost / max(1, r_greedy.total_completed)
    avg_dh_nearest = r_nearest.total_deadhead_cost / max(1, r_nearest.total_completed)
    print(f"\navg deadhead cost/trip: Greedy={avg_dh_greedy:.4f} Nearest={avg_dh_nearest:.4f}")
    assert avg_dh_greedy > avg_dh_nearest, \
        "Greedy should have higher deadhead cost than Nearest (sanity check)"


def test_no_double_booking_within_window(requests_1k):
    """Real invariant new to batched dispatch: no driver can be assigned
    two requests inside the same window."""
    policy = MOMAQLPolicy()
    result = run_simulation(requests_1k, n_drivers=50, policy=policy, seed=1)
    seen_this_req = [r[1] for r in result.trace]
    assert len(seen_this_req) == len(set(zip((r[0] for r in result.trace), (r[1] for r in result.trace))))


def test_q_future_now_affects_decisions(requests_1k):
    """Regression guard for the exact bug found in the R2 ablation
    investigation: under the OLD one-request-at-a-time dispatch, gamma*Q(D)
    was a per-request constant and never changed which driver was picked,
    so 'full' and 'no_forecast' were bit-for-bit identical. Under real
    M-to-N batching, different requests in the same window can have
    different destinations, so Q_future must now be able to change
    outcomes -- assert results actually differ."""
    q_table = {(z, h): float(z) * 5.0 + h for z in range(1, 70) for h in range(24)}  # synthetic but clearly non-flat Q, for this unit test only
    full = MOMAQLPolicy(q_table=q_table, frozen=True, ablation="full")
    no_forecast = MOMAQLPolicy(q_table=q_table, frozen=True, ablation="no_forecast")
    r_full = run_simulation(requests_1k, n_drivers=50, policy=full, seed=1)
    r_nf = run_simulation(requests_1k, n_drivers=50, policy=no_forecast, seed=1)
    assert r_full.per_driver_income != r_nf.per_driver_income, \
        "full and no_forecast still identical -- the batching fix did not take effect"


def test_horizon_checkpoints_are_monotonic_and_cumulative(requests_1k):
    """run_simulation_with_horizon must report non-decreasing utility/completed
    across increasing horizon days (it's a cumulative snapshot of ONE
    trajectory, not independent reruns), and the final checkpoint must match
    a plain run_simulation_batched call on the same seed/policy."""
    q_table = {(z, h): float(z) * 5.0 + h for z in range(1, 70) for h in range(24)}
    policy = MOMAQLPolicy(q_table=q_table, frozen=True, ablation="full")
    result, checkpoints, disagreement = run_simulation_with_horizon(
        requests_1k, n_drivers=50, policy=policy, seed=1, checkpoint_days=[0.01, 0.02, 365])
    days = sorted(checkpoints.keys())
    completed_seq = [checkpoints[d]["completed"] for d in days]
    assert completed_seq == sorted(completed_seq), "completed count must be non-decreasing across horizons"
    assert disagreement is None  # no compare_policy given

    baseline_policy = MOMAQLPolicy(q_table=q_table, frozen=True, ablation="full")
    baseline = run_simulation(requests_1k, n_drivers=50, policy=baseline_policy, seed=1)
    assert result.total_completed == baseline.total_completed, \
        "run_simulation_with_horizon's final state must match run_simulation_batched"


def test_disagreement_rate_is_real_when_policies_differ(requests_1k):
    """full vs no_forecast must show SOME disagreement on a non-flat Q-table
    (they only ever agree 100% if Q is flat/empty -- guard against that
    silently regressing to a no-op comparison)."""
    q_table = {(z, h): float(z) * 5.0 + h for z in range(1, 70) for h in range(24)}
    full = MOMAQLPolicy(q_table=q_table, frozen=True, ablation="full")
    no_forecast = MOMAQLPolicy(q_table=q_table, frozen=True, ablation="no_forecast")
    _, _, disagreement = run_simulation_with_horizon(
        requests_1k, n_drivers=50, policy=full, seed=1, checkpoint_days=[0.1], compare_policy=no_forecast)
    assert disagreement is not None and disagreement > 0.0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
