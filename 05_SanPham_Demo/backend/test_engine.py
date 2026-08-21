"""Backend smoke tests. Priority #1 (per PRODUCT_FIX_PLAN.md P0.1): prove
that assignment explanation marks the driver the REAL Hungarian solve
picked -- not just the locally-highest-scoring candidate, which can
legitimately differ because Hungarian optimizes the whole batch jointly.

Run: `pytest test_engine.py -v` from this directory (needs the same env as
the running server: fastapi, pyarrow, numpy, scipy -- see requirements.txt).
Some tests need the real val.parquet from the sibling dev repo; they are
skipped automatically (not failed) if that file is not present, so this
suite still runs in an environment that only has the submission bundle.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
import engine_adapter  # noqa: E402

sys.path.insert(0, str(paths.SRC_DIR))
from simulator import Driver  # noqa: E402
from policies import hungarian_batch_assign  # noqa: E402

HAS_VAL_DATA = (paths.PARQUET_DATA_DIR / "val.parquet").exists()
needs_val_data = pytest.mark.skipif(not HAS_VAL_DATA, reason="val.parquet not found next to this bundle (see README)")


# ---------------------------------------------------------------------------
# P0.1: prove the REAL hungarian_batch_assign (no reimplementation) can send
# a request to a driver who is NOT that request's local top scorer.
# ---------------------------------------------------------------------------
def test_hungarian_can_diverge_from_local_top_score():
    d1 = Driver(driver_id=1, lat=0, lon=0, available_at=0)
    d2 = Driver(driver_id=2, lat=0, lon=0, available_at=0)
    req_a = {"_idx": 0}
    req_b = {"_idx": 1}
    # Crafted so the greedy/local-best choice for A (d1, score 10) is worse
    # for the BATCH as a whole than giving d1 to B and d2 to A:
    #   local-best assignment:  A=d1(10) + B=d2(1) = 11
    #   Hungarian global optimum: A=d2(9) + B=d1(8) = 17
    scores = {(0, 1): 10.0, (0, 2): 9.0, (1, 1): 8.0, (1, 2): 1.0}

    def score_fn(d, req, dist, eta):
        return scores[(req["_idx"], d.driver_id)]

    cands_map = {
        0: (req_a, [(d1, 0.0, 0.0), (d2, 0.0, 0.0)]),
        1: (req_b, [(d1, 0.0, 0.0), (d2, 0.0, 0.0)]),
    }
    result = hungarian_batch_assign(cands_map, score_fn)
    selected_a = result[0][0].driver_id
    selected_b = result[1][0].driver_id

    # The real Hungarian solve must pick the GLOBAL optimum (d2 for A, d1
    # for B), i.e. request A's actual winner is NOT its local top scorer.
    assert selected_a == 2, "Hungarian should give A to driver 2 (global optimum), not driver 1 (local top score)"
    assert selected_b == 1
    local_top_for_a = max((1, 2), key=lambda did: scores[(0, did)])
    assert local_top_for_a == 1
    assert selected_a != local_top_for_a, "this test is only meaningful if local-best != global-selected"


@needs_val_data
def test_explain_marks_actual_hungarian_winner_not_local_rank_1():
    """Integration-level check of the P0.1 fix: run a real small MOMAQL
    session, and for every assigned request in the batch, confirm
    explain()'s selected_driver_id matches the driver actually committed
    by step() -- regardless of that candidate's local score rank."""
    sess = engine_adapter.SimulationSession(
        run_id="test-explain", dataset="val", n_drivers=60, seed=20260721,
        policy_name="MOMAQL", lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=2000,
    )
    checked_any = False
    for _ in range(20):
        r = sess.step()
        if r.get("done") and "assignments" not in r:
            break
        for a in r["assignments"]:
            checked_any = True
            explanation = sess.explain(a["req_idx"])
            assert explanation is not None
            # This is the actual, real commit made by step() -- ground truth.
            assert explanation["selected_driver_id"] == a["driver_id"]
            winners = [c for c in explanation["candidates"] if c["is_selected"]]
            assert len(winners) == 1
            assert winners[0]["driver_id"] == a["driver_id"]
        if checked_any:
            break
    assert checked_any, "no assignment happened in the first 20 batches -- test setup problem"


@needs_val_data
def test_step_reset_lifecycle():
    sess = engine_adapter.SimulationSession(
        run_id="test-lifecycle", dataset="val", n_drivers=30, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=300,
    )
    r1 = sess.step()
    assert r1["batch"] == 1
    assert sess.batch_count == 1
    sess.reset()
    assert sess.batch_count == 0
    assert sess.done is False
    r2 = sess.step()
    assert r2["batch"] == 1  # after reset, numbering restarts


@needs_val_data
@pytest.mark.parametrize("policy_name", ["Greedy", "Nearest", "LAF", "Exact REASSIGN", "MOMAQL"])
def test_all_five_policies_step_and_explain(policy_name):
    sess = engine_adapter.SimulationSession(
        run_id=f"test-{policy_name}", dataset="val", n_drivers=30, seed=1, policy_name=policy_name,
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=300,
    )
    r = sess.step()
    if r.get("assignments"):
        req_idx = r["assignments"][0]["req_idx"]
        explanation = sess.explain(req_idx)
        assert explanation is not None
        assert explanation["selected_driver_id"] == r["assignments"][0]["driver_id"]


@needs_val_data
def test_feasible_drivers_unique_is_deduplicated_not_sum_of_edges():
    # Operator "Demand/Supply" must use a real unique-driver count -- NOT the
    # sum of per-request candidate edges (one driver can be a feasible
    # candidate for multiple requests in the same window).
    sess = engine_adapter.SimulationSession(
        run_id="test-supply", dataset="val", n_drivers=30, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=300,
    )
    r = sess.step()
    assert "feasible_drivers_unique" in r
    assert 0 <= r["feasible_drivers_unique"] <= sess.n_drivers_actual
    # sum of edges across requests is always >= unique count (never <)
    sum_edges = sum(len(cands) for _req, cands in sess.window_history[r["batch"]]["cands_map"].values())
    assert r["feasible_drivers_unique"] <= sum_edges


@needs_val_data
def test_explain_still_works_for_older_batch_after_newer_steps():
    # Continuous playback prefetches ahead of what's visually playing, so
    # "Why this driver?" for an OLDER batch must still work after newer
    # batches have already been fetched -- not just the very latest one.
    sess = engine_adapter.SimulationSession(
        run_id="test-window-history", dataset="val", n_drivers=30, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=600,
    )
    r1 = sess.step()
    assert r1["batch"] == 1
    r2 = sess.step()
    r3 = sess.step()
    assert r3["batch"] == 3
    if r1.get("assignments"):
        a = r1["assignments"][0]
        explanation = sess.explain(a["req_idx"], batch=1)
        assert explanation is not None
        assert explanation["selected_driver_id"] == a["driver_id"]
    # explicit wrong batch for a req_idx that belongs to an earlier window -> None
    if r1.get("assignments") and r3.get("assignments"):
        wrong = sess.explain(r1["assignments"][0]["req_idx"], batch=r3["batch"])
        assert wrong is None


@needs_val_data
def test_income_histogram_shape():
    sess = engine_adapter.SimulationSession(
        run_id="test-hist", dataset="val", n_drivers=30, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=500,
    )
    r = sess.step()
    hist = r["income_histogram"]
    assert len(hist["bins"]) == len(hist["counts"]) + 1
    assert sum(hist["counts"]) == len(sess.drivers)


@needs_val_data
def test_n_drivers_actual_capped_when_requests_scarce():
    """init_drivers() caps to min(n_drivers, len(requests)) -- the session
    must expose the ACTUAL count, not silently claim the requested one."""
    sess = engine_adapter.SimulationSession(
        run_id="test-cap", dataset="val", n_drivers=500, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=10,
    )
    assert sess.n_drivers_requested == 500
    assert sess.n_drivers_actual == 10
    assert len(sess.drivers) == 10


def test_config_validation_rejects_bad_lambda():
    with pytest.raises(ValueError):
        engine_adapter.SimulationSession(
            run_id="test-bad", dataset="val", n_drivers=10, seed=1, policy_name="Greedy",
            lam=5.0, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=10,
        )


def test_config_validation_rejects_unknown_policy():
    with pytest.raises(ValueError):
        engine_adapter.SimulationSession(
            run_id="test-bad2", dataset="val", n_drivers=10, seed=1, policy_name="NotAPolicy",
            lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=10,
        )


def test_config_validation_rejects_zero_drivers():
    with pytest.raises(ValueError):
        engine_adapter.SimulationSession(
            run_id="test-bad3", dataset="val", n_drivers=0, seed=1, policy_name="Greedy",
            lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=10,
        )


def test_missing_dataset_raises_filenotfound():
    with pytest.raises((ValueError, FileNotFoundError)):
        engine_adapter.SimulationSession(
            run_id="test-bad4", dataset="not_a_real_dataset", n_drivers=10, seed=1, policy_name="Greedy",
            lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=10,
        )


def test_lorenz_points_are_generic_math_not_fake_data():
    pts = engine_adapter.lorenz_points([10.0, 20.0, 30.0, 40.0])
    assert pts[0] == {"x": 0.0, "y": 0.0}
    assert pts[-1]["x"] == 1.0
    assert abs(pts[-1]["y"] - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Time-of-day / day-of-week scenario filters (pure functions, no val.parquet needed)
# ---------------------------------------------------------------------------
def test_time_filter_all_day_and_named_presets():
    assert engine_adapter._hour_in_time_filter(3, None) is True
    assert engine_adapter._hour_in_time_filter(3, {"mode": "all"}) is True
    morning = {"mode": "morning_peak", "start_hour": 6, "end_hour": 9}
    assert engine_adapter._hour_in_time_filter(6, morning) is True
    assert engine_adapter._hour_in_time_filter(8, morning) is True
    assert engine_adapter._hour_in_time_filter(9, morning) is False  # end exclusive
    assert engine_adapter._hour_in_time_filter(5, morning) is False
    evening = {"mode": "evening_peak", "start_hour": 17, "end_hour": 19}
    assert engine_adapter._hour_in_time_filter(18, evening) is True
    assert engine_adapter._hour_in_time_filter(20, evening) is False


def test_time_filter_overnight_wrap():
    night = {"mode": "night", "start_hour": 22, "end_hour": 5}
    assert engine_adapter._hour_in_time_filter(23, night) is True
    assert engine_adapter._hour_in_time_filter(0, night) is True
    assert engine_adapter._hour_in_time_filter(4, night) is True
    assert engine_adapter._hour_in_time_filter(5, night) is False  # end exclusive
    assert engine_adapter._hour_in_time_filter(12, night) is False


def test_day_filter_weekday_weekend_custom():
    assert engine_adapter._weekday_in_day_filter(0, None) is True
    for wd in range(5):  # Mon..Fri
        assert engine_adapter._weekday_in_day_filter(wd, {"mode": "weekday"}) is True
    for wd in (5, 6):  # Sat, Sun
        assert engine_adapter._weekday_in_day_filter(wd, {"mode": "weekday"}) is False
        assert engine_adapter._weekday_in_day_filter(wd, {"mode": "weekend"}) is True
    assert engine_adapter._weekday_in_day_filter(2, {"mode": "custom", "days": [0, 2, 4]}) is True
    assert engine_adapter._weekday_in_day_filter(3, {"mode": "custom", "days": [0, 2, 4]}) is False


@needs_val_data
def test_scenario_filter_applied_before_request_limit():
    # PHASE 3 requirement: filter THEN limit, never limit-then-filter (which
    # could silently starve a narrow scenario of requests that exist later
    # in the dataset but got cut off by an unrelated slice-first limit).
    sess = engine_adapter.SimulationSession(
        run_id="test-filter-order", dataset="val", n_drivers=10, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=50,
        day_filter={"mode": "weekday"},
    )
    assert sess.available_request_count > sess.filtered_request_count >= sess.n
    assert all(r["pickup_weekday"] <= 4 for r in sess.requests)


@needs_val_data
def test_empty_scenario_raises_clear_error_not_crash():
    with pytest.raises(ValueError, match="No requests match"):
        engine_adapter.SimulationSession(
            run_id="test-empty-scenario", dataset="val", n_drivers=10, seed=1, policy_name="Greedy",
            lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=50,
            time_filter={"mode": "custom", "start_hour": 3, "end_hour": 3},  # zero-width window
        )


# ---------------------------------------------------------------------------
# HTTP-level tests via FastAPI TestClient (replay/provenance don't need val.parquet)
# ---------------------------------------------------------------------------
def _client():
    from fastapi.testclient import TestClient
    import app as app_module
    return TestClient(app_module.app)


def test_replay_presets_return_real_rows():
    c = _client()
    presets = c.get("/replay/presets").json()["presets"]
    assert "ablation" in presets
    r = c.get("/replay/ablation").json()
    assert r["source"] == "reports/r2_ablation_results.csv"
    ablations = {row["ablation"] for row in r["rows"]}
    assert {"full", "no_forecast", "no_fairness"} <= ablations


def test_provenance_separates_engine_snapshot_from_dev_repo():
    c = _client()
    r = c.get("/provenance").json()
    assert "bundle_engine_source" in r
    assert "dev_repo" in r
    assert "policies.py" in r["bundle_engine_source"]["files"]
    assert r["bundle_engine_source"]["files"]["policies.py"]["sha256"] is not None
    # the checksum key must match the real dataset_checksums.json key exactly
    assert "val.parquet" in r["dataset_checksums"]


def test_create_simulation_rejects_invalid_policy_with_400():
    c = _client()
    res = c.post("/simulations", json={"policy": "NotAPolicy"})
    assert res.status_code == 400


@needs_val_data
def test_compare_live_returns_200_not_500():
    # Regression for the class-body `forecast_on = forecast_on` NameError
    # (class body name resolution skips the enclosing function scope) that
    # made /compare/live crash with HTTP 500 -- see PRODUCT_FIX_PLAN.md.
    c = _client()
    res = c.post("/compare/live", json={
        "dataset": "val", "n_drivers": 10, "seed": 20260721,
        "lam": 0.5, "gamma": 0.9, "alpha": 0.1, "request_limit": 50,
    })
    assert res.status_code == 200
    body = res.json()
    for label in ("full", "no_forecast"):
        r = body["results"][label]
        assert r["utility"] == r["utility"]  # not NaN
        assert 0.0 <= r["gini"] <= 1.0
        assert r["served"] >= 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
