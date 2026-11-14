# Chuẩn bị model chat cục bộ

Retrieval đã chạy thật với ba phương pháp. Agent còn cần model chat biết gọi
tool; embedding MiniLM hiện có chỉ dùng để tìm vector, không sinh câu trả lời.

## Cấu hình đã kiểm tra

Máy Windows 11, RAM khoảng 15,6 GB, CPU Intel Core Ultra 5 115U, GPU Intel
Graphics tích hợp. Chọn thử `qwen3:4b` để bắt đầu, chưa chọn dựa trên kết quả
benchmark. File model khoảng 2,5 GB, có hỗ trợ tool calling. Tốc độ và chất
lượng phải đo khi chạy thật; độ phủ evidence 14/15 của dense không phải
độ chính xác của model chat.

Nguồn chính thức: [Ollama Windows](https://docs.ollama.com/windows),
[qwen3:4b](https://ollama.com/library/qwen3:4b),
[tool calling](https://docs.ollama.com/capabilities/tool-calling).

## 1. Cài Ollama

Tải bộ cài Windows từ https://ollama.com/download/windows, mở file setup và
cài theo hướng dẫn. Sau khi cài, mở Ollama từ Start menu. Đóng terminal cũ,
mở PowerShell mới để nhận PATH vừa được cài.

```powershell
ollama --version
```

Nếu báo không nhận diện lệnh, kiểm tra bộ cài đã hoàn tất và mở lại terminal.
Ứng dụng thường cài tại `%LOCALAPPDATA%\Programs\Ollama`.

## 2. Tải model cục bộ

```powershell
ollama pull qwen3:4b
ollama ls
```

Chờ tải xong; danh sách cần có `qwen3:4b`. Chạy model cục bộ này không yêu
cầu API key. Tránh chọn tag `:cloud` trong quy trình local này.

Nếu CLI báo không kết nối được server, mở Ollama từ Start menu. Nếu vẫn
chưa có server, chạy `ollama serve` trong terminal riêng và giữ terminal đó mở.

## 3. Kiểm tra từ lab 7

Quay lại thư mục có `starter/`, `data/` và `.venv` của lab 7:

```powershell
cd "C:\Users\Admin\Downloads\K5-L3-Day07-Retrieval-Context-Engineering-main\K5-L3-Day07-Retrieval-Context-Engineering-main"
.\.venv\Scripts\python.exe -X utf8 starter/check_ollama.py --model qwen3:4b --chat
```

Script chỉ dùng thư viện chuẩn Python. Nó đọc version, model digest, kích
thước, capability của model và gửi một câu ngắn yêu cầu trả lời OK. Không
đọc corpus/gold, không cài/tải gì và không chạy câu hỏi benchmark.

Khi thành công, `status` là `ready`, `chat_tested` là `true`,
`tool_calling_advertised` là `true`, và có `chat_response` thực tế. Kết quả
lưu tại `starter/results/ollama-check.json`. Digest giúp ghi lại đúng model
đã dùng dù tag có thể được cập nhật về sau.

Bản kiểm tra hiện đọc `thinking` theo capability thực tế, dùng đủ token và
kiểm tra `done_reason`: câu trả lời bị cắt sẽ báo lỗi thay vì báo `ready`.
Sau khi model sẵn sàng, xem [cách chạy agent thật](AGENT_SETUP_LOCAL.md).

`tool_calling_exercised` vẫn là `false`: đọc capability không chứng minh
agent đã gọi retrieval tool. Phần đó được kiểm tra riêng bằng `starter/run_agent.py`.
Nếu lỗi, script trả exit code 1, ghi `status: error` và nguyên nhân; không
thay bằng câu trả lời giả.

## Bước sau

Nối model với search tool của lab 7, chạy thử một câu dev có đáp án và một
câu dev thiếu bằng chứng, lưu lời gọi model/tool, context cuối, token,
thời gian, câu trả lời và citation. Sau đó so sánh các cấu hình agent trên
dev trước khi chốt và chạy test. Chấm nguồn/citation bằng cách đọc đối chiếu.

API tham khảo: [chat](https://docs.ollama.com/api/chat),
[model details](https://docs.ollama.com/api-reference/show-model-details.md),
[model list](https://docs.ollama.com/api/tags).
