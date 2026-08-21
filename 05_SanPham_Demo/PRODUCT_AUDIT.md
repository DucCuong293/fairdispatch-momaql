# Product Audit — FairDispatch Decision-Support Prototype

Audit thực hiện trước khi viết bất kỳ dòng frontend nào, theo yêu cầu Phần B mục 1–2 của
`FairDispatch_Product_Demo_Requirements_and_Claude_Prompt.md`. Mọi capability dưới đây được
xác minh trực tiếp trong `fairdispatch_v3_clean/src/simulator.py` và `src/policies.py`
(đọc toàn bộ, không đoán), không suy diễn từ tên hàm.

## Engine thật có gì

| Thành phần | Có thật không | Nguồn (file:hàm) |
|---|---|---|
| Batched M-to-N dispatch (60s window) | Có | `simulator.py:run_simulation_batched` |
| Driver state (lat, lon, income, trips, available_at) | Có | `simulator.py:Driver` (dataclass) |
| Request có lat/lon thật (không chỉ zone ID) | Có — NYC TLC thật, lat 40.70–40.88, lon -74.02..-73.91 | `common_loader.py:load_requests_fast` |
| Feasibility (ETA ≤ 600s) | Có | `simulator.py:feasible_drivers` |
| Commit trip (cập nhật driver) | Có | `simulator.py:commit_trip` |
| Hungarian joint assignment (5 policy dùng chung) | Có | `policies.py:hungarian_batch_assign` (scipy `linear_sum_assignment`) |
| Score MOMAQL tách được 3 thành phần | Có — `_score()` trả `(1-λ)(fare-deadhead+γ·Q) + λ·fairness`, có thể decompose trực tiếp không cần recompute công thức khác | `policies.py:MOMAQLPolicy._score` |
| Score 4 baseline (Greedy/Nearest/LAF/REASSIGN) | Có, mỗi cái 1 dòng công thức thật trong `select_batch` | `policies.py` |
| Gini / variance / std / CV | Có | `common_loader.py` |
| Q-table đã train (frozen, dùng cho eval) | Có, file JSON 47KB | `data/momaql_q_table_trained.json` |
| Step-by-window API (tách riêng `Run`/`Step`) | **Không có sẵn** — `run_simulation_batched` chạy `while` liền một mạch, không yield | — |
| Assignment trace với candidate scores khác | **Không có sẵn** — trace chỉ lưu `(req_idx, driver_id, fare, deadhead_cost, dropoff_zone)`, không lưu alternative candidates | `simulator.py:SimResult.trace` |
| Zone polygon/geometry (bản đồ zone) | **Không có** trong repo — chỉ có `zone_id` số nguyên | — |
| Trained MLP model file để serve live | **Không có** — chỉ có kết quả CSV đã chạy sẵn (`train_and_eval_mlp.py` không lưu model ra đĩa) | — |

## Quyết định implementation cho từng gap

| Gap | Quyết định | Lý do |
|---|---|---|
| Không có Step API | Viết `engine_adapter.py`: một generator mỏng lặp lại **đúng logic vòng lặp** của `run_simulation_batched` (copy cấu trúc vòng `while`, nhưng gọi lại `feasible_drivers`, `commit_trip`, `policy.select_batch` **thật** import từ `simulator.py`/`policies.py`, không viết lại thuật toán chấm điểm/matching) | Đúng yêu cầu "không copy logic thuật toán thành bản thứ hai" — chỉ đổi cách điều phối vòng lặp (yield mỗi window), không đổi cách tính điểm/matching |
| Không có candidate-score trace | Khi Step xong một window, backend giữ lại `cands_map` + `mean_income` của window đó trong session; khi FE click vào 1 assignment, backend **gọi lại đúng score function thật** của policy đang chạy (vd `MOMAQLPolicy._score`, hoặc công thức 1 dòng thật của Greedy/Nearest/LAF/REASSIGN lấy verbatim từ `policies.py`) cho từng candidate của request đó | Tính từ implementation thật, không recompute bằng công thức khác |
| Không có zone geometry | Map dùng marker/route thật theo lat/lon thật (driver, pickup, dropoff), không cần polygon/zone shapefile. **Cập nhật round 2 (Leaflet port):** đổi renderer từ SVG tự vẽ sang Leaflet 1.9.4 + basemap CARTO light (CDN, có internet lúc demo), có fallback tĩnh nếu CDN chặn — xem `PRODUCT_FRONTEND_PORT_PLAN.md` | Vẫn là dữ liệu không gian thật, không giả lat/lon; đổi renderer không đổi nguồn data |
| Simulation 195,508 request quá lâu để Step sống | Live mode giới hạn `request_limit` (mặc định 3,000 request đầu, cấu hình được tới toàn bộ) | Step phải phản hồi ngay, không block demo |
| Không có model MLP để serve | MLP chỉ xuất hiện ở Replay Mode (đọc thật `reports/mlp_vs_tabular_summary.csv`), không có live MLP toggle | Không invent capability engine chưa hỗ trợ |
| History 37-ngày quá lâu để chạy live trong demo | Long-Horizon Timeline dùng Replay Mode, đọc thật `reports/multi_horizon_results.csv` (166 dòng gốc, đã verify khớp báo cáo) | Đúng khuyến nghị mục 15–16 của spec |

## Vị trí data thật được dùng (không hard-code)

- **Live simulation**: đọc trực tiếp `fairdispatch_v3_clean/data/val.parquet` qua `pyarrow` (đường dẫn tuyệt đối tới repo dev, vì file parquet quá lớn để copy vào gói nộp — đã disclose trong README).
- **Policy engine**: import trực tiếp `03_Source_Code_Va_Ket_Qua/src/policies.py` + `simulator.py` (bản copy y hệt SHA với repo dev, đã verify ở bước đóng gói trước) — không viết lại.
- **Q-table MOMAQL**: `03_Source_Code_Va_Ket_Qua/data/momaql_q_table_trained.json` (đã có sẵn trong gói).
- **Replay Mode**: đọc trực tiếp `03_Source_Code_Va_Ket_Qua/reports/*.csv` — đúng các file đã dùng để build Research Report/slide (r1_validation_results.csv, r2_ablation_results.csv, r2_ablation_raw.csv, multi_horizon_results.csv, fleet_scale_results.csv, pareto_frontier_summary.csv, mlp_vs_tabular_summary.csv).
- **Provenance**: `dataset_checksums.json` (SHA-256 thật) + `git rev-parse HEAD` thật của repo dev tại thời điểm request.

## 5 deliverable trung tâm (mục 29 của spec) — trạng thái

| # | Deliverable | Trạng thái |
|---|---|---|
| 1 | Map driver+request+assignment thật | Implement — Leaflet + lat/lon thật (round 2: port renderer từ demo_fairdispatch, data/logic không đổi) |
| 2 | Run/Step/Reset | Implement — Step là API thật đồng bộ; "Run" = client tự gọi Step lặp lại (có thể Pause bất kỳ lúc nào vì mỗi step độc lập); không giả animation |
| 3 | Utility/Gini từ engine thật | Implement — tính lại bằng đúng `gini()`/`variance()` từ `common_loader.py` trên state driver thật sau mỗi step |
| 4 | Compare Full vs No-Forecast | Implement — mặc định đọc Replay thật (`r2_ablation_results.csv`, 5 seed, 195,508 request — đáng tin hơn hẳn 1 lần chạy live nhỏ); có thêm nút "Live Quick Compare" chạy 2 live session nhỏ cùng seed/slice để xem trực tiếp |
| 5 | Click assignment → giải thích | Implement — decompose công thức thật theo policy đang chạy |

Rất nên có (implement vì rẻ, dữ liệu đã có sẵn): Run provenance, Run History (in-memory), Driver income distribution (histogram từ state thật), Long-Horizon Timeline (Replay), Lambda slider (đổi λ live cho MOMAQL + hiển thị điểm λ-sweep thật từ Replay).

Bonus không làm (theo đúng khuyến nghị "không cần" của spec): Login/Register, CSV export, MLP live toggle, animation phức tạp, WebSocket/Kafka, microservices.
