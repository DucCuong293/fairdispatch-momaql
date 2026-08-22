# MASTER FIX PROMPT — FairDispatch Live Playback, UI Alignment, Toggle Explainability, Quick Compare 500

## Bối cảnh

Hãy tiếp tục sửa **product hiện tại**, KHÔNG tạo project mới và KHÔNG rewrite những phần đang chạy tốt.

Product path:

```text
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Frontend tham khảo đã có trên máy:

```text
demo_fairdispatch
```

Hãy tiếp tục dùng visual/interaction của `demo_fairdispatch` làm chuẩn, đặc biệt:

- cảm giác xe chạy trên Leaflet map;
- theo dõi tài xế từ vị trí hiện tại → pickup → dropoff;
- điều chỉnh tốc độ;
- control-room UI;
- map ở giữa là trung tâm;
- chuyển động mượt thay vì redraw/nhấp nháy.

Nhưng tuyệt đối giữ rule:

> **Visual animation chỉ là presentation layer. Assignment, driver ID, fare, ETA, pickup/dropoff, Utility, Gini và mọi quyết định phải đến từ engine/API thật.**

Không copy fake Q-score, fake driver ID, precomputed old result hoặc logic demo cũ.

---

# 0. ĐỌC CURRENT CODE TRƯỚC KHI SỬA

Đọc kỹ:

```text
05_SanPham_Demo/frontend/index.html
05_SanPham_Demo/frontend/styles.css
05_SanPham_Demo/frontend/app.js

05_SanPham_Demo/backend/app.py
05_SanPham_Demo/backend/engine_adapter.py
05_SanPham_Demo/backend/test_engine.py

05_SanPham_Demo/PRODUCT_FIX_PLAN.md
05_SanPham_Demo/PRODUCT_FRONTEND_PORT_PLAN.md
05_SanPham_Demo/README.md
```

Đồng thời đọc lại:

```text
demo_fairdispatch/index.html
```

để hiểu chính xác cách frontend cũ tạo cảm giác playback mượt.

Không làm mất các fix đã hoàn thành:

- actual Hungarian winner;
- sequential step;
- backend session lock;
- reset fix;
- validation;
- histogram thật;
- Lorenz thật;
- declined/infeasible request;
- deadhead route;
- provenance;
- context-aware controls;
- tests hiện tại.

---

# 1. VẤN ĐỀ LỚN NHẤT — LIVE MAP HIỆN ĐANG “NHẤP NHÁY”, KHÔNG CÓ CẢM GIÁC XE ĐANG CHẠY

## Root cause hiện tại

Trong `frontend/app.js`, `renderMap(r)` hiện đang làm gần như:

```javascript
Object.values(mapLayers).forEach(function (lg) {
    lg.clearLayers();
});
```

sau đó tạo lại toàn bộ:

- driver markers;
- request markers;
- route lines;

ở mỗi Step.

Vì vậy mỗi batch nhìn giống:

```text
state cũ biến mất
→ state mới xuất hiện
→ marker nhảy vị trí
```

chứ không phải:

```text
driver di chuyển
→ tới pickup
→ đón khách
→ đi tới dropoff
```

Đây chính là lý do UI hiện trông “nhấp nháy”.

## Yêu cầu

Hãy thay cơ chế này bằng một **persistent visual playback layer**.

Không destroy/recreate toàn bộ map state mỗi Step.

---

# 2. PHẢI CÓ CHUYỂN ĐỘNG DRIVER GIỐNG `demo_fairdispatch`

Khi backend trả về một assignment thật:

```text
Driver start
Pickup
Dropoff
Pickup ETA
Trip duration
```

hãy animate marker của tài xế theo:

```text
Driver start
    ↓
Pickup
    ↓
Dropoff
```

### Phase 1 — Deadhead

```text
Driver → Pickup
```

- marker xe chạy dọc tuyến;
- deadhead line dashed;
- có thể dùng màu muted/gray.

### Phase 2 — Passenger Trip

```text
Pickup → Dropoff
```

- marker tiếp tục chạy;
- passenger route solid;
- màu primary/navy.

Khi tới Pickup:

- pickup marker có feedback nhỏ;
- có thể đổi state thành `Passenger onboard`.

Khi tới Dropoff:

- kết thúc animation;
- marker nằm ở destination;
- trip được đánh dấu completed về mặt visual playback.

---

# 3. BACKEND CẦN TRẢ `duration_seconds` CHO ASSIGNMENT

Current `engine_adapter.step()` đã đọc:

```text
duration_seconds
```

từ parquet nhưng `assigned_out` hiện chưa expose field này.

Hãy thêm vào payload thật:

```python
assigned_out.append({
    ...
    "pickup_eta_seconds": eta,
    "duration_seconds": req["duration_seconds"],
})
```

Không thay đổi simulator decision.

Chỉ expose field đã tồn tại để frontend dùng cho playback timing.

Nếu cần thêm:

```text
window_start_seconds
```

đã có rồi, reuse.

---

# 4. ANIMATION KHÔNG ĐƯỢC FAKE STATE

Điều rất quan trọng:

> Engine vẫn là source of truth.

Animation chỉ interpolate giữa các tọa độ thật:

```text
driver_start_lat/lon
pickup_lat/lon
dropoff_lat/lon
```

Không được để animation tự:

- chọn driver;
- thay đổi income;
- hoàn thành request trong backend;
- tính fare;
- tính Q;
- quyết định assignment.

Backend đã commit state thật.

Frontend chỉ đang **phát lại trực quan quyết định thật**.

Có thể ghi nhỏ:

```text
VISUAL PLAYBACK — compressed simulation time
```

để không gây hiểu nhầm là GPS realtime.

---

# 5. PHẢI CÓ SPEED CONTROL

Thêm control rõ ràng giống demo cũ:

```text
Playback Speed
[0.5×] [1×] [2×] [4×] [8×]
```

hoặc slider/select:

```text
0.5×
1×
2×
4×
8×
```

Default:

```text
1×
```

### Ý nghĩa

Đây là **playback speed**, không phải thay đổi physics/engine time.

Ví dụ ở 1×:

- một batch playback khoảng 2–3 giây;
- các trip dài/ngắn giữ tỷ lệ tương đối trong cùng assignment nhưng cần clamp để demo không quá chậm.

Có thể tính:

```javascript
totalRealSeconds = pickup_eta_seconds + duration_seconds
```

sau đó compress vào animation duration.

Ví dụ:

```javascript
basePlaybackMs = clamp(totalRealSeconds * SCALE, 800, 5000)
animationMs = basePlaybackMs / speedMultiplier
```

Không nhất thiết dùng đúng công thức này, nhưng:

- ETA/trip duration thật phải ảnh hưởng tương đối;
- không để trip 30 phút chạy animation 30 phút.

---

# 6. AUTO RUN PHẢI CHỜ VISUAL PLAYBACK, KHÔNG FETCH BATCH MỚI LIÊN TỤC

Current Auto Run đã sửa race bằng sequential:

```javascript
while (running) {
    await doStep();
    await sleep(...);
}
```

Giữ nguyên nguyên tắc này.

Upgrade thành:

```javascript
while (running) {
    const result = await doStep({ auto: true });

    await playBatchAnimations(result, playbackSpeed);

    if (result.done || !running) break;

    await shortGap();
}
```

Tức:

```text
fetch real Step
→ render request state
→ animate actual assignments
→ hoàn thành playback
→ mới fetch Step tiếp
```

Không được quay lại `setInterval` tạo overlap.

---

# 7. MANUAL STEP CŨNG NÊN PLAY ANIMATION

Khi user bấm:

```text
Step
```

flow:

```text
POST /step
→ nhận result
→ animate batch
→ kết thúc
```

Trong lúc animation:

- disable Step tạm thời;
- không cho double click tạo 2 step;
- Pause/Reset phải xử lý an toàn.

---

# 8. PAUSE VÀ SPEED

## Pause

Nếu user bấm Pause khi Auto Run:

tối thiểu:

- không fetch batch mới.

Nếu dễ implement tốt:

- pause visual animation tại vị trí hiện tại;
- Resume tiếp tục.

Nếu pause animation phức tạp:

- cho current animation hoàn thành;
- sau đó dừng trước batch kế tiếp.

Nhưng UI phải rõ.

## Speed

Thay đổi speed phải áp dụng cho batch tiếp theo hoặc animation đang chạy nếu implementation support an toàn.

Không cần over-engineer.

---

# 9. DÙNG PERSISTENT DRIVER MARKERS

Hiện driver markers được tạo lại mỗi step.

Hãy dùng map:

```javascript
driverMarkers = new Map();
```

key:

```text
driver_id
```

Nếu driver đã tồn tại:

```javascript
marker.setLatLng(...)
```

hoặc animate từ lat/lon cũ tới lat/lon mới.

Nếu driver mới:

```javascript
create marker
```

Nếu không còn cần:

remove có kiểm soát.

Không clear toàn bộ `driverLayer` mỗi Step.

Đây là một phần quan trọng để hết flicker.

---

# 10. REQUEST/ROUTE LAYER CÓ THỂ ĐƯỢC QUẢN LÝ THEO BATCH

Không cần giữ tất cả request lịch sử trên map.

Có thể:

- giữ driver markers persistent;
- current-batch request/route layer thay mới;
- nhưng transition phải mượt, không trắng map.

Flow:

```text
old request routes fade/clear
drivers remain
new request markers appear
assignments animate
```

Không clear basemap/driver layer.

---

# 11. NẾU NHIỀU ASSIGNMENT CÙNG BATCH

Không animate nối tiếp từng xe một nếu làm batch kéo dài quá lâu.

Hãy animate các assignment trong batch **đồng thời**, giống hệ thống vận hành.

Ví dụ:

```javascript
await Promise.all(
    assignments.map(a => animateAssignment(a))
)
```

Có thể giới hạn số route được nhấn mạnh để performance ổn.

Các driver không được assignment:

> đứng yên.

---

# 12. MAP SELECTION KHÔNG ĐƯỢC XUNG ĐỘT VỚI ANIMATION

Nếu user click một route trong lúc playback:

- highlight assignment đó;
- không phá animation;
- mở `Why this driver?`.

Selected route có thể:

- thick hơn;
- selected driver marker lớn hơn;
- other routes giảm opacity.

---

# 13. `WHY THIS DRIVER?` PHẢI TOGGLE ĐƯỢC

Hiện tại:

```javascript
selectAssignment(reqIdx)
```

luôn mở selection.

User click lại cùng row/marker thì panel vẫn kẹt.

## Yêu cầu chính xác

Nếu:

```javascript
selectedReqIdx === reqIdx
```

và user click lại cùng assignment:

> đóng selection.

Implement dạng:

```javascript
async function toggleAssignment(reqIdx) {
    if (selectedReqIdx === reqIdx) {
        clearAssignmentSelection();
        return;
    }

    await selectAssignment(reqIdx);
}
```

Mọi nguồn click phải dùng chung:

```text
table row
pickup marker
dropoff marker
route
```

---

# 14. `clearAssignmentSelection()` PHẢI RESET ĐỦ

Khi đóng Why this driver:

```text
selectedReqIdx = null
```

- bỏ row `.selected`;
- clear selection layer;
- restore route opacity/weight;
- restore driver marker style;
- hide `trackerBody`;
- show `trackerEmpty`;
- không reset simulation;
- không clear current batch.

Có thể thêm nút:

```text
×
```

ở góc `Why this driver?`.

User có 3 cách đóng:

1. click lại assignment;
2. click nút ×;
3. nhấn Escape.

Nếu click vùng trống map, có thể đóng luôn nếu dễ.

---

# 15. OPERATIONAL TABLE `REQ / DRIVER / FARE / PICKUP ZONE / DROPOFF ZONE` ĐANG QUÁ GIÃN

Hiện CSS có:

```css
table.rows {
    width: 100%;
}
```

nên 5 cột bị kéo giãn toàn bộ chiều rộng rất lớn.

User không muốn vậy.

## Yêu cầu

Bảng phải:

- compact;
- các cột nằm gần nhau;
- dễ scan;
- không kéo cột Pickup/Dropoff cách nhau hàng trăm pixel không cần thiết.

### Gợi ý

Dùng `colgroup`:

```html
<colgroup>
  <col class="col-req">
  <col class="col-driver">
  <col class="col-fare">
  <col class="col-pickup">
  <col class="col-dropoff">
</colgroup>
```

Ví dụ width:

```text
Req          80px
Driver       115px
Fare         90px
Pickup Zone  115px
Dropoff Zone 120px
```

hoặc width phù hợp nội dung thực tế.

Table:

```css
#assignTable {
    width: auto;
    min-width: 540px;
    table-layout: fixed;
}
```

Không cần stretch 100%.

Container có thể rộng, nhưng table compact và left-aligned.

---

# 16. HEADER VÀ VALUE PHẢI GÓNG THẲNG CỘT

Đây là yêu cầu riêng.

Không để:

```text
FARE header
      $14.50 value
```

lệch hệ alignment.

Dùng nhất quán:

### Text columns

```text
Req
Driver
Pickup Zone
Dropoff Zone
```

left-aligned.

### Numeric

```text
Fare
```

right-aligned cả header và cells.

Ví dụ:

```css
#assignTable th.num,
#assignTable td.num {
    text-align: right;
}
```

Dùng:

```css
font-variant-numeric: tabular-nums;
```

cho:

- fare;
- utility;
- gini;
- income;
- ETA;
- KPI values;
- compare table;
- history table.

---

# 17. GÓNG KPI VALUE THẲNG HÀNG

Trong right panel, các KPI hiện nhìn hơi rời rạc.

Hãy bố trí mỗi KPI row:

```text
Total Utility             $1234.50
Served requests                 12
Avg driver income           $45.20
Avg deadhead cost/trip       $0.31
```

tức:

```css
.kpi-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 110px;
    align-items: baseline;
}
.kpi-value {
    text-align: right;
    font-variant-numeric: tabular-nums;
}
```

Nếu giữ Gini gauge ở trên thì các KPI dưới gauge phải vẫn thẳng value column.

Không để mỗi con số nằm vị trí ngang khác nhau.

---

# 18. GÓNG CỘT Ở COMPARE VÀ HISTORY

Kiểm tra luôn:

- Compare result;
- Run History;
- candidate list trong Why this driver.

Mọi numeric value nên:

```text
right aligned
tabular nums
```

Mọi label:

```text
left aligned
```

Tránh visual “lệch cột”.

---

# 19. FIX HTTP 500 — LIVE QUICK COMPARE

Tôi đã audit current `backend/app.py`.

Root cause rất có khả năng chính là đoạn hiện tại:

```python
for label, forecast_on in (("full", True), ("no_forecast", False)):
    ...

    class _Body:
        dataset = body.dataset
        n_drivers = body.n_drivers
        ...
        forecast_on = forecast_on
```

Trong Python, assignment:

```python
forecast_on = forecast_on
```

bên trong class body có thể gây:

```text
NameError: name 'forecast_on' is not defined
```

do class-body name binding.

Exception này hiện không được chuyển thành response có kiểm soát, nên frontend nhận:

```text
HTTP 500
```

## Fix đúng root cause

KHÔNG dùng dynamic inner class kiểu trên.

Dùng object explicit.

Ví dụ:

```python
from types import SimpleNamespace

params = SimpleNamespace(
    dataset=body.dataset,
    n_drivers=body.n_drivers,
    seed=body.seed,
    policy="MOMAQL",
    lam=body.lam,
    gamma=body.gamma,
    alpha=body.alpha,
    forecast_on=forecast_on,
    request_limit=body.request_limit,
)

sess = _build_session_or_400(run_id, params)
```

Hoặc refactor `_build_session_or_400` nhận một Pydantic/internal config object thật.

Ưu tiên clean typed solution nếu không tốn nhiều code.

Không chỉ catch exception để giấu bug.

---

# 20. TEST BẮT BUỘC CHO `/compare/live`

Sau khi fix, thêm test HTTP thật qua FastAPI TestClient.

Ví dụ request nhỏ để test nhanh:

```json
{
  "dataset": "val",
  "n_drivers": 10,
  "seed": 20260721,
  "lam": 0.5,
  "gamma": 0.9,
  "alpha": 0.1,
  "request_limit": 50
}
```

Expect:

```text
HTTP 200
```

Response phải có:

```json
{
  "results": {
    "full": {
      "utility": ...,
      "gini": ...,
      "served": ...
    },
    "no_forecast": {
      ...
    }
  }
}
```

Test:

```text
full
no_forecast
utility finite
gini 0..1
served >= 0
```

Nếu full dataset path không có trong isolated test:

- mock/build deterministic tiny real-format request set theo pattern tests hiện tại;
- hoặc reuse test fixture đã có.

Nhưng endpoint contract phải được test.

---

# 21. QUICK COMPARE PHẢI CÓ LOADING STATE TỐT

Khi user bấm:

```text
Run Live Quick Compare
```

button:

```text
disabled
```

show:

```text
Running Full...
Running No Forecast...
```

Nếu backend không expose intermediate progress thì không fake percentage.

Có spinner + elapsed time là đủ.

Nếu fail:

show:

```text
Live Quick Compare failed
<backend detail>
```

Không chỉ:

```text
HTTP 500
```

Nếu response có `detail`, frontend phải display detail.

---

# 22. BACKEND ERROR RESPONSE CHO QUICK COMPARE

Wrap lỗi bất ngờ ở endpoint ở mức phù hợp để log server-side.

Ví dụ:

- known config/data error → HTTP 400/404;
- unexpected internal error → log traceback và HTTP 500 có message ngắn.

Không swallow stack trace trong development.

Trong UI không show Python traceback dài.

---

# 23. SPEED CONTROL VISUAL STYLE

Đặt ngay gần:

```text
Run
Pause
Step
Reset
```

Ví dụ:

```text
Playback
0.5×  1×  2×  4×
```

hoặc:

```text
Speed [ 1× ▼ ]
```

Không đặt trong Advanced nếu user cần demo thường xuyên.

---

# 24. CURRENT BATCH STATUS TRONG LÚC ANIMATE

Show:

```text
08:31:00
12 requests arrived
9 assigned
2 declined
1 infeasible

Playback: 1×
```

Trong khi driver chạy:

```text
Driver #73 → Pickup
```

sau đó:

```text
Driver #73 → Dropoff
```

Nếu nhiều xe chạy cùng lúc:

không cần status từng xe ở topbar.

Chỉ assignment selected mới show detail.

---

# 25. KHÔNG ANIMATE 200 DRIVER VÔ NGHĨA

Chỉ animate driver có assignment trong current batch.

Idle driver:

> giữ marker cố định.

Busy driver đã được assignment trước nhưng không có visual trace trung gian từ engine:

> không invent continuous GPS path qua nhiều batch.

Chỉ animate exact assignment payload của batch mới.

---

# 26. PLAYBACK VÀ ENGINE STATE PHẢI TÁCH RIÊNG

Nên có:

```javascript
engineState
visualState
```

hoặc concept tương đương.

Engine result có thể đã ở post-commit state.

Visual playback dùng snapshot:

```text
driver_start
pickup
dropoff
```

sau khi animation hoàn thành:

```text
visual marker = engine destination state
```

Điều này tránh driver marker “teleport” trước khi animation chạy.

---

# 27. ĐỪNG GỌI ĐÂY LÀ REAL-TIME GPS

UI nên dùng:

```text
Simulation Playback
```

hoặc:

```text
Visual Playback
```

Không:

```text
Real-time vehicle tracking
```

vì simulator không mô hình continuous GPS road movement.

Basemap là thật, assignment data là thật từ simulator, còn path interpolation là visualization.

---

# 28. LEAFLET PATH KHÔNG CẦN ROAD ROUTING GIẢ

Current endpoints là lat/lon.

Nếu không có road-routing engine:

- animate theo straight Leaflet polyline giữa real coordinates;
- không invent street route.

Có thể sau này bonus dùng OSRM nếu cần, nhưng KHÔNG thêm dependency/network complexity ở vòng fix này.

---

# 29. TABLE CLICK TOGGLE PHẢI HOẠT ĐỘNG CẢ KHI ANIMATION XONG

Test:

```text
click Req #42
→ Why this driver mở

click Req #42 lần nữa
→ đóng

click Req #43
→ #42 bỏ selected
→ #43 mở

click X
→ đóng

press Escape
→ đóng
```

Map selection cũng clear chính xác.

---

# 30. MAP CLICK TOGGLE CŨNG GIỐNG TABLE

Click route #42:

> mở.

Click lại same route:

> đóng.

Không để table và map có hai state selection khác nhau.

Dùng một function:

```text
toggleAssignmentSelection(reqIdx)
```

cho cả hai.

---

# 31. KHI BATCH MỚI TỚI, XỬ LÝ WHY THIS DRIVER

Nếu đang selected Req #42 mà Auto Run sang batch mới:

- clear previous selection trước khi render/play batch mới;
- panel trở về empty state.

Không để Why this driver giữ data cũ nhưng map đã sang batch mới.

---

# 32. CSS CHO OPERATIONAL LOG

Mục tiêu:

- compact;
- không chiếm quá nhiều height;
- bảng nằm sát nhau;
- row khoảng 28–32px;
- dễ click.

Ví dụ:

```css
.logwrap-inner {
    overflow: auto;
}

#assignTable {
    width: max-content;
    min-width: 560px;
    border-collapse: collapse;
}

#assignTable th,
#assignTable td {
    white-space: nowrap;
    padding: 6px 10px;
}
```

Không bắt buộc dùng đúng số này nhưng đạt đúng visual target.

---

# 33. TEST VISUAL ALIGNMENT Ở 1920×1080 VÀ 1366×768

Đặc biệt screenshot user hiện tại cho thấy layout rộng.

Kiểm tra:

### 1920×1080
- bảng không stretch vô nghĩa;
- right KPI values aligned;
- Why this driver không quá to;
- map vẫn dominant.

### 1366×768
- bảng không overflow phá layout;
- nếu cần horizontal scroll chỉ ở log card;
- right panel usable.

---

# 34. KHÔNG ĐƯỢC LÀM REGRESSION NHỮNG THỨ ĐÃ TỐT

Sau fix phải giữ:

- Leaflet basemap;
- assigned/declined/infeasible marker;
- actual Hungarian selected driver;
- deadhead vs passenger lines;
- income histogram;
- Lorenz;
- compare verified replay;
- long horizon;
- provenance;
- backend validation;
- session lock;
- sequential Auto Run;
- context-aware controls.

---

# 35. IMPLEMENTATION ORDER

Làm theo thứ tự:

## Phase 1 — Quick Compare 500
Fix root cause + test endpoint.

## Phase 2 — Selection toggle
Why this driver toggle + X + Escape.

## Phase 3 — Compact/aligned tables & KPI
Fix operational log width/columns and numeric alignment.

## Phase 4 — Playback architecture
Persistent driver markers + animation queue.

## Phase 5 — Speed control
0.5×/1×/2×/4×/8×.

## Phase 6 — Auto Run integration
Step → animate → next Step.

## Phase 7 — Regression QA
All current tests + new tests + frontend syntax/smoke.

Không bắt đầu bằng cosmetic animation rồi để Quick Compare vẫn HTTP500.

---

# 36. UPDATE DOCUMENTATION

Update:

```text
PRODUCT_FIX_PLAN.md
PRODUCT_FRONTEND_PORT_PLAN.md
README.md
DEMO_SCRIPT.md
```

Ghi rõ:

### Visual Playback

> Driver animation interpolates between actual engine assignment coordinates. It is compressed visual playback, not GPS/road simulation.

### Speed

> Playback speed only affects visualization, not dispatch decisions or engine timing.

### Quick Compare

> Live Quick Compare bug root cause và fix.

---

# 37. DEMO SCRIPT MỚI

Update demo flow:

1. Open app — NYC basemap visible.
2. New MOMAQL run.
3. Set Playback Speed = 1×.
4. Run.
5. Watch multiple assigned drivers move:
   - start → pickup;
   - pickup → dropoff.
6. Change speed to 2×/4×.
7. Pause.
8. Click assignment.
9. Show Why this driver.
10. Click same assignment again → close.
11. Show compact Operational Log.
12. Compare tab.
13. Run Live Quick Compare successfully (no HTTP500).
14. Show Verified Replay.
15. Long Horizon.
16. Provenance.

---

# 38. ACCEPTANCE CRITERIA

## Playback
- [ ] Driver markers no longer teleport/flicker every batch.
- [ ] Assigned drivers visibly move start→pickup→dropoff.
- [ ] Multiple assignments animate concurrently.
- [ ] Animation uses actual engine coordinates.
- [ ] Speed control works.
- [ ] Auto Run waits appropriately for playback.
- [ ] No step concurrency regression.

## Why this driver
- [ ] Click opens.
- [ ] Click same assignment again closes.
- [ ] X closes.
- [ ] Escape closes.
- [ ] Map/table selection stay synchronized.
- [ ] Actual Hungarian winner remains correct.

## Operational log
- [ ] Columns compact.
- [ ] Req/Driver/Fare/Pickup/Dropoff close together.
- [ ] Header and data align exactly.
- [ ] Numeric columns right aligned.
- [ ] Tabular numbers used.

## KPI/values
- [ ] KPI values visually align in one value column.
- [ ] Numeric formatting consistent.

## Live Quick Compare
- [ ] `/compare/live` returns HTTP 200.
- [ ] No class-scope `forecast_on = forecast_on` bug.
- [ ] Test covers endpoint.
- [ ] Frontend shows real result.
- [ ] Failure message includes meaningful backend detail.

## Regression
- [ ] Existing backend tests pass.
- [ ] New tests pass.
- [ ] `node --check frontend/app.js` passes.
- [ ] Leaflet remains functional.
- [ ] Replay Compare/Horizon remain correct.
- [ ] No hard-coded research result introduced.

---

# 39. KHI HOÀN THÀNH TRẢ REPORT

Trả rõ:

```text
1. Playback changes
- ...

2. Speed control
- ...

3. Why this driver toggle
- ...

4. Operational table alignment
- ...

5. KPI/value alignment
- ...

6. Live Quick Compare HTTP500
Root cause:
...
Fix:
...
Test:
...

7. Regression tests
- ...

8. Files changed
- ...

9. Run command
- ...

10. Known limitations
- ...
```

Không chỉ trả `Done`.

---

# CÂU MỆNH LỆNH CUỐI

> **Hãy biến Live Simulation từ kiểu “mỗi Step redraw một trạng thái mới” thành một visual playback mượt giống `demo_fairdispatch`: tài xế thật do Hungarian chọn phải chạy trên Leaflet từ vị trí xuất phát đến pickup rồi đến dropoff, có điều chỉnh tốc độ. Tuy nhiên animation chỉ là lớp hiển thị của assignment thật và tuyệt đối không được tự tạo state. Đồng thời fix triệt để HTTP500 của Live Quick Compare, làm Operational Log compact/gióng cột, và cho phép `Why this driver?` toggle đóng/mở khi click lại cùng assignment.**
