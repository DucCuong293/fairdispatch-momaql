# Visual Data Audit — FairDispatch Slide Deck (24 slide, "New Slide")

Audit thực hiện trước khi sửa `index.html`. Không rerun experiment, không train model
mới, không đổi simulator/policy/config. Toàn bộ số liệu dưới đây trace được về file thật
trong repo. Số liệu chưa có sẵn dạng summary nhưng dữ liệu raw đủ để tính (read-only
aggregate: groupby/mean/percentile) được tính bằng
`scripts/compute_operational_metrics.py` (script chỉ ĐỌC, không ghi vào bất kỳ artifact
gốc nào — chỉ ghi ra `assets/charts/operational_metrics.json`).

## Nguồn đã đọc

`03_Source_Code_Va_Ket_Qua/reports/` (r1_validation_results.csv, r2_ablation_results.csv,
r2_ablation_raw.csv, multi_horizon_results.csv, fleet_scale_results.csv,
dataset_checksums.json), `03_Source_Code_Va_Ket_Qua/final_test/` (baseline/, ablation/,
long_horizon/, validation_vs_test.csv, test_dataset_audit.json, DATA_QUALITY_GATE.md),
`03_Source_Code_Va_Ket_Qua/src/` (simulator.py, policies.py — hằng số cấu hình),
`03_Source_Code_Va_Ket_Qua/scripts/final_test/run_final_test_baselines.py`,
`03_Source_Code_Va_Ket_Qua/run_complete_verifications.py` (nguồn sinh fleet-scale),
`05_SanPham_Demo/` (backend + frontend — chạy local thật để chụp screenshot),
`D:\ProjectVSF\fairdispatch_v3_clean\data\*.parquet` (đọc read-only qua pandas để lấy
date range từng split).

## Bảng audit

| Metric / Figure | Source file | Dùng trong slide? | Slide số | Tại sao quan trọng |
|---|---|---|---|---|
| 67 zone TLC | docs/techdoc, docs/docx_report (đã dẫn nhiều nơi), xác nhận số zone chuẩn của project | Có | 1, 8 | Cho biết quy mô không gian mô phỏng, khán giả cần biết "không phải toàn NYC" |
| 200 driver canonical | `scripts/final_test/run_final_test_baselines.py` (N_DRIVERS=200) | Có | 1, 8 | Quy mô fleet chuẩn dùng cho mọi kết quả headline |
| Batch window 60s | `src/simulator.py` (`window_seconds: float = 60.0`) | Có | 8 | Đã có trong bullet, nay thêm thành KPI number lớn |
| Max pickup ETA 600s | `src/simulator.py` (`MAX_PICKUP_ETA_SECONDS = 600.0`) | Có | 8 | Đã có trong bullet, nay thêm thành KPI number lớn |
| Tổng chuyến Train+Val+Test = 1.303.393 | tự tính: 912.375+195.508+195.510 (đã verify từng số ở `test_dataset_audit.json`) | Có | 1 | Cho biết quy mô dữ liệu ngay từ đầu, tránh nghe "chỉ vài nghìn dòng" |
| Date range Train/Val/Test (2013-01-01→06-13 / 06-13→07-21 / 07-21→08-31) | `data/*.parquet` cột `pickup_ts`, đọc bằng pandas (read-only) | Có | 12 | Chứng minh split THEO THỜI GIAN thật, không random — cốt lõi của "kiểm tra nghiêm túc" |
| Service rate theo policy (Validation, 5 seed mean) | `reports/r1_validation_results.csv` cột `completed_trips`, tự tính `/195.508` | Có | 13 (note), 18 | MOMAQL phục vụ 77,9%–79,7% cầu — cao hơn hẳn 4 baseline còn lại; chứng minh Utility gain KHÔNG đến từ bỏ khách |
| Service rate theo policy (Test) | `final_test/baseline/test_baseline_summary.csv` cột `served_mean` | Có | 18 | Bản Test của cùng insight trên, để trong bảng ổn định Validation-vs-Test có sẵn |
| Avg deadhead cost/chuyến theo policy (Test, $) | `final_test/baseline/test_baseline_summary.csv` cột `avg_deadhead_mean` | Có | 18 | MOMAQL ($0,60) gần bằng REASSIGN thuần hiệu quả ($0,60), thấp hơn Greedy/LAF — chứng minh không lãng phí deadhead để đạt cân bằng |
| P10/P50/P90 thu nhập theo policy (Validation) | `reports/r1_validation_results.csv` cột `p10,p50,p90`, tự tính mean 5 seed | Có (rút gọn thành 1 tỷ lệ) | 13 (note) | Dịch Gini trừu tượng thành số cụ thể: P90/P10 MOMAQL ≈2,3 lần so với Greedy ≈21 lần |
| 13/13 phân theo 3 nhóm (Baseline 5/5, Ablation 4/4, Long-horizon 4/4) | `final_test/validation_vs_test.csv` (đếm trực tiếp `finding_id` theo nhóm F1–F5/F6–F9/F10–F11, cột `generalized`) | Có | 17 | Con số "13/13" hiện tại không nói RÕ 13 là gồm những gì — breakdown cho thấy đều generalize ở mọi nhóm, không phải trung bình che giấu 1 nhóm yếu |
| No-Forecast fairer 5/5 seed cả 2 split | `final_test/validation_vs_test.csv` finding F7 (`notes`: "paired sign consistency val=5/5, test=5/5") | Có | 19 | Thay số Gini trừu tượng bằng phát biểu "đúng 5/5 seed" — dễ hiểu, đủ mạnh, không cần thêm chart |
| Fleet-scale: service rate theo n_drivers (Full) | `reports/fleet_scale_results.csv` cột `completed`, tự tính `/195.508` | Có (1 dòng caption) | 16 | Giải thích CƠ CHẾ vì sao lợi ích forecast biến mất ở 400 driver: service rate đã bão hòa 99,3% dù có forecast hay không — fleet đã đủ, forecast hết chỗ phát huy |
| 3 variant ablation (Full/No Forecast/No Fairness) Utility + Gini (Validation) | `reports/r2_ablation_results.csv` | Có (đã có Full/No-Forecast, bổ sung No-Fairness) | 14 | Slide cũ thiếu hẳn No-Fairness — đây là 1/3 câu chuyện ablation, bỏ sót là mất insight lớn |
| Trục Gini trung bình 5 chiến lược (Validation) | `reports/r1_validation_results.csv`, tự tính mean gini theo policy | Có | 9 | Thay vì đặt vị trí chủ quan trên trục "efficiency↔fairness", dùng đúng số Gini thật để xếp thứ tự — không suy diễn |
| Screenshot Control Room thật, đang chạy | Chụp trực tiếp từ `05_SanPham_Demo` (backend FastAPI chạy local port 8731 + Playwright headless Chromium) | Có | 21 | Yêu cầu tường minh: dùng ảnh sản phẩm thật, không mockup |
| Pickup ETA thật (giây), theo trace | Không có — `record_trace=False` mặc định trong mọi run tạo artifact hiện có; ETA giây không được lưu, chỉ deadhead COST ($) được cộng dồn | **Không** | — | Muốn có cần bật `record_trace=True` và CHẠY LẠI simulation — vi phạm "không rerun experiment" |
| Ví dụ số thật từ trace "Why This Driver" (cho slide 10) | Có thể lấy từ demo đang chạy (engine tính trực tiếp, không phải rerun offline experiment) nhưng cần thêm 1 vòng tương tác UI (search theo ID) | Không (cân nhắc, không theo đuổi thêm) | — | Giá trị tăng thêm nhỏ so với công thức khái niệm đã rõ; 1 screenshot demo thật đã đủ minh chứng sản phẩm hoạt động, tránh lạm dụng tương tác thủ công |
| Demand theo zone (heatmap) | Tính được từ raw parquet (groupby zone) | Xem xét, **không đưa** | — | Không có slide nào trong storyline dành chỗ cho việc này; thêm sẽ phải chèn thêm 1 chart mới ngoài kế hoạch → rủi ro dashboard-hóa |
| Trips per driver (derived) | `served_mean / 200` | Xem xét, **không đưa** | — | Trùng lặp trực tiếp với "served requests"/service rate đã dùng — vi phạm nguyên tắc không duplicate |
| Candidate depth / feasible driver count | Không có trong bất kỳ CSV/log nào; cần instrument lại simulator | **Không** | — | Cần sửa code + rerun để đo — vi phạm nguyên tắc không rerun |
| Fleet utilization (% thời gian driver bận) | Không có cột nào ghi driver-busy-time tổng | **Không** | — | Không tồn tại trong artifact hiện có |

## Screenshot thật

`assets/demo/control_room_live_simulation.png` — chụp bằng Playwright (headless
Chromium) sau khi: (1) chạy `python -m uvicorn app:app --host 127.0.0.1 --port 8731` từ
`05_SanPham_Demo/backend` (dùng đúng `engine_adapter.py` import thẳng
`src/policies.py`/`src/simulator.py` thật — không mock), (2) mở
`http://127.0.0.1:8731/` — backend tự mount frontend tĩnh, (3) bấm "New Run" rồi "Run"
với cấu hình mặc định (MOMAQL, 200 driver, Forecast ON, 3.000 request slice của
Validation), (4) chờ ~12 giây cho batch chạy thật, chụp màn hình. Server đã tắt sau khi
chụp xong (`taskkill` theo PID lấy từ `netstat`). Không sửa code sản phẩm, không tạo dữ
liệu giả, không chỉnh KPI trong ảnh.

## Nguyên tắc chọn lọc đã áp dụng

Với mỗi ứng viên, tự hỏi: "Nếu bỏ thông tin này đi, người nghe có mất insight quan trọng
không?" — 4 mục bị loại (demand theo zone, trips/driver, candidate depth, fleet
utilization, ETA giây thật) đều trả lời KHÔNG hoặc đòi hỏi rerun/instrument lại code, nên
bị loại. 9 mục được giữ đều trả lời CÓ và đều trace được về artifact/source code thật,
không cần rerun.

---

## Round 2 — bổ sung chart/KPI vận hành có chọn lọc + sửa mô tả REASSIGN

| Slide | Visual/KPI added | Source | Why it matters |
|---|---|---|---|
| 8 | 1 dòng phụ: 5&times;5=25 lần chạy baseline, 195.508/195.506 request Val/Test | `operational_metrics.json` (experiment_scale, dataset_scale) | Cho thấy quy mô thực nghiệm mà không cần thêm card mới; slide vẫn thoáng nên thêm được |
| 9 | Sửa mô tả REASSIGN từ "baseline tái dựng theo paper" &rarr; giải thích cách hoạt động thật (fare trừ deadhead cost, không nhìn tương lai, không cân bằng). Rà lại 4 policy còn lại cho rõ hơn | `src/policies.py` (đọc trực tiếp `select_batch` từng class) | Người nghe không biết "paper" là gì; mô tả mới tự đứng được không cần bối cảnh ngoài |
| 11 | Box "Ví dụ thật: MOMAQL trên Test" &mdash; Utility/Gini/Service rate/Avg income/Avg deadhead | `operational_metrics.json` (test_baseline_operational_by_policy.MOMAQL) | Gắn định nghĩa metric với số vận hành thật, không chỉ lý thuyết |
| 12 | Timeline đổi từ tỉ lệ theo ngày sang đúng tỉ lệ số chuyến (70/15/15) | tự tính từ dataset_checksums.json | Đúng yêu cầu "vẽ theo đúng số chuyến"; khác biệt nhỏ so với tỉ lệ ngày (67/16/17) nhưng chính xác hơn |
| 13 | Thêm 5 hbar service rate theo policy (Validation) | `operational_metrics.json` (validation_service_rate_by_policy) | Insight riêng biệt: MOMAQL không chỉ Utility cao mà còn phục vụ nhiều request hơn hẳn — khác với insight P90/P10 đã có, không trùng |
| 16 | Bảng nhỏ Full vs No Forecast service rate ở cả 3 fleet size (trước chỉ có Full) | `operational_metrics.json` (fleet_scale_service_rate) | Cho thấy RÕ cơ chế bão hòa: ở 400 driver cả hai đều ~99%, không phải riêng Full |
| 18 | Table+2 đoạn văn &rarr; 3 metric card (Val&rarr;Test) + 1 câu insight | số đã có, đổi cách trình bày | Giảm chữ, đúng yêu cầu "không cần quá nhiều chữ" |
| 19 | Box "Fairness check": 5/5 seed cả 2 split + &Delta;Gini Test = &minus;0,0427 | `final_test/ablation/test_ablation_results.csv` (gini_mean full vs no_forecast) | Bằng chứng lặp lại qua seed, không phải nhận xét chung chung |
| 20 | 1 câu annotation "ngắn hạn nhỏ, dài hạn rõ hơn" | không đổi số | Làm rõ ý nghĩa chart có sẵn, không thêm 11 checkpoint đầy đủ |
| 23 | Đổi card "1 demo bản đồ hoạt động thật" &rarr; "79,7% service rate MOMAQL trên Test" | `operational_metrics.json` | Scoreboard có cảm giác kỹ thuật/vận hành rõ hơn; demo vẫn được nhắc trong câu kết luận + slide 21 |

Metric cân nhắc thêm nhưng **không dùng** (mới, ngoài danh sách round 1): paired &Delta;Gini
Validation (chỉ tính được cho Test vì `r2_ablation_results.csv` không có bản per-seed đủ để
paired-match theo đúng cách final_test đã làm — dùng số Test là đủ mạnh, không cần thêm số
Validation gây rối).
