# FAIRDISPATCH — FINAL REPORT / TECHDOC / SLIDE UPDATE PROMPTS FOR CLAUDE CODE

## Mục tiêu chung

Dự án FairDispatch đã hoàn thành:

1. Product Demo.
2. Final Held-out Test Evaluation.
3. Data Quality Gate.
4. Claim assessment đã được sửa đúng:
   - `heldout_generalization`
   - `paper_replication_verdict`

Bây giờ Claude Code cần làm vòng cuối:

```text
Research Report
→ Technical Documentation
→ Slide Deck
→ Speaker Notes / Presentation Script
→ Final Consistency Audit
```

Không chạy thêm experiment.

Không thay đổi số liệu raw.

Không sửa policy / simulator / model / hyperparameter.

Không rerun Final Test trừ khi chỉ đọc file để verify.

---

# SOURCE OF TRUTH

Claude phải lấy số liệu từ artifact thật trong project, ưu tiên:

```text
final_test/
├── FINAL_TEST_PROTOCOL.md
├── DATA_QUALITY_GATE.md
├── FINAL_TEST_MENTOR_SUMMARY.md
├── test_quality_transform_manifest.json
├── validation_vs_test.csv
├── test_claim_assessment.csv
├── baseline/
├── ablation/
├── long_horizon/
├── figures/
└── logs/
```

và các validation artifact gốc hiện có trong repository.

Chat summary chỉ dùng làm định hướng, không phải source duy nhất.

---

# PATH RESOLUTION

Trước khi sửa tài liệu, Claude phải search trong:

```text
D:\ProjectVSF
```

và xác minh đúng project root.

Tên project có thể là một trong các dạng:

```text
FairDispatch_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication
FairDispatch_v3_MOMAQL_Fair_Ride_Hailing_Dispatch_Replication
```

Không ghi nhầm sang folder khác.

Cần tìm các folder:

```text
03_Source_Code_Va_Ket_Qua
04_Slide_Thuyet_Trinh
docs
docs/docx_report
docs/techdoc
final_test
```

Nếu có nhiều bản, ưu tiên bản chứa `final_test` mới nhất và Product Demo mới nhất.

---

# PROMPT 1 — UPDATE RESEARCH REPORT

Gửi prompt này cho Claude Code trước.

```text
Bạn là Senior Research Writer + Research Reproducibility Reviewer.

Nhiệm vụ: cập nhật Research Report của FairDispatch sau Final Held-out Test Evaluation.

KHÔNG chạy lại experiment.
KHÔNG thay đổi số liệu raw.
KHÔNG sửa policy/simulator/model.
Chỉ đọc artifact và cập nhật báo cáo.

==================================================
1. RESOLVE PROJECT PATH
==================================================

Search trong D:\ProjectVSF để tìm đúng project root chứa:

- 03_Source_Code_Va_Ket_Qua
- final_test
- report/docx source hiện tại
- docs/docx_report nếu có

Không ghi nhầm sang project clone khác.

==================================================
2. READ SOURCE OF TRUTH
==================================================

Đọc kỹ:

final_test/FINAL_TEST_PROTOCOL.md
final_test/DATA_QUALITY_GATE.md
final_test/FINAL_TEST_MENTOR_SUMMARY.md
final_test/test_quality_transform_manifest.json
final_test/validation_vs_test.csv
final_test/test_claim_assessment.csv
final_test/baseline/test_baseline_summary.csv
final_test/ablation/test_ablation_summary.csv
final_test/long_horizon/test_long_horizon.csv

Đọc thêm validation artifacts đang được report dùng hiện tại.

Nếu report có script build docx/pdf/html thì dùng pipeline hiện có.
Nếu report là docx thủ công, chỉnh nội dung bằng cách an toàn nhất và tạo bản output mới.

==================================================
3. UPDATE RESEARCH STORY
==================================================

Báo cáo cuối phải đổi story từ:

"Validation-only replication"

thành:

"Validation-developed trend replication with held-out temporal test support."

Nhưng vẫn giữ trung thực:

- Đây là trend replication.
- Không phải exact paper reproduction.
- Dataset là NYC TLC 2013, không phải exact paper data.
- Implementation reconstructed.
- Một số paper claims không reproduced.

==================================================
4. ADD / UPDATE SECTION: FINAL HELD-OUT TEST EVALUATION
==================================================

Thêm section lớn:

Final Held-out Test Evaluation

Subsections:

4.1 Purpose
- Test dùng để verify, không dùng để tune.
- Configuration frozen trước khi nhìn Test policy outcomes.

4.2 Test Data Quality Gate
Ghi ngắn gọn:

Raw Test:
195,510 rows

Temporal boundary exclusion:
3 rows

Duration quality:
32 rows repaired from timestamps
1 invalid zero trip excluded

Final evaluated:
195,506 rows

Raw test.parquet checksum unchanged.

Giải thích:
- duration_seconds là derived field bị corrupt.
- timestamps hợp lệ được dùng để repair 32 rows.
- raw data immutable.
- rule được áp dụng trước khi nhìn policy outcome.

4.3 Frozen Protocol
Include:
- MOMAQL λ = 0.5
- γ = 0.9
- α = 0.1
- 200 drivers
- Hungarian joint assignment
- Q-table file/hash
- seeds [20260721..20260725]
- no-test-tuning rule

Nếu artifact cho con số khác, dùng artifact làm source of truth.

4.4 Held-out Baseline Results
Report:
- 5 policies × 5 seeds
- Utility ranking Test giống Validation:
  MOMAQL > Greedy > Nearest > LAF > Exact REASSIGN
- MOMAQL Test Utility ≈ 1,454,053
- MOMAQL Test Gini ≈ 0.2011
- Compare to Validation:
  Utility ≈ 1,422,441
  Gini ≈ 0.2037

Interpret:
MOMAQL operating point stable across temporal periods.

4.5 Held-out Ablation Results
Report:
Full vs No Forecast:
- Test Utility gain +17.1%
- Validation Utility gain +22.4%
- 5/5 seeds same direction
- effect weaker but same direction

Fairness:
- No Forecast fairer than Full on both Validation and Test
- Test paired ΔGini ≈ -0.0427
- 5/5 seeds same direction

No Fairness:
- inequality increases strongly
- Utility decreases on both Validation and Test

4.6 Held-out Long-Horizon Results
Report:
Test span supports Day 37.

Utility gain:
Day 21:
Validation +5.1%
Test +1.2%

Day 37:
Validation +20.2%
Test +13.4%

Interpret:
Delayed Utility benefit generalizes but weaker on Test.

Fairness:
No Forecast remains fairer at Day 37 on both splits.

4.7 Validation vs Test Generalization
Report:
13/13 pre-specified Validation findings generalized directionally to Test.

But explicitly state:

Held-out generalization does NOT mean all paper claims are reproduced.

==================================================
5. UPDATE CLAIM MATRIX
==================================================

Use final corrected assessment:

C1:
Held-out generalization: Generalized
Paper replication verdict: Reproduced

C2:
Held-out generalization: Generalized
Paper replication verdict: Reproduced within adapted-baseline scope

C3:
Held-out generalization: Generalized
Paper replication verdict: Partially Reproduced / strengthened by held-out support

C4:
Held-out generalization: Generalized — discrepancy generalizes
Paper replication verdict: Not Reproduced

C5:
Held-out generalization: Generalized — same mixed pattern
Paper replication verdict: Partially Reproduced
Utility ✓
Fairness ✗

C6:
Held-out generalization: Generalized — same mixed pattern
Paper replication verdict: Partially Reproduced
Inequality ✓
Utility ✗

Do NOT write "6/6 paper claims reproduced."

==================================================
6. UPDATE DISCUSSION
==================================================

Discussion must emphasize:

A. Stronger evidence:
- MOMAQL operating point stable on Test.
- Forecast Utility benefit generalizes.
- Delayed long-horizon Utility effect generalizes.
- Validation observations are not one-period artifacts.

B. Robust negative results:
- Forecast did not improve fairness.
- No Forecast was fairer than Full on both Validation and Test.
- Removing fairness increased inequality but lowered Utility on both Validation and Test.

C. Interpretation:
- Some paper mechanisms are robust in reconstructed implementation.
- Some paper claims are sensitive to implementation/scalarisation/data/dynamics.
- This is valuable partial replication, not failure.

==================================================
7. UPDATE FINAL CONCLUSION
==================================================

Final verdict must be:

"Strong Partial Trend Replication with held-out temporal support."

Recommended conclusion text:

"After freezing the implementation and configuration, the held-out temporal Test evaluation confirmed all 13 pre-specified Validation findings directionally. This strengthens confidence that the observed behavior of the reconstructed implementation is temporally robust. However, the held-out results also confirm that not all qualitative claims from the original paper are reproduced: forecast-driven Utility gains persist, but forecast-driven Fairness improvement remains not reproduced. Therefore, the final verdict is Strong Partial Trend Replication with held-out temporal support."

Rewrite naturally in report style.

==================================================
8. FIGURES / TABLES TO INCLUDE
==================================================

Add or update figures/tables from final_test/figures if available:

- Test baseline Utility–Gini
- Validation vs Test core results
- Test ablation
- Long-horizon Validation vs Test if available
- Final claim matrix

Do not overload report with too many charts.

Detailed raw tables can go appendix.

==================================================
9. OUTPUT
==================================================

Write updated Research Report into the existing report output directory.

If current report is DOCX, create versioned output:

FairDispatch_Research_Report_Final_With_Heldout_Test.docx

If there is Markdown/HTML/PDF source, update source as well.

Also create/update:

REPORT_UPDATE_CHANGELOG.md

Changelog should list:
- sections updated
- figures added
- key result numbers
- files read
- no experiment rerun

==================================================
10. FINAL RESPONSE
==================================================

Return:

Files updated:
- ...

Key report changes:
- ...

Final verdict:
- ...

Checks:
- raw numbers source
- no rerun
- claim matrix corrected
```

---

# PROMPT 2 — UPDATE TECHNICAL DOCUMENTATION

Gửi prompt này sau khi Research Report xong.

```text
Bạn là Senior Technical Writer + Reproducibility Engineer.

Nhiệm vụ: cập nhật TechDoc của FairDispatch sau Final Held-out Test Evaluation.

KHÔNG rewrite report prose.
KHÔNG chạy lại experiment.
KHÔNG thay đổi raw data/result.

TechDoc phải giải thích đủ để mentor hoặc engineer khác tái hiện Final Test.

==================================================
1. RESOLVE AND READ
==================================================

Tìm đúng project root và đọc:

final_test/FINAL_TEST_PROTOCOL.md
final_test/DATA_QUALITY_GATE.md
final_test/test_quality_transform_manifest.json
final_test/logs/commands.log
final_test/logs/environment.txt
final_test/logs/runtimes.csv
final_test/FINAL_TEST_MENTOR_SUMMARY.md

Đọc scripts/final_test nếu có.

Đọc TechDoc hiện tại trong docs/techdoc hoặc location tương đương.

==================================================
2. ADD SECTION: FINAL TEST PROTOCOL
==================================================

Document:

- purpose
- frozen configuration
- exact seed list
- dataset paths
- checksums
- Q-table hash
- source hashes
- simulator/policy files
- no-test-tuning rule

==================================================
3. ADD SECTION: DATA QUALITY TRANSFORM
==================================================

Explain exactly:

Raw test.parquet immutable.

Evaluation transform:

A. Strict temporal boundary:
- exclude 3 rows at validation/test boundary second
- reason: enforce max(val_ts) < min(test_ts)

B. Duration repair/exclusion:
- if stored duration valid: keep
- if stored invalid but timestamp-derived duration valid: repair `duration_seconds_eval`
- if both invalid: exclude
- 32 repaired
- 1 excluded
- final evaluated rows 195,506

Document:
- raw checksum unchanged
- transform manifest path
- no policy outcome inspected before rule

==================================================
4. ADD SECTION: FINAL TEST COMMANDS
==================================================

From commands.log, include:

- audit command
- baseline command
- ablation command
- long-horizon command
- summary command
- test command

If commands.log missing detail, reconstruct from scripts but label as reconstructed.

==================================================
5. ADD SECTION: ARTIFACT MAP
==================================================

List outputs:

final_test/
- protocol
- data-quality files
- baseline per-seed/summary
- ablation per-seed/summary
- long-horizon
- validation_vs_test
- test_claim_assessment
- mentor summary
- figures
- logs

For each, write one sentence explaining purpose.

==================================================
6. ADD SECTION: METRIC DEFINITIONS
==================================================

Ensure definitions:

- Total Utility
- Gini
- Variance
- Std
- Served Requests
- Average Deadhead
- Paired deltas
- Directional generalization
- Paper replication verdict

Clarify:

Fairness is concept.
Gini/Variance are metrics.
Lower Gini/Variance = more equal.

==================================================
7. ADD SECTION: REPRODUCIBILITY LIMITATIONS
==================================================

Include:

- NYC TLC 2013, not exact paper dataset.
- reconstructed implementation.
- 5 seeds only.
- no formal statistical significance claim.
- no λ sweep on Test.
- Test used only after freeze.
- product demo remains validation/demo slice, not test.

==================================================
8. UPDATE EXISTING TECHDOC SECTIONS
==================================================

If TechDoc currently says Test unused, update it.

If TechDoc currently says only Validation, update:

Train:
training/Q

Validation:
development/analysis

Test:
final held-out verification

==================================================
9. OUTPUT
==================================================

Save updated TechDoc in existing techdoc output directory.

If current format is DOCX:
FairDispatch_TechDoc_Final_With_Heldout_Test.docx

If Markdown source exists, update it too.

Create/update:
TECHDOC_UPDATE_CHANGELOG.md

==================================================
10. FINAL RESPONSE
==================================================

Return:

TechDoc updated:
- ...

New reproducibility sections:
- ...

Artifact map:
- ...

Commands verified:
- ...

No rerun:
- yes/no
```

---

# PROMPT 3 — RESTRUCTURE AND UPDATE SLIDES

Gửi prompt này sau Research Report và TechDoc đã cập nhật.

```text
Bạn là Research Presentation Designer + Technical Storytelling Reviewer.

Nhiệm vụ: cập nhật và sắp xếp lại slide deck FairDispatch sau khi đã có Final Held-out Test Evaluation.

Yêu cầu quan trọng:
- Slide phải đơn giản, dễ hiểu, không màu mè phức tạp.
- Font Arial hoặc system sans-serif dễ đọc.
- Không dashboard hóa slide.
- Không nhồi quá nhiều bảng.
- Dùng câu chuyện nghiên cứu rõ ràng.
- Phải sắp xếp lại slide để kết quả Test mới xuất hiện đúng vị trí trong storyline.
- Không chỉ append thêm vài slide Test vào cuối một cách cơ học.

==================================================
1. RESOLVE CURRENT SLIDE LOCATION
==================================================

Tìm slide hiện tại trong project, ví dụ:

04_Slide_Thuyet_Trinh
04_Slide_Thuyet_Trinh/index.html
hoặc file HTML/PPT tương đương.

Backup bản cũ trước khi sửa.

Đọc toàn bộ slide hiện tại và speaker notes nếu có.

Đọc:
- final_test/FINAL_TEST_MENTOR_SUMMARY.md
- final_test/validation_vs_test.csv
- final_test/test_claim_assessment.csv
- updated Research Report
- updated TechDoc nếu cần

==================================================
2. NEW STORYLINE
==================================================

Storyline mới:

A. Problem
Ride-hailing dispatch can maximize system utility while creating driver income inequality.

B. Paper claim / replication target
We replicate qualitative trends, not exact numbers.

C. Reconstructed implementation
NYC TLC 2013, 67 zones, 200 drivers, Hungarian assignment, MOMAQL score.

D. Validation evidence
Used for development and analysis:
- baseline
- ablation
- long horizon
- discrepancy

E. Freeze before Test
Protocol, config, seeds, data quality gate.

F. Held-out Test evidence
13/13 pre-specified findings generalize directionally.

G. Final claim assessment
Robust implementation behavior does not mean all paper claims reproduced.

H. Product demo
Decision-support Control Room, not production Grab clone.

I. Conclusion
Strong Partial Trend Replication with held-out temporal support.

==================================================
3. TARGET SLIDE COUNT
==================================================

Aim for 28–32 slides max.

Do not expand to 40+.

Keep backup appendix if needed.

Suggested structure:

1. Title
2. Agenda
3. Problem: efficiency-only dispatch creates income inequality
4. Why look-ahead matters
5. Paper qualitative claims
6. Replication scope and deviations
7. Train / Validation / Test protocol
8. System architecture / simulator
9. Policies compared
10. MOMAQL decision logic
11. Metrics: Utility, Gini, Variance
12. Validation baseline: MOMAQL operating point
13. Validation ablation: Full vs No Forecast vs No Fairness
14. Validation long horizon: delayed Utility benefit
15. Why Test matters / freeze protocol
16. Test data quality gate
17. Held-out Test baseline: operating point stable
18. Held-out Test ablation: +17.1% Utility, NF fairer
19. Held-out Test long horizon: Day 37 +13.4%
20. Validation vs Test: 13/13 findings generalized
21. Final claim matrix: held-out generalization vs paper replication
22. What this means scientifically
23. Product Demo: Control Room purpose
24. Product Demo: live map + continuous playback
25. Product Demo: Why this driver + fairness/service controls
26. Limitations
27. Final conclusion
28. Q&A

If current deck has important mechanism/sensitivity slides:
- move detailed mechanism probes to appendix;
- do not keep them in main flow unless slide count allows.

==================================================
4. SLIDE-SPECIFIC CONTENT
==================================================

Slide "Train / Validation / Test protocol":
Show:
Train → learn Q/forecast
Validation → development/analysis/freeze
Test → final held-out verification

Slide "Test Data Quality Gate":
Very brief:
Raw Test: 195,510
Boundary excluded: 3
Duration repaired: 32
Invalid zero trip excluded: 1
Final evaluated: 195,506
Raw checksum unchanged
No policy outcome inspected before rule

Slide "Held-out Test baseline":
Show:
MOMAQL Test Utility 1,454,053
MOMAQL Test Gini 0.2011
Validation Utility 1,422,441
Validation Gini 0.2037
Interpretation:
Operating point stable.

Slide "Held-out Test ablation":
Show:
Full vs No Forecast Utility:
Val +22.4%
Test +17.1%

Fairness:
No Forecast fairer on both.

No Fairness:
Inequality up, Utility down on both.

Slide "Held-out Test long horizon":
Show:
Day 21:
Val +5.1%
Test +1.2%

Day 37:
Val +20.2%
Test +13.4%

Interpret:
Delayed Utility benefit generalizes, weaker on Test.

Slide "Validation vs Test":
Headline:
13/13 pre-specified findings generalized directionally.

But add:
This validates robustness of observed behavior, not full paper reproduction.

Slide "Final Claim Matrix":
Use table:

Claim | Held-out Test | Paper Replication

C1 | Generalized | Reproduced
C2 | Generalized | Reproduced within adapted-baseline scope
C3 | Generalized | Partial / strengthened
C4 | Generalized discrepancy | Not Reproduced
C5 | Generalized mixed pattern | Partial: Utility ✓ / Fairness ✗
C6 | Generalized mixed pattern | Partial: Inequality ✓ / Utility ✗

Do NOT write 6/6 paper claims reproduced.

==================================================
5. DESIGN GUIDELINES
==================================================

Use simple visual style:
- white / light background
- dark readable text
- 1 primary blue/navy
- 1 accent color for warning/negative findings
- Arial font
- large titles
- few bullets
- avoid dense tables
- avoid excessive icons
- avoid colorful gradients

Slide should be easy for both technical and non-technical audience.

==================================================
6. CHARTS
==================================================

Use existing final_test/figures where helpful.

But do not overload slides.

Main deck only needs:
- Utility-Gini baseline plot
- Ablation comparison
- Long-horizon line chart
- Claim matrix table

Detailed raw tables can move to appendix.

==================================================
7. PRODUCT DEMO SLIDES
==================================================

Product demo slides should not dominate research story.

Keep 2–3 slides:
- product positioning
- live control room screenshot / description
- demo flow

Position Product Demo after final scientific result.

Reason:
Research verdict first, product demo second.

==================================================
8. SPEAKER NOTES
==================================================

Update speaker notes if current deck has notes.

Notes must include:
- clear explanation that Test generalizes observed findings;
- clear warning that this does not mean all paper claims reproduced;
- simple explanation of Data Quality Gate;
- how to explain C4/C5/C6 honestly.

==================================================
9. OUTPUT
==================================================

Update slide source in existing slide folder.

If deck is HTML:
- update index.html and assets.
- keep backup of old index.html.

If deck is PPTX:
- output final PPTX.

Create:
SLIDE_UPDATE_CHANGELOG.md

Changelog:
- slides added
- slides removed/moved
- new Test slides
- appendix changes
- key numbers included

==================================================
10. FINAL RESPONSE
==================================================

Return:

Slide deck updated:
- ...

New structure:
- ...

Slides moved/removed:
- ...

Final Test slides:
- ...

Speaker notes:
- ...

Known limitations:
- ...
```

---

# PROMPT 4 — UPDATE SPEAKER SCRIPT / THUYẾT TRÌNH SCRIPT

Gửi prompt này sau khi slide xong.

```text
Bạn là presentation coach cho FairDispatch.

Nhiệm vụ: cập nhật kịch bản nói theo slide deck mới có Held-out Test Evaluation.

Đối tượng nghe:
- mentor nghiên cứu;
- người làm app/product;
- một số người không chuyên sâu thuật toán.

Style:
- tiếng Việt tự nhiên;
- dễ hiểu;
- không đọc nguyên chữ trên slide;
- giải thích thuật ngữ đơn giản;
- trung thực với kết quả;
- nhấn đúng điểm mạnh và negative result.

==================================================
1. READ
==================================================

Đọc slide deck mới nhất.

Đọc:
final_test/FINAL_TEST_MENTOR_SUMMARY.md
test_claim_assessment.csv
validation_vs_test.csv

Nếu có kịch bản cũ, update thay vì rewrite từ zero nếu hợp lý.

==================================================
2. UPDATE CORE MESSAGE
==================================================

Kịch bản mới phải nói được:

"Ban đầu em phát triển và phân tích trên Validation. Sau khi freeze implementation và config, em chạy held-out Test. 13/13 finding giữ cùng direction, nên behavior của reconstructed implementation khá robust. Nhưng điều đó không có nghĩa paper được reproduce hoàn toàn. C4 không reproduced; C5/C6 partial."

==================================================
3. ADD TEST EXPLANATION
==================================================

Giải thích Test ngắn:

"Test giống bài thi cuối. Em không dùng Test để chọn λ hay sửa model. Test chỉ dùng sau khi freeze để xem kết luận có generalize không."

Data Quality Gate nói ngắn:

"Trước khi chạy policy, em phát hiện một số lỗi duration từ raw data. Raw file không bị sửa; evaluation view repair 32 derived duration fields từ timestamp, loại 1 record không thể cứu, và loại 3 boundary rows để đảm bảo temporal split strict."

Không nói quá dài.

==================================================
4. UPDATE CLAIM EXPLANATION
==================================================

Phải có đoạn giải thích rất rõ:

"13/13 findings generalized" nghĩa là:
- các pattern quan sát ở Validation lặp lại ở Test.

Không có nghĩa:
- 6/6 claims của paper được reproduce.

Ví dụ:
C4 paper kỳ vọng forecast cải thiện fairness, nhưng cả Validation và Test đều cho No Forecast fairer. Vậy discrepancy mới là thứ generalize.

==================================================
5. FINAL CLOSING
==================================================

Closing nên là:

"Vì vậy verdict cuối của em không phải Full Reproduction, mà là Strong Partial Trend Replication with held-out temporal support."

Sau đó giải thích:
Strong vì:
- 13/13 findings generalize trên Test.

Partial vì:
- fairness-related paper claims không reproduce đầy đủ.

Held-out temporal support vì:
- Test là temporal split chưa dùng để tune.

==================================================
6. OUTPUT
==================================================

Create:

FairDispatch_Final_Presentation_Script_With_Heldout_Test.md

Include:
- slide-by-slide script
- key phrases to remember
- Q&A likely questions
- short 15–20 minute version
- full 25–30 minute version
- explanation of Gini/Fairness/Utility/Test

==================================================
7. FINAL RESPONSE
==================================================

Return file path and summary.
```

---

# PROMPT 5 — FINAL CONSISTENCY AUDIT

Gửi prompt này cuối cùng sau khi report, techdoc, slide, script đều đã cập nhật.

```text
Bạn là Final QA Reviewer cho dự án FairDispatch.

Nhiệm vụ: audit consistency giữa:

- Research Report
- TechDoc
- Slide Deck
- Speaker Script
- final_test artifacts

Không sửa số liệu.
Chỉ sửa text nếu phát hiện inconsistency rõ.

==================================================
1. CHECK KEY NUMBERS
==================================================

Verify all documents use same values:

Raw Test rows: 195,510
Final evaluated Test rows: 195,506
Duration repaired: 32
Invalid duration excluded: 1
Boundary excluded: 3

MOMAQL Validation:
Utility 1,422,441
Gini 0.2037

MOMAQL Test:
Utility 1,454,053
Gini 0.2011

Full vs No Forecast:
Validation +22.4%
Test +17.1%

Long Horizon:
Day 21 Val +5.1%, Test +1.2%
Day 37 Val +20.2%, Test +13.4%

13/13 findings generalized.

Final verdict:
Strong Partial Trend Replication with held-out temporal support.

==================================================
2. CHECK CLAIM WORDING
==================================================

No document may say:

- "6/6 paper claims reproduced"
- "Forecast improves fairness"
- "Full is fairer than No Forecast"
- "Test was used for tuning"
- "This is exact reproduction"
- "MOMAQL is best on every metric"
- "No Fairness increases Utility"

Correct wording:

- C4 Not Reproduced
- C5 Partial: Utility yes, Fairness no
- C6 Partial: Inequality yes, Utility no
- MOMAQL is a balanced operating point, not fairness champion
- LAF can be fairer but lower Utility

==================================================
3. CHECK LIVE DEMO VS TEST
==================================================

Product demo should not claim it runs Test by default.

Correct:
Product Live Demo uses validation/demo slice.

Test is final scientific evaluation.

==================================================
4. CHECK DATA QUALITY
==================================================

All docs must say:
- raw test.parquet unchanged;
- derived duration repaired for 32;
- 1 invalid zero trip excluded;
- 3 boundary rows excluded;
- transform defined before policy outcomes.

==================================================
5. OUTPUT
==================================================

Create:

FINAL_PROJECT_CONSISTENCY_AUDIT.md

Include:
- checked files
- inconsistencies found
- fixes applied
- remaining caveats
- final go/no-go

Return concise summary.
```

---

# RECOMMENDED ORDER TO SEND TO CLAUDE

```text
1. Research Report prompt
2. TechDoc prompt
3. Slide prompt
4. Speaker Script prompt
5. Final Consistency Audit prompt
```

Không làm slide trước report, vì slide nên đi theo conclusion cuối của report.

Không sửa speaker script trước slide, vì script phải bám slide mới.

Không audit trước khi cả 4 thứ xong.
