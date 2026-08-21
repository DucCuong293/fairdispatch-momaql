# Frontend Port Plan — `demo_fairdispatch` visual shell → `05_SanPham_Demo`

Đọc full `demo_fairdispatch/index.html` (678 dòng, phần data JSON inline ở dòng 221–226 bị
bỏ qua — không cần, không liên quan). Port đúng: layout grid, topbar, card/chip/gauge/tracker
style, Leaflet init pattern, log table. KHÔNG port: `NODES`/`TOP_ZONES` (dataset riêng của demo
cũ, không có trong engine hiện tại), Q-score giả, driver label theo reveal index, income
reveal theo mảng precompute, mọi số liệu cũ (S8300/P2-13/MOMAQL Gini~0.925).

## Mapping

| Current component | demo_fairdispatch component | Data source mới | API endpoint | Port approach | Regression risk |
|---|---|---|---|---|---|
| `<svg id="mapSvg">` scatter tự vẽ | `#map` Leaflet + CARTO light tile | `r.drivers[]`, `r.assignments[]`, `r.declined_requests[]`, `r.infeasible_requests[]` (lat/lon thật) | `POST /simulations/{id}/step` | Thay hẳn SVG bằng `L.map`/`L.circleMarker`/`L.polyline`, giữ nguyên bbox NYC thật đã verify (lat 40.70–40.88, lon -74.02..-73.91) | **Cao** — phải giữ đúng field nào vẽ ở đâu (driver_start cho deadhead, pickup/dropoff cho trip) |
| `.legend-inline` dưới map | `.legend` overlay góc bản đồ (`position:absolute`) | tĩnh (chú giải màu) | — | Port class `.legend`, giữ nội dung legend hiện tại (đã đầy đủ hơn bản cũ: có declined/infeasible) | Thấp |
| Header `.topbar` hiện tại (chips ẩn/hiện bằng JS) | `.topbar` gradient navy + `.chips` pill | `session.policy/batch/status`, `/provenance` | đã có | Port CSS `.chips`/`.chip`, giữ đúng field đang bind (Policy/Batch/Status/backend dot) | Thấp |
| `#assignTable` + `#explainBox` (div thường) | `.card.tracker` (route/fare lớn/qrow/compare box) | `GET /explain/{req_idx}` — **đã có `selected_driver_id`/`local_rank`/`is_selected` từ fix P0.1** | đã có | Port style `.tracker`, nội dung vẫn là data thật từ `/explain`, thêm badge "GLOBAL OPTIMUM" khi `local_rank>1` (đúng field đã tồn tại, chỉ đổi trình bày) | **Cao — đây là bug đã fix, phải test lại sau port** |
| `#histBars` (div bar tự vẽ) | `.chart-card` (canvas Chart.js) | `r.income_histogram` (đã tính thật ở backend) | đã có | Giữ nguyên bar tự vẽ bằng div (không thêm dependency Chart.js chỉ vì 1-2 chart — vi phạm YAGNI); áp style `.chart-card` để đồng bộ visual | Thấp |
| `#lorenzWrap svg` | `ch-lorenz` canvas | `r.lorenz` (đã tính thật) | đã có | Giữ SVG polyline tự vẽ hiện tại (đã đúng, nhẹ hơn Chart.js), áp style `.chart-card` | Thấp |
| Không có gauge | `.gauge` SVG donut (Gini) | `r.metrics.gini` | đã có | Thêm 1 gauge donut cho Gini hiện tại (giá trị thật, `stroke-dasharray` tính từ `metrics.gini`) | Thấp (feature mới, không đụng logic cũ) |
| `#historyTable`/tab Compare/Horizon | `table.logtbl` style | không đổi nguồn | đã có | Chỉ đổi CSS (`table.rows` → style gần `logtbl`: sticky header, dot-status), không đổi JS logic | Thấp |
| Grid layout cũ (`.live-grid` 3 cột đơn giản) | `.shell` CSS grid (map col lớn + right panel 328px + log full-width dưới) | — | — | Port grid nhưng **sửa lỗi chồng layer** của bản gốc (`.rightpanel` grid-row:2/4 chồng lên `.logwrap` grid-row:3 cùng cột — bug thật trong demo cũ, không copy nguyên); grid mới: row1 topbar, row2 map+rightpanel cạnh nhau (row2 only), row3 log full-width | Thấp |

## Những gì giữ nguyên 100% (không đụng)

`backend/` toàn bộ (app.py, engine_adapter.py, replay_adapter.py, paths.py, test_engine.py,
requirements.txt) — port lần này chỉ là presentation layer. Toàn bộ logic trong `app.js` liên
quan tới: winner từ `selected_driver_id`/`is_selected` (P0.1), sequential step + `stepInFlight`
guard (P0.2), `setControlsForActiveRun` (P0.3), provenance key + engine-snapshot/dev-repo tách
biệt (P0.5/P1.7), `renderHistogram`/`renderLorenz` đọc field thật (P0.6), context-aware
lambda/forecast (P1.6), validate/n_drivers_actual disclosure (P1.5) — **chỉ đổi phần vẽ
map/DOM, không đổi phần gọi API hay điều kiện logic**.

## Leaflet dependency

CDN giống demo cũ: `unpkg.com/leaflet@1.9.4`. Basemap: CARTO light (`{s}.basemaps.cartocdn.com/light_all`)
— giữ nguyên, không có lý do kỹ thuật để đổi. Có fallback: nếu `window.L` undefined khi init
(CDN chặn/mất mạng), map div hiện message tĩnh thay vì crash toàn app; mọi control/KPI/table
khác vẫn hoạt động bình thường (không phụ thuộc Leaflet).

## Test bắt buộc sau port

1. `pytest backend/test_engine.py -v` — phải vẫn 18/18 pass (backend không đổi). **✅ Verified 21/08 — 18/18 pass.**
2. Regression P0.1 qua curl: `explain` vẫn trả `selected_driver_id` đúng, không bị đổi bởi
   việc sửa app.js. **✅ Verified — quét `/explain/{req_idx}` trên run thật tìm được case
   `selected_local_rank=2` (req 42, driver #0), xác nhận cả backend lẫn field UI mới đọc đúng.**
3. `node --check frontend/app.js` — cú pháp hợp lệ. **✅ Verified.**
4. curl full flow (create → step nhiều lần → explain → reset) qua server thật. **✅ Verified —
   đối chiếu từng field JSON thật (`drivers[]`, `assignments[].driver_start_lat/lon`,
   `declined_requests[]`, `infeasible_requests[]`, `income_histogram`, `lorenz`) khớp đúng
   những gì `app.js` mới đọc.**
5. Chưa test: mở trình duyệt thật xác nhận render/tương tác (môi trường build không có công cụ
   điều khiển trình duyệt) — người dùng cần tự mở `http://127.0.0.1:8731/` để xác nhận.
