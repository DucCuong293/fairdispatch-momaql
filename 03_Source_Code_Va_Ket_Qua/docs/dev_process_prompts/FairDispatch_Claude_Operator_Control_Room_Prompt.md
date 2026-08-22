# CLAUDE CODE IMPLEMENTATION PROMPT — FAIRDISPATCH OPERATOR CONTROL ROOM

Bạn là **Senior Product Engineer + Ride-Hailing Operations Engineer + Research Software Engineer**.

Nhiệm vụ của bạn là nâng cấp trực tiếp bảng điều khiển của FairDispatch hiện tại theo tài liệu đặc tả:

```text
FairDispatch_Operator_Control_Room_Requirements.md
```

HÃY ĐỌC TOÀN BỘ FILE ĐÓ TỪ ĐẦU ĐẾN CUỐI TRƯỚC KHI CODE.

---

# PROJECT PATH

Làm trực tiếp tại:

```text
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Không tạo project mới.

Không rewrite engine.

Không phá các feature hiện tại.

---

# FIRST ACTION — AUDIT

Trước khi sửa UI:

Đọc full:

```text
README.md
PRODUCT_AUDIT.md
PRODUCT_FIX_PLAN.md
PRODUCT_FRONTEND_PORT_PLAN.md
DEMO_SCRIPT.md

frontend/index.html
frontend/styles.css
frontend/app.js

backend/app.py
backend/engine_adapter.py
backend/replay_adapter.py
backend/test_engine.py
```

Xác định:

- current API contracts;
- current live state;
- current batch payload;
- driver state;
- assignment status;
- pickup ETA;
- current metrics;
- driver income;
- available/feasible drivers;
- current playback architecture;
- Live vs Replay;
- current tests.

Không invent field trước khi xác minh.

---

# CREATE IMPLEMENTATION PLAN

Tạo:

```text
OPERATOR_CONTROL_ROOM_PLAN.md
```

với bảng:

```text
Requirement
Current support
Data source
Frontend change
Backend change
Risk
Test
Status
```

---

# CORE PRINCIPLE

KHÔNG thêm feature chỉ để giao diện có nhiều nút.

Mọi Operator metric/control phải có:

> **meaning + source + action**

Ví dụ:

```text
Pickup ETA P90
→ source: actual assignment pickup_eta_seconds
→ meaning: 90% assigned requests have ETA <= value
→ action: alert if above user-defined threshold
```

---

# PHASE 1 — REORGANIZE RIGHT CONTROL PANEL

Tách UI thành:

```text
CURRENT RUN
OPERATING OBJECTIVE
SIMULATION
SERVICE HEALTH
FAIRNESS
ALERTS
MAP LAYERS
ADVANCED / RESEARCH
```

Không để tất cả field ngang hàng.

Giữ map central/largest.

---

# PHASE 2 — OPERATING OBJECTIVE

Implement:

```text
Efficiency
Balanced
Fairness
Custom
```

Mapping phải dựa vào MOMAQL lambda config thật.

Không nói mapping của project = paper.

Suggested:

```text
Efficiency → low lambda
Balanced → canonical lambda 0.5
Fairness → high lambda
Custom → user lambda
```

Nhưng audit current lambda behavior/config trước.

Không hard-code preset nếu không document.

If non-MOMAQL policy selected:

Objective control có thể:

- disable;
- hoặc label `Policy-defined`.

---

# PHASE 3 — MOVE RESEARCH PARAMS TO ADVANCED

Main Operator UI không ưu tiên:

- λ raw;
- γ;
- α;
- seed;
- request limit raw.

Move to:

```text
Advanced / Research ▸
```

Keep:

- Policy;
- Fleet;
- Forecast;
- Objective;
- Scenario.

Research controls vẫn hoạt động.

---

# PHASE 4 — SERVICE RATE

Calculate from actual batch/run state.

Show:

```text
Requests
Assigned
Declined
Infeasible
Service Rate
```

Document formula.

Example:

```text
service_rate = assigned / total_requests
```

Audit denominator semantics.

Do not accidentally count infeasible twice.

Support:

- current window;
- cumulative run if useful.

UI should say which one.

Prefer:

```text
Current Window
```

and optionally:

```text
Run Cumulative
```

---

# PHASE 5 — PICKUP ETA

From actual:

```text
pickup_eta_seconds
```

Calculate:

```text
mean
P90
worst/max
```

At minimum:

```text
Avg
P90
```

Use current batch and/or cumulative clearly labeled.

P90 implementation must be deterministic.

Add backend aggregation only if better than frontend.

Test numeric result.

---

# PHASE 6 — DEMAND / SUPPLY

Define clearly.

Suggested current-window:

```text
Demand = number of requests in window
Supply = number of feasible/available drivers
Ratio = Demand / Supply
```

If `feasible_drivers` returned only aggregated:

use that.

If unique feasible driver count is available, prefer unique count.

Do not sum candidate edges and call them driver supply.

Important.

Show:

```text
Demand
Supply
Demand/Supply Ratio
```

---

# PHASE 7 — ZONE PRESSURE / HEATMAP

If actual coordinates/zone data support:

aggregate current/recent request density.

Implement optional:

```text
Observed Demand Heatmap
```

Supply heatmap:

- idle/available driver density.

Do not label observed demand as forecast.

If forecast Q/demand is not semantically a count:

do not call Q-table `Forecast Demand Heatmap`.

---

# PHASE 8 — MAP LAYERS

Add control:

```text
Drivers
Requests
Active Routes
Recent Trails
Declined
Infeasible
Observed Demand
Supply
Income Layer
```

Only expose implemented layer.

Use existing Leaflet LayerGroup architecture.

Toggling layer must NOT modify engine state.

---

# PHASE 9 — FAIRNESS SUMMARY

Keep current Gini/histogram/Lorenz.

Add operational summary:

```text
Fleet Mean Income
Bottom 10% Avg Income
Top 10% Avg Income
Top/Bottom Ratio
```

Compute from actual driver incomes.

Handle zeros carefully.

If Bottom 10% = 0:

do not render infinite ratio as normal number.

Show:

```text
N/A / ∞
```

with explanation.

---

# PHASE 10 — FAIRNESS GUARDRAIL

User-defined:

```text
Maximum Gini
```

Default can be 0.25 ONLY as a UI operational default if clearly labeled:

> user-defined demo guardrail

Do NOT claim paper recommends 0.25.

Store client-side for current session/localStorage if convenient.

Alert:

```text
Current Gini > Max Gini
```

No automatic policy switching.

---

# PHASE 11 — SERVICE GUARDRAILS

Optional settings:

```text
Min Service Rate
Max Pickup ETA P90
Max Gini
```

Default values must be documented as demo/operator thresholds, not scientific findings.

---

# PHASE 12 — ALERT CENTER

Rule-based alerts.

At minimum:

```text
Service Rate below target
Pickup ETA P90 above target
Gini above guardrail
Demand/Supply shortage
```

Each alert:

```text
severity
title
current value
threshold
optional action
```

No AI-generated text required.

---

# PHASE 13 — CLICKABLE ALERTS

If alert relates to spatial zone:

click:

- pan/zoom to relevant location;
- enable corresponding map layer.

If no reliable zone localization:

do not fake navigation.

---

# PHASE 14 — SEARCH

Add compact search:

```text
Driver / Request
```

At minimum:

- Driver ID;
- Request ID in recent/current retained state.

Action:

- highlight marker/route;
- pan map;
- open driver/assignment detail.

If historical item expired from frontend retention:

show:

```text
Not in current playback buffer
```

not fake.

---

# PHASE 15 — FOLLOW DRIVER

If current continuous playback architecture makes it easy:

implement:

```text
Follow Driver
```

Map gently pans to selected moving marker.

Do not auto zoom continuously.

Toggle OFF returns camera control to user.

Bonus if complex; do not block P1.

---

# PHASE 16 — WHAT-IF PANEL

Reuse current Compare infrastructure.

Expose compact What-if:

```text
Current Policy
Alternative
Run Quick Compare
```

Live result:

```text
LIVE ENGINE — QUICK SLICE
```

Verified experiment:

```text
VERIFIED REPLAY
```

Do not mix.

---

# PHASE 17 — FULL VS NO FORECAST

Keep research interpretation:

```text
Full:
Higher Utility

No Forecast:
Better Fairness
```

Do not label an overall winner.

---

# PHASE 18 — FULL VS NO FAIRNESS

If artifact/endpoint already supports:

add option.

Interpretation must use actual result.

Do not assume removing fairness increases Utility.

Current research observed:

> inequality rises; Utility direction differs.

---

# PHASE 19 — SCENARIO PRESETS

Implement only presets that map to real config.

Suggested:

```text
Balanced Default
Efficiency Focus
Fairness Focus
Custom
```

`Supply Shortage` only if it maps to a real fleet-size/data scenario.

Do not synthesize demand.

---

# PHASE 20 — USER-FACING SIMULATION HORIZON

Replace primary raw:

```text
Request Limit
```

with:

```text
Quick Demo
Medium
Full Validation
Custom
```

Map to exact request_limit values.

Advanced shows raw.

If Full Validation is too slow:

show warning before start.

---

# PHASE 21 — DATA SOURCE PANEL

Show:

```text
NYC TLC 2013
Validation Split
Live Slice: X / 195,508
```

Use actual metadata.

Do not hard-code total if metadata/API already provides it.

If fallback demo dataset used:

badge:

```text
DEMO SLICE
```

---

# PHASE 22 — OPERATOR / RESEARCH VIEW

Only implement if low complexity.

Otherwise use:

```text
Advanced / Research
```

collapsible.

Do not let this feature delay critical operator KPIs.

---

# PHASE 23 — NUMERIC ALIGNMENT

All operational numbers:

```css
font-variant-numeric: tabular-nums;
```

Use label/value grids.

Right align numeric values.

Examples:

```text
Service Rate           92.4%
Pickup ETA Avg          3.8m
Pickup ETA P90          7.4m
Demand/Supply           1.3×
Gini                   0.204
```

---

# PHASE 24 — RESPONSIVE / PROJECTOR

Test:

```text
1920×1080
1600×900
1366×768
```

Map must remain dominant.

Right panel scroll independently if needed.

Do not make whole page excessively tall because of new controls.

Use collapsible sections.

---

# PHASE 25 — DO NOT REGRESS CONTINUOUS PLAYBACK

Must preserve:

- global simulation clock;
- overlapping trips across batches;
- persistent driver markers;
- speed control;
- pause/resume;
- buffer;
- active trip lifecycle;
- recent trails.

New dashboard updates should happen on visible batch activation, not engine prefetch time.

---

# PHASE 26 — DO NOT REGRESS EXPLAINABILITY

Must preserve actual:

```text
selected_driver_id
Hungarian selection
local rank
score components
```

Search/follow/map-layer work cannot break it.

---

# PHASE 27 — DO NOT TOUCH TEST SET WORKFLOW

Current product demo should continue using validation/demo validation slice by default.

Do not switch live demo to:

```text
test.parquet
```

Held-out test remains reserved for final research evaluation.

---

# PHASE 28 — NO FAKE OPERATOR ACTIONS

Do NOT add:

```text
Force assign
Manual driver override
Reposition drivers
Surge pricing
```

unless engine truly implements them.

Alerts can identify issues without pretending the prototype can resolve them.

---

# PHASE 29 — TESTS

Add tests for metric calculation.

At minimum:

## Service Rate

Known request status counts → exact rate.

## Pickup ETA

Known array → exact avg/P90.

## Demand/Supply

Correct unique driver denominator.

## Fairness Summary

Known incomes → mean/top10/bottom10.

## Guardrails

Threshold crossing → correct alert.

## Map Layer

Toggle does not mutate engine.

## Search

Correct driver/request selected.

Run all existing backend tests after changes.

Frontend syntax:

```text
node --check frontend/app.js
```

If browser automation available, smoke test.

---

# PHASE 30 — DOCUMENTATION

Update:

```text
README.md
PRODUCT_AUDIT.md
PRODUCT_FIX_PLAN.md
PRODUCT_FRONTEND_PORT_PLAN.md
DEMO_SCRIPT.md
```

Add:

```text
OPERATOR_CONTROL_ROOM_PLAN.md
```

Document:

- metric definitions;
- guardrail semantics;
- operator vs research fields;
- what is live;
- what is replay;
- what controls engine;
- what controls visualization only.

---

# DEMO FLOW AFTER UPGRADE

1. Open Control Room.
2. Show NYC live map.
3. Point to:
   - Objective = Balanced;
   - Service Rate;
   - ETA;
   - Demand/Supply;
   - Fairness Guardrail.
4. Start MOMAQL Live Run.
5. Watch continuous vehicles.
6. Show Supply Shortage alert if naturally appears.
7. Toggle Demand/Supply layer.
8. Search/follow a driver if available.
9. Click moving assignment → Why This Driver.
10. Show alert/guardrail state.
11. Quick What-if Full vs No Forecast.
12. Verified Long-Horizon.
13. Advanced/Research → show λ/seed/provenance briefly.

---

# PRIORITY — DO NOT OVERBUILD

Mandatory first:

```text
1. Objective Presets
2. Service Rate
3. Pickup ETA Avg/P90
4. Demand/Supply
5. Map Layers
6. Fairness Guardrail
7. Alert Center
8. Search Driver/Request
```

Follow Driver can be next.

Do not implement all bonus features before the mandatory eight are correct.

---

# ACCEPTANCE TEST — 30 SECONDS

After looking at the dashboard for 30 seconds, an app/operations expert must be able to answer:

1. Which policy is running?
2. What operating objective is selected?
3. How many drivers are available/active?
4. How many trips are active?
5. What is the service rate?
6. What is the pickup ETA?
7. Is demand exceeding supply?
8. What is current Utility?
9. Is Fairness outside the guardrail?
10. What alert needs attention?

If not:

> simplify / reorganize UI.

---

# ABSOLUTE RULES

Do not:

- hard-code operational metric values;
- invent production capabilities;
- use test set for demo;
- change research conclusions;
- alter simulator policy behavior;
- add AI chatbot;
- add login/payment;
- rewrite current working architecture;
- remove research provenance.

---

# FINAL PRODUCT TARGET

A viewer should say:

> **“This is no longer just a research simulation dashboard. It looks and behaves like an operator decision-support control room: I can see service health, supply pressure, pickup wait time, fairness guardrails, alerts, and still drill down into the exact dispatch decision and research provenance.”**

---

# WHEN FINISHED

Return a detailed report:

```text
Operator controls implemented:
- ...

New metrics:
- ...

Metric definitions:
- ...

Guardrails:
- ...

Alerts:
- ...

Map layers:
- ...

Search/follow:
- ...

Research controls moved to Advanced:
- ...

Backend changes:
- ...

Frontend changes:
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
