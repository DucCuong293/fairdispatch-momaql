# FairDispatch — Ride-Hailing Dispatch Simulation & Decision-Support Prototype

**Đây không phải app gọi xe production kiểu Grab.** Đây là một prototype cho phép người vận
hành (Operation Manager / Dispatch Engineer / Data Scientist / Research Engineer) **mô phỏng
và so sánh các chiến lược điều phối**, xem vì sao một tài xế được chọn, và quan sát trade-off
dài hạn giữa hiệu quả hệ thống (Utility) và công bằng thu nhập tài xế (Fairness) — dựa thẳng
trên engine nghiên cứu thật của dự án FairDispatch, không phải dashboard trình bày lại số
liệu tĩnh.

> FairDispatch cho phép người vận hành mô phỏng và so sánh các chiến lược điều phối, hiểu vì
> sao một tài xế được chọn, và quan sát trade-off dài hạn giữa hiệu quả hệ thống và công bằng
> thu nhập.

Xem `PRODUCT_AUDIT.md` để biết chính xác capability nào của engine đã được audit trước khi
build, và quyết định implementation cho từng gap. Xem `PRODUCT_FIX_PLAN.md` cho vòng hardening
(bug thật đã tìm và sửa, có test) và `DEMO_SCRIPT.md` cho kịch bản demo 4–6 phút.

## Kiến trúc

```
Web App (frontend/, HTML+CSS+JS thuần)
   |
   v
FastAPI backend (backend/app.py)
   |
   +--> engine_adapter.py --> import THẲNG src/policies.py + src/simulator.py thật
   |                          (không viết lại thuật toán chấm điểm/matching)
   |
   +--> replay_adapter.py --> đọc THẲNG reports/*.csv thật (verified experiment)
```

Không microservices, không Kafka, không WebSocket — kiến trúc đơn giản khớp khối lượng công
việc thật (một backend Python phục vụ vài chục request/giây cho một demo cục bộ).

## Hai nguồn dữ liệu thật (không hard-code)

- **Live Simulation**: đọc trực tiếp `fairdispatch_v3_clean/data/val.parquet` (195,508 request
  NYC TLC thật) qua `pyarrow`, giới hạn theo `request_limit` để Step phản hồi tức thì trong
  demo. File parquet **không** được copy vào gói nộp vì quá lớn (48–225MB/file) — backend đọc
  từ repo dev cạnh gói nộp. Nếu repo dev ở vị trí khác, đặt biến môi trường
  `FAIRDISPATCH_DEV_REPO`.
- **Replay Mode** (`Compare Policies`, `Long-Horizon`): đọc trực tiếp
  `03_Source_Code_Va_Ket_Qua/reports/*.csv` — đúng các file đã dùng để build Research Report và
  slide thuyết trình (5 seed, 195,508 request/seed cho main comparison; 37-ngày cho
  long-horizon). UI luôn gắn badge "Verified Experiment" + ghi rõ tên file nguồn.

## Cài đặt & chạy

```bash
cd 05_SanPham_Demo/backend
pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8731
```

Mở trình duyệt: **http://127.0.0.1:8731/** (FastAPI tự phục vụ luôn thư mục `frontend/`, không
cần chạy 2 server riêng).

## Live Simulation Mode vs Research Replay Mode

| | Live Simulation | Research Replay |
|---|---|---|
| Dữ liệu | Slice nhỏ thật từ `val.parquet` (mặc định 3,000 request đầu) | Toàn bộ 195,508 request × 5 seed, đã verify |
| Tốc độ | Step tức thì, Run tự động lặp Step | Đọc CSV, tức thì |
| Mục đích | Xem engine ra quyết định từng batch, click assignment để giải thích | Xem kết quả nghiên cứu đã verify, đáng tin cậy thống kê |
| Nhãn UI | — | Badge "Verified Experiment" (xanh) khi đọc replay, "Minh hoạ" (vàng) khi live quick-compare |

**Không dùng slice live nhỏ để thay thế kết luận nghiên cứu.** Tab Compare Policies mặc định
show kết quả Replay thật (5 seed đầy đủ); nút "Live Quick Compare" là minh hoạ bổ sung, có ghi
chú rõ không đại diện thống kê.

## Policy hỗ trợ

Đúng 5 policy thật trong `src/policies.py`, dùng chung một Hungarian joint assignment
(`hungarian_batch_assign`, scipy `linear_sum_assignment`):

- **Greedy** — score = fare_amount
- **Nearest** — score = (600 − ETA) × 0.0025
- **LAF** (Lowest Accumulated Fare) — score = rel_fairness × fare
- **Exact REASSIGN** — score = fare − deadhead_cost
- **MOMAQL** — score = (1−λ)(fare − deadhead_cost + γ·Q[dropoff_zone, hour]) + λ·(rel_fairness × fare), dùng Q-table đã train (`data/momaql_q_table_trained.json`, frozen khi đánh giá)

## 5 deliverable trung tâm đã implement

1. **Map driver + request + assignment thật** — Leaflet 1.9.4 (CDN unpkg) + basemap CARTO
   light, marker/route vẽ theo lat/lon NYC thật (không có zone geometry trong repo nên không
   vẽ polygon zone, dùng tọa độ thật thay vì zone trung tâm giả định). Layout/interaction
   (topbar, legend, tracker panel "Why this driver?", log table) port từ
   `demo_fairdispatch/` (visual only — data/logic 100% từ engine hiện tại, xem
   `PRODUCT_FRONTEND_PORT_PLAN.md`). Driver marker chạy trên **một global continuous simulation
   clock** (không phải animation theo-batch): trip từ nhiều batch 60-giây thật của engine có
   thể overlap trực quan (driver batch trước vẫn đang chạy khi request/assignment batch sau đã
   xuất hiện), tốc độ chỉnh 0.5×–8× đổi ngay cho mọi trip đang chạy vì dùng chung một clock.
   Vẫn chỉ là lớp trình bày cho quyết định engine đã có sẵn, không phải GPS/road simulation
   (xem `PRODUCT_FIX_PLAN.md` Round 3–4). Right panel là **Operator Control Room** (Round 5,
   xem `OPERATOR_CONTROL_ROOM_PLAN.md`): Objective preset, Service Health (service rate/ETA
   avg-P90/demand-supply), Fairness (mean/bottom10%/top10%/guardrail), Alert Center, Map Layer
   toggle, Search Driver/Request — tham số nghiên cứu (λ/γ/α/seed) chuyển vào Advanced/Research
   collapsible. Round 6 (`OPERATOR_SCENARIO_CONTROLS_PLAN.md`) thêm Scenario controls: Time-of-
   day filter (Sáng/Chiều/Đêm/Tùy chỉnh, hỗ trợ qua đêm), Day filter (ngày thường/cuối tuần/tùy
   chỉnh, weekday tính thật từ timestamp), Fleet/Horizon preset buttons, Save Run
   (localStorage), scenario summary + badge "SCENARIO FILTER ACTIVE"; toàn bộ 8 section
   rightpanel giờ collapsible (`<details>` native).
2. **Run / Step / Reset** — Step là một lệnh API đồng bộ thật (advance đúng 1 window 60 giây
   qua `feasible_drivers`/`commit_trip`/`policy.select_batch` thật); Run = tự động gọi lại
   Step (Pause dừng ngay vì mỗi step độc lập, không animation giả).
3. **Utility + Gini** — tính lại mỗi step bằng đúng công thức `gini()`/`variance()` từ
   `common_loader.py`, trên state driver thật.
4. **Compare Full vs No-Forecast** — mặc định đọc replay thật (`r2_ablation_results.csv`);
   có thêm Live Quick Compare minh hoạ.
5. **Click assignment → giải thích** — winner đánh dấu bằng `selected_driver_id` thật lấy từ
   kết quả Hungarian (`step()` lưu lại, KHÔNG suy ra từ candidate điểm cao nhất — Hungarian tối
   ưu cả batch nên driver được chọn có thể không phải local rank #1; UI hiện rõ local rank khi
   điều đó xảy ra). Với MOMAQL, decompose đúng 3 số hạng thật của `MOMAQLPolicy._score()`
   (Immediate Utility / Future Zone Value / Fairness Adjustment, cộng lại đúng bằng final
   score); với 4 policy còn lại, show công thức 1 dòng thật lấy verbatim từ `select_batch()`.

Đã có thêm (rẻ, dữ liệu sẵn có): Run provenance (SHA-256 của chính `policies.py`/`simulator.py`
đang chạy, tách biệt rõ với Git HEAD của repo dev), Run History (in-memory), Driver income
histogram + Lorenz curve (tính thật từ income driver mỗi step), map phân biệt driver
idle/busy, assigned/declined/infeasible, deadhead (nét đứt) vs trip khách (nét liền),
Long-Horizon Timeline (Replay, 11 checkpoint ngày 1→37), λ slider context-aware (tự disable
khi policy ≠ MOMAQL), badge rõ **LIVE ENGINE** vs **VERIFIED REPLAY**.

**Chủ động không làm** (đúng khuyến nghị "không cần" của spec): Login/Register, CSV export,
MLP live toggle (không có model file để serve — chỉ có kết quả CSV, xem
`replay_adapter.mlp_vs_tabular`), animation phức tạp, WebSocket/Kafka/microservices, bundle
demo dataset riêng (cân nhắc nhưng không làm — xem `PRODUCT_FIX_PLAN.md` P1.4).

## Tests

```bash
cd 05_SanPham_Demo/backend
python -m pytest test_engine.py -v
```

18 test, bao gồm test quan trọng nhất của cả sản phẩm:
`test_hungarian_can_diverge_from_local_top_score` chứng minh bằng một ví dụ toán học cụ thể
rằng Hungarian joint assignment có thể chọn driver KHÔNG phải điểm cao nhất cục bộ cho một
request, và `test_explain_marks_actual_hungarian_winner_not_local_rank_1` xác nhận endpoint
`/explain` phản ánh đúng điều đó (không phải `i===0`). Các test cần `val.parquet` thật sẽ tự
skip (không fail) nếu chạy trong môi trường chỉ có gói nộp, không có repo dev cạnh bên.

## Known limitations (tự công bố)

- Không có zone polygon/geometry trong repo → map hiện marker/route điểm lat/lon thật trên nền
  Leaflet, không phải bản đồ zone tô màu.
- Leaflet tải qua CDN (unpkg) → cần internet lúc demo; nếu CDN chặn/mất mạng, map hiện thông
  báo fallback tĩnh, còn control/KPI/log/tracker vẫn hoạt động bình thường (không phụ thuộc
  Leaflet).
- Live mode giới hạn request để demo mượt — không dùng để rút kết luận thống kê (dùng Replay
  cho việc đó).
- Không có model MLP đã lưu để serve live — MLP chỉ xuất hiện qua Replay
  (`reports/mlp_vs_tabular_summary.csv`).
- History lưu in-memory, mất khi restart backend (đúng bản chất "prototype", không giả cơ sở
  dữ liệu).
- Backend chạy đồng bộ (sync) — một request Step chặn tới khi tính xong; với slice demo nhỏ
  (≤5,000 request) điều này nhanh (<1s), không cần background job/queue.
- **Chưa test bằng trình duyệt thật** — môi trường build này không có công cụ điều khiển
  trình duyệt. Đã verify toàn bộ backend qua HTTP thật (tạo run, step qua 5 policy, explain,
  compare live, replay, reset, error handling), và verify `app.js` hợp lệ cú pháp, nhưng
  **layout/rendering trên trình duyệt thật chưa được người dùng xác nhận** — hãy mở
  `http://127.0.0.1:8731/` để kiểm tra trước khi coi là hoàn thành.

## Nguồn số liệu (không hard-code)

Mọi số hiển thị trên UI đến từ một trong hai nguồn thật, không có số nào gõ tay vào
frontend: engine trực tiếp (`engine_adapter.py`, mỗi lần Step) hoặc file CSV/JSON thật trong
`03_Source_Code_Va_Ket_Qua/reports/` và `/data/` (`replay_adapter.py`). Xem `PRODUCT_AUDIT.md`
để đối chiếu từng requirement với dòng code/hàm cụ thể.
