# Tái lập bài cá nhân

K5-L3A — 2A202603374 — Nguyễn Tuấn Hiếu.

Chạy lệnh từ thư mục chứa README.md và starter/. Dùng PowerShell; luôn thêm `-X utf8` trên Windows.

## 1. Kiểm tra kết quả đã lưu, không cần model

Các bản chạy thật đã được đóng gói dưới `artifacts/runs/`; từng thư mục có `traces.json`, `run_config.json`, `summary.json`. Nhãn và lý do nằm tại `report/evaluation/`. `artifacts/manifest.json` ghi SHA256 các tệp được chia sẻ. Đường dẫn máy cũ trong metadata chỉ là lịch sử, không cần tồn tại khi đọc kết quả.

```powershell
python -X utf8 -m unittest discover -s tests -v
python -X utf8 starter/verify_submission.py
```

Script kiểm tra không gọi API, không tự tạo nhãn hoặc thay đổi kết quả.

## 2. Chuẩn bị Python và corpus

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch==2.9.1 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force starter/data/day6 | Out-Null
Copy-Item artifacts/day6/chunks.json,artifacts/day6/provenance.json starter/data/day6/
```

Corpus và vector đều là snapshot gốc, có quyền chia sẻ phi thương mại; xem ATTRIBUTION.md. Không cần tải lại PDF để chấm output. Checksum corpus phải khớp protocol đã đóng băng.

## 3. Vector store

Trên máy đã có Day6, dùng database và cache cũ; có thể đặt `$env:DAY6_REPOSITORY` thành thư mục Day6 có `starter/.env`. Không commit `.env`.

Trên máy khác, tạo PostgreSQL có extension pgvector (môi trường gốc dùng image `pgvector/pgvector:0.8.7-pg16`) và một database **mới**. Đặt `$env:DATABASE_URL` bằng chuỗi kết nối của bạn. Sau đó:

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/vector_snapshot.py restore --chunks artifacts/day6/chunks.json --file artifacts/day6/vectors.json
```

Restore chỉ nhận database chưa có bảng day6_chunks; không xóa hay ghi đè bảng hiện hữu. 271 vector từ Day6 được import nguyên dạng, không tạo embedding giả.

Tải đúng embedding revision (lần đầu cần internet):

```powershell
.\.venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; print(snapshot_download('sentence-transformers/all-MiniLM-L6-v2', revision='1110a243fdf4706b3f48f1d95db1a4f5529b4d41', local_dir='starter/data/embedding'))"
$env:EMBEDDING_SNAPSHOT = (Resolve-Path starter/data/embedding).Path
```

Retriever đọc-only, so sánh nội dung toàn bộ chunk và kiểm tra lại 3 vector mẫu bằng embedding model trước khi tìm. Có thể dùng `EMBEDDING_SNAPSHOT` trỏ cache revision gốc thay vì tải lại.

## 4. Model thật và lệnh tái chạy

Cài Ollama, mở dịch vụ cục bộ ở `127.0.0.1:11434`, tải `ollama pull qwen3:4b-instruct`. Không cần API key. Digest thực nghiệm nằm trong run_config; nếu tag về sau thay đổi, ghi là môi trường tái chạy khác. Bản gốc dùng Ollama0.40.16, model digest `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`.

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/run_agent.py --model qwen3:4b-instruct --method dense --all --split dev --top-k 3 --budget 2000 --max-searches 2 --max-model-calls 5 --output starter/results/reproduced-dense-dev
.\.venv\Scripts\python.exe -X utf8 starter/run_agent.py --model qwen3:4b-instruct --method tfidf --all --split dev --top-k 3 --budget 2000 --max-searches 2 --max-model-calls 5 --output starter/results/reproduced-tfidf-dev
```

Để tái lập test của cấu hình **đã chốt**, đổi `--split dev` thành `--split test` và thư mục output thành tên mới. Đây là tái lập, không được dùng test để chỉnh lại cấu hình rồi báo là test độc lập. Không trộn các câu tốt nhất từ nhiều lần chạy.

Retrieval thuần (lặp với tfidf, dense, hybrid trên dev; chỉ baseline tfidf và dense đã chọn trên test):

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/evaluate_retrieval.py --method dense --chunks starter/data/day6/chunks.json --questions data/day7_benchmark/questions_dev.json --split dev --top-k 3 --budget 2000 --output starter/results/reproduced-retrieval-dense-dev
```

Các nhãn trong report/review_decisions.json thuộc đúng run_id gốc. Không áp lại chúng cho kết quả model của một lần chạy mới. Cần đọc nguồn và chấm lại nếu output khác.

## 5. Giới hạn

Context budget đo bằng ký tự (gồm header nguồn), khác với cửa sổ model8192 token. Output tối đa1024 token/lời gọi, 5 lời gọi và 2 search/câu, temperature0, seed42. Model local vẫn có thể khác output theo runtime/hardware. Phí dịch vụ0USD không bao gồm điện và phần cứng. Phần nâng cao100+trang đa phương thức không được tuyên bố hoàn thành.
