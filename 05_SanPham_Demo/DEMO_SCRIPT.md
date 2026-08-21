# Demo Script — FairDispatch Decision-Support Prototype

Mục tiêu: 4–6 phút, kể đúng một câu chuyện end-to-end. Không click qua 20 menu.

## Chuẩn bị

```bash
cd 05_SanPham_Demo/backend
pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8731
```

Mở `http://127.0.0.1:8731/`. Chờ chấm xanh "Backend OK" ở góc trên bên phải.

## Flow (7 bước)

**0. Operator Control Room (bonus, nếu còn thời gian)**
Right panel giờ chia nhóm: Current Run → Operating Objective (Efficiency/Balanced/Fairness
preset) → Simulation → Service Health (Service Rate, Pickup ETA Avg/P90, Demand/Supply) →
Fairness (mean/bottom10%/top10%/guardrail Max Gini) → Alerts → Map Layers → Advanced/Research
(λ/γ/α/seed, gấp gọn). Chỉ trong 30 giây, người xem trả lời được: policy nào, objective nào,
bao nhiêu driver, service rate bao nhiêu, ETA thế nào, demand có vượt supply không, fairness có
vượt guardrail không, alert nào cần chú ý.

**1. Mở Control Room (~20s)**
Map NYC thật (Leaflet + CARTO light) đã hiện sẵn ngay khi mở trang, kể cả trước khi bấm New Run.
> "Đây là decision-support prototype, không phải customer app. Người dùng là operation
> manager/dispatch engineer — mô phỏng và so sánh chiến lược điều phối trước khi áp dụng."

**2. New Run (~20s)**
Giữ mặc định: `MOMAQL / 200 drivers / λ=0.5 / Forecast ON / seed 20260721 / request_limit 3000`.
Bấm **New Run**. Chỉ ra dòng note nếu `n_drivers_actual` khác với số yêu cầu (minh bạch, không
âm thầm chạy ít driver hơn user tưởng).

**3. Run — Continuous City Playback (~60s)**
Đặt **Simulation Speed = 1×**, bấm **Run**. Đây là điểm khác biệt lớn nhất: KHÔNG phải
"batch xuất hiện → tất cả xe chạy → dừng → batch mới" mà là một **đồng hồ mô phỏng liên tục**
(Sim Time chạy liên tục ở card bên phải, Day N · HH:MM:SS) — driver của batch trước vẫn có
thể đang chạy (xanh dương = đang tới điểm đón, tím = đang chở khách) trong khi request/
assignment của batch sau đã xuất hiện trên map, nhiều tuyến chồng lên nhau cùng lúc giống
`demo_fairdispatch`. Đổi speed 2×/4×/8× giữa chừng — mọi xe đang chạy tăng tốc ngay lập tức
(cùng chung 1 đồng hồ). Nếu engine chưa kịp trả batch mới, badge **BUFFERING ENGINE...** hiện
và clock tự đứng, không nhảy thời gian. Chấm cam = declined, chấm viền xám (rỗng) = infeasible.
Bấm **Pause** để đóng băng đúng vị trí hiện tại, **Run** lại để tiếp tục chính xác từ đó.
Click một marker/route trên map hoặc một dòng trong "Recent Operations" log (giữ tối đa 50
dòng gần nhất, không xoá sạch mỗi batch) — mở panel "Why this driver?" kèm **Visual phase**
(Deadheading/Passenger onboard + % progress); panel vẫn đúng dù đã sang batch mới hoặc đang
prefetch trước. Click lại đúng assignment đó (hoặc "×", hoặc Escape) để đóng.

**4. Why this driver? (~60s)** — feature quan trọng nhất
Click một dòng trong bảng Assignment. Chỉ vào panel giải thích:
- nếu driver được chọn **không** phải local rank #1, đọc to dòng cảnh báo: "Hungarian tối ưu
  tổng điểm của cả batch, không tối ưu từng request độc lập" — đây là điểm khác biệt quan
  trọng với greedy per-request, và là bằng chứng UI không nói dối về cách thuật toán thật sự
  hoạt động;
- với MOMAQL: chỉ 3 thanh Immediate Utility / Future Zone Value / Fairness Adjustment cộng
  đúng ra Final Score.

**5. Compare Policies (~60s)**
Chuyển tab. Chỉ bảng Full vs No-Forecast vs No-Fairness, badge **VERIFIED REPLAY** (5 seed,
195,508 request — không phải slice nhỏ). Đọc dòng trade-off: "Full +22,4% Utility, nhưng
No-Forecast Gini thấp hơn — đây là trade-off, không phải Full thắng tuyệt đối." Nếu còn thời
gian, bấm thêm **Live Quick Compare** để cho thấy engine tính trực tiếp trên slice nhỏ (badge
**LIVE ENGINE**, ghi rõ không thay thế verified — đã fix lỗi HTTP 500, xem `PRODUCT_FIX_PLAN.md`
Round 3).

**6. Long-Horizon (~40s)**
Chuyển tab. Kéo slider Day 1 → 14 → 21 → 37. Chỉ ra: gần như không khác biệt tới ngày 14, rồi
utility tách rõ dần — hiệu ứng look-ahead có độ trễ. Badge **VERIFIED REPLAY**.

**7. Run History / Provenance (~20s)**
Chuyển tab History, chỉ run vừa tạo. Đọc footer provenance: SHA-256 của chính
`policies.py`/`simulator.py` đang chạy (engine snapshot thật) — tách biệt rõ với Git HEAD của
repo dev (chỉ dùng để đọc data, không phải commit của engine).

## Kết (10s)

> "FairDispatch cho phép người vận hành mô phỏng và so sánh các chiến lược điều phối, hiểu vì
> sao một tài xế được chọn, và quan sát trade-off dài hạn giữa hiệu quả hệ thống và công bằng
> thu nhập."

## Nếu bị hỏi sâu (backup, không cần demo live)

- "Frontend nói chuyện với model thế nào?" → REST API đồng bộ (`POST /simulations/{id}/step`),
  không WebSocket/queue — khớp khối lượng công việc thật của một demo cục bộ.
- "Nếu bấm Run 2 lần liên tiếp?" → `stepInFlight` chặn phía frontend, `threading.Lock` chặn
  phía backend (409 nếu vẫn lọt qua) — xem `PRODUCT_FIX_PLAN.md` P0.2.
- "Số liệu này từ đâu?" → luôn phân biệt bằng badge: **LIVE ENGINE** = vừa tính từ step() thật;
  **VERIFIED REPLAY** = đọc thẳng CSV đã verify (không tính lại, không hard-code).
