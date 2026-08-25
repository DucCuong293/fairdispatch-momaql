# Driver Tracking Fix Report

## A. Root cause

`doSearch()` located a driver's marker and called `marker.openTooltip()`
**once** — a one-shot action, not persistent state. Separately, every batch
activation calls `syncIdleDrivers()`, which unconditionally does
`m.unbindTooltip(); m.bindTooltip(...)` on **every** driver marker not
currently mid-trip (including the just-searched one, the instant it goes
idle again) — closing whatever the search had just opened. Moving drivers
were never touched by `syncIdleDrivers()` at all (guarded by
`activeTripByDriver.has(...)`), so a driver mid-trip lost its searched
focus even sooner: nothing kept its tooltip open or the map centered on it
as `updateActiveTrips()` moved the marker every frame. There was no
concept of "the driver the user asked to track" anywhere in state — only
"the driver whose marker happened to receive one `openTooltip()` call."

## B. Solution

- `trackedDriverId` — the single source of truth for which driver (if any)
  is being tracked.
- `latestDriverState` — a `driver_id -> last /step row` cache, written in
  `syncIdleDrivers()` **before** its active-trip early return, so a
  tracked driver's income/trips stay fresh even while it's mid-trip and
  its position is owned by the animation clock, not `syncIdleDrivers()`.
- A single reused focus-ring marker (`trackedFocusMarker`) on its own
  `mapLayers.searchFocus` layer group — never `mapLayers.driver`, so
  `syncIdleDrivers()`'s per-batch rebind can never touch it. Bound with a
  Leaflet `permanent: true` tooltip, repositioned and re-contented every
  `requestAnimationFrame` (`updateTrackedDriverFocus`, called from
  `playbackLoop()`) and again immediately after each batch reveal
  (`activateBatch()`), so there is no stale frame right as new
  assignments/state land.
- Auto-pan is throttled (checked at most every 400ms) and only pans when
  the tracked driver's position leaves a padded "safe" viewport
  (`getBounds().pad(-0.15)` + `panInside`) — no per-frame `panTo()`, no
  camera jitter.
- `clearTrackedDriver()` — a single cleanup path, wired into:
  `hardResetPlayback()` (Reset and New Run both funnel through it),
  `toggleAssignmentSelection()` (opening a Request explanation clears any
  active driver tracking), and a new "Bỏ theo dõi" button.
- `startTrackingDriver()` clears any active Request selection first — the
  two focus mechanisms share one mutual-exclusion rule (only one primary
  map focus at a time), enforced at both entry points rather than
  duplicated per caller.

## C. Files changed — 05_SanPham_Demo

- `frontend/app.js` — tracking state, helpers, wiring (see B above).
- `frontend/index.html` — added `#btnUntrackDriver` ("Bỏ theo dõi") next
  to the existing search button.
- `frontend/styles.css` — `.driver-tracking-tooltip` styling.
- `backend/test_driver_tracking_static.py` — new, 8 tests.

No backend logic touched; local data source unchanged (`val.parquet` /
Validation).

## D. Files changed — 06_Deployed

Same three frontend files + `tests/test_driver_tracking_static.py` (8
tests) + `DEPLOYMENT_MANIFEST.json` (bundled_files hashes recomputed for
every changed file). No change to `policies.py`, `simulator.py`, the
Q-table, `test_eval.parquet`, or any replay artifact.

## E. Tests

| Suite | Before | After |
|---|---|---|
| 05 (`backend/`, `pytest .`) | 28 | **36** (+8 static) |
| 06 (`tests/`) | 40 | **48** (+8 static) |
| Deploy repo (`fairdispatch-demo`) | 40 | **48** |

All green, 0 failures, in all three.

## F. Local visual QA (Playwright, real Chromium)

Driver IDs tested: **#0 → #63** (06, 100-driver run) and **#0 → #4** (05,
5-driver run, chosen small on purpose so a request's numeric ID can't
collide with a driver's ID in the shared search-box namespace — see note
below).

27/27 automated browser checks passed for **both** products:
search-while-paused (ring + permanent tooltip appear, wording "Đang theo
dõi Tài xế #N"), tracking survives `Run` across multiple batches (tooltip
text observed live-updating: `Đang tới điểm đón` → `Đang chở khách` as the
trip actually progressed), survives Pause→Run→Step, exactly one ring after
switching to a different driver, "Bỏ theo dõi" clears the ring/tooltip
without touching the driver marker or pausing the sim, Reset clears
tracking, and Request search still opens "Vì sao chọn tài xế này?" and
correctly clears any active driver tracking first. Zero browser console
errors in either run.

Screenshots: `report-assets/driver-tracking/{tracking_paused,
tracking_running, tracking_after_batches, tracking_cleared}.png` (both
products).

**Note on the search box's shared ID namespace**: `doSearch()` checks
`driverMarkers.has(id)` before falling back to a Request lookup — a
pre-existing design choice, not something this fix changes. With enough
drivers, a numerically low Request `req_idx` can collide with a live
`driver_id` and get interpreted as a driver search instead. This is a
UX ambiguity worth knowing about but is out of scope for this fix (not
requested, not a regression it introduced).

## G. Performance

No new DOM nodes or Leaflet layers are created per frame — the focus ring
and its tooltip are created once and repositioned/re-content'd in place.
Auto-pan is explicitly throttled (≥400ms between checks) and only fires
when the tracked driver actually nears the viewport edge. No new backend
calls were added anywhere in the hot path. No FPS/playback degradation
observed during the Playwright runs (steady batch cadence, no dropped
frames visible in the recorded interactions).

## H. Hash integrity

| Artifact | Result |
|---|---|
| `q_table` | unchanged |
| `policies.py` | unchanged |
| `simulator.py` | unchanged |
| `test_eval.parquet` | unchanged |
| `DEPLOYMENT_MANIFEST.json` bundled_files mismatches | **0** (5 files recomputed: `backend/app.py`, `backend/engine_adapter.py`, `frontend/app.js`, `frontend/index.html`, `frontend/styles.css` — all changed since the manifest's last refresh across this session's Vietnamese-UI pass + this fix; everything else unchanged) |

Confirmed against the live `/provenance` endpoint post-deploy (section K).

## I. GitHub

- Repo: `DucCuong293/fairdispatch-demo` (private).
- Branch: `main`.
- Commit: `d003bf0` — "fix: keep searched driver tracked (focus + tooltip)
  during playback".
- Push: succeeded (`72573a2..d003bf0`).

## J. Render

- Auto-deploy triggered on push.
- See final status in the response delivered alongside this report (deploy
  ID, timing) — captured live rather than guessed here.

## K. Public tracking QA

Same Playwright script run against the live public URL post-deploy — see
delivered response for the pass/fail table and provenance re-check.

## L. Remaining risk

- The search-box ID-namespace ambiguity noted in section F (pre-existing,
  not introduced or worsened by this fix).
- No exact-pixel assertion that the focus ring's screen position equals
  the underlying driver marker's screen position frame-for-frame — both
  are repositioned from the *same* `marker.getLatLng()` call every frame,
  which guarantees they coincide by construction, but this wasn't
  independently verified via raw pixel comparison in the browser test
  (verified instead via the ring's *presence* and the tooltip's *content*
  updating correctly across every phase transition, which is the
  user-visible contract).
