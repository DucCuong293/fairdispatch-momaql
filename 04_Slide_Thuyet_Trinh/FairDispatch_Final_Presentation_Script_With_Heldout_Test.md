# KỊCH BẢN THUYẾT TRÌNH FAIRDISPATCH — BẢN CÓ HELD-OUT TEST

> Dùng cho deck **32 slide** (`index.html`, đã tích hợp 3 slide Held-out Test; đã bỏ slide
> công thức TD(0) chi tiết, Test Data Quality Gate riêng, Mechanism Probe, Mechanism
> Diagnostics chi tiết, và Validation-vs-Test Summary riêng theo yêu cầu rút gọn deck).
> Khán giả: mentor + người sản phẩm + một số người không chuyên kỹ thuật.
> Nguồn số liệu: `final_test/FINAL_TEST_MENTOR_SUMMARY.md`, `test_claim_assessment.csv`,
> `validation_vs_test.csv` — không có số liệu nào trong file này bị gõ tay từ trí nhớ,
> tất cả đối chiếu lại với 3 file trên.

---

## 0. Giải thích đơn giản các khái niệm (nói khi cần, không phải slide riêng)

- **Utility**: tổng hiệu quả kinh tế / tổng thu nhập hệ thống tạo ra cho tài xế.
- **Fairness**: mức độ công bằng — thu nhập giữa các tài xế có đồng đều không.
- **Gini**: chỉ số đo chênh lệch, **càng thấp càng công bằng** (0 = tuyệt đối đồng đều).
- **Validation**: tập dữ liệu em dùng để phát triển, thử nghiệm, chỉnh cấu hình.
- **Test (held-out)**: tập dữ liệu **tách riêng, khóa lại, không đụng tới** trong suốt quá
  trình phát triển — giống bài thi cuối kỳ, chỉ mở ra kiểm tra một lần sau khi đã học xong,
  không được quay lại "học thêm" theo điểm thi.

---

## 1. Core message (nói ở đầu Phần 4 — Held-out Test Evidence, và nhắc lại ở Kết luận)

> "Em phát triển và tinh chỉnh toàn bộ hệ thống trên tập Validation. Sau khi chốt cấu hình,
> em đóng băng (freeze) toàn bộ — tham số, seed, Q-table — rồi chạy đúng một lần trên tập
> Test, dữ liệu chưa từng được dùng để tuning. Kết quả: 13 trên 13 phát hiện quan trọng đã
> quan sát trên Validation lặp lại đúng hướng trên Test. Điều này cho thấy hành vi của
> implementation ổn định, không phải trùng hợp trên một tập dữ liệu. Nhưng điều này
> **không có nghĩa** toàn bộ 6 claim định tính của paper gốc đều được reproduce — cụ thể,
> C4 (forecast cải thiện fairness dài hạn) vẫn **Not Reproduced**, còn C5 và C6 chỉ
> **Partial**."

**Giải thích "Test giống bài thi cuối":** "Trong lúc phát triển, em chỉ nhìn Validation để
chọn λ, γ, α và kiểm tra ablation. test.parquet bị khóa lại từ đầu. Chỉ sau khi mọi quyết
định đã chốt — kể cả cách xử lý dữ liệu lỗi — em mới mở Test ra chạy một lần, và không quay
lại sửa gì sau khi thấy kết quả. Nếu em tinh chỉnh model theo điểm Test, đó gọi là leakage
— con số sẽ không còn ý nghĩa kiểm định độc lập nữa."

**Giải thích Data Quality Gate (ngắn gọn — không còn slide riêng, nói bằng lời khi trình bày
slide 12 Dataset & Protocol hoặc slide 25 Held-out Baseline):** "test.parquet gốc không bao giờ bị ghi đè. Em
audit thấy 33 trên 195.510 dòng có trường thời lượng chuyến đi bị lỗi ở tầng dữ liệu thô —
32 dòng phục hồi được từ timestamp gốc (pickup/dropoff), 1 dòng không phục hồi được (pickup
trùng dropoff) nên loại. Cộng thêm 3 dòng bị loại vì trùng giây ranh giới với Validation, để
giữ split thời gian nghiêm ngặt. Quy tắc xử lý này được chốt **trước khi** em nhìn bất kỳ kết
quả policy nào trên Test — không phải chỉnh theo outcome. Evaluation view cuối cùng: 195.506
chuyến."

**Giải thích "13/13 generalized" ≠ "6/6 claim reproduced":** "Hai câu này khác nhau hoàn
toàn. '13/13 generalized' là câu mô tả thuần túy: 13 phát hiện tính toán trên Validation có
lặp lại đúng hướng khi chuyển sang Test không — chỉ nói về tính ổn định của implementation.
'6/6 claim reproduced' là câu đánh giá khoa học: kết quả của em có khớp với tuyên bố định
tính của paper gốc không. Hai trục này độc lập. Ví dụ rõ nhất là claim C4 — paper nói
forecast cải thiện fairness dài hạn, nhưng em quan sát ngược lại: No-Forecast công bằng hơn
Full trên cả Validation lẫn Test, 5/5 seed, nhất quán qua ngày 21 và ngày 37. Chính cái
**discrepancy** với paper đó mới là thứ generalize — không phải claim gốc của paper. Nên C4
vẫn được chấm 'Not Reproduced', dù nó nằm trong nhóm 13/13 generalized."

---

## 2. Kịch bản nói theo từng slide (deck 32 slide)

Quy ước: **[Ngắn]** = nói khi trình bày bản 15–20 phút, có thể lướt nhanh 1 câu.
**[Đầy đủ]** = nói khi trình bày bản 25–30 phút, thêm chi tiết/số liệu.

### PHẦN 1 — Problem & Replication Scope (slide 1–7)

**Slide 1 — FairDispatch (title).** "Em trình bày dự án FairDispatch, tái lập xu hướng của
paper *Long-term Fairness in Ride-Hailing Platform* (Kang et al., 2024). Đây là trend
replication, không phải reimplementation chính xác từng con số."

**Slide 2 — Agenda.** "Bài có 6 phần: Bài toán, Phương pháp, Kết quả trên Validation, Bằng
chứng Held-out Test sau khi freeze, Đánh giá tái lập & Kết luận, và Demo sản phẩm."

**Slide 3 — Research Problem.** "Nếu chỉ tối ưu hiệu quả tức thời, chênh lệch thu nhập giữa
tài xế có thể ngày càng lớn theo thời gian. Utility là tổng hiệu quả hệ thống, Fairness là
mức đồng đều giữa các tài xế."

**Slide 4 — Why Look-ahead Matters.** "Điểm đến của chuyến hiện tại quyết định cơ hội thu
nhập ở batch sau — đó là lý do cần nhìn trước (look-ahead) thay vì chỉ nhìn fare hiện tại."

**Slide 5 — Original Paper Claims.** "Paper không công bố đủ chi tiết để tái lập chính xác
số liệu — phần này chỉ liệt kê tuyên bố định tính đã paraphrase."

**Slide 6 — 6 Claim cần đánh giá.** "Em đánh giá theo 6 claim (C1–C6), không đánh giá theo
con số cụ thể của paper. Verdict cuối cùng — cả trên Validation lẫn Test — nằm ở Phần 5."

**Slide 7 — Paper vs Our Implementation.** "Đây là approximation minh bạch — dataset khác
năm (2013 thay vì 2016), forecast dùng tabular Q thay vì MLP 3 lớp, scalarisation đã sửa đổi.
Mọi deviation được công bố trước khi xem kết quả."

### PHẦN 2 — Methodology & Experimental Setup (slide 8–12)

**Slide 8 — Experimental Architecture.** "Mọi policy dùng chung simulator và Hungarian joint
assignment — chỉ khác nhau ở score function."

**Slide 9 — 5 Policy Definitions.** [Đầy đủ] "Greedy theo fare, Nearest theo ETA, LAF theo
thu nhập tích lũy thấp nhất, Exact REASSIGN khớp formulation gốc paper, MOMAQL là policy học
online — chi tiết slide sau."

**Slide 10 — Simulator Invariants & Test Suite.** [Đầy đủ] "20/20 test invariant pass — đây
là sanity layer, không phải formal proof. Em tự công bố hai trace-based test có coverage yếu
do mặc định không ghi trace."

**Slide 11 — MOMAQL Decision Logic.** "Score = hiệu quả tức thời + giá trị vùng tương lai
γ·Q(zone,hour) + điều chỉnh công bằng λ·income gap. λ=0,5, γ=0,9, α=0,1 mặc định. Ablation:
no_forecast ép Q tương lai về 0, no_fairness ép λ về 0 — công thức TD(0) đầy đủ nằm trong mã
nguồn (src/policies.py), không chiếu riêng một slide."

**Slide 12 — Dataset & Protocol.** "Train 912.375 chuyến để học Q. Validation 195.508 chuyến
— nơi em phát triển, so sánh, chốt cấu hình. Test 195.510 chuyến — giữ riêng, chỉ dùng để
kiểm tra cuối cùng." (đọc thêm đoạn "Giải thích Data Quality Gate" ở mục 1 nếu muốn nói ngay
ở đây: raw 195.510 → loại 3 dòng biên thời gian → sửa 32 dòng duration từ timestamp → loại 1
dòng không phục hồi được → 195.506 chuyến evaluation view, checksum không đổi, rule chốt
trước khi nhìn kết quả policy — không có slide riêng cho phần này, nói bằng lời.)

### PHẦN 3 — Experimental Results & Analysis, trên Validation (slide 13–24)

**Slide 13 — Main Baseline Comparison.** "MOMAQL đạt điểm cân bằng mạnh nhất trên Validation
— không phải policy công bằng nhất (đó là LAF), không phải Utility tuyệt đối nhất ở mọi
metric."

**Slide 14 — R1 per-seed summary.** [Đầy đủ, có thể lướt ở bản ngắn] "Kết quả nhất quán qua
5 seed, không phải một seed may mắn."

**Slide 15 — Lambda sweep.** [Đầy đủ] "Quan hệ Utility–Fairness không đơn điệu vì λ ảnh
hưởng cả candidate ordering trong Hungarian assignment, không chỉ trọng số tuyến tính."

**Slide 16 — Ablation (Validation).** "Full đổi một phần Fairness lấy +22,4% Utility so với
No-Forecast. No-Forecast công bằng hơn Full, No-Fairness bất bình đẳng nhất."

**Slide 17 — Ablation per-seed.** [Đầy đủ] "+22,4% và chiều Gini nhất quán 5/5 seed."

**Slide 18 — Variance/CV.** [Đầy đủ, có thể lướt ở bản ngắn] "Paper dùng variance làm fairness
chính — em giữ song song với Gini."

**Slide 19 — MLP benchmark.** [Đầy đủ, có thể lướt ở bản ngắn] "MLP thật vẫn tốt hơn rõ so với
No-Forecast, nhưng tabular Q canonical vẫn tốt hơn MLP trong simulator này."

**Slide 20 — Long-horizon Utility.** "Hiệu ứng look-ahead xuất hiện trễ: gần 0% đến ngày 14,
+20,2% ở ngày 37 trên Validation."

**Slide 21 — Long-horizon Fairness.** "Lợi thế fairness dài hạn của paper không tái lập theo
Gini trên Validation — từ ngày 21, Full có Gini cao hơn (kém công bằng hơn) No-Forecast. Đây
là negative result, giữ nguyên chứ không ép narrative."

**Slide 22 — Full Multi-Horizon Table.** [Đầy đủ, có thể lướt ở bản ngắn] "Bảng đầy đủ 11
checkpoint cho ai cần chi tiết."

**Slide 23 — Fleet Scale.** [Đầy đủ, có thể lướt ở bản ngắn] "Look-ahead có giá trị lớn nhất
khi thiếu cung, gần biến mất khi dư driver."

**Slide 24 — Fleet Scale raw.** [Đầy đủ, có thể lướt ở bản ngắn]

### PHẦN 4 [MỚI] — Held-out Test Evidence, sau khi freeze (slide 25–27)

**Slide 25 — Freeze + Held-out Baseline.** (đọc "Core message" + "Test giống bài thi cuối" +
Data Quality Gate ở mục 1) "MOMAQL Utility trên Test ≈1.454.053, Gini ≈0,2011 — so với
Validation 1.422.441 và 0,2037. Operating point ổn định, không lệch hướng khi sang dữ liệu
chưa từng thấy."

**Slide 26 — Held-out Ablation.** "Full vs No-Forecast: Validation +22,4% Utility, Test
+17,1% — cùng hướng, biên độ nhỏ hơn. No-Forecast vẫn công bằng hơn Full trên cả hai split,
5/5 seed. No-Fairness vẫn làm bất bình đẳng tăng, Utility giảm trên cả hai."

**Slide 27 — Held-out Long-Horizon.** "Ngày 21: Validation +5,1%, Test +1,2%. Ngày 37:
Validation +20,2%, Test +13,4%. Lợi thế Utility dài hạn generalize nhưng yếu hơn trên Test."
(đọc thêm đoạn "13/13 ≠ 6/6" ở mục 1 ngay sau slide này — không có slide riêng cho Validation
vs Test Summary nữa: "13/13 phát hiện tiền xác định generalize đúng hướng sang Test. Không có
nghĩa mọi claim paper được reproduce.")

### PHẦN 5 — Replication Assessment & Conclusion (slide 28–31)

**Slide 28 — Claim-by-Claim (bảng 2 cột).** "Cột 1 là held-out generalization — thuần mô tả.
Cột 2 là paper replication verdict — đánh giá so với paper. C1, C2 Reproduced. C3 Partially
Reproduced, được củng cố thêm bởi Test. C4 Not Reproduced dù discrepancy generalize. C5:
Utility improves, Fairness does not improve — No Forecast fairer. C6: Inequality reproduced,
Utility không reproduce vì bỏ fairness lại làm Utility giảm."

**Slide 29 — Limitations & Conclusion.** "Kết luận tổng thể: **Strong Partial Trend
Replication with held-out temporal support**." (đọc phần Kết luận ở mục 3 dưới)

**Slide 30 — Product Demo (placeholder).** "Phần demo sẽ trình bày riêng, dùng dữ liệu
Validation/demo mặc định — không dùng Test, vì Test chỉ dành cho đánh giá khoa học cuối này."

**Slide 31 — Overall Project Conclusion.** "6/6 claim của paper được kiểm thử; 13/13 phát
hiện xác nhận lại trên held-out Test sau khi freeze."

**Slide 32 — Cảm ơn.**

---

## 3. Đoạn Kết luận (đọc ở slide 29, nhắc lại ở slide 31)

> "Kết luận cuối cùng của em **không phải** 'Full Reproduction', mà là **'Strong Partial
> Trend Replication with held-out temporal support'**.
>
> **Strong** — vì 13/13 phát hiện quan trọng generalize đúng hướng từ Validation sang Test,
> implementation hành xử nhất quán, không phải may rủi một tập dữ liệu.
>
> **Partial** — vì các claim liên quan đến fairness của paper gốc chưa được reproduce đầy
> đủ: C4 Not Reproduced, C5 và C6 chỉ Partial.
>
> **Held-out temporal support** — vì kết luận này không chỉ dựa trên Validation, mà còn được
> xác nhận trên Test, một tập dữ liệu chưa từng dùng để tuning bất cứ thứ gì."

---

## 4. Cụm từ cần nhớ (key phrases)

- "Held-out generalization ≠ paper replication verdict — hai trục độc lập."
- "13/13 generalized directionally" — KHÔNG nói "13/13 claim reproduced".
- "6/6 claim đã được kiểm thử" — KHÔNG nói "6/6 claim reproduced".
- C4: "No Forecast fairer than Full" — KHÔNG nói "Forecast improves fairness".
- C5: "Utility improves; Fairness does not improve (No Forecast is fairer)" — KHÔNG nói "cả
  hai đều improve".
- C6: "Inequality tăng đúng hướng paper; Utility giảm — ngược hướng paper" — KHÔNG nói "No
  Fairness increases Utility".
- MOMAQL: "một balanced operating point, không phải fairness champion" — KHÔNG nói "MOMAQL is
  best on every metric".
- Test.parquet: "không đổi, checksum verify lại mỗi lần" — KHÔNG nói "Test was used for
  tuning".
- "Strong Partial Trend Replication with held-out temporal support" — verdict cuối, dùng
  đúng nguyên văn.

---

## 5. Q&A dự kiến

**Q1. Tại sao cần chạy thêm Test, Validation chưa đủ sao?**
"Validation dùng để phát triển — nếu chỉ báo cáo trên Validation, luôn có rủi ro overfit
cấu hình vào chính tập đó. Test là kiểm định độc lập, chạy một lần sau khi mọi thứ đã khóa."

**Q2. Test có bị dùng để chọn λ hay sửa gì không?**
"Không. Toàn bộ λ/γ/α, Q-table, seed được hash và freeze trước khi Test chạy — xem
`FINAL_TEST_PROTOCOL.md`. Sau khi thấy kết quả Test, em không sửa lại bất kỳ config nào."

**Q3. 33 dòng lỗi dữ liệu có phải em bịa ra để Test đẹp hơn không?**
"Không. Quy tắc xử lý (sửa 32 dòng phục hồi được từ timestamp, loại 1 dòng không phục hồi
được) được viết ra và chốt **trước khi** em chạy bất kỳ policy nào trên Test — audit đầy đủ ở
`DATA_QUALITY_GATE.md`, không nhìn outcome trước khi quyết định rule."

**Q4. Vậy cuối cùng có tái lập được paper không?**
"Có phần, có phần không — không phải nhị phân pass/fail. C1, C2 Reproduced. C3 Partially
Reproduced. C4 Not Reproduced. C5, C6 Partial. Tổng thể: Strong Partial Trend Replication
with held-out temporal support — không phải Full Reproduction."

**Q5. 13/13 generalized nghĩa là gần như tái lập hết rồi, đúng không?**
"Không đúng. 13/13 generalized nghĩa là 13 phát hiện của em trên Validation — kể cả 4 phát
hiện là discrepancy với paper — lặp lại đúng hướng trên Test. Nó chứng minh implementation ổn
định, không chứng minh paper được reproduce. Ví dụ C4 nằm trong 13/13 đó, nhưng vẫn Not
Reproduced vì bản thân claim của paper (forecast cải thiện fairness) sai hướng, cả trên
Validation lẫn Test."

**Q6. Sản phẩm demo có chạy trên Test không?**
"Không. Demo dùng slice Validation/demo mặc định, có giới hạn số request. Test chỉ dành riêng
cho đánh giá khoa học cuối cùng này, không lộ ra trong Control Room tương tác."

**Q7. Nếu có thêm thời gian, em sẽ làm gì?**
"Chạy λ sweep trên Test (hiện chỉ chạy canonical λ=0,5 theo protocol, không sweep để tránh
leakage); tìm causal evidence rõ hơn cho mechanism probe thay vì chỉ correlational; và revisit
Phase 1 MOMAQL sau khi Phase 2 ổn định hoàn toàn."

**Q8. Test suite của simulator có chứng minh không double booking không?**
"Test suite là sanity layer, không phải formal proof. Em tự phát hiện và công bố hai
trace-based test có coverage yếu vì mặc định không ghi trace — known issue ghi rõ ở slide 10
(Simulator Invariants & Test Suite)."

---

## 6. Hai bản trình bày

### Bản ngắn (15–20 phút)

Trình bày slide: **1, 2, 3, 5, 6, 7, 9, 12, 13, 16, 20, 21, 25, 26, 27, 28, 29, 30, 31, 32**.
Lướt nhanh 1 câu ở các slide đánh dấu **[Đầy đủ]** nếu vẫn muốn chiếu qua; có thể bỏ hẳn slide
chi tiết/raw table/appendix (4, 8, 10, 14, 15, 17–19, 22–24) — số liệu vẫn có sẵn trên slide
nếu mentor hỏi sâu, chỉ không chủ động trình bày.

Trọng tâm: Problem (1 câu) → Claim cần đánh giá → Trend replication trên Validation (1–2
slide đại diện) → nói bằng lời Data Quality Gate ở slide 12 → **3 slide Held-out Test
(Baseline/Ablation/Long-Horizon, slide 25–27, kèm caveat 13/13 ≠ 6/6 bằng lời)** → **Claim
Matrix 2 cột (slide 28)** → Kết luận "Strong Partial Trend Replication with held-out temporal
support" → Demo → Cảm ơn.

### Bản đầy đủ (25–30 phút)

Trình bày toàn bộ 32 slide theo thứ tự, dùng đúng nội dung ở mục 2 (cả **[Ngắn]** lẫn
**[Đầy đủ]**). Dành thời gian nhiều hơn cho: slide 10 (known issue của test suite), slide 15
(λ sweep phi tuyến), slide 21 (fairness dài hạn không tái lập), toàn bộ Phần 4 (Held-out Test,
slide 25–27), và slide 28 (claim matrix 2 cột) — đây là 3 điểm mentor hay hỏi sâu nhất.

---

## 7. Nguồn số liệu đã đối chiếu

`final_test/FINAL_TEST_MENTOR_SUMMARY.md`, `final_test/test_claim_assessment.csv`,
`final_test/validation_vs_test.csv`, `04_Slide_Thuyet_Trinh/index.html` (deck 32 slide đã cập
nhật), `04_Slide_Thuyet_Trinh/speaker_notes.md` (bản cũ, đối chiếu C4/C5/C6 wording). Không
số liệu nào trong file này được gõ từ trí nhớ mà không đối chiếu lại nguồn trên. Không có
policy nào được chạy lại để viết kịch bản này.
