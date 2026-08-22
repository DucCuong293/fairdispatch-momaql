# MASTER PROMPT — PORT FRONTEND `demo_fairdispatch` VÀO FAIRDISPATCH PRODUCT HIỆN TẠI

## Mục tiêu

Tôi muốn nâng cấp **frontend của sản phẩm FairDispatch hiện tại** để có độ trực quan và cảm giác chuyên nghiệp tương đương frontend cũ `demo_fairdispatch`.

Điểm đặc biệt tôi muốn giữ từ frontend cũ là:

> **Bản đồ Leaflet thật nằm chính giữa màn hình, chiếm phần lớn không gian, có basemap thực, driver/request/route hiển thị trực tiếp trên bản đồ, control panel và KPI bố trí xung quanh.**

Hiện backend/research integration của sản phẩm mới đã tốt hơn frontend cũ rất nhiều.

Vì vậy mục tiêu KHÔNG phải quay lại demo cũ.

Mục tiêu là:

> **Frontend/visual shell của demo_fairdispatch + backend/engine/correctness của 05_SanPham_Demo hiện tại.**

Nói cách khác:

```text
demo_fairdispatch
→ lấy visual design, Leaflet map, layout, interaction pattern

05_SanPham_Demo hiện tại
→ giữ backend, API, engine adapter, replay adapter, explainability,
   Utility/Gini thật, Full vs No-Forecast, horizon, provenance,
   P0/P1 fixes, tests
```

Kết quả cuối phải là một sản phẩm **đẹp và trực quan như demo cũ nhưng dữ liệu/decision đều là thật**.

---

# 1. PATH SẢN PHẨM CẦN SỬA

Làm trực tiếp tại:

```text
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Đây là product chính.

Không tạo một product mới song song.

Không rewrite backend nếu không cần.

---

# 2. FRONTEND CŨ PHẢI DÙNG TRỰC TIẾP LÀM VISUAL REFERENCE / VISUAL SHELL

Trên máy có project/folder:

```text
demo_fairdispatch
```

Hãy search trong:

```text
D:\ProjectVSF
```

để tìm nó.

Ví dụ có thể là:

```text
D:\ProjectVSF\demo_fairdispatch
```

hoặc đường dẫn tương đương.

Đọc full:

```text
demo_fairdispatch/index.html
demo_fairdispatch/du_lieu/*
```

Không chỉ đọc lướt.

Hãy hiểu:

- layout;
- map;
- Leaflet initialization;
- basemap tile layer;
- map center/zoom;
- marker styles;
- route visualization;
- topbar;
- right-side control panel;
- trip tracker;
- KPI;
- chart sections;
- log table;
- badges;
- responsive behavior.

---

# 3. LẦN NÀY KHÔNG CHỈ “THAM KHẢO” FRONTEND CŨ

Ở vòng trước frontend cũ chỉ được tham khảo một vài pattern.

Lần này tôi muốn **port trực tiếp visual architecture của nó**.

Có thể:

- copy/adapt HTML structure;
- copy/adapt CSS;
- copy/adapt Leaflet setup;
- copy/adapt panel composition;
- copy/adapt legend;
- copy/adapt topbar;
- copy/adapt spacing;
- copy/adapt card visual;
- copy/adapt map size;
- copy/adapt trip tracker presentation;
- copy/adapt log/table presentation.

Nhưng:

> **KHÔNG copy data hoặc algorithm demo cũ.**

Frontend mới phải nhìn có cảm giác rất gần `demo_fairdispatch`, nhưng mọi state phải được nối lại với API của product mới.

---

# 4. GIỮ TOÀN BỘ BACKEND VÀ CORRECTNESS HIỆN TẠI

Trước khi thay frontend, đọc:

```text
05_SanPham_Demo/README.md
05_SanPham_Demo/PRODUCT_AUDIT.md
05_SanPham_Demo/PRODUCT_FIX_PLAN.md
05_SanPham_Demo/DEMO_SCRIPT.md
05_SanPham_Demo/backend/*
```

Đặc biệt đọc `PRODUCT_FIX_PLAN.md`.

Các fix đã làm tốt **không được regression**.

Hiện đã có các fix quan trọng như:

- actual Hungarian-selected driver trong `Why this driver?`;
- local rank vs actual selected driver;
- Auto Run sequential, không concurrent step;
- session lock;
- Reset button fix;
- requirements có numpy/scipy;
- checksum/provenance fix;
- Driver Income Distribution thật;
- assigned / declined / infeasible requests;
- deadhead line;
- busy-driver semantics;
- backend validation;
- context-aware controls;
- provenance tách engine snapshot/dev repo;
- integration tests;
- Lorenz curve thật.

Tất cả phải giữ nguyên hoặc tốt hơn.

---

# 5. ĐIỂM CẦN THAY LỚN NHẤT: SVG MAP → LEAFLET REAL MAP

Frontend hiện tại đang dùng:

```text
<svg id="mapSvg">
```

và tự project lat/lon lên một canvas trắng.

Tôi KHÔNG muốn tiếp tục kiểu này.

Thay vùng map bằng **Leaflet real map giống demo_fairdispatch**.

Ví dụ:

```html
<div id="dispatchMap"></div>
```

Initialize Leaflet tương tự frontend cũ.

Dùng đúng basemap/tile style đang hoạt động tốt trong `demo_fairdispatch`, nếu không có lý do kỹ thuật để đổi.

Mục tiêu:

> khi mở app, người dùng nhìn ngay thấy NYC trên một bản đồ địa lý thật.

Không còn cảm giác “scatter plot trong hình chữ nhật”.

---

# 6. BẢN ĐỒ PHẢI LÀ TRUNG TÂM UI

Trong Live Simulation:

> map phải là thành phần lớn nhất màn hình.

Target desktop layout gần như:

```text
┌────────────────────────────────────────────────────────────────────┐
│ FairDispatch | LIVE ENGINE | Run ID | MOMAQL | Batch | RUNNING    │
├───────────────────────────────────────────────┬────────────────────┤
│                                               │                    │
│                                               │ Scenario Controls  │
│                                               │                    │
│                                               │ KPI                │
│               LEAFLET MAP                    │                    │
│                                               │ Current Assignment │
│                                               │                    │
│                                               │ Fairness           │
│                                               │                    │
├───────────────────────────────────────────────┴────────────────────┤
│ Timeline / Income Distribution / Operational Log                  │
└────────────────────────────────────────────────────────────────────┘
```

Map nên chiếm khoảng:

> 60–70% chiều ngang phần nội dung chính

trên desktop.

Không để controls chiếm nhiều hơn map.

---

# 7. MAP PHẢI HIỂN THỊ STATE THẬT TỪ ENGINE

Dùng data thật hiện đã trả từ backend.

Show:

## Driver

- idle driver;
- busy driver;
- selected driver highlight.

## Request

- assigned;
- declined;
- infeasible.

## Route

- driver start → pickup = deadhead;
- pickup → dropoff = passenger trip.

## Marker popup / tooltip

Click/hover driver:

```text
Driver #73
Income: $287
Status: Idle / Busy
Current/Next zone: ...
Trips: ...
```

nếu field có thật.

Click pickup:

```text
Request #1842
Pickup zone
Dropoff zone
Fare
Status
```

Click assigned route/request:

> mở Assignment Explanation panel.

---

# 8. DEADHEAD VÀ PASSENGER TRIP PHẢI DỄ PHÂN BIỆT

Trên Leaflet:

```text
Driver → Pickup
```

dùng:

- dashed polyline;
- muted/gray.

```text
Pickup → Dropoff
```

dùng:

- solid polyline;
- primary/navy/blue.

Không cần quá nhiều màu.

---

# 9. ASSIGNED / DECLINED / INFEASIBLE REQUEST

Map phải làm rõ:

```text
Assigned
Declined
Infeasible
```

Ví dụ:

- Assigned pickup = green;
- Dropoff = orange;
- Declined = amber/red;
- Infeasible = gray outline.

Legend phải nhìn được ngay.

Không chỉ show assigned requests.

---

# 10. AUTO FIT / MAP CAMERA

Sau New Run:

- center NYC;
- zoom hợp lý.

Sau Step:

không zoom loạn liên tục.

Ưu tiên:

- map giữ camera ổn định;
- hoặc fit bounds nhẹ khi user chọn một assignment;
- khi click row Assignment, zoom/pan tới driver→pickup→dropoff.

Có nút:

```text
Fit Current Batch
```

nếu hữu ích.

---

# 11. FRONTEND CŨ CÓ TRIP TRACKER RẤT TỐT — HÃY DÙNG LẠI

Trong `demo_fairdispatch` có vùng theo dõi chuyến rất trực quan.

Hãy dùng style/layout đó để làm:

> **Current Assignment / Why this driver?**

Panel nên show:

```text
Request #1842

Pickup: Zone 42
Dropoff: Zone 17
Fare: $21.50

Selected Driver: #73
Pickup ETA: 180s
Current Income: $245

Immediate Utility       +18.60
Future Zone Value        +4.20
Fairness Adjustment      +1.30
Final Score              24.10

Local Candidate Rank     #2
Selected by              Hungarian Global Assignment
```

Nếu selected driver local rank != 1:

show badge:

```text
GLOBAL OPTIMUM
```

và message:

> Driver này không có local score cao nhất cho request riêng lẻ, nhưng được Hungarian chọn để tối ưu tổng score của cả batch.

Đây là signature feature.

---

# 12. CLICK TRÊN MAP VÀ CLICK TRONG TABLE PHẢI ĐỒNG BỘ

Nếu user click:

- route;
- pickup marker;
- assignment row;

thì cùng mở một assignment detail.

Nếu user chọn assignment:

- highlight selected driver;
- highlight deadhead route;
- highlight passenger route;
- dim các assignment khác nếu cần;
- map pan/fit tới assignment.

Điều này làm sản phẩm có cảm giác chuyên nghiệp.

---

# 13. TOPBAR — DÙNG PHONG CÁCH CŨ NHƯNG DATA MỚI

Frontend cũ có topbar/status rất đẹp.

Port lại.

Topbar mới nên show:

```text
FairDispatch
LIVE ENGINE / VERIFIED REPLAY

Run ID: FD-...
Policy: MOMAQL
Drivers: 200
Batch: 16
Time: 08:31
Status: RUNNING
```

Có status dot.

Không show quá nhiều text mô tả dài trong header.

---

# 14. CONTROL PANEL — PORT PHONG CÁCH CŨ

Right-side panel nên có:

## Scenario

```text
Policy
Drivers
Lambda
Forecast
Seed
Request limit
```

## Actions

```text
New Run
Step
Run
Pause
Reset
```

Button layout giống demo cũ hoặc tốt hơn.

Giữ context-aware:

- non-MOMAQL → disable lambda;
- non-MOMAQL → disable forecast.

---

# 15. KPI — GIỮ DATA HIỆN TẠI, ĐỔI VISUAL

Không thay backend.

Show KPI thật:

```text
Total Utility
Gini
Served Requests
Average Income
Average Deadhead
```

Có meaning:

```text
Gini ↓
Lower = more equal driver income
```

KPI visual có thể dùng card/chip style của demo cũ.

Không làm giant cards chiếm map.

---

# 16. DRIVER INCOME DISTRIBUTION + LORENZ

Hai feature này đã được product mới implement thật.

Giữ.

Nhưng hãy styled giống chart section của demo cũ.

Ưu tiên:

```text
Fairness Overview
├── Gini
├── Income Histogram
└── Lorenz Curve
```

Nếu cần space:

- để ở bottom panel;
- hoặc collapsible `Fairness Details`.

Không bỏ.

---

# 17. OPERATIONAL LOG — PORT TỪ DEMO CŨ

Thêm/giữ một log table ở dưới:

```text
Time
Request
Driver
Pickup Zone
Dropoff Zone
Fare
ETA
Status
```

Click row:

> select assignment trên map.

Log không cần lưu toàn bộ 195k request trên DOM.

Chỉ:

- current batch;
- recent N rows;
- pagination/limit nếu cần.

---

# 18. TABS HIỆN TẠI VẪN GIỮ

Current product có:

```text
Live Simulation
Compare Policies
Long-Horizon
Run History
```

Đây là cấu trúc tốt.

Giữ.

Nhưng tab Live phải dùng full visual shell của demo_fairdispatch.

Compare/Horizon/History có thể giữ layout hiện tại, chỉ làm visual consistent với shell mới.

---

# 19. COMPARE POLICIES

Giữ data/replay hiện tại.

Không hard-code.

Must-have:

```text
Full MOMAQL
vs
No Forecast
```

Show:

```text
Utility
Full higher (+22.4%)

Gini
No Forecast lower / more equal
```

Không badge `Winner`.

Có:

```text
VERIFIED REPLAY
```

và source CSV.

Nếu Live Quick Compare còn có:

giữ badge:

```text
LIVE ENGINE — QUICK SLICE
```

Không lẫn hai loại result.

---

# 20. LONG-HORIZON

Giữ replay artifact thật.

Upgrade visual nếu cần để gần demo cũ hơn.

Show line chart:

```text
Utility vs Day
Full
No Forecast
```

và:

```text
Gini vs Day
Full
No Forecast
```

Slider:

```text
Day 1 → 7 → 14 → 21 → 28 → 37
```

Highlight:

```text
Day 21 +5.15%
Day 28 +11.65%
Day 37 +20.19%
```

Fairness:

```text
Day 37
Full Gini ≈ 0.217
No Forecast ≈ 0.151
```

Không thay research conclusion.

---

# 21. RUN HISTORY

Giữ.

Nếu dễ:

thêm row click:

```text
Open Run
Reproduce Run
```

Nhưng đây là bonus.

Không để nó làm ảnh hưởng tới frontend map work.

---

# 22. LEAFLET DEPENDENCY

Ưu tiên dùng chính Leaflet setup đã hoạt động trong `demo_fairdispatch`.

Nếu frontend cũ dùng CDN:

có thể tiếp tục nếu buổi demo có internet.

Nhưng nên có fallback:

- app vẫn load;
- controls vẫn hoạt động;
- markers/spatial state không crash;
- show message nếu tile không tải.

Nếu dễ vendor Leaflet local:

> tốt hơn.

Không dành quá nhiều thời gian cho việc này nếu ảnh hưởng chức năng chính.

---

# 23. BASEMAP

Tôi muốn **bản đồ thật**, không muốn canvas trắng.

Dùng tile provider tương tự `demo_fairdispatch`.

Ví dụ style nhẹ/clean phù hợp dashboard.

Không dùng satellite.

Ưu tiên:

- đường phố;
- địa danh;
- NYC geography;
- màu nền nhạt để marker nổi bật.

---

# 24. KHÔNG COPY LOGIC GIẢ TỪ DEMO CŨ

Đây là absolute rule.

Frontend cũ có một số logic chỉ dùng để minh họa.

Không copy:

```javascript
qScore = 85 + trip.id % 10
```

Không copy fake Q-score.

Không copy driver ID theo reveal index.

Không copy precomputed income reveal.

Không copy old result:

```text
P2-13
S8300
Production Heuristic
MOMAQL Gini ~0.925
```

Không copy frontend animation làm source of truth.

---

# 25. FRONTEND MỚI PHẢI CHỈ DÙNG 2 SOURCE OF TRUTH

## Live Mode

```text
FastAPI
→ current engine adapter
→ actual simulator/policies
```

## Replay Mode

```text
current verified reports/*.csv/json
```

Không có source thứ ba.

---

# 26. KHÔNG REGRESSION `WHY THIS DRIVER?`

Đây là điểm cần test sau khi port frontend.

Actual winner phải lấy từ:

```text
selected_driver_id
```

do backend trả.

Không suy ra từ:

```text
candidate[0]
```

hoặc:

```text
max score
```

Frontend visual có thể giống demo cũ, nhưng logic winner phải giữ bản đã fix.

---

# 27. KHÔNG REGRESSION AUTO RUN

Port visual button từ demo cũ nếu muốn.

Nhưng logic phải giữ:

```text
sequential async Step
```

Không quay lại:

```javascript
setInterval(asyncStep, 350)
```

nếu có nguy cơ overlap.

---

# 28. KHÔNG REGRESSION HISTOGRAM / LORENZ

Histogram:

> actual driver incomes.

Lorenz:

> actual driver incomes.

Không lấy precomputed arrays từ demo cũ.

---

# 29. KHÔNG REGRESSION PROVENANCE

Footer/detail phải tiếp tục phân biệt:

```text
Engine source snapshot
Development dataset repo
Dataset checksum
Seed
Run config
```

Không dùng old demo metadata.

---

# 30. RESPONSIVE

Desktop/projector là ưu tiên số 1.

Target:

```text
1920×1080
1600×900
1366×768
```

Ở 16:9:

- map vẫn lớn;
- controls không che map;
- assignment panel không overflow;
- legend không chiếm quá nhiều.

Ở màn nhỏ:

- stack controls;
- map vẫn usable.

---

# 31. VISUAL STYLE

Tôi muốn cảm giác giống `demo_fairdispatch`:

- chuyên nghiệp;
- app/control-room;
- có real map;
- panel rõ;
- topbar rõ;
- compact;
- dữ liệu trực quan;
- không quá trắng/trống.

Nhưng không cần copy màu 100%.

Có thể giữ identity FairDispatch hiện tại.

Tránh:

- glassmorphism;
- neon;
- giant gradients;
- dark cyberpunk;
- quá nhiều shadow;
- animation trang trí.

---

# 32. REAL-TIME FEEL NHƯNG KHÔNG FAKE REAL-TIME

Có thể animate marker/route nhẹ khi state mới tới.

Nhưng:

> state phải đến từ Step API thật.

Animation chỉ là presentation layer.

Không được dùng animation để tự tạo:

- driver movement;
- trip completion;
- income;
- assignment.

---

# 33. PROGRESS / STATUS

Trong topbar/right panel:

```text
Batch 17
Consumed 840 / 3000
RUNNING
```

Có loading indicator nhỏ.

Không fake percentage nếu backend không biết.

---

# 34. MAP PERFORMANCE

Có thể có 200 driver + nhiều request markers.

Tránh recreate toàn bộ Leaflet map instance mỗi step.

Khuyến nghị:

```text
map instance persistent
LayerGroup:
- driverLayer
- requestLayer
- routeLayer
- selectionLayer
```

Mỗi step:

- clear/update layers;
- không destroy map.

Nếu performance cần:

- reuse markers;
- simplify route count;
- only show current batch.

---

# 35. LEAFLET LAYER DESIGN

Gợi ý:

```text
map
├── baseTileLayer
├── driverLayer
├── requestLayer
├── assignmentLayer
└── selectionLayer
```

Legend cùng màu.

Không nhồi tất cả vào một layer.

---

# 36. DRIVER MARKER

Không cần icon taxi hình ảnh nếu làm rối.

Có thể dùng:

- small circle marker;
- idle gray;
- busy navy;
- selected driver cyan/green outline.

Popup:

> data thật.

---

# 37. REQUEST MARKER

Pickup:

- circle marker.

Dropoff:

- diamond/circle khác.

Declined:

- X marker / red-orange.

Infeasible:

- gray hollow.

Tránh 20 loại icon.

---

# 38. ASSIGNMENT SELECTION EXPERIENCE

Khi click row/route:

1. clear previous selection;
2. highlight selected driver;
3. highlight pickup/dropoff;
4. thicken two route segments;
5. open Explain panel;
6. pan/fit map;
7. show actual selected rank/Hungarian badge.

Đây phải là một interaction rất mượt.

---

# 39. CURRENT BATCH SUMMARY

Trên map hoặc top map panel:

```text
08:31:00
12 requests
27 feasible drivers
9 assigned
2 declined
1 infeasible
```

Giống kiểu live operations dashboard.

---

# 40. RESEARCH/PRODUCT DISTINCTION

Live tab:

```text
LIVE ENGINE
```

Compare/Horizon:

```text
VERIFIED REPLAY
```

Luôn visible.

Mentor phải hiểu trong 3 giây:

> cái nào live, cái nào replay.

---

# 41. PRODUCT POSITIONING

UI title/subtitle có thể là:

```text
FairDispatch
Ride-Hailing Dispatch Control Room
```

Secondary text:

```text
Simulation & Decision-Support Prototype
```

Không cần title dài chiếm topbar.

---

# 42. PRODUCT DEMO FLOW MỤC TIÊU

Sau khi frontend port xong, demo phải chạy được như sau.

## Step 1

Mở app.

Người xem lập tức thấy:

> NYC real basemap ở giữa.

## Step 2

Chọn:

```text
MOMAQL
200 drivers
λ=0.5
Forecast ON
```

New Run.

## Step 3

Bấm Step.

Map hiện:

- drivers;
- requests;
- assignment routes.

## Step 4

Click một assignment.

Map focus route.

Right panel show:

> Why this driver?

## Step 5

Bấm thêm Step / Run.

Nhìn KPI/Fairness update.

## Step 6

Compare tab.

Show verified Full vs No Forecast.

## Step 7

Long-Horizon.

Show delayed Utility effect.

## Step 8

Run History / provenance.

Toàn demo:

> 4–6 phút.

---

# 43. DEMO PHẢI “ĐẸP NGAY KHI MỞ”

Không để first screen:

- map trắng;
- KPI toàn `--`;
- quá nhiều empty panel.

Trước khi New Run:

Map vẫn show:

> NYC basemap.

Có một empty-state overlay nhẹ:

```text
Create a simulation run to visualize dispatch decisions.
```

Nhìn vẫn như sản phẩm hoàn chỉnh.

---

# 44. SỬ DỤNG NHỮNG GÌ ĐÃ BUILD TỐT

Không bỏ:

- FastAPI server;
- current endpoints;
- engine adapter;
- replay adapter;
- tests;
- validation;
- histogram;
- Lorenz;
- compare;
- horizon;
- provenance;
- history;
- explainability;
- P0/P1 fixes.

Frontend port chỉ nên thay:

> presentation / spatial UX / interaction composition.

Backend chỉ sửa nếu frontend mới cần một field thật còn thiếu.

---

# 45. TRƯỚC KHI CODE

Tạo/Update:

```text
PRODUCT_FRONTEND_PORT_PLAN.md
```

Ghi:

```text
Current component
Old demo component to reuse
Data source
API endpoint
Port approach
Regression risk
Test
```

Ví dụ:

| Current | demo_fairdispatch | New source |
|---|---|---|
| SVG map | Leaflet map | `/simulations/{id}/step` |
| assign table | Trip Tracker | actual assignments |
| KPI cards | Topbar/KPI | actual metrics |
| histogram | old histogram visual | actual income_histogram |
| Lorenz | old chart visual | actual lorenz |
| log | old log table | current assignment history |

---

# 46. IMPLEMENTATION ORDER

Làm đúng thứ tự:

## Phase A
Read current product + old frontend.

## Phase B
Port Leaflet map only.

Verify actual data.

## Phase C
Port layout/topbar/right panel.

## Phase D
Wire assignment selection/explainability.

## Phase E
Port histogram/Lorenz/log visuals.

## Phase F
Polish Compare/Horizon/History consistency.

## Phase G
Regression tests.

Không redesign mọi thứ cùng lúc.

---

# 47. REGRESSION TESTS BẮT BUỘC

Sau khi port:

### Backend

Chạy full existing tests.

Tất cả phải pass.

### Frontend smoke test

Verify:

- app loads;
- Leaflet loads;
- NYC basemap visible;
- New Run;
- Step;
- Run;
- Pause;
- Reset;
- driver markers;
- assigned markers;
- declined markers;
- infeasible markers;
- deadhead;
- passenger route;
- assignment click;
- actual Hungarian winner;
- KPI;
- histogram;
- Lorenz;
- Compare;
- Horizon;
- History;
- provenance.

---

# 48. CHECK BUG SIGNATURE

Tạo/giữ test case:

```text
local top-score driver != Hungarian-selected driver
```

UI Explain phải đánh dấu:

> Hungarian-selected driver.

Không local top score.

---

# 49. KHÔNG ĐƯỢC HOÀN THÀNH NẾU CHỈ CÓ MAP ĐẸP

Acceptance không phải:

> “Leaflet đã lên.”

Mà là:

> **Leaflet map thật + actual engine state + actual assignment explainability + preserved research correctness.**

---

# 50. FINAL ACCEPTANCE CHECKLIST

Sản phẩm final phải đạt:

### Visual
- [ ] Real Leaflet basemap
- [ ] Map central / largest
- [ ] Professional control-room composition
- [ ] Clear legend
- [ ] Clear topbar
- [ ] Compact right panel

### Live Engine
- [ ] Actual drivers
- [ ] Actual requests
- [ ] Actual assignments
- [ ] Declined/infeasible
- [ ] Deadhead
- [ ] Passenger route
- [ ] Actual metrics

### Explainability
- [ ] Actual selected driver
- [ ] Local rank
- [ ] Hungarian selection
- [ ] MOMAQL score components
- [ ] Candidate table

### Fairness
- [ ] Gini meaning
- [ ] Income histogram
- [ ] Lorenz

### Research Replay
- [ ] Full vs No Forecast
- [ ] Long Horizon
- [ ] Source artifact shown
- [ ] LIVE vs REPLAY clear

### Reliability
- [ ] Sequential step
- [ ] Reset works
- [ ] Backend validation
- [ ] Tests pass
- [ ] No old fake demo data
- [ ] No fake Q-score
- [ ] No fake driver assignment

---

# 51. DOCUMENTATION

Update:

```text
README.md
PRODUCT_AUDIT.md
PRODUCT_FIX_PLAN.md
DEMO_SCRIPT.md
PRODUCT_FRONTEND_PORT_PLAN.md
```

README screenshot description không bắt buộc.

Nhưng phải document:

> frontend shell được port từ `demo_fairdispatch` visual design, trong khi data/decision đều được nối từ FairDispatch v3 current engine/artifacts.

---

# 52. KHI HOÀN THÀNH, TRẢ REPORT CỤ THỂ

Trả:

```text
Frontend components ported from demo_fairdispatch:
- ...

Current backend/features preserved:
- ...

Leaflet implementation:
- ...

Live engine data wired:
- ...

Explainability regression check:
- ...

Research replay:
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

Không chỉ trả `Done`.

---

# CÂU MỆNH LỆNH QUAN TRỌNG NHẤT

> **Hãy sử dụng chính visual frontend của `demo_fairdispatch` làm nền giao diện cho sản phẩm hiện tại, đặc biệt là Leaflet real map ở chính giữa màn hình. Đừng chỉ “lấy cảm hứng”. Port cấu trúc/layout/map/interaction tốt của frontend đó, nhưng loại bỏ toàn bộ logic/data minh họa cũ và nối nó với backend/engine thật của `05_SanPham_Demo`. Những gì current product đã làm đúng về correctness, explainability, replay, fairness metrics và provenance phải được giữ nguyên.**

---

# PRODUCT QUALITY TARGET

Khi mở ứng dụng, người xem phải có cảm giác:

> **“Đây là một control room ride-hailing thật sự có thể quan sát decision.”**

Sau khi click một assignment, họ phải thấy:

> **“Decision này đến từ engine thật và tôi hiểu vì sao driver này được chọn.”**

Sau khi sang Compare/Horizon, họ phải hiểu:

> **“Research result đã được biến thành một sản phẩm tương tác, chứ không chỉ là slide và biểu đồ.”**

Đó là target cuối cùng.
