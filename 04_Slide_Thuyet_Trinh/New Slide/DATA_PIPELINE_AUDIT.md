# Data Pipeline Audit — FairDispatch (NYC TLC 2013)

Audit thực hiện bằng cách đọc trực tiếp code trong repo này
(`03_Source_Code_Va_Ket_Qua/`) trước khi sửa slide 7/12. Không suy đoán bước nào không có
bằng chứng trong code/doc. Không rerun bất kỳ pipeline nào — chỉ đọc.

## A. Raw source — KHÔNG nằm trong repo này (công khai theo đúng thực tế)

`data/build_sample.py` (dòng 1-21, docstring) nói rõ:

> "Source: the project's own already-cleaned, already-joined, already-zoned canonical
> dataset (`restricted_data/foil_2013_legacy/09_canonical/realistic_2013_splits/development/
> source_month={01..08}/part-000.parquet`) — real NYC TLC 2013 trip+fare data, already
> quality-filtered by the project's own **P2-01 pipeline** (`quality_flag_bitset`,
> `trip_fare_join_status`). No re-cleaning from raw here — that work already exists and is
> real; redoing it would just duplicate already-correct effort."

Nói theo đúng yêu cầu mục 12 của prompt: **Processed dataset was provided/prepared
upstream (dự án Phase 2 riêng, "P2-01 pipeline"); repo `FairDispatch_MOMAQL_Fair_Ride_
Hailing_Dispatch_Replication` này xác minh và tiêu thụ schema đã xử lý sẵn (đọc trực tiếp
cột `pickup_zone_id`, `dropoff_zone_id`, `manhattan_both`, `quality_flag_bitset`,
`trip_fare_join_status` — đã tồn tại sẵn trong parquet) nhưng KHÔNG lưu lại từng bước làm
sạch raw ban đầu (raw TLC parse, join fare, tính quality flag, ánh xạ lat/lon → zone) trong
source tree của repo này.**

Xác nhận thêm từ `docs/techdoc/build_technical_documentation.py` (mục "Giả định A2",
dòng 602-604): *"Biểu diễn không gian dùng 67 zone taxi TLC chính thức, không phải đồ thị
tự gộp cụm — pickup_zone_id/dropoff_zone_id lấy trực tiếp từ cột parquet, codebase này
không có bước clustering thêm."* → xác nhận: **67 zone = hệ thống zone chính thức của NYC
TLC** (không phải cụm tự gộp), và việc ánh xạ tọa độ → zone_id đã xảy ra ở thượng nguồn.

## B. Các bước tiền xử lý THẬT trong repo này (đã verify từng dòng code)

| # | Bước | Chi tiết thật | Source |
|---|---|---|---|
| 1 | Lọc | `manhattan_both = true AND quality_flag_bitset = 0` | `data/build_sample.py` dòng 39-42, 56-59 |
| 2 | Lấy mẫu | Bernoulli sample tỉ lệ theo từng tháng (01-08/2013), tổng đích ~1.300.000 dòng, seed cố định `20260721` | `data/build_sample.py` dòng 49-64 |
| 3 | Gộp + sắp xếp | Gộp 8 file mẫu theo tháng, `ORDER BY pickup_ts` (thời gian thật) | `data/build_sample.py` dòng 67-71; `data/merge_split.py` dòng 13-22 |
| 4 | Chia theo thời gian | 70% sớm nhất &rarr; `train.parquet`, 15% tiếp &rarr; `val.parquet`, 15% cuối &rarr; `test.parquet` — liên tục theo `pickup_ts`, không random | `data/build_sample.py` dòng 73-86 |
| 5 | Dựng request cho simulator | Đọc 9 cột thật (`pickup_ts, pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude, fare_amount, duration_seconds, pickup_zone_id, dropoff_zone_id`), tính thêm `pickup_hour = (epoch_sec // 3600) % 24`, `dropoff_hour = ((epoch_sec + duration_seconds) // 3600) % 24` (giờ thật theo epoch, không lệch theo file) | `common_loader.py` hàm `load_requests_fast`, dòng 5-33 |
| 6 | ETA/deadhead lúc chạy simulator (không phải bước tiền xử lý, tính runtime) | Haversine giữa pickup/dropoff lat-lon thật, quy đổi thời gian bằng tốc độ hằng số giả định 12 mph | `src/simulator.py` dòng 25-40 (`haversine_miles`, `eta_seconds`, hằng `AVG_SPEED_MPH`) |

Không có bước nào trong danh sách trên là suy đoán — mỗi dòng đọc trực tiếp từ code đã dẫn.
**Không có** bước lọc `fare > 0`, `distance > 0`, loại outlier, hay drop duplicate nào trong
repo này — nếu những bước đó tồn tại, chúng nằm ở pipeline P2-01 thượng nguồn, ngoài phạm
vi source tree đang audit.

## C. Schema thật của MỘT chuyến (record) mà simulator nhận

Full canonical schema (đọc trực tiếp `train.parquet` bằng `pyarrow.parquet`, 32 cột) có đủ
thông tin nghiệp vụ (fare breakdown, driver_key, vendor_id, borough, split_label...), nhưng
**FairDispatch chỉ thật sự dùng 9/32 cột** (qua `common_loader.load_requests_fast`) + 2 cột
tự tính:

```
pickup_ts            timestamp[us]   thời điểm đón khách thật
pickup_latitude       double         tọa độ điểm đón
pickup_longitude      double         tọa độ điểm đón
dropoff_latitude      double         tọa độ điểm trả
dropoff_longitude     double         tọa độ điểm trả
fare_amount            double         cước phí thật ($)
duration_seconds       int64         thời lượng chuyến thật (giây)
pickup_zone_id          int32         zone TLC nơi đón (đã có sẵn trong parquet)
dropoff_zone_id         int32         zone TLC nơi trả (đã có sẵn trong parquet)
--- tự tính trong common_loader.py, không có sẵn trong parquet ---
pickup_hour             int           giờ trong ngày lúc đón (0-23)
dropoff_hour             int           giờ trong ngày lúc trả (0-23)
```

`pickup_zone_id`/`dropoff_zone_id` chính là 2 trường mà `MOMAQLPolicy._score` dùng để tra
`Q[dropoff_zone, dropoff_hour]` (`src/policies.py` dòng 214-219) — Q(vùng,giờ) hợp lý với
cấu trúc dữ liệu này chính vì mọi record đã sẵn có đúng 2 trục (zone, hour) ở độ chi tiết
Q-table cần, không phải suy diễn thêm.

## D. Dataset profile — tính từ dữ liệu thật (read-only, `scripts/profile_dataset.py`)

Chạy trên toàn bộ 1.303.393 dòng (train+val+test gộp, đúng 3 file dùng thật trong project).

| Metric | Giá trị | Ghi chú |
|---|---|---|
| Tổng số chuyến | 1.303.393 | 912.375 + 195.508 + 195.510 |
| Khoảng thời gian | 01/01/2013 00:00:10 &ndash; 31/08/2013 23:59:28 | 243 ngày quan sát |
| Pickup zone thực sự xuất hiện | 66 / 67 | Dropoff zone: 67/67 |
| Chuyến/ngày | trung vị 5.466 &middot; TB 5.363,8 &middot; min 2.030 &middot; max 6.698 | |
| Giờ cao điểm | 19h (18h&ndash;21h nói chung cao) &mdash; 6,59% tổng chuyến | |
| Giờ thấp điểm | 5h &mdash; 0,74% tổng chuyến | |
| Fare trung vị | $8,50 (P25 $6,00 &middot; P75 $12,00 &middot; P90 $16,00) | |
| Thời lượng chuyến trung vị | 540 giây (9 phút) &middot; P90 1.140 giây (19 phút) | |
| Khoảng cách chuyến trung vị | 1,59 dặm &middot; P90 3,81 dặm | cột `trip_distance_miles` &mdash; KHÔNG phải nguồn ETA của simulator (simulator tự tính lại bằng haversine, xem mục B.6) |

Top 10 pickup zone (theo `pickup_zone_id`, số chuyến): 237 (53.002) &middot; 161 (50.119)
&middot; 234 (48.531) &middot; 170 (48.061) &middot; 162 (47.728) &middot; 236 (47.472)
&middot; 230 (46.281) &middot; 48 (45.014) &middot; 79 (44.805) &middot; 186 (42.846).
Chênh lệch giữa top 1 và top 10 không lớn (53.002 vs 42.846, ~1,2 lần) — demand không tập
trung cực đoan vào 1-2 vùng, phân bố tương đối trải đều trong nhóm zone đông đúc nhất; vì lý
do này, chart top-zone không có insight mạnh bằng chart giờ-trong-ngày (biên độ 0,74%&ndash;
6,59%, gấp ~9 lần), nên **chart được chọn cho slide là "chuyến theo giờ trong ngày"**, không
dùng top-zone hay heatmap zone&times;hour.

## E. Trả lời 6 câu hỏi QA bắt buộc

1. **Dữ liệu đến từ đâu?** NYC TLC 2013 trip+fare data thật, đã được làm sạch/join/gán zone
   sẵn ở pipeline P2-01 thượng nguồn (ngoài repo này); repo này lấy mẫu và chia lại theo
   thời gian.
2. **Khoảng thời gian nào?** 01/01/2013 &ndash; 31/08/2013 (243 ngày, 8 tháng).
3. **Bao nhiêu chuyến?** 1.303.393 (912.375 Train + 195.508 Validation + 195.510 Test).
4. **Một chuyến gồm gì?** 9 trường thật (thời điểm đón, tọa độ đón/trả, fare, thời lượng,
   zone đón/trả) + 2 trường tự tính (giờ đón, giờ trả) — xem mục C.
5. **Tiền xử lý thế nào?** Lọc Manhattan+chất lượng (2 cờ có sẵn) &rarr; lấy mẫu tỉ lệ theo
   tháng &rarr; sắp xếp theo `pickup_ts` &rarr; chia liên tục 70/15/15 theo thời gian — xem
   mục B.
6. **Đi vào simulator ra sao?** `load_requests_fast` dựng request 11 trường/dòng; mỗi cửa
   sổ 60 giây, simulator tính ETA bằng haversine + tốc độ giả định, ghép bằng Hungarian
   theo score của từng policy.
