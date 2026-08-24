# FairDispatch Final Test Demo -- Live Deployment Report

Public URL: **https://fairdispatch-demo.onrender.com**
Report generated: 2026-08-24 (post-fix verification pass).

## A. Local final gate

- 38/38 tests pass (`06_Deployed/tests/test_deploy_bundle.py`).
- `DEPLOYMENT_MANIFEST.json`: 12/12 bundled files hash-match (0 mismatch).
- No modification made to `05_SanPham_Demo`, canonical `engine/src/policies.py`,
  canonical `engine/src/simulator.py`, `data/test_eval.parquet` sources, or
  the Q-table -- only `06_Deployed`-scoped files were touched (plus its own
  `.gitattributes`/`render.yaml` additions during Git hardening).

## B. GitHub

- Repo: `https://github.com/DucCuong293/fairdispatch-demo` (dedicated repo,
  not a subdirectory of the research repo). **Visibility: private** (switched
  from public to private after initial deployment -- see incident note in
  section C).
- Branch: `main`.
- Final commit: `4dcb67f` -- "fix: preserve exact byte content (disable git
  line-ending conversion) + add render.yaml".
- Note: an earlier commit (`5213591`) had 8 files silently corrupted by local
  `core.autocrlf=true` (LF -> CRLF) during `git add`, changing their
  committed blob hashes away from canonical even though every local
  working-tree copy stayed byte-correct throughout. Root-caused, fixed via
  `.gitattributes` (`* -text`) + full re-stage, and re-verified byte-for-byte
  before the fix commit was pushed.

## C. Render

- Service ID: `srv-da5s9rrbc2fs73a45l6g`, name `fairdispatch-demo`.
- Plan: **Free**. Region: Oregon. Runtime: Docker.
- Health check path: `/health` (confirmed correctly stored after fixing an
  earlier Git-Bash path-mangling bug that had stored it as a Windows
  filesystem path).
- Auto-deploy: on, triggered on push to `main`.
- Latest deploy: `dep-da5t1rou01pc738deokg`, status **live**, built from
  commit `4dcb67f` (started 2026-08-24T05:04:47Z).
- **Incident: repo visibility change broke Render access (self-inflicted,
  caught and fixed same session).** After the deployment above went live,
  the repo was switched public -> private. Render's GitHub App installation
  did not automatically retain read access to the now-private repo -- a
  manual `render deploys create` triggered `Error: received response code
  404: not found: https://api.github.com/repositories/1344508640`. GitHub's
  own Repository-access list for the Render App already showed
  `fairdispatch-demo` selected and saved, so the break was on Render's side
  (a stale cached repo link on the service itself), not the GitHub App
  grant. Fixed via the Render dashboard: Settings -> Build -> Source ->
  Edit -> re-selected `DucCuong293/fairdispatch-demo` from the picker ->
  Deploy. This re-established the service's repo link and the very next
  `render deploys create` succeeded. A CLI-only attempt
  (`render services update --repo <same-url>`) did NOT fix it by itself --
  the dashboard re-pick step was necessary.
- Post-fix `/provenance` re-verification against the new live deployment --
  **0 mismatches**:

  | Field | Value | Expected | Result |
  |---|---|---|---|
  | `runtime_dataset.sha256` | `2984be13...c91b08` | same | OK |
  | `raw_test_source.matches_canonical` | `true` | `true` | OK |
  | `engine_source.files["policies.py"].sha256` | `fe9e9588...32f5ac` | same | OK |
  | `engine_source.files["simulator.py"].sha256` | `b2dbf2e9...890368d` | same | OK |
  | `q_table.sha256` | `9af13c33...5d64bdb` | same | OK |
  | `runtime_dataset.rows` | 195,506 | 195,506 | OK |

## D. Public smoke test (against the corrected live deployment)

| Check | Result |
|---|---|
| `GET /` | HTTP 200 |
| `GET /health` | HTTP 200, `status:"ok"`, all deps true, `test_eval_rows:195506` |
| `GET /policies` | HTTP 200, `["Greedy","Nearest","LAF","Exact REASSIGN","MOMAQL"]` |
| `GET /replay/ablation` | HTTP 200 |
| `GET /replay/long_horizon` | HTTP 200 |
| `POST /simulations` (test, MOMAQL, 200 drivers, request_limit 3000) | HTTP 200, `total_requests:3000`, dataset label `"Final Test Evaluation View"`, `total_rows_available:195506` |
| 10x `POST /simulations/{id}/step` | all HTTP 200, no 5xx, response sizes 22.5-25 KB |
| `GET /simulations/{id}/explain/{req_idx}` (req_idx from a real assignment) | HTTP 200, full candidate/score breakdown returned |
| `POST /simulations/{id}/reset` | HTTP 200, `reset:true` |
| Negative: `request_limit=10001` | HTTP 400, public-limit message (max 10,000) |
| Negative: `n_drivers=401` | HTTP 400, public-limit message (max 400) |
| Negative: `/compare/live` `request_limit=3001` | HTTP 400, public-limit message (max 3,000) |

## E. UI consistency (static asset inspection)

- Home page (`/`) loads, HTTP 200.
- `/app.js` and `/styles.css` both load, HTTP 200.
- Dataset label `"Final Test Evaluation View"` present in served HTML.
- `"195,506"` request count present in served HTML.
- Live-limit note mentions `10,000` in served HTML.
- `"Verified"` / `"Replay"` labeling present in served HTML.
- `/replay/presets` returns 7 presets including `long_horizon` and
  `ablation`; their final on-screen display text (e.g. whether
  `long_horizon` renders as "Long Horizon") is composed client-side by
  `app.js` from these preset keys and was **not** independently confirmed
  in an actual browser -- this one item needs a quick human eyeball check
  of the live page, not just the static fetch performed here.

## F. Performance (Render Free, Oregon region, single uvicorn worker)

Measured from this machine against the public URL, warm instance (already
awake from prior smoke-test traffic in this same session -- cold-start/
spin-down-wake latency was not separately measured, since doing so would
require deliberately idling the service 15+ min first):

- `/health`: ~0.35s.
- Create simulation (3000 requests, 200 drivers): ~0.77s.
- Per-step latency: ~0.33-0.71s across 10 steps, no trend of degradation.
- `/replay/*` fetch: ~0.34-0.37s.
- No 5xx, no timeout, no visible throttling in this session's traffic.
- These are single-request, single-session measurements from one location;
  they are **not** a substitute for local-Docker benchmarking and should not
  be read as guaranteed under concurrent public load -- Render Free is a
  shared/limited-CPU instance type.

## G. Costs / Render Free tier

- Plan: Free. No credit card requested or provided during this deployment.
- 750 free instance-hours/month; spins down after 15 min idle, ~1 min wake
  on next request.
- Ephemeral filesystem -- not used at runtime (dataset/artifacts are baked
  into the Docker image).
- Overage billing requires a payment method on file; none was added, so any
  overage would suspend the service rather than silently charge it.
- **Cloud resource created**: Render Free Web Service. **Direct hosting
  charge**: $0.

## H. User manual actions taken

1. Approved running `render services create` after the harness's
   permission classifier flagged it ("chạy").
2. Installed/authorized the Render GitHub App for this repo via
   `https://github.com/apps/render/installations/new` ("được rồi đấy").
3. Fixed repo-selection scope for the Render GitHub App via
   `https://github.com/settings/installations` -> Render -> Configure
   ("xong nhé").

No other manual action was required -- `gh` was already authenticated, the
Render CLI login device-code flow ran unattended in the background once the
user completed the browser-side approval.

## I. Final verdict

**DEPLOYED -- PUBLIC URL VERIFIED**
