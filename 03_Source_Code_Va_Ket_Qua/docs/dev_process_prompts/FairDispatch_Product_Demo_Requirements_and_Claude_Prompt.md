# FAIRDISPATCH — PRODUCT DEMO REQUIREMENTS & CLAUDE CODE IMPLEMENTATION PROMPT

# PHẦN A — TOÀN BỘ TƯ VẤN SẢN PHẨM TỪ GÓC NHÌN APP/PRODUCT EXPERT

Nếu tôi là người làm **app/product engineering** và vừa nghe xong phần research của bạn, tôi sẽ không muốn thấy thêm một dashboard chứa các biểu đồ giống phần thuyết trình. Tôi sẽ muốn thấy một câu trả lời rất cụ thể:

> **“Research này khi biến thành sản phẩm thì người dùng có thể làm được gì với nó?”**

Với FairDispatch, sản phẩm hợp lý nhất không phải một “app gọi xe hoàn chỉnh kiểu Grab”, vì project của bạn chưa giải toàn bộ bài toán đó. Sản phẩm nên là một **Dispatch Simulation & Decision Dashboard**: cho phép người vận hành nhìn thấy request, driver, cách policy phân chuyến, tác động của quyết định lên Utility/Fairness và so sánh các chiến lược điều phối.

Nếu bạn làm đúng hướng đó, tôi sẽ đánh giá rất cao vì nó nối được:

> **Paper → Algorithm → Experiment → Product behavior.**

---

# 1. Nếu tôi là app expert, điều đầu tiên tôi muốn hiểu là “Ai dùng sản phẩm này?”

Tôi sẽ hỏi bạn ngay:

> “Sản phẩm này làm cho ai?”

Câu trả lời tốt nhất theo project hiện tại không phải:

> “Cho khách hàng đặt xe.”

Mà nên là:

> **“Cho người vận hành hệ thống ride-hailing hoặc research/operation team thử nghiệm và quan sát các chiến lược dispatch trước khi áp dụng.”**

Tức user chính có thể là:

**Operation Manager / Dispatch Engineer / Data Scientist / Research Engineer.**

Họ muốn biết:

> Với cùng một tập request và cùng một fleet, nếu tôi chạy Greedy, LAF, MOMAQL hay bỏ Forecast thì hệ thống sẽ phân xe khác nhau thế nào và kết quả kinh tế/công bằng thay đổi ra sao?

Ngay khi bạn nói được như vậy, app có mục tiêu rất rõ.

---

# 2. Tôi sẽ muốn nhìn thấy một “Control Room”, không phải một trang web nhiều menu

Nếu tôi thiết kế sản phẩm cho bạn, màn hình chính gần như sẽ như thế này:

```text
┌─────────────────────────────────────────────────────────────────┐
│ FairDispatch           Scenario: NYC Validation     RUNNING ●   │
├───────────────┬────────────────────────────────┬────────────────┤
│               │                                │                │
│  CONTROLS     │                                │   KPI          │
│               │                                │                │
│ Policy        │            MAP                 │ Utility        │
│ MOMAQL        │                                │ $1.42M         │
│               │      Drivers + Requests        │                │
│ Drivers 200   │        + Assignment            │ Gini           │
│ λ 0.5         │                                │ 0.204          │
│ Forecast ON   │                                │                │
│ Seed 42       │                                │ Served trips   │
│               │                                │ ...            │
│ [Run]         │                                │                │
│ [Pause]       │                                │                │
├───────────────┴────────────────────────────────┴────────────────┤
│ Timeline        Day 1 ───── Day 14 ───── Day 21 ───── Day 37  │
├─────────────────────────────────────────────────────────────────┤
│ Assignment / Driver / Request details                           │
└─────────────────────────────────────────────────────────────────┘
```

Đây là kiểu màn hình tôi muốn bạn hướng tới.

Không cần đẹp cầu kỳ.

Quan trọng là **tôi nhìn một phát hiểu hệ thống đang làm gì**.

---

# 3. Phần quan trọng nhất phải là bản đồ

Vì đây là ride-hailing.

Nếu demo sản phẩm mà phần trung tâm chỉ là:

> bảng số liệu + chart

thì tôi sẽ thấy nó giống research dashboard hơn là ứng dụng vận hành.

Tôi muốn thấy:

- các zone;
- vị trí driver;
- request mới;
- pickup;
- destination;
- assignment mà policy vừa chọn;
- driver đang busy hay idle.

Ví dụ driver có thể là các điểm nhỏ.

Request có thể hiển thị:

```text
Pickup Zone 12
       ↓
Dropoff Zone 31
Fare $18.40
```

Khi MOMAQL chọn Driver 24:

```text
Driver 24
    ↓ deadhead
Pickup
    ↓ trip
Dropoff
```

Chỉ vậy thôi đã khiến algorithm của bạn từ một công thức trở thành **một hệ thống đang ra quyết định**.

---

# 4. Tôi muốn có nút “Step” hơn cả animation đẹp

Đây là một feature tôi cực kỳ muốn bạn có.

Ngoài:

> Run

hãy có:

> **Step / Next Batch**

Ví dụ:

```text
[◀]  [▶ Next Batch]  [Run]  [Pause]
```

Khi tôi bấm Next Batch:

```text
T = 08:31:00

12 requests arrive
27 feasible drivers
↓
MOMAQL scores assignments
↓
9 requests assigned
3 declined
```

Sau đó map cập nhật.

Tại sao feature này rất giá trị?

Vì mentor có thể nhìn thấy:

> **algorithm thực sự đang hoạt động từng bước.**

Nó tốt hơn nhiều so với một animation chạy nhanh mà người xem không hiểu chuyện gì vừa xảy ra.

---

# 5. Tôi đặc biệt muốn click vào một assignment và hỏi: “Tại sao chọn driver này?”

Đây có thể trở thành feature ấn tượng nhất của sản phẩm.

Ví dụ click vào:

> Request #1842

App hiện:

```text
Request
Pickup: Zone 42
Destination: Zone 17
Fare: $21.50
```

Sau đó:

```text
Selected Driver: #73
Current income: $245
Pickup ETA: 180 sec

Immediate Utility       +18.60
Future Zone Value        +4.20
Fairness Adjustment      +1.30
--------------------------------
Final Score             24.10
```

Và bên dưới:

```text
Other candidates

Driver 14      22.90
Driver 31      20.41
Driver 73      24.10   ← selected
```

Đây là lúc research của bạn biến thành **explainable product**.

Người làm app nhìn vào sẽ hiểu ngay:

> “À, engine này không chỉ trả về driver ID. Nó còn giải thích được quyết định.”

Đây là điểm cực mạnh.

---

# 6. Tôi muốn có một Compare Mode

Với project của bạn, đây gần như là feature bắt buộc.

Một nút:

> **Compare Policies**

Sau đó:

```text
Scenario cố định:
Dataset = validation
Drivers = 200
Seed = 42
```

Chọn:

```text
A: Full MOMAQL
B: No Forecast
```

App chạy cùng một scenario rồi trả:

| Metric | Full | No Forecast | Difference |
|---|---:|---:|---:|
| Utility | 1.42M | 1.16M | **+22.4%** |
| Gini ↓ | 0.204 | **0.146** | Full less fair |
| Served trips | ... | ... | ... |
| Avg deadhead | ... | ... | ... |

Ngay dưới đó:

```text
TRADE-OFF

Full
↑ Higher Utility

No Forecast
↑ Better Fairness
```

Đây chính là kết quả research quan trọng nhất của bạn được đưa vào product.

---

# 7. Tôi còn muốn Compare Mode có Full vs No Fairness

Vì điều này giải thích trực tiếp vì sao fairness component tồn tại.

Ví dụ:

```text
Full                No Fairness

Utility             Utility
1.42M               0.90M

Gini                Gini
0.204               0.450
```

Rồi app có một câu interpretation:

> Removing the fairness component significantly increases income inequality in this simulation.

Không cần dùng AI để viết câu đó.

Nó chỉ cần là interpretation rule từ experiment.

---

# 8. KPI panel nên cực kỳ ít

Đừng làm một dashboard với 15 KPI.

Ở màn hình chính tôi chỉ muốn khoảng:

| KPI | Ý nghĩa |
|---|---|
| **Total Utility** | hệ thống tạo ra bao nhiêu giá trị |
| **Gini** | mức inequality |
| **Served Requests** | bao nhiêu chuyến được phục vụ |
| **Average Driver Income** | mức thu nhập trung bình |
| **Income Range / Std** | độ phân tán |
| **Average Deadhead** | chi phí vận hành |

Và nếu muốn rất sát paper:

> Variance.

Nhưng không cần biến màn hình thành Excel.

---

# 9. Fairness phải được giải thích ngay trên UI

Vì user không chuyên sẽ nhìn:

> Gini = 0.204

và không biết tốt hay xấu.

Nên UI cần:

```text
Gini
0.204 ↓

Lower = more equal driver income
```

Hoặc:

```text
Fairness
Relatively balanced

Gini: 0.204
```

Không được chỉ show số.

Đây là một nguyên tắc product quan trọng:

> **Metric phải có meaning.**

---

# 10. Tôi rất muốn thấy phân phối thu nhập driver

Không chỉ Gini.

Một biểu đồ cực đơn giản:

```text
Driver income distribution
```

Hoặc histogram:

```text
Income
0–100      ██
100–200    █████
200–300    ███████████
300–400    ███████
400+       ██
```

Nếu đổi từ:

> No Forecast

sang:

> Full

tôi muốn nhìn thấy phân phối thay đổi.

Vì Gini là một số tổng hợp.

Distribution giúp người xem **thấy fairness bằng mắt**.

---

# 11. Một view rất hay nữa là “Driver Ranking”

Ví dụ:

| Driver | Trips | Income | Relative to Mean |
|---|---:|---:|---:|
| #18 | 42 | $392 | +18% |
| #71 | 39 | $366 | +10% |
| ... | ... | ... | ... |
| #24 | 21 | $183 | −45% |

Khi bật LAF:

> distribution co lại.

Khi No Fairness:

> top/bottom gap mở rộng.

Cực dễ hiểu với người không chuyên.

---

# 12. Timeline là feature rất phù hợp với chính nghiên cứu của bạn

Paper là:

> **long-term fairness**

nên sản phẩm không nên chỉ hiện trạng thái cuối.

Tôi muốn có timeline:

```text
Day 1 ─ Day 7 ─ Day 14 ─ Day 21 ─ Day 28 ─ Day 37
```

Có thể kéo slider.

Khi kéo:

> map + KPI + distribution thay đổi.

Đây sẽ là cách rất đẹp để demo result nổi bật nhất của bạn.

Ví dụ chọn Full và No Forecast.

Tại Day 7:

```text
Utility difference ≈ 0%
```

Day 21:

```text
+5.15%
```

Day 28:

```text
+11.65%
```

Day 37:

```text
+20.19%
```

Người không biết RL vẫn hiểu ngay:

> “À, hiệu quả chỉ xuất hiện sau thời gian dài.”

Đây là một productization cực kỳ phù hợp với research.

---

# 13. Tôi muốn một Scenario Builder rất nhỏ

Không cần hàng chục config.

Chỉ vài cái quan trọng:

```text
Scenario
────────────────────
Policy        MOMAQL ▼
Drivers       200
Lambda        0.5
Forecast      ON
Dataset       Validation
Seed          42
Horizon       37 days

[Run Simulation]
```

Đây là đủ.

Advanced setting có thể ẩn:

```text
Advanced ▸
```

Ở trong mới có:

- γ;
- α;
- ETA threshold;
- batch duration;
- deadhead cost.

Đừng bắt người dùng nhìn thấy tất cả parameter ngay.

---

# 14. Lambda slider sẽ là một demo rất đẹp

Bạn đã có λ sweep.

Hãy biến nó thành UI:

```text
Efficiency          Fairness
    ◀──────●──────────▶
          λ = 0.5
```

Khi user chọn:

```text
λ = 0
```

app hiện:

> Efficiency-oriented.

Khi:

```text
λ = 1
```

> Fairness-oriented.

Sau khi chạy:

> Utility/Gini result.

Đây là cách rất trực quan để explain multi-objective problem.

---

# 15. Nhưng đừng để slider làm người xem tưởng kết quả real-time

Nếu simulation mất thời gian, không cần giả live.

Người làm app sẽ đánh giá cao tính trung thực hơn animation fake.

Có thể làm:

```text
λ = 0.5
[Run Experiment]
```

Sau đó:

```text
Running...
Batch 432 / 3258
████████████████░░ 72%
```

Đây hoàn toàn ổn.

---

# 16. Tôi muốn thấy một Run ID

Điểm này rất “engineering” và sẽ làm sản phẩm của bạn khác dashboard sinh viên.

Mỗi experiment:

```text
Run ID
FD-20260821-00142

Policy     MOMAQL
Drivers    200
λ          0.5
Seed       42
Dataset    validation
```

Sau khi chạy:

> Save Result.

Lý do:

> một người làm app/data muốn biết kết quả này đến từ lần chạy nào.

Nó nối product với reproducibility.

---

# 17. Tôi muốn History

Ví dụ:

| Run | Policy | Drivers | λ | Utility | Gini |
|---|---|---:|---:|---:|---:|
| #142 | MOMAQL | 200 | 0.5 | 1.42M | 0.204 |
| #141 | No Forecast | 200 | — | 1.16M | 0.146 |
| #140 | LAF | 200 | — | 0.77M | 0.002 |

Click vào một run:

> mở lại toàn bộ scenario.

Đây là feature rất thực tế.

---

# 18. Nếu là app expert, tôi sẽ rất thích “Reproduce this run”

Một button:

> **Re-run**

hoặc:

> **Reproduce Run**

Nó sử dụng lại:

- dataset;
- seed;
- policy;
- configs.

Rất phù hợp với bản chất research của project.

---

# 19. Architecture phía sau tôi sẽ muốn hiểu

Tôi không cần bạn show microservices phức tạp.

Tôi muốn architecture đơn giản và có logic:

```text
                  ┌──────────────┐
                  │   Web App    │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Simulation   │
                  │ API / Server │
                  └──────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  Simulator         Policy Engine       Metrics
                        │
          ┌─────────────┼───────────────┐
          ▼             ▼               ▼
       Greedy          LAF            MOMAQL
```

Data:

```text
NYC TLC
   ↓
processed dataset
   ↓
simulation engine
```

Không cần Kubernetes.

Không cần Kafka.

Không cần microservice nếu project không cần.

Một app expert tốt sẽ thích:

> **simple architecture that matches the workload.**

---

# 20. API tôi sẽ muốn thấy

Không cần hàng chục endpoint.

Một MVP có thể chỉ cần:

```text
POST /simulations
GET  /simulations/{id}
GET  /simulations/{id}/metrics
GET  /simulations/{id}/timeline
GET  /simulations/{id}/assignments
```

Ví dụ request:

```json
{
  "policy": "momaql",
  "drivers": 200,
  "lambda": 0.5,
  "seed": 42,
  "horizon_days": 37
}
```

Response:

```json
{
  "run_id": "FD-142",
  "status": "running"
}
```

Sau đó UI polling hoặc stream progress.

Đây là đủ để chứng minh:

> algorithm đã được productized thành service.

---

# 21. Tôi sẽ hỏi “Có phải các chart đang hard-code không?”

Đây là câu cực kỳ dễ bị hỏi.

Nếu tôi là app engineer và thấy:

> 1.42M
> 0.204
> +22.4%

tôi sẽ hỏi:

> “Những số này lấy trực tiếp từ engine hay anh hard-code từ report vào frontend?”

Câu trả lời tốt nhất phải là:

> **“Frontend lấy kết quả từ simulation output/API. Không hard-code kết quả experiment.”**

Nếu product chỉ dùng static CSV cho demo thì cũng được, nhưng phải nói đúng:

> “Đây là replay mode từ artifact đã chạy trước.”

Đừng giả vờ real-time nếu không phải.

---

# 22. Tôi muốn sản phẩm có hai chế độ

Đây là cách tôi nghĩ hợp lý nhất.

### Simulation Mode

User tự chọn:

- policy;
- driver count;
- lambda;
- seed.

Rồi run.

### Research Replay Mode

App có các experiment đã verify sẵn:

```text
Main Comparison
Ablation
Long Horizon
Fleet Sensitivity
Lambda Sweep
```

Click:

> replay result.

Điều này cực kỳ phù hợp vì một số experiment 37 ngày có thể chạy lâu.

Bạn không cần bắt mentor đứng chờ.

---

# 23. Demo thực tế tôi muốn bạn trình bày chỉ khoảng 4–6 phút

Đừng demo 20 phút.

Tôi muốn xem đúng một câu chuyện end-to-end:

1. **Mở dashboard**, giới thiệu đây là simulation/decision-support tool.
2. Chọn scenario `200 drivers / MOMAQL / λ=0.5 / Forecast ON`.
3. Bấm **Step** vài batch để nhìn driver-request assignment trên map.
4. Click một assignment và show **Why this driver?**
5. Mở **Compare Full vs No Forecast**, cho thấy `+22.4% Utility` và `Gini 0.204 vs 0.146`.
6. Kéo **timeline Day 7 → Day 21 → Day 37** để cho thấy delayed Utility effect.
7. Kết bằng **Run History / reproducibility**.

Nếu bạn làm được flow này, tôi sẽ cảm thấy:

> “Research engine đã trở thành một sản phẩm có mục đích.”

---

# 24. Tôi không muốn bạn demo bằng cách click 20 menu

Một product demo tốt không phải chứng minh:

> app có nhiều feature.

Nó phải chứng minh:

> **user giải quyết được một vấn đề.**

Câu chuyện user của bạn là:

> “Tôi muốn biết policy nào nên dùng và trade-off Utility–Fairness của nó là gì.”

Mọi UI đều nên phục vụ câu hỏi đó.

---

# 25. Tôi sẽ đánh giá UX của bạn bằng một test rất đơn giản

Sau khoảng 30 giây nhìn màn hình, tôi phải trả lời được:

> Hệ thống đang chạy policy nào?

> Có bao nhiêu driver?

> Đang ở thời điểm nào?

> Policy vừa assign chuyến nào cho ai?

> Utility hiện tại là bao nhiêu?

> Fairness hiện tại tốt hay xấu?

Nếu tôi không trả lời được 6 câu đó:

> UI đang quá khó hiểu.

---

# 26. Một điều rất quan trọng: đừng gọi nó là “ứng dụng dispatch production”

Project hiện tại chưa có:

- GPS realtime;
- traffic realtime;
- customer app;
- driver app;
- payment;
- authentication;
- production dispatch latency;
- failover;
- regulatory logic;
- road routing đầy đủ.

Vì vậy cách định vị tốt nhất là:

> **FairDispatch — Ride-Hailing Dispatch Simulation & Decision-Support Prototype**

Không phải:

> “Hệ thống điều phối taxi hoàn chỉnh.”

Sự trung thực này giúp bạn trông chuyên nghiệp hơn.

---

# 27. Tôi cũng không cần Login/Register

Nếu Claude hay AI khác định làm:

```text
Login
Register
Forgot Password
Profile
Settings
```

hãy bỏ hết.

Không liên quan tới giá trị nghiên cứu.

Trong demo này:

> **màn hình đầu tiên nên là Control Room.**

---

# 28. Những feature tôi xem là Must-have và Bonus

| Thành phần | Mức độ |
|---|---|
| Scenario configuration | **Must-have** |
| Policy selection | **Must-have** |
| Driver/request map | **Must-have** |
| Run / Pause / Step | **Must-have** |
| Utility + Gini | **Must-have** |
| Full vs No-Forecast comparison | **Must-have** |
| Timeline / horizon | **Must-have** |
| Assignment details | **Must-have** |
| Run ID/config provenance | **Rất nên có** |
| Driver income distribution | **Rất nên có** |
| Lambda slider | **Rất nên có** |
| Run history | **Rất nên có** |
| Explain “why this driver” | **Điểm cộng rất lớn** |
| MLP/Q selector | Bonus |
| CSV export | Bonus |
| Full experiment builder | Bonus |
| Authentication | Không cần hiện tại |
| Fancy animation | Không cần |
| AI chatbot | Không cần |

---

# 29. Nếu chỉ có thời gian làm một MVP rất nhỏ

Tôi sẽ yêu cầu đúng **một màn hình**.

Bên trái:

```text
Policy
Drivers
λ
Forecast
Seed

RUN
STEP
RESET
```

Ở giữa:

> Map.

Bên phải:

```text
Utility
Gini
Requests Served
Average Income
```

Phía dưới:

```text
Timeline
+
Assignment Detail
```

Có thêm:

> `Compare Full vs No Forecast`

là đủ để demo cực tốt.

---

# 30. Nếu muốn “wow” tôi mà không cần UI đẹp

Hãy làm feature này:

> **Click Driver → show history**

Ví dụ:

```text
Driver #73

Current zone: 18
Income: $287
Trips: 31

Timeline
08:12  Zone 4  → Zone 12   +$13
08:31  Zone 12 → Zone 18   +$21
09:02  Zone 18 → Zone 31   +$17
...
```

Bên cạnh:

```text
Income vs fleet mean

Driver #73     $287
Fleet mean     $241

+19.1%
```

Ngay lập tức fairness trở thành một thứ cụ thể.

---

# 31. Một feature “wow” thứ hai: Fairness before/after

Ví dụ:

```text
Before assignment

Driver income
A  $180
B  $250
C  $110
D  $320

Gini 0.26
```

Policy chọn B hay C.

Sau assignment:

```text
After assignment

Gini 0.24
```

Hoặc:

```text
Immediate utility: +$18
Fairness impact: -0.02 Gini
```

Nếu làm được calculation thực sự từ engine thì cực kỳ hay.

Nhưng không invent nếu engine chưa hỗ trợ.

---

# 32. Điều tôi sẽ đánh giá về engineering

Khi demo xong, tôi rất có thể hỏi bạn:

> “Frontend nói chuyện với model thế nào?”

> “Simulation chạy đồng bộ hay background job?”

> “Một experiment 37 ngày mất bao lâu?”

> “Nếu user bấm Run hai lần thì sao?”

> “State được lưu ở đâu?”

> “Nếu simulation fail thì UI hiện gì?”

> “Có thể reproduce run không?”

> “Các result có lấy từ same engine với report không?”

Bạn không nhất thiết phải có production-grade answer cho tất cả.

Nhưng architecture phải có logic.

---

# 33. Error state cũng là thứ tôi nhìn

Ví dụ user chọn:

```text
Drivers = 0
```

Hoặc dataset thiếu.

App không nên crash.

Nó phải hiện:

> Driver count must be greater than 0.

Simulation fail:

```text
Run failed
Reason: dataset not found

[Retry]
```

Đây là điểm người làm app chú ý mà researcher thường bỏ qua.

---

# 34. Loading state rất quan trọng

Nếu run lâu:

Đừng để button đứng im.

Hiện:

```text
Simulation running

Day 17 / 37
Batch 14,203 / 31,050

████████████░░░ 46%
```

Và cho:

> Cancel.

Một app expert nhìn feature này sẽ biết bạn hiểu asynchronous workload.

---

# 35. Đừng cố làm real-time nếu chưa cần

Project hiện là simulator.

Vậy:

> **simulation/replay UX**

hoàn toàn hợp lý.

Không cần WebSocket, Kafka, live GPS chỉ để làm “xịn”.

Bạn có thể nói:

> “Nếu triển khai production, stream request có thể thay dataset replay; nhưng MVP hiện tại cố ý dùng deterministic replay để phục vụ evaluation và reproducibility.”

Đây là một câu rất mạnh.

---

# 36. Tôi sẽ muốn product giữ được “research provenance”

Ở góc màn hình:

```text
Experiment
Run FD-142

Dataset: NYC TLC 2013 Validation
Seed: 42
Policy: MOMAQL
λ: 0.5
γ: 0.9
Drivers: 200
```

Điều này rất hợp với bạn.

Một app bình thường có thể không cần.

Nhưng **research product** thì cực kỳ nên có.

---

# 37. Tôi còn muốn Export

Một nút:

> Export Run

Có thể tải:

```text
metrics.csv
assignments.csv
config.json
```

Hoặc:

> Download Report.

Đây là feature bonus nhưng rất hợp use case.

---

# 38. Màn hình compare tốt nhất nên có cả con số và câu nghĩa

Đừng chỉ:

```text
+22.4%
```

Nên:

```text
Full vs No Forecast

Utility
+22.4%
Full higher

Fairness
Gini 0.204 vs 0.146
No Forecast more equal
```

Sau đó:

> **Trade-off: higher efficiency, higher inequality.**

Ai không chuyên cũng hiểu.

---

# 39. Tôi muốn bạn đưa đúng research result vào product, không cố “làm Full thắng”

Đây là điểm quan trọng.

Product không nên có badge:

> 🟢 Recommended: Full

chỉ vì bạn nghiên cứu MOMAQL.

Nên ghi:

> Full: higher Utility.

> No Forecast: better Fairness.

Và cho người dùng tự chọn preference.

Nếu muốn recommendation:

```text
Objective
○ Maximize Utility
○ Balanced
○ Prioritize Fairness
```

Rồi recommendation theo objective.

Đó mới đúng multi-objective.

---

# 40. Product message cuối cùng nên rất rõ

Nếu tôi là app expert, sau demo tôi muốn nhớ đúng một câu:

> **FairDispatch lets an operator simulate and compare dispatch policies, see why assignments are made, and understand the long-term trade-off between system utility and driver fairness.**

Tiếng Việt:

> **FairDispatch cho phép người vận hành mô phỏng và so sánh các chiến lược điều phối, hiểu vì sao một tài xế được chọn, và quan sát trade-off dài hạn giữa hiệu quả hệ thống và công bằng thu nhập.**

Nếu app của bạn làm đúng câu này:

> sản phẩm đã có định vị rất tốt.

---

# Tôi sẽ chấm product demo của bạn như thế nào?

Nếu tôi là người làm app, rubric của tôi sẽ gần như:

| Tiêu chí | Tôi quan tâm |
|---|---:|
| User/problem rõ | 15% |
| End-to-end flow chạy được | **20%** |
| Algorithm thực sự nối với UI | **20%** |
| Map/dispatch visualization | 10% |
| Utility/Fairness dễ hiểu | 10% |
| Compare policies | 10% |
| Explainability | 5% |
| Reproducibility/run provenance | 5% |
| Error/loading UX | 3% |
| Visual beauty | **2%** |

Bạn thấy điểm thú vị không?

> **Tôi gần như không quan tâm app đẹp bao nhiêu.**

Tôi quan tâm:

> **Nó có thật không?**

> **Algorithm có chạy phía sau không?**

> **Người dùng hiểu được quyết định không?**

> **Research result có biến thành interaction được không?**

---

# Nếu là mentor app của bạn, tôi sẽ giao task sản phẩm như sau

> **Build a minimal FairDispatch decision-support application that allows an operator to configure a dispatch scenario, run or replay the simulator, visualize driver–request assignments, inspect why a driver was selected, compare Full MOMAQL against at least No-Forecast, and observe Utility/Fairness changes over time. Every displayed metric must originate from the actual simulation outputs rather than hard-coded presentation data. The product should prioritize traceability and clarity over visual polish.**

Và tôi sẽ coi **5 thứ này là deliverable trung tâm**:

1. **Map có driver + request + assignment thật.**
2. **Run / Pause / Step simulation.**
3. **Utility + Gini/Fairness cập nhật từ engine.**
4. **Compare Full vs No Forecast.**
5. **Click assignment → giải thích vì sao driver được chọn.**

Làm tốt 5 thứ này, tôi sẽ đánh giá sản phẩm **rất cao dù giao diện chỉ trắng, Arial và vài nút đơn giản**.

Điều tôi đặc biệt khuyên là đừng biến phần product thành một dự án frontend quá lớn. **Giá trị độc đáo của bạn nằm ở dispatch engine và research evidence**, nên app chỉ cần làm cho hai thứ đó **nhìn thấy được, tương tác được và giải thích được**.

---

# PHẦN B — PROMPT CHO CLAUDE CODE TRIỂN KHAI SẢN PHẨM

Hãy đọc **toàn bộ file Markdown này từ đầu đến cuối trước khi code**.

File này là **product requirement / mentor expectation chính thức** cho phần Product Demo của dự án FairDispatch.

Bạn phải hiểu kỹ:

- user của sản phẩm là ai;
- sản phẩm dùng để giải quyết vấn đề gì;
- research engine hiện có cung cấp những gì;
- sản phẩm KHÔNG phải app gọi xe production kiểu Grab;
- sản phẩm phải là một **Ride-Hailing Dispatch Simulation & Decision-Support Prototype**;
- mọi số liệu/metric phải có nguồn từ engine/output thật;
- không hard-code result chỉ để demo;
- không tự invent capability mà engine chưa hỗ trợ;
- clarity, traceability, explainability và reproducibility quan trọng hơn visual polish.

---

## THƯ MỤC TRIỂN KHAI

Triển khai toàn bộ sản phẩm vào:

```text
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Không làm thay đổi hoặc phá source research hiện tại nếu không thực sự cần thiết.

Nếu cần dùng source/engine hiện có từ repository cha, hãy:

- import/reuse hợp lý;
- hoặc tạo adapter/API layer;
- không copy logic thuật toán thành một bản thứ hai nếu có thể tái sử dụng trực tiếp.

---

# 1. TRƯỚC KHI CODE: AUDIT PROJECT

Không bắt đầu bằng frontend.

Trước tiên hãy đọc toàn bộ repository liên quan để xác định:

- source simulator;
- policy engine;
- MOMAQL implementation;
- Greedy;
- Nearest;
- LAF;
- REASSIGN;
- Full;
- No Forecast;
- No Fairness;
- data contracts;
- request schema;
- driver state;
- assignment output;
- metrics;
- Gini calculation;
- variance;
- utility;
- deadhead;
- timeline/checkpoint;
- experiment scripts;
- reports CSV/JSON;
- existing outputs;
- configs;
- CLI commands;
- tests.

Hãy xác minh exact source path/function/class trước khi kết nối vào product.

Không invent file/function/module.

---

# 2. XÁC ĐỊNH KHẢ NĂNG THẬT CỦA ENGINE

Trước khi triển khai UI, hãy tạo một file audit nội bộ, ví dụ:

```text
05_SanPham_Demo/PRODUCT_AUDIT.md
```

Trong đó ghi:

| Product requirement | Engine support | Source | Implementation plan |
|---|---|---|---|
| Run simulation | Yes/No | file/function | ... |
| Step batch | Yes/No | ... | ... |
| Pause | ... | ... | ... |
| Driver positions | ... | ... | ... |
| Request positions/zones | ... | ... | ... |
| Assignment explanation | ... | ... | ... |
| Utility | ... | ... | ... |
| Gini | ... | ... | ... |
| Timeline | ... | ... | ... |
| Full vs No Forecast | ... | ... | ... |
| History | ... | ... | ... |

Nếu một feature chưa được engine hỗ trợ:

- không fake;
- không hard-code như live feature;
- hoặc implement adapter/helper nếu có thể tính chính xác từ state thật;
- hoặc đánh dấu rõ `Replay only` / `Not available in live mode`.

---

# 3. PRODUCT POSITIONING

Tên/định vị nên rõ:

> **FairDispatch — Ride-Hailing Dispatch Simulation & Decision-Support Prototype**

User chính:

- Operation Manager;
- Dispatch Engineer;
- Data Scientist;
- Research Engineer.

Core job-to-be-done:

> Với cùng scenario, người vận hành có thể xem các policy điều phối khác nhau ra quyết định thế nào và trade-off Utility–Fairness thay đổi ra sao.

---

# 4. KHÔNG LÀM NHỮNG THỨ SAU

Không cần:

- Login;
- Register;
- Forgot Password;
- Profile;
- role management;
- payment;
- customer booking flow;
- driver mobile app;
- fake GPS realtime;
- Kafka;
- Kubernetes;
- microservice phức tạp;
- AI chatbot;
- fancy animation;
- glassmorphism;
- dark cyberpunk UI;
- stock image;
- decorative dashboard không liên quan.

Không biến project thành app Grab giả.

---

# 5. MÀN HÌNH CHÍNH: CONTROL ROOM

Ưu tiên một màn hình chính duy nhất.

Layout gợi ý:

```text
┌─────────────────────────────────────────────────────────────────┐
│ FairDispatch        Run ID / Scenario                STATUS     │
├───────────────┬────────────────────────────────┬────────────────┤
│               │                                │                │
│  CONTROLS     │            MAP                 │      KPI       │
│               │                                │                │
│ Policy        │ Drivers                        │ Utility        │
│ Drivers       │ Requests                       │ Gini           │
│ Lambda        │ Assignments                    │ Served trips   │
│ Forecast      │                                │ Avg income     │
│ Seed          │                                │ Deadhead       │
│ Horizon       │                                │                │
│               │                                │                │
│ Run / Step    │                                │                │
├───────────────┴────────────────────────────────┴────────────────┤
│ Timeline / Horizon                                              │
├─────────────────────────────────────────────────────────────────┤
│ Assignment / Driver / Request Detail                            │
└─────────────────────────────────────────────────────────────────┘
```

Không cần pixel-perfect theo sơ đồ.

Ưu tiên usability.

---

# 6. MAP / SPATIAL VIEW — MUST HAVE

Map/spatial view phải là trung tâm sản phẩm.

Phải cố gắng hiển thị dữ liệu thật:

- taxi zones hoặc spatial representation thật;
- driver current position/zone;
- request pickup;
- request dropoff;
- selected assignment;
- idle/busy state nếu engine cung cấp.

Nếu repository không có lat/lon cho mọi state nhưng có zone ID:

- dùng zone-level visualization;
- nếu có taxi-zone geometry thì load geometry thật;
- không invent coordinate giả mà không ghi rõ.

Khi chọn một assignment:

```text
Driver
→ Pickup
→ Destination
```

phải nhìn được ít nhất ở mức zone/spatial relationship.

---

# 7. SIMULATION CONTROLS — MUST HAVE

Cần có:

- Run;
- Pause nếu architecture cho phép;
- Step / Next Batch;
- Reset.

`Step` là feature ưu tiên rất cao.

Khi Step:

hiển thị tối thiểu:

```text
Current time
Requests arrived
Feasible drivers
Assignments
Declined/unmatched requests
```

Sau đó update:

- map;
- KPI;
- assignment detail;
- timeline state.

Nếu engine hiện tại không expose step API, hãy xem có thể wrap iterator/batch loop đúng cách không.

Không fake step bằng animation nếu state không thực sự thay đổi từ engine.

---

# 8. SCENARIO BUILDER — MUST HAVE

Chỉ hiển thị config quan trọng:

```text
Policy
Drivers
Lambda
Forecast
Dataset
Seed
Horizon
```

Policy nên support tối thiểu những gì source hiện có.

Advanced settings có thể collapse:

```text
Gamma
Alpha
ETA threshold
Batch duration
Deadhead cost
```

Chỉ expose parameter thật sự tồn tại.

---

# 9. KPI PANEL — MUST HAVE

Ưu tiên:

- Total Utility;
- Gini;
- Served Requests;
- Average Driver Income;
- Income dispersion / Std;
- Average Deadhead;
- Variance nếu thuận tiện.

Không cần quá 6–7 KPI.

Mỗi metric phải có meaning.

Ví dụ:

```text
Gini
0.204 ↓
Lower = more equal driver income
```

Không chỉ show `0.204`.

---

# 10. DRIVER INCOME DISTRIBUTION — RẤT NÊN CÓ

Hiển thị:

- histogram;
- hoặc simple distribution chart.

Mục tiêu:

> user nhìn thấy fairness bằng mắt, không chỉ qua Gini.

Phải lấy từ actual driver incomes/state.

---

# 11. DRIVER RANKING / DRIVER DETAIL — RẤT NÊN CÓ

Bảng:

```text
Driver
Trips
Income
Relative to fleet mean
Current zone
Status
```

Click driver:

show:

- history nếu trace tồn tại;
- income;
- trips;
- current state;
- relative to mean.

Nếu trace không tồn tại trong current engine run:

- không fake history;
- có thể enable record_trace đúng cách;
- hoặc ghi rõ history chỉ có khi trace mode bật.

---

# 12. ASSIGNMENT EXPLAINABILITY — ĐIỂM CỘNG RẤT LỚN

Click request/assignment và show:

```text
Request
Pickup
Destination
Fare
```

```text
Selected Driver
Current income
Pickup ETA
```

Với MOMAQL, nếu engine có thể expose score components, show:

```text
Immediate Utility
Future Zone Value
Fairness Adjustment
Final Score
```

Và nếu có thể:

```text
Alternative candidates
Driver X score
Driver Y score
Selected Driver score
```

Quan trọng:

- phải tính từ exact implementation thật;
- không recompute bằng formula khác;
- tốt nhất refactor score function để có optional explanation payload;
- không làm thay đổi actual decision behavior.

Nếu một baseline không có component tương tự, show explanation phù hợp với baseline đó.

Ví dụ Nearest:

> shortest pickup ETA.

---

# 13. COMPARE MODE — MUST HAVE

Ít nhất support:

```text
Full MOMAQL
vs
No Forecast
```

Cùng:

- dataset;
- drivers;
- seed;
- horizon.

Show:

| Metric | Full | No Forecast | Difference |
|---|---:|---:|---:|

Tối thiểu:

- Utility;
- Gini;
- Served requests nếu có;
- Average deadhead nếu có.

Interpretation phải đúng research evidence:

```text
Full:
Higher Utility

No Forecast:
Better Fairness
```

Không đánh badge Full là overall winner.

---

# 14. FULL VS NO FAIRNESS — RẤT NÊN CÓ

Show:

- Utility;
- Gini;
- variance nếu có.

Interpretation:

> Removing fairness increases income inequality in this implementation.

Đồng thời không nói Utility tăng nếu raw result hiện tại cho Utility giảm.

---

# 15. LONG-HORIZON TIMELINE — MUST HAVE

Timeline nên support các checkpoint thật:

```text
Day 1
2
3
4
5
6
7
14
21
28
37
```

Ưu tiên show Full vs No Forecast.

Có thể dùng Research Replay Mode từ raw result hiện có nếu live 37-day run quá lâu.

Khi chọn checkpoint:

- Utility;
- Gini;
- difference;
- chart;
- nếu có trace/state tương ứng thì map/distribution.

Không giả rằng map historical state tồn tại nếu artifact không lưu.

---

# 16. RESEARCH REPLAY MODE — MUST/VERY HIGH PRIORITY

Do long experiment có thể tốn thời gian, sản phẩm nên có hai mode.

## Simulation Mode

Chạy engine thật với user config.

## Research Replay Mode

Load artifact thật từ:

- reports/*.csv;
- reports/*.json;
- outputs thật.

Preset:

- Main Comparison;
- Ablation;
- Long Horizon;
- Fleet Sensitivity;
- Lambda Sweep;
- MLP vs Tabular nếu có.

UI phải ghi rõ:

> Replay from verified experiment artifacts.

Không giả là simulation đang live.

---

# 17. RUN ID / PROVENANCE — RẤT NÊN CÓ

Mỗi run nên có:

```text
Run ID
Dataset
Policy
Drivers
Lambda
Gamma
Alpha
Seed
Horizon
Timestamp
```

Nếu có Git commit:

show commit.

Nếu dataset checksum có:

show checksum hoặc link/detail.

Mục tiêu là traceability.

---

# 18. RUN HISTORY — RẤT NÊN CÓ

List run:

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

Click run:

- restore config;
- show result.

Có:

> Re-run / Reproduce Run

nếu có thể.

---

# 19. EXPORT — BONUS

Có thể export:

- metrics.csv;
- assignments.csv;
- config.json;
- driver metrics;
- report summary.

Chỉ export artifact thật.

---

# 20. LOADING / ASYNC UX

Nếu simulation không hoàn thành ngay:

show:

```text
Running
Current day/batch
Progress
Elapsed time
```

Có:

- Cancel nếu dễ implement an toàn;
- disable duplicate Run;
- không cho user spam run.

Nếu backend hiện tại chạy sync và việc background job quá phức tạp:

- implement đơn giản nhưng trung thực;
- ít nhất show loading state;
- không giả progress nếu không biết progress thật.

---

# 21. ERROR STATES

Phải xử lý:

- invalid driver count;
- missing dataset;
- invalid policy;
- missing Q-table/model;
- invalid lambda;
- simulation exception;
- empty result.

Không crash trắng màn hình.

Hiển thị error dễ hiểu và có Retry/Reset nếu phù hợp.

---

# 22. ARCHITECTURE

Ưu tiên kiến trúc đơn giản:

```text
Web App
   ↓
Simulation API / Application Layer
   ↓
Existing FairDispatch Simulator / Policy Engine
   ↓
Metrics / Results / Artifacts
```

Có thể dùng:

- Python backend nếu engine hiện là Python;
- FastAPI/Flask nếu phù hợp với repo;
- frontend HTML/CSS/JS hoặc React/Vite nếu repo đã phù hợp.

Không cần microservices.

Chọn stack dựa trên code hiện có và tốc độ tích hợp.

---

# 23. API TỐI THIỂU GỢI Ý

Nếu xây backend service, có thể dùng contract gần như:

```text
POST /simulations
GET  /simulations/{id}
GET  /simulations/{id}/metrics
GET  /simulations/{id}/timeline
GET  /simulations/{id}/assignments
GET  /simulations/{id}/drivers
```

Có thể thêm:

```text
POST /simulations/{id}/step
POST /simulations/{id}/pause
POST /simulations/{id}/resume
POST /simulations/{id}/cancel
```

nhưng chỉ nếu backend architecture thực sự support.

Không cần ép đúng endpoint này nếu có design đơn giản hơn.

---

# 24. DATA KHÔNG ĐƯỢC HARD-CODE

Đây là acceptance criterion rất quan trọng.

Không hard-code:

```text
1.42M
0.204
22.4%
```

trong app như result giả.

Có hai nguồn hợp lệ:

### Live simulation

Metric lấy từ engine.

### Replay

Metric load từ reports/artifact thật.

UI phải phân biệt hai mode.

---

# 25. PRODUCT DEMO FLOW PHẢI TỐI ƯU CHO 4–6 PHÚT

Chuẩn bị flow có thể demo:

1. Mở Control Room.
2. Giới thiệu user/problem.
3. Chọn `MOMAQL / 200 drivers / lambda=0.5 / Forecast ON`.
4. Step 1–3 batch.
5. Show map assignment.
6. Click assignment → Why this driver?
7. Compare Full vs No Forecast.
8. Show +Utility vs Gini trade-off.
9. Mở long-horizon replay:
   - Day 7;
   - Day 21;
   - Day 37.
10. Show Run History / provenance.
11. Kết luận sản phẩm.

Không demo quá nhiều menu.

---

# 26. UX ACCEPTANCE TEST

Trong 30 giây nhìn app, user phải trả lời được:

1. Policy nào đang chạy?
2. Bao nhiêu drivers?
3. Đang ở thời điểm/batch nào?
4. Assignment vừa xảy ra là gì?
5. Utility hiện tại bao nhiêu?
6. Fairness hiện tại tốt/xấu như thế nào?

Nếu không:

- simplify UI.

---

# 27. DESIGN

Không cần giao diện cầu kỳ.

Ưu tiên:

- white/light background;
- Arial/Inter/system font;
- dark readable text;
- một màu primary;
- semantic color có kiểm soát;
- map là trọng tâm;
- spacing rõ;
- KPI dễ nhìn;
- responsive cho màn hình laptop/projector.

Không dành thời gian quá nhiều cho visual polish.

---

# 28. PRODUCT MESSAGE

Product phải truyền tải được câu:

> **FairDispatch lets an operator simulate and compare dispatch policies, see why assignments are made, and understand the long-term trade-off between system utility and driver fairness.**

Tiếng Việt:

> **FairDispatch cho phép người vận hành mô phỏng và so sánh các chiến lược điều phối, hiểu vì sao một tài xế được chọn, và quan sát trade-off dài hạn giữa hiệu quả hệ thống và công bằng thu nhập.**

---

# 29. ACCEPTANCE CRITERIA TRUNG TÂM

Ưu tiên tuyệt đối 5 deliverable:

1. **Map có driver + request + assignment thật.**
2. **Run / Pause / Step simulation** (Pause nếu engine/architecture hỗ trợ; Step là quan trọng nhất).
3. **Utility + Gini/Fairness cập nhật từ engine/artifact thật.**
4. **Compare Full vs No Forecast.**
5. **Click assignment → giải thích vì sao driver được chọn.**

Sau đó:

- timeline;
- run provenance;
- income distribution;
- history;
- lambda slider;
- error/loading UX.

---

# 30. TESTING

Trước khi coi là hoàn thành:

- run backend tests;
- run frontend/build test nếu có;
- smoke test toàn flow;
- verify UI numbers với raw engine/report output;
- verify Full vs No Forecast;
- verify no hard-coded experiment metrics;
- test invalid input;
- test missing artifact;
- test Step;
- test Reset;
- test Compare;
- test replay;
- test assignment explainability.

Nếu có browser automation phù hợp thì dùng.

---

# 31. DOCUMENTATION

Tạo tối thiểu:

```text
05_SanPham_Demo/
├── README.md
├── PRODUCT_AUDIT.md
├── ...
```

README phải có:

- product purpose;
- architecture;
- setup;
- run command;
- demo flow;
- live vs replay distinction;
- supported policies;
- known limitations;
- source of metrics/results.

---

# 32. KHÔNG HỎI USER NHỮNG THỨ CÓ THỂ TỰ TÌM TRONG REPO

Chủ động audit và triển khai.

Chỉ hỏi nếu có một quyết định thực sự không thể resolve từ:

- code;
- data;
- configs;
- results;
- documentation.

---

# 33. KHI HOÀN THÀNH

Trả summary:

```text
Implemented:
- ...

Live simulation features:
- ...

Replay features:
- ...

Explainability:
- ...

Data sources:
- ...

Commands:
- ...

Known limitations:
- ...

Files:
D:\ProjectVSF\FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\05_SanPham_Demo
```

Không chỉ trả “Done”.

---

# FINAL OBJECTIVE

Sản phẩm cuối không cần giống Grab.

Nó phải khiến một người làm app/product engineering có thể nhìn và nói:

> “Research engine này đã được productize thành một decision-support prototype có user rõ, flow rõ, algorithm thật nối với UI, metric có provenance, và người dùng nhìn thấy được trade-off Utility–Fairness.”

Ưu tiên:

> **algorithm thật + interaction thật + explanation thật + reproducibility**

hơn:

> **giao diện đẹp.**
