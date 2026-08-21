# Speaker Notes — FairDispatch Research Presentation (Review Version, 31 slide)

Dựa trên `docs/FairDispatch_v3_Mentor_Presentation_Playbook.md` (mentor guidance) và số liệu thật đã verify lại trực tiếp từ `reports/*.csv` tại thời điểm build slide (Git HEAD `3174cefd4b98fc06172cbda8586f76da78d3ad9e`). Không có số liệu nào trong slide bị chỉnh sửa để giống paper hơn.

**Đây là bản review đầy đủ 32 slide** — chưa phải bản trình bày cuối cùng. Counter trên deck chạy tuần tự 1/32 → 32/32. Các slide chi tiết/bổ sung (công thức đầy đủ, per-seed summary, bảng raw, mechanism chi tiết...) giờ nằm **ngay sau** slide chính mà chúng bổ trợ, trong đúng Phần (1–4) của Agenda — không còn tách thành một khối "phụ lục" riêng ở cuối. Đọc hết rồi mới quyết định slide nào giữ lại khi thuyết trình thật, cùng mentor.

Agenda (5 phần) không đổi: Problem & Replication Scope · Methodology & Experimental Setup · Experimental Results & Analysis · Replication Assessment & Conclusion · Product Demo.

Quy ước mỗi slide: **Purpose** = mục tiêu slide này phục vụ câu chuyện gì · **What to say** = ý chính cần nói (không đọc nguyên văn slide) · **Key numbers** = số phải nhớ chính xác · **Caveat** = giới hạn/điều không được overclaim · **Mentor Q** = câu hỏi mentor rất có thể hỏi ngay sau slide này.

**Nguyên tắc bao trùm (đọc trước khi thuyết trình):** phân biệt rõ *"experiment đã được đánh giá đầy đủ"* với *"hướng gốc của paper được tái lập hoàn toàn"*. Cả 6 claim đều có evidence thật và đều được kiểm thử nghiêm túc — một số cùng hướng paper (Reproduced), một số khác hướng (Direction differs / trade-off khác). Không dùng ngôn ngữ pass/fail nhị phân; không biến negative result thành positive result.

---

## PHẦN 1 — Problem & Replication Scope (slide 3–7)

### Slide 1/32 — Title
**Purpose:** Định vị ngay từ đầu: đây là trend replication, không phải build sản phẩm.
**What to say:** "Em được giao replicate xu hướng của paper Long-term Fairness in Ride-Hailing Platform. Vì paper không công bố đủ implementation details, em xác định từ đầu đây là trend replication chứ không phải exact numerical reproduction."
**Caveat:** Không nói "tái lập paper" trần trụi — luôn kèm "trend/qualitative".
**Mentor Q:** "Em replicate paper hay làm một hệ thống khác?" → Q1.

### Slide 2/32 — Agenda
**Purpose:** Cho mentor biết cấu trúc 5 phần, dễ theo dõi.
**What to say:** Đọc nhanh 5 mục, nhấn: "Phần 5 hiện là placeholder, sẽ hoàn thiện sau khi phần research được chốt."
**Caveat:** Đừng dừng lại giải thích Product Demo ở đây — để dành slide 31.

### Slide 3/32 — Research Problem
**Purpose:** Định nghĩa Utility/Fairness bằng ngôn ngữ đơn giản trước khi vào bài toán long-term.
**What to say:** "Nếu chỉ tối ưu hiệu quả tức thời, một số tài xế liên tục nhận chuyến tốt hơn, chênh lệch accumulated income ngày càng lớn theo thời gian. Utility là tổng hiệu quả toàn hệ thống; Fairness là mức độ đồng đều của utility tích lũy giữa các driver."
**Caveat:** Visual 3-driver là minh họa khái niệm (đã ghi rõ trên slide), không phải dữ liệu thực nghiệm.

### Slide 4/32 — Why Look-ahead Matters
**Purpose:** Giải thích cơ chế opportunity cost trước khi vào công thức.
**What to say:** "Destination của chuyến hiện tại đặt driver vào một trạng thái không gian–thời gian mới; nếu trạng thái đó có giá trị tương lai cao, chấp nhận chuyến đó tạo lợi ích tích lũy ở batch sau. Myopic chỉ nhìn fare hiện tại; look-ahead cộng thêm future zone value."
**Caveat:** Đây là giải thích cơ chế, chưa phải bằng chứng thực nghiệm — bằng chứng ở slide 24 (Mechanism Probe).
**Mentor Q:** "Tại sao cần prediction?" → "opportunity cost của assignment hiện tại thay đổi theo giá trị trạng thái tương lai."

### Slide 5/32 — Original Paper Claims (định tính) · chi tiết cho slide 3–4/6
**Purpose:** Cung cấp bối cảnh gốc của paper bằng ngôn ngữ định tính — nguồn mà 6 claim (slide 6) được paraphrase từ đó.
**What to say:** "Đây là paraphrase tuyên bố định tính gốc của paper — em không trích số liệu Table gốc vì không thể verify độc lập trong phạm vi audit này."
**Caveat:** Không phải bản dịch nguyên văn paper, chỉ paraphrase phục vụ tổ chức claim.
**Mentor Q:** "Paper nói chính xác gì ở Table 1?" → Em chưa verify độc lập số liệu Table gốc nên không trích, chỉ dùng tuyên bố định tính.

### Slide 6/32 — Claims to Replicate
**Purpose:** Neo toàn bộ presentation vào 6 claim cụ thể (paraphrase từ slide 5).
**What to say:** Đọc nhanh C1–C6, nói: "Verdict cuối cùng ở Phần 4, mọi experiment sau đây phục vụ một hoặc nhiều claim này."
**Caveat:** Đừng tiết lộ verdict ở đây — để dành cho slide 28.

### Slide 7/32 — Paper vs Our Implementation
**Purpose:** Slide "ăn điểm" quan trọng nhất — chủ động công bố deviation trước khi mentor tự tìm ra.
**What to say:** "Em muốn disclosure trước khi show kết quả, vì các deviation này quyết định mức độ claim mà em có thể đưa ra."
**Key numbers:** 2013 vs 2016 · 200 driver (assumption) · 67 zone · tabular Q canonical + MLP benchmark riêng.
**Caveat:** Không nói "gần giống paper" — nói đúng "explicit approximation".
**Mentor Q:** "Tại sao dùng 2013 thay vì 2016?" / "Tại sao 200 driver?" → Q2, Q3.

---

## PHẦN 2 — Methodology & Experimental Setup (slide 8–13)

### Slide 8/32 — Experimental Architecture
**Purpose:** Chứng minh so sánh baseline công bằng (controlled comparison) trước khi tin kết quả.
**What to say:** "Cả 5 policy đi qua cùng một Hungarian joint assignment với dummy decline — khác biệt chính chỉ là score function, tránh confound."
**Caveat:** Không show code — chỉ sơ đồ pipeline.
**Mentor Q:** "Hungarian solver có bắt mọi request phải match không?" → không, dummy decline score 0.

### Slide 9/32 — 5 Policy Definitions · chi tiết cho slide 8
**Purpose:** Liệt kê chính xác score function từng policy khi mentor hỏi implementation detail.
**What to say:** "Cả 5 policy đi qua cùng `hungarian_batch_assign` với dummy decline — chỉ score function khác nhau."
**Caveat:** Không đọc hết bảng nếu không được hỏi sâu.
**Mentor Q:** "Nearest/Greedy/LAF hoạt động cụ thể thế nào?" → mở slide này.

### Slide 10/32 — Simulator Invariants & Test Suite · chi tiết cho slide 8
**Purpose:** Backup độ tin cậy simulator khi mentor hỏi về correctness, đặt ngay sau Architecture vì cùng nói về nền tảng simulator.
**What to say:** "20/20 test invariant pass — đây là sanity layer, không phải formal proof of correctness. Em tự phát hiện và công bố hai trace-based test có coverage yếu do record_trace mặc định False."
**Key numbers:** 20/20 test pass.
**Caveat:** Không nói "20/20 chứng minh simulator hoàn toàn đúng".
**Mentor Q:** "Test có chứng minh không double booking không?" → Q17.

### Slide 11/32 — MOMAQL Decision Logic
**Purpose:** Giải thích công thức score ở mức khái niệm, không cần đọc TD(0) đầy đủ.
**What to say:** "MOMAQL cộng ba phần vào score: immediate utility, future zone value (γ·Q look-ahead), và fairness adjustment (λ). Q là look-ahead value estimator, KHÔNG phải demand-count predictor như MLP của paper."
**Key numbers:** λ=0,5 · γ=0,9 · α=0,1 (mặc định).
**Caveat:** Không nói "λ của em giống λ của paper". Công thức đầy đủ + TD(0): slide 12.
**Mentor Q:** "Q-table của em có thật sự là forecast không?" → Q4.

### Slide 12/32 — Project Score + TD(0) Formula (full) · chi tiết cho slide 11
**Purpose:** Backup công thức toán học đầy đủ khi mentor muốn xem chi tiết thay vì bản khái niệm ở slide 11.
**What to say:** Đọc công thức, nhấn α/γ/λ mặc định và rule ablation (no_forecast ép Q_future=0, no_fairness ép λ=0).
**Key numbers:** λ=0,5 · γ=0,9 · α=0,1.
**Caveat:** Scalarisation không tương đương toán học với paper — λ hai bên không so sánh trực tiếp.
**Mentor Q:** "Công thức cụ thể ra sao, TD(0) update thế nào?" → mở slide này.

### Slide 13/32 — Dataset & Experimental Protocol
**Purpose:** Cho mentor thấy quy mô thực nghiệm nghiêm túc, dùng demand thật.
**What to say:** Đọc nhanh 6 con số, không đọc package version.
**Key numbers:** Train 912.375 · Val 195.508 · Test 195.510 · 200 driver · 5 seed · batch 60s.
**Caveat:** Không dành quá 20 giây cho slide này.

---

## PHẦN 3 — Experimental Results & Analysis (slide 14–27)

### Slide 14/32 — Main Baseline Comparison
**Purpose:** Câu bắt buộc phải nói đúng trong toàn bộ presentation. Scatter thật: X=Gini (trái=fair hơn), Y=Utility (trên=tốt hơn).
**What to say:** "MOMAQL đạt utility cao nhất và fair hơn Greedy, Nearest, REASSIGN. LAF nằm sát trục trái (Gini gần 0) nhưng utility thấp nhất. Đây là balanced trade-off, không phải dominance."
**Key numbers:** MOMAQL 1.422.441$/0,204 · Greedy 1.001.551$/0,531 · Nearest 789.444$/0,430 · LAF 766.265$/0,002 · REASSIGN 648.160$/0,417.
**Caveat:** KHÔNG BAO GIỜ nói "MOMAQL tốt nhất mọi mặt" — LAF fair hơn rõ rệt.
**Mentor Q:** "LAF Gini 0,002, sao em nói MOMAQL tốt hơn?" → Q8.

### Slide 15/32 — R1 Per-Seed Summary · chi tiết cho slide 14
**Purpose:** Chứng minh kết quả R1 nhất quán qua 5 seed, không phải seed may mắn.
**What to say:** "Dot = mean 5 seed, thanh mờ = khoảng min–max."
**Key numbers:** MOMAQL 1.412.304–1.433.470$ · Greedy 986.915–1.021.638$ · LAF 731.814–797.745$.
**Caveat:** Summary trực quan; 25 dòng raw gốc ở `reports/r1_validation_results.csv`.
**Mentor Q:** "Kết quả R1 có ổn định qua từng seed không?" → mở slide này.

### Slide 16/32 — Utility–Fairness λ Sweep
**Purpose:** Scatter Utility vs Gini theo từng λ — cho thấy non-monotonicity trực quan.
**What to say:** "λ không chỉ đổi trọng số theo đường tuyến tính — nó đổi cả candidate ordering và throughput trong Hungarian assignment. λ=0,8 có utility cao nhất, cao hơn cả λ=0,6."
**Key numbers:** λ=0,8 → 1.555.401$/0,228 · λ=1,0 → 766.265$/0,0019 (gần trùng LAF).
**Caveat:** Không gọi đây là "true Pareto frontier" — dùng "Empirical λ Sweep".
**Mentor Q:** "Vì sao λ=0,8 utility cao hơn λ=0?" → Q10.

### Slide 17/32 — Ablation Study
**Purpose:** Slide thể hiện research honesty rõ nhất, đóng khung như trade-off đa mục tiêu — không phải Full "thắng" No-Forecast.
**What to say:** "Full không fair hơn No-Forecast. Nó tạo một operating point có Utility cao hơn 22,4% nhưng inequality cũng cao hơn. Platform có thể chọn Full nếu ưu tiên efficiency hơn — đó là preference, không phải bằng chứng Full công bằng hơn."
**Key numbers:** Full 1.422.441$/0,2037 · No Forecast 1.162.077$/0,1458 · No Fairness 898.025$/0,4504.
**Caveat:** KHÔNG được nói "forecast improves fairness" — raw data cho hướng ngược lại.
**Mentor Q:** "Vậy tại sao tài liệu cũ nói forecast giúp fairness?" → Q5.

### Slide 18/32 — Ablation Per-Seed Summary · chi tiết cho slide 17
**Purpose:** Chứng minh +22,4% utility và Gini gap nhất quán 5/5 seed, không phải một seed lệch.
**What to say:** "Cả 5 seed đều cho Full utility cao hơn và Gini cao hơn No-Forecast — không có seed nào đảo chiều."
**Key numbers:** Full 1.412.304–1.433.470$ · No Forecast 1.149.234–1.186.956$ · No Fairness 859.659–931.964$.
**Mentor Q:** "+22,4% có seed nào lệch không?" → khẳng định 5/5 seed cùng hướng, mở slide này làm bằng chứng.

### Slide 19/32 — Variance / Coefficient of Variation · chi tiết cho slide 17
**Purpose:** Đối chiếu với metric variance mà paper thực sự dùng làm fairness quantity chính (thay vì Gini).
**What to say:** "Paper dùng variance của accumulated utility. Em báo Gini làm metric trực quan chính vì dễ đọc, ít nhạy scale, nhưng vẫn giữ variance/CV song song."
**Key numbers:** Full variance 8.345.652 · No Forecast 2.473.498 · No Fairness 14.234.559.
**Mentor Q:** "Sao dùng Gini mà không dùng variance như paper?" → mở slide này, đọc số liệu song song.

### Slide 20/32 — MLP Benchmark · chi tiết cho slide 17
**Purpose:** Backup kiến trúc MLP + so sánh 3 forecast representation — mở rộng câu chuyện ablation (No-Forecast bỏ hẳn forecast; MLP đổi cách biểu diễn forecast).
**What to say:** "MLP thật vẫn tốt hơn rõ No-Forecast, nhưng tabular Q canonical vẫn tốt hơn MLP trong simulator này — kết quả phụ thuộc cách forecast được biểu diễn."
**Key numbers:** Tabular Q 1.422.441$/0,204 · MLP 1.392.473$/0,226 · No Forecast 1.162.077$/0,146.
**Caveat:** Không tuyên bố tái lập chính xác kiến trúc MLP của paper (paper under-specified).
**Mentor Q:** "MLP của em có giống paper không?" → Q19.

### Slide 21/32 — Long-Horizon Utility (line chart)
**Purpose:** Một trong những kết quả đẹp nhất project — hiệu ứng trễ (delayed effect).
**What to say:** "Quan sát 1: hai đường gần như trùng nhau đến ngày 14. Quan sát 2: utility tách rõ từ ngày 21, đạt +20,19% ở ngày 37."
**Key numbers:** Ngày 21: +5,15% · Ngày 28: +11,65% · Ngày 37: +20,19%.
**Caveat:** Trục ngày không tuyến tính (1..7 rồi nhảy 14,21,28,37) — đã ghi chú trên chart.

### Slide 22/32 — Long-Horizon Fairness (line chart)
**Purpose:** Slide negative-result quan trọng nhất deck — phải nói thẳng, không né.
**What to say:** "Quan sát 1: đến ngày 14, Gini gần bằng nhau. Quan sát 2: từ ngày 21, Full có Gini cao hơn — kém công bằng hơn No-Forecast. Đây là nơi replication khác paper."
**Key numbers:** Ngày 37 — Full Gini 0,217 vs No-Forecast Gini 0,151.
**Caveat:** Central discrepancy của cả bài. Dùng "Direction differs", không dùng "Not Reproduced" trần trụi.
**Mentor Q:** "Paper nói prediction giúp long-term fairness, em có reproduce được không?" → Q6.

### Slide 23/32 — Full Multi-Horizon Table · chi tiết cho slide 21–22
**Purpose:** Bảng đầy đủ 11 checkpoint, backup số cho cả slide 21 (Utility) và 22 (Fairness) khi mentor hỏi một ngày cụ thể.
**What to say:** Chỉ đọc nếu mentor hỏi số chính xác một ngày nào đó.
**Mentor Q:** "Ngày 21 (hoặc bất kỳ ngày nào) chính xác utility/Gini bao nhiêu?" → mở bảng này.

### Slide 24/32 — Mechanism Probe
**Purpose:** Giải thích TIMING của sự phân kỳ (slide 21–22), không chứng minh nguyên nhân.
**What to say:** "Các diagnostic này giải thích timing, em coi chúng là correlational evidence, không phải causal proof."
**Key numbers:** Disagreement ngày 1–7 ≈0,08% → ngày 8–37 ≈15%. |ΔQ|: ngày 7≈1,88 → ngày 37≈0,82.
**Caveat:** Không dùng từ "chứng minh" — chỉ "gợi ý"/"trùng khớp thời điểm".
**Mentor Q:** "Mechanism ngày 14–21 là do Q convergence à?" → Q18.

### Slide 25/32 — Mechanism Diagnostics Chi Tiết · chi tiết cho slide 24
**Purpose:** Thêm chi tiết Q-convergence, weekly-cycle hypothesis, spatial candidate pool.
**What to say:** Đọc phần liên quan câu hỏi cụ thể. Nhấn: weekly-cycle hypothesis đã bị bác bỏ bằng thực nghiệm — không có chu kỳ 7 ngày rõ ràng.
**Key numbers:** state visited ngày 1≈1.086 → ngày 37≈1.441 · fairness score share ngày 1≈1,2% → ngày 37≈4,5%.
**Caveat:** Correlational, không causal. Candidate-pool dùng geometry tĩnh, chỉ là diagnostic mật độ.
**Mentor Q:** "Weekly cycle có thật không?" → Không, đã bác bỏ bằng thực nghiệm, xem slide này.

### Slide 26/32 — Fleet-Scale Sensitivity
**Purpose:** Cho thấy hiểu operating regime, không chỉ hiểu một con số cố định.
**What to say:** "Look-ahead mạnh nhất khi thiếu cung (N=100: +41,9%), giảm dần khi fleet bão hòa (N=400: gần 0%)."
**Key numbers:** N=100: +41,9% · N=200: +23,3% · N=400: +0,0%.
**Caveat:** 3 seed (không phải 5).
**Mentor Q:** "Tại sao dùng 200 drivers?" → "Em chạy sensitivity N=100/200/400 và thấy forecast advantage giảm về gần 0 khi fleet bão hòa."

### Slide 27/32 — Fleet-Scale Full Raw Results · chi tiết cho slide 26
**Purpose:** Backup số liệu đầy đủ cho slide 26.
**What to say:** Đọc nếu mentor hỏi raw N=100/200/400 chi tiết.
**Key numbers:** N=100 full 1.114.780$/0,1199, no-forecast 785.366$/0,0999 · N=200, N=400 tương tự (xem bảng).
**Caveat:** 3 seed, không phải 5.
**Mentor Q:** "Số liệu fleet-scale đầy đủ ra sao?" → mở slide này.

---

## PHẦN 4 — Replication Assessment & Conclusion (slide 28–29)

### Slide 28/32 — Claim-by-Claim Replication Assessment
**Purpose:** Slide trả lời trực tiếp "Cuối cùng em replicate được không?" — dễ bị hiểu sai nhất nếu nói không cẩn thận.
**What to say:** "6/6 claim đã được kiểm thử đầy đủ bằng experiment thật — khác với '6/6 claim đều reproduced hoàn toàn'. C1, C2 cùng hướng paper. C3 supported có điều kiện. C4, C5, C6 cho thấy trade-off/direction khác paper ở một phần — không phải experiment thất bại."
**Caveat quan trọng nhất của cả deck:** KHÔNG nói "6/6 claim reproduced". Chỉ nói "6/6 claim đã được kiểm thử/đánh giá". Về C4: long-term fairness direction không reproduce theo Gini/variance — nói thẳng. Về C6: inequality direction giống paper, Utility direction khác — chỉ nửa hướng đúng.
**Mentor Q:** "Tóm lại em replicate được không?" → one-sentence verdict cuối file.

### Slide 29/32 — Limitations & Conclusion
**Purpose:** Đóng phần research story bằng framing cân bằng: không phải fail/success nhị phân, cũng không overclaim.
**What to say:** "FairDispatch tái lập được cơ chế trade-off và lợi ích Utility dài hạn của look-ahead. Fairness direction thì khác paper. Tổng thể: Strong Partial Trend Replication."
**Caveat:** Không dùng "Full Reproduction". Không dùng "project thất bại".
**Mentor Q:** "Nếu có thêm 1 tuần, em làm gì?" → Q22.

---

## PHẦN 5 — Product Demo (slide 30)

### Slide 30/32 — Product Demo (placeholder)
**Purpose:** Giữ đúng cấu trúc 5 phần đã hứa trong Agenda, không vội invent demo.
**What to say:** "Phần này sẽ hoàn thiện sau khi research story được chốt với mentor."
**Caveat:** Không trình bày flow demo cụ thể nào chưa được audit.

---

## CLOSING — Tổng kết & Cảm ơn (slide 31–32)

### Slide 31/32 — Overall Project Conclusion
**Purpose:** Tổng kết toàn bộ dự án ở tầm nhìn cao (khác slide 29 — slide 29 chỉ nói về replication verdict, slide này nói về cả khối lượng công việc: simulator, 5 policy, 15+ experiment).
**What to say:** "Em đã xây một simulator độc lập với 5 policy dùng chung solver, chạy hơn 15 experiment để kiểm thử cả 6 claim bằng dữ liệu thật, và báo cáo trung thực mọi kết quả kể cả phần khác hướng paper. Verdict cuối: Strong Partial Trend Replication."
**Key numbers:** 5 policy · 15+ experiment · 6/6 claim kiểm thử · 5 seed.
**Caveat:** Đây là slide tổng kết ngắn — không lặp lại chi tiết đã nói ở slide 28/29, chỉ chốt bằng 4 dòng + verdict badge.
**Mentor Q:** —

### Slide 32/32 — Cảm ơn
**Purpose:** Đóng buổi trình bày, mở phần Q&A.
**What to say:** "Cảm ơn mentor đã dành thời gian. Em sẵn sàng cho câu hỏi."
**Caveat:** Không thêm nội dung mới ở đây — đây là slide bookend đơn giản, giống phong cách slide Title.
**Mentor Q:** —

---

## Ngân hàng câu trả lời nhanh (trích mentor playbook, đã verify số liệu — số slide đã cập nhật theo thứ tự mới)

**Q1. Em replicate paper hay làm hệ thống khác?**
Em replicate ở mức qualitative claims dưới một implementation được disclosure rõ. Em không tuyên bố exact algorithmic reproduction vì dataset year, forecast representation và scalarisation có deviation. Bảng Paper-vs-Ours (slide 7) xác định chính xác phạm vi đó.

**Q2. Tại sao dùng 2013 trong khi paper dùng 2016?**
Đây là temporal-slice deviation. Em dùng dữ liệu TLC thật đã có pipeline chất lượng và temporal split reproducible. Vì year khác nên em không so absolute numbers, chỉ kiểm tra trend.

**Q3. Tại sao dùng 200 drivers?**
Paper không nêu driver count đủ rõ nên 200 là assumption. Em chạy sensitivity N=100/200/400 (slide 26) và thấy forecast advantage giảm về gần 0 khi fleet bão hòa, nên kết luận được giới hạn theo operating regime.

**Q4. Q-table của em có thật sự là forecast không?**
Không theo nghĩa demand-count predictor của paper. Em gọi chính xác nó là state-value/look-ahead proxy Q(zone,hour), học discounted future net utility. Em có một MLP demand predictor riêng để kiểm tra forecast representation (slide 20) và công khai khác biệt này.

**Q5. Vậy tại sao có tài liệu cũ nói forecast giúp fairness?**
Raw ablation hiện tại không hỗ trợ câu đó. Full tăng utility +22,4%, nhưng No-Forecast có Gini và variance thấp hơn. Cách diễn giải đúng em dùng trong defense là: utility contribution reproduced, fairness contribution direction differs; claim joint utility+fairness chỉ partial (C5).

**Q6. Paper nói prediction giúp long-term fairness, em có reproduce được không?**
Không theo Gini trajectory. Tới ngày 14 hai policy gần nhau; từ ngày 21 Full có utility advantage lớn dần nhưng No-Forecast lại có Gini thấp hơn. Long-term fairness direction không reproduce — em coi đây là central discrepancy (C4: Direction differs).

**Q7. Vậy project còn giá trị gì nếu core fairness claim không reproduce?**
Replication không chỉ có giá trị khi confirm paper. Nó cho biết phần nào của claim robust với implementation changes. Cả 6 claim đều đã được kiểm thử nghiêm túc bằng experiment thật, dù không phải mọi hướng đều khớp paper.

**Q8. LAF Gini 0,002, sao em nói MOMAQL tốt hơn?**
Em không nói MOMAQL fair hơn LAF. LAF là fairness extreme nhưng utility chỉ khoảng 766.265$. MOMAQL là balanced point: utility 1.422.441$ với Gini 0,204. Kết luận là trade-off, không phải dominance.

**Q9. Tại sao No-Fairness lại utility thấp hơn? Không vô lý sao?**
Đây là discrepancy thật (C6). Trong implementation của em, λ thay đổi candidate score và tương tác với decline=0, nên fairness term không đơn thuần là penalty lấy bớt utility; nó có thể thay đổi throughput và future fleet distribution. Inequality direction đúng như paper, nhưng Utility direction ngược paper. Em mới có plausible mechanisms, chưa coi đó là causal proof.

**Q10. λ=0,8 utility cao hơn λ=0, vậy trade-off ở đâu?**
Empirical λ sweep không đơn điệu. Extreme λ=1 cho fairness gần hoàn hảo nhưng utility sụp, chứng minh có trade-off ở một vùng. Interior λ còn thay đổi assignment dynamics, nên một số điểm cải thiện cả utility và fairness. Em gọi đây là empirical operating-point curve, không giả định một monotonic theoretical frontier.

**Q11. 5 seeds có đủ không?**
5 seed giúp thể hiện variability cho main experiments, không phải large-sample statistical guarantee. Em dùng mean/std và kiểm tra direction nhất quán (slide 15/18); nếu nâng mức publication-grade, em sẽ tăng seed và report confidence interval.

**Q12. Multi-horizon là chạy 11 lần hay một trajectory?**
Một trajectory với checkpoint tại ngày 1,2,3,4,5,6,7,14,21,28,37. Cách này giữ cùng history tới mỗi checkpoint, phù hợp để quan sát cumulative divergence.

**Q13. Có data leakage không?**
Train Q/MLP trên train, main evaluation trên validation, temporal split, test được giữ riêng.

**Q14. 67 zones từ đâu?**
TLC taxi zone ID có sẵn trong parquet đã xử lý. Đây là approximation cho graph nodes của paper, không phải reproduction chính xác spatial clustering gốc.

**Q15. Tại sao 12 mph?**
Đây là giả định đơn giản hóa của simulator để chuyển haversine deadhead distance thành ETA. Không phải road routing thật — em công bố nó như một threat to external validity.

**Q16. Hungarian solver có bắt mọi request phải match không?**
Không. Ma trận được pad dummy rows/columns với decline/stay-idle score 0, nên request/driver có thể unmatched. Pair chỉ thắng decline nếu score có lợi.

**Q17. Test có chứng minh không double booking không?**
Test suite là sanity layer, không phải proof. Em biết hai trace-based test hiện có coverage yếu vì record_trace mặc định False — known issue đã ghi ở slide 10.

**Q18. Mechanism ngày 14–21 là do Q convergence à?**
Em chưa gọi là causal. Biên độ cập nhật Q giảm và policy disagreement tăng cùng giai đoạn, nên đây là correlational support (slide 25). Causal test cần intervention, ví dụ freeze Q tại các checkpoint hoặc inject controlled forecast strength.

**Q19. MLP của em có giống paper không?**
Không thể khẳng định exact vì paper under-specified. MLP của em là một demand-prediction sensitivity experiment với embedding + hour one-hot + 64/32 hidden layer (slide 20), sau đó aggregate/rescale để đi vào cùng score. Em không dùng nó để claim exact MLP reproduction.

**Q20. Strongest result của em là gì?**
Delayed utility effect của look-ahead: gần 0 tới ngày 14, +5,15% ngày 21, +11,65% ngày 28, +20,19% ngày 37, đi cùng policy disagreement chuyển từ ~0,08% early lên ~15% late.

**Q21. Weakest/unresolved result?**
Forecast fairness direction (C4). Full có utility cao hơn nhưng Gini/variance xấu hơn No-Forecast. Đây là claim em chưa reproduce theo đúng hướng paper.

**Q22. Nếu có thêm 1 tuần, em làm gì?**
Ưu tiên: (1) align đúng 2016 data, (2) implement paper scalarisation gần nhất có thể, (3) forecast OD count trực tiếp, (4) controlled ablation (frozen Q tại checkpoint, so sánh assignment decisions with/without fairness term), (5) tăng seed, (6) road-network ETA sensitivity.

**Q23. "6/6 claim đã kiểm thử" nghĩa là gì, khác "6/6 reproduced" thế nào?**
"Đã kiểm thử" nghĩa là mỗi claim đều có một experiment thật, số liệu thật, và một kết luận rõ ràng. "Reproduced" nghĩa là kết quả cùng hướng paper. Trong 6 claim, C1/C2 reproduced, C3 supported có điều kiện, còn C4/C5/C6 cho thấy direction differs hoặc chỉ partial. Nói "6/6 reproduced" sẽ là overclaim.

**Q24. Reproducibility có đảm bảo không, commit nào?**
Git HEAD hiện tại (`3174cefd...`) khác commit ghi trong `dataset_checksums.json` — em đã tự phát hiện gap này. Trước khi nộp cuối em sẽ commit toàn bộ snapshot thật và regenerate mọi artifact từ cùng một commit.

---

## Câu mở đầu 60 giây (đọc gần nguyên văn nếu cần)

"Em được giao replicate xu hướng của paper Long-term Fairness in Ride-Hailing Platform. Vì paper không công bố đủ implementation details, em xác định từ đầu đây là trend replication chứ không phải exact numerical reproduction. Em tách paper thành sáu claim liên quan đến utility–fairness trade-off, baseline superiority, long-horizon behavior, forecast contribution và fairness ablation. Sau đó em xây một simulator độc lập trên NYC TLC thật, dùng cùng joint Hungarian assignment framework cho 5 policy, chạy main experiments trên 5 seed, rồi dùng ablation và multi-horizon tới 37 ngày để kiểm tra từng claim. Kết quả quan trọng nhất là look-ahead tạo utility advantage trễ, đạt khoảng +20% ở ngày 37; tuy nhiên fairness advantage so với no-forecast không xuất hiện. Vì vậy replication của em xác nhận một phần cơ chế dài hạn nhưng không xác nhận toàn bộ fairness claim của paper."

## Câu kết 45 giây

"Kết luận của em không phải paper được reproduce hoàn toàn, cũng không phải project thất bại. Em thấy ba điều. Thứ nhất, fairness-aware scoring tạo một operating point cân bằng tốt hơn các efficiency baseline, dù LAF vẫn là fairness extreme. Thứ hai, look-ahead tạo lợi ích utility rất rõ nhưng chỉ xuất hiện sau một horizon đủ dài, và effect phụ thuộc fleet scarcity. Thứ ba, fairness benefit của forecast không xuất hiện trong implementation này; No-Forecast thực tế có Gini thấp hơn — đây là một trade-off khác paper, không phải lỗi thực nghiệm. Do đó em đánh giá tổng thể đây là Strong Partial Trend Replication. Bước tiếp theo em ưu tiên align scalarisation và forecast target sát paper hơn, rồi chạy controlled ablation để phân biệt effect do forecast, matching dynamics hay fairness objective."

## One-sentence verdict (nếu mentor hỏi thẳng cuối buổi)

"Cả 6 claim của paper đều đã được em kiểm thử bằng experiment thật: balanced utility–fairness behavior và delayed long-horizon utility benefit của look-ahead được reproduce rõ, còn forecast-driven fairness improvement và utility increase khi bỏ fairness cho thấy trade-off/direction khác paper; vì vậy em đánh giá đây là a Strong Partial Trend Replication, không phải full reproduction."
