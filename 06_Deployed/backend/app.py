"""FairDispatch -- Ride-Hailing Dispatch Simulation & Decision-Support
Prototype backend (DEPLOYED bundle). Live endpoints wrap the real engine
(engine_adapter); replay endpoints read real verified Final Test artifacts
(replay_adapter). No endpoint here hard-codes a metric.

DEPLOY-SPECIFIC CHANGES vs 05_SanPham_Demo/backend/app.py:
  - default dataset is "test" (Final Test Evaluation View), not "val".
  - added GET /health for Render health checks (200 healthy / 503 degraded).
  - request_limit default unchanged (3000, live simulation is an
    interactive slice); dataset itself has 195,506 requests available, but
    a PUBLIC-DEMO safety cap bounds how much of it one Live Simulation run
    may touch (see PUBLIC_DEMO_LIMITS below) -- Verified Replay still reads
    the full 195,506-request Final Test artifacts, uncapped.
  - SESSIONS is bounded to MAX_SESSIONS (oldest evicted on overflow) so an
    unattended public demo cannot grow unbounded in-process RAM.
Must run with exactly one uvicorn worker -- SESSIONS/HISTORY are in-process
RAM state (see README.md)."""
from __future__ import annotations

import time
import uuid
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import engine_adapter
import replay_adapter
import paths

app = FastAPI(title="FairDispatch -- Trợ lý ra quyết định điều phối (Đã triển khai)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Insertion-ordered so the OLDEST run is the one evicted on overflow (FIFO,
# not LRU-by-access) -- see _remember_session() below.
SESSIONS: "OrderedDict[str, engine_adapter.SimulationSession]" = OrderedDict()
HISTORY: list[dict] = []
MAX_SESSIONS = 20
MAX_HISTORY = 100

TEST_EVAL_ROWS = 195506

# Public-demo safety caps: this bundle may be exposed on a public Render URL
# with no auth. These bound how much CPU/RAM one visitor's Live Simulation
# request can consume -- they do NOT limit what data exists (the Final Test
# Evaluation View still has all 195,506 requests; Verified Replay reads the
# full 5-seed Final Test artifacts uncapped).
LIVE_REQUEST_LIMIT_MAX = 10000
COMPARE_REQUEST_LIMIT_MAX = 3000
N_DRIVERS_MAX = 400


def _validate_public_demo_limits(request_limit: int, n_drivers: int, max_request_limit: int) -> None:
    errors = []
    if request_limit is None or request_limit <= 0:
        errors.append("request_limit phải > 0")
    elif request_limit > max_request_limit:
        errors.append(
            f"request_limit vượt giới hạn demo công khai (tối đa {max_request_limit:,}). "
            f"Đây chỉ là giới hạn cho Mô phỏng trực tiếp tương tác để giữ server nhẹ -- dữ liệu "
            f"Tập kiểm thử cuối đã chuẩn hóa vẫn có đủ 195.506 yêu cầu chuyến, và Kết quả kiểm chứng vẫn đọc "
            f"đầy đủ kết quả 5 seed trên toàn bộ 195.506 yêu cầu chuyến, không bị cắt."
        )
    if n_drivers is None or n_drivers <= 0:
        errors.append("n_drivers phải > 0")
    elif n_drivers > N_DRIVERS_MAX:
        errors.append(f"n_drivers vượt giới hạn demo công khai (tối đa {N_DRIVERS_MAX}).")
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))


def _remember_session(run_id: str, session: engine_adapter.SimulationSession) -> None:
    SESSIONS[run_id] = session
    if len(SESSIONS) > MAX_SESSIONS:
        oldest_run_id, _ = SESSIONS.popitem(last=False)
        for h in HISTORY:
            if h["run_id"] == oldest_run_id:
                h["status"] = "evicted"
                break


class TimeFilter(BaseModel):
    mode: str = "all"  # "all" | "morning_peak" | "evening_peak" | "night" | "custom"
    start_hour: int | None = None
    end_hour: int | None = None


class DayFilter(BaseModel):
    mode: str = "all"  # "all" | "weekday" | "weekend" | "custom"
    days: list[int] | None = None  # 0=Mon .. 6=Sun, only used when mode="custom"


class CreateSimRequest(BaseModel):
    dataset: str = "test"
    policy: str = "MOMAQL"
    n_drivers: int = 200
    seed: int = 20260721
    lam: float = 0.5
    gamma: float = 0.9
    alpha: float = 0.1
    forecast_on: bool = True
    request_limit: int = 3000
    time_filter: TimeFilter | None = None
    day_filter: DayFilter | None = None


def _build_session_or_400(run_id: str, body) -> engine_adapter.SimulationSession:
    tf = body.time_filter.model_dump() if getattr(body, "time_filter", None) else None
    df = body.day_filter.model_dump() if getattr(body, "day_filter", None) else None
    if tf and tf.get("start_hour") is not None and not (0 <= tf["start_hour"] <= 23):
        raise HTTPException(status_code=400, detail="time_filter.start_hour phai trong 0..23")
    if tf and tf.get("end_hour") is not None and not (0 <= tf["end_hour"] <= 23):
        raise HTTPException(status_code=400, detail="time_filter.end_hour phai trong 0..23")
    if df and df.get("days") and not all(0 <= d <= 6 for d in df["days"]):
        raise HTTPException(status_code=400, detail="day_filter.days phai trong 0..6 (0=Mon)")
    try:
        return engine_adapter.SimulationSession(
            run_id=run_id, dataset=body.dataset, n_drivers=body.n_drivers, seed=body.seed,
            policy_name=body.policy, lam=body.lam, gamma=body.gamma, alpha=body.alpha,
            forecast_on=body.forecast_on, request_limit=body.request_limit,
            time_filter=tf, day_filter=df,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Cấu hình không hợp lệ: {e}") from e


def _record_from_session(s: engine_adapter.SimulationSession, status: str) -> dict:
    return {
        "run_id": s.run_id, "policy": s.policy_name,
        "n_drivers_requested": s.n_drivers_requested, "n_drivers_actual": s.n_drivers_actual,
        "seed": s.seed, "lam": s.lam, "gamma": s.gamma, "forecast_on": s.forecast_on,
        "dataset": s.dataset, "request_limit": s.request_limit, "created_at": s.created_at,
        "t0_epoch_seconds": s.t0_epoch_seconds,
        "time_filter": s.time_filter, "day_filter": s.day_filter,
        "filtered_request_count": s.filtered_request_count, "available_request_count": s.available_request_count,
        "status": status, "utility": None, "gini": None,
    }


@app.post("/simulations")
def create_simulation(body: CreateSimRequest):
    _validate_public_demo_limits(body.request_limit, body.n_drivers, LIVE_REQUEST_LIMIT_MAX)
    run_id = "FD-" + time.strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6]
    session = _build_session_or_400(run_id, body)
    _remember_session(run_id, session)
    HISTORY.insert(0, _record_from_session(session, "created"))
    if len(HISTORY) > MAX_HISTORY:
        del HISTORY[MAX_HISTORY:]
    note = None
    if session.n_drivers_actual != session.n_drivers_requested:
        note = (f"Yêu cầu {session.n_drivers_requested} tài xế nhưng dataset/slice hiện tại chỉ đủ "
                f"request để khởi tạo {session.n_drivers_actual} tài xế thực tế (init_drivers() seed "
                f"từ request đầu tiên, giới hạn bởi request_limit).")
    return {
        "run_id": run_id, "total_requests": session.n, "config": HISTORY[0], "note": note,
        "constants": {
            "eta_threshold_seconds": engine_adapter.MAX_PICKUP_ETA_SECONDS,
            "batch_window_seconds": session.WINDOW_SECONDS,
            "deadhead_cost_per_second_usd": engine_adapter.COST_PER_SECOND_DEADHEAD_USD,
        },
        "dataset_info": {
            "name": "Final Test Evaluation View", "total_rows_available": TEST_EVAL_ROWS,
        },
    }


def _get_session(run_id: str) -> engine_adapter.SimulationSession:
    s = SESSIONS.get(run_id)
    if s is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} không tồn tại (có thể server đã restart).")
    return s


def _update_history(run_id: str, metrics: dict | None, done: bool):
    for h in HISTORY:
        if h["run_id"] == run_id:
            h["status"] = "done" if done else "running"
            if metrics:
                h["utility"] = metrics["utility"]
                h["gini"] = metrics["gini"]
            break


@app.get("/simulations")
def list_history():
    return {"runs": HISTORY[:MAX_HISTORY]}


@app.get("/simulations/{run_id}")
def get_simulation(run_id: str):
    s = _get_session(run_id)
    return {
        "run_id": s.run_id, "policy": s.policy_name,
        "n_drivers_requested": s.n_drivers_requested, "n_drivers_actual": s.n_drivers_actual,
        "seed": s.seed, "lam": s.lam, "gamma": s.gamma, "alpha": s.alpha, "forecast_on": s.forecast_on,
        "dataset": s.dataset, "total_requests": s.n, "requests_consumed": s.i,
        "batch_count": s.batch_count, "done": s.done,
    }


@app.post("/simulations/{run_id}/step")
def step_simulation(run_id: str):
    s = _get_session(run_id)
    try:
        result = s.step()
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    _update_history(run_id, result.get("metrics"), result.get("done", False))
    return result


@app.post("/simulations/{run_id}/reset")
def reset_simulation(run_id: str):
    s = _get_session(run_id)
    s.reset()
    _update_history(run_id, None, False)
    return {"run_id": run_id, "reset": True}


@app.get("/simulations/{run_id}/explain/{req_idx}")
def explain_assignment(run_id: str, req_idx: int, batch: int | None = None):
    s = _get_session(run_id)
    result = s.explain(req_idx, batch=batch)
    if result is None:
        detail = ("Yêu cầu này không nằm trong đợt vừa chạy gần nhất." if batch is None
                   else f"Yêu cầu này không nằm trong đợt #{batch} (có thể đã bị loại khỏi lịch sử gần đây).")
        raise HTTPException(status_code=404, detail=detail)
    return result


class CompareLiveRequest(BaseModel):
    dataset: str = "test"
    n_drivers: int = 200
    seed: int = 20260721
    lam: float = 0.5
    gamma: float = 0.9
    alpha: float = 0.1
    request_limit: int = 1500


@app.post("/compare/live")
def compare_live(body: CompareLiveRequest):
    """So sánh nhanh minh họa trên một lát dữ liệu trực tiếp nhỏ -- KHÔNG thay thế
    kết quả kiểm chứng 5 seed của Kiểm thử cuối tại /replay/ablation."""
    _validate_public_demo_limits(body.request_limit, body.n_drivers, COMPARE_REQUEST_LIMIT_MAX)
    out = {}
    for label, forecast_on in (("full", True), ("no_forecast", False)):
        run_id = f"cmp-{label}-{uuid.uuid4().hex[:6]}"
        params = SimpleNamespace(
            dataset=body.dataset, n_drivers=body.n_drivers, seed=body.seed, policy="MOMAQL",
            lam=body.lam, gamma=body.gamma, alpha=body.alpha, forecast_on=forecast_on,
            request_limit=body.request_limit,
        )
        sess = _build_session_or_400(run_id, params)
        while not sess.done:
            sess.step()
        incomes = [d.total_income for d in sess.drivers]
        out[label] = {
            "utility": sum(incomes), "gini": engine_adapter.gini(incomes),
            "served": sess.result.total_completed, "requests_used": sess.n,
            "n_drivers_actual": sess.n_drivers_actual,
        }
    return {
        "note": "So sánh nhanh trực tiếp trên lát dữ liệu nhỏ (minh họa) -- không thay thế kết quả "
                "kiểm chứng 5 seed Kiểm thử cuối đầy đủ ở /replay/ablation.",
        "results": out,
    }


@app.get("/replay/presets")
def replay_presets():
    return {"presets": list(replay_adapter.PRESETS.keys())}


@app.get("/replay/{preset}")
def replay_data(preset: str):
    fn = replay_adapter.PRESETS.get(preset)
    if fn is None:
        raise HTTPException(status_code=404, detail=f"Preset '{preset}' không tồn tại. Có: {list(replay_adapter.PRESETS)}")
    return fn()


@app.get("/provenance")
def provenance():
    return replay_adapter.provenance()


@app.get("/policies")
def list_policies():
    return {"policies": list(engine_adapter.ALL_POLICIES)}


@app.get("/health")
def health(response: Response):
    checks = {"engine": False, "q_table": False, "test_eval": False, "test_eval_rows": 0,
              "replay_ablation": False, "replay_long_horizon": False}
    try:
        checks["engine"] = "MOMAQL" in engine_adapter.ALL_POLICIES
    except Exception:
        pass
    try:
        checks["q_table"] = paths.Q_TABLE_PATH.exists() and len(engine_adapter.load_trained_q_table()) > 0
    except Exception:
        pass
    try:
        d = engine_adapter._load_columns()
        checks["test_eval"] = d["n"] == TEST_EVAL_ROWS
        checks["test_eval_rows"] = d["n"]
    except Exception:
        pass
    try:
        checks["replay_ablation"] = len(replay_adapter.ablation()["rows"]) > 0
    except Exception:
        pass
    try:
        checks["replay_long_horizon"] = len(replay_adapter.long_horizon()["rows"]) > 0
    except Exception:
        pass

    ok = all([checks["engine"], checks["q_table"], checks["test_eval"],
              checks["replay_ablation"], checks["replay_long_horizon"]])
    response.status_code = 200 if ok else 503
    return {"status": "ok" if ok else "degraded", **checks}


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
