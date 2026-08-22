# FAIRDISPATCH — OPERATOR CONTROL PANEL ENHANCEMENT SPEC
## Bổ sung control theo ảnh tham khảo nhưng chỉ giữ những gì thực sự hữu ích cho người vận hành

---

# 1. MỤC TIÊU

Bảng điều khiển hiện tại của FairDispatch đã có:

- Run / Pause / Step / Reset
- Playback speed
- Policy
- Fleet size
- Forecast
- λ
- Dataset / Seed / Request limit
- Service / Fairness metrics
- Leaflet map
- Continuous playback
- Why This Driver
- Compare / Replay / Long-Horizon
- Provenance / History

Ảnh tham khảo cho thấy một số UX pattern tốt:

- nút preset thay vì dropdown;
- lọc theo thời gian;
- lọc theo ngày;
- dừng sau N chuyến;
- lưu bản chạy;
- panel thu gọn;
- bố trí control compact.

Mục tiêu của vòng này là:

> **Lấy những control hữu ích cho Operator, bỏ những control mang tính demo cũ/research-specific hoặc không có semantic thật trong engine hiện tại.**

Không thêm control chỉ vì “trông chuyên nghiệp”.

---

# 2. NGUYÊN TẮC QUYẾT ĐỊNH

Một control chỉ được thêm nếu trả lời được 3 câu:

1. Người vận hành dùng nó để làm gì?
2. Nó có dữ liệu/logic thật trong engine hiện tại không?
3. Nó có ảnh hưởng rõ tới scenario, playback hoặc cách quan sát không?

Nếu không trả lời được:

> không thêm.

---

# 3. CONTROL TỪ ẢNH THAM KHẢO — PHÂN LOẠI

## A. Chạy liên tục / Một chuyến / Đặt lại

### Verdict
✅ GIỮ / PHẢI CÓ

Map sang:

```text
Run
Step
Reset
```

Giữ Pause hiện tại.

---

## B. Tốc độ 1× / 2× / 4× / 8×

### Verdict
✅ GIỮ / PHẢI CÓ

Đây là playback speed.

Phải điều khiển:

> global simulation clock

không thay đổi dispatch decision.

---

## C. Số xe song song 1 / 4 / 8

### Verdict
❌ KHÔNG DÙNG NHƯ ENGINE CONTROL

Lý do:

Số xe đang chạy đồng thời phải do simulator quyết định.

Frontend không được giới hạn:

```text
chỉ cho 4 driver chạy
```

nếu engine đang có 18 active trips.

### Có thể chuyển thành

```text
VISUAL DENSITY

[ Low ] [ Medium ] [ Full ]
```

hoặc:

```text
ROUTE TRAILS

[ Off ] [ Recent ] [ Extended ]
```

Chỉ ảnh hưởng visualization.

Không ảnh hưởng engine.

---

## D. Dừng sau 200 chuyến

### Verdict
✅ NÊN CÓ

Nhưng đổi wording thành:

```text
SIMULATION HORIZON
```

Preset:

```text
Quick Demo
Standard
Extended
Custom
```

Ví dụ:

```text
Quick Demo     200 requests
Standard       3,000 requests
Extended       10,000 requests
Custom
```

Nếu current product đang mặc định 3,000 thì giữ preset phù hợp.

Raw request limit chuyển xuống Advanced.

---

## E. Tin cậy 70 / 80 / 90%

### Verdict
❌ KHÔNG THÊM

Lý do:

Current engine không có một calibrated confidence probability rõ ràng.

Không được tạo:

```text
Confidence 90%
```

nếu không trả lời được “confidence của cái gì”.

Không fake:

- Q confidence;
- dispatch confidence;
- forecast confidence;
- fairness confidence.

Sau này chỉ thêm nếu có model uncertainty/calibration thật.

---

## F. Hiệu chỉnh q chung / theo band

### Verdict
❌ KHÔNG ĐƯA VÀO MAIN OPERATOR UI

Đây là research/debug control.

Current Operator không cần biết.

Nếu project thật sự có mode Q calibration riêng:

đặt trong:

```text
Advanced / Research
```

Nếu current engine không có semantic rõ:

> không thêm.

---

## G. Nhóm đại diện / >300k

### Verdict
❌ KHÔNG THÊM

Đây là control đặc thù demo cũ.

Không có giá trị rõ trong current FairDispatch:

- dispatch;
- service;
- fairness;
- supply;
- demand.

Không thêm chỉ vì ảnh cũ có.

---

## H. Giờ: cả ngày / 6–9 / 17–19 / 22–5

### Verdict
✅ RẤT NÊN CÓ

Đây là control có giá trị vận hành thật.

Tên:

```text
TIME SCENARIO
```

Preset:

```text
[ All Day ]
[ Morning Peak 06–09 ]
[ Evening Peak 17–19 ]
[ Night 22–05 ]
[ Custom ]
```

UI tiếng Việt có thể là:

```text
[ Cả ngày ]
[ Sáng cao điểm ]
[ Chiều cao điểm ]
[ Ban đêm ]
[ Tùy chỉnh ]
```

---

# 4. TIME FILTER SEMANTICS

Time filter phải lọc request từ dataset thật.

Không chỉnh thuật toán.

Ví dụ:

```text
17:00–19:00
```

→ chỉ replay/simulate requests có timestamp nằm trong range.

Phải ghi rõ:

```text
SCENARIO FILTER ACTIVE
Friday · 17:00–19:00
```

Không dùng result scenario slice này để thay thế canonical research results.

---

# 5. CUSTOM TIME RANGE

Cho:

```text
Start Hour
End Hour
```

Ví dụ:

```text
00h → 23h
```

Validation:

```text
0..23
```

Support overnight:

```text
22 → 05
```

phải xử lý:

```text
hour >= 22 OR hour < 5
```

không coi là invalid.

---

# 6. THỨ / NGÀY TRONG TUẦN

### Verdict
✅ NÊN CÓ

Operator thường quan tâm:

```text
Weekday vs Weekend
```

hơn từng ngày riêng lẻ.

Main UI ưu tiên:

```text
[ All ]
[ Weekday ]
[ Weekend ]
[ Custom ]
```

Custom expand:

```text
[ Mon ] [ Tue ] [ Wed ] [ Thu ] [ Fri ] [ Sat ] [ Sun ]
```

Nếu UI tiếng Việt:

```text
[ Cả tuần ]
[ Ngày thường ]
[ Cuối tuần ]
[ Tùy chỉnh ]
```

---

# 7. WEEKDAY/WEEKEND SEMANTICS

Phải map theo timestamp thật.

Ví dụ:

```text
Weekday = Mon–Fri
Weekend = Sat–Sun
```

Không hard-code row index.

---

# 8. LƯU BẢN CHẠY

### Verdict
✅ RẤT NÊN CÓ

Nâng cấp thành:

```text
SAVE RUN
```

Lưu tối thiểu:

```text
Run ID
Policy
Objective
Fleet Size
Forecast
Lambda
Seed
Dataset
Time Filter
Day Filter
Simulation Horizon
Playback settings
Metrics
Provenance
```

Có thể:

- localStorage;
- JSON export;
- Run History backend.

Nếu Run History hiện có thì tích hợp vào đó.

---

# 9. RE-RUN / REPRODUCE SCENARIO

Sau Save Run:

nếu dễ:

```text
Open
Re-run
```

Restore:

- policy;
- fleet;
- forecast;
- λ;
- seed;
- time/day filter;
- horizon.

Không cần restore playback camera state.

---

# 10. COLLAPSIBLE CONTROL SECTIONS

### Verdict
✅ PHẢI CÓ SAU KHI PANEL DÀI

Ảnh tham khảo có:

```text
thu gọn ▲
```

Đây là UX tốt.

Sections:

```text
CURRENT RUN
OPERATING OBJECTIVE
SCENARIO FILTERS
SIMULATION
SERVICE HEALTH
FAIRNESS
ALERTS
MAP LAYERS
ADVANCED / RESEARCH
```

Mỗi section có:

```text
▲ / ▼
```

Không collapse Current Run mặc định nếu không cần.

---

# 11. PRESET BUTTONS THAY DROPDOWN KHI CÓ ÍT OPTION

Đây là pattern rất đáng lấy từ ảnh.

Dùng segmented buttons cho:

## Playback Speed

```text
[1×] [2×] [4×] [8×]
```

## Objective

```text
[Efficiency] [Balanced] [Fairness]
```

## Time

```text
[All] [6–9] [17–19] [22–05]
```

## Day

```text
[All] [Weekday] [Weekend]
```

## Fleet

Nếu engine support rõ:

```text
[100] [200] [400] [Custom]
```

Không dùng dropdown cho 3–4 lựa chọn đơn giản.

---

# 12. FLEET PRESETS

Research đã có:

```text
100
200
400
```

nên có thể đưa thành preset.

Main UI:

```text
FLEET SIZE

[100] [200] [400] [Custom]
```

Canonical:

```text
200
```

Nếu user chọn Custom:

show numeric input.

Validation:

```text
> 0
<= available requests/state constraints
```

---

# 13. FORECAST CONTROL

Giữ:

```text
Forecast
ON / OFF
```

Chỉ active khi:

```text
Policy = MOMAQL
```

Non-MOMAQL:

disable.

Tooltip:

> Only applicable to MOMAQL.

---

# 14. OPERATING OBJECTIVE

Giữ từ operator-control-room design:

```text
[ Efficiency ]
[ Balanced ]
[ Fairness ]
[ Custom ]
```

Mapping:

```text
Balanced → canonical λ
```

Efficiency/Fairness mapping phải document.

Không pretend λ monotonic perfectly if empirical sweep is non-monotonic.

Do not label:

```text
Fairness = λ 1 always best operating point
```

unless explicitly intended as preset.

---

# 15. ADVANCED / RESEARCH

Đưa các raw research controls xuống:

```text
λ
γ
α
Seed
Exact Request Limit
Dataset
ETA Threshold
Batch Window
Deadhead Cost
```

Main Operator UI không cần nhìn tất cả.

---

# 16. USER-FACING PANEL TARGET

```text
┌────────────────────────────────┐
│ CURRENT RUN                    │
│ LIVE ENGINE · FD-...           │
│ Day 2 · 17:42:18               │
├────────────────────────────────┤
│ OPERATING OBJECTIVE            │
│ [Efficiency][Balanced][Fair]   │
├────────────────────────────────┤
│ SCENARIO                       │
│                                │
│ Fleet                          │
│ [100] [200] [400] [Custom]     │
│                                │
│ Forecast                       │
│ [ON] [OFF]                     │
│                                │
│ Time                           │
│ [All][6–9][17–19][22–05]       │
│                                │
│ Day                            │
│ [All][Weekday][Weekend]        │
│                                │
│ Horizon                        │
│ [Quick][Standard][Extended]    │
├────────────────────────────────┤
│ SIMULATION                     │
│ [▶ Run][Ⅱ Pause][▶| Step]      │
│ [↻ Reset]                      │
│                                │
│ Speed                          │
│ [1×][2×][4×][8×]               │
├────────────────────────────────┤
│ SERVICE HEALTH                 │
│ ...                            │
├────────────────────────────────┤
│ FAIRNESS                       │
│ ...                            │
├────────────────────────────────┤
│ ALERTS                         │
│ ...                            │
├────────────────────────────────┤
│ MAP LAYERS                     │
│ ...                            │
├────────────────────────────────┤
│ [💾 Save Run]                  │
├────────────────────────────────┤
│ ADVANCED / RESEARCH          ▼ │
└────────────────────────────────┘
```

---

# 17. DENSITY / ROUTE TRAIL CONTROL

Nếu map quá rối:

không dùng:

```text
Concurrent vehicles = 4
```

mà dùng:

```text
VISUAL DENSITY
[Low][Medium][Full]
```

hoặc:

```text
ROUTE TRAILS
[Off][Recent][Extended]
```

Visualization only.

---

# 18. SCENARIO FILTER BADGE

Khi time/day filter không phải default:

topbar/map phải show:

```text
SCENARIO FILTER ACTIVE
```

Ví dụ:

```text
Friday · 17:00–19:00
```

Giúp người xem không nhầm đây là canonical run.

---

# 19. RESEARCH INTEGRITY

Time/day/fleet/horizon scenario có thể tạo run khác canonical.

Được phép.

Nhưng:

> không cập nhật research conclusion tự động từ run demo.

Verified research replay vẫn riêng.

Main paper result vẫn từ canonical validation experiments.

---

# 20. TEST SET

Không expose held-out test như một casual scenario preset.

Test set vẫn reserved cho final evaluation.

Main Product Demo:

```text
Validation
```

Nếu Test sau này được thêm:

badge:

```text
FINAL EVALUATION
```

và không cho user tùy tiện tune rồi rerun trong Operator main flow.

---

# 21. KHÔNG THÊM CONFIDENCE

Nhắc lại:

Không:

```text
70% / 80% / 90%
```

nếu không có calibrated metric thật.

Không lấy UI element cũ chỉ vì đẹp.

---

# 22. KHÔNG THÊM Q CALIBRATION MODE

Không:

```text
q chung
theo band
```

trừ khi current engine thật có use case research rõ.

Không cần cho Operator.

---

# 23. KHÔNG THÊM REPRESENTATIVE GROUP

Không:

```text
đại diện
>300k
```

Nếu không có semantic current project.

---

# 24. SAVE RUN UI

Button:

```text
💾 Save Run
```

Click:

show confirmation:

```text
Run FD-... saved
```

Nếu export JSON:

file name:

```text
fairdispatch_run_FD-....json
```

---

# 25. SCENARIO SUMMARY

Sau khi filter active:

```text
CURRENT SCENARIO

Balanced
MOMAQL
200 drivers
Forecast ON

Friday
17:00–19:00

Validation
Standard Horizon
```

Người vận hành phải nhìn một phát hiểu.

---

# 26. FORM VALIDATION

Custom Time:

- valid hour;
- overnight allowed.

Custom Days:

- at least one day.

Custom Fleet:

- positive integer.

Custom Horizon:

- positive integer;
- warning if very large.

---

# 27. BACKEND FILTERING

Nếu backend hiện chỉ slice first N requests:

thêm optional:

```text
hour_start
hour_end
weekday_filter
```

filter trước khi request_limit.

Quan trọng:

```text
filter dataset
→ then apply request_limit
```

Không:

```text
take first 3000
→ then filter
```

vì có thể còn rất ít requests.

---

# 28. DETERMINISM

Cùng:

```text
dataset
time/day filter
request_limit
seed
policy
config
```

phải reproduce same scenario nếu engine deterministic.

Save Run phải giữ filter config.

---

# 29. API CONTRACT GỢI Ý

Simulation create request có thể mở rộng:

```json
{
  "dataset": "val",
  "policy": "MOMAQL",
  "n_drivers": 200,
  "lambda": 0.5,
  "forecast_on": true,
  "seed": 20260721,

  "request_limit": 3000,

  "time_filter": {
    "mode": "evening_peak",
    "start_hour": 17,
    "end_hour": 19
  },

  "day_filter": {
    "mode": "weekday",
    "days": [0,1,2,3,4]
  }
}
```

Không bắt buộc exact schema.

Use typed Pydantic models.

---

# 30. BACKEND METADATA RESPONSE

Return scenario summary:

```text
filtered_request_count
available_request_count
time_filter
day_filter
actual_driver_count
```

UI hiển thị đúng.

---

# 31. SCENARIO EMPTY STATE

Nếu filter:

```text
Sunday · 03:00–04:00
```

mà no request:

không crash.

Show:

```text
No requests match this scenario.
Change time/day filters.
```

---

# 32. PERFORMANCE

Time/day filtering nên được cache nếu cần.

Không reread/parquet-convert toàn file mỗi toggle nếu current request cache đã tồn tại.

Filter in memory từ cached request set là hợp lý.

---

# 33. SECTION COLLAPSE STATE

Có thể nhớ bằng localStorage:

```text
Advanced collapsed
Alerts expanded
```

Bonus.

Không cần backend.

---

# 34. UI DENSITY

Preset controls compact.

Không tăng panel height quá nhiều.

Use:

```text
segmented controls
2-column label/control rows
collapsible sections
```

Map vẫn dominant.

---

# 35. THỨ TỰ ƯU TIÊN

## MUST

1. Time-of-day presets
2. Day / Weekday / Weekend filter
3. Horizon presets
4. Save Run integration
5. Collapsible sections
6. Preset-button UX
7. Fleet presets 100/200/400 if supported
8. Scenario summary/badge

## DO NOT ADD

1. Confidence
2. Q band calibration
3. Representative group
4. Concurrent vehicle engine limiter

---

# 36. ACCEPTANCE TEST

Operator có thể:

```text
Balanced
200 drivers
Forecast ON
Friday
17:00–19:00
Standard Horizon
```

bấm Run.

UI phải ghi rõ scenario active.

Simulation dùng đúng subset data.

Save Run giữ đúng scenario.

Re-run restore đúng scenario.

---

# 37. KẾT LUẬN

Những gì nên lấy từ ảnh tham khảo:

> **preset buttons + time/day scenario filters + horizon + save + collapsible panel**

Những gì không nên lấy:

> **confidence + q calibration + representative group + concurrent-car limiter**

Mục tiêu là:

> **bảng điều khiển giàu khả năng vận hành hơn nhưng vẫn trung thực với engine hiện tại.**
---

# 38. BỔ SUNG BẮT BUỘC — LAYOUT SPACING / DENSITY

Ngoài các control/operator feature ở trên, frontend hiện tại còn một vấn đề bố cục cần sửa trong cùng vòng triển khai này:

> **Khoảng cách theo chiều dọc giữa các khu vực đang quá lớn, đặc biệt là sau hàng chart và trước Operational Log.**

Ảnh hiện tại cho thấy:

```text
Map
↓
Charts
↓



        [RẤT NHIỀU KHOẢNG TRẮNG]



↓
Operational Log
```

Điều này làm dashboard:

- nhìn loãng;
- mất cảm giác “control room”;
- phải cuộn nhiều hơn không cần thiết;
- main content không đồng bộ về mật độ với sidebar.

Mục tiêu phải trở thành:

```text
MAP
  ↓ 8–14px
ANALYTICS CHARTS
  ↓ 8–14px
OPERATIONAL LOG
```

Không được dùng negative margin để kéo các section lại.

---

# 39. AUDIT ROOT CAUSE CSS

Claude phải audit các property/layout rule có thể gây stretch:

```text
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

Đặc biệt ở:

```text
app
workspace
main content
left column
map section
analytics section
bottom/log section
sidebar
```

Tìm các pattern như:

```css
height: 100%;
min-height: ...;
flex: 1;
grid-template-rows: auto auto 1fr auto;
justify-content: space-between;
```

nếu chúng khiến một row vô hình chiếm phần còn lại của viewport.

Phải sửa root cause.

Không dùng:

```css
margin-top: -200px;
```

hoặc hack tương tự.

---

# 40. MAIN CONTENT FLOW

Nếu dùng CSS Grid, ưu tiên flow kiểu:

```css
.main-left {
    display: grid;
    grid-template-rows: auto auto auto;
    gap: 10px;
    align-content: start;
    min-height: 0;
}
```

Nếu dùng Flex:

```css
.main-left {
    display: flex;
    flex-direction: column;
    gap: 10px;
    justify-content: flex-start;
}
```

Không dùng:

```css
justify-content: space-between;
```

cho container chứa:

```text
Map
Charts
Operational Log
```

---

# 41. OPERATIONAL LOG VỊ TRÍ

Operational Log phải nằm ngay dưới Analytics.

Target:

```text
Charts
↓ khoảng 10px
Operational Log
```

Operational Log không được bị neo xuống đáy viewport.

Nếu table dài:

```css
.operations-table-wrap {
    max-height: 180px - 240px;
    overflow-y: auto;
}
```

hoặc giá trị responsive tương đương.

Header table có thể sticky.

Không để outer log card tự chiếm vài trăm pixel trống.

---

# 42. ANALYTICS HEIGHT

Các chart:

```text
Driver Income Distribution
Lorenz Curve
```

không cần parent row quá cao.

Desktop target khoảng:

```text
180–260px
```

tùy viewport.

Có thể dùng:

```css
.analytics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
```

và:

```css
.analytics-card {
    height: clamp(180px, 22vh, 240px);
}
```

nếu phù hợp code hiện tại.

Không đặt analytics container kiểu:

```text
height: 40vh
```

nếu tạo khoảng trắng.

---

# 43. MAP HEIGHT

Map vẫn phải là visual trung tâm.

Ở 1920×1080:

```text
Map khoảng 430–520px
```

là reasonable target.

Không giảm map quá nhiều chỉ để nhét control.

Visual rhythm mong muốn:

```text
Header / Tabs
Map
10px
Charts
10px
Operational Log
```

---

# 44. SIDEBAR PHẢI SCROLL ĐỘC LẬP

Right sidebar sau khi bổ sung:

- Current Run
- Operating Objective
- Scenario
- Simulation
- Service Health
- Fairness
- Alerts
- Map Layers
- Advanced / Research

sẽ dài.

Phải cho sidebar scroll độc lập.

Ví dụ:

```css
.workspace {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: 10px;
    align-items: start;
}

.sidebar {
    position: sticky;
    top: ...;
    max-height: calc(100vh - ...);
    overflow-y: auto;
}
```

Điểm quan trọng:

> Sidebar không được ép chiều cao của left content.

---

# 45. SECTION DENSITY

Desktop target:

```text
Main grid gap           8–12px
Card internal padding  10–14px
Section margin          8–12px
Control row gap          4–8px
Segmented control h     30–34px
```

Không để mỗi section cách nhau 20–40px trừ khi có lý do.

Bảng điều khiển phải compact nhưng vẫn đọc được.

---

# 46. OPERATIONAL LOG DENSITY

Table nên:

```text
row height khoảng 28–34px
```

Cell padding khoảng:

```text
5–8px vertical
8–10px horizontal
```

Không stretch cột vô nghĩa.

Giữ:

- Req
- Driver
- Fare
- Pickup Zone
- Dropoff Zone

gọn và scan nhanh.

Numeric column:

- right-aligned;
- `font-variant-numeric: tabular-nums`.

---

# 47. CONTROL PANEL DENSITY

Các segmented button:

```text
Objective
Fleet
Time
Day
Speed
Horizon
```

nên compact.

Không để control panel dài chỉ vì padding/margin quá lớn.

Các section đã có collapsible behavior phải được tận dụng.

---

# 48. BROWSER ZOOM

Không thiết kế dựa trên browser zoom 33%.

Bắt buộc QA ở:

```text
100% browser zoom
```

với:

```text
1920×1080
1600×900
1366×768
```

---

# 49. RESPONSIVE ACCEPTANCE

## 1920×1080

- map vẫn là vùng chính;
- chart ngay dưới map;
- log ngay dưới chart;
- không có vùng trắng khổng lồ;
- sidebar gọn.

## 1600×900

- layout vẫn cùng cấu trúc;
- sidebar tự scroll khi cần.

## 1366×768

- map usable;
- analytics compact;
- log có internal scroll;
- sidebar không kéo left column cao bất thường.

---

# 50. KHÔNG LÀM REGRESSION KHI SỬA SPACING

Spacing/layout fix không được làm mất:

- Leaflet map;
- continuous playback;
- global simulation clock;
- route trails;
- Why This Driver;
- Operator controls;
- chart rendering;
- Operational Log;
- Compare / Replay / Long-Horizon.

Mục tiêu chỉ là:

> **sắp xếp chặt và đúng hơn, không cắt chức năng.**

---

# 51. VISUAL ACCEPTANCE TARGET

Không chấp nhận:

```text
MAP
CHARTS



huge blank



LOG
```

Phải thành:

```text
MAP
↓ 8–14px
CHARTS
↓ 8–14px
LOG
```

Đây là một acceptance criterion bắt buộc cùng với các control/operator feature trong tài liệu này.
