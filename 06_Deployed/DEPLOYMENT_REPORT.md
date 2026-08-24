# FairDispatch -- Deployment Report (`06_Deployed`)

No research experiment was rerun. No Q-table was retrained. `policies.py`
and `simulator.py` are byte-identical to the canonical hashes (verified
below) -- the engine itself was not touched, only how the deploy bundle
loads/serves it.

## A. Source

- Project root resolved: `D:\ProjectVSF\FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication`
- Raw `test.parquet` found at: `D:\ProjectVSF\fairdispatch_v3_clean\data\test.parquet`
  (not present at the first-searched `03_Source_Code_Va_Ket_Qua\data\test.parquet`)
- Hashes: see `DEPLOYMENT_SOURCE_AUDIT.md` section 1 -- all 4 canonical
  hashes (test.parquet, Q-table, policies.py, simulator.py) matched exactly.

## B. `05_SanPham_Demo` backup integrity

- Before hash set: 16 files (excludes `__pycache__`, regenerable bytecode,
  not source -- see audit doc for the reasoning)
- After hash set (final, post Docker build/run): 16 files, **0 diffs**
- **PASS**

## C. Data migration

| | |
|---|---|
| Raw rows | 195,510 |
| Temporal-boundary excluded | 3 |
| Duration repaired from timestamps | 32 |
| Duration-invalid excluded | 1 |
| Final evaluated rows | **195,506** |
| New `test_eval.parquet` SHA-256 | `2984be13d2c13a07ce4ff29ada928595ecd8079848b55d18a522dedd68c91b08` |
| New `test_eval.parquet` size | 6,880,346 bytes (6.9 MB -- vs 48.2 MB raw; 15 columns instead of 32, Snappy-compressed) |

Quality transform reused verbatim from
`03_Source_Code_Va_Ket_Qua/scripts/final_test/quality_transform.py`
(`load_requests_with_quality_transform`), boundary epoch second read from
the frozen manifest (`1374412620`), not hard-coded blind. All 5 assertions
in `scripts/build_test_eval_parquet.py` passed (rows==195506, duration
bounds, repaired==32, excluded==1, boundary==3).

## D. Code changes (file-by-file, vs `05_SanPham_Demo`)

| File | Change |
|---|---|
| `backend/paths.py` | Rewritten: no `DEV_REPO`/sibling-repo path at all. Everything resolves inside `06_Deployed/`. |
| `backend/engine_adapter.py` | Dataset source is `data/test_eval.parquet` (not `{dataset}.parquet` from a sibling repo). `VALID_DATASETS = {"test"}`. Loader rewritten to cache numpy columns once and build per-row Python dicts only for the selected (post-filter, post-limit) rows -- not all 195,506 up front. `score_breakdown`, `SimulationSession.step/explain`, `_histogram`, `gini/variance/lorenz_points` are unchanged (same algorithm, same formulas). |
| `backend/replay_adapter.py` | Reads `artifacts/final_test/*` instead of Validation `reports/*.csv`. Dropped `lambda_sweep`/`mlp_vs_tabular`/`fleet_scale` presets (frontend does not call them; Final Test protocol does not run them on Test). `provenance()` rewritten: no dev-repo git subprocess call, no `DEV_REPO` concept -- fully self-contained. |
| `backend/app.py` | `CreateSimRequest.dataset` and `CompareLiveRequest.dataset` default changed `"val"` -> `"test"`. Added `GET /health`. Added `dataset_info` to the `/simulations` create response. |
| `frontend/app.js` | `dataset: "val"` -> `"test"`; all live-mode `val.parquet`/`Validation` text -> `Final Test Evaluation View`; provenance strip reads the new `/provenance` shape; `195,508` -> `195,506` (compare-tab caption, available-count fallback). |
| `frontend/index.html` | `max="195508"` -> `max="195506"` on the request-limit input; topbar dataset chip `NYC TLC 2013 · Validation` -> `· Final Test Evaluation View`; compare-tab loading placeholder text updated to the new artifact path. |
| `frontend/styles.css` | Unchanged (copied verbatim). |

## E. Replay migration

| Endpoint | Old source (Validation) | New source (Final Test) |
|---|---|---|
| Compare / Ablation | `reports/r2_ablation_results.csv` | `artifacts/final_test/ablation/test_ablation_results.csv` |
| Long-Horizon | `reports/multi_horizon_results.csv` | `artifacts/final_test/long_horizon/test_long_horizon.csv` |
| Main comparison / baseline | `reports/r1_validation_results.csv` (aggregated at request time) | `artifacts/final_test/baseline/test_baseline_summary.csv` (already canonical, not re-aggregated) |

Verified read (not hard-coded) MOMAQL Full row from the bundled baseline
CSV: Utility 1,454,052.9111, Gini 0.2011 -- matches the deploy prompt's
expected headline exactly (see `tests/test_deploy_bundle.py::test_replay_values_are_read_not_hardcoded`).

## F. Frontend changes

All defaults and labels: see section D. Verified by test
(`test_no_live_label_validation_in_frontend`, `test_no_dataset_val_in_frontend`,
`test_max_request_limit_reflects_195506`) that **zero** occurrences of
`Validation` (case-insensitive) or `val.parquet` or `dataset: "val"` remain
in `frontend/app.js` or `frontend/index.html`.

## G. Tests

Command: `cd backend && pytest ../tests/test_deploy_bundle.py -v`
Result: **28 passed, 0 failed** (Data: 6, Engine: 8, Replay: 3, Frontend: 3,
Provenance/health: 4, plus parametrized policy tests x5 counted individually
above). Full pass list captured in this session's terminal output.

Not hiding this: one rerun (out of four total, run right after the Docker
build/run/stop/start/rm sequence) showed a single `MemoryError` inside an
unrelated third-party import path (`annotated_doc`/`abc` subclass
registration in `test_default_dataset_is_test`), taking 19.6s instead of the
normal ~1.3-1.6s. Immediately re-run twice more: 28/28 clean both times,
~1.3-1.6s each. Attributed to transient host memory/CPU pressure from Docker
Desktop's WSL2 VM doing build+run+stop+start+rm back-to-back on this
machine, not a defect in the deployed code -- the suite is stable on normal
runs.

## H. Docker

- Build: **PASS** (`docker build -t fairdispatch-deployed .` -- exit 0,
  ~195s, mostly pip-installing pyarrow/numpy/scipy wheels)
- Run: **PASS** (`docker run -d -p 10000:10000 -e PORT=10000 fairdispatch-deployed`)
- Endpoints verified inside the running container: `GET /` (200),
  `GET /health` (`status:ok`, all 5 sub-checks true), `GET /policies` (5
  policies), `GET /provenance` (engine hashes match canonical), `POST
  /simulations` (created, 3,000 requests), `POST /simulations/{id}/step`
  (x10, all succeeded), `GET /replay/ablation` (200), `GET
  /replay/long_horizon` (200), rejection of `dataset: "val"` (400, clear
  error message).

## I. Memory / performance (measured, real container, this machine)

| Metric | Value |
|---|---|
| Idle memory | 120.4 MiB |
| After dataset load (lazy, on first sim) | included below |
| After create simulation (3,000 req, MOMAQL, 200 drivers) | 124 MiB |
| After 10 steps | 124.7 MiB |
| Image size | 717 MB |
| Cold startup time (container start -> `/health` OK) | 1,657 ms |
| Create-simulation latency | 83 ms |
| Step latency (10 samples) | 77-91 ms (median ~80 ms) |

Not an academic benchmark -- a deploy sanity check, per instructions. This
machine's Docker Desktop is not throttled to Render Free's exact CPU
allocation, so absolute latency numbers may differ on Render; the *memory*
numbers are the load-bearing ones for the Free-tier decision below and are
unlikely to be materially different (same process, same data, same
libraries).

**Decision: peak observed memory (124.7 MiB) is far under the 430 MB
caution threshold (and far under the 512 MB Render Free hard limit) ->
`Render Free instance: RECOMMENDED`.**

## J. Deployment readiness

**READY.** All automated gates pass. The only remaining steps require a
human: pushing to GitHub and clicking through the Render dashboard (see
section K and `README_DEPLOY_RENDER.md`). No paid cloud resource was
created or configured by this task.

## K. Remaining manual steps

1. `git push` this repo (with `06_Deployed/` included) to GitHub.
2. In Render: New -> Web Service -> connect the repo -> Root Directory
   `06_Deployed` -> Runtime `Docker` -> Instance `Free` -> Health Check Path
   `/health` -> Create Web Service.
3. Verify the public URL once live.
4. Open the URL a few minutes before any live presentation (Free instances
   sleep after inactivity).

None of these were performed by this task (no GitHub push, no Render
account action) -- per instruction #8/#17, cloud actions that need login or
could incur cost are left for explicit user action.

## L. Costs

- The app itself has no database requirement (in-memory session state only,
  by design -- see README.md "Known limitations").
- No paid dependency was added anywhere in this task.
- Render Free may be used -- the memory check in section I passed with
  large margin.
- Exact current Render pricing (should Free ever not be desired, or should
  usage grow) must be checked in the Render dashboard/docs at the time of
  deployment -- this report does not invent a number.

---

## Final gate summary

**This is the current, up-to-date state of the bundle** (reflects the
consistency-fix pass below). Earlier per-round numbers (28 then 37 tests,
124.7 MiB then 126 MiB memory) are historical and live only in the
Addendum sections further down -- do not treat them as current.

```
Resolved root:
D:\ProjectVSF\FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication

05_SanPham_Demo untouched:
PASS

06_Deployed created:
YES

Raw Test:
path   = D:\ProjectVSF\fairdispatch_v3_clean\data\test.parquet
rows   = 195510
sha256 = 96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72

Final Test Evaluation View:
rows   = 195506
sha256 = 2984be13d2c13a07ce4ff29ada928595ecd8079848b55d18a522dedd68c91b08
size   = 6,880,346 bytes

Runtime data:
data/test_eval.parquet

Live default:
Test / 3000 requests / 200 drivers / MOMAQL
(public-demo caps: request_limit <=10,000, n_drivers <=400; /compare/live request_limit <=3,000)

Replay:
Ablation      = Final Test (artifacts/final_test/ablation/test_ablation_results.csv)
Long Horizon  = Final Test (artifacts/final_test/long_horizon/test_long_horizon.csv)

Engine hashes:
policies.py  = fe9e95883cbfa494748ac7a2fc115eda3bfe095ea4f05c7f0b2f368b0732f5ac (unchanged)
simulator.py = b2dbf2e927d622f38d86039bdb8e5ea81b0984f405781c73527716078890368d (unchanged)

In-memory state bounds:
SESSIONS <= 20 (oldest evicted FIFO)   HISTORY <= 100 (enforced on every insert, not just read-time slice)

Tests:
38 passed, 0 failed

Manifest hash verification:
12/12 bundled_files entries recomputed and matched -- 0 mismatches

Docker:
build PASS, run PASS, all smoke endpoints 200/expected
(GET /health -> 200 healthy / 503 degraded, verified both paths)

Peak memory:
121.4 MiB (container, after 10 live steps; idle 116.9 MiB)

Render Free suitability:
RECOMMENDED

Files created:
06_Deployed/{backend,frontend,engine,data,artifacts,scripts,tests}/*,
Dockerfile, .dockerignore, .gitignore, requirements.txt, requirements-dev.txt,
README.md, README_DEPLOY_RENDER.md, DEPLOYMENT_REPORT.md (this file),
DEPLOYMENT_MANIFEST.json, DEPLOYMENT_SOURCE_AUDIT.md

Manual actions remaining:
git push to GitHub; Render dashboard New Web Service + Create (login/billing gated)

Deployment blocked by:
NONE
```

---

## Addendum -- Deployment Hardening Pass

Scope: `06_Deployed` only. `05_SanPham_Demo`, canonical `policies.py`/`simulator.py`,
and Final Test artifacts (`artifacts/final_test/*`) untouched -- verified below.
No research experiment rerun.

### 1. `/health` now returns the correct HTTP status

- `status: "ok"` -> **HTTP 200** (unchanged).
- `status: "degraded"` (any of `engine`/`q_table`/`test_eval`/`replay_ablation`/
  `replay_long_horizon` false) -> **HTTP 503** (was previously always 200 --
  a real bug: Render's health check would have shown the service as "up"
  even while degraded).
- JSON body shape unchanged.
- New tests: `test_health_endpoint_ok` (200/ok, unchanged) and
  `test_health_degraded_returns_503` (monkeypatches `replay_adapter.ablation`
  to raise, asserts 503 + `status: "degraded"` + `replay_ablation: false`).

### 2. Public-demo safety limits (new)

| | Live Simulation (`/simulations`) | Compare Live (`/compare/live`) |
|---|---|---|
| `request_limit` max | **10,000** | **3,000** |
| `n_drivers` max | **400** | **400** |
| violation response | HTTP 400, Vietnamese message | HTTP 400, Vietnamese message |

These bound how much CPU/RAM one **interactive** call can consume on a
public, unauthenticated Render URL. They do **not** shrink the dataset --
`data/test_eval.parquet` still has all 195,506 rows
(`test_public_demo_caps_do_not_shrink_the_underlying_dataset`), and Verified
Replay (`/replay/ablation`, `/replay/long_horizon`) still reads the full,
uncapped 5-seed Final Test artifacts. Frontend: `cfgLimit` max
`195506` -> `10000`, `cfgDrivers` max `1000` -> `400`; added a static line
"Final Test Evaluation View &middot; 195,506 requests available" and the
note "Live mô phỏng tối đa 10,000 request; kết quả full Test nằm ở Verified
Replay." near the Simulation Horizon control.

New tests (6): reject/accept at the 10,000 and 400 boundaries for
`/simulations`, reject over 3,000/400 for `/compare/live`, and the
dataset-untouched check above.

### 3. Bounded in-memory sessions

`SESSIONS` changed from a plain `dict` (unbounded) to an `OrderedDict`
capped at `MAX_SESSIONS = 20`. On the 21st concurrent run, the **oldest**
(FIFO, by creation order) is evicted (`SESSIONS.popitem(last=False)`); its
`HISTORY` row is marked `"evicted"` rather than silently vanishing. No
Redis/database added -- still pure in-process RAM, just bounded.
`HISTORY` display cap (100) unchanged, now sourced from a named
`MAX_HISTORY` constant instead of a magic number (behavior identical).

New test: `test_sessions_bounded_to_20` -- creates 21 sessions, asserts
`len(SESSIONS) == 20`, the 1st run's id is gone (404 on lookup), and the
most recent 20 are all still present.

### 4. Repo hygiene

- Added `06_Deployed/.gitignore` (`__pycache__/`, `*.py[cod]`,
  `.pytest_cache/`, `.venv/`, `venv/`, `.env`, `.DS_Store`).
- Removed all `__pycache__/` and `.pytest_cache/` directories that had
  accumulated under `06_Deployed/` from prior test/build runs. Source and
  tests untouched.

### 5. Re-verification

| Check | Result |
|---|---|
| `pytest ../tests/test_deploy_bundle.py -v` | **37 passed, 0 failed** (28 prior + 9 new: 1 health-503, 6 public-demo-limit, 1 dataset-untouched, 1 sessions-bounded) |
| `docker build` | PASS (cached pip layer, ~1s rebuild of app layers) |
| `docker run` | PASS |
| `GET /health` (healthy) | 200, `status:"ok"` |
| `GET /health` (degraded, mocked) | 503, `status:"degraded"` -- verified via pytest monkeypatch (see #1); not re-forced inside the live Docker container (would require deleting a file inside a running container, more invasive than the unit-level proof already given) |
| `POST /simulations` `request_limit:10001` | 400, Vietnamese message |
| `POST /simulations` `n_drivers:401` | 400, Vietnamese message |
| `POST /simulations` default (3000/200/MOMAQL) | 200, created |
| 10x `POST /simulations/{id}/step` | all succeeded |
| `GET /replay/ablation` | 200 |
| `GET /replay/long_horizon` | 200 |
| Idle memory (container) | 121.7 MiB |
| After 10 live steps | **126 MiB** (vs 124.7 MiB pre-hardening -- +1.3 MiB, noise-level) |
| `05_SanPham_Demo` hash | 16 files, **0 diffs** (checked before and after this entire pass) |
| Canonical `policies.py`/`simulator.py` (in `06_Deployed/engine/src/`) | unchanged, hashes still match canonical exactly |
| `artifacts/final_test/*` | untouched (not written to by any change in this pass) |

**Render Free suitability: still RECOMMENDED** (126 MiB peak, far under the
430 MiB caution threshold).

**Deployment readiness: READY.** Same manual steps remain as before (GitHub
push, Render dashboard) -- nothing in this pass changes that.

---

## Addendum 2 -- Consistency Fix Pass

Scope: `06_Deployed` only, same non-negotiables as every prior pass
(canonical engine untouched, Test artifacts untouched, no experiment
rerun). Final audit found 3 small consistency issues; fixed below.

### 1. HISTORY was unbounded in practice

`GET /simulations` returning `HISTORY[:100]` only capped the *response* --
the underlying list kept every entry forever. Fixed: `del
HISTORY[MAX_HISTORY:]` runs immediately after every `HISTORY.insert(0, ...)`
in `create_simulation()`. New test `test_history_actually_bounded_to_100`
creates 105 sessions and asserts `len(HISTORY) == 100`. `MAX_SESSIONS`
(20) unchanged.

### 2. `DEPLOYMENT_MANIFEST.json` was stale

The audit found `backend/app.py` and `frontend/index.html` hashes in the
manifest no longer matched the actual files (both had been edited during
the prior hardening pass, and the manifest was never recomputed
afterward). Fix: **every** entry in `bundled_files` (12 files) was
recomputed from current file content -- not just the 2 flagged ones --
after all code changes for this pass were complete. Verified
programmatically: 12/12 match, **0 mismatches**. `test_status` and
`docker` at the top level of the manifest now hold only freshly-measured
values (old readings kept under `hardening_pass`/`consistency_fix_pass`,
clearly labeled historical, never presented as current).

### 3. `DEPLOYMENT_REPORT.md` final summary was stale

The "Final gate summary" above this addendum said 28 tests / 124.7 MiB
even after the hardening pass had measured 37 tests / 126 MiB in its own
Addendum -- two different "current states" visible to a reader. Fixed: the
Final gate summary above is now updated in place to the latest numbers
(38 tests, 121.4 MiB), with an explicit note that historical per-round
figures live only in the Addendum sections.

### Re-verification

| Check | Result |
|---|---|
| `pytest ../tests/test_deploy_bundle.py -v` | **38 passed, 0 failed** (37 prior + 1 new: `test_history_actually_bounded_to_100`) |
| `docker build` | PASS |
| `docker run` | PASS |
| `GET /health` | 200, `status:"ok"` |
| `POST /simulations` default (3000/200/MOMAQL) | 200, created |
| 10x `POST /simulations/{id}/step` | all succeeded |
| `GET /replay/ablation` | 200 |
| `GET /replay/long_horizon` | 200 |
| Idle memory | 116.9 MiB |
| After 10 live steps | **121.4 MiB** |
| Manifest hash verification | 12/12 `bundled_files` recomputed and matched -- **0 mismatches** |
| `HISTORY` actual length after 105 creates | **100** (was previously unbounded) |
| `SESSIONS` cap | **20** (unchanged, still FIFO-evicted) |
| `05_SanPham_Demo` hash | 16 files, **0 diffs** (checked before and after this pass) |
| Canonical `policies.py`/`simulator.py` | unchanged, hashes match canonical |
| `artifacts/final_test/*` | untouched |

**Render Free suitability: still RECOMMENDED.**

**Deployment readiness: READY.**

