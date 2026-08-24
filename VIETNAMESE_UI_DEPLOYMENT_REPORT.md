# Vietnamese UI — Deployment Report

Public URL: **https://fairdispatch-demo.onrender.com**

## A. Scope

- **05 modified files**: `frontend/index.html`, `frontend/app.js`,
  `backend/app.py`, `backend/engine_adapter.py`, `README.md`,
  `backend/test_engine.py` (1 assertion updated to match new Vietnamese
  error text), `backend/test_frontend_vietnamese_ui.py` (new).
- **06 modified files**: `frontend/index.html`, `frontend/app.js`,
  `backend/app.py`, `backend/engine_adapter.py`, `README.md`,
  `README_DEPLOY_RENDER.md` (UI-label cross-references only),
  `tests/test_deploy_bundle.py` (1 assertion updated),
  `tests/test_frontend_vietnamese_ui.py` (new).
- **Deployed repo modified files** (`github.com/DucCuong293/fairdispatch-demo`):
  same 6 files as 06 above, synced 1:1 from `06_Deployed`.
- **Not touched**: `05_SanPham_Demo`'s canonical `engine/src/policies.py` /
  `engine/src/simulator.py`, `data/test_eval.parquet`, the Q-table, any
  Final Test artifact, `styles.css` (no text content to translate).

## B. Translation inventory

See `VIETNAMESE_UI_AUDIT.md` (full inventory + baseline glossary). Totals:
~120 strings in each `index.html`, ~55 in each `app.js`, ~12 backend
messages in each `app.py`, ~7-8 in each `engine_adapter.py`. Allowed
English remaining: canonical names (FairDispatch/MOMAQL/Greedy/Nearest/
LAF/REASSIGN/NYC TLC 2013) + all technical/API identifiers.

## C. Key wording

See `VIETNAMESE_UI_AUDIT.md` §"Key wording" table — Control Room, Live
Simulation, Compare Policies, Long-Horizon, Run History, Service Health,
Utility/Gini/Fairness, badges (LIVE ENGINE → ENGINE TRỰC TIẾP, VERIFIED
REPLAY → KẾT QUẢ KIỂM CHỨNG), and the MOMAQL score-breakdown labels
(Immediate Utility / Future Zone Value / Fairness Adjustment).

## D. 05 local QA

- App start: `uvicorn app:app --port 8092` → HTTP 200 on `/`.
- UI: Vietnamese tab labels (Mô phỏng trực tiếp / So sánh chiến lược /
  Đánh giá dài hạn / Lịch sử lần chạy), dataset label "Tập xác thực"
  confirmed present in served HTML.
- Simulation: create (val, MOMAQL, 50 drivers, 200 requests) → 200, step →
  200, reset → 200.
- Compare / Long-Horizon / provenance: endpoints reachable, 200.
- Tests: `pytest .` → **28 passed** (26 original + 2 new i18n static-check
  parametrizations).
- **PASS.**

## E. 06 local QA

- Tests: `pytest tests/` → **40 passed** (38 original + 2 new).
- Docker: not rebuilt this pass (no dependency/runtime change, only text
  literals in already-verified files) — local `uvicorn` run used instead
  for speed; the deployed container build (Render) is the authoritative
  Docker-path verification and is covered in section G below.
- Health: `/health` → `{"status":"ok",...,"test_eval_rows":195506}`.
- Live: create (test, MOMAQL, 50 drivers, 200 requests) → 200, 3× step →
  200, explain(assigned req_idx) → 200 with full candidate breakdown,
  reset → 200.
- Replay: `/replay/ablation`, `/replay/long_horizon` → 200.
- Provenance: q_table / policies.py / simulator.py / runtime_dataset
  hashes all match canonical (0 mismatch).
- **PASS.**

## F. GitHub

- Repo: `github.com/DucCuong293/fairdispatch-demo` (private).
- Branch: `main`.
- Commit: `72573a2` — "feat: Vietnamize entire user-facing UI (labels,
  buttons, tabs, tooltips, error messages)".
- Push: succeeded (`4dcb67f..72573a2 main -> main`).

## G. Render

- Auto-deploy triggered on push (as configured, `autoDeployTrigger: commit`).
- Deploy `dep-da5tire7bikc73c04pag`, status **live**, built from commit
  `72573a2` (started 2026-08-24T05:41:01Z, finished 05:41:36Z, ~35s — layer
  cache reuse, only text files changed).
- Public URL: `https://fairdispatch-demo.onrender.com`.
- Health: `/health` → 200, `status:"ok"`.
- **PASS.**

## H. Provenance integrity

| Field | Result |
|---|---|
| `q_table.sha256` | matches canonical |
| `engine_source.files["policies.py"].sha256` | matches canonical |
| `engine_source.files["simulator.py"].sha256` | matches canonical |
| `runtime_dataset.sha256` | matches canonical |
| `runtime_dataset.rows` | 195,506 |
| **Mismatches** | **0** |

Confirms the UI-only change did not touch engine/data byte-identity —
expected, since no engine/data file was in the diff.

## I. English leakage

- Forbidden user-facing English remaining: **0** (verified by
  `test_frontend_vietnamese_ui.py`, both products, and manual review of
  the full raw string-literal candidate list — see
  `VIETNAMESE_UI_FINAL_AUDIT.md`).
- Allowed terms + reason: canonical algorithm/dataset names (rule 1.1),
  all JSON field names / API routes / DOM ids / JS identifiers / CSS
  classes / file names / SHA-256 hashes (rule 1.1 + §12 — API contract
  and internal identifiers are explicitly out of scope), source-code
  comments (never rendered).

## J. Public smoke test (against the live deployment, post-translation)

| Check | Result |
|---|---|
| `GET /` (Vietnamese tab labels present) | 200, OK |
| `GET /health` | 200, `status:"ok"` |
| `POST /simulations` (test, MOMAQL, 200 drivers, 3000 req) | 200 |
| 3× `POST /simulations/{id}/step` | all 200 |
| `POST /simulations/{id}/reset` | 200 |
| Negative: `n_drivers=401` | 400, Vietnamese message (đúng diacritics) |
| Negative: `policy=BOGUS` | 400, Vietnamese message (đúng diacritics) |
| `/provenance` hash re-check | 0 mismatch |

No browser-automation tool was available in this environment; the
Public UI Check was done via raw HTTP fetch of the served HTML/JS
(confirmed Vietnamese labels present, dataset label, live-limit note,
badge text) rather than an actual rendered screenshot — recommend one
manual eyeball pass of `https://fairdispatch-demo.onrender.com` to
confirm layout/wrapping is not broken by the (generally longer)
Vietnamese label text, since that visual check is outside this
environment's tooling.

## K. Final verdict

```
VIETNAMESE UI COMPLETE — LOCAL + DEPLOYED VERIFIED
```
