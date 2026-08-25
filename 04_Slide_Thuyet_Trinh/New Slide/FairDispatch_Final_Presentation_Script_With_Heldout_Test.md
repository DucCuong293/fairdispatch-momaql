# KỊCH BẢN THUYẾT TRÌNH FAIRDISPATCH

> Dùng cho deck **24 slide, một bộ duy nhất** (`index.html`) — không còn Phụ lục, không còn
> file appendix.html trong luồng trình bày. Storyline: Bài toán và mục tiêu → Hệ thống
> FairDispatch → Cách điều phối và chỉ số đánh giá → Kết quả thực nghiệm → Demo sản phẩm →
> Giới hạn và kết luận → Cảm ơn.
> Khán giả: anh quản lý App/Product trước tiên, cộng mentor nghiên cứu + người không chuyên.
> Nguồn số liệu: `final_test/FINAL_TEST_MENTOR_SUMMARY.md`, `test_claim_assessment.csv`,
> `validation_vs_test.csv`, `reports/fleet_scale_results.csv`, `05_SanPham_Demo/README.md` —
> không có số liệu nào gõ tay không đối chiếu.

---

## 0. Giải thích đơn giản các khái niệm

- **Utility (hiệu quả tổng thể)**: tổng hiệu quả kinh tế / tổng thu nhập hệ thống tạo ra cho
  tài xế.
- **Fairness (công bằng thu nhập)**: mức độ đồng đều thu nhập giữa các tài xế.
- **Gini (độ chênh lệch thu nhập)**: chỉ số đo chênh lệch, **càng thấp càng công bằng**.
- **Validation / Test**: Validation là nơi phát triển, chọn cấu hình; Test là tập tách riêng,
  chỉ mở ra kiểm tra một lần sau khi mọi thứ đã chốt — giống bài thi cuối kỳ.
- **Demo**: công cụ giúp người ra quyết định thử nghiệm và so sánh trước khi áp dụng thật,
  không phải hệ thống tự vận hành production.

---

## 1. Core message (mở đầu, nhắc lại ở Kết luận)

> "FairDispatch là một hệ thống mô phỏng và đánh giá chiến lược điều phối, giúp so sánh
> hiệu quả và công bằng trước khi áp dụng một chiến lược điều phối thật. Có dữ liệu, bộ mô
> phỏng, 5 chiến lược điều phối, bộ đánh giá kết quả, kiểm chứng trên tập Test chưa từng dùng,
> và một demo bản đồ chạy được thật."

**Giải thích "Test giống bài thi cuối":** "Trong lúc phát triển, em chỉ dùng Validation để
chọn cấu hình. Test bị khóa lại từ đầu. Sau khi mọi quyết định đã chốt, em mới mở Test ra chạy
đúng một lần, không quay lại sửa gì sau khi thấy kết quả."

**Giải thích "13/13 giữ cùng chiều" khác "mọi tuyên bố của paper đều đúng":** "'13/13' là câu mô
tả thuần túy: 13 phát hiện trên Validation có lặp lại đúng hướng khi sang Test không — chỉ nói
về độ ổn định. Còn việc từng tuyên bố cụ thể của paper có khớp hay không là đánh giá riêng — ví
dụ rõ nhất là forecast cải thiện fairness dài hạn: paper nói có, nhưng em quan sát ngược lại,
nhất quán trên cả hai split. Chính discrepancy đó mới là thứ giữ cùng chiều, không phải tuyên
bố gốc của paper."

---

## 2. Kịch bản theo từng slide (24 slide)

Quy ước: **[Ngắn]** = nói trong bản 10–15 phút. **[Đầy đủ]** = thêm chi tiết cho bản 20–25 phút.

### Phần 1 — Bài toán và mục tiêu (slide 1–3)

**Slide 1 — Title.** "Em trình bày FairDispatch — hệ thống mô phỏng và đánh giá chiến lược
điều phối cân bằng hiệu quả và công bằng. Dữ liệu NYC Taxi 2013, thuật toán MOMAQL, có demo mô
phỏng trực quan."

**Slide 2 — Nội dung trình bày.** "6 phần: Bài toán và mục tiêu, Hệ thống FairDispatch, Cách
điều phối và chỉ số đánh giá, Kết quả thực nghiệm, Demo sản phẩm, Giới hạn và kết luận."

**Slide 3 — Bài toán.** "Nền tảng gọi xe cần phục vụ nhiều chuyến và tối ưu hiệu quả. Nhưng
nếu chỉ ưu tiên chuyến có lợi nhất, thu nhập tài xế có thể bị lệch. Bài toán: vừa giữ hiệu quả
hệ thống, vừa hạn chế chênh lệch thu nhập tài xế."

### Phần 2 — Hệ thống FairDispatch (slide 4–6)

**Slide 4 — Là gì.** "FairDispatch là một hệ thống hỗ trợ đánh giá chiến lược điều phối chuyến
xe — không phải app khách hàng, không phải app tài xế, không phải hệ thống production thay
Grab/XanhSM. Nó là công cụ mô phỏng, công cụ so sánh thuật toán, công cụ giải thích quyết định,
và một bản demo trực quan."

**Slide 5 — Phục vụ ai.** "3 nhóm dùng: người quản lý vận hành, kỹ sư điều phối, nhóm dữ
liệu/nghiên cứu. Giá trị: mô phỏng trước khi áp dụng thật, so sánh hiệu quả và công bằng, xem
lý do hệ thống chọn tài xế, kiểm thử trên dữ liệu lịch sử."

**Slide 6 — 5 phần chính.** "Dữ liệu và kịch bản, bộ mô phỏng điều phối, các chiến lược điều
phối, bộ đánh giá kết quả, giao diện demo trực quan — mỗi phần map thẳng vào code thật."

### Phần 3 — Cách điều phối và chỉ số đánh giá (slide 7–11)

**Slide 7 — Kiến trúc tổng thể.** "Từ dữ liệu NYC Taxi, qua xử lý vùng/thời gian/khoảng cách,
bộ mô phỏng, chiến lược điều phối, ghép tài xế–chuyến xe, chỉ số đánh giá, tới demo bản đồ."

**Slide 8 — Bộ mô phỏng hoạt động thế nào.** "Gom request theo cửa sổ 60 giây, chỉ xét tài xế
tới đón được trong tối đa 10 phút, ghép bằng Hungarian Assignment — thuật toán ghép tối ưu.
Sau mỗi chuyến, hệ thống cập nhật vị trí, thu nhập, trạng thái tài xế."

**Slide 9 — 5 chiến lược so sánh.** "Greedy ưu tiên chuyến có lợi cao, Nearest ưu tiên tài xế
gần khách nhất, LAF ưu tiên tài xế thu nhập thấp, REASSIGN là baseline tái dựng theo paper,
MOMAQL kết hợp cả hiệu quả hiện tại, giá trị tương lai, và công bằng."

**Slide 10 — MOMAQL quyết định thế nào.** "Lợi ích chuyến hiện tại, cộng giá trị khu vực sau
khi trả khách, cộng điều chỉnh theo thu nhập tài xế, bằng điểm ghép tài xế–chuyến xe. Nếu hai
chuyến gần giống nhau, hệ thống ưu tiên chuyến giúp cân bằng thu nhập tốt hơn."

**Slide 11 — Chỉ số đánh giá.** "Không chỉ đo doanh thu: Utility càng cao càng tốt, Gini càng
thấp càng công bằng, Variance/CV càng thấp càng tốt, số chuyến phục vụ phản ánh nhu cầu, và
Deadhead — quãng đường chạy rỗng — càng thấp càng tốt."

### Phần 4 — Kết quả thực nghiệm (slide 12–20)

**Slide 12 — Dữ liệu và kiểm thử.** "Train 912.375 chuyến để học giá trị khu vực, Validation
195.508 chuyến để phát triển, Test 195.510 chuyến để kiểm tra cuối. Test không dùng để chọn
tham số."

**Slide 13 — Kết quả 1.** "MOMAQL đạt Utility 1.422.441, Gini 0,2037 trên Validation — điểm
cân bằng tốt. LAF công bằng nhất nhưng Utility thấp; Greedy/Nearest kém cân bằng hơn. MOMAQL là
điểm cân bằng, không phải chiến lược tốt nhất ở mọi chỉ số."

**Slide 14 — Kết quả 2.** "Forecast giúp Utility +22,4% trên Validation — khi hệ thống nhìn
trước khu vực tài xế sẽ đến, quyết định dài hạn tốt hơn. Nhưng No Forecast lại có Gini thấp
hơn, tức công bằng hơn trong thí nghiệm này."

**Slide 15 — Kết quả 3.** "Look-ahead — nhìn trước tương lai — không giúp nhiều ngay lập tức:
ngày 21 mới +5,1%, nhưng đến ngày 37 đã +20,2%. Nếu chỉ chạy thử vài ngày đầu thì khó thấy lợi
ích."

**Slide 16 — Fleet-scale.** "Khi đội xe khan hiếm, dự báo tương lai có giá trị hơn: 100 tài xế
lợi ích +41,9%, 200 tài xế +23,3%, 400 tài xế gần như bằng 0. Forecast hữu ích nhất trong bối
cảnh thiếu tài xế hoặc nhu cầu cao."

**Slide 17 — Kiểm tra cuối trên Test.** "Sau khi chốt cấu hình, em chạy lại một lần trên Test —
dữ liệu chưa dùng để phát triển thuật toán. 13/13 xu hướng chính tiếp tục giữ cùng chiều."

**Slide 18 — Test: điểm cân bằng ổn định.** "Test cho Utility 1.454.053, Gini 0,2011 — gần với
Validation. Điểm cân bằng của MOMAQL không phải chỉ xuất hiện ngẫu nhiên."

**Slide 19 — Test: forecast vẫn giúp Utility.** "Full vs No Forecast: Validation +22,4%, Test
+17,1% — cùng hướng. No Forecast vẫn công bằng hơn Full trên cả hai split — forecast giúp hiệu
quả, nhưng chưa tái lập được việc forecast cải thiện fairness."

**Slide 20 — Test dài hạn.** "Ngày 21: Validation +5,1%, Test +1,2%. Ngày 37: Validation
+20,2%, Test +13,4%. Xu hướng dài hạn generalize — giữ cùng chiều — sang Test."

### Phần 5 — Demo sản phẩm (slide 21)

**Slide 21 — DEMO.** "Mô phỏng trực tiếp trên bản đồ NYC Taxi validation slice: driver, request,
tuyến đón/trả khách. Có thể Run/Pause/Step và chỉnh tốc độ. Có Why This Driver để xem lý do
chọn tài xế, và Compare để so sánh Full/No Forecast/No Fairness." (Sau câu này, chuyển sang
demo trực tiếp — không cần nói thêm nhiều bằng lời.)

### Phần 6 — Giới hạn và kết luận (slide 22–23)

**Slide 22 — Giới hạn và hướng phát triển.** "Dữ liệu NYC Taxi 2013, không phải dữ liệu gốc
của paper. GSM/XanhSM chưa có dữ liệu thực để backtest đầy đủ. Simulator vẫn là mô phỏng, chưa
phải production. Một số claim fairness chưa tái lập được. Chỉ kiểm thử với số seed giới hạn.
Hướng tới: chạy trên dữ liệu GSM/XanhSM nếu được cung cấp, bổ sung ràng buộc vận hành thật, thử
A/B test offline, cải thiện forecast và mục tiêu công bằng."

**Slide 23 — Kết luận.** (đọc mục 3 dưới)

**Slide 24 — Cảm ơn.** "Em xin cảm ơn anh và mọi người đã lắng nghe. Em sẵn sàng demo trực
tiếp và trả lời câu hỏi."

---

## 3. Đoạn Kết luận (đọc ở slide 23)

> "Sáu điều đã đạt được: một pipeline đầu-cuối từ dữ liệu chuyến xe đến mô phỏng điều phối; so
> sánh 5 chiến lược điều phối trên cùng bộ mô phỏng và chỉ số; MOMAQL cho điểm cân bằng tốt
> giữa Utility và Gini — Validation Utility 1.422.441/Gini 0,2037, Test Utility
> 1.454.053/Gini 0,2011; forecast giúp tăng Utility — Validation +22,4%, Test +17,1%; 13/13 xu
> hướng chính giữ cùng chiều trên Test; và một demo bản đồ để minh họa, giải thích quyết định
> điều phối.
>
> Kết luận khoa học, nói ngắn: **Strong Partial Trend Replication with held-out temporal
> support** — nhiều phát hiện quan trọng giữ đúng hướng khi sang Test, nhưng không phải mọi
> tuyên bố của paper gốc đều được tái lập đầy đủ."

---

## 4. Cụm từ cần nhớ

- "13/13 xu hướng chính giữ cùng chiều trên Test" — KHÔNG nói "6/6 paper claims reproduced".
- "No Forecast công bằng hơn Full trên cả Validation và Test" — KHÔNG nói "Forecast improves
  fairness".
- "MOMAQL là điểm cân bằng, không phải chiến lược tốt nhất mọi chỉ số."
- "Demo là công cụ mô phỏng, không phải hệ thống production."
- "Strong Partial Trend Replication with held-out temporal support" — verdict cuối, nguyên
  văn.

---

## 5. Q&A dự kiến

**Q1. FairDispatch phục vụ ai, giải quyết gì?**
"Phục vụ người quản lý vận hành, kỹ sư điều phối, nhóm dữ liệu/nghiên cứu — giúp mô phỏng, so
sánh và giải thích chiến lược điều phối trước khi áp dụng thật."

**Q2. Sản phẩm demo có deploy thật không?**
"Chạy local, engine là thật — không mock. Chưa deploy public vì đây là prototype nội bộ cho
team vận hành/nghiên cứu, chưa phải sản phẩm khách hàng cuối."

**Q3. Test có bị dùng để chọn cấu hình không?**
"Không. Cấu hình được chốt trước khi Test chạy. Sau khi thấy kết quả, không sửa lại gì."

**Q4. 13/13 giữ cùng chiều nghĩa là tái lập paper hết rồi à?**
"Không. 13/13 chỉ nói 13 phát hiện trên Validation lặp lại đúng hướng khi sang Test — kể cả
những phát hiện là discrepancy với paper. C4 nằm trong số đó nhưng vẫn 'không thấy xu hướng
này' vì chính discrepancy mới là thứ giữ cùng chiều, không phải tuyên bố gốc của paper."

**Q5. Cuối cùng có nên tin dùng MOMAQL không?**
"Ở mức điểm vận hành cân bằng đã kiểm chứng hai lần (Validation + Test) — không phải giải pháp
hoàn hảo mọi mặt. Muốn công bằng tuyệt đối thì LAF là lựa chọn khác, đánh đổi Utility thấp hơn
nhiều."

**Q6. Fleet-scale nghĩa là gì, ứng dụng ra sao?**
"Khi đội xe ít so với nhu cầu, forecast giúp Utility tăng rất mạnh (100 tài xế +41,9%). Khi đội
xe đã đủ (400 tài xế), lợi ích gần như biến mất. Nên forecast hữu ích nhất khi nguồn cung tài
xế đang thiếu."

**Q7. Nếu triển khai thật thì cần thêm gì?**
"Dữ liệu realtime thay vì replay lịch sử, hạ tầng chịu tải nhiều request/giây, và một vòng A/B
test thật trên một phần nhỏ traffic trước khi áp dụng toàn hệ thống."

---

## 6. Hai bản trình bày

### Bản ngắn (10–15 phút)

Trình bày toàn bộ **24 slide** theo đúng thứ tự — deck đã được rút gọn đủ để trình bày hết
trong 10–15 phút mà không cần bỏ slide nào. Nếu thiếu thời gian, có thể lướt nhanh Slide 11
(chỉ số đánh giá) vì nội dung đã tự giải thích trên slide.

### Bản đầy đủ (20–25 phút)

Trình bày toàn bộ 24 slide, dùng thêm phần giải thích chi tiết ở mục 2 cho mỗi slide, và mở
rộng phần Q&A ở mục 5 nếu mentor/quản lý hỏi sâu.

---

## 7. Nguồn số liệu đã đối chiếu

`final_test/FINAL_TEST_MENTOR_SUMMARY.md`, `final_test/test_claim_assessment.csv`,
`final_test/validation_vs_test.csv`, `reports/fleet_scale_results.csv`,
`05_SanPham_Demo/README.md`, `05_SanPham_Demo/OPERATOR_CONTROL_ROOM_PLAN.md`,
`04_Slide_Thuyet_Trinh/index.html` (deck 24 slide, một bộ duy nhất, không còn Phụ lục). Không
số liệu nào gõ từ trí nhớ mà không đối chiếu lại nguồn trên. Không có chiến lược nào được chạy
lại để viết kịch bản này.
