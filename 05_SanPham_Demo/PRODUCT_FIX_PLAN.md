# Product Fix Plan — FairDispatch Decision-Support Prototype

Audit lại toàn bộ `05_SanPham_Demo` (backend + frontend) đối chiếu với
`FairDispatch_Product_Hardening_Frontend_Reference_Claude_Prompt.md`. Mỗi issue dưới đây đã
tự verify trong code thật trước khi liệt kê ở đây (không suy đoán).

## P0 — phải sửa trước demo

| # | Issue | Root cause | File | Fix | Test | Status |
|---|---|---|---|---|---|---|
| P0.1 | "Why this driver?" đánh dấu sai winner | `explain()` sort candidate theo score local rồi frontend lấy `i===0` làm winner — sai vì Hungarian là **global joint optimization**, driver điểm cao nhất cục bộ có thể bị dồn cho request khác | `backend/engine_adapter.py` (`step`, `explain`), `frontend/app.js` (`explainAssignment`) | `step()` lưu `selected_driver_id` thật theo `req_idx` từ `assignments` (kết quả Hungarian thật) vào `last_window`; `explain()` trả `selected_driver_id` + `local_rank`/`is_selected` cho từng candidate; frontend đổi điều kiện winner từ `i===0` sang `c.is_selected` | `backend/test_engine.py::test_hungarian_can_diverge_from_local_top_score` (chứng minh divergence có thật) + `::test_explain_marks_actual_hungarian_winner_not_local_rank_1` (chứng minh fix đúng) | **Fixed & verified** (18/18 test pass + curl HTTP thật) |
| P0.2 | Auto Run có thể chạy chồng step (race condition) | `setInterval(doStep, 350)` với `doStep` async — nếu 1 step chậm hơn 350ms, interval có thể bắn step tiếp trong khi step trước chưa xong | `frontend/app.js` | Đổi sang async sequential `while(running){ await doStep(); await sleep(300); }` có guard `stepInFlight`; backend thêm `threading.Lock` per-session, step chồng nhau → HTTP 409 thay vì corrupt state | Manual: gọi step liên tiếp nhanh qua curl, xác nhận không lỗi; lock code review | **Fixed** |
| P0.3 | Reset không bật lại nút Step | Sau khi simulation `done`, `elStep.disabled=true`; handler `btnReset` không set lại | `frontend/app.js` | `setControlsForActiveRun(hasRun, isDone)` dùng chung cho mọi transition, Reset gọi với `isDone=false` | Manual: chạy hết 1 run nhỏ, Reset, xác nhận Step bấm lại được | **Fixed** |
| P0.4 | `requirements.txt` thiếu dependency thật | `policies.py` có `import numpy as np` và `from scipy.optimize import linear_sum_assignment` — cả hai **không có** trong `requirements.txt` | `backend/requirements.txt` | Thêm `numpy==2.2.6`, `scipy==1.16.2`, pin đúng version đã `pip show` trong môi trường build | `pip show` xác nhận version khớp | **Fixed** |
| P0.5 | Provenance đọc sai key checksum | `dataset_checksums.json` dùng key `"val.parquet"`, nhưng `app.js` đọc `r.dataset_checksums.val` → luôn `undefined` → hiện `"?..."` | `frontend/app.js`, `backend/replay_adapter.py` | Đổi sang `r.dataset_checksums["val.parquet"]`; thiếu thì hiện `"Unavailable"` | Gọi `/provenance` thật qua curl, xác nhận SHA-256 khớp `dataset_checksums.json` | **Fixed & verified** |
| P0.6 | Driver Income Distribution chưa render thật | `#histBars` tồn tại trong HTML nhưng không hàm nào ghi bar vào đó | `backend/engine_adapter.py` (`_histogram`), `frontend/app.js` (`renderHistogram`) | Backend tính bin thật từ income driver mỗi step (`income_histogram` field); frontend vẽ bar theo tần suất thật | `test_income_histogram_shape` + curl xác nhận `bins`/`counts` có dữ liệu thật | **Fixed & verified** |

## P1 — rất nên sửa trước presentation

| # | Issue | Fix | Status |
|---|---|---|---|
| P1.1 | Map chỉ vẽ assigned, không phân biệt declined/infeasible | Backend `step()` trả thêm toạ độ pickup của request declined/infeasible; map vẽ 3 màu khác nhau | Đã làm |
| P1.2 | Deadhead vs trip chưa phân biệt nét đứt/liền | Line driver→pickup dùng `stroke-dasharray` (deadhead), pickup→dropoff nét liền (trip khách) | Đã làm |
| P1.3 | Nhãn vị trí driver busy gây hiểu nhầm | Driver "busy" đang hiện toạ độ **dropoff đích đến** (đã update ngay lúc commit, đúng theo field `Driver.lat/lon` thật của simulator — simulator không mô hình hoá vị trí giữa đường) — thêm tooltip label rõ "vị trí dropoff kế tiếp (chưa tới)" thay vì ngầm hiểu là vị trí hiện tại | Đã làm (label rõ, không đổi model) |
| P1.4 | Live mode phụ thuộc path repo dev ngoài bundle | Cân nhắc bundle demo slice thật (3,000 dòng đầu val.parquet) vào `data/demo_val.parquet` | Không làm ở vòng này — rủi ro thời gian/kích thước hơn giá trị tăng thêm; giữ nguyên cơ chế fallback rõ ràng đã có (`FAIRDISPATCH_DEV_REPO`), ghi rõ trong README |
| P1.5 | Backend chưa validate input | Thêm validation: `n_drivers>0`, `0<=lam<=1`, `0<gamma<=1` (gamma=0 hợp lệ về toán học nhưng vô nghĩa với model — vẫn cho phép, chỉ chặn âm/quá 1), `0<alpha<=1`, `request_limit>0`, policy hợp lệ, dataset tồn tại; nếu `n_drivers` > số request khả dụng để seed, trả về **actual initialized count** thay vì số yêu cầu | Đã làm |
| P1.6 | Control không context-aware | Khi policy != MOMAQL: disable Lambda slider + Forecast toggle, tooltip "Chỉ áp dụng cho MOMAQL" | Đã làm |
| P1.7 | Provenance lẫn "engine snapshot" với "dev repo HEAD" | Tách rõ 2 khái niệm trong response `/provenance`: `bundle_engine_source` (bản src/policies.py dùng để chạy — trong bundle) vs `dev_repo_git_head` (HEAD của repo dev, chỉ dùng để lấy data parquet, không phải commit của engine đang chạy) | Đã làm |
| P1.8 | Chưa có test | Thêm `backend/test_engine.py`: create/step/reset/explain/compare/replay/validation/missing-dataset/histogram/provenance + test riêng cho P0.1 | Đã làm |
| P1.9 | Offline reliability | ~~Không áp dụng — frontend không dùng CDN nào~~ (đã đổi ở round Leaflet port, xem cuối file): giờ dùng CDN Leaflet 1.9.4, có fallback tĩnh nếu `window.L` undefined | Đã cập nhật — control/KPI/log/tracker không phụ thuộc Leaflet, chỉ map bị ảnh hưởng nếu CDN chặn |

## P2 — giá trị cao, làm nếu còn thời gian

Lorenz curve (P2.5) — làm, vì rẻ (thêm 1 SVG polyline từ income thật, công thức Lorenz chuẩn
tự viết lại, không copy code cũ) và giá trị giải thích Gini cao. Driver Ranking (P2.1),
Reproduce Run (P2.3), Export (P2.7) — không làm ở vòng này (bonus, không nằm trong 5 deliverable
trung tâm), ghi vào "Known limitations" thay vì âm thầm bỏ qua.

## Tham khảo frontend cũ (`demo_fairdispatch`) — đã dùng gì / không dùng gì

**Đã tham khảo (UI pattern, viết lại bằng code/màu/data của mình):** khái niệm badge dạng pill
nhỏ (`LIVE ENGINE` / `VERIFIED REPLAY` / `DEMO SLICE`), công thức Lorenz curve (toán chuẩn,
không phải logic riêng của họ — viết lại bằng income thật của session hiện tại).

**Tuyệt đối không dùng:** `qScore = 85 + trip.id % 10` (Q-score giả), driver label theo
`revealIdx` (không phải driver_id thật từ Hungarian), income reveal theo mảng precompute chia
dần, `requestAnimationFrame` tự quyết định state, mọi số liệu cũ (`S8300`, `MOMAQL Gini
~0.925`, `P2-13`, `Production Heuristic`) — không liên quan tới FairDispatch hiện tại.

## Round 2 — port trực tiếp visual shell từ `demo_fairdispatch` (Leaflet map)

Khác round 1 (chỉ "tham khảo pattern"): round này port trực tiếp layout/CSS/Leaflet init/tracker
panel/log table từ `demo_fairdispatch`, chi tiết mapping ở `PRODUCT_FRONTEND_PORT_PLAN.md`.
Backend (`app.py`/`engine_adapter.py`/`replay_adapter.py`/`paths.py`) **không đổi** — chỉ
`frontend/index.html`, `frontend/styles.css`, `frontend/app.js`. Đã verify sau port:

- `pytest backend/test_engine.py -v` — 18/18 pass (backend không đổi, như dự kiến).
- `node --check frontend/app.js` — cú pháp hợp lệ.
- curl full flow thật (create MOMAQL/50 driver → step nhiều lần → explain) xác nhận field JSON
  (`drivers[].lat/lon/busy/income`, `assignments[].driver_start_lat/lon`, `declined_requests[]`,
  `infeasible_requests[]`, `income_histogram`, `lorenz`) khớp đúng những gì `app.js` mới đọc.
- Quét `/explain/{req_idx}` qua nhiều req_idx, tìm được case `selected_local_rank=2` thật (req 16
  batch đầu là rank 1, nhưng req 42 cùng run có driver #0 được chọn dù rank cục bộ #2) — xác nhận
  bug P0.1 vẫn được UI mới hiển thị đúng (badge "GLOBAL OPTIMUM" trong `.tracker`).
- Chưa tự mở trình duyệt xác nhận render (môi trường build không có công cụ điều khiển trình
  duyệt) — xem "Known limitations" trong README.

## Round 3 — Visual Playback, toggle explainability, compact tables, fix `/compare/live` HTTP 500

**Root cause HTTP 500 (`/compare/live`):** `class _Body: forecast_on = forecast_on` bên trong
vòng `for` — Python class-body name resolution KHÔNG nhìn thấy scope hàm bao ngoài (chỉ
global/builtin), nên RHS `forecast_on` raise `NameError` ngay khi định nghĩa class → crash
thành HTTP 500 không kiểm soát. Fix: thay bằng `types.SimpleNamespace(...)` (`backend/app.py`).
Test: `backend/test_engine.py::test_compare_live_returns_200_not_500`. **Verify qua curl thật
sau fix: HTTP 200**, `results.full`/`results.no_forecast` có `utility`/`gini`/`served` hợp lệ.

**Visual Playback:** Driver marker interpolate tuyến tính giữa 3 toạ độ thật
(`driver_start` → `pickup` → `dropoff`) lấy từ chính response `/step` đã commit — animation
KHÔNG tự quyết định driver/fare/ETA/assignment, chỉ phát lại trực quan quyết định đã có. Sau
khi animation xong, marker snap về đúng state `r.drivers[]` từ backend (không bao giờ lệch
engine — xem comment trong `app.js`). Driver marker persistent theo `driver_id` (`Map`, không
xoá `driverLayer` mỗi step) — hết hiện tượng nhấp nháy/teleport. Route/request layer vẫn vẽ lại
mỗi batch (không cần giữ lịch sử toàn bộ). Backend thêm field `duration_seconds` vào
`assignments[]` (`engine_adapter.py`, đã có sẵn trong parquet, chỉ expose thêm) để tính thời
lượng playback thật — **verify qua curl thật field có mặt đúng**.

**Speed control:** `Playback Speed` 0.5×/1×/2×/4×/8× chỉ chia tỷ lệ thời gian animation
(`animationMs / speedMultiplier`), không đổi engine/quyết định thật.

**Why this driver? toggle:** `toggleAssignmentSelection(reqIdx)` — click lại cùng assignment
(table row / map marker / map route) đóng panel; nút "×" và phím Escape cũng đóng; batch mới
tới tự động `clearAssignmentSelection()` (không giữ panel cũ khi map đã sang batch mới).

**Compact tables:** `table.rows` đổi từ `width:100%` sang `width:max-content;min-width:540px`
+ `colgroup` width cố định từng cột — hết cột giãn hết chiều rộng màn hình. KPI đổi sang
`.kpi-row` grid 2 cột (label trái, value phải, `tabular-nums`) để mọi con số thẳng hàng.

Test: `pytest backend/test_engine.py -v` → 19/19 pass. `node --check frontend/app.js` → OK.

## Round 4 — Continuous City Playback (thay batch-by-batch bằng global simulation clock)

**Root cause cảm giác "đứng hình theo frame"**: Round 3 vẫn `await Promise.all(jobs)` rồi mới
`await playBatchAnimations(r)` trước khi fetch batch kế — mỗi batch là một barrier cứng, xe
batch trước buộc phải chạy xong mới thấy batch sau. `requestAnimationFrame` tự nó không sai,
vấn đề nằm ở lifecycle await-theo-batch.

**Kiến trúc mới:** một global simulation clock (`playback.simTime`, giây, cùng đơn vị với
`window_start_seconds` backend) chạy bằng **một** `requestAnimationFrame` loop duy nhất cho
toàn map — không còn 1 RAF riêng mỗi trip. Engine vẫn dispatch từng batch 60 giây thật
(`SimulationSession.WINDOW_SECONDS` không đổi); frontend tách **Engine Producer** (gọi
`POST /step` tuần tự, KHÔNG concurrent, đẩy kết quả vào `engineQ.queue`, prefetch tối đa 4
batch) khỏi **Visual Consumer** (`consumeDueBatches()`: chỉ activate batch khi
`window_start_seconds <= simTime`). Trip từ nhiều batch overlap thật trên map — driver batch
trước vẫn có thể đang chạy trong khi request/assignment batch sau đã xuất hiện.

**Buffering**: nếu `simTime` sắp cần batch mới nhưng `engineQ.queue` rỗng và engine chưa done
→ clock tự đứng (không advance), badge `BUFFERING ENGINE...` hiện; khi có data, resume không
nhảy thời gian.

**Active trip model**: mỗi trip lưu `startSim/pickupSim/dropoffSim` tính từ
`window_start_seconds + pickup_eta_seconds (+ duration_seconds)` — số thật từ backend, không
random. Nội suy tuyến tính driver_start→pickup→dropoff mỗi frame. Driver marker persistent
(`driverMarkers` Map theo `driver_id`); **driver đang có active trip KHÔNG BAO GIỜ bị
`syncIdleDrivers()` từ `r.drivers` (state post-commit của backend) đè vị trí** — đây là bug
lớn nhất phải tránh (xem comment `syncIdleDrivers`/`activateBatch` trong `app.js`).

**Why this driver? qua prefetch**: backend `engine_adapter.SimulationSession` đổi từ 1
`last_window` sang `window_history` (OrderedDict, ring buffer 32 batch gần nhất).
`explain(req_idx, batch=None)` nhận thêm `batch` optional; endpoint
`GET /explain/{req_idx}?batch=N` (không đổi path, thêm query param — giữ contract cũ khi
`batch` bị bỏ qua = batch mới nhất). Test:
`test_explain_still_works_for_older_batch_after_newer_steps` — step 3 lần, verify explain
batch #1 vẫn đúng sau khi đã có batch #3, và batch không tồn tại trả 404 rõ ràng. **Verify qua
curl thật** trên server sống: đúng kết quả cho cả 2 case.

**Route/trail lifecycle**: route active (opacity cao) → khi trip dropoff xong chuyển sang
`historyTrail` (opacity thấp, CSS `transition:opacity .6s` cho fade mượt), tự xoá sau
`3×WINDOW_SECONDS` giây mô phỏng. Declined/infeasible marker retention `2×WINDOW_SECONDS`.
Route/marker KHÔNG bị clear toàn bộ mỗi batch nữa.

**Selection giữ qua batch mới**: `clearAssignmentSelection()` không còn gọi mỗi batch — chỉ tự
đóng khi trip's retention hết hạn (`purgeExpired`), user tự đóng ("×"/Esc/click lại), hoặc
Reset/New Run.

**Speed 0.5×–8×** đổi `BASE_SIM_SEC_PER_REAL_SEC * speed` của global clock (không phải chia
animationMs từng trip riêng như Round 3) — đổi speed giữa chừng áp dụng ngay cho mọi trip đang
chạy vì tất cả dùng chung một clock.

**Manual Step semantics đổi**: không còn "đợi hết trip của batch này" — Step = advance đúng 60
giây mô phỏng (`playback.stepTarget = simTime + 60`); trip dài hơn 60s tiếp tục ở Step sau.

**Async cancellation**: `runGeneration` tăng ở New Run/Reset; producer kiểm tra
`gen === runGeneration` trước khi push batch vào queue — response cũ từ run trước không bao
giờ lọt vào run mới.

**Không đổi (giữ nguyên):** `/compare/live` fix Round 3, Verified Replay (Compare/Horizon/
History), provenance, session lock backend, Leaflet basemap/CARTO tile, actual Hungarian
winner/local rank.

Test: `pytest backend/test_engine.py -v` → **20/20 pass**. `node --check frontend/app.js` → OK.
Curl thật: tạo run → step 3 lần (`window_start_seconds` tăng dần đúng thứ tự) → explain batch
cũ vẫn đúng → explain batch không tồn tại → 404 → reset OK.

## Round 5 — Operator Control Room (từ research UI sang operations decision-support)

Chi tiết đầy đủ ở `OPERATOR_CONTROL_ROOM_PLAN.md`. Tóm tắt:

- **Backend thêm 1 field thật**: `feasible_drivers_unique` trong response `/step`
  (`engine_adapter._step_locked()`) — đếm driver **duy nhất** xuất hiện trong candidate list
  của ít nhất 1 request trong window, KHÔNG sum số cạnh candidate (audit yêu cầu rõ tránh nhầm
  "supply" = tổng edge). Test: `test_feasible_drivers_unique_is_deduplicated_not_sum_of_edges`.
- **Backend thêm constants thật** vào response `/simulations`: `eta_threshold_seconds` (600,
  từ `simulator.MAX_PICKUP_ETA_SECONDS`), `batch_window_seconds` (60, từ
  `SimulationSession.WINDOW_SECONDS`), `deadhead_cost_per_second_usd` (0.0025, từ
  `simulator.COST_PER_SECOND_DEADHEAD_USD`) — hiện ở Advanced panel dạng "600 sec · fixed",
  không phải input giả.
- **Objective Presets**: Efficiency/Balanced/Fairness map λ=0.1/0.5/0.9 (nhãn vận hành tự đặt,
  không phải khuyến nghị paper — ghi rõ trong tooltip); Custom mở lại slider λ raw; kéo slider
  tay tự chuyển về Custom.
- **Service Rate** = `assigned / requests_arrived` (mẫu số = assigned+declined+infeasible,
  loại trừ lẫn nhau, không đếm trùng).
- **Pickup ETA Avg/P90/Worst**: tính client-side từ `assignments[].pickup_eta_seconds` batch
  hiện tại (Current Window), P90 = nearest-rank percentile, deterministic.
- **Demand/Supply**: Demand=`requests_arrived`, Supply=`feasible_drivers_unique` thật; nếu
  Supply=0 hiện "N/A / ∞" thay vì số vô nghĩa.
- **Fairness Summary**: Fleet Mean/Bottom10%/Top10%/Top-Bottom ratio tính từ `r.drivers[].income`
  thật mỗi batch; Bottom10%=0 → "N/A / ∞", không chia cho 0 âm thầm.
- **Fairness Guardrail**: Max Gini operator tự đặt, lưu `localStorage`, ghi rõ "tự đặt, không
  phải khuyến nghị từ paper".
- **Alert Center**: rule-based (Service Rate/ETA P90/Gini/Demand-Supply), threshold operator-
  defined (`MIN_SERVICE_RATE=0.90`, `MAX_PICKUP_P90_SEC=480`, `SHORTAGE_RATIO_THRESHOLD=1.5`),
  ghi rõ trong code comment đây là demo guardrail.
- **Map Layers**: tách 1 layer gộp cũ (`requestStatus`) thành `requestMarkers`/`declined`/
  `infeasible` riêng để checkbox toggle độc lập từng layer — chỉ add/removeLayer Leaflet, không
  gọi API, không đổi engine state.
- **Search**: Driver ID/Request ID trong buffer hiện tại (`driverMarkers`/`activeTrips`/
  `historyTrail`) — nếu không có, báo "Not in current playback buffer", không giả kết quả.
- **Bonus SKIP theo đúng permission của spec** ("Bonus if complex; do not block P1"): Follow
  Driver, Demand/Supply heatmap, Income layer, Driver Ranking, Scenario Presets, Save Scenario,
  Operator/Research toggle, Fleet What-if.
- **Bug thật tự phát hiện khi restructure HTML**: `updateStatusGrid()` vẫn set
  `#sgAssigned`/`#sgDeclInfeas` sau khi 2 span đó bị xoá khỏi statusGrid (chuyển sang Service
  Health card) → sẽ crash `Cannot set properties of null`. Phát hiện qua đối chiếu có hệ thống
  toàn bộ `getElementById()` trong `app.js` với id thật trong `index.html` (`comm -23`), sửa
  trước khi test trên trình duyệt.

Test: `pytest backend/test_engine.py -v` → **21/21 pass**. `node --check frontend/app.js` → OK.
Curl thật: `constants` đúng {600, 60, 0.0025}; `feasible_drivers_unique` thật; denominator
service rate (`assigned+declined+infeasible == requests_arrived`) khớp.

## Round 6 — Operator Scenario Controls (time/day filter, presets, Save Run, layout spacing)

Chi tiết đầy đủ ở `OPERATOR_SCENARIO_CONTROLS_PLAN.md`. Tóm tắt:

- **Backend thêm field thật** `pickup_weekday` (tính từ epoch giây, `(days_since_epoch+3)%7`,
  1970-01-01 là Thứ 5 thật) + `TimeFilter`/`DayFilter` Pydantic models + hàm thuần
  `_hour_in_time_filter()`/`_weekday_in_day_filter()`/`apply_scenario_filters()`.
- **Filter order fix**: `SimulationSession.__init__` đổi từ "slice request_limit rồi mới có
  thể filter" sang **load full dataset → filter theo time/day → slice request_limit** — tránh
  scenario hẹp (vd "Chủ nhật 3-4h sáng") bị mất hết request chỉ vì bị cắt bởi limit không liên
  quan. Response `/simulations` thêm `filtered_request_count`/`available_request_count`.
- **Empty scenario**: raise `ValueError` rõ ràng → HTTP 400, không crash.
- **Horizon presets đổi giá trị** theo spec mới: Quick=200/Standard=3000 (giữ default hiện
  tại)/Extended=10000/Custom (Round 5 dùng 3000/10000/195508 — spec Round 6 audit lại và chỉnh).
- **Fleet presets** 100/200/400/Custom — đổi `n_drivers` thật, KHÔNG dùng để giới hạn số xe
  animate trên map (đúng yêu cầu "concurrent vehicle" không được dùng làm engine control).
- **Save Run**: localStorage (`fd_saved_runs`, cap 20), lưu config+metrics thật của run hiện
  tại, không cần backend endpoint mới.
- **Collapsible**: toàn bộ 8 section rightpanel chuyển sang `<details>` native (trước chỉ
  Advanced có). Phát hiện + sửa bug CSS có sẵn: `.section-title` chỉ style cho `h2`, các `h3`
  dùng class đó (đa số card) bị mất màu navy/uppercase từ trước — gộp lại thành 1 rule chung.
- **Layout spacing root cause** (khoảng trắng lớn trước Operational Log): `.rightpanel{grid-row:
  1/3}` không bound chiều cao → CSS Grid track-sizing giãn row1 để chứa sidebar ngày càng dài
  (nhiều card Operator). Fix: `align-self:start` + `max-height:calc(100vh - 150px)` +
  `overflow-y:auto` — sidebar tự scroll độc lập, KHÔNG dùng negative margin.
- **Không thêm** (đúng permission của spec): Confidence %, Q calibration, nhóm đại diện,
  concurrent-vehicle engine limiter.

Test: `pytest backend/test_engine.py -v` → **26/26 pass** (+5 test time/day filter). `node
--check frontend/app.js` → OK. Curl thật: weekday filter (140,174/195,508 request khớp), giờ
qua đêm 22-5 (41,800/195,508), empty scenario → HTTP 400 đúng message.
