# Deploying `06_Deployed` to Render (Web Service, Docker)

**Status: already deployed.** Live public URL:
**https://fairdispatch-demo.onrender.com**

This document now describes what was actually done, so a future redeploy
(or an audit of the current setup) can reproduce or verify it exactly.

## What was actually used

- **Repo**: dedicated repo `https://github.com/DucCuong293/fairdispatch-demo`
  (public), containing ONLY the contents of `06_Deployed` at repo root (no
  subdirectory root-path config needed). This was chosen over pushing
  `06_Deployed` as a subdirectory of the main research-project repo, to keep
  the deployed surface minimal and independently auditable.
- **Branch**: `main`. Latest commit deployed: `4dcb67f` ("fix: preserve
  exact byte content (disable git line-ending conversion) + add
  render.yaml").
- **Service**: created directly via Render CLI (`render services create
  --type web_service --runtime docker --plan free ...`), not the dashboard
  wizard. A `render.yaml` Blueprint file is present at the repo root as a
  reference/reproducibility artifact but was not itself used to launch the
  service.
- **Service ID**: `srv-da5s9rrbc2fs73a45l6g`. **Plan**: Free. **Region**:
  Oregon. **Auto-deploy**: on, triggered on every push to `main` (confirmed
  working: the fix commit above auto-triggered deploy
  `dep-da5siqm7bikc73bvhk2g`, which went live).
- **Health Check Path**: `/health` -- HTTP 200 (`status:"ok"`) when the
  engine, Q-table, `test_eval.parquet`, and both replay artifacts all
  loaded; HTTP 503 (`status:"degraded"`) otherwise. Confirmed correct in
  production.
- **Start command**: left as the Dockerfile's own `CMD` (`uvicorn app:app
  --host 0.0.0.0 --port ${PORT:-10000} --workers 1`); Render supplies
  `$PORT`.
- **Environment variables**: none set. No `FAIRDISPATCH_DEV_REPO` or
  `D:\...` path -- the deployed bundle has zero dependency on anything
  outside itself.

## Reproducing this from scratch

```bash
# 1. Push a repo containing 06_Deployed's contents at its root
git init && git add -A && git commit -m "deploy: FairDispatch Final Test demo"
gh repo create <name> --public --source=. --push

# 2. Create the Render service (Free plan, Docker runtime)
render services create --name <name> --type web_service --repo <github-url> \
  --branch main --runtime docker --plan free --health-check-path /health \
  --confirm -o json
```

Requires: `gh` authenticated, Render CLI installed + `render login
--confirm` completed, and the Render GitHub App authorized for the target
repo (`https://github.com/apps/render/installations/new`, or
`github.com/settings/installations` -> Render -> Configure -> add the repo)
-- this authorization step has no CLI/API equivalent and must be done once
in the GitHub web UI.

**If the repo's visibility is later changed (public -> private or vice
versa)**: the GitHub-side App permission (Configure -> Repository access)
may already show the repo correctly, but Render's own service-level repo
link can still go stale and return `404: not found:
api.github.com/repositories/<id>` on deploy. Fixing the GitHub side alone is
not sufficient -- also go to the Render dashboard: service -> Settings ->
Build -> Source -> **Edit** -> re-select the repo from the picker -> Deploy.
`render services update --repo <same-url>` via CLI does NOT trigger this
re-link by itself.

## Public-demo safety

This service has no authentication -- anyone with the URL can create Live
Simulation runs. Server-side caps are in place (see `README.md`):
`request_limit` max 10,000 (3,000 for `/compare/live`), `n_drivers` max 400,
and at most 20 concurrent in-memory sessions (oldest evicted first, FIFO).
Confirmed live against the public URL (all three limits correctly return
HTTP 400 with an explanatory message).

## Render Free tier facts (per `render.com/docs/free`)

- No credit card required to create.
- 750 free instance-hours/month.
- Spins down after 15 min of inactivity; first request after sleep can take
  up to ~1 min to wake.
- Ephemeral filesystem -- irrelevant here since `test_eval.parquet` and all
  artifacts are baked into the Docker image, never written at runtime.
- Overages (bandwidth/build-minutes) are billed only if a payment method is
  on file; otherwise the service is suspended, not silently charged.
- No billing/payment method was requested or provided during this
  deployment.

## Costs

- No database/Redis/disk was added.
- No paid resource or paid plan was created.
- Direct hosting charge for this service: **$0 (Free plan)**.
