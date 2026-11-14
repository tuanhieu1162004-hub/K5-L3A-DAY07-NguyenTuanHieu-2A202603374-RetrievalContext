# Khắc phục lỗi hết output token trên dev

Lượt `20261114_201554_120565` đã chạy đủ 17 câu với `qwen3:4b`: 8 answered,
2 abstain, 7 error. Các câu lỗi: q05, q07, q09, q12, q13, q14, q15.
Các phản hồi bị cắt có `done_reason: length`, output token bằng giới hạn
1024. q09 chưa kịp search; các câu khác đã search nhưng chưa hoàn tất.

Đây là baseline hợp lệ cần giữ lại, không thay lỗi bằng đáp án giả và không
chỉ gộp các câu thành công từ nhiều run để báo điểm.

## Cấu hình cải thiện được thử

Đổi model chat sang `qwen3:4b-instruct`, phiên bản Instruct-2507 không sinh
reasoning riêng. Giữ nguyên corpus, query dev, dense C, top-k 3, context
2000 ký tự, 2 search, 5 model call, 1024 output token, seed và temperature.
Đây là đổi model/weights/template, phải ghi model digest mới trong báo cáo.

Nguồn: [Ollama tag](https://ollama.com/library/qwen3:4b-instruct),
[model card chính thức](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507).

Đã thử điều chỉnh template trên trọng số cũ nhưng không xác nhận được hành
vi như mong đợi; không dùng biến thể đó trong benchmark. Hai tag thử lỗi đã
được dọn, model gốc và toàn bộ trace cũ vẫn giữ nguyên. Bản Instruct chính
thức được tải riêng qua Ollama và kiểm tra trên q05, q09, dev-absent-01 trước
khi chạy toàn dev.

## Chạy lại nếu cần tái lập

Model đã có trên máy trong phiên làm việc này. Trên máy mới:

```powershell
ollama pull qwen3:4b-instruct
```

Kiểm tra API local và tool capability:

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/check_ollama.py --model qwen3:4b-instruct --chat --output starter/results/ollama-instruct-check.json
```

`thinking: null` có nghĩa dùng mặc định của model. Với tag Instruct này,
model card xác định non-thinking; cần đối chiếu thêm `thinking_characters`
và output thực tế trong trace, không chỉ nhìn badge capability của họ model.

Chạy đủ 17 câu dev, lưu riêng với baseline:

```powershell
$day6Python = "C:\Users\Admin\Downloads\K5-L3-Day06-DataIngestionEngineering-main\.venv\Scripts\python.exe"
& $day6Python -X utf8 starter/run_agent.py --model qwen3:4b-instruct --method dense --all --split dev --top-k 3 --budget 2000 --max-searches 2 --max-model-calls 5 --output starter/results/agent-dev-dense-instruct
```

Xem tổng hợp gần nhất:

```powershell
$instructRun = Get-Content starter/results/agent-dev-dense-instruct/latest.json -Raw -Encoding UTF8 | ConvertFrom-Json
$instructRun | Format-List
```

## So sánh và chấm

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/compare_agent_runs.py
```

Script kiểm tra cùng corpus checksum, câu hỏi, embedding/index, top-k,
budget và các giới hạn; đối chiếu số đếm summary với trace. Nó tạo:

- `report/agent_dev_comparison.md` và `.json`: kết quả trước/sau, token,
  thời gian, lỗi, độ phủ gold trong context; chưa tự chấm grounded answer.
- `report/agent_dev_review.md`: mỗi câu, đáp án tham chiếu, citation và
  context cuối để người chấm đối chiếu.

Độ phủ context theo gold dùng cùng quy tắc nhóm evidence của benchmark;
không thay thế điểm context 0/1/2 do người chấm đọc và giải thích.

Sao chép `reviews_template.json` trong thư mục run thành `reviews.json`,
giữ bản chấm đã có nếu thực hiện lại. Điền answer_grade (0/1/2),
citation_support, context_grade hoặc abstention_correct theo BENCHMARK.md,
kèm người/công cụ chấm và lý do. Không tự cho điểm 2 chỉ vì status=answered.

Chưa chốt pipeline cuối và chưa chạy test. Giảm lỗi kỹ thuật không đồng
nghĩa tăng độ chính xác; model có thể thêm thông tin ngoài context hoặc
gắn ID có thật vào một khẳng định không được đoạn đó hỗ trợ.

Ví dụ đã đọc ở lượt Instruct: [q13 có ID hợp lệ nhưng đoạn được dẫn chưa
hỗ trợ thứ tự đánh giá đối số](../report/agent_dev_source_notes.md).
