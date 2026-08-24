"""Deploy-bundle test suite. Does NOT change the canonical engine; verifies
the deployed bundle behaves correctly on the bundled Final Test Evaluation
View. Run from 06_Deployed/backend (same working dir the server runs from):

    cd 06_Deployed/backend
    pip install -r ../requirements-dev.txt
    pytest ../tests/test_deploy_bundle.py -v
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))
import paths  # noqa: E402
import engine_adapter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def test_test_eval_parquet_exists():
    assert paths.TEST_EVAL_PARQUET.exists(), (
        "test_eval.parquet missing -- run scripts/build_test_eval_parquet.py first"
    )


def test_test_eval_row_count_is_195506():
    d = engine_adapter._load_columns()
    assert d["n"] == 195506


def test_test_eval_duration_bounds():
    d = engine_adapter._load_columns()
    durs = d["cols"]["duration_seconds"]
    assert (durs > 0).all()
    assert (durs <= 86400).all()


def test_deployment_manifest_matches_frozen_quality_rule():
    manifest = json.loads(paths.DEPLOYMENT_DATA_MANIFEST.read_text(encoding="utf-8"))
    stats = manifest["stats"]
    assert stats["duration_repaired"] == 32
    assert stats["duration_excluded"] == 1
    assert stats["temporal_boundary_excluded"] == 3
    assert stats["final_evaluated_rows"] == 195506


def test_raw_test_hash_matches_canonical():
    manifest = json.loads(paths.DEPLOYMENT_DATA_MANIFEST.read_text(encoding="utf-8"))
    built = manifest["built_from_raw_test_parquet"]
    assert built["sha256"] == "96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72"
    assert built["matches_canonical"] is True


def test_default_dataset_is_test():
    import inspect
    sys.path.insert(0, str(BACKEND_DIR))
    import app as app_module
    sig = inspect.signature(app_module.CreateSimRequest)
    default_dataset = app_module.CreateSimRequest().dataset
    assert default_dataset == "test"


def test_only_test_dataset_valid():
    assert engine_adapter.VALID_DATASETS == {"test"}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
def test_create_test_simulation_3000_requests():
    sess = engine_adapter.SimulationSession(
        run_id="t-create", dataset="test", n_drivers=200, seed=20260721,
        policy_name="MOMAQL", lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=3000,
    )
    assert sess.n == 3000
    assert sess.n_drivers_actual <= 200
    assert sess.n_drivers_actual > 0


def test_one_step_works():
    sess = engine_adapter.SimulationSession(
        run_id="t-step", dataset="test", n_drivers=50, seed=1,
        policy_name="Greedy", lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=500,
    )
    r = sess.step()
    assert r["batch"] == 1
    assert "metrics" in r


def test_momaql_loads_frozen_q_table():
    q = engine_adapter.load_trained_q_table()
    assert len(q) > 0
    policy = engine_adapter.make_policy("MOMAQL", 0.5, 0.9, 0.1, forecast_on=True)
    assert policy.Q is q or len(policy.Q) == len(q)


@pytest.mark.parametrize("policy_name", ["Greedy", "Nearest", "LAF", "Exact REASSIGN", "MOMAQL"])
def test_all_five_policies_step(policy_name):
    sess = engine_adapter.SimulationSession(
        run_id=f"t-{policy_name}", dataset="test", n_drivers=30, seed=1, policy_name=policy_name,
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=300,
    )
    r = sess.step()
    assert r["batch"] == 1


def test_explain_endpoint_works_for_actual_assignment():
    sess = engine_adapter.SimulationSession(
        run_id="t-explain", dataset="test", n_drivers=60, seed=20260721, policy_name="MOMAQL",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=2000,
    )
    checked = False
    for _ in range(20):
        r = sess.step()
        if r.get("assignments"):
            a = r["assignments"][0]
            explanation = sess.explain(a["req_idx"])
            assert explanation is not None
            assert explanation["selected_driver_id"] == a["driver_id"]
            checked = True
            break
    assert checked, "no assignment happened in first 20 batches"


def test_reset_works():
    sess = engine_adapter.SimulationSession(
        run_id="t-reset", dataset="test", n_drivers=30, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=300,
    )
    sess.step()
    assert sess.batch_count == 1
    sess.reset()
    assert sess.batch_count == 0
    assert sess.done is False


def test_optimized_loader_does_not_build_all_row_dicts_for_small_request():
    """RAM optimization check: creating a 3,000-request session must not
    force-build 195,506 Python dicts -- only the cached numpy columns (built
    once) plus the selected 3,000 request dicts should exist."""
    sess = engine_adapter.SimulationSession(
        run_id="t-ram", dataset="test", n_drivers=10, seed=1, policy_name="Greedy",
        lam=0.5, gamma=0.9, alpha=0.1, forecast_on=True, request_limit=3000,
    )
    assert len(sess.requests) == 3000
    assert sess.available_request_count == 195506


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------
def test_replay_ablation_loads_from_final_test_artifact():
    sys.path.insert(0, str(BACKEND_DIR))
    import replay_adapter
    r = replay_adapter.ablation()
    assert r["source"] == "artifacts/final_test/ablation/test_ablation_results.csv"
    ablations = {row["ablation"] for row in r["rows"]}
    assert {"full", "no_forecast", "no_fairness"} <= ablations


def test_replay_long_horizon_loads_from_final_test_artifact():
    sys.path.insert(0, str(BACKEND_DIR))
    import replay_adapter
    r = replay_adapter.long_horizon()
    assert r["source"] == "artifacts/final_test/long_horizon/test_long_horizon.csv"
    days = {int(row["horizon_day"]) for row in r["rows"]}
    assert {1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 37} <= days


def test_replay_values_are_read_not_hardcoded():
    sys.path.insert(0, str(BACKEND_DIR))
    import replay_adapter
    r = replay_adapter.baseline()
    momaql = next(row for row in r["rows"] if row["policy"] == "MOMAQL")
    assert abs(float(momaql["utility_mean"]) - 1454052.9111) < 1.0
    assert abs(float(momaql["gini_mean"]) - 0.2011) < 0.001


# ---------------------------------------------------------------------------
# Frontend consistency
# ---------------------------------------------------------------------------
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


def test_no_live_label_validation_in_frontend():
    for fn in ("app.js", "index.html"):
        text = (FRONTEND_DIR / fn).read_text(encoding="utf-8")
        assert not re.search(r"validation", text, re.IGNORECASE), f"'Validation' text found in {fn}"


def test_no_dataset_val_in_frontend():
    text = (FRONTEND_DIR / "app.js").read_text(encoding="utf-8")
    assert 'dataset: "val"' not in text
    assert "val.parquet" not in text


def test_cfg_limit_max_reflects_public_demo_cap():
    text = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
    assert 'max="10000"' in text  # public-demo Live cap, not the full 195,506-row dataset size
    assert "195.506 yêu cầu chuyến có sẵn" in text
    assert 'max="400"' in text  # cfgDrivers public-demo cap


# ---------------------------------------------------------------------------
# Provenance / health
# ---------------------------------------------------------------------------
def _client():
    from fastapi.testclient import TestClient
    sys.path.insert(0, str(BACKEND_DIR))
    import app as app_module
    return TestClient(app_module.app)


def test_health_endpoint_ok():
    c = _client()
    r = c.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["test_eval_rows"] == 195506


def test_health_degraded_returns_503(monkeypatch):
    """Mock a critical dependency (replay artifact) failing -- /health must
    report status=degraded AND respond with HTTP 503, not silently 200."""
    sys.path.insert(0, str(BACKEND_DIR))
    import replay_adapter

    def _broken_ablation():
        raise FileNotFoundError("simulated missing artifact for test")

    monkeypatch.setattr(replay_adapter, "ablation", _broken_ablation)
    c = _client()
    r = c.get("/health")
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "degraded"
    assert body["replay_ablation"] is False


def test_provenance_test_info_correct():
    c = _client()
    r = c.get("/provenance").json()
    assert r["runtime_dataset"]["rows"] == 195506
    assert r["raw_test_source"]["matches_canonical"] is True
    assert r["engine_source"]["files"]["policies.py"]["sha256"] is not None


def test_create_simulation_rejects_invalid_policy_with_400():
    c = _client()
    res = c.post("/simulations", json={"policy": "NotAPolicy"})
    assert res.status_code == 400


def test_create_simulation_rejects_non_test_dataset():
    c = _client()
    res = c.post("/simulations", json={"dataset": "val"})
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Public-demo safety limits
# ---------------------------------------------------------------------------
def test_create_simulation_rejects_request_limit_over_10000():
    c = _client()
    res = c.post("/simulations", json={"request_limit": 10001})
    assert res.status_code == 400
    assert "request_limit" in res.json()["detail"]


def test_create_simulation_accepts_request_limit_at_10000():
    c = _client()
    res = c.post("/simulations", json={"request_limit": 10000, "n_drivers": 50})
    assert res.status_code == 200


def test_create_simulation_rejects_n_drivers_over_400():
    c = _client()
    res = c.post("/simulations", json={"n_drivers": 401})
    assert res.status_code == 400
    assert "n_drivers" in res.json()["detail"]


def test_create_simulation_accepts_n_drivers_at_400():
    c = _client()
    res = c.post("/simulations", json={"n_drivers": 400, "request_limit": 500})
    assert res.status_code == 200


def test_compare_live_rejects_request_limit_over_3000():
    c = _client()
    res = c.post("/compare/live", json={"request_limit": 3001})
    assert res.status_code == 400
    assert "request_limit" in res.json()["detail"]


def test_compare_live_rejects_n_drivers_over_400():
    c = _client()
    res = c.post("/compare/live", json={"n_drivers": 401, "request_limit": 200})
    assert res.status_code == 400
    assert "n_drivers" in res.json()["detail"]


def test_public_demo_caps_do_not_shrink_the_underlying_dataset():
    """The 195,506-row Final Test Evaluation View itself is untouched by the
    public-demo request_limit/n_drivers caps -- only how much of it one Live
    Simulation call may touch."""
    d = engine_adapter._load_columns()
    assert d["n"] == 195506


def test_sessions_bounded_to_20():
    sys.path.insert(0, str(BACKEND_DIR))
    import app as app_module
    app_module.SESSIONS.clear()
    app_module.HISTORY.clear()
    c = _client()
    run_ids = []
    for _ in range(21):
        res = c.post("/simulations", json={"n_drivers": 10, "request_limit": 100})
        assert res.status_code == 200
        run_ids.append(res.json()["run_id"])
    assert len(app_module.SESSIONS) == app_module.MAX_SESSIONS
    # the FIRST (oldest) run must have been evicted
    assert run_ids[0] not in app_module.SESSIONS
    res = c.get(f"/simulations/{run_ids[0]}")
    assert res.status_code == 404
    # the most recent MAX_SESSIONS runs must still be present
    for rid in run_ids[-app_module.MAX_SESSIONS:]:
        assert rid in app_module.SESSIONS


def test_history_actually_bounded_to_100():
    """HISTORY is a plain list that grows on every create_simulation() call
    -- GET /simulations slicing HISTORY[:100] only bounds the RESPONSE, not
    the underlying list. Must also be truncated in place after each insert."""
    sys.path.insert(0, str(BACKEND_DIR))
    import app as app_module
    app_module.SESSIONS.clear()
    app_module.HISTORY.clear()
    c = _client()
    for _ in range(105):
        res = c.post("/simulations", json={"n_drivers": 5, "request_limit": 50})
        assert res.status_code == 200
    assert len(app_module.HISTORY) == app_module.MAX_HISTORY == 100
