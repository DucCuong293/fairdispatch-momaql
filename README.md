# FairDispatch — MOMAQL: Tái lập Định tính Fair Ride-Hailing Dispatch

Gói nộp cho mentor — tái lập định tính (qualitative trend replication) của
Kang et al. [2024], *"Long-term Fairness in Ride-Hailing Platform"*
(ECML PKDD 2024, [arXiv:2407.17839](https://arxiv.org/abs/2407.17839)).

Đây là repo chính thức, bản duy nhất:
**https://github.com/DucCuong293/fairdispatch-momaql**
Nội dung sắp xếp theo loại tài liệu để mentor dễ mở đúng thứ cần xem.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `01_Tai_Lieu_Ky_Thuat/` | `Technical_Documentation.docx` — tài liệu kỹ thuật cho kỹ sư: kiến trúc, data contract, module spec, lệnh chạy lại, reproducibility package. |
| `02_Bao_Cao_Du_An/` | `Bao_Cao_Nghien_Cuu_FairDispatch_MOMAQL.docx` — báo cáo nghiên cứu/thực nghiệm cho mentor: claim-by-claim assessment, kết quả chính, discrepancy analysis. |
| `03_Source_Code_Va_Ket_Qua/` | Toàn bộ mã nguồn Python (simulator, policies, 12 script thực nghiệm), toàn bộ kết quả thật trong `reports/`, bảng Q đã huấn luyện, và 2 bản LaTeX paper (EN/VI) kèm PDF đã compile. **Không gồm** `data/*.parquet` (dữ liệu thô, quá lớn để đóng gói — xem SHA-256 trong `reports/dataset_checksums.json` để xác minh). |
| `04_Slide_Thuyet_Trinh/` | Slide thuyết trình bảo vệ (script, speaker notes, style) — xem `05_SanPham_Demo/` cho sản phẩm demo tương tác thật. |

Cả 2 file DOCX đều tự chứa (ảnh nhúng sẵn trong file, không cần file rời).
Mọi hình ảnh trong 2 tài liệu đều là biểu đồ thật vẽ từ số liệu trong
`reports/*.csv`, hoặc sơ đồ khối tự vẽ mô tả pipeline thật — không dùng
ảnh AI-generated.

## Tóm tắt kết quả chính (số thật, trung bình 5 seed)

| Chính sách | Utility ($) | Gini |
|---|---:|---:|
| **MOMAQL** | **1.422.441** | **0,204** |
| Greedy | 1.001.551 | 0,531 |
| Nearest | 789.444 | 0,430 |
| LAF | 766.265 | 0,002 |
| Exact REASSIGN | 648.160 | 0,417 |

Đánh giá đầy đủ theo từng claim của paper (Reproduced / Partially
Reproduced / Not Reproduced), cả trên Validation lẫn trên một
**Final Held-out Test** chạy sau khi mọi cấu hình đã đóng băng
(13/13 phát hiện tiền xác định generalize đúng hướng sang Test) —
xem Mục 9 (Final Held-out Test Evaluation) và Mục 10 (Replication
Assessment) của
`02_Bao_Cao_Du_An/Bao_Cao_Nghien_Cuu_FairDispatch_MOMAQL.docx`.

---

*AI Research Internship, Ride Allocation Group. Đóng gói: tháng 8, 2026.*
