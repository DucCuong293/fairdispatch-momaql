# FAIRDISPATCH — OPERATOR CONTROL ROOM PRODUCT REQUIREMENTS
## Nâng cấp bảng điều khiển từ Research Simulation UI thành Operations Decision-Support Control Room

---

# 1. MỤC TIÊU

Sản phẩm FairDispatch hiện tại đã có nền tảng tốt:

- Live Simulation;
- Leaflet real map;
- continuous playback;
- MOMAQL / baseline policies;
- Run / Pause / Step / Reset;
- playback speed;
- Utility / Gini;
- assignment explanation;
- Full vs No Forecast;
- Long-Horizon;
- Driver income distribution;
- Lorenz;
- provenance;
- run history;
- verified research replay.

Vòng nâng cấp này **không nhằm thêm algorithm mới**.

Mục tiêu là làm cho bảng điều khiển nói đúng ngôn ngữ của:

- Operation Manager;
- Dispatch Engineer;
- Product/App Engineer;
- Research Engineer.

Sản phẩm phải chuyển từ:

> **Research simulation interface**

sang:

> **Operations decision-support control room**

mà vẫn giữ toàn bộ correctness của research engine.

---

# 2. NGUYÊN TẮC SẢN PHẨM

Một Operator không muốn nhìn hàng loạt tham số kỹ thuật trước tiên.

Họ muốn biết:

1. Hệ thống đang vận hành tốt không?
2. Có đủ tài xế không?
3. Khách có được phục vụ không?
4. Khách phải chờ bao lâu?
5. Khu vực nào đang thiếu xe?
6. Thu nhập tài xế có đang quá chênh lệch không?
7. Policy hiện tại đang ưu tiên Efficiency hay Fairness?
8. Có cảnh báo nào cần xử lý không?
9. Nếu đổi chiến lược thì trade-off sẽ thay đổi thế nào?
10. Tôi có thể click vào đâu để hiểu một quyết định cụ thể?

Researcher thì vẫn cần:

- λ;
- γ;
- α;
- seed;
- Q;
- request limit;
- dataset;
- provenance.

Vì vậy UI phải có **hai lớp thông tin**:

```text
Operator-facing controls
        ↓
Advanced / Research controls
```

---

# 3. OPERATING OBJECTIVE — MUST HAVE

Không bắt Operator bắt đầu bằng:

```text
λ = 0.5
```

Thêm nhóm:

```text
OPERATING OBJECTIVE

[ Efficiency ] [ Balanced ] [ Fairness ] [ Custom ]
```

Ý nghĩa:

## Efficiency

Ưu tiên hiệu quả kinh tế.

Có thể map sang λ thấp.

## Balanced

Điểm vận hành cân bằng.

Mặc định có thể map sang λ = 0.5 nếu đúng canonical config hiện tại.

## Fairness

Ưu tiên phân phối thu nhập đồng đều hơn.

Có thể map sang λ cao.

## Custom

Mở slider/input λ.

Quan trọng:

> Mapping phải dựa vào config thật của engine.

Không invent preset không tồn tại.

---

# 4. KHÔNG ẨN HOÀN TOÀN λ

λ vẫn cần tồn tại.

Nhưng nên đặt ở:

```text
Advanced / Research
```

hoặc chỉ hiện khi:

```text
Objective = Custom
```

Tooltip:

> Controls the Utility–Fairness weighting in the current MOMAQL implementation.

Không nói λ của project tương đương λ của paper.

---

# 5. CONTROL PANEL NÊN CHIA THÀNH 5 NHÓM

## A. Current Run

## B. Operating Objective

## C. Simulation / Playback

## D. Service Health + Fairness

## E. Alerts + Map Layers

Cuối cùng:

## Advanced / Research ▸

---

# 6. CURRENT RUN SUMMARY — MUST HAVE

Panel đầu tiên:

```text
CURRENT RUN

LIVE ENGINE
FD-20260821-0124

Policy       MOMAQL
Objective    Balanced
Drivers      200
Forecast     ON

Dataset      Validation
Live Slice   3,000 / 195,508
Seed         20260721
```

Nếu đang replay:

```text
VERIFIED REPLAY
```

Không trộn Live với Replay.

---

# 7. RUN STATE — MUST HAVE

Hiển thị rõ:

```text
ENGINE        READY / RUNNING / BUFFERING / DONE
PLAYBACK      RUNNING / PAUSED
SIM TIME      Day 2 · 17:42:18
SPEED         2×
ACTIVE TRIPS  18
QUEUE         4 batches
```

Không bắt buộc show tất cả nếu chật.

Tối thiểu:

- Engine Status;
- Simulation Time;
- Playback Speed;
- Active Trips.

---

# 8. SIMULATION CONTROLS — MUST HAVE

Giữ:

```text
▶ Run
Ⅱ Pause
▶| Step
↻ Reset
```

Playback Speed:

```text
[ 1× ] [ 2× ] [ 4× ] [ 8× ]
```

Có thể thêm 0.5× nếu cần.

Không làm thay đổi dispatch decision.

Speed chỉ tác động:

> visual simulation clock.

---

# 9. SERVICE RATE — MUST HAVE

Operator rất quan tâm request có được phục vụ không.

Hiển thị:

```text
SERVICE RATE

Requests this window     42
Assigned                 36
Declined                  4
Infeasible                2

Service Rate           85.7%
Target                 ≥90%
```

Có progress bar nhẹ.

Metric phải lấy từ engine state thật.

---

# 10. PICKUP ETA — MUST HAVE

Không chỉ biết request được assign.

Phải biết khách chờ bao lâu.

Show:

```text
PICKUP ETA

Average      3.8 min
P90          7.2 min
Worst        9.8 min
```

Nếu backend hiện chưa aggregate:

tính từ:

```text
pickup_eta_seconds
```

của actual assignments.

Không hard-code.

---

# 11. DEMAND / SUPPLY — MUST HAVE

Show:

```text
DEMAND / SUPPLY

Active Requests       42
Available Drivers     27

Demand / Supply       1.56×

Status
SUPPLY SHORTAGE
```

Nếu current batch data support.

Definition phải rõ.

Ví dụ:

```text
Demand = requests in current window
Supply = feasible/available drivers
```

Không dùng khái niệm mơ hồ.

---

# 12. SUPPLY / DEMAND THEO ZONE — RẤT NÊN CÓ

Nếu dữ liệu đủ:

```text
Zone                  Demand   Drivers   Status

Midtown                  21        8      HIGH
Upper East Side          13       14      OK
Queens                    9        3      HIGH
```

Chỉ top N zone đáng chú ý.

Không cần bảng 67 zone trong main panel.

---

# 13. MAP LAYERS — MUST HAVE

Thêm:

```text
MAP LAYERS

☑ Drivers
☑ Requests
☑ Active Routes
☑ Recent Trails

☐ Declined Requests
☐ Infeasible Requests
☐ Demand Heatmap
☐ Supply Heatmap
☐ Driver Income Layer
```

Chỉ bật layer mà data thật support.

Nếu heatmap chưa support backend:

có thể aggregate từ current request/driver coordinates.

Không invent demand forecast layer nếu không có data.

---

# 14. ROUTE TRAIL CONTROL — RẤT NÊN CÓ

```text
ROUTE TRAILS

○ Off
● Recent
○ Extended
```

Chỉ điều khiển visualization retention.

Không thay đổi engine.

---

# 15. DEMAND HEATMAP — RẤT NÊN CÓ

Leaflet layer:

> current observed demand density.

Không gọi là forecast nếu chỉ từ current/recent requests.

Label đúng:

```text
Observed Demand
```

Nếu forecast layer thật tồn tại:

có thể tách:

```text
Forecast Demand
```

---

# 16. SUPPLY HEATMAP — RẤT NÊN CÓ

Dựa vào:

- idle/available driver positions;
- feasible driver distribution.

Giúp Operator thấy:

> driver tập trung ở đâu.

---

# 17. FAIRNESS OVERVIEW — MUST HAVE

Không chỉ Gini gauge.

Show:

```text
FAIRNESS

Gini                  0.204
Status                 Moderate

Fleet Mean Income      $283
Bottom 10% Avg         $154
Top 10% Avg            $471

Top / Bottom           3.06×
```

Nếu current run chưa đủ driver/trip:

show N/A đúng cách.

---

# 18. FAIRNESS GUARDRAIL — MUST HAVE

Operator có thể đặt:

```text
Maximum Gini
0.25
```

Option:

```text
☑ Alert when exceeded
```

Không tự đổi policy.

Chỉ tạo alert.

Ví dụ:

```text
⚠ FAIRNESS LIMIT EXCEEDED

Current Gini    0.271
Limit           0.250
```

---

# 19. SERVICE GUARDRAILS — RẤT NÊN CÓ

Panel:

```text
SERVICE TARGETS

Minimum Service Rate      90%
Maximum Pickup P90         8m
Maximum Gini              0.25
```

Status:

```text
Service Rate       93%     ✓
Pickup P90         9.2m    ⚠
Gini               0.204   ✓
```

Chỉ alert.

Không tự thay đổi engine.

---

# 20. ALERT CENTER — MUST HAVE

Một Operator không nên tự nhìn 10 biểu đồ để tìm vấn đề.

Panel:

```text
ALERTS

⚠ Midtown demand exceeds supply 2.1×

⚠ Pickup ETA P90 reached 9.2 min

✓ Fairness within configured threshold

✓ No infeasible-request spike
```

Severity:

```text
CRITICAL
WARNING
INFO / OK
```

Không cần notification backend phức tạp.

Rule-based frontend/backend state là đủ.

---

# 21. ALERT PHẢI CLICK ĐƯỢC — RẤT NÊN CÓ

Ví dụ:

```text
⚠ Supply shortage in Zone 43
```

Click:

- zoom map tới zone/area;
- bật relevant layer;
- highlight request/driver cluster nếu có.

---

# 22. SEARCH — RẤT NÊN CÓ

Field:

```text
Find
[ Driver / Request / Zone __________ ]
```

Support tối thiểu:

- Driver ID;
- Request ID.

Nếu zone naming dễ:

- Zone ID/name.

Action:

- highlight;
- pan/zoom;
- open detail.

---

# 23. FOLLOW DRIVER — RẤT NÊN CÓ

Trong Driver Detail:

```text
[ Follow Driver ]
```

Khi bật:

- map pan nhẹ theo moving marker;
- không auto zoom liên tục.

Panel:

```text
FOLLOWING DRIVER #73

Income            $287
Trips              31
vs Fleet Mean      +9.2%
Status             Passenger onboard
Destination        Zone 17
Available in       6m 18s
```

Chỉ show field thật.

---

# 24. DRIVER DETAIL / RANKING — RẤT NÊN CÓ

Driver Ranking:

```text
Driver
Trips
Income
vs Fleet Mean
Status
Zone
```

Filter:

```text
Highest income
Lowest income
Largest deviation
```

Không cần 200 row cùng lúc.

Top/bottom 10 là đủ.

---

# 25. WHY THIS DRIVER — GIỮ NGUYÊN SIGNATURE FEATURE

Không làm regression.

Phải tiếp tục show:

```text
Request
Pickup
Dropoff
Fare

Selected Driver
Pickup ETA
Current Income

Immediate Utility
Future Zone Value
Fairness Adjustment
Final Score

Local Candidate Rank
Selected by Hungarian Global Assignment
```

Nếu selected rank != #1:

show:

```text
GLOBAL OPTIMUM
```

---

# 26. WHAT-IF — MUST HAVE / VERY HIGH VALUE

Operator cần hỏi:

> Nếu đổi policy thì sao?

Ngay trong Control Room có thể có:

```text
WHAT IF?

Current
MOMAQL · Balanced

Compare with
[ No Forecast ▼ ]

[ Run What-if ]
```

Mini-result:

```text
                     Current      Alternative

Utility               ...             ...
Gini                  ...             ...
Service Rate          ...             ...
Pickup ETA            ...             ...
```

Nếu dùng verified artifact:

badge:

```text
VERIFIED REPLAY
```

Nếu run live quick compare:

badge:

```text
LIVE ENGINE — QUICK SLICE
```

Không trộn.

---

# 27. WHAT-IF FULL VS NO FORECAST — MUST HAVE

Interpretation:

```text
Full
Higher Utility

No Forecast
More Equal Income
```

Không gọi Full là overall winner.

---

# 28. WHAT-IF FULL VS NO FAIRNESS — RẤT NÊN CÓ

Show:

- Utility;
- Gini;
- variance nếu có.

Interpretation:

> Removing fairness increases inequality in this implementation.

Không nói Utility direction khác raw result.

---

# 29. FLEET WHAT-IF — BONUS

Nếu engine support đủ nhanh:

```text
What if fleet = 100 / 200 / 400?
```

Có thể dùng verified fleet replay nếu muốn nhanh.

Badge phải rõ.

Không hard-code result.

---

# 30. SCENARIO PRESETS — RẤT NÊN CÓ

```text
SCENARIO PRESET

[ Balanced Default ▼ ]

Balanced Default
Efficiency Focus
Fairness Focus
Supply Shortage
Custom
```

Preset phải map vào config thật.

Không invent synthetic “High Demand” nếu không có scenario data thật.

---

# 31. SAVE SCENARIO — BONUS

Lưu config:

```text
policy
drivers
lambda
forecast
dataset
seed
horizon/request slice
```

Không cần user account.

Local storage hoặc export JSON là đủ.

---

# 32. BASIC VS ADVANCED

Main panel không show quá nhiều research parameter.

## OPERATIONS

```text
Objective
Policy
Fleet Size
Forecast
Scenario
```

## PLAYBACK

```text
Run
Pause
Step
Speed
```

## ADVANCED / RESEARCH ▸

```text
λ
γ
α
Seed
Request Limit
Dataset
ETA Threshold
Batch Window
Deadhead Cost
```

Chỉ editable nếu engine support.

---

# 33. SEED — ĐƯA XUỐNG ADVANCED

Không để Seed là primary operator control.

Tooltip:

> Deterministic initialization for reproducible runs.

---

# 34. REQUEST LIMIT — ĐỔI USER-FACING LANGUAGE

Thay raw:

```text
Request Limit = 3000
```

bằng:

```text
SIMULATION HORIZON

Quick Demo
3,000 requests

Medium
10,000 requests

Full Validation

Custom
```

Advanced mới show raw count.

---

# 35. DATA SOURCE — MUST HAVE

Panel:

```text
DATA SOURCE

NYC TLC 2013
Validation Split

Live Slice
3,000 / 195,508 requests
```

Nếu sau này có Test:

label:

```text
Held-out Test
FINAL EVALUATION
```

Không dùng test trong live demo mặc định.

---

# 36. OPERATOR VIEW / RESEARCH VIEW — BONUS RẤT HAY

Toggle:

```text
[ Operator View ] [ Research View ]
```

## Operator

Show:

- Objective;
- Service Health;
- ETA;
- Supply/Demand;
- Alerts;
- Guardrails.

Hide/collapse:

- α;
- γ;
- seed;
- provenance details.

## Research

Show:

- λ;
- γ;
- α;
- seed;
- Q/debug;
- provenance;
- raw metrics.

Nếu implementation quá lớn:

> dùng Advanced/Research collapsible thay vì full two-view mode.

---

# 37. KHÔNG THÊM MANUAL DISPATCH OVERRIDE

Không thêm:

```text
Force Assign Driver
```

Engine hiện là research simulator.

Manual override sẽ phá:

- decision consistency;
- explainability;
- evaluation semantics.

Để Future Work.

---

# 38. KHÔNG THÊM DRIVER REPOSITION BUTTON NẾU ENGINE CHƯA SUPPORT

Không thêm:

```text
Send 20 drivers to Midtown
```

nếu simulator chưa có reposition action thật.

Có thể:

- detect shortage;
- alert;
- show suggested area.

Nhưng không giả action.

---

# 39. KHÔNG THÊM PRODUCTION FEATURE NGOÀI SCOPE

Không cần hiện tại:

- Login;
- Payment;
- Customer app;
- Driver app;
- Surge pricing;
- incident management;
- GPS telemetry;
- production failover;
- Kafka;
- Kubernetes;
- AI chatbot.

---

# 40. 8 FEATURE ƯU TIÊN CAO NHẤT

Nếu chỉ làm một vòng nâng cấp nữa, ưu tiên:

## P1

1. **Operating Objective Presets**
   - Efficiency / Balanced / Fairness / Custom

2. **Service Rate**
   - Assigned / Declined / Infeasible / %

3. **Pickup ETA**
   - Average / P90

4. **Demand / Supply**
   - requests vs available/feasible drivers

5. **Map Layer Control**
   - driver/request/routes/trails/heatmaps

6. **Fairness Guardrail**
   - max Gini

7. **Alert Center**
   - shortage / high ETA / fairness threshold

8. **Search / Follow Driver**

---

# 41. NICE-TO-HAVE SAU P1

- Driver Ranking;
- Driver Detail;
- Scenario Presets;
- Save Scenario;
- What-if Fleet;
- Operator / Research toggle;
- Top/Bottom income summary;
- click alert → zoom;
- route-trail density.

---

# 42. PANEL LAYOUT MỤC TIÊU

```text
┌────────────────────────────────┐
│ CURRENT RUN                    │
│ LIVE ENGINE                    │
│ FD-20260821-0124               │
│ Day 2 · 17:42:18               │
├────────────────────────────────┤
│ OPERATING OBJECTIVE            │
│                                │
│ Efficiency Balanced Fairness   │
│             ●                  │
│                                │
│ Policy          MOMAQL         │
│ Fleet           200            │
│ Forecast        ON             │
├────────────────────────────────┤
│ SIMULATION                     │
│                                │
│ ▶ Run   Ⅱ Pause   ▶| Step      │
│                                │
│ Speed  1×  2×  4×  8×         │
├────────────────────────────────┤
│ SERVICE HEALTH                 │
│                                │
│ Service Rate        92.4% ✓    │
│ Pickup ETA Avg      3.8m  ✓    │
│ Pickup ETA P90      7.4m  ✓    │
│ Demand/Supply       1.3×  ⚠    │
├────────────────────────────────┤
│ FAIRNESS                       │
│                                │
│ Gini                 0.204     │
│ Target               ≤0.25 ✓   │
│ Income gap           2.4×      │
├────────────────────────────────┤
│ ALERTS                         │
│                                │
│ ⚠ Midtown supply shortage      │
│ ✓ Fairness within threshold    │
├────────────────────────────────┤
│ MAP LAYERS                     │
│ ☑ Drivers                      │
│ ☑ Requests                     │
│ ☑ Active routes                │
│ ☐ Demand heatmap               │
│ ☐ Income layer                 │
├────────────────────────────────┤
│ ADVANCED / RESEARCH ▸          │
└────────────────────────────────┘
```

---

# 43. ADVANCED PANEL TARGET

```text
ADVANCED / RESEARCH

λ                 0.5
γ                 0.9
α                 0.1

Seed              20260721

Dataset
Validation

Request Limit     3000

ETA Threshold     600 sec
Batch Window       60 sec
Deadhead Cost      0.0025
```

Nếu fixed:

```text
600 sec · fixed
```

Không tạo input giả.

---

# 44. KPI VISUAL ALIGNMENT

Mọi numeric value:

```css
font-variant-numeric: tabular-nums;
```

Rows:

```text
Service Rate             92.4%
Pickup ETA Avg            3.8m
Pickup ETA P90            7.4m
Demand/Supply             1.3×
Gini                     0.204
```

Values phải nằm cùng một cột.

---

# 45. HEALTH STATUS SEMANTICS

Không dùng màu tùy tiện.

Có thể:

```text
Good     green
Warning  amber
Critical red
Neutral  gray/navy
```

Không biến cả dashboard thành đèn giao thông.

---

# 46. THRESHOLDS

Threshold mặc định phải:

- configurable;
- ghi rõ chỉ là operational guardrail;
- không được nói là threshold từ paper nếu không phải.

Ví dụ:

```text
Service rate target = user-defined
Gini target = user-defined
Pickup P90 max = user-defined
```

---

# 47. ALERT RULES

Ví dụ:

```text
if service_rate < min_service_rate
→ warning

if pickup_eta_p90 > max_pickup_p90
→ warning

if gini > max_gini
→ warning

if demand_supply_ratio > threshold
→ warning
```

Threshold supply shortage phải document.

---

# 48. 30-SECOND OPERATOR TEST

Trong 30 giây, user phải trả lời được:

1. Policy nào đang chạy?
2. Objective hiện tại là gì?
3. Bao nhiêu driver?
4. Active trips bao nhiêu?
5. Request service rate bao nhiêu?
6. Pickup ETA hiện thế nào?
7. Demand có vượt supply không?
8. Utility thế nào?
9. Fairness có vượt guardrail không?
10. Alert nào cần chú ý?

Nếu không:

> simplify panel.

---

# 49. PRODUCT MESSAGE

Sản phẩm phải truyền tải:

> **FairDispatch giúp người vận hành quan sát trạng thái điều phối, kiểm soát mục tiêu Utility–Fairness, phát hiện thiếu cung hoặc suy giảm service quality, và so sánh các chiến lược dispatch mà không làm mất khả năng truy vết research.**

---

# 50. ACCEPTANCE CRITERIA

## Operator Controls
- [ ] Objective presets
- [ ] Policy/Fleet/Forecast visible
- [ ] Research parameters moved to Advanced
- [ ] Playback controls remain clear

## Service Health
- [ ] Service Rate
- [ ] Assigned/Declined/Infeasible
- [ ] Pickup ETA Avg
- [ ] Pickup ETA P90
- [ ] Demand/Supply

## Fairness
- [ ] Gini
- [ ] Guardrail
- [ ] Fleet mean income
- [ ] Top/Bottom income summary where supported

## Alerts
- [ ] Service alert
- [ ] ETA alert
- [ ] Fairness alert
- [ ] Supply shortage alert

## Map
- [ ] Layer toggles
- [ ] Drivers
- [ ] Requests
- [ ] Routes
- [ ] Trails
- [ ] Demand/Supply overlays if implemented

## Investigation
- [ ] Search Driver/Request
- [ ] Follow Driver if implemented
- [ ] Why This Driver preserved

## Research Integrity
- [ ] No fake metrics
- [ ] No fake actions
- [ ] Live vs Replay remains clear
- [ ] No test-set leakage
- [ ] Existing research conclusion unchanged

---

# 51. ƯU TIÊN

Thứ tự:

```text
P1.1 Objective Presets
P1.2 Service Rate
P1.3 Pickup ETA Avg/P90
P1.4 Demand/Supply
P1.5 Map Layers
P1.6 Fairness Guardrail
P1.7 Alert Center
P1.8 Search/Follow Driver
```

Sau đó mới:

```text
Driver Ranking
Scenario Presets
Operator/Research View
Fleet What-if
Save Scenario
```

---

# 52. KHÔNG ĐƯỢC LÀM REGRESSION

Phải giữ nguyên những gì current product đã làm tốt:

- Leaflet map;
- continuous city playback;
- global simulation clock;
- playback speed;
- pause/resume;
- batch buffer;
- actual Hungarian-selected driver;
- Why This Driver;
- income histogram;
- Lorenz;
- Full vs No Forecast;
- Live Quick Compare;
- Verified Replay;
- Long-Horizon;
- provenance;
- history;
- validation;
- tests.

---

# 53. KẾT LUẬN PRODUCT

Bảng điều khiển tốt không phải bảng có nhiều nút nhất.

Bảng điều khiển tốt là bảng cho đúng người biết:

> **hệ thống đang có vấn đề gì và tôi cần chú ý vào đâu.**

FairDispatch cần giữ hai lớp:

```text
Operator:
Service / Supply / ETA / Alerts / Guardrails

Researcher:
λ / γ / α / Seed / Q / Provenance
```

Đây là hướng nâng cấp chính.
