# Multi-Driver Tracking Report

## Root cause / previous limitation

The prior pass (`DRIVER_TRACKING_FIX_REPORT.md`) fixed single-driver
tracking with one `trackedDriverId` variable and one reused focus-ring
marker. By construction that design could only ever track **one** driver
at a time — searching a second driver silently replaced the first, with
no way to watch several drivers side by side.

## New design

- `trackedDrivers` — a `Map<driverId, {driverId, focusMarker}>`, one
  dedicated focus-ring + permanent tooltip **per tracked driver**, all on
  the same `mapLayers.searchFocus` layer (still never touched by
  `syncIdleDrivers()`'s per-batch tooltip rebind on the *original* driver
  markers).
- `cameraTargetDriverId` — exactly one of the tracked drivers is the
  camera target at any time. Only that driver's overlay ever triggers
  auto-pan; the rest keep updating position/tooltip every frame without
  fighting the camera. Clicking a chip's body (or re-searching an
  already-tracked driver) switches the target; removing the current
  target falls back to the most-recently-added remaining tracked driver.
- Tracking chips panel (`#trackingPanel` / `#trackingChips`) — "Đang theo
  dõi N tài xế", one pill per driver with a "×" to untrack just that one,
  the camera target's chip visually active (filled), plus "Ngừng theo dõi
  tất cả".
- `MAX_TRACKED_DRIVERS = 10` — frontend-only UX guard (no API/backend
  change); the 11th search attempt is blocked with a Vietnamese message
  and the tracked set stays at 10.
- **Request selection and driver tracking are now independent** — this
  follow-up explicitly reversed the previous pass's mutual-exclusion rule.
  Opening "Vì sao chọn tài xế này?" no longer clears `trackedDrivers`.

## 05_SanPham_Demo

Files: `frontend/{app.js,index.html,styles.css}`,
`backend/test_driver_tracking_static.py` (rewritten, 10 tests).
Tests: 38/38 pass.
Browser QA: 31/31 Playwright checks PASS (15-driver run, `val.parquet`
data). Screenshots: `report-assets/multi-driver-tracking/`.

## 06_Deployed

Files: same three frontend files +
`tests/test_driver_tracking_static.py` (rewritten, 10 tests) +
`DEPLOYMENT_MANIFEST.json` (3 hashes recomputed).
Tests: 50/50 pass.
Browser/Docker QA: 31/31 Playwright checks PASS (15-driver run, Final Test
data). Screenshots: `report-assets/multi-driver-tracking/`.

A real bug was caught during this pass's own QA run (not a regression
from before, a bug in this follow-up's first draft): `renderTrackingPanel()`
hid the panel on 0 tracked drivers but left the stale chip DOM nodes
behind (`chipsEl.innerHTML` was only cleared in the "has drivers" branch).
Fixed by clearing it in both branches; re-run confirmed 0 chips after
"Ngừng theo dõi tất cả".

## GitHub

Repo: `DucCuong293/fairdispatch-demo` (private), branch `main`. Commit and
push status delivered in the final structured response alongside this
report (captured live, not guessed here).

## Render

Deploy ID / public URL / health status delivered in the final response.

## Public QA

Driver IDs tested + exact behavior (add 3, duplicate search, chip-click
target switch, Run persistence across batches, remove-one, remove-target
fallback, Request coexistence, 10-driver limit + guard message, clear-all)
— delivered in the final response, run against the live public URL after
deploy with the cache-busting version bumped again (`?v=multi-tracking-1`)
so the fix isn't served stale from browser cache.

## Performance

10 tracked drivers held simultaneously with no runaway layer creation —
overlay count observed to track exactly the tracked-driver count at every
step (`0 → 3 → 3 → 2 → 1 → 10 → 0`) across the Playwright run, in both
local runs. No new DOM node or Leaflet layer created per animation frame;
auto-pan remains throttled and single-target only. No new backend/API
calls anywhere in this pass.

## Provenance

Q-table, `policies.py`, `simulator.py`, `test_eval.parquet` — unchanged.
`DEPLOYMENT_MANIFEST.json` `bundled_files` mismatches: 0 after recompute
(`frontend/app.js`, `frontend/index.html`, `frontend/styles.css` were the
only files touched this pass, all three recomputed).
