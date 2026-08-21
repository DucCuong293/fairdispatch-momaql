# KỊCH BẢN THUYẾT TRÌNH FAIRDISPATCH
## Bản nói tự nhiên, dễ hiểu cho cả người có và không có chuyên môn

> **Dùng cho deck 32 slide FairDispatch đã chốt.**  
> Mục tiêu của kịch bản này không phải để đọc như văn bản, mà để giúp người trình bày biết **mỗi slide cần nói gì, nói theo thứ tự nào, nhấn vào đâu và chuyển sang slide tiếp theo ra sao**.

---

# Cách dùng kịch bản

- Không cần học thuộc từng câu.
- Hãy nhớ **ý chính + 1–2 con số quan trọng** của mỗi slide.
- Khi nói, ưu tiên từ đơn giản trước, thuật ngữ kỹ thuật nói sau.
- Nếu khán giả không chuyên, luôn giải thích thuật ngữ ngay lần đầu xuất hiện.
- Không cần đọc tất cả chữ đang có trên slide.
- Những slide chứa bảng chi tiết có thể nói nhanh hơn, chỉ chỉ vào phần cần thiết.

Một số quy ước nên giữ xuyên suốt:

- **Utility**: có thể hiểu đơn giản là tổng hiệu quả kinh tế / tổng thu nhập mà hệ thống tạo ra.
- **Fairness**: mức độ công bằng giữa các tài xế.
- **Gini**: chỉ số đo mức chênh lệch thu nhập, **càng thấp càng công bằng**.
- **Forecast / Look-ahead**: sử dụng thông tin tương lai để hỗ trợ quyết định hiện tại.
- **Full**: cấu hình đầy đủ, có cả look-ahead và fairness.
- **No Forecast**: bỏ phần nhìn trước tương lai.
- **No Fairness**: bỏ thành phần ưu tiên công bằng.
- **Trend replication**: tái lập xu hướng/kết luận định tính của paper, không yêu cầu số liệu giống hệt.

---

# PHẦN MỞ ĐẦU

## Slide 1 — FairDispatch

### Mục tiêu
Giới thiệu bài toán, paper và phạm vi nghiên cứu ngay từ đầu.

### Kịch bản nói

“Em xin trình bày dự án **FairDispatch**.

Dự án này được thực hiện dựa trên paper *Long-term Fairness in Ride-Hailing Platform* của Kang và cộng sự.

Bài toán mà paper quan tâm là một vấn đề khá thực tế trong các nền tảng gọi xe: khi hệ thống phân chuyến cho tài xế, nếu chúng ta chỉ cố tối đa hóa doanh thu hoặc hiệu quả ngay tại thời điểm hiện tại thì về lâu dài có thể xuất hiện tình trạng một nhóm tài xế liên tục nhận được các chuyến tốt, trong khi một nhóm khác kiếm được ít hơn.

Vì vậy paper đặt ra câu hỏi: liệu có thể điều phối chuyến xe sao cho vừa giữ được hiệu quả kinh tế, vừa hạn chế chênh lệch thu nhập giữa các tài xế trong thời gian dài hay không?

Mục tiêu của em không phải làm cho kết quả giống paper từng con số. Em thực hiện theo hướng **trend replication**, tức là xem những xu hướng và kết luận quan trọng của paper có xuất hiện lại trong hệ thống em xây dựng hay không.”

### Chuyển slide

“Trước khi đi vào chi tiết, em xin trình bày nhanh cấu trúc của bài.”

---

## Slide 2 — Agenda

### Kịch bản nói

“Bài trình bày gồm 5 phần chính.

Phần đầu tiên, em nói về bài toán và phạm vi mà em replicate.

Phần hai là cách hệ thống được xây dựng và cách em thiết kế thực nghiệm.

Phần ba là phần quan trọng nhất: các kết quả thực nghiệm và phân tích.

Phần bốn là tổng hợp xem từng claim của paper được tái lập đến mức nào.

Cuối cùng là phần demo sản phẩm.”

### Chuyển slide

“Đầu tiên, chúng ta cần hiểu tại sao bài toán fairness lại xuất hiện trong ride-hailing.”

---

# PHẦN 1 — BÀI TOÁN & PHẠM VI TÁI LẬP

## Slide 3 — Tối ưu hiệu quả tức thời có thể tạo chênh lệch thu nhập

### Kịch bản nói

“Ta có thể hình dung rất đơn giản như thế này.

Giả sử có ba tài xế A, B và C.

Nếu mỗi lần hệ thống chỉ chọn tài xế nào giúp chuyến hiện tại tạo ra lợi ích cao nhất thì có thể tài xế A thường xuyên được nhận những chuyến tốt hơn.

Sau nhiều giờ hoặc nhiều ngày, tổng thu nhập của A sẽ cao hơn B và C khá nhiều.

Ở đây có hai khái niệm chính.

**Utility** là tổng hiệu quả hoặc tổng giá trị kinh tế mà hệ thống tạo ra.

Còn **Fairness** là mức độ đồng đều của phần utility đó giữa các tài xế.

Nói đơn giản, một hệ thống có thể kiếm được rất nhiều tiền, nhưng nếu phần lớn lợi ích tập trung vào một số ít tài xế thì hệ thống đó chưa chắc đã công bằng.”

### Điểm cần nhấn mạnh

“Fairness ở đây không có nghĩa mọi người bắt buộc phải nhận đúng bằng nhau, mà là tránh để khoảng cách thu nhập trở nên quá lớn.”

### Chuyển slide

“Vấn đề tiếp theo là vì sao chỉ nhìn chuyến hiện tại lại chưa đủ.”

---

## Slide 4 — Vì sao Look-ahead quan trọng?

### Kịch bản nói

“Một điểm rất quan trọng trong bài toán này là: **một chuyến xe không kết thúc tác động của nó khi khách xuống xe**.

Ví dụ một tài xế nhận chuyến từ khu vực A sang khu vực B.

Sau khi hoàn thành chuyến, tài xế không còn ở A nữa mà đang ở B.

Nếu B là khu vực sắp có nhu cầu gọi xe cao, thì chuyến hiện tại vô tình đặt tài xế vào một vị trí rất tốt cho các chuyến tiếp theo.

Ngược lại, nếu tài xế bị đưa tới một khu vực ít khách, thu nhập tương lai có thể bị ảnh hưởng.

Một chính sách **myopic** chỉ nhìn số tiền của chuyến hiện tại.

Còn **look-ahead** cố gắng nhìn thêm giá trị của trạng thái tương lai.

Đó chính là lý do paper đưa yếu tố prediction vào việc điều phối.”

### Ví dụ dễ hiểu

“Có thể hiểu giống như chơi cờ: nước đi tốt không nhất thiết là nước ăn được nhiều quân nhất ngay lập tức, mà có thể là nước đặt mình vào vị trí tốt cho vài lượt tiếp theo.”

### Chuyển slide

“Vậy paper gốc thực sự muốn chứng minh những điều gì?”

---

## Slide 5 — Tuyên bố định tính của paper

### Kịch bản nói

“Em tóm tắt paper thành ba ý lớn.

Thứ nhất, nếu chỉ tối ưu hiệu quả tức thời thì chênh lệch accumulated utility giữa các tài xế có thể tăng lên theo thời gian.

Thứ hai, nếu đưa thông tin về nhu cầu tương lai vào quyết định hiện tại, hệ thống có khả năng cân bằng tốt hơn giữa hiệu quả và công bằng trong dài hạn.

Và thứ ba, giữa Utility và Fairness tồn tại một sự đánh đổi.

Nói dễ hiểu hơn, thường chúng ta khó có thể vừa tối đa hóa tuyệt đối doanh thu, vừa làm cho thu nhập của tất cả tài xế gần như giống hệt nhau.

Vì vậy vấn đề thực tế là tìm một điểm cân bằng hợp lý.”

### Chuyển slide

“Từ ba ý lớn đó, em cụ thể hóa thành sáu claim để kiểm thử.”

---

## Slide 6 — 6 claim cần kiểm thử

### Kịch bản nói

“Thay vì nói chung chung rằng em replicate paper, em chia bài toán thành sáu claim cụ thể.

C1 là kiểm tra xem Utility và Fairness có thật sự tạo ra trade-off hay không.

C2 là xem phương pháp đề xuất có tạo ra điểm cân bằng tốt hơn các baseline hay không.

C3 liên quan tới sự ổn định khi thời gian quan sát dài hơn.

C4 và C5 tập trung vào vai trò của forecast.

C6 kiểm tra điều gì xảy ra khi bỏ hoàn toàn fairness.

Điểm em muốn nhấn mạnh ở đây là: **mỗi claim đều phải có experiment riêng để kiểm chứng**, thay vì chỉ nhìn một bảng kết quả rồi kết luận toàn bộ paper đúng hay sai.”

### Chuyển slide

“Nhưng trước khi xem kết quả, em cần nói rõ một điều rất quan trọng: implementation của em không giống paper 100%.”

---

## Slide 7 — Paper và implementation của dự án khác nhau ở đâu?

### Kịch bản nói

“Đây là slide em muốn công bố rất rõ trước khi trình bày kết quả.

Paper dùng dữ liệu NYC năm 2016, còn dự án hiện tại dùng dữ liệu NYC TLC năm 2013.

Paper mô tả không gian dưới dạng các node được gộp trên graph, trong khi em sử dụng 67 taxi zone.

Paper cũng không công bố rõ số lượng driver, nên em chọn 200 driver làm cấu hình chính và sau đó có thêm sensitivity experiment với 100 và 400 driver.

Một khác biệt lớn nữa là prediction.

Paper dùng MLP dự báo demand, trong khi cấu hình chính của em dùng Q-table theo zone và hour như một **look-ahead value proxy**. Em vẫn có một MLP riêng để kiểm tra sensitivity, nhưng em không coi nó là reproduction chính xác của MLP paper.

Vì vậy em gọi công việc này là **trend replication dưới một implementation được xây dựng lại một cách minh bạch**, chứ không gọi là exact reproduction.”

### Câu nên nhấn

“Những khác biệt này là lý do em tập trung so sánh **hướng của kết quả**, không so tuyệt đối từng con số với paper.”

### Chuyển slide

“Sau khi xác định phạm vi như vậy, phần tiếp theo là cách hệ thống thực nghiệm được xây dựng.”

---

# PHẦN 2 — PHƯƠNG PHÁP & THIẾT LẬP THỰC NGHIỆM

## Slide 8 — Experimental Architecture

### Kịch bản nói

“Pipeline của simulator khá đơn giản về mặt logic.

Đầu vào là dữ liệu chuyến taxi thực của NYC.

Các request được gom thành từng batch 60 giây.

Ở mỗi batch, hệ thống tìm những tài xế đang rảnh và có thể đến điểm pickup trong tối đa 600 giây.

Sau đó mỗi policy tạo một ma trận điểm số giữa driver và request.

Ma trận này được đưa vào thuật toán Hungarian để tìm assignment tổng thể.

Điểm quan trọng là **tất cả policy đều dùng chung simulator và chung Hungarian solver**.

Như vậy khi kết quả khác nhau, nguyên nhân chính đến từ cách policy đánh giá chuyến đi, chứ không phải do mỗi baseline dùng một cơ chế matching khác nhau.”

### Giải thích Hungarian đơn giản

“Nếu không chuyên về thuật toán, có thể hiểu Hungarian ở đây là cách hệ thống tìm một phương án ghép tài xế với chuyến sao cho tổng điểm của toàn batch là tốt nhất, thay vì ghép từng chuyến một cách độc lập.”

### Chuyển slide

“Các policy khác nhau cụ thể ở điểm số như thế nào thì em trình bày ở slide tiếp theo.”

---

## Slide 9 — 5 Policy

### Kịch bản nói

“Em so sánh tổng cộng 5 policy.

**Greedy** ưu tiên chuyến có fare cao.

**Nearest** ưu tiên tài xế gần điểm đón nhất.

**LAF**, tức Lowest Accumulated Fare, ưu tiên các tài xế đang có tổng thu nhập thấp hơn.

**REASSIGN** dùng lợi ích chuyến đi sau khi trừ chi phí tài xế phải chạy rỗng đến điểm pickup.

Và cuối cùng là **MOMAQL**, chính sách chính của dự án, kết hợp lợi ích hiện tại, giá trị tương lai và yếu tố fairness.

Điểm em muốn nhấn ở slide này không phải từng công thức, mà là: **năm policy có cùng môi trường và cùng solver; thứ khác nhau chính là logic chấm điểm**.”

### Chuyển slide

“Trước khi tin vào kết quả của simulator, em cũng kiểm tra một số invariant cơ bản.”

---

## Slide 10 — Simulator invariants & tests

### Kịch bản nói

“Simulator phải đảm bảo một số nguyên tắc tối thiểu.

Một tài xế chỉ được coi là khả thi nếu đang rảnh và có thể tới điểm pickup trong giới hạn thời gian.

Khi một chuyến được giao, thu nhập, vị trí và thời điểm rảnh tiếp theo của tài xế đều được cập nhật.

Deadhead distance, tức quãng đường tài xế chạy tới đón khách mà chưa có hành khách, được tính bằng khoảng cách haversine và giả định tốc độ trung bình 12 mph.

Hiện tại 20 trên 20 test invariant đều pass.

Tuy nhiên em không coi 20/20 test là bằng chứng simulator hoàn hảo.

Em cũng đã phát hiện hai test dựa vào trace có coverage yếu do `record_trace=False` mặc định.

Em chủ động giữ điểm này trong tài liệu vì em muốn phân biệt giữa ‘test pass’ và ‘đã chứng minh hệ thống không có lỗi’.”

### Chuyển slide

“Bây giờ em đi vào phần quan trọng nhất của MOMAQL: cách một assignment được chấm điểm.”

---

## Slide 11 — MOMAQL Decision Logic

### Kịch bản nói

“Có thể hiểu score của MOMAQL gồm ba phần.

Phần thứ nhất là **Immediate Utility**: chuyến hiện tại đem lại bao nhiêu lợi ích sau khi trừ chi phí chạy rỗng.

Phần thứ hai là **Future Zone Value**: nếu chuyến này đưa tài xế tới một zone nào đó vào một giờ nhất định, trạng thái đó có giá trị tương lai như thế nào.

Phần thứ ba là **Fairness Adjustment**: nếu một tài xế hiện đang kiếm ít hơn mức trung bình, hệ thống có thể ưu tiên người đó hơn một chút.

Ba yếu tố này kết hợp lại thành Assignment Score.”

### Nói rõ Q-table

“Q-table của em không phải dự báo số lượng request giống MLP trong paper.

Nó nên được hiểu là một ước lượng: ‘nếu tài xế kết thúc ở zone này vào giờ này thì trạng thái đó có giá trị tương lai bao nhiêu?’”

### Chuyển slide

“Nếu mentor muốn xem cụ thể về mặt toán học thì đây là công thức đầy đủ.”

---

## Slide 12 — Công thức score và TD(0)

### Kịch bản nói

“Ở công thức này, em không cần đi sâu tất cả ký hiệu nếu người nghe không chuyên.

Ý chính là phần efficiency gồm fare hiện tại, trừ deadhead cost, cộng thêm giá trị tương lai `gamma nhân Q`.

Sau đó nó được kết hợp với fairness term thông qua lambda.

Q-table được cập nhật online bằng TD(0).

Có ba tham số chính trong cấu hình mặc định:

- lambda bằng 0,5,
- gamma bằng 0,9,
- alpha bằng 0,1.

Ở ablation, nếu bỏ forecast thì em ép future Q bằng 0.

Nếu bỏ fairness thì lambda bằng 0.

Một lưu ý rất quan trọng: lambda trong project **không tương đương toán học** với lambda của paper vì cách scalarisation khác nhau. Vì vậy em không so trực tiếp giá trị lambda giữa hai bên.”

### Chuyển slide

“Tiếp theo là dữ liệu và quy mô thực nghiệm.”

---

## Slide 13 — Dataset & protocol

### Kịch bản nói

“Dữ liệu được chia theo thời gian thành ba phần.

Train có khoảng 912 nghìn chuyến.

Validation khoảng 195 nghìn chuyến.

Test cũng khoảng 195 nghìn chuyến.

Cấu hình chính sử dụng 200 driver và 67 zone.

Các main experiment được lặp lại trên 5 seed để giảm khả năng một kết quả xuất hiện chỉ vì một trạng thái random may mắn.

Request được xử lý theo batch 60 giây.

Điểm quan trọng là tất cả so sánh chính đều sử dụng cùng data và cùng protocol.”

### Chuyển slide

“Sau phần thiết lập, bây giờ em đi vào kết quả.”

---

# PHẦN 3 — KẾT QUẢ THỰC NGHIỆM & PHÂN TÍCH

## Slide 14 — Main baseline comparison

### Kịch bản nói

“Đây là kết quả so sánh chính giữa 5 policy.

Trục ngang là Gini. **Càng sang trái càng công bằng.**

Trục dọc là Utility. **Càng lên cao càng tốt.**

MOMAQL nằm ở vị trí có Utility cao nhất, khoảng 1,42 triệu, với Gini khoảng 0,204.

Greedy có Utility khoảng 1 triệu nhưng Gini lên tới khoảng 0,531, tức chênh lệch thu nhập lớn hơn rõ rệt.

Nearest và REASSIGN cũng có Utility thấp hơn và Gini cao hơn MOMAQL.

Một điểm rất quan trọng là LAF.

LAF có Gini gần bằng 0, tức cực kỳ công bằng, nhưng Utility chỉ khoảng 0,77 triệu.

Do đó em **không kết luận MOMAQL là policy công bằng nhất**.

Kết luận đúng là MOMAQL tạo ra một **điểm cân bằng mạnh**: Utility rất cao trong khi inequality vẫn thấp hơn nhiều so với các baseline thiên về efficiency.”

### Ví dụ dễ hiểu

“Có thể hình dung LAF chia chiếc bánh rất đều nhưng chiếc bánh nhỏ hơn. MOMAQL tạo ra chiếc bánh lớn hơn nhiều và vẫn giữ mức chia tương đối cân bằng.”

### Chuyển slide

“Để kiểm tra kết quả này có phải do một seed may mắn hay không, em xem thêm từng seed.”

---

## Slide 15 — Per-seed summary

### Kịch bản nói

“Ở đây, mỗi chấm là giá trị trung bình qua 5 seed, còn thanh mờ là khoảng min đến max.

Điều đáng chú ý là khoảng kết quả của MOMAQL khá hẹp.

Utility của MOMAQL nằm khoảng 1,412 đến 1,433 triệu.

Gini nằm khoảng 0,195 đến 0,211.

Điều này cho thấy kết quả chính ở slide trước khá ổn định qua các seed, chứ không phụ thuộc vào một lần chạy đặc biệt.”

### Chuyển slide

“Sau khi biết MOMAQL có một operating point tốt, em kiểm tra tiếp ảnh hưởng của lambda.”

---

## Slide 16 — Lambda sweep

### Kịch bản nói

“Lambda là tham số điều chỉnh mức độ hệ thống quan tâm đến fairness.

Nếu mọi thứ đơn giản, ta có thể kỳ vọng lambda tăng thì Utility giảm dần và fairness tốt dần.

Nhưng thực tế của hệ thống này không đơn điệu như vậy.

Ví dụ lambda bằng 0,8 lại cho Utility cao nhất, khoảng 1,555 triệu.

Trong khi lambda bằng 1 đưa fairness lên mức gần hoàn hảo nhưng Utility giảm mạnh xuống khoảng 0,766 triệu, gần giống LAF.

Điều này xảy ra vì lambda không chỉ thay đổi trọng số toán học.

Nó còn thay đổi thứ tự các cặp driver-request trong ma trận score, từ đó làm thay đổi assignment và trạng thái fleet về sau.

Vì vậy em gọi biểu đồ này là **Empirical Lambda Sweep**, không gọi nó là một Pareto frontier lý tưởng.”

### Chuyển slide

“Tiếp theo là thí nghiệm quan trọng nhất để tách vai trò của từng thành phần: ablation.”

---

## Slide 17 — Ablation Study

### Kịch bản nói

“Ở đây em có ba cấu hình.

**Full** là hệ thống đầy đủ.

**No Forecast** bỏ look-ahead.

**No Fairness** bỏ thành phần fairness.

Về Utility, Full đạt khoảng 1,42 triệu.

No Forecast đạt khoảng 1,16 triệu.

Tức Full cao hơn khoảng **22,4%**.

Đây là bằng chứng khá mạnh cho thấy look-ahead đang tạo ra giá trị kinh tế.

Tuy nhiên nếu nhìn sang Gini, No Forecast có Gini khoảng 0,146, thấp hơn Full là 0,204.

Như vậy No Forecast lại công bằng hơn.

Em không cố biến điều này thành ‘Full tốt hơn mọi mặt’.

Cách em diễn giải là: **Full chấp nhận mức inequality cao hơn để đổi lấy Utility cao hơn đáng kể.**

Đây là một trade-off vận hành.

Nếu nền tảng ưu tiên efficiency hơn một chút, Full có thể là lựa chọn hợp lý. Nếu mục tiêu ưu tiên fairness tuyệt đối hơn thì No Forecast hoặc LAF lại có lợi thế.”

### Nói rõ No Fairness

“No Fairness cho Gini khoảng 0,45, tức chênh lệch thu nhập tăng mạnh.

Nhưng Utility cũng giảm chứ không tăng như paper kỳ vọng.

Đây là một điểm khác paper và em giữ nguyên như một negative result.”

### Chuyển slide

“Để kiểm tra trade-off này có ổn định qua các seed không, em xem tiếp dữ liệu từng seed.”

---

## Slide 18 — Ablation per-seed

### Kịch bản nói

“Điểm quan trọng ở đây là cả 5 seed đều cho cùng một hướng.

Full luôn có Utility cao hơn No Forecast.

Và No Forecast luôn có Gini thấp hơn Full.

Vì vậy chênh lệch ở slide trước không phải do một seed bất thường.

Nói cách khác, đây là một pattern ổn định trong implementation hiện tại.”

### Chuyển slide

“Vì paper gốc dùng variance làm fairness metric chính, em cũng kiểm tra xem kết luận có thay đổi nếu không dùng Gini hay không.”

---

## Slide 19 — Variance / CV

### Kịch bản nói

“Paper dùng variance của accumulated utility làm chỉ số fairness chính.

Trong project em dùng Gini làm chỉ số trực quan vì Gini dễ so sánh giữa các hệ thống có tổng Utility khác nhau.

Nhưng em vẫn giữ variance và coefficient of variation để đối chiếu.

Kết quả cũng cùng hướng với Gini.

Full có variance khoảng 8,35 triệu.

No Forecast chỉ khoảng 2,47 triệu.

No Fairness cao nhất, khoảng 14,23 triệu.

Vì vậy việc No Forecast công bằng hơn Full không chỉ là do em chọn Gini; variance của paper cũng cho cùng một kết luận.”

### Chuyển slide

“Tiếp theo em thử thay representation của forecast bằng một MLP thật.”

---

## Slide 20 — MLP benchmark

### Kịch bản nói

“Trong cấu hình chính em dùng Q-table làm look-ahead value.

Để xem kết quả có phụ thuộc hoàn toàn vào cách representation này hay không, em xây thêm một MLP dự báo demand.

MLP nhận thông tin về pickup zone, destination zone và hour.

Sau đó dự báo demand theo OD pair và thời gian.

Kết quả, MLP đạt Utility khoảng 1,392 triệu.

Nó thấp hơn Tabular Q là 1,422 triệu nhưng vẫn cao hơn rõ No Forecast là 1,162 triệu.

Như vậy một forecast model khác vẫn tạo ra lợi ích Utility.

Tuy nhiên fairness của MLP không tốt hơn No Forecast.

Điểm em muốn rút ra ở đây là: **giá trị của việc nhìn trước tương lai vẫn xuất hiện, nhưng mức độ hiệu quả phụ thuộc cách forecast được biểu diễn và tích hợp vào decision score**.”

### Chuyển slide

“Cho đến đây chúng ta mới nhìn kết quả cuối cùng. Nhưng paper nhấn mạnh chữ ‘long-term’, nên em muốn xem lợi ích này thay đổi thế nào khi horizon kéo dài.”

---

## Slide 21 — Long-Horizon Utility

### Kịch bản nói

“Đây là một trong những kết quả mà em thấy đáng chú ý nhất.

Từ ngày 1 tới khoảng ngày 14, hai đường Full và No Forecast gần như trùng nhau.

Nói cách khác, trong ngắn hạn, việc có look-ahead hay không gần như chưa tạo khác biệt đáng kể về Utility.

Nhưng sau đó sự khác biệt bắt đầu xuất hiện.

Ở ngày 21, Full cao hơn khoảng **5,15%**.

Ngày 28, chênh lệch tăng lên khoảng **11,65%**.

Và đến ngày 37, Full cao hơn khoảng **20,19%**.

Điều này cho thấy hiệu ứng của look-ahead là một **delayed effect**.

Nó không nhất thiết giúp ngay lập tức, nhưng khi các quyết định tích lũy đủ lâu, hai policy đưa fleet vào những trạng thái khác nhau và khoảng cách Utility bắt đầu mở rộng.”

### Ví dụ dễ hiểu

“Có thể hiểu giống như một chiến lược đầu tư dài hạn: vài ngày đầu nhìn gần như không khác, nhưng sau đủ thời gian, hiệu ứng tích lũy mới hiện rõ.”

### Chuyển slide

“Nhưng nếu nhìn về fairness thì câu chuyện lại khác.”

---

## Slide 22 — Long-Horizon Fairness

### Kịch bản nói

“Trên biểu đồ này, Gini càng thấp thì càng công bằng.

Đến khoảng ngày 14, Full và No Forecast vẫn gần như giống nhau.

Nhưng từ ngày 21 trở đi, Full có Gini cao hơn No Forecast.

Đến ngày 37:

Full khoảng **0,217**.

No Forecast khoảng **0,151**.

Như vậy, trong implementation của em, look-ahead tạo lợi ích Utility dài hạn rất rõ nhưng **không tạo lợi thế fairness dài hạn như paper kỳ vọng**.

Đây là một trong những discrepancy quan trọng nhất của dự án.

Em không xem nó là một experiment thất bại.

Ngược lại, đây chính là kết quả mà replication cần chỉ ra: phần nào của paper được giữ lại, và phần nào nhạy với cách implementation.”

### Câu nên nói chậm

“Ở đây em muốn nhấn mạnh: **Full tốt hơn về Utility, nhưng No Forecast tốt hơn về Fairness. Hai mục tiêu này không cùng đi theo một hướng.**”

### Chuyển slide

“Nếu mentor muốn xem từng checkpoint cụ thể, em có bảng đầy đủ ở slide tiếp theo.”

---

## Slide 23 — Full Multi-Horizon Table

### Kịch bản nói

“Bảng này chứa toàn bộ 11 checkpoint.

Em không đọc từng dòng.

Điểm cần nhìn là từ ngày 1 đến ngày 14, chênh lệch Utility gần như bằng 0.

Từ ngày 21 trở đi Utility Full tăng dần so với No Forecast.

Trong khi Gini của Full lại cao hơn.

Bảng này chủ yếu dùng để kiểm tra số cụ thể khi cần.”

### Chuyển slide

“Sau khi thấy hai policy bắt đầu tách nhau từ khoảng ngày 14 đến 21, câu hỏi tiếp theo là: tại sao?”

---

## Slide 24 — Mechanism Probe

### Kịch bản nói

“Em làm thêm một số diagnostic để hiểu thời điểm phân kỳ.

Ở giai đoạn ngày 1 đến 7, tỷ lệ quyết định khác nhau giữa Full và No Forecast chỉ khoảng **0,08%**.

Tức là dù một bên có look-ahead và một bên không, thực tế chúng vẫn gần như chọn cùng assignment.

Nhưng từ ngày 8 đến 37, tỷ lệ disagreement tăng lên khoảng **15%**.

Cùng lúc đó, mức thay đổi Q-table giảm dần từ khoảng 1,88 xuống 0,82.

Điều này gợi ý rằng khi Q-table dần hình thành các khác biệt giá trị giữa các zone và time, look-ahead bắt đầu đủ mạnh để thay đổi quyết định assignment.

Và khi các quyết định khác nhau đủ nhiều, Utility trajectory mới bắt đầu tách ra.”

### Cảnh báo khoa học

“Tuy nhiên em không gọi đây là bằng chứng nhân quả.

Hai hiện tượng xảy ra cùng thời điểm, nhưng để chứng minh Q convergence là nguyên nhân trực tiếp, cần một controlled intervention khác.”

### Chuyển slide

“Em còn kiểm tra sâu thêm một vài giả thuyết khác.”

---

## Slide 25 — Mechanism diagnostics chi tiết

### Kịch bản nói

“Slide này có ba phân tích bổ sung.

Thứ nhất, số state Q-table đã quan sát tăng dần và gần bão hòa vào cuối horizon.

Thứ hai, tỷ trọng fairness trong score tăng từ khoảng 1,2% ở ngày đầu lên khoảng 4,5% ở ngày 37.

Tức fairness có ảnh hưởng tăng dần, nhưng efficiency và look-ahead vẫn chiếm phần lớn score.

Thứ ba, em kiểm tra giả thuyết liệu sự phân kỳ có liên quan chu kỳ tuần hay không.

Kết quả không thấy một pattern 7 ngày lặp lại rõ ràng, nên giả thuyết weekly cycle không được hỗ trợ.

Ngoài ra, core zone có nhiều candidate driver hơn periphery, nhưng phân tích đó dùng geometry tĩnh nên em chỉ coi là diagnostic, không phải bằng chứng causal.”

### Chuyển slide

“Một sensitivity khác rất quan trọng là số lượng driver.”

---

## Slide 26 — Fleet-Scale Sensitivity

### Kịch bản nói

“Ở đây em thay đổi quy mô fleet.

Khi chỉ có 100 driver, tức cung tương đối khan hiếm, Full có Utility cao hơn No Forecast tới khoảng **41,9%**.

Với 200 driver, lợi thế còn khoảng **23,3%**.

Nhưng khi tăng lên 400 driver, lợi thế gần như bằng 0.

Điều này rất hợp lý về mặt vận hành.

Khi thiếu tài xế, việc đặt đúng driver vào đúng khu vực cho tương lai rất quan trọng.

Nhưng khi tài xế quá nhiều, gần như request nào cũng dễ tìm được driver phù hợp, nên thông tin look-ahead không còn tạo nhiều giá trị.”

### Insight cần nhấn

“Vì vậy em không kết luận forecast luôn hữu ích trong mọi điều kiện. Giá trị của nó phụ thuộc vào mức độ khan hiếm supply.”

### Chuyển slide

“Bảng tiếp theo là số liệu đầy đủ của sensitivity này.”

---

## Slide 27 — Fleet-scale raw results

### Kịch bản nói

“Ở đây em giữ raw summary cho ba mức 100, 200 và 400 driver.

Điểm chính vẫn là xu hướng lợi ích Utility giảm dần khi fleet tăng.

Đây cũng là một cách kiểm tra rằng lựa chọn 200 driver không hoàn toàn tùy ý, vì em đã khảo sát thêm cả hai phía.”

### Chuyển slide

“Sau toàn bộ các experiment, em tổng hợp lại từng claim.”

---

# PHẦN 4 — ĐÁNH GIÁ TÁI LẬP & KẾT LUẬN

## Slide 28 — Claim-by-Claim Assessment

### Kịch bản nói

“Đây là slide trả lời trực tiếp câu hỏi: cuối cùng em replicate được đến đâu?

Em muốn phân biệt hai câu.

**6 trên 6 claim đã được kiểm thử.**

Nhưng điều đó **không có nghĩa 6 trên 6 claim đều reproduce hoàn toàn**.

C1 về Utility–Fairness trade-off được reproduce.

C2 về balanced policy so với baseline cũng được reproduce trong phạm vi implementation này.

C3 về long-horizon stability có bằng chứng hỗ trợ, nhưng em vẫn giữ caveat vì definition không hoàn toàn giống paper.

C4 về forecast cải thiện fairness dài hạn thì hướng kết quả khác paper: Utility tốt lên, nhưng Gini không tốt lên.

C5 vì vậy chỉ được reproduce một phần: Utility được hỗ trợ, Fairness thì không.

C6 cũng partial: bỏ fairness làm bất bình đẳng tăng mạnh đúng như kỳ vọng, nhưng Utility lại giảm thay vì tăng.

Vì vậy kết luận của em không phải ‘paper đúng hoàn toàn’ hay ‘paper sai’.

Kết luận là: **một số cơ chế khá robust, còn một số behavior phụ thuộc mạnh vào cách implementation và operating condition**.”

### Câu rất quan trọng

“Replication có giá trị không chỉ khi nó xác nhận paper, mà còn khi nó chỉ ra phần nào không tái xuất hiện.”

### Chuyển slide

“Dựa trên đó, em tổng kết điểm mạnh, hạn chế và verdict cuối.”

---

## Slide 29 — Limitations & Conclusion

### Kịch bản nói

“Có năm limitation chính.

Thứ nhất, dữ liệu là năm 2013 thay vì 2016.

Thứ hai, cấu hình chính dùng Tabular Q thay cho MLP của paper.

Thứ ba, scalarisation đã được sửa đổi.

Thứ tư, số driver và cách chia 67 zone là assumption của implementation.

Thứ năm, một số baseline là adapted baseline chứ không phải code gốc của paper.

Vì vậy em không dùng cụm từ Full Reproduction.

Kết luận của em là **Strong Partial Trend Replication**.

‘Partial’ vì không phải mọi claim đều cùng hướng paper.

‘Strong’ vì các claim đều được kiểm thử bằng nhiều lớp experiment: baseline, ablation, long-horizon, mechanism probe, forecast sensitivity và fleet sensitivity.

Ba kết luận quan trọng nhất là:

Một, MOMAQL tạo ra một balanced operating point tốt.

Hai, look-ahead có delayed Utility advantage rất rõ trong horizon dài.

Ba, fairness behavior không đi cùng hướng paper trong implementation hiện tại.”

### Chuyển slide

“Sau phần nghiên cứu, em chuyển sang phần sản phẩm.”

---

# PHẦN 5 — PRODUCT DEMO

## Slide 30 — Product Demo

### Nếu demo chưa hoàn thiện ở thời điểm nói

“Phần sản phẩm đầu ra em đang tách riêng khỏi phần research.

Ở giai đoạn này phần nghiên cứu, experiment và kết luận đã được chốt trước.

Sau đó em mới đóng gói logic dispatch thành một flow sản phẩm gồm input, decision/dispatch và output/dashboard.

Trong bản slide hiện tại, phần này mới là khung để xác định vị trí của demo trong toàn bộ câu chuyện.

Khi demo hoàn thiện, phần này sẽ tập trung vào việc cho người dùng thấy một request đi vào hệ thống, hệ thống lựa chọn driver như thế nào, và kết quả Utility/Fairness được hiển thị ra sao.”

### Nếu demo đã hoàn thiện trước ngày thuyết trình

Thay đoạn trên bằng kịch bản demo thực tế, tuyệt đối không nói “placeholder”.

### Chuyển slide

“Trước khi kết thúc, em xin tổng kết toàn bộ dự án trong một slide.”

---

# TỔNG KẾT

## Slide 31 — Overall Project Conclusion

### Kịch bản nói

“Nếu nhìn toàn bộ dự án, em đã xây một simulator độc lập với 5 policy cùng dùng chung Hungarian solver.

Em thực hiện hơn 15 experiment bao gồm baseline, lambda sweep, ablation, long-horizon, mechanism probe, fleet sensitivity và forecast sensitivity.

Cả 6 claim đều được kiểm thử bằng dữ liệu NYC TLC thật và các main experiment được lặp qua 5 seed.

Điều quan trọng nhất em học được từ dự án này không phải chỉ là cách implement một thuật toán.

Mà là cách đi từ một claim trong paper, biến nó thành experiment, rồi dùng dữ liệu để quyết định mình có thật sự reproduce được claim đó hay không.

Verdict cuối cùng của em vẫn là:

**Strong Partial Trend Replication.**”

### Chuyển slide

“Em xin kết thúc phần trình bày tại đây.”

---

## Slide 32 — Cảm ơn

### Kịch bản nói

“Em cảm ơn mentor và mọi người đã dành thời gian lắng nghe.

Em sẵn sàng nhận câu hỏi và trao đổi thêm về methodology, kết quả hoặc implementation.”

---

# PHẦN NHỚ NHANH TRƯỚC KHI LÊN NÓI

## 1. Bốn ý bắt buộc phải nhớ

### Ý 1 — Đây là trend replication

Không nói:

> “Em reproduce paper hoàn toàn.”

Nên nói:

> “Em kiểm tra lại các xu hướng định tính của paper dưới một implementation độc lập.”

---

### Ý 2 — MOMAQL không phải fair nhất

LAF fair hơn nhiều.

Nhưng MOMAQL có Utility cao hơn rất nhiều.

Do đó:

> MOMAQL = balanced operating point.

---

### Ý 3 — Forecast không làm fairness tốt hơn trong project

Full:
- Utility cao hơn No Forecast khoảng **22,4%**.
- Nhưng Gini cũng cao hơn.

Do đó:

> Forecast giúp Utility, nhưng fairness direction khác paper.

---

### Ý 4 — Kết quả mạnh nhất là long-horizon Utility

Nhớ ba con số:

- Day 21: **+5,15%**
- Day 28: **+11,65%**
- Day 37: **+20,19%**

Đây là result rất dễ kể và dễ nhớ.

---

# Cách giải thích các thuật ngữ cho người không chuyên

## Utility

Nói:

> “Utility có thể hiểu đơn giản là tổng lợi ích kinh tế mà hệ thống tạo ra.”

Không cần bắt đầu bằng công thức.

---

## Fairness

Nói:

> “Fairness là mức độ lợi ích được phân phối đồng đều giữa các tài xế.”

---

## Gini

Nói:

> “Gini đo mức chênh lệch thu nhập. Gini càng thấp thì càng công bằng. Gini bằng 0 nghĩa là mọi người có mức thu nhập bằng nhau.”

---

## Variance

Nói:

> “Variance cũng đo mức độ các tài xế lệch khỏi mức thu nhập trung bình. Variance thấp hơn nghĩa là thu nhập tập trung gần nhau hơn.”

---

## Look-ahead

Nói:

> “Look-ahead nghĩa là khi giao chuyến hiện tại, hệ thống còn nhìn xem chuyến đó sẽ đưa tài xế đến đâu và khu vực đó có giá trị gì trong tương lai.”

---

## Q-table

Nói:

> “Q-table giống một bảng ghi nhớ xem từng khu vực vào từng giờ thường có giá trị tương lai như thế nào.”

---

## Hungarian Algorithm

Nói:

> “Đây là thuật toán tìm cách ghép nhiều tài xế với nhiều chuyến cùng lúc sao cho tổng điểm của toàn bộ assignment tốt nhất.”

---

## Ablation

Nói:

> “Ablation là cách cố tình bỏ một thành phần ra khỏi hệ thống để xem chính thành phần đó đóng góp điều gì.”

---

## Seed

Nói:

> “Seed là các lần khởi tạo ngẫu nhiên khác nhau. Chạy nhiều seed giúp kiểm tra kết quả có ổn định hay chỉ do may mắn ở một lần chạy.”

---

# Một phiên bản mở đầu tự nhiên hơn nếu không muốn nói quá học thuật

“Em xin trình bày FairDispatch.

Bài toán của em xuất phát từ một vấn đề khá dễ hình dung: một hệ thống gọi xe có thể rất giỏi kiếm tiền, nhưng nếu những chuyến tốt cứ rơi vào một nhóm tài xế thì sau một thời gian khoảng cách thu nhập giữa các tài xế sẽ ngày càng lớn.

Paper em replicate thử giải quyết cả hai mục tiêu: vừa giữ hiệu quả kinh tế, vừa hạn chế chênh lệch thu nhập trong dài hạn.

Em không cố làm lại chính xác từng con số của paper, vì có một số chi tiết paper không công bố đầy đủ. Thay vào đó em tách paper thành từng claim, chạy experiment cho từng claim và xem xu hướng nào xuất hiện lại trong implementation của em.”

---

# Một phiên bản kết thúc tự nhiên

“Qua toàn bộ experiment, em không kết luận paper được reproduce hoàn toàn.

Em tái lập được khá rõ trade-off Utility–Fairness và đặc biệt là lợi ích Utility dài hạn của look-ahead.

Nhưng fairness của forecast không đi cùng hướng paper trong implementation này.

Với em đây không phải kết quả xấu, vì mục tiêu của replication không phải ép dữ liệu giống paper mà là tìm xem claim nào thực sự xuất hiện lại.

Vì vậy em đánh giá dự án ở mức Strong Partial Trend Replication.

Em xin cảm ơn mọi người và sẵn sàng nhận câu hỏi.”

---

# 10 câu hỏi rất dễ được hỏi sau bài thuyết trình

## 1. Tại sao không dùng đúng dữ liệu 2016?

“Đây là một deviation của project. Vì vậy em không so absolute number với paper, chỉ so xu hướng. Nếu nâng fidelity, bước đầu tiên của em là chạy đúng slice 2016.”

---

## 2. Tại sao chọn 200 driver?

“Paper không công bố rõ số driver nên 200 là assumption. Em có chạy sensitivity 100, 200 và 400 driver để kiểm tra tác động của assumption này.”

---

## 3. Tại sao Full Gini cao hơn No Forecast mà vẫn dùng Full?

“Vì đây là bài toán đa mục tiêu. Full tạo Utility cao hơn khoảng 22,4%, nhưng chấp nhận inequality cao hơn. Việc chọn operating point nào phụ thuộc mức độ nền tảng ưu tiên hiệu quả hay fairness.”

---

## 4. MOMAQL có phải policy tốt nhất không?

“Nếu chỉ xét Utility thì MOMAQL tốt nhất trong main baseline. Nếu chỉ xét fairness thì LAF tốt hơn. Em gọi MOMAQL là balanced operating point chứ không nói tốt nhất mọi mặt.”

---

## 5. Tại sao forecast không cải thiện fairness giống paper?

“Em chưa có bằng chứng causal chắc chắn. Có thể do khác dataset, scalarisation, forecast representation hoặc simulator dynamics. Vì vậy em chỉ kết luận direction khác paper, chưa kết luận paper sai.”

---

## 6. Q-table có phải forecast không?

“Không phải demand forecast trực tiếp. Nó là look-ahead value proxy, tức ước lượng giá trị tương lai của một zone-hour state.”

---

## 7. Kết quả mạnh nhất là gì?

“Delayed Utility effect của look-ahead: gần như không khác đến day 14, sau đó +5,15% day 21, +11,65% day 28 và +20,19% day 37.”

---

## 8. Vì sao khi 400 driver forecast gần như không còn lợi ích?

“Khi supply quá dư, gần như request nào cũng dễ được phục vụ. Khi đó việc lựa chọn vị trí tương lai không còn quan trọng như lúc driver khan hiếm.”

---

## 9. Tại sao gọi là Strong Partial Trend Replication?

“Partial vì không phải mọi direction đều giống paper. Strong vì cả 6 claim đều được kiểm thử với nhiều experiment bổ sung và repeated seeds, chứ không chỉ một bảng kết quả.”

---

## 10. Nếu làm tiếp, ưu tiên gì?

“Em sẽ ưu tiên dùng đúng dữ liệu 2016, align scalarisation sát paper hơn, dùng forecast demand gần paper hơn và làm controlled ablation để giải thích rõ nguyên nhân của fairness discrepancy.”

---

# Nhịp nói đề xuất

Nếu trình bày đầy đủ 32 slide:

- Slide 1–7: khoảng 5–6 phút
- Slide 8–13: khoảng 5–6 phút
- Slide 14–27: khoảng 12–16 phút
- Slide 28–32: khoảng 4–5 phút

Tổng hợp lý:

> **Khoảng 26–33 phút**, chưa tính Q&A.

Nếu thời gian thực tế chỉ khoảng 15–20 phút, không nên cố đọc hết toàn bộ chi tiết. Những slide như:

- 9
- 10
- 12
- 15
- 18
- 19
- 20
- 23
- 25
- 27

có thể nói rất nhanh hoặc dùng như backup evidence.

---

# Câu cuối cần nhớ

> **Đừng cố chứng minh project hoàn hảo. Hãy chứng minh rằng cách bạn đọc dữ liệu và đưa ra kết luận là đáng tin.**
