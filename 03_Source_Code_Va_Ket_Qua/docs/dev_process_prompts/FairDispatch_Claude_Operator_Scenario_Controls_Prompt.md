# CLAUDE CODE PROMPT — ADD OPERATOR SCENARIO CONTROLS TO FAIRDISPATCH

Bạn là Senior Product Engineer + Research Software Engineer.

Hãy nâng cấp trực tiếp FairDispatch hiện tại dựa trên tài liệu:

```text
FairDispatch_Operator_Control_Presets_TimeFilters_Requirements.md
```

**Đọc toàn bộ file đó trước khi code.**

---

# PROJECT PATH

```text
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Không tạo project mới.

Không rewrite engine.

Không làm mất continuous playback, Leaflet map, Why This Driver, Compare, Replay, Horizon, provenance và tests hiện tại.

---

# FIRST — AUDIT CURRENT UI / API

Đọc:

```text
frontend/index.html
frontend/styles.css
frontend/app.js

backend/app.py
backend/engine_adapter.py
backend/replay_adapter.py
backend/test_engine.py

README.md
PRODUCT_FIX_PLAN.md
PRODUCT_FRONTEND_PORT_PLAN.md
OPERATOR_CONTROL_ROOM_PLAN.md
```

Xác định chính xác:

- current create-run payload;
- request timestamp field;
- weekday extraction;
- data cache;
- request_limit semantics;
- current fleet control;
- Save Run / History implementation;
- panel sections;
- Advanced/Research state.

Không invent field.

---

# CREATE PLAN

Tạo/update:

```text
OPERATOR_SCENARIO_CONTROLS_PLAN.md
```

Columns:

```text
Feature
Current support
Data source
Frontend changes
Backend changes
Tests
Status
```

---

# PHASE 1 — TIME-OF-DAY FILTER

Implement operator-facing segmented buttons:

```text
[ All Day ]
[ Morning Peak ]
[ Evening Peak ]
[ Night ]
[ Custom ]
```

Mapping:

```text
All Day       00–24
Morning Peak  06–09
Evening Peak  17–19
Night         22–05
```

Custom:

```text
Start Hour
End Hour
Apply
```

Overnight must work.

---

# PHASE 2 — DAY FILTER

Main:

```text
[ All ]
[ Weekday ]
[ Weekend ]
[ Custom ]
```

Custom:

```text
Mon Tue Wed Thu Fri Sat Sun
```

Use actual timestamp weekday.

---

# PHASE 3 — FILTER ORDER

Correct order:

```text
load/cached dataset
→ apply day filter
→ apply time filter
→ apply request_limit
→ init simulation
```

Do not take first 3000 before filtering.

Return:

```text
filtered_request_count
used_request_count
```

---

# PHASE 4 — HORIZON PRESETS

Replace primary raw request limit UI with:

```text
Simulation Horizon

[ Quick ]
[ Standard ]
[ Extended ]
[ Custom ]
```

Map to documented values.

Suggested only if matches current product:

```text
Quick = 200
Standard = 3000
Extended = 10000
```

Audit before committing.

Custom raw numeric.

Raw `request_limit` remains under Advanced.

---

# PHASE 5 — FLEET PRESETS

If current engine supports:

```text
100
200
400
```

implement segmented:

```text
[100] [200] [400] [Custom]
```

Canonical default:

```text
200
```

Do not use this control to limit visual moving cars.

It changes actual engine fleet size.

---

# PHASE 6 — REMOVE/DO NOT ADD CONCURRENT VEHICLE ENGINE LIMIT

Do NOT implement:

```text
1 car
4 cars
8 cars
```

as engine control.

If visual clutter needs control:

use:

```text
Visual Density
Low / Medium / Full
```

or existing route-trail retention.

Visualization only.

---

# PHASE 7 — DO NOT ADD CONFIDENCE

Do NOT add:

```text
70%
80%
90%
```

unless engine has calibrated uncertainty.

Current requirement says no.

---

# PHASE 8 — DO NOT ADD Q BAND / REPRESENTATIVE GROUP

Do NOT add:

```text
q chung
theo band
đại diện
>300k
```

unless current FairDispatch code already has a real, documented use case.

Do not port old demo-specific controls.

---

# PHASE 9 — SAVE RUN

Integrate current Run History/Save flow.

Save:

```text
Run ID
Policy
Objective
Fleet
Forecast
Lambda
Seed
Dataset
Time Filter
Day Filter
Horizon
Metrics
Provenance
```

If Save currently only saves metrics:

extend config.

---

# PHASE 10 — RE-RUN

If current history architecture supports low-complexity restore:

add:

```text
Re-run
```

Load saved config including filters.

Bonus if complex; Save itself is mandatory.

---

# PHASE 11 — COLLAPSIBLE SECTIONS

Add collapse toggles:

```text
CURRENT RUN
OPERATING OBJECTIVE
SCENARIO
SIMULATION
SERVICE HEALTH
FAIRNESS
ALERTS
MAP LAYERS
ADVANCED / RESEARCH
```

Default:

- Current Run open
- Objective open
- Scenario open
- Simulation open
- Service Health open
- Fairness maybe open
- Alerts open if active
- Map Layers collapsed/open based on space
- Advanced collapsed

Keep panel compact.

---

# PHASE 12 — PRESET BUTTON UX

Use segmented controls instead of dropdown where options <= 4.

Prioritize:

```text
Objective
Fleet
Time
Day
Speed
Horizon
```

Ensure keyboard accessibility:

- buttons;
- aria-pressed if applicable.

---

# PHASE 13 — SCENARIO SUMMARY

Show:

```text
CURRENT SCENARIO

Balanced
MOMAQL
200 drivers
Forecast ON

Friday / Weekday
17:00–19:00

Validation
Standard · 3,000 requests
```

Only actual selected settings.

---

# PHASE 14 — FILTER ACTIVE BADGE

If Time or Day != default:

show visible badge:

```text
SCENARIO FILTER ACTIVE
```

Example:

```text
Weekday · 17:00–19:00
```

Do not confuse with canonical validation run.

---

# PHASE 15 — DATA SOURCE

Keep:

```text
NYC TLC 2013
Validation
```

Show:

```text
Used X / filtered Y / total 195,508
```

Use actual metadata, not hard-code if API can derive.

Test set remains unavailable from normal Operator scenario UI.

---

# PHASE 16 — TEST SET RULE

DO NOT switch live demo to test.

DO NOT add:

```text
Test
```

as casual segmented control.

Held-out test remains for final scientific evaluation later.

---

# PHASE 17 — BACKEND FILTER MODEL

Use Pydantic typed config.

Example concept:

```python
class TimeFilter(BaseModel):
    mode: str = "all"
    start_hour: int | None = None
    end_hour: int | None = None

class DayFilter(BaseModel):
    mode: str = "all"
    days: list[int] | None = None
```

Validate:

```text
hour 0..23
days 0..6
```

Overnight accepted.

---

# PHASE 18 — CACHE

Do not reread full parquet for every filter selection.

Reuse existing request cache.

Filter cached request list/table.

If cache currently loses timestamp object:

retain enough field for hour/weekday.

---

# PHASE 19 — TIMESTAMP SEMANTICS

Audit actual `pickup_ts` type.

If numeric epoch/seconds:

convert correctly.

If already parsed datetime:

use directly.

Do not assume timezone incorrectly.

Current NYC TLC timestamps must be interpreted consistently with research preprocessing.

---

# PHASE 20 — EMPTY SCENARIO

If no requests after filter:

return controlled response:

```text
No requests match selected scenario.
```

HTTP 400 or valid empty-session behavior depending architecture.

Frontend:

show message, not crash.

---

# PHASE 21 — CONTINUOUS PLAYBACK

Filters affect which requests engine receives.

After run starts:

continuous playback architecture remains unchanged.

Do not filter visually after engine assignment.

Filter before simulator.

---

# PHASE 22 — LIVE QUICK COMPARE

If Live Quick Compare uses current scenario:

pass:

- fleet;
- time filter;
- day filter;
- request horizon;
- seed;
- lambda.

Label:

```text
LIVE ENGINE — SCENARIO QUICK COMPARE
```

If not implemented safely:

keep Quick Compare canonical and explicitly say filters do not apply.

Prefer consistency.

---

# PHASE 23 — VERIFIED REPLAY

Verified Research Replay remains canonical artifact.

Do NOT dynamically apply time/day filter to precomputed verified results unless artifact supports it.

If filters active:

Replay tab still clearly:

```text
Canonical Verified Experiment
```

not current filtered scenario.

---

# PHASE 24 — ADVANCED PANEL

Move/show:

```text
Lambda
Gamma
Alpha
Seed
Exact Request Limit
Dataset
ETA threshold
Batch window
Deadhead cost
```

Only editable if truly supported.

Fixed values labeled fixed.

---

# PHASE 25 — UI STYLE

Use current professional control-room visual.

Reference image pattern:

- compact segmented controls;
- small labels;
- clear active selection;
- collapsible panel;
- no giant dropdowns.

Do not copy old demo data or old business logic.

---

# PHASE 26 — TESTS

Add tests:

## Time Filter

- all day
- 06–09
- 17–19
- 22–05 overnight
- custom

## Day Filter

- weekday
- weekend
- custom days

## Filter Order

Known dataset:
filter first → limit after.

## Empty Scenario

No crash.

## Save Run

Saved config includes filters.

## Re-run if implemented

Config restored.

## Test Set

No casual live test selector.

Run existing test suite.

Frontend:

```text
node --check frontend/app.js
```

---

# PHASE 27 — DOCUMENTATION

Update:

```text
README.md
PRODUCT_AUDIT.md
PRODUCT_FIX_PLAN.md
OPERATOR_CONTROL_ROOM_PLAN.md
DEMO_SCRIPT.md
```

Add/update:

```text
OPERATOR_SCENARIO_CONTROLS_PLAN.md
```

Document:

- time presets;
- day presets;
- horizon presets;
- filter order;
- scenario vs canonical research;
- Save Run;
- controls intentionally NOT added.

Explicitly document:

```text
Confidence control not implemented because no calibrated confidence metric exists.
```

```text
Concurrent vehicle limiter not implemented because active vehicle count is determined by simulator.
```

---

# PHASE 28 — DEMO FLOW

Demo:

1. Open app.
2. Show Balanced / 200 / Forecast ON.
3. Time:
   ```text
   Evening Peak 17–19
   ```
4. Day:
   ```text
   Weekday
   ```
5. Horizon:
   ```text
   Standard
   ```
6. Scenario badge appears.
7. Run.
8. Continuous playback.
9. Show service/fairness.
10. Save Run.
11. Reset.
12. Change:
   ```text
   Weekend · All Day
   ```
13. Start another run.
14. Show History if needed.

This demonstrates operator scenario analysis.

---

# ACCEPTANCE CRITERIA

- [ ] Time presets work.
- [ ] Overnight works.
- [ ] Day presets work.
- [ ] Custom days work.
- [ ] Filtering occurs before request limit.
- [ ] Horizon presets work.
- [ ] Fleet presets work.
- [ ] Save Run includes scenario.
- [ ] Scenario summary visible.
- [ ] Active filter badge visible.
- [ ] Panel sections collapsible.
- [ ] Main controls use segmented buttons.
- [ ] No fake confidence.
- [ ] No q-band control.
- [ ] No representative-group control.
- [ ] No concurrent-vehicle engine limiter.
- [ ] Test set remains reserved.
- [ ] Continuous playback unchanged.
- [ ] Why This Driver unchanged.
- [ ] Compare/Replay/Long-Horizon unchanged.
- [ ] Existing tests still pass.

---

# FINAL TARGET

The control panel should feel like:

> **“I can quickly choose a realistic operating scenario — fleet size, peak period, weekday/weekend, simulation horizon — run it, watch the city operate, save the run, and compare outcomes.”**

It should NOT feel like:

> **“A panel full of arbitrary research knobs copied from an old demo.”**

---

# WHEN FINISHED

Return:

```text
Controls added:
- ...

Controls intentionally not added:
- ...

Time/day filtering implementation:
- ...

Horizon presets:
- ...

Fleet presets:
- ...

Save Run:
- ...

Backend/API changes:
- ...

Tests:
- ...

Files changed:
- ...

Run command:
- ...

Known limitations:
- ...
```

Do not reply only:

> Done.
---

# PHASE 29 — FIX LAYOUT SPACING / DENSITY TRONG CÙNG VÒNG TRIỂN KHAI

Sau khi audit/triển khai các Operator Scenario Controls ở trên, phải sửa luôn vấn đề bố cục hiện tại:

> **Map và analytics đã đúng vị trí, nhưng đang có một khoảng trắng chiều dọc rất lớn giữa hàng charts và Operational Log.**

Đây là frontend layout bug / density issue, không phải content requirement.

Không tạo prompt/project riêng. Sửa trong cùng task này.

---

## 29.1 AUDIT ROOT CAUSE

Search trong:

```text
frontend/styles.css
frontend/index.html
```

và DOM/layout runtime cho:

```css
height
min-height
max-height
flex
flex-grow
grid-template-rows
align-content
justify-content
gap
margin
padding
overflow
```

Đặc biệt audit wrapper của:

```text
workspace
main/left column
map
analytics
bottom/log
sidebar
```

Tìm pattern như:

```css
height: 100%;
min-height: ...;
flex: 1;
grid-template-rows: ... 1fr ...;
justify-content: space-between;
```

có thể tạo “empty stretch row”.

Phải sửa root cause.

TUYỆT ĐỐI KHÔNG fix bằng:

```css
margin-top: -200px;
```

hay negative-margin hack.

---

## 29.2 MAIN LEFT COLUMN TARGET

Target vertical flow:

```text
Map
8–14px
Analytics charts
8–14px
Operational Log
```

Nếu Grid:

```css
.main-left {
    grid-template-rows: auto auto auto;
    align-content: start;
    gap: 10px;
    min-height: 0;
}
```

Nếu Flex:

```css
.main-left {
    flex-direction: column;
    justify-content: flex-start;
    gap: 10px;
}
```

Không dùng:

```css
justify-content: space-between;
```

cho map/charts/log container.

---

## 29.3 ANALYTICS HEIGHT

Charts phải có height hợp lý, không kéo parent quá cao.

Desktop target:

```text
180–260px
```

Có thể dùng responsive `clamp()` nếu phù hợp.

Không để blank canvas/card height quá lớn.

---

## 29.4 OPERATIONAL LOG

Operational Log phải nằm ngay dưới analytics.

Nếu nhiều row:

```css
.operations-table-wrap {
    max-height: 180px–240px;
    overflow-y: auto;
}
```

Header sticky nếu hữu ích.

Không để card/log wrapper neo ở bottom viewport.

---

## 29.5 SIDEBAR INDEPENDENT SCROLL

Right Operator Control Room sẽ dài hơn sau khi thêm:

```text
Objective
Scenario
Simulation
Service Health
Fairness
Alerts
Map Layers
Advanced
```

Sidebar phải:

```text
scroll independently
```

và không kéo chiều cao left column.

Suggested concept:

```css
.workspace {
    grid-template-columns: minmax(0, 1fr) 300px;
    align-items: start;
}

.sidebar {
    max-height: calc(100vh - header/tabs);
    overflow-y: auto;
}
```

Không bắt buộc exact value.

---

## 29.6 DENSITY

Desktop target:

```text
main gap             8–12px
card padding        10–14px
control row gap      4–8px
segmented height    30–34px
```

Operational Log rows:

```text
~28–34px
```

Không làm panel quá thoáng.

---

## 29.7 KEEP MAP DOMINANT

Map vẫn là phần lớn nhất.

Ở 1920×1080 target khoảng:

```text
430–520px map height
```

nếu phù hợp current header/tabs.

Không hy sinh map chỉ để nhét controls.

---

## 29.8 QA AT 100% BROWSER ZOOM

Không dùng browser zoom 33% làm tiêu chuẩn.

Bắt buộc test:

```text
1920×1080 @100%
1600×900  @100%
1366×768  @100%
```

Check:

```text
no giant white gap
charts directly below map
log directly below charts
sidebar scrolls independently
map remains dominant
```

Nếu có Playwright/browser screenshot:

dùng để verify.

---

## 29.9 NO REGRESSION

Spacing fix không được làm hỏng:

- Leaflet;
- continuous playback;
- global simulation clock;
- route trails;
- Why This Driver;
- Operator scenario filters;
- Service Health;
- Fairness;
- Alerts;
- Map Layers;
- Compare;
- Replay;
- Long-Horizon.

---

# PHASE 30 — UPDATE ACCEPTANCE CRITERIA

Ngoài acceptance criteria đã có, bắt buộc thêm:

```text
- [ ] No large blank vertical gap between analytics and Operational Log.
- [ ] Operational Log directly follows analytics with ~8–14px gap.
- [ ] Main-left content is not stretched by sidebar height.
- [ ] Sidebar scrolls independently when long.
- [ ] No negative-margin layout hack.
- [ ] 1920×1080 @100% looks compact and professional.
- [ ] 1600×900 @100% looks correct.
- [ ] 1366×768 @100% is usable.
```

---

# PHASE 31 — IMPLEMENTATION ORDER CẬP NHẬT

Làm trong cùng một round theo thứ tự:

```text
1. Audit current UI/API
2. Time/day filters
3. Horizon presets
4. Fleet presets
5. Save Run / scenario summary
6. Collapsible/preset-button UX
7. Layout spacing/density root-cause fix
8. Responsive QA
9. Regression tests
10. Documentation
```

Không coi task hoàn thành nếu control mới hoạt động nhưng layout vẫn có khoảng trắng lớn.
