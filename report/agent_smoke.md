# Kiểm tra tích hợp agent thật trên hai câu dev

**Nhật ký lịch sử:** kết quả đầy đủ và nhãn cuối nằm trong [báo cáo cá nhân](individual/2A202603374_NguyenTuanHieu.md). Các mô tả "chưa chạy" bên dưới phản ánh thời điểm smoke test, không phải trạng thái bản nộp cuối.

Đây là kiểm tra tích hợp, không phải độ chính xác benchmark đầy đủ. Chưa
chạy agent trên toàn bộ dev để chọn cấu hình, chưa chạy test. Các lượt thử
dùng prompt/bộ đọc phản hồi khác nhau; không gộp thành tỷ lệ đạt.

## Cấu hình lượt xác nhận cuối

- Run: `20261114_194624_573936`.
- Model: local Ollama `qwen3:4b`, Ollama 0.40.16, model digest
  `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`.
- Thinking theo capability: true; reasoning mode: default; seed 42,
  temperature 0, num_ctx 8192, tối đa 1024 output token mỗi lời gọi.
- Dense MiniLM + pgvector Day 6, strategy C, 271 chunk; top-k 3,
  budget 2000 ký tự, tối đa 2 search và 5 model call mỗi câu.
- Trace: `starter/results/agent-smoke-dense/20261114_194624_573936/traces.json`.
  Prompt, tool schema, checksum code/corpus và cấu hình ở `run_config.json`.

| Query | Trạng thái | Search | Model call | Thời gian |
|---|---|---:|---:|---:|
| q01 | answered | 1 | 2 | 219,8 giây |
| dev-absent-01 | abstain | 1 | 2 | 170,7 giây |

Tổng: 1 answered, 1 abstain, 0 error; 3062 prompt token và 1946 output token
theo API. Output token bao gồm reasoning. Phí dịch vụ 0 USD, không gồm
điện/máy. Model chạy CPU; không dùng thời gian retrieval làm thời gian trả
lời end-to-end.

## Câu có đáp án

Question: What does an interpreter do?

Model tự yêu cầu search với nguyên câu hỏi, sau đó gọi final_answer:

> An interpreter is a program that reads another program and executes it [588a2586f952d92e2134a52f]

Citation xuất hiện trong context, nguồn Think Python 2, trang PDF 28.
Chunk định nghĩa interpreter là chương trình đọc và thực thi chương trình
khác. Đối chiếu AI: đoạn này hỗ trợ nội dung trả lời; không chỉ kiểm tra ID.

## Câu thiếu bằng chứng

Question: What exact monthly subscription price does the indexed material
state for PythonAnywhere?

Model tự yêu cầu search nguyên câu hỏi, nhận các đoạn trang PDF 24 và 33.
Chúng giới thiệu/chỉ dẫn dùng PythonAnywhere, không nêu giá thuê bao tháng.
Model trả token cuối `ABSTAIN`; ứng dụng lưu nguyên token và render:

> The retrieved passages do not provide enough evidence to answer.

Không thêm mức giá suy đoán. Việc câu này thiếu bằng chứng trong corpus
còn được ghi riêng ở `data/day7_benchmark/absence_audit.json`; không kết
luận từ top-k đơn thuần. Nhận xét nguồn này do AI thực hiện, người học cần
đối chiếu lại; `reviews_template.json` vẫn chưa được điền nhãn người chấm.

## Giữ các lần lỗi để phân tích

| Run | q01 | dev-absent-01 | Ghi nhận |
|---|---|---|---|
| 20261114_190845_020130 | error | abstain | Model sinh đáp án có nguồn nhưng thiếu trường citation khai báo lặp lại; lượt sửa định dạng sau timeout |
| 20261114_192133_580474 | answered | error | Model trả `abstain` dạng văn bản; bộ đọc cũ đòi terminal tool call nên lặp sửa định dạng |
| 20261114_193415_367280 | error | abstain | Câu trả lời trực tiếp có nguồn chưa được bộ đọc cũ nhận; lượt sửa tiếp theo chạm giới hạn token |
| 20261114_194624_573936 | answered | abstain | Nhận native terminal tool, final text có citation và token ABSTAIN tường minh sau search |

Các run lỗi giữ nguyên summary/trace cũ, không đổi thành thành công sau khi
sửa code. Bộ đọc mới chỉ lấy citation từ marker thật trong câu trả lời rồi
kiểm tra context, không tự gắn nguồn. Chỉ token ABSTAIN tường minh sau
search được render thành từ chối; văn bản không có citation không tự được
coi là abstention. Token bị cắt vẫn là lỗi.

Thử `/no_think` ở run thứ hai chưa giảm reasoning ổn định trên cấu hình
Ollama/model này; không báo đó là cải thiện tốc độ đã được chứng minh. Các
thay đổi giao thức/prompt đồng thời khác nhau nên chưa thể tách ảnh hưởng
từng biến từ bảng trên.

## Chặng còn lại

Chạy đủ 17 câu dev cho baseline và các cấu hình so sánh; đọc context,
câu trả lời, citation và lỗi; chốt pipeline trước khi chạy test. Không dùng
hai câu chạy thử hoặc trạng thái answered để báo grounded accuracy.

Lệnh chạy lại: [AGENT_SETUP_LOCAL.md](../docs/AGENT_SETUP_LOCAL.md).
