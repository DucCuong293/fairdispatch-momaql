# FairDispatch -- Deployed Bundle (06_Deployed)

Self-contained deploy package for the FairDispatch decision-support prototype.
Built from `05_SanPham_Demo` (unchanged, kept as the local backup) + real
engine/artifacts from `03_Source_Code_Va_Ket_Qua`. Runs with **no dependency**
on any path outside this folder -- see `DEPLOYMENT_SOURCE_AUDIT.md` and
`DEPLOYMENT_REPORT.md` for exactly what changed and why.

## What changed vs `05_SanPham_Demo`

- **Live Simulation now runs on the Final Test Evaluation View**
  (`data/test_eval.parquet`, 195,506 rows), not `val.parquet`. The raw
  `test.parquet` (195,510 rows) is never used directly -- the frozen quality
  transform (temporal-boundary exclusion + duration repair) already used by
  every Final Test script is applied once, at build time
  (`scripts/build_test_eval_parquet.py`), never at request time.
- **Replay (Compare Policies / Long-Horizon) now reads Final Test artifacts**
  (`artifacts/final_test/`), not Validation `reports/*.csv`.
- **Loader is columnar/vectorized**, not "195,506 Python dicts up front then
  slice 3,000". Scenario filters (time-of-day, day-of-week) are vectorized
  numpy masks; per-row dicts are built only for the rows actually used.
- **No sibling-repo dependency.** Engine (`policies.py`, `simulator.py`,
  `common_loader.py`), Q-table, and Final Test artifacts are all bundled
  inside `06_Deployed/`.
- Added `GET /health` (200 when healthy, **503 when degraded**) and a
  self-contained `/provenance` (no dev-repo git lookup).
- **Public-demo safety limits** on the interactive Live endpoints (see
  below) and a bounded in-process session cache (max 20 concurrent runs,
  oldest evicted first) -- this bundle may sit behind a public, unauthenticated
  Render URL.

## Two modes

Note: the UI itself is fully Vietnamese (tabs: "Mô phỏng trực tiếp" /
"So sánh chiến lược" / "Đánh giá dài hạn" / "Lịch sử lần chạy"; badges:
"ENGINE TRỰC TIẾP" / "KẾT QUẢ KIỂM CHỨNG"). This section keeps the English
mode names below for cross-referencing the technical docs (`DEPLOYMENT_REPORT.md`
etc.), not as a claim about what's rendered on screen.

### Live Simulation ("Mô phỏng trực tiếp")
- Dataset: **Final Test Evaluation View** (195,506 requests available).
- Default: 3,000 requests, interactive.
- Choose Policy, Operating Objective preset, Fleet size, Time-of-day /
  Day-of-week filter.
- Run / Pause / Step / Reset.
- Click an assignment -> "Vì sao chọn tài xế này?" (real per-candidate score
  breakdown, the actual Hungarian winner -- not just the local top scorer).
- Service Health / Fairness Guardrail panels.

**Live mode is a real-engine illustration on a subset** (default 3,000 of
195,506 requests) -- it is NOT the verified full-Test statistic. For that,
use Verified Replay.

**Public-demo safety limits** (protect the server, not the data -- the
dataset itself always has all 195,506 rows; Verified Replay always reads
the full uncapped Final Test artifacts):

| | `/simulations` (Live) | `/compare/live` |
|---|---|---|
| `request_limit` max | 10,000 | 3,000 |
| `n_drivers` max | 400 | 400 |

Exceeding either returns HTTP 400 with a Vietnamese explanation. At most 20
Live sessions are held in memory at once; creating a 21st evicts the
oldest.

### Verified Replay ("Kết quả kiểm chứng")
- **Compare Policies**: Final Test artifact, 5 seeds, full 195,506-request
  evaluation per seed (`artifacts/final_test/ablation/test_ablation_results.csv`).
- **Long-Horizon**: Final Test, Day 1-37 checkpoints
  (`artifacts/final_test/long_horizon/test_long_horizon.csv`).

Do not confuse the Live slice with the Verified Replay numbers -- they answer
different questions (does the engine visibly work? vs. what did the full,
frozen, 5-seed Final Test actually find?).

## Running locally

```bash
cd backend
pip install -r ../requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`.

## Running tests

```bash
cd backend
pip install -r ../requirements-dev.txt
pytest ../tests/test_deploy_bundle.py -v
```

## Docker

```bash
docker build -t fairdispatch-deployed .
docker run --rm -p 10000:10000 -e PORT=10000 fairdispatch-deployed
```

## Rebuilding `test_eval.parquet`

Only needed if the raw `test.parquet` or the frozen quality-transform rule
changes (it shouldn't -- both are frozen). Requires the raw `test.parquet`
to exist locally (searched at
`03_Source_Code_Va_Ket_Qua/data/test.parquet`, then
`D:/ProjectVSF/fairdispatch_v3_clean/data/test.parquet`, then scanned under
`D:/ProjectVSF`):

```bash
python scripts/build_test_eval_parquet.py
```

## Known limitations (by design, not bugs)

- **Single process, single worker.** `SESSIONS`/`HISTORY` are in-process RAM
  state, bounded (max 20 sessions, oldest evicted first; history display
  capped at 100). A restart/redeploy loses in-memory run history. Do not
  run more than 1 uvicorn worker (a second worker would not share state
  with the first -- see Dockerfile comment).
- No database. This is a decision-support prototype, not a production
  dispatch system -- Postgres/Redis are deliberately out of scope for this.
- Render Free instances sleep after inactivity -- open the URL a few
  minutes before presenting.
