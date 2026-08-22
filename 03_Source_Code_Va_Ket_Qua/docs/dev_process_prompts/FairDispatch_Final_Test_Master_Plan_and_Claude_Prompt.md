# FAIRDISPATCH — FINAL HELD-OUT TEST EVALUATION
## Master Plan + Mentor Expectations + Claude Code Execution Prompt

> **Mục tiêu:** sử dụng `test.parquet` như **held-out temporal test set cuối cùng** để xác nhận các kết luận cốt lõi của FairDispatch sau khi toàn bộ implementation, hyperparameter và research interpretation đã được chốt trên Train + Validation.
>
> Đây KHÔNG phải một vòng tuning mới.
>
> Đây là **final scientific verification** trước khi cập nhật Research Report, TechDoc và Slide để đóng dự án.

---

# PHẦN A — TƯ DUY NGHIÊN CỨU CẦN GIỮ

## 1. Vai trò của Train / Validation / Test

Pipeline cần được trình bày rõ:

```text
NYC TLC 2013
│
├── TRAIN
│     ├── Train / build Q-table
│     └── Train MLP sensitivity model nếu có
│
├── VALIDATION
│     ├── Develop simulator
│     ├── Compare policies
│     ├── λ sweep
│     ├── Ablation
│     ├── Long-horizon
│     ├── Mechanism probes
│     ├── Fleet sensitivity
│     └── Freeze final configuration
│
└── TEST
      └── Final held-out verification
```

Test không được dùng để:

- chọn λ;
- đổi γ;
- đổi α;
- sửa score;
- sửa policy;
- sửa simulator;
- chọn seed đẹp;
- đổi số driver vì kết quả test chưa đẹp;
- thử nhiều cấu hình rồi chọn cấu hình tốt nhất trên test.

---

# 2. Nguyên tắc quan trọng nhất

Trước khi nhìn kết quả policy trên `test.parquet`, phải freeze:

```text
implementation
configuration
seed list
metrics
experiments
claim criteria
```

Sau khi test đã chạy:

> **Không được quay lại tune theo test.**

Nếu Test khác Validation:

> giữ nguyên kết quả và phân tích.

Đó mới là giá trị của held-out test.

---

# 3. Vì sao mentor sẽ quan tâm bước này?

Nếu tôi là mentor nghiên cứu, sau khi nghe toàn bộ validation experiments, tôi sẽ hỏi:

> “Các kết luận này có giữ được trên một khoảng thời gian chưa được dùng để phát triển hệ thống không?”

Tôi không cần Test ra số giống Validation.

Tôi muốn biết:

- hướng kết quả có generalize không;
- effect size thay đổi bao nhiêu;
- negative result có lặp lại không;
- claim nào robust;
- claim nào chỉ xuất hiện trên validation;
- limitation của implementation nằm ở đâu.

---

# PHẦN B — NHỮNG THÔNG TIN MENTOR SẼ MUỐN THẤY

## 4. Data split integrity

Mentor sẽ muốn biết:

```text
Train time range
Validation time range
Test time range
```

Và xác minh:

```text
max(train_timestamp) < min(validation_timestamp)
max(validation_timestamp) < min(test_timestamp)
```

Nếu có overlap:

> phải báo ngay.

Không được tiếp tục gọi test là held-out temporal test nếu overlap.

---

# 5. Test dataset audit

Trước khi chạy policy, tạo audit cho `test.parquet`.

Tối thiểu:

```text
row count
schema
time range
number of calendar days
unique pickup zones
unique dropoff zones
missing-value counts
invalid coordinate counts
fare distribution
duration distribution
request count per day
request count per hour
weekday/weekend composition
checksum
```

Không cần exploratory analysis quá sâu.

Mục tiêu là xác minh:

> Test hợp lệ và có cùng data contract với Validation.

---

# 6. Distribution shift summary

Mentor sẽ hỏi:

> “Test có giống Validation không?”

Không cần statistical paper-level domain adaptation analysis.

Nhưng nên so:

```text
Validation vs Test

Trips
Days
Fare mean / median
Duration mean / median
Hourly demand distribution
Top pickup zones
Weekday/weekend ratio
```

Nếu shift đáng kể:

> ghi nhận như một yếu tố giải thích possible generalization gap.

Không dùng shift để biện minh trước khi nhìn result.

---

# 7. Test temporal span

Phải xác định chính xác:

```text
test_days = ?
```

Điều này quyết định có thể kiểm chứng long-horizon tới:

```text
Day 37
```

hay không.

Nếu test < 37 days:

> không ép chạy Day 37.

Chỉ dùng checkpoints nằm trong test span.

---

# 8. Exact frozen configuration

Mentor phải nhìn được final config:

```text
Policy                 MOMAQL canonical
Drivers                200
λ                      0.5
γ                      0.9
α                      0.1
Batch Window           60 sec
Pickup ETA Threshold   600 sec
Deadhead cost          current frozen value
Assignment Solver      Hungarian joint assignment
Q-table checkpoint     exact file + SHA-256
Dataset                test.parquet + SHA-256
```

Nếu source hiện tại khác các con số trên:

> audit code và lấy **exact frozen values từ repository**, không sửa code để khớp tài liệu này.

---

# 9. Seed list

Không chọn seed sau khi xem Test.

Dùng đúng seed list của main validation experiments.

Output phải ghi:

```text
Seeds:
[...exact list...]
```

Nếu repository không có một canonical 5-seed list duy nhất:

> xác minh từ main validation experiment artifact/script trước khi chạy.

Không tự phát minh.

---

# 10. Environment / reproducibility

Mentor sẽ muốn:

```text
Git/source snapshot
Working tree status
Python version
OS
Package versions
CPU/GPU if relevant
Exact commands
Runtime
Dataset checksum
Q/model checksum
Output hashes nếu có
```

Không cần biến thành production MLOps.

Nhưng một người khác phải có khả năng biết:

> result đến từ snapshot nào.

---

# PHẦN C — PRE-REGISTERED FINAL TEST PROTOCOL

## 11. Tạo `FINAL_TEST_PROTOCOL.md` trước khi chạy Test

File này phải được tạo trước khi policy evaluation chạy.

Nó phải ghi:

```text
Purpose
Frozen implementation
Frozen configuration
Frozen seeds
Metrics
Experiments
Claim criteria
No-tuning rule
Output paths
Timestamp
Source snapshot
```

Sau khi tạo:

> không chỉnh protocol vì nhìn thấy test result.

Nếu buộc phải sửa do bug implementation thật:

- document bug;
- document change;
- rerun entire affected test suite;
- không chọn sửa chỉ vì metric xấu.

---

# 12. Không “mở Test thử một chút”

Không chạy:

```text
MOMAQL test seed 1
```

rồi nhìn xem đẹp không trước khi protocol freeze.

Data audit được phép.

Policy outcome inspection:

> chỉ sau freeze.

---

# PHẦN D — CORE FINAL TEST SUITE

## 13. Test Suite A — Main Baseline Comparison

Chạy 5 policies:

```text
MOMAQL
Greedy
Nearest
LAF
Exact REASSIGN
```

Trên:

```text
test.parquet
200 drivers
same frozen seeds
same simulator
same Hungarian assignment framework
```

Metrics tối thiểu:

```text
Total Utility
Gini
Variance
Std
Served Requests
Average Driver Income
Average Deadhead
```

Nếu metric nào validation main experiment không có hoặc không reliable:

> không invent.

---

# 14. Baseline outputs

Tạo:

```text
reports/final_test/test_baseline_per_seed.csv
reports/final_test/test_baseline_summary.csv
```

Per-seed:

```text
policy
seed
utility
gini
variance
std
served
avg_income
avg_deadhead
runtime
```

Summary:

```text
policy
utility_mean
utility_std
gini_mean
gini_std
variance_mean
variance_std
served_mean
...
```

---

# 15. Test Suite B — Key Ablation

Chạy:

```text
Full
No Forecast
No Fairness
```

Cùng:

```text
test.parquet
200 drivers
same frozen seeds
same Q checkpoint
same simulator
```

Output:

```text
test_ablation_per_seed.csv
test_ablation_summary.csv
```

---

# 16. Những câu hỏi Ablation phải trả lời

## Q1 — Forecast Utility benefit có generalize?

Validation:

```text
Full Utility > No Forecast
≈ +22.4%
```

Test cần tính:

```text
utility_delta_pct =
(Full - NoForecast) / NoForecast * 100
```

Không yêu cầu phải +22.4%.

Chỉ kiểm:

```text
direction
effect size
seed consistency
```

---

## Q2 — Fairness discrepancy có generalize?

Validation:

```text
No Forecast Gini < Full Gini
No Forecast Variance < Full Variance
```

Test cần trả lời:

```text
No Forecast còn fairer không?
```

Nếu có:

> negative result mạnh hơn vì generalize sang held-out test.

Nếu không:

> fairness discrepancy không stable across temporal splits.

Cả hai đều có giá trị.

---

## Q3 — No Fairness behavior có generalize?

Validation:

```text
No Fairness
→ inequality tăng mạnh
→ Utility lại giảm
```

Test cần tách hai direction:

```text
Inequality direction
Utility direction
```

Không gộp thành một verdict duy nhất.

---

# 17. Test Suite C — Long-Horizon Verification

Chỉ chạy nếu temporal span cho phép.

Preferred checkpoints nếu test đủ:

```text
1
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

Policies:

```text
Full
No Forecast
```

Metrics:

```text
Utility
Gini
Variance nếu practical
```

Output:

```text
test_long_horizon.csv
```

---

# 18. Nếu Test không đủ 37 ngày

Ví dụ Test chỉ có 14 ngày:

chạy:

```text
1
2
3
4
5
6
7
14
```

Report:

> Held-out test period does not support an independent 37-day verification.

Không tạo synthetic repeated days.

Không nối Test với Validation để đủ 37 ngày.

---

# 19. Multi-horizon implementation

Ưu tiên cùng methodology validation:

> một trajectory dài với checkpoints

nếu validation đã dùng cách đó.

Không chạy mỗi horizon như independent trajectory nếu đó không phải protocol validation.

---

# PHẦN E — NHỮNG EXPERIMENT KHÔNG NÊN CHẠY TRÊN TEST

## 20. Không chạy λ sweep trên Test

Validation đã dùng để khám phá operating points.

Test không dùng để:

> tìm λ tốt hơn.

Không chạy:

```text
0.0
0.2
0.4
...
1.0
```

trên test để chọn.

---

# 21. Không chạy exploratory mechanism probes trên Test như main suite

Không cần lặp lại:

```text
weekly-cycle hypothesis
candidate depth
core/periphery exploratory diagnostics
Q-state discovery
fairness score share
```

trừ khi có một pre-specified secondary verification rất rõ.

Test ưu tiên:

> core claims.

---

# 22. Không chạy fleet sensitivity để chọn driver count

Fleet 100/200/400 đã là validation sensitivity.

Không dùng Test để quyết định:

> 200 có phải tốt nhất không.

Nếu mentor sau này yêu cầu external robustness:

có thể làm một secondary appendix analysis.

Nhưng không nằm trong core final test.

---

# 23. MLP sensitivity

MLP benchmark là secondary sensitivity, không phải canonical paper reproduction.

Không bắt buộc chạy trên Test.

Nếu chạy:

- declare trước protocol;
- không dùng kết quả để thay canonical forecast;
- label Secondary Sensitivity.

Default recommendation:

> không chạy trong core final test.

---

# PHẦN F — METRICS & STATISTICAL REPORTING

## 24. Không chỉ báo mean

Với 5 seeds, report:

```text
mean
std
min
max
per-seed values
```

Đặc biệt cho:

```text
Utility
Gini
```

---

# 25. Paired seed differences

Vì cùng seed/scenario có thể so Full vs No Forecast:

tính per-seed:

```text
ΔUtility
ΔUtility%
ΔGini
ΔVariance
```

Sau đó report:

```text
mean paired delta
std paired delta
sign consistency
```

Ví dụ:

```text
Full Utility higher in 5/5 seeds
No Forecast lower Gini in 5/5 seeds
```

Thông tin này rất mentor-friendly.

---

# 26. P-value không phải ưu tiên

Chỉ có ~5 seeds.

Không nên cố biến project thành statistical significance exercise.

Ưu tiên:

```text
effect size
direction
seed consistency
mean ± std
```

Nếu có confidence interval:

> label clearly as descriptive/limited due small n.

Không overclaim significance.

---

# 27. Utility không gọi là Revenue

Trong tất cả Final Test output:

> dùng `Total Utility`.

Không tự đổi thành:

```text
Revenue
Profit
Platform Revenue
```

vì utility proxy hiện là:

```text
fare - deadhead cost proxy (+ future component in score)
```

tùy context.

---

# 28. Fairness terminology

Phải nói rõ:

```text
Fairness = concept/objective
Gini = inequality metric
Variance = paper-aligned dispersion metric
```

Gini:

```text
lower = more equal
```

Variance:

```text
lower = more equal
```

Không có một universal “fairness index” duy nhất.

---

# PHẦN G — VALIDATION VS TEST ANALYSIS

## 29. Tạo bảng trung tâm `validation_vs_test.csv`

Columns:

```text
finding_id
finding
validation_value
test_value
validation_direction
test_direction
generalized
notes
```

Ví dụ findings:

```text
MOMAQL Utility > Greedy
MOMAQL Gini < Greedy
MOMAQL Utility > Nearest
MOMAQL Gini < Nearest
LAF is fairness extreme
Full Utility > No Forecast
No Forecast Gini < Full
No Forecast Variance < Full
No Fairness Gini > Full
No Fairness Utility direction
Delayed long-horizon utility advantage
Long-horizon fairness direction
```

---

# 30. Mentor summary table

Tạo human-readable:

```text
reports/final_test/FINAL_TEST_MENTOR_SUMMARY.md
```

Bảng:

| Finding | Validation | Test | Generalized? | Interpretation |
|---|---|---|---|---|

Không chỉ dump CSV.

---

# 31. Effect-size comparison

Với key results:

```text
Validation effect
Test effect
Difference
```

Ví dụ:

```text
Full vs No Forecast Utility

Validation +22.4%
Test       +X%
```

Interpretation:

```text
same direction / weaker / stronger / reversed
```

---

# 32. Generalization không có nghĩa số giống nhau

Không dùng threshold kiểu:

> Test phải trong ±5% Validation.

Không có cơ sở.

Generalization chủ yếu xét:

```text
direction
relative ordering
qualitative trade-off
effect persistence
```

và report effect size.

---

# PHẦN H — CLAIM-BY-CLAIM FINAL VERDICT

## 33. C1 — Utility–Fairness trade-off exists

Test evidence:

- baseline operating points;
- MOMAQL vs LAF / efficiency baselines;
- optional canonical λ point only.

Không cần test λ sweep.

Verdict categories:

```text
Generalized
Partially Generalized
Not Generalized
Not Testable
```

---

# 34. C2 — Proposed policy provides a strong balanced point vs adapted baselines

Check:

```text
MOMAQL utility ranking
MOMAQL Gini relative to Greedy/Nearest/REASSIGN
LAF fairness extreme
```

Không yêu cầu MOMAQL fairer than LAF.

Không nói:

> dominates all baselines.

---

# 35. C3 — Long-horizon behavior

Check:

```text
trajectory stability
delayed utility divergence if horizon sufficient
```

Nếu test horizon ngắn:

```text
Not fully testable
```

không ép verdict.

---

# 36. C4 — Forecast improves long-term fairness

Validation hiện không reproduce.

Test:

```text
Full Gini/Variance vs No Forecast over horizon
```

Nếu Test vẫn No Forecast fairer:

> Not Reproduced, now confirmed on held-out test.

Nếu Test đảo lại theo paper:

> fairness direction is temporally unstable / validation discrepancy does not generalize.

Không đơn giản đổi thành “Reproduced” mà bỏ qua validation.

---

# 37. C5 — Forecast improves Utility + Fairness

Tách:

```text
Utility component
Fairness component
```

Final verdict có thể:

```text
Partial
```

nếu một phần giữ, một phần không.

---

# 38. C6 — Removing fairness raises Utility + inequality

Tách:

```text
inequality direction
utility direction
```

Nếu Test lại:

```text
inequality ↑
utility ↓
```

thì validation negative result generalizes.

Nếu utility direction đổi:

> mixed across temporal splits.

---

# 39. Tạo `test_claim_assessment.csv`

Columns:

```text
claim
paper_expectation
validation_result
test_result
generalization
final_verdict
evidence_file
caveat
```

---

# PHẦN I — FIGURES MENTOR SẼ MUỐN THẤY

## 40. Figure 1 — Test Baseline Utility vs Gini

Scatter:

```text
x = Gini ↓
y = Utility ↑
```

Policies:

```text
MOMAQL
Greedy
Nearest
LAF
REASSIGN
```

Không cần fancy style.

---

# 41. Figure 2 — Validation vs Test baseline

Có thể:

```text
Utility grouped bars
Gini grouped bars
```

hoặc paired dot plot.

Mục tiêu:

> nhìn direction nhanh.

---

# 42. Figure 3 — Test Ablation

Show:

```text
Full
No Forecast
No Fairness
```

Utility + Gini.

---

# 43. Figure 4 — Validation vs Test Ablation Delta

Ví dụ:

```text
Full vs No Forecast Utility gain
Validation vs Test
```

và:

```text
Gini difference
Validation vs Test
```

---

# 44. Figure 5 — Test Long-Horizon

Nếu test span đủ:

```text
Utility Full vs No Forecast
Gini Full vs No Forecast
```

Không bắt buộc nếu horizon không đủ.

---

# PHẦN J — MENTOR QUESTIONS CẦN CHUẨN BỊ TRƯỚC

## 45. “Test set có thực sự chưa dùng không?”

Phải trả lời dựa trên audit:

```text
Used only for checksum/data integrity before final protocol
No policy/hyperparameter selection used test outcomes
```

Nếu thực tế trước đây đã chạy policy trên Test:

> phải trung thực và hạ mức claim “untouched”.

Không giả.

---

# 46. “Vì sao main research dùng Validation mà giờ mới Test?”

Trả lời:

> Validation được dùng để phát triển implementation, kiểm tra ablation và lựa chọn/freeze research configuration. Test được giữ riêng để làm final held-out temporal verification.

---

# 47. “Nếu Test khác Validation thì sao?”

Trả lời:

> Không tune lại. Em report generalization gap và phân tích distribution shift / implementation sensitivity.

---

# 48. “Vì sao không chạy mọi experiment trên Test?”

Trả lời:

> Test dùng để xác nhận hypotheses cốt lõi đã được định nghĩa trước, không dùng để tiếp tục exploration. Exploratory experiments thuộc Validation.

---

# 49. “Có statistical significance không?”

Trả lời:

> Main evidence là effect size, mean/std và paired seed consistency. Với 5 seeds, em không overclaim formal significance.

---

# 50. “Test có đúng năm/data paper không?”

Không.

Vẫn là:

```text
NYC TLC 2013
```

Do đó final result vẫn là:

> trend replication under reconstructed implementation

không phải exact paper reproduction.

---

# PHẦN K — OUTPUT DIRECTORY

## 51. Root output path

Claude phải lưu toàn bộ Final Test work vào:

```text
D:\ProjectVSF\FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\03_Source_Code_Va_Ket_Qua
```

**Quan trọng:**

Trước khi ghi file, Claude phải xác minh path này thực sự tồn tại.

Nếu actual project root trên máy có tên gần giống nhưng khác:

```text
FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication
```

hoặc path khác,

> KHÔNG tự ghi nhầm sang project khác.

Hãy search `D:\ProjectVSF` và xác minh đúng repository chứa:

```text
03_Source_Code_Va_Ket_Qua
```

Sau đó dùng exact discovered path.

---

# 52. Cấu trúc đề xuất

Trong:

```text
03_Source_Code_Va_Ket_Qua
```

tạo/giữ cấu trúc:

```text
03_Source_Code_Va_Ket_Qua/
│
├── final_test/
│   ├── FINAL_TEST_PROTOCOL.md
│   ├── FINAL_TEST_README.md
│   ├── FINAL_TEST_MENTOR_SUMMARY.md
│   ├── test_dataset_audit.json
│   ├── split_integrity.json
│   ├── validation_vs_test.csv
│   ├── test_claim_assessment.csv
│   │
│   ├── baseline/
│   │   ├── test_baseline_per_seed.csv
│   │   └── test_baseline_summary.csv
│   │
│   ├── ablation/
│   │   ├── test_ablation_per_seed.csv
│   │   └── test_ablation_summary.csv
│   │
│   ├── long_horizon/
│   │   └── test_long_horizon.csv
│   │
│   ├── figures/
│   │   ├── test_baseline_utility_gini.*
│   │   ├── validation_vs_test.*
│   │   ├── test_ablation.*
│   │   └── test_long_horizon.*   # if applicable
│   │
│   └── logs/
│       ├── commands.log
│       ├── environment.txt
│       └── runtimes.csv
│
└── scripts/
    └── final_test/
        ├── audit_test_dataset.py
        ├── run_final_test_baselines.py
        ├── run_final_test_ablation.py
        ├── run_final_test_long_horizon.py
        └── build_final_test_summary.py
```

Nếu repository convention hiện tại có `reports/`, `figs/`, `scripts/` riêng:

> adapt structure theo project hiện tại.

Không tạo duplicate architecture vô lý.

---

# PHẦN L — EXECUTION GATES

## 53. Gate 1 — Protocol freeze

Claude phải dừng và xác nhận internally:

```text
FINAL_TEST_PROTOCOL.md created
Frozen config resolved
Seed list resolved
Source snapshot recorded
```

sau đó mới chạy policy evaluation.

Không cần hỏi user nếu mọi thứ resolve được từ repo.

---

# 54. Gate 2 — Dataset integrity

Nếu:

```text
temporal overlap
schema mismatch
missing critical columns
checksum mismatch
```

thì:

> không chạy final evaluation tiếp.

Tạo:

```text
FINAL_TEST_BLOCKER.md
```

và report blocker.

---

# 55. Gate 3 — Smoke test

Trước full 5-seed suite:

chạy một **technical smoke test** cực nhỏ chỉ để xác minh code path không crash.

Quan trọng:

> Không inspect / interpret policy performance từ smoke test.

Smoke test không được dùng để tune.

---

# 56. Gate 4 — Full suite

Sau smoke:

run full baseline + ablation.

Long horizon sau khi xác nhận temporal span.

---

# 57. Gate 5 — No tuning

Sau khi full result tồn tại:

> chỉ analysis/report.

Không đổi config.

---

# PHẦN M — CODE QUALITY / REPRODUCIBILITY

## 58. Reuse current research engine

Không viết lại simulator.

Không tạo policy copy mới.

Dùng exact current source.

Nếu cần script orchestration:

> import existing modules.

---

# 59. Output must be deterministic

Same:

```text
source
dataset
seed
config
```

phải reproduce same result trong giới hạn deterministic implementation.

---

# 60. Preserve raw outputs

Không chỉ ghi summary.

Phải giữ:

```text
per-seed raw result
```

để mentor có thể audit.

---

# 61. Failure handling

Nếu một seed fail:

không silently drop.

Report:

```text
policy
seed
error
```

và fail suite hoặc mark incomplete.

Không tính mean từ 4/5 seeds mà không nói.

---

# 62. Runtime

Ghi runtime:

```text
experiment
policy
seed
wall_time_sec
```

Mentor/app engineer cũng có thể hỏi scalability.

---

# PHẦN N — FINAL MENTOR-FACING SUMMARY

## 63. `FINAL_TEST_MENTOR_SUMMARY.md`

Đây phải là file dễ đọc nhất.

Structure:

```text
1. Why held-out test was run
2. Dataset integrity
3. Frozen protocol
4. Main baseline results
5. Ablation results
6. Long-horizon result
7. Validation vs Test
8. Claim-by-claim assessment
9. What generalized
10. What did not generalize
11. Limitations
12. Final scientific verdict
13. Files / reproducibility
```

---

# 64. Mentor summary không được né negative result

Nếu:

```text
forecast Utility benefit disappears
```

nói thẳng.

Nếu:

```text
No Forecast no longer fairer
```

nói thẳng.

Nếu:

```text
MOMAQL baseline ranking changes
```

nói thẳng.

Không viết lại claim để “đạt”.

---

# 65. Suggested final verdict categories

Không hard-code verdict trước.

Sau Test chọn dựa trên evidence:

```text
Strong Partial Trend Replication with held-out temporal support

Partial Trend Replication with mixed held-out generalization

Validation-only trend replication; key findings do not generalize

Insufficient held-out horizon for long-term verification
```

Không dùng:

> Full Reproduction

trừ khi evidence thực sự vượt scope hiện tại — điều này rất unlikely do implementation deviations.

---

# PHẦN O — SAU FINAL TEST

## 66. Chưa chỉnh Report trong task này

Task Final Test kết thúc khi:

```text
data audit
test experiments
validation-vs-test
claim assessment
mentor summary
figures
reproducibility
```

hoàn tất.

Sau đó mới làm vòng riêng:

```text
Research Report
TechDoc
Slides
Speaker Notes
```

để không trộn execution với writing.

---

# 67. Những tài liệu sau này cần update

Sau khi chúng ta review Final Test result:

```text
Research Report
Technical Documentation
Claim Matrix
Conclusion
Limitations
Slide deck
Speaker notes
Reproducibility section
```

Đây sẽ là vòng cuối của dự án.

---

# PHẦN P — MASTER PROMPT CHO CLAUDE CODE

## ROLE

Bạn là:

> **Senior Research Engineer + Reproducibility Engineer + Experimental ML Engineer**

Nhiệm vụ của bạn là thực hiện **Final Held-out Test Evaluation** cho FairDispatch.

Đây là final scientific verification.

Không phải exploration.

Không phải hyperparameter tuning.

---

# 68. Working directory

Target user-provided location:

```text
D:\ProjectVSF\FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication\03_Source_Code_Va_Ket_Qua
```

Trước khi code:

1. Search `D:\ProjectVSF`.
2. Xác minh đúng repository.
3. Xác minh folder `03_Source_Code_Va_Ket_Qua`.
4. Xác minh source/results hiện tại.
5. Xác minh train/val/test paths.

Nếu user-provided root khác actual existing project root chỉ bởi naming/version:

> dùng actual repository chứa đúng source bundle, và document resolved path.

Không ghi vào folder sai.

---

# 69. Read before execution

Đọc toàn bộ tài liệu/source liên quan:

```text
README
TechDoc
Research Report
existing reports
dataset checksum manifest
experiment scripts
simulator
policies
metrics
Q-table trainer/checkpoint
baseline scripts
ablation scripts
multi-horizon scripts
tests
```

Xác minh actual frozen implementation.

Không dựa hoàn toàn vào con số ghi trong prompt này nếu source hiện tại khác.

Source of truth:

```text
current finalized repository + existing canonical validation artifacts
```

---

# 70. Resolve canonical validation setup

Trước Test, tìm chính xác:

```text
main validation seed list
MOMAQL λ
γ
α
driver count
batch size/window
ETA threshold
deadhead cost
Q checkpoint
policy definitions
metric implementations
Hungarian solver
```

Không hỏi user nếu repo/artifact resolve được.

---

# 71. Create protocol FIRST

Tạo:

```text
final_test/FINAL_TEST_PROTOCOL.md
```

Nội dung đầy đủ theo các section ở trên.

Record:

```text
created_at
source snapshot
working tree status
dataset hashes
Q hash
seed list
experiments
metrics
no-tuning rule
```

Sau đó không sửa criteria do kết quả test.

---

# 72. Audit data BEFORE policy runs

Tạo script:

```text
scripts/final_test/audit_test_dataset.py
```

Audit:

- train;
- validation;
- test;

để xác minh temporal separation.

Outputs:

```text
test_dataset_audit.json
split_integrity.json
```

Include exact timestamps.

---

# 73. Check dataset checksum

Compare:

```text
test.parquet
```

against existing checksum manifest.

If mismatch:

> BLOCK.

Do not silently continue.

---

# 74. Determine test horizon

Compute actual calendar/temporal span.

Set long-horizon checkpoints to only supported horizons.

Record in protocol/readme.

---

# 75. Technical smoke test

Run a small code-path smoke test.

Do not use smoke result for scientific analysis.

Log only:

```text
PASS / FAIL
```

---

# 76. Run Main Baselines

Use exact current engine.

Policies:

```text
MOMAQL
Greedy
Nearest
LAF
Exact REASSIGN
```

Same canonical seed list.

Write raw per-seed immediately.

Do not wait until end to manually copy values.

---

# 77. Run Key Ablation

Variants:

```text
Full
No Forecast
No Fairness
```

Same seeds/config.

Write raw.

---

# 78. Run Long Horizon

Only if supported.

Use same single-trajectory-with-checkpoints methodology as canonical validation experiment if that is what source currently uses.

Do not redesign.

---

# 79. Build summaries

Generate:

```text
mean
std
min
max
paired deltas
sign consistency
```

for key comparisons.

---

# 80. Validation artifact loading

Do not rerun Validation unless necessary.

Prefer read existing verified validation CSVs.

Find canonical artifacts.

Document source files.

---

# 81. Build Validation vs Test

Create:

```text
validation_vs_test.csv
```

and human-readable analysis.

Do not compare unrelated experiment settings.

---

# 82. Claim assessment

Create:

```text
test_claim_assessment.csv
```

Use final test evidence.

Do not force claims to reproduce.

---

# 83. Figures

Generate clean research figures.

Do not overwrite validation figures.

Store under final_test figures.

Use consistent:

```text
Gini ↓
lower is better
Utility ↑
```

---

# 84. Mentor summary

Create:

```text
FINAL_TEST_MENTOR_SUMMARY.md
```

This is required.

It must answer:

```text
Did main baseline ordering generalize?
Did forecast Utility benefit generalize?
Did fairness discrepancy generalize?
Did No-Fairness inequality effect generalize?
Did delayed long-horizon effect generalize?
Which claims are now stronger/weaker?
```

---

# 85. Do not tune

ABSOLUTE RULE:

After any Test result is visible:

Do not modify:

```text
λ
γ
α
policy score
Q initialization
drivers
seed list
threshold
metric
simulator behavior
```

for the purpose of improving test.

If a genuine implementation bug is found:

1. document;
2. fix only if objectively a bug;
3. rerun all affected Test experiments;
4. document both invalidated and corrected run;
5. do not cherry-pick.

---

# 86. Do not run exploratory sweeps

Do not run on Test:

```text
λ sweep
random hyperparameter search
multiple driver counts to choose best
forecast model selection
seed selection
```

unless explicitly marked as secondary pre-specified analysis before Test outcomes are inspected.

Default:

> do not.

---

# 87. Test-set protection

Do not expose Test to product demo.

Do not copy Test results into live demo.

Test is research final evaluation.

---

# 88. Testing the evaluation code

Add/execute tests for:

```text
metric calculations
seed loop
output schema
dataset split integrity
paired delta calculations
checkpoint extraction
failure handling
```

Existing simulator tests must still pass.

---

# 89. Final output validation

Before finishing:

verify all expected files exist.

Verify CSV row counts.

Verify no missing seed.

Verify no NaN key metric without explanation.

Verify figures correspond to CSV.

Verify summary numbers programmatically match raw per-seed.

---

# 90. Final report from Claude

When finished, respond with:

```text
Resolved project path:
...

Protocol:
...

Test data audit:
...

Temporal split integrity:
...

Frozen configuration:
...

Seeds:
...

Baseline Test:
...

Ablation Test:
...

Long-horizon Test:
...

Validation vs Test:
...

Claims:
...

Artifacts:
...

Tests:
...

Runtime:
...

Known limitations:
...

IMPORTANT:
No test-driven tuning was performed.
```

Do not reply only:

> Done.

---

# PHẦN Q — ACCEPTANCE CHECKLIST

## Scientific integrity

- [ ] Test protocol frozen before policy outcomes.
- [ ] Train/Val/Test temporal integrity audited.
- [ ] Test checksum verified.
- [ ] No test-driven tuning.
- [ ] Same canonical seeds.
- [ ] Same frozen implementation.

## Baseline

- [ ] 5 policies.
- [ ] 5 canonical seeds.
- [ ] Raw per-seed retained.
- [ ] Mean/std/min/max.
- [ ] Utility/Gini/Variance.

## Ablation

- [ ] Full.
- [ ] No Forecast.
- [ ] No Fairness.
- [ ] Paired deltas.
- [ ] Seed direction consistency.

## Horizon

- [ ] Test span audited.
- [ ] Only valid checkpoints.
- [ ] Same methodology as Validation.
- [ ] No synthetic extension.

## Generalization

- [ ] Validation vs Test table.
- [ ] Effect-size comparison.
- [ ] Claim-by-claim final assessment.
- [ ] Negative results preserved.

## Reproducibility

- [ ] Commands logged.
- [ ] Environment captured.
- [ ] Source snapshot recorded.
- [ ] Dataset/Q hashes recorded.
- [ ] Runtime recorded.

## Mentor-facing

- [ ] FINAL_TEST_MENTOR_SUMMARY.md.
- [ ] Baseline figure.
- [ ] Ablation figure.
- [ ] Validation vs Test figure.
- [ ] Long-horizon figure if supported.

---

# PHẦN R — FINAL SCIENTIFIC GOAL

Sau task này, chúng ta phải có khả năng trả lời một câu rất rõ:

> **“Những kết luận nào của FairDispatch được phát triển trên Validation thực sự generalize sang một temporal test set chưa được dùng trong quá trình development?”**

Đó là mục đích duy nhất của Test.

Không phải:

> “Làm sao để Test đẹp?”

Sau khi câu hỏi này được trả lời xong:

> **bước cuối cùng của project là cập nhật Research Report + TechDoc + Slides bằng evidence Final Test, rồi đóng dự án.**
