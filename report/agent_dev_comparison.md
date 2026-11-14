# So sánh hai cấu hình agent trên dev

Cùng corpus 271 chunk C, 17 câu dev, dense top-k=3, context 2.000 ký tự, tối đa 2 search/5 model call, 1.024 output token mỗi lời gọi.

| Model | Câu | answered | abstain | error | Context đủ gold | Output token | Tổng thời gian câu hỏi |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen3:4b | 17 | 8 | 2 | 7 | 13/15 | 21913 | 73.0 phút |
| qwen3:4b-instruct | 17 | 15 | 2 | 0 | 14/15 | 1865 | 11.0 phút |

Đây là số lần hoàn tất/ lỗi, không phải độ chính xác. Cần chấm nội dung và citation trước khi chọn pipeline cuối.

Context đủ gold dùng cùng quy tắc OR giữa nhóm, AND giữa fragment trong benchmark_support.py; chỉ câu có đáp án vào mẫu số. Đây không phải điểm grounded answer hay chấm context thủ công.

## Phân tích lỗi

Baseline lỗi ở: q05, q07, q09, q12, q13, q14, q15. Các câu có output bị cắt: q05, q07, q09, q12, q13, q14, q15.
q09 hết token trước khi gọi retrieval; q05 và q07 đã tìm tài liệu nhưng hết token trước câu trả lời. q14 còn có phản hồi không đúng định dạng/citation trước khi bị cắt.
Cấu hình Instruct còn lỗi ở: không có.

Giả thuyết: phần reasoning của model cũ chiếm output budget; dùng bản Instruct trả lời trực tiếp sẽ giảm cắt token và thời gian. Đây là đổi model/weights/template, không phải sửa nhãn hoặc thay đáp án bằng kết quả giả.
Các giới hạn API, corpus, split và retrieval được giữ giống nhau; model digest/thiết lập thực tế nằm trong JSON đi kèm. Thời gian là một lần đo trên máy local, chưa phải thí nghiệm timing lặp lại.

## Nhật ký và bước chấm

Baseline: `C:\Users\Admin\Downloads\K5-L3-Day07-Retrieval-Context-Engineering-main\K5-L3-Day07-Retrieval-Context-Engineering-main\starter\results\agent-dev-dense\20261114_201554_120565`.
Candidate: `C:\Users\Admin\Downloads\K5-L3-Day07-Retrieval-Context-Engineering-main\K5-L3-Day07-Retrieval-Context-Engineering-main\starter\results\agent-dev-dense-instruct\20261114_225910_368066`.
Run cũ được giữ nguyên. Không trộn các câu thành công từ các run thành một benchmark mới.
Đọc [tập chấm dev](agent_dev_review.md), điền bản sao reviews_template.json thành reviews.json và ghi người/công cụ chấm. Nhãn AI phải được ghi rõ, không đại diện cho nhãn người học.
Chưa chạy test. Chưa kết luận một cấu hình tốt hơn về grounded answer chỉ từ việc giảm lỗi kỹ thuật.
