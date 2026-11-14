# Chạy agent thật với Ollama và pgvector

Cập nhật sau khi chạy đủ dev: bản thinking gặp 7 lỗi hết token. Xem
[cấu hình Instruct và hướng dẫn chấm](AGENT_DEV_IMPROVEMENT.md) để tái lập
phương án cải thiện. Các lệnh bên dưới vẫn giữ để tái lập baseline ban đầu.

Model chat `qwen3:4b` chọn tool và trả lời. Embedding MiniLM 384 chiều của
Day 6 biến query thành vector để tìm tài liệu. Đây là hai model khác nhau.

## 1. Kiểm tra model chat

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/check_ollama.py --model qwen3:4b --chat
```

Script đọc `thinking` từ model đã cài. Model hiện quảng bá `values: [true]`;
dùng `think: true` để phân tách reasoning và câu trả lời cuối. Giới hạn kiểm
tra là 256 output token, bao gồm token suy nghĩ. Chỉ đạt `ready` khi có câu
trả lời `OK` hoàn chỉnh. `done: true` chưa đủ; `done_reason: length` là lỗi.

## 2. Chạy hai câu dev để kiểm tra tích hợp

Chạy từ thư mục lab 7. Dùng Python lab 6 đã có thư viện embedding/database:

```powershell
$day6Python = "C:\Users\Admin\Downloads\K5-L3-Day06-DataIngestionEngineering-main\.venv\Scripts\python.exe"
& $day6Python -X utf8 starter/run_agent.py --model qwen3:4b --method dense --ids q01 dev-absent-01 --split dev --top-k 3 --budget 2000 --max-searches 2 --max-model-calls 5 --max-output-tokens 1024 --output starter/results/agent-smoke-dense
```

Đây là chạy thử hai câu dev, không phải điểm benchmark agent đầy đủ. Mỗi
lần chạy tạo thư mục thời gian riêng để giữ trace/nhãn cũ. Kết quả mới nhất
nằm trong `starter/results/agent-smoke-dense/latest.json`.

Kết quả hai câu đã chạy thật, gồm cả các lượt lỗi trước khi sửa giao thức:
[nhật ký tích hợp](../report/agent_smoke.md). Lượt xác nhận cuối có một
answered, một abstain và không có error; mất tổng khoảng 6,5 phút trên CPU.

```powershell
$agentRun = Get-Content starter/results/agent-smoke-dense/latest.json -Raw -Encoding UTF8 | ConvertFrom-Json
$agentTraces = Get-Content (Join-Path $agentRun.run_directory 'traces.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$agentTraces | Select-Object query_id,status,answer,citations | Format-List
```

Lưu mảng JSON vào biến trước khi Select-Object để PowerShell liệt kê từng
trace đúng cách. Nối trực tiếp ConvertFrom-Json với Select-Object có thể
hiển thị các trường trống trên một số phiên bản PowerShell.

## Có cần API key không?

Cấu hình này không cần API key. Code đã gọi HTTP API cục bộ của Ollama tại
`http://127.0.0.1:11434/api/chat`; model Qwen3 chạy trên máy. MiniLM và
pgvector cũng chạy cục bộ. Các token trong summary là số đo sử dụng,
không phải hóa đơn dịch vụ model bên ngoài.

Chỉ khi đổi sang dịch vụ model online yêu cầu xác thực mới cần cấu hình
key theo nhà cung cấp. Đề cho phép model cục bộ; không bắt buộc API trả phí.

## 3. Cách hoạt động

Model gọi native tools: `search_documents(query)` để tìm evidence;
`final_answer(answer)` để kết thúc có nguồn; `abstain(reason)`
để từ chối khi thiếu bằng chứng. Model phải yêu cầu tìm trước khi kết thúc.

Citation được lấy từ marker thật trong câu trả lời của model rồi đối chiếu
context. Không bắt model lặp lại cùng ID trong một trường arguments khác,
không tạo citation từ gold hoặc tự gắn nguồn khi model chưa nêu nguồn.

Sau search, model cũng có thể trả lời trực tiếp bằng assistant message.
Bộ đọc áp dụng cùng quy tắc citation; nếu có tiền tố riêng một dòng
`final_answer`, chỉ bỏ tiền tố định dạng đó và giữ nội dung gốc trong
`raw_model_final`. Văn bản không có citation hợp lệ và không phải đúng token
ABSTAIN vẫn là lỗi định dạng, không được tự chuyển thành từ chối.

Mặc định `--reasoning-mode default` dùng chế độ reasoning của model. Có thể
thử `--reasoning-mode no-think` để thêm soft switch `/no_think` vào system
prompt theo hướng dẫn Qwen3; API vẫn dùng `think: true` theo capability.
Thử nghiệm local cho thấy soft switch này chưa giảm reasoning ổn định với
tool calling, nên không coi nó là cải thiện đã được chứng minh. Cấu hình
thực tế được ghi trong run_config; không cần tải model mới để thử hai chế độ.

Một số phản hồi trả đúng token `ABSTAIN` thay vì native tool call. Sau ít
nhất một search, bộ điều phối chấp nhận riêng token đó là quyết định từ chối
của model, lưu `raw_model_final` và render thông báo thiếu bằng chứng. Không
suy luận abstention từ việc thiếu citation hoặc từ nhãn answerable.

Query đầu được hướng dẫn giữ nguyên câu hỏi; query viết lại được đánh dấu
`query_is_original` trong trace. Kết quả retrieval query gốc đã có ở bước
so sánh ba phương pháp; cần báo riêng khi agent viết lại/tìm nhiều lượt.

Ứng dụng chạy tool thật rồi gửi context có nguồn trở lại model. Filter lấy
từ câu hỏi, không lấy từ gold. Giới hạn số search/model call là cấu hình
thử nghiệm, không phải giới hạn bắt buộc của đề.

Context giữ kết quả lượt mới trước, sau đó chunk cũ chưa trùng, trong budget
ký tự. Tool message cũ được rút gọn; chỉ một context tích lũy hiện hành được
gửi vào model. Trace giữ nguyên kết quả/context từng lượt để kiểm tra.

`run_agent.py` chỉ đưa question và filter đã có vào agent/retriever. ID/split
gắn trace; gold, expected_answer, answerable không đi vào model. Chỉ phần
tạo biểu mẫu đánh giá bên ngoài agent sử dụng answerable.

## 4. Đọc đầu ra và chấm

Mỗi thư mục run có `run_config.json` (digest/version, tham số, prompt,
tool schema, corpus checksum), `traces.json` (model/tool call, query,
context, câu trả lời, citation, token, thời gian, lỗi), `cases.json`,
`reviews_template.json` và `summary.json`.

Trace lưu độ dài reasoning, token, final và tool call; không xuất nội dung
reasoning thành câu trả lời hoặc nhãn grounded answer. `summary.json` chỉ
đếm answered/abstain/error, chưa tự chấm nội dung đúng hay sai.

Citation được kiểm tra ID trong context hiện tại và marker `[chunk-id]`.
Điều đó chưa chứng minh nguồn hỗ trợ khẳng định; cần đọc đối chiếu. Lỗi hết
token là `error`, không biến thành đáp án/abstention. Lỗi model/database
được ghi riêng. Lỗi kết nối không được thay bằng kết quả giả.

Model chạy trên CPU có thể mất vài phút cho mỗi câu. Timeout mặc định là
300 giây mỗi lời gọi, tối đa 1024 output token gồm reasoning. Trace đếm cả
HTTP attempt lỗi; nếu không nhận được token usage thì ghi rõ số lượt có
token không biết, không coi token của request thất bại là 0 đã đo được.

Sao chép `reviews_template.json` thành `reviews.json` để chấm. Điền
`answer_grade` 0/1/2 hoặc `abstention_correct`, nhãn `citation_support` cho
từng citation, `context_grade` 0/1/2, lý do và người/công cụ chấm. Không ghi
nhãn AI thành nhãn do người học tự chấm.

## 5. Bước tiếp theo

Sau khi tích hợp chạy được, dùng `--all --split dev` thay `--ids ...` để
chạy đủ 17 câu. So sánh baseline/các cấu hình cải thiện và chấm trên dev,
chốt pipeline rồi mới chạy test. Không dùng hai câu chạy thử để báo độ
chính xác toàn benchmark.

Nguồn API: [tool calling](https://docs.ollama.com/capabilities/tool-calling),
[chat](https://docs.ollama.com/api/chat),
[thinking metadata](https://docs.ollama.com/api-reference/show-model-details.md).
Soft switch: [hướng dẫn chính thức Qwen3](https://qwenlm.github.io/blog/qwen3/#advanced-usages).
