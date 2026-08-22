# FairDispatch v3 — Mentor Presentation Playbook
## Cách thuyết trình một replication study để được đánh giá cao

**Dự án:** FairDispatch v3 — MOMAQL Fairness-Aware Ride-Hailing Dispatch  
**Paper đối chiếu:** Kang et al. (2024), *Long-term Fairness in Ride-Hailing Platform*, ECML PKDD 2024, arXiv:2407.17839  
**Loại công việc:** Qualitative / trend replication, không phải exact numerical reproduction  
**Mục đích tài liệu này:** Đóng vai mentor đã giao bài, chỉ ra mentor muốn nghe gì, muốn thấy bằng chứng gì, cách kể câu chuyện nghiên cứu, cấu trúc slide, thiết kế slide, cách nói, các điểm dễ bị hỏi và các câu trả lời nên chuẩn bị.

---

# 0. Tôi đã audit những gì?

Tôi không chỉ đọc README. Tôi đã đối chiếu hai ZIP theo các lớp sau:

- source code của simulator và policies;
- toàn bộ script chạy thí nghiệm;
- các script huấn luyện Q-table và MLP;
- toàn bộ CSV/JSON trong `reports/`;
- Research Report DOCX;
- Technical Documentation DOCX;
- hai bản LaTeX/PDF tiếng Việt và tiếng Anh;
- toàn bộ figure đang dùng trong report;
- mentor requirements / mentor guidance `.md`;
- repository state và Git metadata;
- dataset checksum manifest;
- cấu trúc gói nộp cho mentor.

Hai ZIP có quan hệ như sau:

- `fairdispatch_v3_clean.zip` là repository đầy đủ hơn, có `.git`, source, reports, docs và ba file parquet.
- `FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication.zip` là submission bundle được đóng gói lại theo:
  - Technical Documentation;
  - Research Report;
  - source + results;
  - paper EN/VI;
  - thư mục slide đang để trống.
- 64 file source/result trùng giữa submission bundle và repository đầy đủ có SHA-256 giống nhau trong lần kiểm tra này.

Ba parquet rất lớn không được giải mã row-by-row trong môi trường audit này vì không có parquet engine, nhưng:
- file thực sự tồn tại;
- kích thước file được kiểm tra;
- SHA-256 thực tế khớp chính xác `reports/dataset_checksums.json`;
- contract và row count được đối chiếu từ code, report và techdoc.

Checksum đã xác minh:

| Artifact | SHA-256 |
|---|---|
| `train.parquet` | `d763f86b93a57baee996929719435a401caf52ae1daffbb6f20d533022c9706d` |
| `val.parquet` | `075e2a1b65c4b45abde92257e661edbcbdc25b3289818ae244d8f0526922a966` |
| `test.parquet` | `96e7133fec5f55a8260b5e2fc26327405c51e67529e2a96662a003cd6c66bc72` |
| `momaql_q_table_trained.json` | `9af13c33219f989e23a8ee9eca9e0cda3262996e34849bcc6dfab0cab5d64bdb` |

Hai ZIP tại thời điểm audit:

| ZIP | SHA-256 |
|---|---|
| report/submission bundle | `246d08e2daf9b8ed5431835c0ac55090eb4154abc1f7d473c69f2a0941bd73a2` |
| full repository ZIP | `fd7a94fa5722971e8a0482403560c3d9bca78dfae776956c1c3423c04430c67b` |

---

# 1. Kết luận mentor trước khi nói về slide

Nếu tôi là mentor đã giao bài này, tôi **không quan tâm trước tiên rằng slide đẹp hay code nhiều**.

Tôi sẽ đánh giá bạn qua một câu hỏi:

> **Em có hiểu chính xác paper tuyên bố điều gì, có xây một replication hợp lý, có tạo bằng chứng thực nghiệm đủ đáng tin, và có trung thực khi kết quả của em không đi cùng hướng paper hay không?**

Đây là một **research replication defense**, không phải demo sản phẩm.

Vì vậy, cách gây ấn tượng tốt nhất không phải:

> “Model của em tốt hơn baseline.”

mà là:

> “Em xác định 6 claims của paper, xây từng experiment để kiểm tra từng claim, công bố rõ các deviation, và kết luận claim nào reproduced, claim nào chỉ partial, claim nào không reproduced.”

Nếu bạn làm được điều này, mentor sẽ thấy bạn có tư duy nghiên cứu.

---

# 2. Điều mentor thực sự muốn nghe

Một mentor nghiên cứu sẽ muốn nghe 8 lớp thông tin, theo đúng thứ tự logic.

## 2.1. Paper đang giải bài toán gì?

Bạn cần nói được bằng ngôn ngữ của mình, không đọc abstract.

Bài toán không đơn thuần là “chia chuyến công bằng”.

Nó là:

> Trong ride-hailing, nếu chỉ tối đa hóa hiệu quả hiện tại thì một số tài xế có thể liên tục nhận được các chuyến tốt hơn, làm chênh lệch accumulated utility tăng theo thời gian. Paper đặt bài toán multi-objective: vừa giữ utility tổng cao, vừa kiểm soát bất công bằng giữa tài xế trên horizon dài.

Điểm “long-term” là cốt lõi.

Bạn phải nói rõ:

- fairness được quan sát trên **accumulated utility**, không phải chỉ một trip;
- quyết định tốt ở thời điểm hiện tại chưa chắc tốt cho toàn horizon;
- future demand / look-ahead được đưa vào để tránh quyết định myopic.

Nếu mentor hỏi:

> “Tại sao cần prediction?”

Không nên trả lời:

> “Vì prediction giúp model biết tương lai.”

Nên trả lời:

> “Vì giá trị của một assignment không chỉ nằm ở fare hiện tại. Destination của chuyến hiện tại đặt driver vào một state không gian–thời gian mới. Nếu state đó có giá trị tương lai cao, chấp nhận chuyến đó có thể tạo lợi ích tích lũy ở các batch sau. Prediction/look-ahead làm thay đổi opportunity cost của assignment hiện tại.”

---

## 2.2. Chính xác bạn replicate cái gì?

Bạn phải nói rất sớm:

> **Đây là trend replication, không phải exact reproduction.**

Rồi nói tại sao:

- paper không công bố đủ MLP hyperparameters;
- không rõ driver count;
- spatial clustering không đủ chi tiết;
- exploration/Q-learning details không đầy đủ;
- một số baseline detail không đủ;
- project dùng NYC TLC 2013 thay vì slice 2016 của paper;
- project dùng objective/scalarisation đã sửa;
- canonical implementation dùng tabular `Q(zone, hour)` look-ahead, không phải MLP của paper.

Câu nên dùng:

> “Em không tuyên bố tái lập con số của paper. Em kiểm tra xem dưới một interpretation minh bạch và reproducible của các thành phần bị under-specified, các quan hệ định tính mà paper báo cáo có xuất hiện lại hay không.”

Đây là một câu rất mạnh trong defense.

---

## 2.3. Bạn đã thay đổi gì so với paper?

Mentor sẽ muốn một bảng **Paper vs Ours**.

Đây là slide bắt buộc.

Ít nhất phải có:

| Component | Paper | FairDispatch v3 | Cách gọi |
|---|---|---|---|
| Dataset year | NYC Taxi 2016 | NYC TLC 2013 | Deviation |
| Spatial representation | merged graph nodes, không đủ chi tiết | 67 TLC taxi zones | Approximation |
| Driver count | không rõ | 200 | Assumption |
| Forecast | 3-layer MLP demand predictor | canonical: tabular Q(zone,hour); MLP có benchmark riêng | Modified |
| RL state/look-ahead | theo paper | zone/hour value approximation | Modified |
| Scalarisation | utility + variance fairness, có λ/ω | score riêng dùng efficiency/look-ahead + relative income gap | Modified |
| Matching | assignment formulation | joint Hungarian M-to-N + decline dummy | Comparable mechanism |
| Evaluation | paper setting | 5 seeds main experiments, validation 195,508 trips | Reproducible protocol |

Điều quan trọng:

> Đừng giấu deviation ở slide cuối.

Đưa chúng lên **trước khi show result**.

Nếu mentor tự tìm ra sau thì cảm giác sẽ là bạn đang né.

Nếu bạn tự nói trước thì nó trở thành điểm cộng về research maturity.

---

# 3. Mentor muốn bạn chứng minh hệ thống có đáng tin trước khi tin result

Một mentor tốt sẽ nghĩ:

> “Nếu simulator sai thì tất cả đồ thị sau đó vô nghĩa.”

Bạn cần chứng minh tối thiểu:

- Driver có `location`, `available_at`, `total_income`.
- Request được xử lý theo thời gian.
- Driver chỉ feasible nếu đang free và pickup ETA <= 600 giây.
- Deadhead được tính bằng haversine + giả định 12 mph.
- Driver được commit trip thì:
  - income cập nhật;
  - vị trí chuyển đến dropoff;
  - `available_at` tăng theo pickup ETA + trip duration.
- Tất cả policies dùng cùng một joint matching framework:
  - Hungarian algorithm;
  - dummy rows/columns;
  - có lựa chọn decline/stay idle;
  - policies khác nhau chủ yếu ở scoring function.

Đây là điểm rất tốt trong project.

Trong `src/policies.py`, tất cả 5 policy đã được đưa về cùng một reference frame bằng Hungarian joint assignment. Đây là thứ nên nói vì nó giúp baseline comparison công bằng hơn.

Không cần show source code 200 dòng.

Chỉ cần diagram:

```text
Requests trong 60s batch
        +
Feasible drivers
        ↓
Driver × Request score matrix
        ↓
Hungarian joint assignment
        ↓
Commit feasible positive-value pairs
        ↓
Update driver state + income
```

Và nói:

> “Em cố định assignment solver cho mọi policy; yếu tố thay đổi chủ yếu là score function, để tránh confound do một policy chạy sequential còn policy khác chạy joint assignment.”

Đây là một câu rất research-oriented.

---

# 4. Công thức implementation bạn phải hiểu để trả lời miệng

## 4.1. Utility thực tế của project

Project dùng gần dạng:

```text
net = fare_amount - deadhead_eta_seconds × 0.0025
```

Đây là accumulated income/utility theo driver.

Bạn phải thừa nhận:

> Nó là operational proxy trong simulator, không được tuyên bố tương đương tuyệt đối với geographic benefit/cost function của paper.

---

## 4.2. Fairness

Project báo:

- Gini;
- variance;
- std;
- coefficient of variation ở một số experiment.

Paper dùng variance accumulated utility làm primary fairness quantity.

Trong slide:

- dùng **Gini là metric trực quan chính** nếu bạn muốn;
- nhưng phải nhắc paper dùng variance;
- nên có appendix chứa variance/CV để mentor biết bạn không đổi metric rồi quên paper.

Câu nên nói:

> “Gini được dùng để dễ đọc và ít nhạy với scale hơn trong các comparison chính, nhưng em vẫn báo variance song song vì đó là metric gần với paper hơn.”

---

## 4.3. MOMAQL score trong project

Canonical project score:

```text
score =
(1 - λ) × [fare - deadhead_cost + γ × Q(destination_zone, destination_hour)]
+
λ × [relative income gap] × fare
```

với:

- default `λ = 0.5`;
- `γ = 0.9`;
- `α = 0.1`;
- no-forecast => Q future = 0;
- no-fairness => λ = 0.

Điểm rất quan trọng:

> **λ của project không tương đương toán học với λ của paper.**

Không được nói:

> “Paper λ=1 nên em sweep λ=1 để reproduce.”

Vì scalarisation khác.

---

## 4.4. Q-table là gì?

Project canonical không dùng Q-table như một demand count predictor.

Nó học:

> giá trị tương lai chiết khấu của việc kết thúc ở một `(zone, hour)`.

TD(0):

```text
Q(P,h) ← Q(P,h) + α × [reward + γQ(D,h') - Q(P,h)]
```

Bạn nên gọi nó:

> **look-ahead value estimator / state-value proxy**

thay vì:

> “forecast MLP của paper”.

Project có thêm một MLP thật để benchmark, nhưng đó là experiment bổ sung.

---

# 5. Các kết quả mạnh nhất hiện có

## 5.1. R1 — Main baseline comparison

Trung bình 5 seed:

| Policy | Utility | Gini ↓ |
|---|---:|---:|
| MOMAQL | **1,422,441** | **0.204** |
| Greedy | 1,001,551 | 0.531 |
| Nearest | 789,444 | 0.430 |
| LAF | 766,265 | **0.002** |
| Exact REASSIGN | 648,160 | 0.417 |

Điểm nói đúng:

> “MOMAQL tạo operating point cân bằng mạnh: utility cao nhất, đồng thời fairness tốt hơn rõ rệt Greedy, Nearest và Exact REASSIGN.”

Điểm **không được nói**:

> “MOMAQL tốt hơn tất cả baseline cả utility lẫn fairness.”

Vì LAF có:

- Gini ≈ 0.002;
- tốt hơn rất nhiều MOMAQL về fairness;
- nhưng utility thấp hơn đáng kể.

Cách nói tốt nhất:

> “MOMAQL không phải policy công bằng nhất. LAF là fairness extreme. Điểm mạnh của MOMAQL là trade-off: giữ utility cao nhất trong khi giảm inequality mạnh so với các efficiency-oriented baselines.”

Đây là khác biệt giữa **Pareto/balanced superiority** và **dominate tất cả metrics**.

---

# 6. ĐIỂM RỦI RO LỚN NHẤT TRONG BÁO CÁO HIỆN TẠI

Phần này rất quan trọng.

Nếu mentor kiểm tra CSV và đọc report kỹ, có ba chỗ bạn có thể bị hỏi ngay.

---

## 6.1. Rủi ro số 1 — Claim C5 hiện đang bị diễn giải quá mạnh

`reports/r2_ablation_results.csv`:

| Variant | Utility | Gini ↓ | Variance ↓ |
|---|---:|---:|---:|
| Full | 1,422,441 | 0.2037 | 8.346M |
| No Forecast | 1,162,077 | **0.1458** | **2.473M** |
| No Fairness | 898,025 | 0.4504 | 14.235M |

Full so với No Forecast:

- Utility: **+22.4%** cho Full.
- Nhưng Gini: `0.2037 > 0.1458` => Full **kém công bằng hơn** theo Gini.
- Variance: `8.346M > 2.473M` => Full **kém công bằng hơn** theo variance.

Vì vậy câu:

> “Prediction helps utility + fairness: Reproduced”

không được raw evidence hỗ trợ nếu fairness được hiểu bằng Gini/variance đang báo.

Cách nói nên sửa:

> “Forecast/look-ahead contribution to utility is strongly reproduced: Full gains +22.4% utility. However, the fairness direction is not reproduced in this implementation: No-Forecast has lower Gini and variance. Therefore the original joint utility+fairness ablation claim is only partially reproduced.”

Nếu mentor bắt lỗi này và bạn chủ động nói trước, đó là điểm cộng lớn.

---

## 6.2. Rủi ro số 2 — Long-horizon benefit xuất hiện ở utility, không phải fairness

Mean Full vs No Forecast:

| Day | Utility advantage Full | Full Gini | No-Forecast Gini |
|---:|---:|---:|---:|
| 1 | ~0.00% | 0.0441 | 0.0441 |
| 2 | ~0.00% | 0.0577 | 0.0580 |
| 3 | ~0.00% | 0.0738 | **0.0730** |
| 4 | -0.01% | **0.0600** | 0.0623 |
| 5 | -0.01% | **0.0863** | 0.0890 |
| 6 | -0.03% | **0.0997** | 0.1011 |
| 7 | -0.02% | **0.1072** | 0.1092 |
| 14 | +0.04% | **0.1745** | 0.1753 |
| 21 | **+5.15%** | 0.2154 | **0.1993** |
| 28 | **+11.65%** | 0.2260 | **0.1835** |
| 37 | **+20.19%** | 0.2168 | **0.1513** |

Như vậy:

- day 1–14: utility gần như tied;
- day 21–37: Full có utility advantage lớn dần;
- nhưng từ day 21 trở đi, **No-Forecast lại có Gini thấp hơn**.

Do đó:

> Đừng đặt tên câu chuyện “Prediction improves long-term fairness”.

Evidence mạnh hiện có là:

> **“Look-ahead produces a delayed long-horizon utility advantage.”**

Còn paper’s long-term fairness claim:

> **không được reproduce theo Gini trong project hiện tại.**

Đây là negative result quan trọng, không phải thứ cần giấu.

Research presentation tốt sẽ có một slide riêng:

> **“The paper’s long-term fairness advantage is not reproduced by our Gini trajectory.”**

Mentor thường đánh giá cao hơn việc bạn nói rõ negative result và phân tích nó, thay vì cố ép hình.

---

## 6.3. Rủi ro số 3 — C2 không phải “MOMAQL thắng mọi baseline cả hai metric”

LAF:

- utility ~766k;
- Gini ~0.002.

Nó cực kỳ fair nhưng utility thấp.

Vì vậy không được dùng từ:

> “dominates all baselines”

theo nghĩa Pareto.

Nên nói:

> “MOMAQL provides the strongest balanced operating point among the adapted baselines.”

Hoặc:

> “MOMAQL has the highest utility and substantially lower inequality than Greedy/Nearest/REASSIGN, while LAF remains the fairness extreme at a large utility cost.”

---

# 7. Claim matrix tôi khuyên dùng khi thuyết trình

Nếu tôi là mentor, tôi muốn một bảng **khắt khe hơn** report hiện tại.

| Claim | Evidence của project | Verdict nên nói |
|---|---|---|
| C1 — Utility/fairness trade-off tồn tại | λ sweep có extreme λ=1 cực fair nhưng utility collapse; interior non-monotonic | **Reproduced, with non-monotonicity** |
| C2 — Proposed có balanced trade-off tốt hơn baselines | Highest utility; fairer Greedy/Nearest/REASSIGN; LAF fairer nhưng utility thấp | **Reproduced within adapted-baseline scope** |
| C3 — RL behavior ổn định khi horizon dài | Full Gini tăng rồi gần plateau; Q change giảm dần; không phải replication sạch của paper | **Partially Reproduced** |
| C4 — Prediction cải thiện long-term fairness | Full Gini kém No-Forecast từ day 21 trở đi | **Not Reproduced for fairness** |
| C5 — Prediction giúp cả utility + fairness | +22.4% utility, nhưng fairness metric xấu hơn | **Partially Reproduced: utility yes, fairness no** |
| C6 — Bỏ fairness => utility tăng + inequality bùng nổ | inequality bùng nổ; utility lại giảm ~36.9% | **Partially Reproduced: fairness direction yes, utility direction no** |

Đây là bảng tôi khuyên dùng cho oral defense.

Nó trung thực hơn và khớp raw results.

---

# 8. Pareto experiment nên kể thế nào?

Pareto summary:

| λ | Utility | Gini ↓ |
|---:|---:|---:|
| 0.0 | 898,025 | 0.4504 |
| 0.2 | 1,273,490 | 0.2479 |
| 0.4 | 1,382,972 | 0.2195 |
| 0.5 | 1,422,441 | 0.2037 |
| 0.6 | 1,432,217 | **0.1993** |
| 0.8 | **1,555,401** | 0.2282 |
| 1.0 | 766,265 | **0.0019** |

Đây không phải một đường trade-off monotonic đơn giản.

Từ λ=0 → 0.6:

- utility tăng;
- fairness cũng tốt lên.

λ=0.8:

- utility cao nhất;
- fairness xấu đi một chút.

λ=1:

- fairness gần hoàn hảo;
- utility collapse.

Điều này rất đáng nói.

Không nên vẽ câu chuyện:

> “λ càng tăng thì utility giảm, fairness tăng.”

Raw result không nói vậy.

Cách nói:

> “Scalarisation tạo nhiều operating regime. Vì matching có decline option và fairness score cũng thay đổi candidate ordering, λ không chỉ chuyển trọng số giữa hai mục tiêu theo một đường tuyến tính; nó còn thay đổi throughput và assignment feasibility. Vì vậy empirical frontier của implementation này là non-monotonic.”

Đây là một câu trả lời sâu.

Mentor có thể hỏi:

> “Vì sao λ=0.8 còn utility cao hơn λ=0?”

Bạn trả lời:

> “Vì objective không chỉ reweight một reward cố định. Fairness term thay đổi assignment ordering và việc một pair có score dương hay âm dưới decline=0; điều đó có thể giữ driver ở trạng thái thuận lợi hơn và tăng số assignment có giá trị trong tương lai. Vì thế λ tác động cả distribution lẫn throughput.”

---

# 9. No-Fairness ablation: negative result rất đáng giá

No-Fairness:

- Utility = 898,025;
- Gini = 0.4504.

Full:

- Utility = 1,422,441;
- Gini = 0.2037.

Paper kỳ vọng:

- bỏ fairness -> utility tăng;
- inequality tăng mạnh.

Project thấy:

- inequality tăng mạnh: **đúng hướng**;
- utility giảm ~36.9%: **ngược hướng paper**.

Không nên xem đây là “project thất bại”.

Nó là discrepancy cần giải thích.

Giả thuyết hợp lý:

- fairness term không chỉ đóng vai trò penalty;
- trong simulator có decline option;
- income balancing có thể vô tình giữ fleet distribution tốt hơn;
- λ thay đổi matching decisions và throughput;
- objective implementation khác paper;
- forecast proxy khác paper;
- simplified mobility/ETA làm dynamics khác.

Nhưng phải phân biệt:

> **Plausible explanation** ≠ **confirmed cause**.

Nên nói:

> “Em có các mechanism hypotheses, nhưng chưa có controlled ablation đủ để gọi chúng là causal proof.”

---

# 10. Long-horizon experiment: đây là một phần rất đáng show

Điểm mạnh:

- không chỉ chạy day 1,2,... như các run độc lập;
- project có `run_simulation_with_horizon`;
- checkpoint trên **một trajectory**;
- day 1 → 37;
- cho thấy delayed divergence.

Utility Full vs No-Forecast:

- gần như tied đến day 14;
- day 21: +5.15%;
- day 28: +11.65%;
- day 37: +20.19%.

Đây là evidence rất đẹp cho:

> **look-ahead value only becomes decision-relevant after sufficient state visitation / cumulative dynamics.**

Nhưng nhớ:

> Đây là evidence về utility advantage, không được tự chuyển thành fairness advantage.

---

# 11. Mechanism experiments: nên dùng để giải thích, không dùng để “chứng minh nhân quả”

Project có nhiều experiment vượt mức tối thiểu. Đây là điểm mạnh.

## 11.1. Policy disagreement

5 seed full validation:

- khoảng 11.6% → 14.3%;
- mean xấp xỉ 13%.

Spatial/temporal split:

- day 1–7: disagreement tổng chỉ khoảng **0.08%**;
- day 8–37: khoảng **15%+**;
- core zones cao hơn periphery.

Cách kể:

> “Early in the trajectory, forecast and no-forecast policies almost always choose the same assignments. Later, as Q differences accumulate, their decisions diverge materially.”

Đây là một bridge rất tốt với delayed utility divergence.

---

## 11.2. Q-table convergence

- state visited day 1: ~1086;
- day 7: ~1381;
- day 14: ~1418;
- day 21: ~1427;
- day 37: ~1441.

Mean absolute ΔQ vs previous day:

- day 7 ~1.88;
- day 14 ~1.37;
- day 21 ~0.91;
- day 37 ~0.82.

Cách nói:

> “Q-table coverage saturates and update magnitude decreases around the same period in which Full and No-Forecast utility begin to separate.”

Nhưng ngay sau đó phải thêm:

> “This is correlational evidence; em chưa có intervention cố định Q-convergence để chứng minh causality.”

---

## 11.3. Fairness/look-ahead score balance

Fairness share trong absolute score:

- day 1: ~1.2%;
- day 14: ~3.5%;
- day 21: ~4.3%;
- day 37: ~4.5%.

Efficiency/look-ahead vẫn >95%.

Ý nghĩa:

> fairness term tăng dần về relative influence, nhưng không hề trở thành dominant term.

Đừng nói:

> “Sau day 21 fairness chi phối.”

Raw result không cho phép.

---

## 11.4. Weekly-cycle hypothesis

Experiment không thấy một chu kỳ 7 ngày rõ ràng lặp lại.

Có weekday/weekend difference khoảng mức 12% theo report, nhưng không có recurring 7-day mechanism mạnh.

Đây là ví dụ tốt để nói:

> “Em đặt hypothesis rồi bác bỏ nó bằng experiment.”

Mentor nghiên cứu thường thích điều này.

---

## 11.5. Spatial candidate-pool

Core có candidate depth lớn hơn periphery đáng kể.

Nhưng script này dùng static/read-only geometry, không commit driver movement.

Do đó:

> chỉ dùng như diagnostic về local candidate density, không gọi nó là dynamic causal explanation cho long-horizon transition.

---

## 11.6. Fleet-scale sensitivity

3 seeds:

- N=100: Full utility advantage rất lớn (~42%);
- N=200: ~23%;
- N=400: gần 0%.

Ý nghĩa rất hay:

> look-ahead value mạnh nhất khi hệ thống bị supply scarcity; khi fleet gần saturation, gần như request nào cũng được phục vụ nên forecast advantage biến mất.

Đây là một kết quả rất đáng show.

Nó giúp câu chuyện có chiều sâu:

> “Forecast is not universally useful; its value depends on operational regime.”

---

# 12. MLP benchmark: nên show thế nào?

Project có một MLP thật:

- zone embeddings: 16;
- input:
  - pickup zone embedding;
  - destination zone embedding;
  - 24-dim hour one-hot;
- layers:
  - input → 64;
  - ReLU;
  - 64 → 32;
  - ReLU;
  - 32 → 1;
- target: `log1p(count)` của OD pair + hour;
- Adam;
- lr = 0.005;
- 30 epochs;
- batch = 2048.

Sau đó predicted OD demand được:

- sum qua destinations để thành zone-hour outbound demand;
- min-max rescale sang range của tabular Q;
- đưa vào cùng score formula.

Kết quả:

| Forecast representation | Utility | Gini |
|---|---:|---:|
| Tabular Q | **1,422,441** | **0.204** |
| MLP Demand Forecast | 1,392,473 | 0.226 |
| No Forecast | 1,162,077 | **0.146** |

Cách kể:

> “Em bổ sung MLP để kiểm tra sensitivity với forecast representation. MLP thật tạo utility gain rõ so với no-forecast, nhưng canonical tabular Q vẫn tốt hơn MLP trong simulator này. Điều này cho thấy kết quả phụ thuộc representation và cách forecast được tích hợp.”

Không được nói:

> “Em đã reproduce exact 3-layer MLP của paper.”

Vì:

- architecture cụ thể do project tự chọn;
- aggregation/rescaling là custom;
- paper under-specified.

---

# 13. Một điểm reproducibility mentor có thể hỏi

Current Git HEAD trong full ZIP:

```text
3174cefd4b98fc06172cbda8586f76da78d3ad9e
```

Nhưng:

- working tree trong ZIP đang có nhiều modified files so với HEAD;
- `reports/dataset_checksums.json` còn ghi commit:
  `cefcd7465f2469a8d8c16e053966011085c50a2b`.

Điều này nghĩa là:

> commit hash hiện được ghi ở report không hoàn toàn đủ để xác định **working-tree snapshot** đang được nộp.

Trước presentation/final submission, tôi khuyên:

1. commit toàn bộ snapshot thật sự dùng để nộp;
2. regenerate:
   - checksum manifest;
   - figures;
   - Research Report;
   - TechDoc;
3. để mọi tài liệu cùng chỉ một commit;
4. chạy `git status --short` và bảo đảm sạch;
5. lưu command log của run cuối.

Nếu mentor hỏi reproducibility mà bạn nói:

> “Em có commit hash.”

Nhưng họ clone commit đó rồi result files khác, sẽ mất điểm.

Tốt nhất phải có:

> **clean commit + dataset SHA-256 + config/seeds + generated outputs.**

---

# 14. 20/20 tests: nói thế nào cho đúng?

Report/TechDoc ghi 20 tests pass.

Đây là điểm tốt.

Nhưng TechDoc cũng tự disclosure:

- `test_no_double_booking_within_window`;
- `test_time_monotonicity`;

đang chạy với `record_trace=False`, nên assertions dựa trên trace có thể iterate empty trace.

Do đó đừng nói:

> “20/20 tests chứng minh simulator hoàn toàn đúng.”

Nói:

> “20 invariant tests là sanity layer. Tuy nhiên em đã xác định hai trace-based tests có coverage yếu do default `record_trace=False`; vì vậy test suite không được xem là formal proof of simulator correctness.”

Nếu bạn tự nói được điều này, mentor sẽ thấy bạn hiểu test quality chứ không chỉ đếm test.

---

# 15. Mentor sẽ muốn phần trình bày chính đi theo câu chuyện nào?

Tôi khuyên theo narrative:

```text
Research question
      ↓
What the paper claims
      ↓
What I can/cannot replicate
      ↓
How I built a controlled simulator
      ↓
Main baseline evidence
      ↓
Ablation
      ↓
Long-horizon behavior
      ↓
Negative result on fairness
      ↓
Mechanism probes
      ↓
Sensitivity / robustness
      ↓
Claim-by-claim verdict
      ↓
Limitations + next experiment
```

Không nên đi theo:

```text
Folder structure
→ code file 1
→ code file 2
→ class 1
→ class 2
→ screenshot
→ result
```

Cách thứ hai là software demo, không phải research defense.

---

# 16. Slide nghiên cứu nên đơn giản hay phức tạp?

## Câu trả lời ngắn

> **Visually simple, scientifically dense.**

Tức là:

- slide nhìn rất đơn giản;
- nhưng evidence bên trong có chiều sâu.

“Đơn giản” không phải:

- ít nghiên cứu;
- chỉ 3 bullet;
- bỏ công thức;
- bỏ result.

Nó nghĩa là:

- mỗi slide chỉ có **một câu hỏi hoặc một kết luận**;
- một primary visual;
- ít text;
- không trang trí thừa;
- không nhét cả report lên slide.

---

# 17. Phong cách thiết kế slide tôi khuyên dùng

## 17.1. Format

- 16:9.
- White / very light background.
- Không dùng dark cyberpunk theme.
- Không gradient.
- Không neon.
- Không animation phức tạp.
- Không ảnh AI minh họa taxi/robot nếu không phục vụ evidence.

Research deck phải giống:

> một nhóm nghiên cứu trình bày experiment,

không giống:

> pitch deck startup.

---

## 17.2. Palette

Giữ gần phong cách DOCX hiện tại: trắng + navy.

Khuyến nghị:

- Background: `#FFFFFF`
- Primary text: `#1A1A1A`
- Primary research/navy: `#17365D`
- Secondary gray: `#6B7280`
- Light divider: `#E5E7EB`

Semantic colors:

- Full / Proposed: blue/navy
- No Forecast: gray
- No Fairness: red
- Reproduced: green chỉ dùng cho status
- Partial: amber
- Not Reproduced: red

Không dùng màu status làm màu chart nếu gây nhầm.

---

## 17.3. Mapping màu phải cố định

Ví dụ toàn deck:

- `Full / MOMAQL` = blue
- `No Forecast` = gray
- `No Fairness` = red

Đừng slide 8 Full màu xanh, slide 9 Full màu tím.

Consistency cực kỳ quan trọng.

---

## 17.4. Typography

Gợi ý:

- Title: 30–36 pt.
- Key conclusion number: 32–44 pt.
- Body: 20–24 pt.
- Chart axis/legend: >=18 pt nếu có thể.
- Citation/footnote: 10–12 pt.

Không dùng chữ 14–16 pt để nhét thêm nội dung.

Nếu phải dùng chữ bé:

> slide đang quá tải.

---

## 17.5. Layout

Một slide result tốt:

```text
[ Conclusion headline -------------------------------- ]

[              CHART 65–75%              ] [ 2 key points ]

[ footnote / data / seeds / lower-is-better            ]
```

Hoặc:

```text
[ Conclusion headline ]

[ Chart full width ]

[ 1 sentence interpretation ]
```

---

# 18. Headline phải là kết luận, không phải tên section

Không nên:

> “Experimental Results”

Nên:

> **“MOMAQL achieves the strongest balanced operating point, but LAF remains the fairness extreme.”**

Không nên:

> “Ablation Study”

Nên:

> **“Look-ahead adds +22.4% utility, but does not improve fairness in our implementation.”**

Không nên:

> “Multi-Horizon”

Nên:

> **“The forecast effect is delayed: ~0% through day 14, +20.2% utility by day 37.”**

Headline như vậy khiến mentor hiểu slide trong 2 giây.

---

# 19. Bộ slide chính tôi đề xuất

Nếu presentation khoảng 15 phút:

> **15–17 main slides + appendix.**

Nếu mentor chỉ cho 10 phút:

> rút xuống 11–12 slides, giữ các slide có dấu ★.

---

# Slide 1 ★ — Title + thesis

## Headline

**FairDispatch v3: Trend Replication of Long-Term Fairness-Aware Ride-Hailing Dispatch**

Subtitle:

> Replicating qualitative claims of Kang et al. (2024), not exact numerical results

## Show

Rất sạch:

- title;
- paper;
- 1 câu thesis;
- tên/project.

Không cần architecture ngay.

## Bạn nói

> “Bài này không đặt mục tiêu khớp con số paper. Em tách paper thành các claim về utility, fairness, forecast và horizon, rồi kiểm tra từng claim trên một simulator độc lập với dữ liệu NYC TLC thật.”

Thời gian: 20–30 giây.

---

# Slide 2 ★ — What is the scientific question?

## Headline

**Can look-ahead improve the utility–fairness decision over a long horizon?**

## Show

Một diagram cực đơn giản:

```text
Current request
   ↓
Assign driver now
   ↓
Driver ends in a new zone
   ↓
Future opportunities change
   ↓
Long-term utility / fairness
```

Bên phải:

- Utility ↑
- Inequality ↓
- Horizon ↑

## Bạn nói

Giải thích “myopic vs long-term”.

Không giải thích code.

---

# Slide 3 ★ — Claims to replicate

## Headline

**I evaluate claims, not paper numbers.**

## Show

6 claims, cực ngắn:

- C1: utility–fairness trade-off
- C2: better balanced operating point
- C3: long-horizon stability
- C4: forecast improves long-term fairness
- C5: forecast ablation improves utility + fairness
- C6: no-fairness => high utility, high inequality

Mỗi claim có icon/status để trống; status sẽ reveal ở cuối.

## Bạn nói

> “Toàn bộ experiment của em được tổ chức quanh các claim này.”

---

# Slide 4 ★ — Paper vs replication

## Headline

**This is an explicit approximation, not an exact reimplementation.**

## Show

Bảng 5–7 rows lớn, dễ đọc.

Quan trọng nhất:

- 2016 → 2013
- graph nodes → 67 TLC zones
- unspecified drivers → 200
- MLP → tabular Q canonical + MLP benchmark
- paper scalarisation → modified score
- baseline adaptation

## Bạn nói

> “Em muốn disclosure trước khi show result, vì các deviation này quyết định mức độ claim mà em có thể đưa ra.”

Đây là slide rất dễ ăn điểm.

---

# Slide 5 ★ — System / experiment architecture

## Headline

**All policies share the same simulator and joint assignment solver.**

## Show

```text
NYC TLC
↓
Temporal split
↓
60-s request batches
↓
Feasible driver set
↓
Policy score matrix
↓
Hungarian joint assignment + decline
↓
Driver state update
↓
Utility / Gini / variance
```

Một nhánh Q/look-ahead đi vào MOMAQL score.

## Bạn nói

Nhấn mạnh controlled comparison.

---

# Slide 6 — Data + protocol

## Headline

**The main comparison uses real validation demand and repeated seeds.**

## Show

4–6 big-number cards:

- Train: 912,375
- Val: 195,508
- Test: 195,510
- Drivers: 200
- Main seeds: 5
- Batch: 60s

Footer:

- NYC TLC 2013;
- 67 zones;
- ETA <= 600s;
- deadhead 12 mph haversine assumption.

## Bạn nói

Chỉ nói các giả định quan trọng.

Không đọc package versions.

---

# Slide 7 ★ — Baseline result

## Headline

**MOMAQL is the strongest balanced policy — not the fairest policy.**

## Show

Ưu tiên một scatter:

- x = Utility ↑
- y = Gini ↓

hoặc hai chart nhưng highlight rõ:

- MOMAQL;
- LAF fairness extreme.

Trên slide nên annotate:

> MOMAQL: 1.422M / 0.204  
> LAF: 0.766M / 0.002

## Bạn nói

> “MOMAQL đạt utility cao nhất và fair hơn Greedy, Nearest, REASSIGN. Nhưng LAF fair hơn hẳn, đổi lại utility thấp. Vì vậy kết luận đúng là balanced trade-off, không phải dominance.”

Đây là câu bắt buộc.

---

# Slide 8 — Pareto / λ

## Headline

**The empirical trade-off exists, but it is non-monotonic.**

## Show

Pareto plot hiện có, nhưng nên:

- bỏ đường nối nếu nó gây cảm giác “frontier lý tưởng”;
- dùng scatter + label λ;
- đánh dấu λ=0, 0.6, 0.8, 1.0.

## Bạn nói

- λ=1 cực fair nhưng utility collapse;
- interior points cải thiện cả hai metric;
- scalarisation + decline làm đường không monotonic.

Mentor thích cách giải thích này hơn việc chỉ nói “Pareto”.

---

# Slide 9 ★ — Ablation

## Headline

**Look-ahead adds +22.4% utility, but fairness is worse than No-Forecast.**

## Show

Hai panel:

### Utility
- Full: 1.422M
- No Forecast: 1.162M
- No Fairness: 0.898M

### Gini
- Full: 0.204
- No Forecast: **0.146**
- No Fairness: 0.450

Annotate:

- `Full vs No-Forecast: +22.4% utility`
- `No-Forecast is fairer on Gini`

## Bạn nói

Đây là slide thể hiện research honesty.

> “Ablation xác nhận look-ahead giúp utility, nhưng không xác nhận fairness direction của paper. Vì vậy C5 chỉ partial.”

Không né.

---

# Slide 10 ★ — Long-horizon utility

## Headline

**The look-ahead effect is delayed: ~0% through day 14, +20.2% by day 37.**

## Show

`multi_horizon_2phase_breakthrough.png` rất phù hợp.

Có thể đơn giản lại.

## Bạn nói

- phase 1: policies gần như giống nhau;
- phase 2: utility separates;
- day21 +5.1%;
- day28 +11.6%;
- day37 +20.2%.

Đây là một trong những result đẹp nhất project.

---

# Slide 11 ★ — Long-horizon fairness

## Headline

**The paper’s long-term fairness advantage is not reproduced by Gini.**

## Show

Chỉ fairness curve.

Highlight:

- Full Gini day37 ≈ 0.217
- No-Forecast ≈ 0.151

Ghi rõ:

> lower is better

## Bạn nói

> “Đây là nơi replication khác paper. Look-ahead giúp utility dài hạn nhưng không cải thiện fairness metric của em. Em giữ negative result này thay vì ép narrative.”

Nếu mentor nghiên cứu nghiêm túc, slide này rất có giá trị.

---

# Slide 12 — Mechanism probe

## Headline

**Policy decisions diverge only after the look-ahead becomes behaviorally relevant.**

## Show

2 mini plots:

- disagreement early vs late;
- Q Δ convergence.

Key annotations:

- day1–7 disagreement ~0.08%;
- day8–37 ~15%;
- Q update magnitude decreases toward day21–37.

## Bạn nói

> “Các diagnostic này giải thích timing, nhưng em coi chúng là correlational mechanism evidence, không phải causal proof.”

---

# Slide 13 — Fleet-scale sensitivity

## Headline

**Forecast value is strongest under scarcity and vanishes near saturation.**

## Show

N=100 / 200 / 400.

Có thể show utility advantage:

- ~42%
- ~23%
- ~0%

## Bạn nói

Đây là result rất hay vì nó chỉ ra operating condition.

---

# Slide 14 — Forecast representation

## Headline

**A real MLP forecast works, but the tabular look-ahead proxy performs better here.**

## Show

3 rows:

- Tabular Q
- MLP
- No Forecast

Utility + Gini.

## Bạn nói

- MLP là sensitivity experiment;
- không exact paper architecture;
- custom aggregation/rescaling;
- không overclaim.

Nếu presentation chỉ 10 phút, chuyển slide này xuống appendix.

---

# Slide 15 ★ — Corrected claim matrix

## Headline

**Several qualitative trends replicate; the core fairness forecast claim remains mixed.**

## Show

| Claim | Verdict |
|---|---|
| C1 | Reproduced, qualified |
| C2 | Reproduced within scope |
| C3 | Partial |
| C4 | **Not reproduced for fairness** |
| C5 | **Partial: utility yes, fairness no** |
| C6 | **Partial: inequality yes, utility no** |

Dùng status màu nhẹ.

## Bạn nói

Không giải thích lại toàn bộ.

Chỉ 3 takeaway.

---

# Slide 16 ★ — Limitations / threats to validity

## Headline

**The study tests qualitative mechanisms under a disclosed approximation.**

## Show

Chỉ 5 items:

1. 2013 vs 2016.
2. Tabular Q != paper MLP.
3. Modified scalarisation.
4. 200-driver / 67-zone simulator assumptions.
5. Baselines are adapted, not exact paper baselines.

Nếu còn chỗ:

6. lightweight ETA/no road network.

## Bạn nói

> “Vì những limitation này em không kết luận paper sai. Em chỉ kết luận các claim nào survive dưới implementation này.”

Đây là câu rất quan trọng.

---

# Slide 17 ★ — Conclusion

## Headline

**FairDispatch reproduces a long-horizon utility mechanism, but not the full long-term fairness claim.**

## Show

3 takeaways:

1. MOMAQL gives the strongest balanced utility/fairness point among adapted baselines.
2. Look-ahead has delayed utility value: +20% by day37.
3. Fairness benefit vs no-forecast is not reproduced; this is the main unresolved discrepancy.

Bottom:

> Next experiment: align paper scalarisation + exact forecast target + controlled causal ablations.

## Bạn nói

Không nói “project thành công 100%”.

Nói:

> “Giá trị của replication là xác định cả phần robust lẫn phần không robust.”

---

# 20. Appendix mentor sẽ rất thích

Main deck không cần chứa tất cả.

Appendix nên có 8–12 slides.

## A1 — Exact paper numbers

- Table 1;
- ablation;
- parameters.

## A2 — Paper vs project equations

- paper scalarisation;
- project scalarisation.

## A3 — Policy definitions

- Greedy;
- Nearest;
- LAF;
- Exact REASSIGN;
- MOMAQL.

## A4 — Per-seed R1

Show error bars/raw seed table.

## A5 — Per-seed ablation

Mentor hỏi:

> “+22.4% có nhất quán 5 seed không?”

Có thể trả lời từ raw data.

## A6 — Variance / CV

Vì paper dùng variance.

## A7 — Full multi-horizon table

1,2,3,4,5,6,7,14,21,28,37.

## A8 — MLP architecture

Có diagram nhỏ.

## A9 — Fleet scale

Full raw values.

## A10 — Mechanism diagnostics

- spatial disagreement;
- candidate pool;
- Q convergence;
- weekly-cycle rejection;
- score balance.

## A11 — Simulator invariants

- lifecycle;
- no overlap;
- feasibility;
- 20 tests;
- known two weak trace tests.

## A12 — Reproducibility

- commit;
- SHA-256;
- seeds;
- commands.

---

# 21. Những thứ KHÔNG nên đưa vào main slides

Không đưa:

- repository tree 40 dòng;
- package version table;
- 20 dòng command;
- full source screenshot;
- class diagram chi tiết;
- tất cả equations;
- 15-row dataset schema;
- full troubleshooting;
- all 16 CSV list;
- full TechDoc content.

Đó là appendix / tài liệu hỗ trợ.

Main talk phải trả lời:

> “What is the research question, what evidence did I obtain, and what does it mean?”

---

# 22. Figure hiện tại: cái nào dùng được, cái nào nên sửa

## 22.1. `r1_validation_unified_comparison.png`

Dùng được.

Nhưng trên slide:

- highlight MOMAQL;
- làm LAF thành fairness-extreme;
- các baseline còn lại neutral gray;
- thêm “lower Gini = fairer”.

Không để người nghe hiểu nhầm MOMAQL fair nhất.

---

## 22.2. `r2_ablation_unified_comparison.png`

Rất đáng dùng.

Thậm chí figure này tự cho thấy:

> No-Forecast Gini thấp hơn Full.

Vì vậy lời nói phải khớp chart.

Không được vừa show chart này vừa nói “forecast improves fairness”.

---

## 22.3. `multi_horizon_2phase_breakthrough.png`

Rất tốt cho utility narrative.

Tiêu đề slide phải nói **utility**.

Không dùng chart này làm evidence cho fairness.

---

## 22.4. `multi_horizon_unified_curve.png`

Rất quan trọng vì nó show cả utility lẫn Gini.

Trong main deck nên tách thành hai slide:

- utility;
- fairness.

Vì hai panel đang kể hai câu chuyện khác nhau.

---

## 22.5. `pareto_frontier_unified_curve.png`

Cần thận trọng với từ “Pareto frontier”.

Một số interior points có thể dominate nhau.

Trong slide nên gọi:

> **Empirical λ sweep / utility–fairness operating points**

an toàn hơn “true Pareto frontier”.

Có thể chỉ highlight non-monotonicity.

---

# 23. Cách nói khi trình bày

## 23.1. Nói theo evidence

Không:

> “Em nghĩ model này tốt.”

Nên:

> “Across 5 seeds, MOMAQL utility trung bình 1.422M với Gini 0.204; Greedy đạt 1.002M với Gini 0.531.”

---

## 23.2. Tách observation và interpretation

### Observation

> “Full và No-Forecast gần như tied utility tới day14.”

### Interpretation

> “Điều này gợi ý look-ahead chưa đủ ảnh hưởng đến assignment ở phase đầu.”

### Mechanism evidence

> “Policy disagreement day1–7 chỉ khoảng 0.08%, sau đó tăng lên ~15%.”

### Limitation

> “Tuy nhiên đây vẫn là correlational explanation.”

Cấu trúc này rất mạnh.

---

# 24. Mẫu opening 60 giây

Bạn có thể nói gần theo logic này:

> “Em được giao replicate xu hướng của paper Long-term Fairness in Ride-Hailing Platform. Vì paper không công bố đủ implementation details, em xác định từ đầu đây là trend replication chứ không phải exact numerical reproduction. Em tách paper thành sáu claim liên quan đến utility–fairness trade-off, baseline superiority, long-horizon behavior, forecast contribution và fairness ablation. Sau đó em xây một simulator độc lập trên NYC TLC thật, dùng cùng joint Hungarian assignment framework cho 5 policy, chạy main experiments trên 5 seeds, rồi dùng ablation và multi-horizon tới 37 ngày để kiểm tra từng claim. Kết quả quan trọng nhất là look-ahead tạo utility advantage trễ, đạt khoảng +20% ở day37; tuy nhiên fairness advantage so với no-forecast không xuất hiện. Vì vậy replication của em xác nhận một phần cơ chế dài hạn nhưng không xác nhận toàn bộ fairness claim của paper.”

Nếu bạn mở đầu như vậy, mentor biết ngay:

- bạn hiểu task;
- bạn hiểu giới hạn;
- bạn không che negative result;
- presentation sẽ có structure.

---

# 25. Mẫu closing 45 giây

> “Kết luận của em không phải paper được reproduce hoàn toàn. Em thấy ba điều. Thứ nhất, fairness-aware scoring tạo một operating point cân bằng tốt hơn các efficiency baselines, dù LAF vẫn là fairness extreme. Thứ hai, look-ahead tạo lợi ích utility rất rõ nhưng chỉ xuất hiện sau một horizon đủ dài, và effect phụ thuộc fleet scarcity. Thứ ba, fairness benefit của forecast không xuất hiện trong implementation này; No-Forecast thực tế có Gini thấp hơn. Do đó em đánh giá đây là partial trend replication. Bước tiếp theo em ưu tiên align scalarisation và forecast target sát paper hơn, rồi chạy controlled ablations để phân biệt effect do forecast, matching dynamics hay fairness objective.”

---

# 26. Các câu mentor rất có thể hỏi

## Q1. “Em replicate paper hay làm một hệ thống khác?”

**Trả lời:**

> “Em replicate ở mức qualitative claims dưới một implementation được disclosure rõ. Em không tuyên bố exact algorithmic reproduction vì dataset year, forecast representation và scalarisation có deviation. Bảng Paper-vs-Ours của em xác định chính xác phạm vi đó.”

---

## Q2. “Tại sao dùng 2013 trong khi paper dùng 2016?”

> “Đây là temporal-slice deviation. Em dùng dữ liệu TLC thật đã có pipeline chất lượng và temporal split reproducible. Vì year khác nên em không so absolute numbers, chỉ kiểm tra trend. Nếu muốn tăng fidelity, bước tiếp theo là chạy đúng 2016 slice.”

---

## Q3. “Tại sao dùng 200 drivers?”

> “Paper không nêu driver count đủ rõ nên 200 là assumption. Em không chỉ giữ một giá trị: em chạy sensitivity N=100/200/400 và thấy forecast advantage giảm về gần 0 khi fleet bão hòa, nên kết luận được giới hạn theo operating regime.”

Đây là câu trả lời rất mạnh.

---

## Q4. “Q-table của em có thật sự là forecast không?”

> “Không theo nghĩa demand-count predictor của paper. Em gọi chính xác nó là state-value/look-ahead proxy Q(zone,hour), học discounted future net utility. Em có một MLP demand predictor riêng để kiểm tra forecast representation và công khai khác biệt này.”

---

## Q5. “Vậy tại sao README/report nói forecast giúp fairness?”

Đây là câu nguy hiểm.

Nên trả lời thẳng:

> “Raw ablation hiện tại không hỗ trợ câu đó. Full tăng utility +22.4%, nhưng No-Forecast có Gini và variance thấp hơn. Vì vậy cách diễn giải đúng em sử dụng trong defense là utility contribution reproduced, fairness contribution not reproduced; claim joint utility+fairness chỉ partial.”

Không cố bẻ metric.

---

## Q6. “Paper nói prediction giúp long-term fairness, em có reproduce được không?”

> “Không theo Gini trajectory. Tới day14 hai policy gần nhau; từ day21 Full có utility advantage lớn dần nhưng No-Forecast lại có Gini thấp hơn. Vì vậy long-term fairness direction không reproduce. Em coi đây là central discrepancy.”

---

## Q7. “Vậy project còn giá trị gì nếu core fairness claim không reproduce?”

> “Replication không chỉ có giá trị khi confirm paper. Nó cho biết phần nào của claim robust với implementation changes. Ở đây long-horizon utility mechanism và scarcity sensitivity xuất hiện mạnh, còn fairness claim nhạy với objective/forecast representation. Điều này giúp xác định experiment tiếp theo cần align.”

---

## Q8. “LAF Gini 0.002, sao em nói MOMAQL tốt hơn?”

> “Em không nói MOMAQL fair hơn LAF. LAF là fairness extreme nhưng utility chỉ khoảng 0.766M. MOMAQL là balanced point: utility 1.422M với Gini 0.204. Kết luận là trade-off, không phải dominance.”

---

## Q9. “Tại sao No-Fairness lại utility thấp hơn? Không vô lý sao?”

> “Đây là discrepancy thật. Trong implementation của em, λ thay đổi candidate score và interaction với decline=0, nên fairness term không đơn thuần là penalty lấy bớt utility; nó có thể thay đổi throughput và future fleet distribution. Em mới có plausible mechanisms, chưa coi đó là causal proof.”

---

## Q10. “λ=0.8 utility cao hơn λ=0, vậy trade-off ở đâu?”

> “Empirical λ sweep không monotonic. Extreme λ=1 cho fairness gần hoàn hảo nhưng utility collapse, chứng minh có trade-off ở một vùng. Tuy nhiên interior λ còn thay đổi assignment dynamics, nên một số điểm cải thiện cả utility và fairness. Em gọi đây là empirical operating-point curve chứ không giả định một monotonic theoretical frontier.”

---

## Q11. “5 seeds có đủ không?”

> “5 seeds giúp thể hiện variability cho main experiments, nhưng không phải large-sample statistical guarantee. Em dùng mean/std và kiểm tra direction nhất quán; nếu nâng mức publication-grade, em sẽ tăng seeds và report confidence intervals/effect tests.”

---

## Q12. “Multi-horizon là chạy 11 lần hay một trajectory?”

> “Một trajectory với checkpoints tại các ngày 1,2,3,4,5,6,7,14,21,28,37. Cách này giữ cùng history tới mỗi checkpoint và phù hợp để quan sát cumulative divergence.”

---

## Q13. “Có data leakage không?”

Bạn phải giải thích đúng pipeline:

- train Q/MLP trên train;
- main evaluation trên val;
- temporal split;
- test được giữ riêng.

Nếu actual script nào dùng khác, phải theo code thực tế.

---

## Q14. “67 zones từ đâu?”

> “TLC taxi zone IDs có sẵn trong processed parquet. Đây là approximation cho graph nodes của paper, không phải reproduction exact spatial clustering.”

---

## Q15. “Tại sao 12 mph?”

> “Đây là lightweight simulator assumption để chuyển haversine deadhead distance thành ETA. Nó không phải road routing; em disclosure nó như threat to external validity.”

---

## Q16. “Hungarian solver có bắt mọi request phải match không?”

> “Không. Matrix được pad dummy rows/columns với decline/stay-idle score 0, nên request/driver có thể unmatched. Pair chỉ thắng decline nếu score có lợi.”

---

## Q17. “Test có chứng minh không double booking không?”

> “Test suite là sanity layer, không phải proof. Em còn biết hai trace-based tests hiện có coverage yếu vì record_trace mặc định False. Đây là known issue em đã ghi trong TechDoc.”

---

## Q18. “Mechanism day14–21 là do Q convergence à?”

> “Em chưa thể gọi là causal. Q update magnitude giảm và policy disagreement tăng cùng giai đoạn, nên nó là correlational support. Causal test cần intervention, ví dụ freeze Q tại các checkpoints hoặc inject controlled forecast strengths.”

---

## Q19. “MLP của em có giống paper?”

> “Không thể khẳng định exact vì paper under-specified. MLP của em là một demand-prediction sensitivity experiment với embeddings + hour one-hot + 64/32 hidden layers, sau đó aggregate/rescale để đi vào cùng score. Em không dùng nó để claim exact MLP reproduction.”

---

## Q20. “Strongest result của em là gì?”

Tôi khuyên trả lời:

> “Delayed utility effect of look-ahead: gần 0 tới day14, +5.1% day21, +11.6% day28, +20.2% day37, đi cùng policy disagreement chuyển từ ~0.08% early lên ~15% late.”

---

## Q21. “Weakest / unresolved result?”

> “Forecast fairness direction. Full có utility cao hơn nhưng Gini/variance xấu hơn No-Forecast. Đây là claim em chưa reproduce.”

---

## Q22. “Nếu có thêm 1 tuần, em làm gì?”

Ưu tiên:

1. align exact 2016 data;
2. implement paper scalarisation gần nhất có thể;
3. forecast OD counts trực tiếp;
4. controlled ablations:
   - frozen Q at day checkpoints;
   - same assignment decisions with/without fairness term;
   - matching decline sensitivity;
5. more seeds;
6. road-network ETA sensitivity.

---

# 27. Mentor không muốn nghe gì quá lâu?

Không mất 3 phút vào:

- cài Python;
- file structure;
- requirements;
- `pip install`;
- class names;
- generated DOCX;
- GitHub folder.

Nếu mentor hỏi engineering:

> appendix / TechDoc.

Main talk phải ưu tiên **scientific reasoning**.

---

# 28. Tỉ lệ thời gian thuyết trình

## Nếu 15 phút

- Problem + claims: 2 phút
- Scope + methodology: 3 phút
- Main results: 5 phút
- Mechanism + sensitivity: 2 phút
- Verdict + limitations: 2 phút
- Buffer: 1 phút

## Nếu 10 phút

- Problem: 1
- Scope: 1.5
- Method: 1.5
- R1 + ablation: 2.5
- horizon utility + fairness: 2
- verdict: 1.5

## Nếu 20 phút

Có thể thêm:

- Pareto;
- fleet sensitivity;
- MLP;
- mechanism probes.

---

# 29. Nguyên tắc “one slide = one claim”

Một slide chỉ nên trả lời một câu.

Ví dụ:

> “Does MOMAQL beat baselines?”

Một slide.

> “Does forecast matter?”

Một slide.

> “When does forecast matter?”

Một slide.

> “Does it improve fairness?”

Một slide khác.

Không gom cả bốn vào một trang.

---

# 30. Cách giảm text

Thay vì:

> “MOMAQL obtained a utility of 1.422M, while Greedy obtained 1.001M. The Gini coefficient of MOMAQL was 0.204…”

Dùng:

```text
+42% utility vs Greedy
0.204 Gini vs 0.531
```

và nói phần còn lại bằng miệng.

Slide là visual support.

Không phải teleprompter.

---

# 31. Table trên slide

Nếu table > 6 rows:

- đưa appendix;
- hoặc highlight 3 rows quan trọng.

Main table nên:

- làm MOMAQL bold;
- LAF fairness cell highlight;
- không tô 5 màu cho 5 policy.

---

# 32. Chart nên sửa theo nguyên tắc research

- Luôn ghi `Gini ↓` hoặc `lower is better`.
- Utility nên format `1.42M` thay vì `1,422,441.1207`.
- Error bar nếu 5 seed.
- Nếu chart long-horizon mean 5 seeds, ghi rõ.
- Nếu mechanism chỉ 3 seeds, ghi rõ.
- Nếu multi-horizon là checkpoint cùng trajectory, ghi rõ ở footnote.
- Không cắt trục theo cách phóng đại chênh lệch.
- Không dùng 3D.
- Không dùng pie chart.
- Không dùng radar chart cho scientific evidence.

---

# 33. Citation trên slide

Footer nhỏ:

> Kang et al., ECML PKDD 2024, arXiv:2407.17839

Ở slide methodology / paper claims.

Không cần cite paper ở mọi slide result của bạn.

Result slide nên có:

> Source: `reports/r2_ablation_results.csv`, 5-seed mean

Điều này làm deck rất audit-friendly.

---

# 34. Cách biểu diễn Reproduced / Partial / Not

Không chỉ dùng màu.

Dùng cả text/icon:

- ✓ Reproduced
- ~ Partial
- ✕ Not reproduced
- — Not evaluated

Vì:

- accessibility;
- mentor in bản in đen trắng vẫn đọc được.

---

# 35. Slide Research khác slide Tech/Product

## Product slide

Thường hỏi:

> What did we build?

## Research slide

Phải hỏi:

> What hypothesis did we test?

> What evidence supports/rejects it?

> What can we conclude?

Vì vậy đừng dành main deck cho architecture quá lâu.

Architecture chỉ là phương tiện để tạo evidence.

---

# 36. Tôi sẽ chấm bạn thế nào nếu là mentor?

Một rubric thực tế:

| Hạng mục | Trọng số tôi sẽ chú ý |
|---|---:|
| Hiểu đúng paper/question | 15% |
| Scope/deviation minh bạch | 15% |
| Experimental design đáng tin | 15% |
| Main evidence | 20% |
| Ablation + long-horizon | 15% |
| Phân tích discrepancy | 10% |
| Reproducibility | 5% |
| Kỹ năng trình bày/Q&A | 5% |

Điểm cao không đến từ animation.

Nó đến từ:

> **claim → experiment → evidence → verdict → limitation**

---

# 37. Ba thứ khiến tôi đánh giá bạn cao ngay

## 37.1. Chủ động nói negative result

> “Forecast utility replicated; forecast fairness did not.”

Rất mạnh.

---

## 37.2. Không gọi approximation là exact

> “Q is a look-ahead value proxy, not the paper’s demand MLP.”

Rất mạnh.

---

## 37.3. Phân biệt correlation và causation

> “Q convergence coincides with the transition; it does not prove it causes the transition.”

Rất mạnh.

---

# 38. Ba thứ khiến tôi trừ điểm ngay

## 38.1. Nói “MOMAQL tốt nhất mọi mặt”

Sai vì LAF fair hơn.

## 38.2. Nói “forecast cải thiện fairness”

Không khớp raw Gini/variance.

## 38.3. Nói “replicate paper thành công”

Quá rộng.

Phải nói:

> claim-by-claim.

---

# 39. Checklist trước ngày thuyết trình

- [ ] Sửa narrative C5: utility yes, fairness no.
- [ ] Sửa narrative C4: long-term fairness not reproduced by Gini.
- [ ] Không nói MOMAQL dominates LAF on fairness.
- [ ] Đổi “causal mechanisms” thành “mechanism probes” nếu chưa có controlled intervention.
- [ ] Kiểm tra mọi con số slide với CSV.
- [ ] Gini có label “lower is better”.
- [ ] Utility có unit rõ.
- [ ] Mỗi chart ghi seeds.
- [ ] Main vs mechanism experiment ghi 5 seeds / 3 seeds rõ.
- [ ] Commit current working tree.
- [ ] `git status` sạch.
- [ ] Regenerate reports/docs/figures từ commit final.
- [ ] Cập nhật checksum manifest/commit hash.
- [ ] Chuẩn bị appendix Paper-vs-Ours.
- [ ] Chuẩn bị appendix scalarisation equations.
- [ ] Chuẩn bị appendix raw ablation.
- [ ] Chuẩn bị câu trả lời vì sao 2013/200 drivers/67 zones.
- [ ] Chuẩn bị câu trả lời vì sao No-Fairness utility giảm.
- [ ] Chuẩn bị câu trả lời vì sao No-Forecast fairer.
- [ ] Rehearse 10 phút và 15 phút.
- [ ] Có bản PDF backup của slide.
- [ ] Không phụ thuộc internet trong presentation.

---

# 40. Nếu mentor chỉ cho bạn 8 slide

Giữ đúng 8:

1. Problem + thesis.
2. Claims.
3. Paper vs Ours.
4. Architecture/protocol.
5. Baseline trade-off.
6. Ablation.
7. Long-horizon utility + fairness split.
8. Claim matrix + conclusion.

Appendix chứa tất cả phần khác.

---

# 41. Nếu mentor cho 12–15 phút — bộ “tối ưu”

Tôi ưu tiên:

1. Title.
2. Scientific question.
3. Claims.
4. Paper vs Ours.
5. Simulator/experiment architecture.
6. Data/protocol.
7. Baseline result.
8. Pareto / λ.
9. Ablation.
10. Long-horizon utility.
11. Long-horizon fairness.
12. Mechanism disagreement/Q.
13. Fleet scale.
14. Claim matrix.
15. Limitations.
16. Conclusion.

MLP xuống appendix nếu thiếu thời gian.

---

# 42. Câu hỏi bạn phải tự trả lời trơn tru không nhìn slide

Bạn cần nói được ngay:

1. Paper giải bài toán gì?
2. “Long-term” khác short-term thế nào?
3. Utility của project là gì?
4. Fairness của project là gì?
5. Paper dùng fairness nào?
6. State/action/reward của implementation?
7. Forecast/look-ahead vào score ở đâu?
8. Tại sao Q không phải demand prediction?
9. Tại sao dùng Hungarian?
10. Tại sao decline option?
11. Tại sao 200 drivers?
12. Tại sao 67 zones?
13. Tại sao 2013?
14. Full vs No Forecast khác nhau đúng một thành phần gì?
15. Full vs No Fairness khác gì?
16. Main R1 result?
17. LAF nói lên điều gì?
18. Ablation nói lên điều gì?
19. Long-horizon utility nói lên điều gì?
20. Long-horizon fairness nói lên điều gì?
21. Claim nào mạnh nhất?
22. Claim nào fail?
23. Limitation lớn nhất?
24. Nếu làm tiếp, experiment đầu tiên là gì?

Nếu trả lời trơn tru 24 câu này, bạn gần như đã sẵn sàng defense.

---

# 43. Một cách kể dự án rất “research”

Bạn có thể tư duy toàn bộ buổi thuyết trình bằng 5 câu:

### 1. Question
> Paper nói look-ahead giúp cân bằng utility/fairness dài hạn. Điều đó có survive khi replicate độc lập không?

### 2. Method
> Tôi xây một controlled dispatch simulator, cùng assignment solver, nhiều policies, 5 seeds và long-horizon checkpoints.

### 3. Positive evidence
> MOMAQL có balanced utility/fairness tốt; look-ahead tạo delayed utility advantage rất lớn.

### 4. Negative evidence
> Nhưng forecast không cải thiện fairness trong implementation này, và removing fairness không tăng utility như paper.

### 5. Scientific conclusion
> Một số mechanisms robust, core fairness direction thì nhạy với implementation; cần alignment/causal ablations tiếp theo.

Đó là một câu chuyện nghiên cứu mạnh hơn nhiều so với:

> “Đây là model của em, đây là code, đây là accuracy.”

---

# 44. Mentor-facing “one sentence verdict”

Nếu mentor hỏi cuối cùng:

> “Tóm lại em replicate được không?”

Câu trả lời tôi khuyên:

> **“Em replicate được một phần các xu hướng định tính: balanced utility–fairness behavior và delayed long-horizon utility benefit của look-ahead xuất hiện rõ, nhưng forecast-driven fairness improvement và utility increase khi bỏ fairness không xuất hiện; vì vậy em đánh giá đây là a partial trend replication, không phải full reproduction.”**

Đây là câu chính xác nhất với evidence hiện tại.

---

# 45. Điều chỉnh Research Report trước khi dùng nó như nguồn cho slide

Tôi khuyên không bê nguyên verdict trong DOCX hiện tại lên slide.

Cần rà lại tối thiểu:

## A. C5

Hiện report nói:

> forecast helps utility + fairness: reproduced.

Nên đổi:

> utility contribution reproduced; fairness contribution not reproduced; overall partial.

## B. C4

Hiện report có wording cho rằng long-term fairness direction được xác nhận quanh day21.

Nhưng mean Gini:

- Full xấu hơn No-Forecast sau day21.

Nên đổi verdict.

## C. C2 wording

Đổi:

> “MOMAQL vượt trội baseline cả utility lẫn Gini cùng lúc”

thành:

> “MOMAQL đạt balanced operating point mạnh, trong khi LAF là fairness extreme.”

## D. “Causal mechanisms”

Đổi thành:

> “mechanism probes / candidate explanations”

trừ khi có controlled intervention.

---

# 46. Technical Documentation nên đóng vai trò gì trong presentation?

Không trình bày TechDoc từ đầu đến cuối.

TechDoc là:

> **defense backup.**

Nếu mentor hỏi:

- chạy lại bằng lệnh gì?
- data contract?
- simulator lifecycle?
- exact score?
- dependency?
- checksum?
- test?
- known issue?

Bạn mở appendix hoặc TechDoc.

Main slide không biến thành TechDoc.

---

# 47. Report DOCX hiện tại về mặt hình thức

Research Report hiện đã theo hướng academic/professional:

- nền trắng;
- heading navy;
- bảng gọn;
- figure từ data thật;
- không trang trí dư thừa.

Đó là style đúng.

Slide nên **đơn giản hơn nữa**:

- ít bảng hơn;
- font lớn hơn;
- một visual/claim;
- một câu conclusion ở top.

Không copy screenshot nguyên trang DOCX lên slide.

---

# 48. Một quy tắc slide rất quan trọng

> **Mentor phải hiểu “so what?” trong 5 giây.**

Nếu nhìn chart 5 giây mà chưa biết:

- tốt hay xấu;
- ai thắng;
- lower/higher;
- claim nào;

thì slide chưa tốt.

Do đó annotation trực tiếp:

```text
+22.4% utility
```

```text
No-Forecast has lower Gini
```

```text
Delayed divergence starts ~day21
```

tốt hơn để mentor tự đọc.

---

# 49. Backup plan nếu mentor bắt đầu hỏi code sâu

Không mở IDE rồi scroll ngẫu nhiên.

Chuẩn bị 4 code snippets appendix:

1. Hungarian + dummy decline.
2. MOMAQL score.
3. TD(0) update.
4. Driver commit state update.

Mỗi snippet tối đa 10–15 lines.

Highlight đúng dòng.

---

# 50. Backup plan nếu mentor hỏi thống kê

Bạn nên biết:

- main 5 seeds;
- mechanism một số 3 seeds;
- mean/std;
- không claim statistical significance nếu chưa làm test phù hợp;
- effect sizes về utility đủ lớn ở long horizon;
- fairness direction nhất quán cần đọc raw seeds trước khi nói tuyệt đối.

Nếu chưa có inferential statistics:

> nói rõ descriptive repeated-seed evidence.

Không invent p-value.

---

# 51. Backup plan nếu mentor hỏi “Why Gini?”

Nói:

> “Paper’s primary fairness is variance of accumulated utility. I retain variance, but Gini is used as a scale-normalized inequality summary that is easier to compare across operating points. I therefore avoid claiming metric equivalence and show both where the paper comparison matters.”

---

# 52. Backup plan nếu mentor hỏi “Why not exact numerical reproduction?”

Nói 4 lớp:

1. under-specified paper details;
2. different data year;
3. modified forecast;
4. modified scalarisation.

Sau đó:

> “Therefore exact number matching would create false precision.”

Câu này rất tốt.

---

# 53. Những điểm project thật sự đáng tự tin

Bạn có nhiều thứ đáng show:

- source implementation độc lập;
- real NYC TLC data;
- explicit dataset hashes;
- multi-seed comparisons;
- common matching framework;
- ablations;
- long-horizon checkpointing;
- Pareto/λ sweep;
- MLP sensitivity;
- fleet-scale sensitivity;
- mechanism diagnostics;
- known-issue disclosure;
- Research Report + TechDoc tách rõ.

Không cần cố biến mọi claim thành positive result để làm project “đẹp”.

Project đã có đủ chiều sâu.

---

# 54. Điều làm presentation xuất sắc

Một buổi presentation xuất sắc sẽ khiến mentor nghĩ:

> “Bạn này không chỉ chạy model. Bạn ấy biết audit paper, xác định fidelity, thiết kế experiment, đọc contradictory evidence, không overclaim và biết experiment tiếp theo cần làm gì.”

Đó mới là mức nên nhắm.

---

# 55. Final slide design specification

Nếu sau này tạo deck, tôi khuyên specification:

```text
Aspect ratio: 16:9
Background: white
Primary: #17365D
Text: #1A1A1A
Secondary: #6B7280
Full/MOMAQL: blue/navy
No Forecast: gray
No Fairness: red
Status green/amber/red only for verdict
Title: 32–36 pt
Body: 20–24 pt
Chart labels: >=18 pt
Footnote: 10–12 pt
Animations: none or simple appear
Transitions: none/fade
Max main bullets: 3
Primary visuals per slide: 1
```

Phong cách:

> **clean academic research presentation**.

Không dùng:

- glassmorphism;
- neon;
- gradient;
- 3D;
- stock taxi photo;
- AI image;
- decorative icons everywhere.

---

# 56. Action items ưu tiên trước presentation

## Priority 0 — phải làm

1. Sửa claim C4/C5 trong narrative.
2. Sửa C2 wording về LAF.
3. Không gọi mechanism correlation là causal.
4. Commit snapshot final, clean Git state.
5. Regenerate docs/results provenance.

## Priority 1 — rất nên làm

6. Tạo slide riêng utility horizon và fairness horizon.
7. Tạo corrected claim matrix.
8. Tạo Paper-vs-Ours slide.
9. Tạo baseline scatter utility vs Gini.
10. Chuẩn bị appendix equations.

## Priority 2 — nếu còn thời gian

11. Add more seeds / confidence intervals.
12. Re-run exact 2016 slice.
13. Align scalarisation closer to paper.
14. Controlled Q freeze/forecast-strength ablation.
15. Fix two weak trace tests.

---

# 57. Mentor verdict nếu bạn trình bày theo hướng hiện tại vs hướng tôi đề xuất

## Nếu bạn trình bày theo wording hiện report mà không sửa

Rủi ro:

- mentor thấy No-Forecast Gini thấp hơn;
- hỏi vì sao vẫn nói forecast improves fairness;
- thấy LAF Gini gần 0;
- hỏi vì sao nói MOMAQL tốt hơn cả Gini;
- credibility giảm.

## Nếu bạn trình bày theo hướng corrected

Bạn có thể nói:

> “Hai điểm paper không reproduce trong implementation của em là đây.”

Khi đó negative evidence trở thành:

- analytical maturity;
- research integrity;
- depth.

Đây là cách tôi khuyên.

---

# 58. Tóm tắt cuối cùng

## Mentor muốn nghe

- scientific question;
- exact claims;
- scope;
- paper-vs-ours;
- simulator validity;
- controlled experiment;
- results;
- ablation;
- horizon;
- negative results;
- mechanism evidence;
- limitations;
- reproducibility;
- next experiment.

## Mentor muốn thấy

- claim matrix;
- Paper-vs-Ours table;
- pipeline;
- R1 utility/fairness;
- ablation;
- horizon utility;
- horizon fairness;
- mechanism probe;
- fleet sensitivity;
- limitation/verdict.

## Slide nên như thế nào?

> **Đơn giản về hình thức, sâu về evidence.**

## Câu chuyện nên là gì?

> **Không phải “em build được MOMAQL”.**

Mà là:

> **“Em đã kiểm tra từng scientific claim của paper bằng một replication độc lập, và đây là bằng chứng cho phần reproduced cũng như phần không reproduced.”**

---

# 59. Câu cuối tôi muốn bạn nhớ khi lên bảo vệ

> **Không cần làm cho project trông hoàn hảo. Hãy làm cho reasoning của bạn trông đáng tin.**

Trong một replication study, một kết quả `Not Reproduced` được phân tích đúng có giá trị hơn một kết luận `Reproduced` không khớp dữ liệu.

Với project hiện tại, cách trình bày mạnh nhất là:

> **balanced-policy result mạnh + delayed utility effect mạnh + fairness discrepancy được công khai + mechanism/sensitivity được dùng để giải thích một cách có giới hạn.**

Đó là câu chuyện nghiên cứu thuyết phục nhất mà dữ liệu hiện tại cho phép.
