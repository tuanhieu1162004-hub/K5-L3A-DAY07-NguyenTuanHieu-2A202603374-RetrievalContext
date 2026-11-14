# Ví dụ cần chấm nguồn dù agent không lỗi

Run được đọc: `20261114_225910_368066`, model `qwen3:4b-instruct`.
Đây là nhận xét kiểm tra của Codex (AI), không phải nhãn người học đã chấm
cho toàn bộ benchmark. Các reviews_template vẫn giữ trạng thái chưa chấm.

## q13

Câu hỏi yêu cầu xác định biểu thức đối số được đánh giá trước hay sau khi
gọi hàm. Model trả lời về thứ tự đánh giá và dẫn chunk
`dd1bf77ddb19877772dc93ab`, trang PDF 48.

Đoạn được dẫn là các định nghĩa glossary: argument, local variable,
return value và fruitful function. Nó không nêu thứ tự đánh giá biểu thức
đối số so với thời điểm gọi hàm. Vì vậy ID citation có trong context nhưng
chưa hỗ trợ khẳng định được gắn nguồn. Khi chấm cần đánh dấu citation này
không hỗ trợ, thay vì cho đúng chỉ vì ID hợp lệ.

Evidence tham chiếu của câu này nằm ở trang PDF 44 trong benchmark dev.
Xem toàn bộ context và đáp án tham chiếu ở [tập chấm dev](agent_dev_review.md).

Kết luận giới hạn: lượt mới giảm lỗi cắt token; vẫn phải đọc từng câu và
nguồn trước khi kết luận grounded answer tốt hoặc chốt pipeline để chạy test.
