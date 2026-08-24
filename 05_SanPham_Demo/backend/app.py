"""FairDispatch -- Ride-Hailing Dispatch Simulation & Decision-Support
Prototype backend. Live endpoints wrap the real engine (engine_adapter);
replay endpoints read real verified experiment artifacts (replay_adapter).
No endpoint here hard-codes a metric -- see PRODUCT_AUDIT.md."""
from __future__ import annotations

import time
import uuid
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import engine_adapter
import replay_adapter

app = FastAPI(title="FairDispatch -- Trợ lý ra quyết định điều phối")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SESSIONS: dict[str, engine_adapter.SimulationSession] = {}
HISTORY: list[dict] = []


class TimeFilter(BaseModel):
    mode: str = "all"  # "all" | "morning_peak" | "evening_peak" | "night" | "custom"
    start_hour: int | None = None
    end_hour: int | None = None


class DayFilter(BaseModel):
    mode: str = "all"  # "all" | "weekday" | "weekend" | "custom"
    days: list[int] | None = None  # 0=Mon .. 6=Sun, only used when mode="custom"


class CreateSimRequest(BaseModel):
    dataset: str = "val"
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
    run_id = "FD-" + time.strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6]
    session = _build_session_or_400(run_id, body)
    SESSIONS[run_id] = session
    HISTORY.insert(0, _record_from_session(session, "created"))
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
    return {"runs": HISTORY[:100]}


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
        # P0.2 defense-in-depth: a second overlapping step on the same
        # session (should not happen if the frontend guards correctly, but
        # the backend must not silently corrupt state if it does).
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
    """batch is optional: omit for the most recently fetched window (back-compat),
    or pass the batch a still-playing prefetched trip belongs to -- window_history
    keeps the last MAX_WINDOW_HISTORY windows so continuous playback can explain a
    trip from an earlier batch while newer batches have already been fetched."""
    s = _get_session(run_id)
    result = s.explain(req_idx, batch=batch)
    if result is None:
        detail = ("Yêu cầu này không nằm trong đợt vừa chạy gần nhất." if batch is None
                   else f"Yêu cầu này không nằm trong đợt #{batch} (có thể đã bị loại khỏi lịch sử gần đây).")
        raise HTTPException(status_code=404, detail=detail)
    return result


class CompareLiveRequest(BaseModel):
    dataset: str = "val"
    n_drivers: int = 200
    seed: int = 20260721
    lam: float = 0.5
    gamma: float = 0.9
    alpha: float = 0.1
    request_limit: int = 1500


@app.post("/compare/live")
def compare_live(body: CompareLiveRequest):
    """So sánh nhanh minh họa trên một lát dữ liệu trực tiếp nhỏ -- KHÔNG thay thế
    kết quả kiểm chứng 195.508 yêu cầu x 5 seed tại /replay/ablation."""
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
                "kiểm chứng 5 seed đầy đủ ở /replay/ablation.",
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


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
