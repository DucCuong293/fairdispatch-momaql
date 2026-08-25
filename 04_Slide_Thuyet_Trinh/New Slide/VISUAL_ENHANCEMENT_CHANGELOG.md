# Visual Enhancement Changelog — FairDispatch Slide Deck (New Slide/)

Bản gốc `04_Slide_Thuyet_Trinh/index.html` (24 slide, đã chốt) được giữ nguyên làm backup.
Toàn bộ thay đổi trong changelog này chỉ nằm trong `04_Slide_Thuyet_Trinh/New Slide/`.

**Không rerun experiment. Không train model mới. Không đổi simulator/policy/config. Không
thêm/xoá slide. Không đổi flow 6 phần hiện tại.** Slide count: **24 → 24** (không đổi, chỉ bổ
sung chart/KPI/diagram/screenshot ở slide phù hợp).

## Quy trình

1. Audit toàn bộ artifact thật trước khi sửa HTML — xem `VISUAL_DATA_AUDIT.md` (bảng đầy đủ
   nguồn/quyết định dùng hay không dùng từng metric).
2. Tính các số chưa có sẵn dạng summary bằng script READ-ONLY
   `scripts/compute_operational_metrics.py` (chỉ đọc `reports/*.csv`, `final_test/*.csv`,
   `data/*.parquet`, hằng số trong `src/simulator.py` — ghi duy nhất 1 file JSON
   `assets/charts/operational_metrics.json`, không ghi đè bất kỳ artifact gốc nào).
3. Chụp 1 screenshot thật của demo đang chạy (`assets/demo/control_room_live_simulation.png`)
   — xem mục "Screenshot thật" bên dưới.
4. Sửa `index.html` theo nguyên tắc "mất thông tin này có mất insight quan trọng không?" —
   chỉ 13/24 slide được đổi, 11 slide còn lại giữ nguyên vì đã đủ rõ.
5. QA: render toàn bộ 24 slide bằng headless Chromium (Playwright) ở 1600&times;900 (khớp tỉ
   lệ 16:9 của `.stage`), kiểm tra từng slide bằng mắt.

## Slide được bổ sung chart/KPI/diagram (13/24)

| Slide | Thêm gì | Loại | Nguồn số liệu |
|---|---|---|---|
| 1 — Title | 3 KPI nhỏ: 67 vùng, 200 tài xế, ~1,3tr chuyến | KPI number | `dataset_checksums.json`, tự tính tổng 3 split |
| 3 — Bài toán | Sơ đồ khái niệm (Tối ưu lợi nhuận → Driver A/B lệch → khoảng cách thu nhập tăng) | Diagram (minh họa, ghi rõ "không phải số liệu") | — |
| 6 — 5 phần chính | Table chữ &rarr; pipeline diagram 5 bước ngang | Diagram | — |
| 8 — Bộ mô phỏng | 4 KPI lớn (60s/&le;600s/200/67) + mini sequence Request&rarr;Candidate&rarr;Assignment&rarr;Update | KPI + diagram | `src/simulator.py`, `run_final_test_baselines.py` |
| 9 — 5 chiến lược | Trục Gini trung bình thật, xếp đúng thứ tự công bằng | Chart (spectrum, data-driven, không chủ quan) | `r1_validation_results.csv` |
| 12 — Dữ liệu | Thanh timeline tỉ lệ theo ngày, kèm date range thật từng split | Stacked bar / timeline | `data/*.parquet` cột `pickup_ts` |
| 13 — Kết quả 1 | Câu quy đổi P90/P10 income ratio (MOMAQL ~2,3&times; vs Greedy ~21&times;) | Text annotation (không thêm chart mới) | `r1_validation_results.csv` cột p10,p90 |
| 14 — Ablation | Thêm variant No Fairness vào cả 2 mini bar chart (trước chỉ có Full/No Forecast) | Chart (mở rộng chart có sẵn) | `r2_ablation_results.csv` |
| 15 — Long horizon | Vùng tô mờ "khoảng chênh" giữa 2 đường từ ngày 14 | Chart (mở rộng chart có sẵn) | tính lại từ toạ độ đã có |
| 16 — Fleet-scale | Câu giải thích cơ chế: service rate theo fleet size (59,2%&rarr;78,1%&rarr;99,3%) | Text annotation | `fleet_scale_results.csv` cột completed |
| 17 — Kiểm tra Test | Table+bullet &rarr; số lớn 13/13 + 3 category card (Baseline 5/5, Ablation 4/4, Long-horizon 4/4) | KPI + breakdown | `validation_vs_test.csv`, đếm theo nhóm finding |
| 18 — Test ổn định | Thêm dòng Service rate vào bảng; thêm câu Deadhead trung bình | Table row + text | `test_baseline_summary.csv` |
| 19 — Test ablation | Câu "No Forecast fairer ở 5/5 seed" thay vì mô tả chung chung | Text (chính xác hoá, không thêm chart) | `validation_vs_test.csv` finding F7 |
| 20 — Test dài hạn | Table &rarr; grouped bar chart (Ngày 21/37 &times; Validation/Test) | Chart (chuyển từ table) | số đã có, không đổi |
| 21 — Demo | Screenshot THẬT (không mockup) chiếm 55-65% slide, layout 2 cột | Screenshot thật | chụp trực tiếp từ `05_SanPham_Demo` đang chạy |
| 23 — Kết luận | Danh sách &rarr; scoreboard 6 KPI lớn + 1 câu kết + verdict nhỏ (không phải headline) | KPI cards | số đã có, không đổi |

11 slide giữ nguyên (2, 4, 5, 7, 10, 11, 22, 24 và các phần không liệt kê ở trên) vì đã đủ rõ,
thêm visual sẽ không tăng insight (xem lý do từng mục trong `VISUAL_DATA_AUDIT.md`).

## Operational metrics mới tìm được

Xem bảng đầy đủ trong `VISUAL_DATA_AUDIT.md`. Tóm tắt 6 nhóm đã dùng: service rate theo
policy (Validation+Test), avg deadhead cost/chuyến (Test), P10/P50/P90 income &rarr; tỉ lệ
P90/P10 (Validation), 13/13 breakdown theo 3 nhóm, service rate theo fleet size, date range
thật từng split dữ liệu.

4 nhóm cân nhắc nhưng **không đưa vào slide**: demand theo zone (không có chỗ trong storyline
hiện tại), trips/driver (trùng lặp với service rate), candidate depth/feasible driver count và
pickup ETA giây thật (không tồn tại trong artifact hiện có — cần rerun/instrument lại simulator
mới đo được, vi phạm nguyên tắc không rerun), fleet utilization (không có cột nào ghi nhận).

## Screenshot thật

`assets/demo/control_room_live_simulation.png` — chụp bằng Playwright (headless Chromium) sau
khi chạy `05_SanPham_Demo/backend` local (uvicorn, port 8731, engine thật import từ
`src/policies.py`/`src/simulator.py`, không mock), bấm New Run &rarr; Run với cấu hình mặc định
(MOMAQL, 200 driver, Forecast ON), chờ batch chạy thật rồi chụp. Server đã tắt sau khi xong.
Không sửa code sản phẩm, không edit ảnh, không có KPI/label nào bị chỉnh sửa sau khi chụp.

## Chart creation

Không tạo file PNG bằng matplotlib — toàn bộ chart mới dùng **inline SVG/HTML/CSS**, đúng style
đã có sẵn trong `styles.css` (không thêm class CSS mới nào), để nhất quán với các chart cũ
trong deck và không cần quản lý thêm file ảnh. Mọi toạ độ/chiều cao bar đều tính trực tiếp từ
số liệu trong `scripts/compute_operational_metrics.py` hoặc từ CSV gốc — không có số nào gõ
tay không đối chiếu. `assets/charts/operational_metrics.json` là output traceable của script,
giữ lại làm bằng chứng nguồn gốc số liệu.

## Files updated / created

- `New Slide/index.html` — full copy từ bản gốc, sửa 13 slide theo bảng trên.
- `New Slide/speaker_notes.md` — full copy, cập nhật ghi chú cho 9 slide có nội dung mới
  (8, 9, 12, 13, 14, 16, 17, 18, 21).
- `New Slide/FairDispatch_Final_Presentation_Script_With_Heldout_Test.md` — copy nguyên vẹn,
  vẫn đúng với nội dung mới (không có mâu thuẫn), không sửa thêm.
- `New Slide/styles.css`, `New Slide/script.js` — copy nguyên vẹn, không đổi gì (không cần
  class CSS mới, không cần logic mới).
- `New Slide/VISUAL_DATA_AUDIT.md` — tạo mới (audit trước khi sửa).
- `New Slide/VISUAL_ENHANCEMENT_CHANGELOG.md` — file này.
- `New Slide/scripts/compute_operational_metrics.py` — tạo mới, script read-only.
- `New Slide/assets/charts/operational_metrics.json` — output của script trên.
- `New Slide/assets/demo/control_room_live_simulation.png` — screenshot thật.

**Không đổi:** `04_Slide_Thuyet_Trinh/index.html` và các file gốc khác ngoài `New Slide/` —
giữ nguyên làm bản backup theo đúng yêu cầu.

## QA

Không có pipeline export PDF sẵn trong deck này (deck hiển thị 1 slide/lần qua CSS
`display:none`, không có print stylesheet). QA thực hiện tương đương: render từng slide trong
số 24 slide bằng headless Chromium ở đúng tỉ lệ trình chiếu (1600&times;900, khớp 16:9), chụp
ảnh và kiểm tra bằng mắt từng slide: chữ không tràn, chart label đọc được, trục không bị cắt,
không distortion, contrast đủ. Phát hiện 1 lỗi (2 label "REASSIGN"/"Nearest" đè lên nhau ở
slide 9 do 2 điểm Gini quá gần nhau) — đã sửa bằng cách gộp thành 1 nhãn chung, re-render xác
nhận hết lỗi. 0 console error / page error trong toàn bộ 24 lần render.

**PDF QA: PASS** (qua kiểm tra screenshot 16:9, không phải file .pdf thật — xem giải thích
trên).

## Scientific/factual check (grepped sau khi sửa)

Không đổi bất kỳ số liệu đóng băng nào: MOMAQL Validation Utility 1.422.441/Gini 0,2037; Test
1.454.053/0,2011; Full vs No-Forecast +22,4%/+17,1%; Long-horizon Day21 +5,1%/+1,2%, Day37
+20,2%/+13,4%; Fleet 100&rarr;+41,9%/200&rarr;+23,3%/400&rarr;+0,01%; 13/13. Không xuất hiện
"Forecast improves fairness", "MOMAQL tốt nhất mọi metric", hay bất kỳ câu cấm nào khác. Mọi số
liệu mới (service rate, deadhead, P10/P90, date range, fleet service rate) đều trace được về
CSV/parquet/source code thật, liệt kê đầy đủ trong `VISUAL_DATA_AUDIT.md`.
