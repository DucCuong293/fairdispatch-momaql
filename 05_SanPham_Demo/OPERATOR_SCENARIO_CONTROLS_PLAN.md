# Operator Scenario Controls — Implementation Plan

| Feature | Current support | Data source | Frontend changes | Backend changes | Tests | Status |
|---|---|---|---|---|---|---|
| Time-of-day filter | Không có | mới: `pickup_hour` (đã có), filter theo giờ thật | Segmented buttons Cả ngày/Sáng/Chiều/Đêm/Tùy chỉnh + custom start/end hour | `_hour_in_time_filter()` + `TimeFilter` Pydantic model, overnight wrap (22..5) | `test_time_filter_all_day_and_named_presets`, `test_time_filter_overnight_wrap` | Done |
| Day filter | Không có | mới: `pickup_weekday` (mới tính từ epoch thật) | Buttons Cả tuần/Ngày thường/Cuối tuần/Tùy chỉnh (checkbox T2-CN) | `_weekday_in_day_filter()` + `DayFilter`; weekday = `(epoch_day+3)%7` (epoch 0 = Thứ 5 thật) | `test_day_filter_weekday_weekend_custom` | Done |
| Filter order | limit áp trước (bug tiềm ẩn) | — | — | `SimulationSession.__init__`: load full → `apply_scenario_filters()` → slice `request_limit` | `test_scenario_filter_applied_before_request_limit` | Done |
| Horizon presets | Có (Round 5, giá trị 3000/10000/195508) | — | Đổi giá trị theo spec mới: Quick=200/Standard=3000/Extended=10000/Custom | Không (dùng `request_limit` thật) | Manual | Done |
| Fleet presets | Chỉ có raw input | — | Buttons 100/200/400/Custom, đổi `n_drivers` thật gửi backend | Không | Manual | Done |
| Save Run | Không có | localStorage | Nút "💾 Save Run" lưu config+metrics thật (policy/objective/fleet/forecast/λ/γ/α/seed/dataset/time_filter/day_filter/request_limit + utility/gini/served batch gần nhất) vào `localStorage["fd_saved_runs"]`, cap 20 | Không | Manual | Done |
| Collapsible sections | Chỉ Advanced có `<details>` | — | Toàn bộ 8 section (Current Run/Objective/Scenario/Simulation/Service Health/Fairness/Alerts/Map Layers) chuyển sang `<details>` native | Không | Manual | Done |
| Scenario summary + badge | Không có | Đọc trực tiếp form state | `updateScenarioSummary()` render text + badge "SCENARIO FILTER ACTIVE" khi time/day != default | Không | Manual | Done |
| Layout spacing bug | Khoảng trắng lớn trước Operational Log | CSS root cause | Xem mục dưới | — | Manual @ 1920×1080/1600×900/1366×768 | Done |

## Không thêm (đúng permission của spec)

Confidence 70/80/90% (không có calibrated metric thật), Q calibration chung/theo band (research/
debug control, không cần cho Operator), nhóm đại diện/>300k (không có semantic trong project
hiện tại), concurrent-vehicle engine limiter (số xe active do simulator quyết định, frontend
không được giới hạn — nếu cần giảm rối mắt, dùng Map Layers/Recent Trails có sẵn, không phải
engine control).

## Layout spacing root cause (Phase 38-51 của spec)

`.rightpanel{grid-row:1/3}` trong `.shell` (grid `1fr 330px` / `auto auto`) không bound chiều
cao — khi sidebar dài ra (nhiều card Operator mới), track-sizing của CSS Grid giãn row1 (map)
để chứa sidebar, đẩy `.logwrap` (row2) xuống, tạo khoảng trắng lớn giữa charts và Operational
Log. Fix root cause (KHÔNG dùng negative margin): `.rightpanel{align-self:start;max-height:
calc(100vh - 150px);overflow-y:auto;}` — sidebar tự scroll độc lập, không còn ảnh hưởng chiều
cao row1/row2. Giảm gap `.shell`/`.chartsrow` 14px→10px theo density target (8-12px).

## Test set

Không đổi — `dataset` vẫn cố định `"val"` (Validation), không có control nào expose `test`
trong luồng Operator thông thường (đúng Phase 16/20/27 của spec).

## Time filter semantics

`_hour_in_time_filter(hour, filter)`: nếu `start<=end` → `start<=hour<end`; nếu `start>end`
(qua nửa đêm, vd 22→5) → `hour>=start OR hour<end`. Test cả 2 nhánh + case rỗng (start==end).

## Day filter semantics

`pickup_weekday` tính thật từ epoch giây: `(days_since_epoch + 3) % 7`, 0=Thứ 2..6=Chủ nhật
(1970-01-01 là Thứ 5 thật → offset +3). Weekday = 0..4, Weekend = 5..6.
