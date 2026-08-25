# Speaker Notes — FairDispatch (24 slide, một bộ duy nhất)

Deck = `index.html`, đúng **24 slide**, toàn bộ tiếng Việt. Không còn Phụ lục, không còn
file appendix.html trong luồng trình bày — mọi câu hỏi sâu (công thức, per-seed, sweep) trả lời
trực tiếp bằng lời hoặc mở source code, không lật sang file khác.

Bản này (`New Slide/`) bổ sung chart/KPI/diagram/screenshot thật ở 13 slide (1, 3, 6, 8, 9,
12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23) — số liệu tự tính read-only qua
`scripts/compute_operational_metrics.py` từ artifact có sẵn, không rerun experiment. Xem
`VISUAL_DATA_AUDIT.md` để biết nguồn từng con số mới.

## Phần 1 — Bài toán và mục tiêu (slide 3)

**Slide 1 — Title.** "FairDispatch — hệ thống mô phỏng và đánh giá chiến lược điều phối cân
bằng hiệu quả và công bằng. Dữ liệu NYC Taxi 2013, thuật toán MOMAQL, có demo mô phỏng trực
quan."

**Slide 2 — Nội dung trình bày.** 6 phần: Bài toán và mục tiêu, Hệ thống FairDispatch, Cách
điều phối và chỉ số đánh giá, Kết quả thực nghiệm, Demo sản phẩm, Giới hạn và kết luận.

**Slide 3 — Bài toán.** "Nền tảng gọi xe cần phục vụ nhiều chuyến và tối ưu hiệu quả, nhưng
nếu chỉ ưu tiên chuyến có lợi nhất thì thu nhập tài xế có thể bị lệch. Bài toán: vừa giữ hiệu
quả, vừa hạn chế chênh lệch thu nhập."

## Phần 2 — Hệ thống FairDispatch (slide 4-6)

**Slide 4 — Là gì.** Hệ thống hỗ trợ đánh giá chiến lược điều phối — không phải app khách hàng,
không phải app tài xế, không phải hệ thống production thay Grab/XanhSM.

**Slide 5 — Phục vụ ai.** 3 nhóm: người quản lý vận hành, kỹ sư điều phối, nhóm dữ liệu/nghiên
cứu. Giá trị: mô phỏng trước khi áp dụng, so sánh hiệu quả–công bằng, xem lý do chọn tài xế,
kiểm thử trên dữ liệu lịch sử.

**Slide 6 — 5 phần chính.** Dữ liệu và kịch bản, bộ mô phỏng điều phối, các chiến lược điều
phối, bộ đánh giá kết quả, giao diện demo trực quan — mỗi phần map thẳng vào code thật.

## Phần 3 — Cách điều phối và chỉ số đánh giá (slide 7-11)

**Slide 7 — Kiến trúc tổng thể.** 3 khối: DỮ LIỆU (NYC TLC 2013 đã làm sạch sẵn ở thượng
nguồn → lọc Manhattan + chất lượng → gán 67 zone TLC + giờ → chia Train/Validation/Test),
DISPATCH ENGINE (bộ mô phỏng batch 60 giây → 5 chiến lược → Hungarian Assignment), OUTPUT
(Utility/Fairness → demo bản đồ). Chi tiết tiền xử lý xem ở Slide 12.

**Slide 8 — Bộ mô phỏng hoạt động thế nào.** 4 KPI lớn trên slide: 60 giây/batch, ≤600 giây
pickup ETA, 200 tài xế, 67 zone — đọc thẳng từ số trên slide, không cần nói lại bằng lời. Ghép
bằng Hungarian Assignment (thuật toán ghép tối ưu), cập nhật trạng thái sau mỗi chuyến.

**Slide 9 — 5 chiến lược so sánh.** Greedy (ưu tiên fare cao nhất), Nearest (ưu tiên pickup ETA
ngắn nhất), LAF (ưu tiên tài xế thu nhập thấp hơn trung bình), REASSIGN (ghép tối ưu theo lợi
ích ròng hiện tại — fare trừ deadhead cost — chưa nhìn tương lai, chưa cân bằng thu nhập),
MOMAQL (kết hợp cả ba yếu tố). Trục Gini bên dưới bảng xếp đúng thứ tự công bằng thật (LAF
công bằng nhất, Greedy kém nhất) — không phải sơ đồ minh họa chủ quan.

**Slide 10 — MOMAQL quyết định thế nào.** Lợi ích hiện tại + giá trị khu vực tương lai + điều
chỉnh thu nhập = điểm ghép. Nếu hai chuyến gần giống nhau, hệ thống ưu tiên chuyến giúp cân
bằng thu nhập tốt hơn.

**Slide 11 — Chỉ số đánh giá.** Utility (hiệu quả tổng thể), Gini (độ chênh lệch thu nhập),
Variance/CV, số chuyến phục vụ, Deadhead (quãng đường chạy rỗng).

## Phần 4 — Kết quả thực nghiệm (slide 12-20)

**Slide 12 — Dữ liệu và kiểm thử (nói khoảng 40-60 giây).** "Bộ dữ liệu em dùng là NYC TLC
2013, gồm hơn 1,3 triệu chuyến từ tháng 1 tới cuối tháng 8. Mỗi chuyến không được đưa thẳng
vào thuật toán — em phải chuẩn hóa nó thành một request mà simulator hiểu được: thời điểm
xuất phát, khu vực đón, khu vực trả, thời lượng/fare và các trường cần thiết khác. Sau tiền
xử lý, dữ liệu được sắp theo thời gian và chia liên tục thành Train, Validation và Test chứ
không random. Train dùng để học giá trị khu vực, Validation dùng để phát triển và đánh giá,
Test để kiểm tra cuối." Cleaning/feature step thật (đọc từ code, không suy đoán): lọc
`manhattan_both=true AND quality_flag_bitset=0` (2 cờ có sẵn từ pipeline thượng nguồn, không
tự tính lại ở đây) → lấy mẫu tỉ lệ theo tháng ~1,3tr dòng → sắp theo `pickup_ts` → chia
70/15/15. `pickup_hour`/`dropoff_hour` là 2 trường DUY NHẤT tự tính trong repo này
(`common_loader.py`), từ epoch giây thật. Chi tiết đầy đủ: `DATA_PIPELINE_AUDIT.md`. Train 912.375, Validation 195.508, Test 195.510. Thanh
timeline cho thấy 3 tập nối liền theo thời gian thật trong 2013 (Train 01/01–13/06, Validation
13/06–21/07, Test 21/07–31/08) — không phải random split. Test không dùng để chọn tham số.

**Slide 13 — Kết quả 1.** MOMAQL Validation Utility 1.422.441, Gini 0,2037 — điểm cân bằng,
không phải chiến lược tốt nhất mọi chỉ số. LAF công bằng nhất nhưng Utility thấp. Nếu cần ví
dụ cụ thể hơn Gini: tài xế P90 ở MOMAQL chỉ kiếm gấp ~2,3 lần P10 (so với ~21 lần ở Greedy).

**Slide 14 — Kết quả 2.** Forecast +22,4% Utility trên Validation. Nhưng No Forecast lại có
Gini thấp hơn — công bằng hơn trong thí nghiệm này. Slide có thêm variant thứ ba No Fairness:
bỏ hẳn thành phần công bằng làm Utility giảm mạnh (898k) **và** bất bình đẳng tăng mạnh (Gini
0,45) — xấu cả hai trục, không phải đánh đổi có lợi.

**Slide 15 — Kết quả 3.** Look-ahead (nhìn trước tương lai): ngày 21 +5,1%, ngày 37 +20,2% —
lợi ích rõ dần theo thời gian, không thấy ngay ở vài ngày đầu.

**Slide 16 — Fleet-scale (mới).** 100 tài xế +41,9%, 200 tài xế +23,3%, 400 tài xế +0,01% —
forecast có giá trị lớn nhất khi đội xe khan hiếm, gần biến mất khi dư thừa nguồn cung. Cơ chế:
service rate (Full) đi từ 59,2% (100 tài xế) lên 78,1% (200) và bão hòa 99,3% (400) — fleet đủ
rồi thì forecast hết chỗ tối ưu thêm.

**Slide 17 — Kiểm tra cuối trên Test.** Chạy lại sau khi chốt cấu hình, trên dữ liệu chưa dùng
để phát triển thuật toán — 13/13 xu hướng chính giữ cùng chiều, chia đều cả 3 nhóm: Baseline
5/5, Ablation 4/4, Long-horizon 4/4 — không phải một nhóm yếu bị trung bình che đi. Nói ngắn,
không cần đi sâu freeze protocol/hash.

**Slide 18 — Test: điểm cân bằng ổn định.** Test Utility 1.454.053, Gini 0,2011 — gần
Validation, không phải ngẫu nhiên. Thêm 2 điểm: Service rate 77,9%→79,7% (MOMAQL phục vụ cao
hơn hẳn 4 chiến lược còn lại, nên Utility cao không phải nhờ bỏ khách); Deadhead trung bình
$0,60/chuyến trên Test, gần bằng REASSIGN thuần hiệu quả, thấp hơn Greedy/LAF.

**Slide 19 — Test: forecast vẫn giúp Utility.** Test +17,1% (so với Validation +22,4%). No
Forecast vẫn công bằng hơn Full trên cả hai split.

**Slide 20 — Test dài hạn.** Ngày 21: Val +5,1%/Test +1,2%. Ngày 37: Val +20,2%/Test +13,4%.
Generalize = giữ cùng xu hướng khi chuyển sang dữ liệu mới.

## Phần 5 — Demo sản phẩm (slide 21)

**Slide 21 — DEMO.** Ảnh bên trái là screenshot THẬT chụp từ sản phẩm đang chạy (không phải
mockup) — dùng luôn để mở đầu, nói ngắn rồi demo trực tiếp: bản đồ NYC Taxi validation slice,
Run/Pause/Step, chỉnh tốc độ, Why This Driver (xem lý do chọn tài xế), Compare Full/No
Forecast/No Fairness.

## Phần 6 — Giới hạn và kết luận (slide 22-23)

**Slide 22 — Giới hạn và hướng phát triển.** Dữ liệu 2013 không phải gốc paper, GSM/XanhSM
chưa có dữ liệu thật, simulator chưa phải production, một số claim fairness chưa tái lập, seed
giới hạn. Hướng tới: dữ liệu GSM/XanhSM, ràng buộc vận hành thật, A/B test offline, cải thiện
forecast/fairness.

**Slide 23 — Kết luận.** 6 ý: pipeline đầu-cuối, so sánh 5 chiến lược, MOMAQL điểm cân bằng
(số liệu Validation/Test), forecast tăng Utility (Val/Test), 13/13 xu hướng giữ cùng chiều, có
demo bản đồ. Câu cuối nhỏ, không phải headline: "Strong Partial Trend Replication with
held-out temporal support."

**Slide 24 — Cảm ơn.** Cảm ơn người nghe, sẵn sàng demo trực tiếp và trả lời câu hỏi.

---

## Cụm từ cần nhớ

- "13/13 xu hướng chính giữ cùng chiều trên Test" — KHÔNG nói "6/6 paper claims reproduced".
- "No Forecast công bằng hơn Full" — KHÔNG nói "Forecast improves fairness".
- "MOMAQL là điểm cân bằng, không phải chiến lược tốt nhất mọi chỉ số."
- Verdict cuối, nguyên văn: "Strong Partial Trend Replication with held-out temporal support."

## Q&A dự kiến (không đổi so với bản trước)

1. FairDispatch phục vụ ai? → Slide 5.
2. Demo có deploy thật không? → Chạy local, engine thật, chưa deploy public.
3. Test có bị dùng để chọn cấu hình không? → Không, chốt trước khi chạy Test.
4. 13/13 nghĩa là tái lập hết paper? → Không, chỉ là xu hướng giữ cùng chiều — không phải mọi
   tuyên bố của paper gốc đều đúng xu hướng (ví dụ forecast cải thiện fairness thì không).
5. Nên tin dùng MOMAQL không? → Điểm cân bằng đã kiểm chứng hai lần, không phải giải pháp hoàn
   hảo mọi mặt; muốn công bằng tuyệt đối thì LAF đánh đổi Utility thấp hơn.
