# Operator Control Room — Implementation Plan

8 P1 mandatory features (theo `FairDispatch_Operator_Control_Room_Requirements.md` §40).
Nice-to-have (Driver Ranking, Scenario Presets, Operator/Research toggle, Fleet What-if, Save
Scenario, Follow Driver, Demand/Supply heatmap, Income layer) **không làm vòng này** — đúng
permission của chính spec ("Bonus if complex; do not block P1").

| Requirement | Current support | Data source | Frontend change | Backend change | Risk | Test | Status |
|---|---|---|---|---|---|---|---|
| Objective Presets | Chỉ có λ slider raw | `cfgLam` input (config thật) | Button group Efficiency/Balanced/Fairness/Custom map sang λ 0.1/0.5/0.9/raw; tự chuyển Custom khi user kéo slider tay | Không | Thấp — chỉ UI label, λ vẫn gửi thật lên `POST /simulations` | Manual: chọn Efficiency → λ=0.1 gửi đúng | Done |
| Service Rate | `r.assigned`/`r.declined`/`r.infeasible_requests` đã có | `activateBatch(batch)` | `service_rate = assigned / requests_arrived` (mẫu số = assigned+declined+infeasible, không đếm trùng) | Không (đã đủ field) | Thấp | Manual + code review denominator | Done |
| Pickup ETA Avg/P90/Worst | `assignments[].pickup_eta_seconds` có, chưa aggregate | current batch assignments | Tính avg/P90 (nearest-rank, deterministic)/worst client-side mỗi batch activate | Không | Thấp | Unit-style JS self-check (`__pctl_selftest`) | Done |
| Demand/Supply | Demand có (`requests_arrived`); Supply (unique feasible driver) **chưa có** | mới: `feasible_drivers_unique` | Card hiện Demand/Supply/Ratio + status SHORTAGE | `engine_adapter._step_locked()` thêm `feasible_driver_ids = set()` — unique, không sum candidate edges | Trung bình — phải đúng semantics | `test_feasible_drivers_unique_is_deduplicated_not_sum_of_edges` | Done |
| Map Layer Control | 1 layer gộp request+declined+infeasible | Leaflet LayerGroup | Tách `mapLayers.requestMarkers`/`declined`/`infeasible`; checkbox toggle add/removeLayer, không đụng engine | Không | Thấp | Manual: toggle không gọi API nào | Done |
| Fairness Guardrail | Gini gauge có, chưa có ngưỡng | `batch.metrics.gini` | Input Max Gini (localStorage), alert khi vượt | Không | Thấp | Manual | Done |
| Alert Center | Chưa có | Service Rate/ETA P90/Gini/Demand-Supply đã tính ở trên | `evaluateAlerts(batch)` rule-based, render list severity | Không | Thấp | Manual: threshold crossing đúng | Done |
| Search Driver/Request | Chưa có | `driverMarkers`, `activeTrips`/`historyTrail` | Input + Enter → highlight/pan; nếu không có trong buffer → thông báo rõ, không giả | Không | Thấp | Manual | Done |

## Giữ nguyên (không đụng)

Continuous playback (global clock, prefetch, active trips, persistent driver marker, speed,
buffering), explainability (`selected_driver_id`/local rank/Hungarian), `/compare/live` fix,
Verified Replay (Compare/Horizon/History), provenance, session lock, tests hiện có.

## Metric definitions (operator-facing, không phải paper)

- **Service Rate** = assigned / (assigned + declined + infeasible) của batch đã activate gần
  nhất (Current Window). Mẫu số = `requests_arrived`.
- **Pickup ETA Avg/P90/Worst** = tính từ `pickup_eta_seconds` thật của assignments batch hiện
  tại. P90 = nearest-rank percentile (`sorted[ceil(0.9*n)-1]`), deterministic.
- **Demand** = `requests_arrived` batch hiện tại. **Supply** = `feasible_drivers_unique` (driver
  duy nhất xuất hiện trong candidate list của ít nhất 1 request, không sum edge).
- **Fairness guardrail / Service guardrails** = ngưỡng operator tự đặt (localStorage), KHÔNG
  phải khuyến nghị từ paper — ghi rõ trong tooltip UI.
- **Alert rules**: `service_rate < min_service_rate`, `pickup_eta_p90 > max_pickup_p90`,
  `gini > max_gini`, `demand/supply > shortage_ratio (mặc định 1.5×, operator-defined)`.
