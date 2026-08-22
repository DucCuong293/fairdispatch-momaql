# FairDispatch Product Hardening + Frontend Reference + Claude Code Master Prompt

## Mục đích

Tài liệu này tổng hợp:

1. Toàn bộ vấn đề cần sửa trong sản phẩm `05_SanPham_Demo` hiện tại.
2. Các cải tiến nên bổ sung để sản phẩm đạt mức demo tốt trước mentor/app engineer.
3. Phân tích frontend tham khảo `demo_fairdispatch`.
4. Những phần **được phép tham khảo** từ frontend cũ.
5. Những phần **không được phép bê sang**, vì không phải logic thật của engine hiện tại.
6. Một Master Prompt cho Claude Code để audit, sửa và hoàn thiện trực tiếp sản phẩm hiện có.

---

# PHẦN I — NGUYÊN TẮC CHUNG

Sản phẩm hiện tại đã đi đúng hướng:

> **FairDispatch — Ride-Hailing Dispatch Simulation & Decision-Support Prototype**

Không được biến nó thành:

- app Grab giả;
- customer booking app;
- driver mobile app;
- dashboard research chỉ để xem biểu đồ;
- UI đẹp nhưng số liệu hard-code;
- animation giả mô phỏng algorithm.

Giá trị trung tâm phải tiếp tục là:

> **Research engine thật → API/Application layer → Product UI → Explainable decision → Compare policies → Long-term Utility/Fairness**

Những phần hiện tại đã tốt thì **giữ lại và cải thiện**, không rewrite từ đầu nếu không cần.

---

# PHẦN II — ĐÁNH GIÁ FRONTEND THAM KHẢO `demo_fairdispatch`

Tôi đã đọc full:

```text
demo_fairdispatch/
├── index.html
└── du_lieu/
    ├── chuyen.json
    ├── nodes.json
    ├── p2_13_driver_incomes.json
    ├── p2_13_driver_incomes_by_scale.json
    ├── p2_13_real_agg_by_scale.json
    └── top_zones.json
```

`index.html` là một file rất lớn, chứa:

- CSS;
- Leaflet;
- Chart.js;
- HTML;
- JS;
- một lượng JSON inline lớn.

Frontend này có nhiều ý tưởng UX tốt nhưng **không được dùng như source of truth về algorithm**.

---

# PHẦN III — NHỮNG GÌ NÊN THAM KHẢO TỪ FRONTEND CŨ

## 1. Control-room layout

Frontend cũ dùng cấu trúc rất hợp với FairDispatch:

```text
Topbar
────────────────────────────────────

Map / Spatial View          Right Control Panel

Charts / Diagnostics

Operational Log
```

Đây là layout rất phù hợp để tham khảo.

Sản phẩm mới nên tiếp tục ưu tiên:

> **Map là vùng lớn nhất.**

Bên phải:

- status;
- controls;
- assignment detail;
- fairness/KPI.

---

## 2. Topbar KPI / status chips

Frontend cũ có các chip:

```text
Đang chạy
Đã xong
Gini MOMAQL
Gini đối chứng
Δ Gini
```

Ý tưởng tốt.

Sản phẩm mới có thể dùng topbar dạng:

```text
Run ID
Policy
Status
Current Batch / Time
Drivers
Utility
Gini
```

Nhưng số liệu phải lấy từ engine/API hiện tại.

Không copy giá trị cũ.

---

## 3. Leaflet map

Frontend cũ dùng Leaflet và map nền CARTO/OpenStreetMap.

Đây là điểm rất đáng tham khảo.

Có:

- pickup marker;
- dropoff marker;
- vehicle marker;
- route;
- location labels;
- top zones.

Sản phẩm mới nên dùng lại **cách bố trí/interaction map**, nhưng dữ liệu map phải đến từ simulation state thật.

---

## 4. Legend rõ ràng

Frontend cũ có legend:

```text
MOMAQL
Đối chứng
Điểm đón
Điểm trả
```

Sản phẩm mới nên có legend rõ hơn:

```text
Idle Driver
Busy Driver
Assigned Request
Declined Request
Infeasible Request
Pickup
Dropoff
Deadhead
Passenger Trip
```

---

## 5. Control panel bên phải

Frontend cũ bố trí tốt:

- Play;
- Next;
- Reset;
- Save;
- compare policy;
- speed;
- scale;
- time filter.

Có thể tham khảo cách nhóm control.

Sản phẩm mới không cần copy toàn bộ control.

Chỉ giữ control có ý nghĩa với engine hiện tại.

---

## 6. Trip Tracker

Frontend cũ có:

```text
Chuyến đang theo dõi

Route
Fare
Driver MOMAQL
Driver đối chứng
Distance
Time
Q-score
```

Ý tưởng này rất tốt.

Sản phẩm mới nên nâng cấp thành:

> **Assignment Explanation / Why this driver?**

Nó phải show:

```text
Request
Selected Driver
Pickup ETA
Immediate Utility
Future Zone Value
Fairness Adjustment
Final Score
Local Candidate Rank
Hungarian Selection
```

---

## 7. Histogram phân phối thu nhập

Frontend cũ đã có histogram thu nhập.

Đây là feature rất phù hợp với fairness.

Sản phẩm mới nên implement thật từ:

```text
actual driver income state
```

Không chỉ Gini.

---

## 8. Lorenz Curve

Frontend cũ có Lorenz curve.

Đây là một visualization rất phù hợp để giải thích Gini.

Không bắt buộc main view, nhưng có thể đặt trong:

```text
Fairness Details
```

hoặc:

```text
Research Replay
```

Nếu dùng, phải tính từ actual driver incomes hoặc artifact thật.

---

## 9. Cumulative chart

Frontend cũ có chart dạng:

> Hội tụ lợi thế tích lũy.

Sản phẩm mới có thể dùng ý tưởng này cho:

```text
Utility over time
Gini over time
Full vs No Forecast
```

Đặc biệt phù hợp với long-horizon result.

---

## 10. Live / Static / Reference badges

Frontend cũ dùng các badge như:

```text
LIVE
THAM CHIẾU TĨNH
TĨNH
CẢNH BÁO
OK
```

Đây là ý tưởng cực kỳ tốt.

Sản phẩm mới nên dùng badge rõ:

```text
LIVE ENGINE
REPLAY ARTIFACT
VERIFIED EXPERIMENT
ESTIMATED / NOT AVAILABLE
```

Điều này giúp phân biệt:

> cái gì đang chạy từ engine

với:

> cái gì đang đọc artifact nghiên cứu.

---

## 11. Operational log

Frontend cũ có log table theo trip.

Sản phẩm mới nên có một bảng:

```text
Time
Request
Selected Driver
Pickup ETA
Utility
Policy
Status
```

Click row:

> mở assignment explanation.

---

## 12. Responsive layout

Frontend cũ có breakpoint:

```text
< 1200px
```

và chuyển layout thành một cột.

Sản phẩm mới nên tiếp tục responsive tối thiểu cho:

- 1920×1080;
- laptop;
- projector.

---

## 13. Save snapshot

Frontend cũ có nút lưu JSON.

Sản phẩm mới có thể nâng cấp thành:

```text
Export Run
```

với:

- config.json;
- metrics.csv/json;
- assignments.csv;
- provenance.

---

# PHẦN IV — NHỮNG GÌ TUYỆT ĐỐI KHÔNG ĐƯỢC COPY TỪ FRONTEND CŨ

Đây là phần rất quan trọng.

Frontend cũ là **reference UI**, không phải reference algorithm.

---

## 1. Không copy Q-score giả

Frontend cũ có đoạn:

```javascript
const qScore = (85 + (trip.id % 10)).toFixed(1);
```

Đây không phải Q-score từ engine thật.

Không được dùng logic kiểu này trong product mới.

Q-score/future value phải lấy trực tiếp từ policy thật.

---

## 2. Không copy driver ID giả

Frontend cũ tạo driver label kiểu:

```text
MOMAQL-<index>
baseline-<index>
```

dựa trên `revealIdx`.

Đây không phải driver assignment thật từ simulator.

Product mới phải dùng:

> **actual driver_id được Hungarian chọn.**

---

## 3. Không copy animation như thể là simulation thật

Frontend cũ dùng:

```text
requestAnimationFrame
```

để animate trip từ origin → destination.

Đó là visual simulation/replay.

Product mới có thể dùng animation để minh họa, nhưng:

> state/assignment phải lấy từ backend engine thật.

Không để visual animation tự quyết định state.

---

## 4. Không copy income slicing logic

Frontend cũ có đoạn lấy income array rồi chia:

```text
realIncome = incomeArr[idx] / 40
```

để reveal dần.

Không dùng kiểu này cho Live Mode.

Live Mode phải dùng driver income thật từ simulator state.

Replay Mode có thể dùng artifact, nhưng phải ghi rõ replay.

---

## 5. Không copy dữ liệu/result cũ

Frontend cũ có các giá trị như:

```text
S8300
MOMAQL Gini ~0.925
Production Heuristic
P2-13
seed 20260721
```

Đây không phải result của FairDispatch v3 replication hiện tại.

Không được đưa vào product mới.

---

## 6. Không copy claim/alert của project cũ

Ví dụ frontend cũ có logic:

```text
MOMAQL tốt hơn đối chứng
MOMAQL kém hơn đối chứng
```

dựa trên một bộ result khác.

Product mới phải dùng đúng interpretation hiện tại:

```text
Full:
Higher Utility

No Forecast:
Better Fairness

No Fairness:
Higher inequality
```

---

## 7. Không copy Exact REASSIGN estimated result

Frontend cũ còn có cảnh báo:

```text
Exact REASSIGN:
ước tính minh họa
chưa re-run thật
```

Không dùng những số đó trong product mới.

Chỉ dùng artifact của repository hiện tại.

---

## 8. Không tiếp tục pattern một HTML 900KB chứa toàn bộ data

Frontend cũ nhúng rất nhiều JSON vào `index.html`.

Product mới đã có backend/API.

Hãy giữ architecture hiện tại:

```text
Frontend
→ API
→ Engine/Artifacts
```

Không quay lại giant inline HTML.

---

# PHẦN V — P0: CÁC LỖI PHẢI SỬA TRƯỚC DEMO

---

# P0.1 — FIX `WHY THIS DRIVER?`

Đây là lỗi quan trọng nhất.

Current product đang có nguy cơ đánh dấu:

```text
candidate score cao nhất
=
selected driver
```

Điều này sai với Hungarian global assignment.

Hungarian tối ưu toàn bộ batch.

Một request có thể nhận driver có local score rank #2 hoặc #3 để tổng score của toàn batch tốt hơn.

## Phải sửa

Backend phải lưu exact assignment thật:

```text
request_id/request_idx
→ selected_driver_id
```

`/explain` phải trả:

```json
{
  "request_id": "...",
  "selected_driver_id": "...",
  "candidates": [...]
}
```

Frontend xác định winner bằng:

```text
candidate.driver_id === selected_driver_id
```

Tuyệt đối không:

```text
i === 0
```

## Nâng cấp explainability

Nếu selected driver không có local score rank #1:

show:

```text
Selected by Global Hungarian Assignment
Local Candidate Rank: #2
```

Có thể thêm:

> Hungarian tối ưu tổng score của cả batch, không tối ưu từng request độc lập.

Đây có thể trở thành feature WOW.

---

# P0.2 — FIX AUTO RUN RACE CONDITION

Không dùng:

```javascript
setInterval(doStep, 350)
```

nếu `doStep()` async.

Phải đảm bảo:

> chỉ có một step đang chạy tại một thời điểm.

Ưu tiên:

```text
async sequential loop
```

Logic:

```javascript
while (running) {
    await doStep();
    await sleep(delay);
}
```

Có:

```text
stepInFlight
```

guard ở frontend.

Backend nên có lock per simulation session.

---

# P0.3 — FIX RESET BUTTON STATE

Sau simulation hoàn thành, Step/Run có thể bị disable.

Reset phải:

- clear state;
- clear selection;
- enable Run;
- enable Step;
- reset progress;
- reset KPI;
- reset map;
- reset assignment detail.

---

# P0.4 — FIX REQUIREMENTS

Current requirements phải chứa đủ dependency thật.

Ít nhất kiểm tra:

```text
fastapi
uvicorn
pydantic
pyarrow
numpy
scipy
```

và các package khác mà engine thực sự import.

Tốt nhất pin version đã test.

---

# P0.5 — FIX DATASET CHECKSUM / PROVENANCE KEY

Nếu JSON dùng key:

```text
"val.parquet"
```

frontend phải đọc đúng key.

Không để:

```text
SHA-256: ?...
```

Nếu checksum unavailable:

> hiển thị `Unavailable`

chứ không render dữ liệu sai.

---

# P0.6 — IMPLEMENT THẬT DRIVER INCOME DISTRIBUTION

Current product có placeholder/container cho histogram nhưng chưa render thật.

Phải implement:

```text
actual driver incomes
→ bins
→ histogram
```

Update sau mỗi step hoặc theo interval hợp lý.

Nếu chưa implement:

> không được claim feature đã có.

---

# PHẦN VI — P1: RẤT NÊN SỬA TRƯỚC PRESENTATION

---

# P1.1 — HIỂN THỊ TẤT CẢ REQUEST TRONG BATCH

Map không chỉ show assigned request.

Phải phân biệt:

```text
Assigned
Declined
Infeasible
Pending
```

Color/shape khác nhau.

Ví dụ:

```text
Assigned = green/blue
Declined = amber
Infeasible = gray/red
```

Backend trả request status đầy đủ.

---

# P1.2 — HIỂN THỊ DRIVER → PICKUP DEADHEAD

Map nên có:

```text
Driver Start
- - - - - - > Pickup
               |
               └──────> Dropoff
```

Dashed:

> deadhead.

Solid:

> passenger trip.

Backend assignment payload cần:

```text
driver_start_lat
driver_start_lon
pickup_lat
pickup_lon
dropoff_lat
dropoff_lon
pickup_eta
deadhead_miles
```

---

# P1.3 — LÀM RÕ BUSY DRIVER POSITION

Simulator có thể cập nhật driver location thành destination ngay khi trip commit.

UI không được gọi đó là:

> current physical position

nếu driver vẫn busy.

Label:

```text
Busy driver:
Planned dropoff / next available location
```

Hoặc backend lưu snapshot:

```text
decision-time location
```

---

# P1.4 — SELF-CONTAINED DEMO DATA

Hiện Live Mode phụ thuộc vào external dev repo/data path.

Nên bundle một deterministic dataset slice nhỏ:

```text
05_SanPham_Demo/
└── data/
    └── demo_val.parquet
```

Ví dụ:

> 3,000 real NYC TLC validation requests.

Flow:

```text
Full development dataset tồn tại
→ dùng full dataset

không tồn tại
→ fallback demo slice
```

UI ghi:

```text
Demo Slice — real NYC TLC data
```

Không gọi nó full validation.

---

# P1.5 — BACKEND INPUT VALIDATION

Validate:

```text
n_drivers > 0
0 <= lambda <= 1
0 <= gamma <= 1
0 < alpha <= 1
request_limit > 0
seed valid integer
supported policy
dataset exists
```

Nếu requested drivers > data available:

- reject;
- hoặc return actual initialized count.

Không để UI nói 1000 driver khi engine chỉ tạo 50.

---

# P1.6 — CONTEXT-AWARE CONTROLS

Nếu:

```text
Policy != MOMAQL
```

thì:

- disable Lambda;
- disable Forecast;
- disable Q-specific controls.

Tooltip:

> Only applicable to MOMAQL.

---

# P1.7 — FIX PROVENANCE SEMANTICS

Phải phân biệt:

```text
Engine Source Snapshot
Development Repo
Dataset Artifact
```

Nếu source engine đến từ submission bundle, đừng show Git HEAD của một repo khác như thể nó là engine commit.

Show:

```text
Engine snapshot / manifest commit
Current dev repo HEAD
Working tree clean/dirty
Dataset SHA-256
```

---

# P1.8 — THÊM PRODUCT TEST

Tối thiểu:

- backend API smoke test;
- create simulation;
- step;
- reset;
- compare;
- replay;
- explain assignment;
- selected driver correctness;
- invalid config;
- missing dataset;
- histogram output;
- provenance.

Đặc biệt unit/integration test cho:

> Hungarian actual selected driver vs explanation selected driver.

---

# P1.9 — OFFLINE DEMO RELIABILITY

Frontend tham khảo cũ phụ thuộc CDN:

```text
Google Fonts
Leaflet CDN
Chart.js CDN
CARTO tiles
```

Đối với buổi present, internet có thể không ổn định.

Sản phẩm mới nên:

- bundle Leaflet/Chart.js local nếu thực tế;
- hoặc có fallback;
- không để app trắng khi mất CDN.

Map tile có thể vẫn cần internet.

Nếu offline:

- vẫn render driver/request trên coordinate canvas/Leaflet blank layer;
- show `Basemap unavailable — spatial overlay still active`.

---

# PHẦN VII — P2: CẢI TIẾN GIÁ TRỊ CAO

---

# P2.1 — DRIVER RANKING

Show:

```text
Driver
Trips
Income
vs Fleet Mean
Status
Zone
```

Sort:

- highest income;
- lowest income;
- largest deviation.

Click:

> driver detail.

---

# P2.2 — DRIVER DETAIL / HISTORY

Show:

```text
Driver ID
Current/Next zone
Income
Trips
vs Fleet Mean
Availability
```

Nếu trace bật:

```text
Trip history
```

Không fake nếu trace không có.

---

# P2.3 — REPRODUCE RUN

Run History row click:

- load config;
- show result;
- `Re-run`.

---

# P2.4 — LONG-HORIZON LINE CHART

Không chỉ slider + cards.

Show:

```text
Utility vs Horizon
Full vs No Forecast
```

và:

```text
Gini vs Horizon
```

Slider có cursor trên chart.

Highlight:

```text
Day 7
Day 21
Day 28
Day 37
```

---

# P2.5 — LORENZ CURVE

Tham khảo frontend cũ.

Có thể đặt trong:

```text
Fairness Details
```

Input:

> current actual driver incomes.

---

# P2.6 — FAIRNESS BEFORE / AFTER ASSIGNMENT

Nếu engine state cho phép:

```text
Gini before assignment
Gini after assignment
```

Không cần gọi đó là causal fairness gain nếu score dùng metric khác.

Chỉ show:

> observed change for this batch/assignment.

---

# P2.7 — EXPORT RUN

Export:

```text
config.json
metrics.json
assignments.csv
drivers.csv
provenance.json
```

---

# P2.8 — LAMBDA SWEEP REPLAY

Research Replay:

> Lambda Sweep.

Show empirical Utility–Gini operating points.

Không cần chạy live toàn sweep.

---

# PHẦN VIII — UX / VISUAL DIRECTION

Tham khảo frontend cũ ở mức:

- topbar;
- card spacing;
- map centric layout;
- right control panel;
- badges;
- chart row;
- log table.

Nhưng không copy nguyên giao diện.

Sản phẩm mới nên sạch hơn.

## Layout đề xuất

```text
┌───────────────────────────────────────────────────────────────┐
│ FairDispatch | LIVE/REPLAY | Run ID | Policy | Time | Status │
├─────────────┬───────────────────────────────────┬─────────────┤
│ Scenario    │                                   │ KPI         │
│ Controls    │               MAP                 │             │
│             │                                   │             │
│             │                                   │             │
├─────────────┴───────────────────────────────────┴─────────────┤
│ Timeline / Compare / Fairness Distribution                    │
├───────────────────────────────────────────────────────────────┤
│ Assignment Log / Why This Driver                              │
└───────────────────────────────────────────────────────────────┘
```

---

# PHẦN IX — STATUS / BADGE SYSTEM

Dùng rõ:

```text
LIVE ENGINE
```

cho số từ active simulation.

```text
VERIFIED REPLAY
```

cho số từ research CSV/JSON.

```text
DEMO SLICE
```

cho dataset fallback.

```text
UNAVAILABLE
```

nếu dữ liệu không tồn tại.

Không hiển thị fake approximation như thật.

---

# PHẦN X — COMPARE MODE

Must-have:

```text
Full MOMAQL
vs
No Forecast
```

Show:

```text
Utility:
Full higher

Fairness:
No Forecast more equal
```

Có thể thêm:

```text
Full vs No Fairness
```

No Fairness:

> inequality tăng.

Không gọi một policy là overall winner nếu multi-objective.

---

# PHẦN XI — PRODUCT DEMO FLOW SAU KHI SỬA

## 1. Mở Control Room

Nói:

> Đây là decision-support prototype, không phải customer app.

## 2. New Run

```text
MOMAQL
200 drivers
lambda 0.5
Forecast ON
Seed 42
```

## 3. Step

Bấm 2–3 batch.

Show:

- request;
- feasible drivers;
- assignments;
- declined/infeasible;
- map update.

## 4. Why this driver?

Click request.

Show:

- actual selected driver;
- score decomposition;
- local rank;
- Hungarian global selection.

## 5. Compare

Full vs No Forecast.

Show:

- Utility;
- Gini;
- interpretation.

## 6. Long Horizon

Replay:

```text
Day 7
Day 21
Day 37
```

## 7. Fairness Distribution

Show:

- histogram;
- Lorenz nếu có.

## 8. Provenance / History

Show:

- Run ID;
- seed;
- dataset;
- engine snapshot;
- reproduce.

Tổng:

> 4–6 phút.

---

# PHẦN XII — MASTER PROMPT CHO CLAUDE CODE

## ROLE

Bạn là Senior Product Engineer + ML/Research Engineer.

Nhiệm vụ của bạn là **sửa và hoàn thiện sản phẩm FairDispatch hiện tại**, không đập đi làm lại.

Sản phẩm hiện có nhiều phần đã tốt:

- FastAPI/Application layer;
- engine adapter;
- replay adapter;
- Live Simulation;
- Research Replay;
- Control Room;
- Map/spatial view;
- KPI;
- Compare;
- Horizon;
- Run History;
- Provenance;
- Assignment explanation.

Hãy reuse tối đa những gì đã đúng.

---

# PATH SẢN PHẨM CHÍNH

Làm trực tiếp tại:

```text
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Không tạo một project mới song song trừ khi cần backup.

Trước khi sửa:

> tạo backup hoặc commit/checkpoint phù hợp.

---

# FRONTEND THAM KHẢO

Trên máy có một frontend cũ tên gần như:

```text
demo_fairdispatch
```

Hãy chủ động search trong:

```text
D:\ProjectVSF
```

để tìm directory/file này.

Có thể là:

```text
demo_fairdispatch\index.html
```

hoặc folder tương đương.

Nếu tìm thấy:

- đọc full `index.html`;
- đọc các JSON đi kèm;
- hiểu layout và interaction.

Frontend này chỉ dùng làm:

> **UI/UX reference.**

Không dùng làm:

> algorithm source.

---

# CỰC KỲ QUAN TRỌNG: FRONTEND CŨ CÓ LOGIC MINH HỌA KHÔNG ĐƯỢC COPY

Tôi đã audit frontend tham khảo và phát hiện:

### Q-score minh họa

Có logic kiểu:

```javascript
qScore = 85 + trip.id % 10
```

Không phải Q thật.

### Driver ID minh họa

Driver được label theo reveal index.

Không phải Hungarian-selected driver.

### Income reveal

Income được lấy từ precomputed array rồi reveal/chia theo logic demo.

Không phải active simulator income.

### Animated trips

Animation chạy bằng frontend/requestAnimationFrame.

Không được coi là simulation engine.

### Old result set

Có:

```text
P2-13
S8300
Production Heuristic
MOMAQL Gini ~0.925
```

không phải result hiện tại.

**TUYỆT ĐỐI KHÔNG COPY NHỮNG LOGIC/DATA NÀY.**

---

# CHỈ THAM KHẢO FRONTEND CŨ Ở CÁC KHÍA CẠNH

Có thể reuse/adapt:

- Leaflet map style;
- topbar;
- status chips;
- right control panel;
- Play/Next/Reset layout;
- trip tracker layout;
- fairness card;
- histogram;
- Lorenz curve;
- cumulative chart;
- operational log;
- live/static badges;
- responsive grid;
- map legend.

Nhưng mọi dữ liệu phải đến từ:

```text
current engine
```

hoặc:

```text
verified current research artifacts.
```

---

# PHASE 1 — AUDIT CURRENT PRODUCT

Đọc full:

```text
05_SanPham_Demo
```

bao gồm:

- README;
- PRODUCT_AUDIT;
- backend;
- frontend;
- adapters;
- tests;
- requirements;
- data path;
- replay artifacts.

Xác minh lại tất cả issue trong tài liệu này.

Tạo:

```text
PRODUCT_FIX_PLAN.md
```

với:

```text
Issue
Severity
Root cause
Files affected
Fix
Test
Status
```

Không code blind.

---

# PHASE 2 — FIX P0 TRƯỚC

Bắt buộc sửa:

## P0.1
Actual Hungarian selected driver trong Explainability.

## P0.2
Sequential Auto Run; không concurrent step.

## P0.3
Reset button state.

## P0.4
requirements/dependencies.

## P0.5
dataset checksum/provenance key.

## P0.6
Driver Income Distribution render thật.

Không chuyển sang visual polish trước khi P0 pass.

---

# PHASE 3 — FIX P1

Thực hiện nếu engine support hợp lý:

1. Assigned / declined / infeasible request on map.
2. Driver→Pickup deadhead line.
3. Busy driver state semantics.
4. Self-contained demo dataset slice.
5. Backend parameter validation.
6. Context-aware controls.
7. Correct provenance semantics.
8. Integration tests.
9. Offline fallback / vendor dependencies nếu phù hợp.

---

# PHASE 4 — FRONTEND UPGRADE

Không rewrite UI.

Hãy nâng cấp bằng các pattern tốt từ frontend cũ.

Ưu tiên:

## Topbar

Show:

```text
FairDispatch
LIVE / REPLAY
Run ID
Policy
Batch/Time
Status
```

## Map

Central and largest.

## Right Panel

```text
Scenario
Simulation Controls
KPI
Current Assignment
```

## Bottom

```text
Timeline
Income Distribution
Operational Log
```

Không làm dashboard quá chật.

---

# PHASE 5 — EXPLAINABILITY

Đây là signature feature.

Backend phải expose exact decision payload.

Ví dụ:

```json
{
  "request_id": 1842,
  "selected_driver_id": 73,
  "selected_local_rank": 2,
  "selected_by_hungarian": true,
  "request": {...},
  "selected_driver": {...},
  "components": {
    "immediate_utility": 18.6,
    "future_zone_value": 4.2,
    "fairness_adjustment": 1.3,
    "final_score": 24.1
  },
  "candidates": [...]
}
```

Payload phải khớp actual engine implementation.

Nếu formula implementation không có exact components riêng:

- refactor theo cách giữ nguyên numeric decision;
- thêm debug/explanation return;
- test score trước/sau refactor giống nhau.

---

# PHASE 6 — MAP

Nếu có lat/lon thật:

dùng Leaflet.

Show:

- idle driver;
- busy driver;
- pickup;
- dropoff;
- assigned;
- declined;
- infeasible.

Show:

```text
Driver → Pickup
```

dashed.

Show:

```text
Pickup → Dropoff
```

solid.

Nếu tile network fail:

- spatial overlay vẫn phải hoạt động.

---

# PHASE 7 — FAIRNESS UX

Implement:

## Gini

```text
Lower = more equal income
```

## Income Histogram

actual driver incomes.

## Optional Lorenz Curve

actual incomes.

## Driver Ranking

nếu đủ thời gian.

Không chỉ show raw Gini.

---

# PHASE 8 — RESEARCH REPLAY

Giữ/reuse adapter hiện tại.

Preset:

```text
Main Comparison
Ablation
Long Horizon
Fleet Sensitivity
Lambda Sweep
MLP Sensitivity
```

chỉ nếu artifact hiện tại có.

Badge:

```text
VERIFIED REPLAY
```

Không gọi live.

Long Horizon:

- line chart;
- slider;
- Full/No Forecast.

---

# PHASE 9 — RUN HISTORY / PROVENANCE

History:

```text
Run ID
Policy
Drivers
Lambda
Seed
Utility
Gini
Status
```

Thêm:

> Reproduce Run

nếu khả thi.

Provenance:

```text
Engine snapshot
Dataset
SHA-256
Seed
Config
Git status/commit where applicable
```

Không trộn engine snapshot với unrelated repo HEAD.

---

# PHASE 10 — DEMO DATA PACKAGING

Ưu tiên làm product có thể chạy ngay.

Bundle:

```text
data/demo_val.parquet
```

hoặc format phù hợp.

Lấy từ dữ liệu thật.

Không synthetic.

README ghi:

```text
Demo Slice
source
row count
checksum
```

---

# PHASE 11 — ERROR / LOADING UX

Implement:

- invalid input;
- missing dataset;
- missing model/Q-table;
- API failure;
- simulation failure;
- empty data.

Loading:

```text
Running
Current batch
Progress if known
Elapsed time
```

Không fake progress.

---

# PHASE 12 — TESTS

Bắt buộc có test cho bug quan trọng nhất:

> local best candidate != Hungarian selected driver.

Verify:

```text
Explain UI/backend marks actual Hungarian driver.
```

Thêm:

- step concurrency;
- reset;
- histogram;
- compare;
- replay;
- provenance;
- validation;
- fallback dataset.

---

# PHASE 13 — FINAL QA

Kiểm tra:

## Correctness

- no hard-coded research metric;
- no old demo data;
- no synthetic Q;
- actual selected driver;
- actual KPI.

## Live vs Replay

rõ bằng badge.

## UI

30-second test:

User biết được:

1. policy;
2. driver count;
3. current time/batch;
4. current assignment;
5. Utility;
6. Fairness meaning.

## Demo flow

chạy 4–6 phút trơn tru.

---

# DOCUMENTATION

Update:

```text
README.md
PRODUCT_AUDIT.md
PRODUCT_FIX_PLAN.md
```

Thêm:

```text
DEMO_SCRIPT.md
```

với flow:

1. open app;
2. new MOMAQL run;
3. step;
4. why driver;
5. compare;
6. horizon;
7. provenance.

---

# KHÔNG LÀM

- Không rewrite research engine.
- Không hard-code result.
- Không copy fake Q-score từ demo cũ.
- Không fake assignment.
- Không fake real-time.
- Không biến demo cũ thành backend.
- Không dùng old P2-13 result.
- Không đổi research conclusion.
- Không thêm login/payment/chatbot.
- Không over-engineer.

---

# FINAL ACCEPTANCE CRITERIA

Sản phẩm hoàn thành khi:

### Engine
- actual engine drives Live Mode.

### Explainability
- actual Hungarian selected driver correctly shown.

### Map
- driver/request/assignment truthfully visualized.

### Fairness
- Gini + distribution understandable.

### Compare
- Full vs No Forecast correct.

### Horizon
- delayed Utility effect visible from verified artifact.

### Reproducibility
- Run ID/config/provenance available.

### Reliability
- no concurrent step race;
- reset works;
- dependencies complete;
- demo works offline/fallback as much as practical.

### Documentation
- setup and demo flow reproducible.

---

# KHI HOÀN THÀNH

Trả về:

```text
P0 fixed:
- ...

P1 fixed:
- ...

Frontend reference adopted:
- ...

Frontend reference intentionally NOT adopted:
- ...

New features:
- ...

Tests:
- ...

Demo command:
- ...

Known limitations:
- ...

Files changed:
- ...
```

Không chỉ trả:

> Done.

---

# PRODUCT QUALITY TARGET

Mục tiêu không phải app đẹp nhất.

Mục tiêu là khi một app/product engineer xem demo, họ có thể nói:

> **“Đây là một research engine đã được productize đúng nghĩa: interaction là thật, decision có thể giải thích, result có nguồn gốc, live/replay được phân biệt rõ, và UI giúp tôi hiểu trade-off Utility–Fairness.”**
