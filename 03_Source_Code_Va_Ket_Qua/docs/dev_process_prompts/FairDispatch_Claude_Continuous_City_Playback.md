# MASTER PROMPT — CONTINUOUS CITY PLAYBACK FOR FAIRDISPATCH
## Mục tiêu: biến animation theo-batch hiện tại thành một dòng vận hành liên tục giống demo_fairdispatch

---

# 0. BỐI CẢNH

Product path:

```text
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Đây là sản phẩm hiện tại đã gần hoàn thiện.

KHÔNG tạo project mới.

KHÔNG rewrite backend/research engine nếu không cần.

KHÔNG làm mất các fix correctness hiện có.

Tôi muốn tập trung gần như hoàn toàn vào:

> **Live Simulation Playback**

để khi bấm Run, người xem có cảm giác:

> **một hệ thống ride-hailing đang vận hành liên tục trên bản đồ NYC**

chứ không phải:

> batch xuất hiện → tất cả xe chạy → tất cả dừng → batch mới xuất hiện.

---

# 1. ĐỌC CURRENT IMPLEMENTATION TRƯỚC

Đọc full:

```text
frontend/app.js
frontend/index.html
frontend/styles.css
backend/engine_adapter.py
backend/app.py
PRODUCT_FIX_PLAN.md
PRODUCT_FRONTEND_PORT_PLAN.md
README.md
```

Đặc biệt đọc đoạn:

```javascript
animateDriverAlong()
playBatchAnimations()
doStep()
renderStep()
```

Current code hiện có:

```javascript
var jobs = r.assignments.map(...);
await Promise.all(jobs);
```

và:

```javascript
await renderStep(r);
```

trước khi Auto Run fetch batch kế tiếp.

Đây là root cause chính của cảm giác:

> **frame-by-frame / batch-by-batch**

dù từng marker bên trong batch có dùng `requestAnimationFrame`.

---

# 2. VẤN ĐỀ KHÔNG PHẢI `requestAnimationFrame`

Đừng bỏ `requestAnimationFrame`.

Nó hoàn toàn phù hợp để render chuyển động mượt.

Vấn đề là lifecycle hiện tại:

```text
Fetch Batch #1
↓
Start all Batch #1 animations
↓
WAIT UNTIL EVERY TRIP OF BATCH #1 FINISHES
↓
Fetch Batch #2
↓
Start all Batch #2 animations
↓
WAIT
...
```

Do:

```javascript
await Promise.all(jobs);
```

Kết quả:

- tất cả xe bắt đầu gần cùng lúc;
- tất cả xe thuộc batch đó phải hoàn tất;
- mới xuất hiện request/chuyến mới;
- thành phố có cảm giác bị “đóng băng theo frame”.

Tôi KHÔNG muốn behavior này.

---

# 3. TARGET BEHAVIOR

Tôi muốn:

```text
Simulation time
────────────────────────────────────────────────────────────→

Batch 1       Batch 2       Batch 3       Batch 4
  │             │             │             │
  ▼             ▼             ▼             ▼
Driver A ───────────────────────────────►
        start → pickup → dropoff

Driver B       ─────────────────────►
               start → pickup → dropoff

Driver C                     ─────────────────────────►
                             start → pickup → dropoff

Driver D                                      ───────►
```

Điều quan trọng:

> **Batch mới được đưa vào trong khi các trip cũ vẫn đang chạy.**

Không có barrier:

```text
“mọi xe batch trước phải chạy xong”
```

trước batch tiếp theo.

Đây chính là cảm giác liên tục tôi cần.

---

# 4. CORE ARCHITECTURE MỚI — GLOBAL SIMULATION CLOCK

Hãy xây một **global playback clock**.

Ví dụ state:

```javascript
var playback = {
    running: false,
    paused: true,

    simTimeSec: null,
    lastWallTimeMs: null,

    speed: 1,

    // 1x: 1 real second = 60 simulation seconds
    baseSimSecondsPerRealSecond: 60,

    rafId: null
};
```

Con số chính xác có thể điều chỉnh sau QA, nhưng concept phải là:

```text
simulation time chạy liên tục
```

không phải:

```text
mỗi trip có một clock độc lập rồi Promise.all.
```

---

# 5. GLOBAL RAF LOOP

Chỉ nên có **một animation loop chính** cho toàn map.

Pseudo-code:

```javascript
function playbackLoop(nowMs) {
    if (!playback.running) return;

    if (playback.lastWallTimeMs == null) {
        playback.lastWallTimeMs = nowMs;
    }

    var dtWallSec =
        (nowMs - playback.lastWallTimeMs) / 1000;

    playback.lastWallTimeMs = nowMs;

    if (!playback.paused && !engineBuffering) {
        playback.simTimeSec +=
            dtWallSec
            * playback.baseSimSecondsPerRealSecond
            * playback.speed;
    }

    consumeDueBatchEvents(playback.simTimeSec);

    updateAllActiveTrips(playback.simTimeSec);

    updatePlaybackUI();

    playback.rafId =
        requestAnimationFrame(playbackLoop);
}
```

`requestAnimationFrame` vẫn được dùng.

Nhưng giờ nó update:

> **toàn bộ thành phố / mọi active vehicle theo cùng một clock.**

---

# 6. ACTIVE TRIPS MODEL

Tạo:

```javascript
var activeTrips = new Map();
```

Key có thể là:

```text
req_idx
```

hoặc:

```text
batch + req_idx
```

Mỗi trip visual:

```javascript
{
    reqIdx,
    driverId,

    startSimSec,
    pickupSimSec,
    dropoffSimSec,

    startLatLng,
    pickupLatLng,
    dropoffLatLng,

    phase,

    driverMarker,

    deadheadLine,
    passengerLine,

    pickupMarker,
    dropoffMarker,

    completedAtSimSec
}
```

---

# 7. SỬ DỤNG THỜI GIAN THẬT TỪ ENGINE

Current backend đã trả:

```text
window_start_seconds
pickup_eta_seconds
duration_seconds
```

Dùng chính các field này.

Cho assignment:

```javascript
var startSimSec =
    batch.window_start_seconds;

var pickupSimSec =
    startSimSec
    + assignment.pickup_eta_seconds;

var dropoffSimSec =
    pickupSimSec
    + assignment.duration_seconds;
```

Không dùng random duration.

Không dùng fake Q.

Không dùng duration tự nghĩ ra.

---

# 8. BATCH ENGINE VẪN LÀ 60 GIÂY

Backend simulator đang batch:

```text
WINDOW_SECONDS = 60
```

Giữ nguyên.

Điều đó có nghĩa:

```text
Batch #N
window_start = T

Batch #N+1
window_start ≈ T + 60s
```

Ở frontend playback:

> khi global `simTimeSec` đi đến batch time tiếp theo, batch đó được activate.

Các trip trước **không bị dừng**.

---

# 9. ENGINE PRODUCER + VISUAL CONSUMER

Tách hai concern.

## Engine Producer

Nhiệm vụ:

```text
POST /step
→ lấy quyết định thật từ simulator
→ đưa response vào batch queue
```

## Visual Consumer

Nhiệm vụ:

```text
global simulation clock
→ đến thời gian của batch nào
→ activate batch đó
→ thêm trip vào activeTrips
```

Không còn:

```text
step
→ await toàn bộ trip
→ step tiếp
```

---

# 10. BATCH EVENT QUEUE

Tạo:

```javascript
var batchQueue = [];
```

Mỗi item chính là response thật từ:

```text
POST /simulations/{id}/step
```

Sort/order theo:

```text
window_start_seconds
```

Ví dụ:

```javascript
batchQueue.push(batchResult);
```

`consumeDueBatchEvents(simTime)`:

```javascript
while (
    batchQueue.length
    && batchQueue[0].window_start_seconds
       <= simTime
) {
    activateBatch(batchQueue.shift());
}
```

---

# 11. PREFETCH BUFFER ĐỂ KHÔNG BỊ KHỰNG

Để animation giống demo cũ, không nên đợi tới đúng batch boundary mới bắt đầu HTTP request.

Hãy prefetch một lượng nhỏ batch.

Ví dụ:

```javascript
var TARGET_BUFFER_BATCHES = 4;
```

Producer:

```javascript
async function fillBatchBuffer() {
    while (
        autoRunning
        && !engineDone
        && batchQueue.length < TARGET_BUFFER_BATCHES
    ) {
        var result = await api("/step", ...);
        batchQueue.push(result);
    }
}
```

Chỉ gọi step tuần tự.

KHÔNG concurrent backend step.

Session lock vẫn giữ nguyên.

---

# 12. CỰC KỲ QUAN TRỌNG — PREFETCH KHÔNG ĐƯỢC PHÁ `WHY THIS DRIVER`

Current backend explainability trước đây chỉ phụ thuộc `last_window`.

Nếu frontend prefetch batch mới, `last_window` có thể bị overwrite trong khi user đang xem batch trước.

Hãy audit implementation hiện tại.

Nếu `/explain` vẫn chỉ giữ một `last_window`, phải sửa.

Có 2 hướng hợp lệ.

---

## Hướng ưu tiên A — Backend giữ recent explanation snapshots

Trong session:

```python
self.window_history = OrderedDict()
```

Mỗi batch lưu serialized explanation inputs/output.

Ví dụ key:

```text
batch_number
```

hoặc:

```text
(batch, req_idx)
```

Giữ ring buffer:

```text
last 20–50 batches
```

không cần toàn bộ run.

Endpoint:

```text
GET /simulations/{run_id}/batches/{batch}/explain/{req_idx}
```

hoặc contract tương đương.

Frontend assignment lưu:

```text
batch_number
req_idx
```

Click trip cũ vẫn explain được.

---

## Hướng B — Step response chứa explanation snapshot

Nếu đơn giản hơn:

mỗi assigned request có thể kèm đủ:

```text
selected_driver
local_rank
score components
candidate summary
```

trong response.

Nhưng nếu candidate list lớn:

> không nên làm payload quá nặng.

Hướng A thường sạch hơn.

---

# 13. KHÔNG PREFETCH VÔ HẠN

Chỉ buffer ít batch.

Ví dụ:

```text
4–8 batch
```

Mục tiêu chỉ là:

> che network/backend latency.

Không chạy toàn bộ 3000 request phía backend rồi mới playback.

---

# 14. BUFFERING STATE

Nếu:

```text
sim clock sắp tới batch kế tiếp
```

nhưng:

```text
batchQueue rỗng
```

do backend không theo kịp:

> pause simulation clock.

Không để timeline chạy qua event chưa có.

Show badge:

```text
BUFFERING ENGINE...
```

Khi queue có batch:

> resume clock.

Điều này đặc biệt quan trọng ở:

```text
8×
```

---

# 15. SPEED MODEL

Tôi muốn UI:

```text
Tốc độ mô phỏng
[1×] [2×] [4×] [8×]
```

Có thể thêm:

```text
0.5×
```

nếu hữu ích.

Speed phải thay đổi:

> tốc độ **global simulation clock**.

Không phải:

> chỉ chia duration animation riêng từng trip.

Ví dụ:

```text
1×
1 real second = 60 simulation seconds

2×
1 real second = 120 simulation seconds

4×
1 real second = 240 simulation seconds

8×
1 real second = 480 simulation seconds
```

Có thể tuning base factor sau.

---

# 16. ĐỔI SPEED TRONG KHI ĐANG CHẠY

Phải hoạt động ngay.

Vì clock update bằng:

```text
deltaWall × speed
```

nên user đổi:

```text
1× → 4×
```

không cần restart active trip.

Mọi xe đang chạy tự tăng tốc đồng bộ.

Đây là một lợi ích lớn của global clock.

---

# 17. UPDATE ACTIVE TRIP POSITION

Trong mỗi RAF frame:

```javascript
function updateTrip(trip, simTimeSec) {
    if (simTimeSec < trip.pickupSimSec) {
        // DEADHEAD
    }
    else if (simTimeSec < trip.dropoffSimSec) {
        // PASSENGER ONBOARD
    }
    else {
        // COMPLETED
    }
}
```

---

# 18. DEADHEAD INTERPOLATION

Nếu:

```text
startSim <= t < pickupSim
```

progress:

```javascript
var p =
    (t - startSim)
    / (pickupSim - startSim);
```

position:

```text
driver_start → pickup
```

Use linear interpolation.

NYC local coordinate range nhỏ nên lat/lon interpolation đủ cho visualization.

Không invent road route.

---

# 19. PASSENGER TRIP INTERPOLATION

Nếu:

```text
pickupSim <= t < dropoffSim
```

progress:

```javascript
var p =
    (t - pickupSim)
    / (dropoffSim - pickupSim);
```

position:

```text
pickup → dropoff
```

---

# 20. KHÔNG DÙNG EASING QUÁ MẠNH

Để nhìn như movement liên tục:

ưu tiên:

```text
linear interpolation
```

hoặc easing rất nhẹ.

Không:

- bounce;
- elastic;
- zoom animation;
- repeated acceleration/deceleration mạnh.

Đây là simulation playback, không phải game UI.

---

# 21. DRIVER PHASE VISUAL

Marker/tooltip nên biết state.

## Deadheading

```text
Driver #73
→ Heading to pickup
Request #1842
ETA phase
```

## Passenger onboard

```text
Driver #73
● Passenger onboard
→ Zone 17
```

## Completed / Idle

```text
Driver #73
Idle / available
```

---

# 22. PERSISTENT DRIVER MARKER

Giữ:

```javascript
driverMarkers = new Map()
```

nhưng không gọi:

```text
setLatLng(engine dropoff)
```

cho một driver đang có active visual trip.

Đây là vấn đề cực kỳ quan trọng.

---

# 23. ENGINE POST-COMMIT STATE VS VISUAL STATE

Backend simulator commit trip ngay khi assignment được quyết định.

Nên response:

```text
r.drivers
```

có thể đã chứa:

```text
driver.lat/lon = dropoff
```

dù visual playback đang còn ở giữa chuyến.

Do đó:

> **KHÔNG được sync active visual driver từ `r.drivers`.**

Logic:

```javascript
if (driver has activeTrip) {
    // global clock owns its displayed position
}
else {
    // backend driver state can update marker
}
```

---

# 24. ACTIVE TRIP DRIVER KHÔNG ĐƯỢC SNAP TỚI DESTINATION KHI BATCH MỚI TỚI

Current architecture dễ gặp:

```text
Trip A đang animation
↓
Batch mới response có driver state = dropoff
↓
syncIdleDrivers()
↓
marker teleport tới dropoff
```

Global `activeTrips` phải ngăn điều này.

Nếu:

```text
activeTripByDriver.has(driverId)
```

thì backend sync không được override marker position.

---

# 25. KHI TRIP KẾT THÚC

Khi:

```text
simTime >= dropoffSim
```

set:

```text
marker = exact dropoff coordinate
```

remove:

```text
activeTripByDriver[driverId]
```

sau đó backend state có thể quản lý marker lại.

---

# 26. ASSERTION ĐỂ BẮT VISUAL/ENGINE CONFLICT

Nếu batch mới assign driver X nhưng frontend vẫn thấy:

```text
active trip X endSim > newBatch.window_start
```

đó là inconsistency.

Không silently override.

Trong development:

```javascript
console.warn(...)
```

và snap previous trip only as fallback.

Có thể show dev warning.

Theo simulator đúng, driver chỉ feasible khi:

```text
available_at <= window_start
```

nên bình thường conflict không nên xảy ra.

---

# 27. ROUTE LAYER KHÔNG ĐƯỢC CLEAR MỖI BATCH

Current:

```javascript
mapLayers.route.clearLayers();
```

không phù hợp với continuous playback.

Nếu trip từ batch cũ vẫn đang chạy:

> route của nó phải còn.

Thay architecture.

---

# 28. ACTIVE ROUTE OBJECTS

Mỗi active trip tự giữ:

```text
deadheadLine
passengerLine
pickupMarker
dropoffMarker
```

Không đặt tất cả active trip vào layer bị clear theo batch.

Có thể:

```javascript
activeTripLayer
ephemeralRequestLayer
historyTrailLayer
selectionLayer
```

---

# 29. LAYER ARCHITECTURE ĐỀ XUẤT

```text
Leaflet Map
│
├── baseTileLayer
│
├── historyTrailLayer
│
├── activeRouteLayer
│
├── requestStatusLayer
│
├── driverLayer
│
└── selectionLayer
```

---

# 30. REQUEST STATUS LAYER

`declined` / `infeasible` request có thể là ephemeral.

Giữ khoảng:

```text
1–3 simulated batch periods
```

sau đó fade/remove.

Không clear đột ngột ngay khi batch mới tới.

Điều này làm map “sống” liên tục.

---

# 31. TRAIL HISTORY — RẤT NÊN LÀM ĐỂ CÓ CẢM GIÁC GIỐNG DEMO CŨ

Trong ảnh demo_fairdispatch, người xem thấy nhiều tuyến đã/đang chạy cùng lúc.

Sản phẩm mới nên giữ **route trail ngắn hạn**.

Khi trip complete:

- active route giảm opacity;
- chuyển sang `historyTrailLayer`;
- giữ thêm khoảng 2–5 batch mô phỏng;
- sau đó fade/remove.

Ví dụ:

```text
active route = opacity 0.8
recent completed = opacity 0.18
old completed = remove
```

Không giữ hàng nghìn route.

---

# 32. ROUTE PHASE FEEDBACK

Trong deadhead phase:

```text
deadhead line highlighted
passenger line faint
```

Sau pickup:

```text
deadhead line fades
passenger line highlighted
```

Sau dropoff:

```text
whole route becomes history trail
```

Đây là visual nhỏ nhưng tạo cảm giác theo dõi chuyến rất tốt.

---

# 33. PICKUP EVENT

Khi simTime crossing:

```text
pickupSimSec
```

trigger một lần:

- pickup marker pulse nhẹ;
- marker style chuyển `passenger onboard`;
- selected assignment panel phase đổi.

Không dùng animation màu mè.

---

# 34. DROPOFF EVENT

Khi crossing:

```text
dropoffSimSec
```

trigger:

- dropoff marker pulse nhẹ;
- trip complete;
- driver marker state chuyển available theo backend state phù hợp;
- route thành history trail.

---

# 35. NHIỀU XE PHẢI CHẠY ĐỒNG THỜI

Không:

```text
animate driver A
await
animate driver B
await
```

Không:

```text
Promise.all(currentBatch)
await before next batch
```

Mà:

> activeTrips có thể chứa trip từ nhiều batch khác nhau.

RAF loop update tất cả.

Đây là target cốt lõi.

---

# 36. ĐỪNG GIỚI HẠN “SỐ XE SONG SONG” BẰNG CÁCH THAY ĐỔI ENGINE

Frontend cũ có control:

```text
SỐ XE SONG SONG
```

Nhưng product mới không được dùng control đó để thay đổi assignment thật.

Nếu muốn có:

```text
Visual Density
```

chỉ dùng để:

- hide some non-selected route trails;
- giảm label;
- tối ưu performance.

Không được làm thay đổi engine.

Không bắt buộc implement ở vòng này.

---

# 37. FOLLOW A DRIVER — BONUS WOW FEATURE

Nếu dễ implement:

khi user click một moving driver:

show button:

```text
Follow
```

Khi Follow ON:

map pan nhẹ theo marker.

Không zoom liên tục.

Click Follow OFF:

camera đứng yên.

Đây là bonus, không P0.

---

# 38. SELECTED DRIVER PHẢI NỔI BẬT TRONG LÚC DI CHUYỂN

Nếu user click assignment:

- selected driver marker lớn hơn;
- active route dày hơn;
- other routes opacity thấp hơn;
- Why This Driver mở;
- map không làm dừng animation.

Click lại:

> đóng selection.

Fix toggle hiện tại phải giữ nguyên.

---

# 39. WHY THIS DRIVER PHẢI CÓ LIVE PHASE

Trong panel có thể thêm:

```text
Visual phase
Deadheading to pickup
```

hoặc:

```text
Passenger onboard
```

Progress:

```text
42%
```

Đây chỉ là visual progress theo global sim clock.

Decision explanation vẫn từ engine thật.

---

# 40. BATCH ACTIVATION KHÔNG ĐƯỢC CLEAR WHY THIS DRIVER NẾU TRIP VẪN ĐANG ACTIVE

Current code:

```javascript
clearAssignmentSelection();
```

mỗi `renderStep()`.

Với continuous playback, behavior này không còn hợp lý.

Nếu selected trip vẫn đang active:

> giữ selection qua batch mới.

Chỉ auto clear nếu:

- trip đã complete và retention time hết;
- user đóng;
- reset/new run.

Điều này quan trọng để user có thể theo dõi một tài xế qua nhiều batch.

---

# 41. OPERATIONAL LOG PHẢI TIẾP TỤC NHẬN BATCH MỚI TRONG KHI XE CŨ ĐANG CHẠY

Đừng replace toàn table mỗi batch nếu muốn cảm giác live.

Có thể giữ:

```text
recent 30–100 assignment rows
```

append mới ở đầu/cuối.

Mỗi row:

```text
time
req
driver
fare
pickup
dropoff
phase/status
```

Click row vẫn select được trip nếu còn retained.

---

# 42. CURRENT ASSIGN TABLE VS OPERATIONAL LOG

Nếu current code chỉ show current-batch table:

nâng thành:

> Recent Operations

với bounded history.

Ví dụ:

```text
last 50 rows
```

Không để DOM tăng vô hạn.

---

# 43. TOPBAR STATUS PHẢI CHẠY LIÊN TỤC

Show:

```text
Sim Time: 08:31:42
Speed: 2×
Active trips: 18
Queued batches: 3
Completed: 421
```

Không bắt buộc tất cả.

Tối thiểu:

```text
Sim Time
Speed
Active trips
```

sẽ tạo cảm giác rất sống.

---

# 44. SIMULATION CLOCK DISPLAY

Dựa trên:

```text
window_start_seconds
```

convert thành:

```text
Day N · HH:MM:SS
```

Update mỗi RAF hoặc 4–10 lần/second.

Không chỉ thay đổi mỗi batch.

Ví dụ:

```text
Day 3 · 17:42:18
```

nó phải “chạy”.

Đây là một trong những yếu tố làm app giống vận hành thật.

---

# 45. SPEED 1× / 2× / 4× / 8×

Tuning target gợi ý:

```text
1×:
1 real sec ≈ 60 sim sec
```

Tức:

- batch mới khoảng mỗi 1s;
- trip 10 phút ≈ 10s;
- trip 20 phút ≈ 20s.

Điều này tạo overlap rất đẹp.

Nếu quá chậm:

```text
base = 90 hoặc 120 sim sec / real sec
```

Tune bằng mắt.

Nhưng relative relationship phải giữ.

---

# 46. HIGH SPEED 8× VÀ BACKEND THROUGHPUT

Ở 8×:

batch event có thể tới rất nhanh.

Nếu backend producer không theo kịp:

> BUFFERING.

Không để:

- skip batch;
- overlap POST /step;
- fabricate states.

Có thể cap effective playback:

```text
Engine-limited
```

nếu cần.

---

# 47. INITIAL BUFFER

Khi user bấm Run:

đừng bắt animation chạy ngay lập tức với queue rỗng.

Flow:

```text
Run
↓
Preloading 3 batches...
↓
READY
↓
Clock starts
```

Thời gian preload rất ngắn.

Show:

```text
Preparing live playback...
```

Sau khi đủ:

> movement bắt đầu mượt ngay.

---

# 48. MANUAL STEP CŨNG ĐỔI SEMANTICS

Current Step:

> fetch một batch và đợi toàn bộ trip batch đó finish.

Không còn phù hợp.

New Step nên nghĩa:

> **Advance one 60-second simulation window.**

Flow:

```text
Pause clock
↓
ensure next batch response
↓
activate next batch
↓
animate clock từ T → T+60s theo selected speed
↓
pause
```

Các trip dài hơn 60s:

> vẫn chưa tới dropoff.

Bấm Step tiếp:

> chúng tiếp tục di chuyển.

Đây là behavior rất tự nhiên.

---

# 49. MANUAL STEP KHÔNG CẦN CHỜ TRIP COMPLETE

Đây là thay đổi quan trọng.

Step = một simulation batch/window.

Không phải:

> complete all trips that started in this batch.

---

# 50. RESET

Reset phải cancel:

```text
RAF clock state
activeTrips
batchQueue
producer
trail timers
selected trip
recent log
```

sau đó:

```text
POST backend reset
```

và về clean ready state.

Không để orphan animation tiếp tục sau Reset.

---

# 51. NEW RUN

New Run phải:

- cancel old playback generation;
- increment `playbackGenerationId`;
- mọi old async producer response kiểm generation;
- nếu stale → ignore.

Điều này tránh:

```text
old run response quay về sau
→ chèn batch vào run mới.
```

---

# 52. ASYNC CANCELLATION SAFETY

Có thể dùng:

```javascript
var runGeneration = 0;
```

Mỗi New Run/Reset:

```javascript
runGeneration++;
```

Producer capture:

```javascript
var myGeneration = runGeneration;
```

Response:

```javascript
if (myGeneration !== runGeneration) return;
```

Nếu dùng AbortController được thì tốt.

---

# 53. EXPLAINABILITY HISTORY LÀ BẮT BUỘC NẾU PREFETCH

Nhắc lại:

> không được để producer advance backend rồi `Why this driver` mất khả năng giải thích trip đang hiển thị.

Phải test.

---

# 54. BACKEND RECENT WINDOW HISTORY — GỢI Ý

Ví dụ:

```python
from collections import OrderedDict

self.window_history = OrderedDict()
self.max_window_history = 32
```

Sau mỗi batch:

lưu:

```text
batch
window_start
cands
income snapshot
selected_by_req
mean_income
```

Hoặc tốt hơn:

> precompute serialized explanations cho assigned requests.

Sau đó pop oldest.

---

# 55. ENDPOINT EXPLAIN MỚI

Ví dụ:

```text
GET /simulations/{run_id}/batches/{batch}/explain/{req_idx}
```

Response giữ contract hiện tại cộng batch.

Frontend row/trip lưu:

```text
batch
req_idx
```

Nếu không muốn đổi endpoint public quá nhiều:

có thể:

```text
GET /simulations/{id}/explain/{req_idx}?batch=17
```

Miễn correctness.

---

# 56. PERF — RAF KHÔNG NHẤT THIẾT UPDATE 60FPS CHO 200 MARKER

Dùng `requestAnimationFrame`, nhưng throttle visual update khoảng:

```text
30 FPS
```

nếu cần.

Ví dụ:

```javascript
if (now - lastRenderMs < 33) return;
```

Clock vẫn chính xác theo wall delta.

30 FPS đã rất mượt.

---

# 57. LEAFLET PERFORMANCE

Không recreate:

```text
L.map
LayerGroup
driver marker
```

mỗi frame.

Chỉ:

```text
marker.setLatLng()
line.setStyle()
```

khi cần.

---

# 58. DRIVER MARKER STYLE

Để nhìn chuyên nghiệp hơn:

### Idle
small neutral circle.

### Deadhead
blue/cyan moving dot.

### Passenger onboard
strong navy/purple moving dot.

### Selected
larger ring.

Không cần taxi icon ảnh.

Nếu dùng `DivIcon` với mũi tên hướng đi thì bonus.

---

# 59. HEADING / BEARING — BONUS

Nếu dùng icon có orientation:

tính bearing giữa current → next point.

Rotate CSS arrow.

Không bắt buộc.

Không làm ảnh hưởng deadline.

---

# 60. MAP CAMERA

Không auto fit mỗi batch.

Điều đó gây giật.

Camera mặc định đứng yên.

Chỉ:

- user zoom/pan;
- click selected assignment → optional fit bounds;
- Follow driver → optional.

---

# 61. KHÔNG CLEAR ROUTES LÀM MAP FLASH

Current batch request markers mới có thể xuất hiện.

Nhưng:

- basemap giữ;
- active drivers giữ;
- active routes giữ;
- history trail giữ.

Không có frame trắng giữa các batch.

---

# 62. FADE TRANSITIONS

Có thể dùng CSS/Leaflet opacity transition cho:

- completed route fade;
- declined marker fade;
- pickup/dropoff fade.

Không fade moving driver.

---

# 63. PRODUCT MUST LOOK ALIVE

Trong lúc Run:

người xem phải luôn thấy ít nhất một số trong các thứ:

- driver moving;
- active route;
- sim clock moving;
- status counters changing;
- new requests appearing;
- completed route fading.

Không có trạng thái:

> tất cả đứng im chờ batch kế tiếp

trừ khi thực sự không có active trips.

---

# 64. KHÔNG INVENT CONTINUOUS GPS

Dù nhìn “thật”:

UI phải gọi:

```text
Simulation Playback
```

không:

```text
Live GPS Tracking
```

Route interpolation:

```text
straight segment between real coordinates
```

vì chưa có road router.

---

# 65. OLD `demo_fairdispatch` LÀ VISUAL TARGET, KHÔNG PHẢI LOGIC SOURCE

Các screenshot user cung cấp cho thấy target feeling:

- basemap luôn sống;
- nhiều tuyến chồng lên nhau;
- xe/trip xuất hiện liên tục;
- speed có thể đổi;
- panel không block map;
- chart bên dưới update dần;
- không có cảm giác “reset frame”.

Hãy tái tạo **cảm giác vận hành** này.

Không copy:

- old result;
- old Q-score;
- fake driver identity;
- old P2-13 logic.

---

# 66. FAIRNESS / KPI UPDATE

Backend metrics đến theo batch.

Có thể update KPI khi batch event được activated.

Không cần interpolate Utility/Gini mỗi frame.

Như vậy:

```text
movement continuous
KPI changes at dispatch windows
```

hoàn toàn hợp lý.

---

# 67. HISTOGRAM / LORENZ

Cũng update theo activated batch.

Không update mỗi RAF.

Giữ performance.

---

# 68. RECENT OPERATION LOG

Append row khi batch event activate.

Không chờ trip complete.

Status row có thể live-update:

```text
TO PICKUP
ON TRIP
DONE
```

dựa trên active trip phase.

Chỉ update visible recent rows.

---

# 69. TRIP COMPLETION COUNTER

Backend `served_total` có thể được increment at commit time, không phải visual dropoff time.

Không được giả đây là “physically arrived now”.

Nếu UI có:

```text
Engine Served
```

giữ metric backend.

Nếu muốn visual completion count:

tách tên:

```text
Playback completed
```

Không trộn.

---

# 70. TEST CASE — CONTINUITY

Tạo frontend/dev diagnostic.

Scenario:

```text
Trip A:
start T=0
duration 600 sec

Batch 2:
T=60 sec
Trip B starts
```

At:

```text
simTime = 120 sec
```

expect:

```text
Trip A active
Trip B active
```

Không Trip A complete chỉ vì Batch 2 bắt đầu.

---

# 71. TEST CASE — DRIVER REASSIGNMENT

Trip A:

```text
Driver 5
endSim = 600
```

New assignment Driver 5 chỉ được activate:

```text
startSim >= 600
```

If not:

log inconsistency.

---

# 72. TEST CASE — SPEED CHANGE

At 1×:

run 2 real seconds.

Capture sim advance.

Change 4×.

Next 2 real seconds:

advance ~4× more.

Active trip progress must continue, not restart.

---

# 73. TEST CASE — PAUSE

Pause:

- `simTimeSec` stops;
- moving markers stop;
- no batch activation;
- producer may continue filling small buffer if desired;
- Resume continues from same position.

---

# 74. TEST CASE — BUFFERING

Artificially delay backend.

If queue empty:

- sim clock stops;
- active trip position freezes;
- UI says BUFFERING;
- when data arrives resume without time jump.

---

# 75. TEST CASE — RESET

During active animation:

Reset.

Expect:

- no old marker movement after reset;
- no old queued batch activation;
- map clean;
- backend run reset;
- no console errors.

---

# 76. TEST CASE — WHY THIS DRIVER WITH PREFETCH

Prefetch batch N+3.

User click assignment from currently visible batch N.

Explain must still return correct:

```text
selected_driver
local rank
candidate scores
Hungarian decision
```

---

# 77. ACCEPTANCE VISUAL

I should be able to watch the map for 15–30 seconds and see:

```text
some cars currently deadheading
some cars currently carrying passengers
new assignments appearing
old assignments still moving
some trips finishing
new trips starting
```

all at the same time.

This is the key acceptance criterion.

---

# 78. IMPORTANT — NO `await Promise.all(active trip completion)` BARRIER

There may still be Promise usage.

But Auto Run must NEVER do:

```javascript
await Promise.all(all trip animations in current batch);
then fetch next step;
```

Remove that architecture.

This is the single most important code-level change.

---

# 79. AUTO RUN NEW FLOW

Target:

```text
Run clicked
↓
Start producer
↓
Prebuffer 3–4 batches
↓
Set simTime to first batch window_start
↓
Start global RAF clock
↓
Activate Batch 1
↓
Trips begin
↓
60 simulated seconds later
Activate Batch 2
WHILE Batch 1 trips may still be moving
↓
Activate Batch 3...
```

Exactly this.

---

# 80. MANUAL STEP NEW FLOW

Target:

```text
Paused
↓
Step
↓
Ensure next batch event available
↓
Advance global sim clock by exactly 60 simulation seconds
over a short wall-time animation
↓
Pause again
```

Existing trips continue only as far as 60 simulation seconds.

---

# 81. SPEED BUTTON MEANING

Label clearly:

```text
Simulation Speed
```

or:

```text
Playback Speed
```

Tooltip:

> Changes visual simulation clock only; dispatch decisions remain unchanged.

---

# 82. OPTIONAL “TRAIL DENSITY”

If map becomes cluttered:

simple control:

```text
Trails
Low / Medium / High
```

It only controls how long completed routes remain.

Does not alter engine.

Bonus only.

---

# 83. CHARTS BÊN DƯỚI

Không cần redesign lớn.

Nhưng chart update theo batch activation, không producer fetch time.

Nếu producer prefetches ahead:

> UI must NOT update KPI/charts before visual simulation reaches that batch.

Very important.

---

# 84. SOURCE OF VISIBLE STATE

Distinguish:

```text
engine future buffer
```

from:

```text
visible playback state
```

Prefetched batch is NOT yet visible.

Only when:

```text
batch.window_start <= simTime
```

do:

- KPI update;
- log append;
- request markers appear;
- assignments become active.

---

# 85. DATA STRUCTURE GỢI Ý

```javascript
var playbackState = {
    currentSimTime: null,
    speed: 1,
    running: false,
    paused: true,
    buffering: false
};

var engineState = {
    done: false,
    producerBusy: false,
    queue: []
};

var activeTrips = new Map();
var activeTripByDriver = new Map();
var recentTrips = new Map();
```

Không bắt buộc exact names.

---

# 86. PRODUCER PSEUDO-CODE

```javascript
async function pumpEngine(gen) {
    if (engineState.producerBusy) return;
    engineState.producerBusy = true;

    try {
        while (
            playbackState.running &&
            !engineState.done &&
            engineState.queue.length < BUFFER_TARGET &&
            gen === runGeneration
        ) {
            var r = await api(
                "/simulations/" + currentRunId + "/step",
                { method: "POST" }
            );

            if (gen !== runGeneration) return;

            engineState.queue.push(r);

            if (r.done) {
                engineState.done = true;
                break;
            }
        }
    } finally {
        engineState.producerBusy = false;
    }
}
```

---

# 87. CONSUMER PSEUDO-CODE

```javascript
function consumeDueBatches() {
    while (
        engineState.queue.length &&
        engineState.queue[0].window_start_seconds
            <= playbackState.currentSimTime
    ) {
        var batch = engineState.queue.shift();

        activateBatch(batch);

        pumpEngine(runGeneration);
    }
}
```

---

# 88. ACTIVE TRIP UPDATE PSEUDO-CODE

```javascript
function updateActiveTrips(t) {
    activeTrips.forEach(function (trip, key) {
        if (t < trip.pickupSimSec) {
            updateDeadhead(trip, t);
        }
        else if (t < trip.dropoffSimSec) {
            updatePassengerTrip(trip, t);
        }
        else {
            completeVisualTrip(trip);
            activeTrips.delete(key);
            activeTripByDriver.delete(trip.driverId);
        }
    });
}
```

---

# 89. IMPORTANT: DON'T CREATE ONE RAF PER TRIP ANYMORE

Current:

```text
animateDriverAlong()
→ requestAnimationFrame per trip
```

New architecture should prefer:

> **one global RAF loop**

because:

- speed change affects everything instantly;
- Pause affects everything instantly;
- all vehicles share one clock;
- easier to keep synchronized;
- easier buffering behavior;
- fewer animation lifecycle bugs.

You may remove `animateDriverAlong()` or keep helper interpolation functions only.

---

# 90. INTERPOLATION HELPERS

Example:

```javascript
function lerp(a, b, t) {
    return a + (b - a) * t;
}

function lerpLatLng(a, b, t) {
    return [
        lerp(a[0], b[0], t),
        lerp(a[1], b[1], t)
    ];
}
```

Clamp:

```text
0..1
```

---

# 91. SIM CLOCK FORMAT

Implement:

```javascript
function formatSimTime(sec) {
    var day = Math.floor(sec / 86400) + 1;
    var s = sec % 86400;
    var hh = Math.floor(s / 3600);
    var mm = Math.floor((s % 3600) / 60);
    var ss = Math.floor(s % 60);

    return "Day " + day + " · "
        + HH + ":" + MM + ":" + SS;
}
```

Use actual timestamp convention already in dataset carefully.

If `pickup_ts` is seconds-from-start rather than epoch:

label accordingly.

---

# 92. DO NOT BREAK LIVE QUICK COMPARE

Animation refactor must not touch:

```text
/compare/live
verified compare
long horizon
run history
```

unless shared code safely changes.

---

# 93. DO NOT BREAK ASSIGNMENT EXPLANATION

Preserve:

- selected Hungarian driver;
- local candidate rank;
- components;
- toggle open/close.

Upgrade history only as needed for buffer.

---

# 94. DO NOT BREAK LEAFLET MAP

Keep:

- CARTO/OpenStreetMap basemap;
- current styling;
- map center;
- real coordinates;
- declined/infeasible markers;
- deadhead line;
- passenger line.

Improve lifecycle only.

---

# 95. NO NEW FRAMEWORK REQUIRED

Do not introduce React/Vue just for this.

Current HTML/CSS/JS + Leaflet is sufficient.

Keep dependency footprint low.

---

# 96. DOCUMENT ARCHITECTURE

Update:

```text
PRODUCT_FRONTEND_PORT_PLAN.md
PRODUCT_FIX_PLAN.md
README.md
DEMO_SCRIPT.md
```

Add section:

```text
Continuous Playback Architecture
```

Explain:

```text
Engine runs discrete 60-second dispatch windows.
Frontend maps those discrete decisions onto a continuous compressed
simulation clock. Trips from different windows may overlap visually.
The animation never changes engine decisions.
```

---

# 97. DEMO SCRIPT SAU FIX

## Start

Mở NYC map.

## New Run

```text
MOMAQL
200 drivers
λ 0.5
Forecast ON
```

## Run 1×

Nói:

> Mỗi dispatch window vẫn là 60 giây như simulator, nhưng frontend phát lại trên một đồng hồ liên tục.

Watch:

- old trip moving;
- new trip starts;
- multiple drivers overlap.

## Switch 4×

Cars accelerate together.

## Pause

Everything freezes at current position.

## Resume

Everything continues exactly from there.

## Click moving trip

Why This Driver opens while trip keeps moving.

## Follow if available

optional.

## Compare / Horizon

unchanged.

---

# 98. VISUAL QA TARGET — GIỐNG SCREENSHOT DEMO CŨ

Tôi muốn feeling:

- real basemap;
- nhiều active path cùng lúc;
- colored moving vehicle points;
- some paths fading;
- no total redraw;
- no batch barrier;
- speed changes visible immediately;
- city never looks like “static snapshot”.

Không cần copy exact old colors.

---

# 99. FINAL ACCEPTANCE CHECKLIST

## Clock
- [ ] One global continuous simulation clock.
- [ ] Sim time updates continuously.
- [ ] Speed multiplier affects global clock.
- [ ] Pause freezes exact current state.
- [ ] Resume continues.

## Engine
- [ ] Engine still dispatches in 60s batches.
- [ ] Steps remain sequential.
- [ ] No concurrent backend step.
- [ ] Small prefetch buffer only.
- [ ] Buffering safely pauses clock.

## Trips
- [ ] Trips from different batches overlap.
- [ ] Driver start→pickup→dropoff.
- [ ] Active trip is not snapped by backend post-commit state.
- [ ] Multiple cars move simultaneously.
- [ ] Completed route fades into recent trail.

## UI
- [ ] New requests appear while old trips are still moving.
- [ ] Operational log appends continuously.
- [ ] KPI/chart updates on visible batch activation, not prefetch time.
- [ ] Selected trip remains selected across new batches.
- [ ] Why This Driver remains correct.

## Reliability
- [ ] Reset cancels all old visual state.
- [ ] New Run ignores stale async responses.
- [ ] 1×/2×/4×/8× stable.
- [ ] No memory leak from route/marker history.
- [ ] 1366×768 and 1920×1080 usable.

---

# 100. CÂU MỆNH LỆNH QUAN TRỌNG NHẤT

> **Đừng tiếp tục animation theo mô hình “batch → Promise.all tất cả xe chạy xong → batch tiếp theo”. Hãy chuyển Live Simulation sang một global continuous simulation clock. Backend vẫn tạo quyết định rời rạc mỗi 60 giây, nhưng frontend phải phát lại các chuyến trên cùng một timeline liên tục, vì vậy một tài xế của batch trước vẫn có thể đang chạy trong khi request và assignment của batch sau đã xuất hiện. Dùng một requestAnimationFrame loop toàn cục để cập nhật mọi active trip, không một RAF riêng bị await theo batch. Speed control thay đổi tốc độ clock toàn cục. Đây là thay đổi quyết định để sản phẩm có cảm giác vận hành liên tục giống demo_fairdispatch.**

---

# KHI HOÀN THÀNH — REPORT

Trả rõ:

```text
Root cause of old frame-like playback:
- ...

Continuous playback architecture:
- ...

Global clock:
- ...

Engine buffer:
- ...

Active trip model:
- ...

Why This Driver history handling:
- ...

Speed / pause behavior:
- ...

Route/trail lifecycle:
- ...

Tests performed:
- ...

Files changed:
- ...

Known limitations:
- ...
```

Không chỉ trả:

> Done.
