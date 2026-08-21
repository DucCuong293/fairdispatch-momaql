# Data Quality Gate — test.parquet `duration_seconds` anomaly

**Status: AUDIT ONLY. No Final Test policy has been run. `test.parquet` on disk
is untouched — checksum unchanged (`96e7133f...`, verified against
`reports/dataset_checksums.json`).**

## 1. Phát hiện chính xác là gì?

33 dòng trong `test.parquet` có field `duration_seconds` bị sai (giá trị
~4,255,507 đến 4,294,815 giây, tức ~1183–1193 giờ ≈ 49.4–49.7 ngày). NHƯNG:
`pickup_ts`/`dropoff_ts` thật của đúng 33 dòng đó hoàn toàn bình thường —
`dropoff_ts - pickup_ts` tính ra chỉ từ 0 giây (1 dòng, pickup==dropoff hệt
nhau) đến tối đa 14,440 giây (~4.01 giờ), trung vị 1,488 giây (~25 phút).

Kết luận: **timestamp thật hoàn toàn hợp lệ — chỉ riêng field
`duration_seconds` đã lưu sai giá trị.**

## 2. Có bao nhiêu rows bị ảnh hưởng?

33 / 195,510 dòng của `test.parquet`.

## 3. Tỷ lệ bao nhiêu %?

**0.016879%** (≈1/5,940 dòng).

## 4. Max duration là bao nhiêu?

- `duration_seconds` lưu (sai): **4,294,815 giây ≈ 1,193.0 giờ ≈ 49.7 ngày.**
- `dropoff_ts - pickup_ts` tính thật (đúng) của cùng 33 dòng: **14,440 giây ≈ 4.01 giờ** (dòng lớn nhất).

## 5. Stored duration có khớp timestamp không?

**Không.** Với đúng 32/33 dòng: `duration_seconds` lệch `dropoff_ts-pickup_ts`
khoảng 4.25–4.29 triệu giây — không phải sai số làm tròn nhỏ. 1/33 dòng có
`pickup_ts == dropoff_ts` (0 giây thật) nhưng `duration_seconds` vẫn lưu
4,294,815.

(Ghi chú phụ: sai số nhỏ 2–3 giây giữa stored và computed cũng tồn tại rải
rác ở CẢ 3 split — train 27,260 dòng, val 2,454 dòng, test 306 dòng — đây là
nhiễu làm tròn/parse timestamp bình thường, không liên quan tới 33 dòng bất
thường. Cụm bất thường ≥4,200,000 giây CHỈ xuất hiện ở test, 0 dòng ở train/val.)

## 6. Train có anomaly tương tự không?

**Không.** `train.parquet` (912,375 dòng): `duration_seconds` max = 8,640s
(2.4 giờ), 0 dòng > 4h/6h/12h/24h.

## 7. Validation có anomaly tương tự không?

**Không.** `val.parquet` (195,508 dòng): max = 8,640s (2.4 giờ) — giống hệt
train, 0 dòng > 4h.

## 8. Test có anomaly tương tự không?

**Có** — đây chính là 33 dòng đang audit. Đây là split DUY NHẤT có bất
thường này.

## 9. Các split có dùng cùng preprocessing không?

**Có, giống hệt nhau.** Cả `build_sample.py` và `merge_split.py` (script
duy nhất tạo cả 3 file) chỉ dùng `SELECT *` truyền nguyên cột từ nguồn
canonical thượng nguồn, lọc bởi `manhattan_both=true AND quality_flag_bitset=0`,
rồi cắt theo `pickup_ts` thời gian (`LIMIT`/`OFFSET`). **Không có bất kỳ dòng
code nào tính lại hoặc lọc `duration_seconds`** ở cả 2 script — xem trích dẫn
chính xác file/dòng trong `preprocessing_duration_audit.md`.

## 10. Có evidence đây là preprocessing bug không?

**Không** — đã loại trừ. `build_sample.py`/`merge_split.py` không đụng vào
`duration_seconds`, nên không thể là nguồn gây lỗi.

## 11. Có evidence đây là raw-data anomaly không?

**Có, xác nhận trực tiếp.** Đã trace 1 dòng cụ thể (`trip_key=522975df...`,
`row_idx=164421`, `source_month=8`, `source_row_number=10607937`) ngược lại
file nguồn canonical thượng nguồn
(`restricted_data/.../source_month=08/part-000.parquet`, ngoài repo này):
`duration_seconds=4294815` và `quality_flag_bitset=0` **đã tồn tại y hệt ở
nguồn thượng nguồn**, giống byte-for-byte với `test.parquet`. Lỗi có từ
nguồn dữ liệu gốc, không phải do pipeline của project này tạo ra.

## 12. Nếu giữ nguyên, simulator có thể bị ảnh hưởng thế nào?

`simulator.py:101`: `d.available_at = now + eta + req["duration_seconds"]`.
Nếu 1 trong 33 request này được Hungarian assign cho 1 driver, driver đó bị
khóa khỏi fleet (`feasible_drivers()` kiểm tra `d.available_at > now` tại
`simulator.py:84`) trong ~1,193 giờ ≈ **49.7 ngày** — dài hơn TOÀN BỘ test
span (42 ngày, `test_n_days` từ `split_integrity.json`). Tức driver đó coi
như **biến mất khỏi fleet cho hết cả kỳ đánh giá**, làm giảm ngầm effective
fleet size mà không có cảnh báo nào — có thể ảnh hưởng khác nhau tuỳ policy
(policy nào "vô tình" chọn phải request lỗi sẽ bị mất driver oan). Đây chỉ
là giải thích cơ chế qua code — **chưa chạy policy nào để đo impact thật**.

## 13. Rule ≤24h có phải data-quality rule hợp lý không?

**Có, hợp lý và không cherry-pick.** 3 lý do:

- Margin rất lớn cả 2 phía: ngưỡng 24h = 86,400s nằm giữa max thật hợp lệ
  của toàn bộ 3 split (2.4h ở train/val; 4.01h là dòng lớn nhất trong 33
  dòng lỗi ở test) và cụm giá trị lỗi (~1,183–1,193 giờ) — cách xa **~49
  lần** so với cụm lỗi, và **~6–10 lần rộng rãi hơn** so với chuyến dài nhất
  từng thấy trong dữ liệu thật. Không nằm sát biên 33 dòng theo kiểu chọn số
  để vừa khít.
- Không có chuyến nào thật trong khoảng 4–24h bị threshold này loại nhầm —
  đã kiểm tra: 0 dòng trong toàn bộ 3 split rơi vào khoảng (4h, 24h).
- Không có existing pipeline rule nào tốt hơn để dùng (câu 9/10) — filter
  duy nhất đã có (`quality_flag_bitset=0`) đã áp dụng nhưng KHÔNG bắt được
  lỗi này (xem câu 10).

## 14. Recommendation

## RECOMMENDATION (revised, user-approved): **minimal deterministic repair**

**KHÔNG loại toàn bộ 33 dòng.** Evidence tự audit đã chứng minh 32/33 dòng
có `pickup_ts`/`dropoff_ts` hợp lệ và `computed_duration = dropoff_ts -
pickup_ts` dương, ≤24h — chỉ derived field `duration_seconds` bị corrupt.
Xoá 32 request hợp lệ đó khỏi held-out test là mất dữ liệu không cần thiết.
Thay vào đó: **timestamp được coi là nguồn dữ liệu authoritative**,
`duration_seconds` là derived field bị lỗi ở các dòng này — sửa (repair) từ
timestamp thay vì loại bỏ toàn bộ request.

Rule áp dụng UNIFORM trên train/val/test (train/val expected 0
repaired/excluded — đã verify programmatically, không hard-code):

```text
computed_duration = dropoff_ts - pickup_ts

if 0 < duration_seconds <= 24h:
    giữ nguyên (KEPT_RAW)
elif 0 < computed_duration <= 24h:
    duration_seconds_eval = computed_duration   (REPAIRED_FROM_TIMESTAMPS)
else:
    exclude khỏi evaluation view                (EXCLUDED_INVALID_DURATION)
```

### Why

- Timestamp là nguồn dữ liệu authoritative; `duration_seconds` chỉ là
  derived/corrupt field ở các dòng này (câu 11) — sửa từ nguồn authoritative
  hợp lý hơn xoá cả request.
- Giữ lại request hợp lệ tránh xoá held-out test không cần thiết — chỉ loại
  đúng 1 dòng thực sự không thể phục hồi (`pickup_ts==dropoff_ts`, computed
  duration = 0, không dương).
- Rule được định nghĩa và freeze **trước khi nhìn bất kỳ Test policy
  outcome nào** — thuần từ audit dữ liệu.

### Kết quả thật (verify bằng code, không hard-code — `quality_transform.py`)

| Split | Original | Boundary excluded | Repaired | Duration excluded | Final evaluated |
|---|---:|---:|---:|---:|---:|
| train | 912,375 | 0 | 0 | 0 | 912,375 |
| val | 195,508 | 0 | 0 | 0 | 195,508 |
| test | 195,510 | 3 | **32** | **1** | **195,506** |

Dòng bị exclude do duration (verify đúng dự đoán, không hard-code):
`row_idx=164421`, `pickup_ts==dropoff_ts`, computed duration=0s, trip_distance=0,
fare=$0, total=$0 — zero trip thật, không thể phục hồi.

### Thiết kế (evaluation-time transform, KHÔNG sửa file gốc)

```text
test.parquet (immutable, checksum 96e7133f... KHÔNG đổi — verify lại sau transform)
        │
        ▼
rule 1: temporal-boundary hygiene (tách biệt, KHÔNG trộn với rule 2)
        exclude 3 dòng test trùng giây ranh giới với val.max
        │
        ▼
rule 2: duration-quality minimal deterministic repair
        32 repaired từ timestamp, 1 excluded (không thể phục hồi)
        │
        ▼
Final Test Evaluation View: 195,510 − 3 − 1 = 195,506 requests
```

Không overwrite `duration_seconds` gốc — mỗi request giữ cả
`duration_seconds_raw`, `duration_seconds` (= eval, đã repair nếu có), và
`quality_action` (`KEPT_RAW`/`REPAIRED_FROM_TIMESTAMPS`/
`EXCLUDED_INVALID_DURATION`/`EXCLUDED_TEMPORAL_BOUNDARY`). Chi tiết đầy đủ:
`final_test/test_quality_transform_manifest.json`.

## Files created

- `final_test/test_duration_anomalies.csv` — đầy đủ 33 dòng, mọi field liên
  quan (timestamp, computed vs stored duration, distance, fare, zone,
  toạ độ, quality flags, provenance columns).
- `final_test/test_duration_audit.json` — bảng so sánh train/val/test +
  finding structured.
- `final_test/preprocessing_duration_audit.md` — trích dẫn chính xác
  file/dòng code + bằng chứng trace ngược nguồn thượng nguồn.
- `final_test/DATA_QUALITY_GATE.md` — file này.

## NEXT ACTION

Chờ quyết định của bạn: áp dụng filter C (khuyến nghị) hay giữ nguyên (A).
**Chưa chạy bất kỳ Final Test policy nào — MOMAQL/Greedy/Nearest/LAF/
REASSIGN, Full/No Forecast/No Fairness, λ sweep đều CHƯA được chạy trên
test.parquet.**
