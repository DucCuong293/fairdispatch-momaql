# Vietnamese UI Audit — Translation Inventory

Scope: `05_SanPham_Demo/{frontend,backend}` and `06_Deployed/{frontend,backend}`.
Method: exhaustive string-literal scan of `index.html` / `app.js` (quoted
literals matched against `[A-Za-z0-9 ,.!?&/#:%()+-]` with no Vietnamese
diacritics = English-leakage candidate), manual triage of every candidate,
then scripted exact-match replacement with a pre/post occurrence-count guard
(script aborts and writes nothing if a count doesn't match expectation —
no partial/silent edits). Backend Python files audited separately for
non-diacritic ASCII "Vietnamese" strings (a pre-existing pattern in this
codebase — messages already meant to be Vietnamese but typed without
accents).

## Totals

| Source | User-facing strings translated | Notes |
|---|---|---|
| `06_Deployed/frontend/index.html` | 120 | labels, buttons, tab names, table headers, tooltips, badges |
| `06_Deployed/frontend/app.js` | ~55 | tooltips, alert titles, phase labels, scoreBar labels, provenance strip |
| `05_SanPham_Demo/frontend/index.html` | 119 | same as 06, minus 1 line 06-only has (dataset row-count hint) |
| `05_SanPham_Demo/frontend/app.js` | ~55 | same set, adapted for 05's Validation-based provenance block |
| `06_Deployed/backend/app.py` | 12 | HTTPException details, FastAPI title, endpoint docstring |
| `06_Deployed/backend/engine_adapter.py` | 7 | validate_config errors, concurrent-step lock message |
| `05_SanPham_Demo/backend/app.py` | 12 | same set as 06 |
| `05_SanPham_Demo/backend/engine_adapter.py` | 8 | same set as 06 + FileNotFoundError setup message |
| `styles.css` (both) | 0 | no text content, only `▾`/`▸` glyphs |

## Key wording (baseline used, per the prompt's glossary)

| English | Vietnamese |
|---|---|
| Control Room | Trung tâm điều phối |
| Live Simulation | Mô phỏng trực tiếp |
| Compare Policies | So sánh chiến lược |
| Long-Horizon | Đánh giá dài hạn |
| Run History | Lịch sử lần chạy |
| New Run / Save Run | Tạo lần chạy mới / Lưu lần chạy |
| Step / Run / Pause / Reset | Bước / Chạy / Tạm dừng / Đặt lại |
| Why this driver? | Vì sao chọn tài xế này? |
| Verified Replay (badge) | KẾT QUẢ KIỂM CHỨNG |
| Live Engine (badge) | ENGINE TRỰC TIẾP |
| Service Health / Service Rate | Tình trạng phục vụ / Tỷ lệ phục vụ |
| Assigned / Declined / Infeasible | Đã gán chuyến / Bị từ chối / Không khả thi |
| Pickup ETA (Avg/P90/Worst) | ETA đón (trung bình/P90/lâu nhất) |
| Demand / Supply | Nhu cầu / Nguồn cung |
| Utility / Gini | Hiệu quả (tổng thể) / Gini (giữ nguyên, tên chỉ số thống kê) |
| Fairness | Công bằng (thu nhập) |
| Mean Income / Bottom 10% / Top 10% | Thu nhập trung bình / Nhóm 10% thấp nhất / Nhóm 10% cao nhất |
| Deadhead | Chạy rỗng |
| Final Test Evaluation View | Tập kiểm thử cuối đã chuẩn hóa |
| Full / No Forecast / No Fairness (ablation labels) | Đầy đủ / Không dự báo / Không công bằng |
| Immediate Utility / Future Zone Value / Fairness Adjustment | Giá trị tức thời / Giá trị khu vực tương lai / Điều chỉnh công bằng |

## Kept in English (per rule 1.1/2 — canonical names, technical identifiers)

`FairDispatch`, `MOMAQL`, `Greedy`, `Nearest`, `LAF`, `REASSIGN`, `NYC TLC
2013`, all JSON field names (`request_limit`, `n_drivers`, `policy`,
`utility`, `gini`, `run_id`, …), API routes (`/simulations`,
`/replay/ablation`, …), file names, SHA-256 hashes, `Seed`/`λ`/`γ`/`α`
technical parameter symbols, DOM element ids, JS variable/function names,
CSS class names, source-code comments.

## Applied to both products?

Yes — every translated string in 06's frontend/backend has a matching
translation applied to 05's equivalent string, with the known structural
differences between the two products preserved (05 still reads
`val.parquet` / "Tập xác thực"; 06 reads `test_eval.parquet` / "Tập kiểm
thử cuối đã chuẩn hóa"; 05 has no `/health` endpoint; 05's `/provenance`
strip shows `val.parquet` SHA-256 + dev-repo HEAD instead of row-count).

## Not touched (explicitly out of scope)

- `05_SanPham_Demo`'s canonical `engine/src/policies.py`,
  `engine/src/simulator.py` (algorithm code, not touched at all).
- Any JSON field *value* not rendered by the frontend (e.g.
  `replay_adapter.py`'s `"label": "VERIFIED TEST EXPERIMENT"` and
  `engine_source.note` in `/provenance` — confirmed via `grep` that
  `app.js` never reads `.label` or `.note` from these responses, so they
  are backend/audit metadata, not UI copy).
- `03_Source_Code_Va_Ket_Qua`, research reports, Q-table, Final Test
  artifacts, `test_eval.parquet` — untouched, per the task's explicit
  research-integrity constraint.
