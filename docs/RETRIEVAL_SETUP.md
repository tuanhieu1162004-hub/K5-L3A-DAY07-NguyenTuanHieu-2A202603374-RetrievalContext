# So sánh TF-IDF, dense và hybrid

Kết quả chạy thật trên dev được lưu trong [bảng so sánh](../report/retrieval_dev.md).

Chạy từ thư mục lab 7 có `starter/`, `data/` và `tests/`. Dùng cùng corpus
271 chunk của strategy C, câu hỏi dev và metadata filter đã chốt. Không đưa
gold hoặc đáp án vào retriever. Bộ test được giữ cho bước sau khi chọn pipeline.

## 1. Python và model dùng lại từ lab 6

TF-IDF và unit test chạy được bằng `.venv` của lab 7. Dense và hybrid dùng
môi trường lab 6 đã có PyTorch, Sentence Transformers, psycopg và dotenv:

```powershell
$day6Python = "C:\Users\Admin\Downloads\K5-L3-Day06-DataIngestionEngineering-main\.venv\Scripts\python.exe"
& $day6Python --version
```

PostgreSQL của lab 6 cần đang chạy. Nếu đã tắt, khởi động Docker Desktop và
chạy lệnh sau để bật lại đúng dịch vụ/volume:

```powershell
docker compose -p day6_student_starter -f "C:\Users\Admin\Downloads\K5-L3-Day06-DataIngestionEngineering-main\K5-L3-Day06-DataIngestionEngineering-main\starter\docker-compose.yml" up -d --wait
```

Model: `sentence-transformers/all-MiniLM-L6-v2`, revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, CPU, vector chuẩn hóa 384 chiều.
Chương trình đọc snapshot model đã tải ở lab 6; chỉ dùng file cục bộ.
Thông tin kết nối đọc từ `starter/.env` của lab 6, không ghi URL/password
vào kết quả. Kết nối database dùng giao dịch `REPEATABLE READ READ ONLY`.

Khi khởi tạo, kiểm tra toàn bộ ID, nội dung, source, page, metadata và số
chiều vector khớp corpus đã chốt. Tính lại embedding của ba chunk chọn theo
ID để kiểm tra với vector lưu trong database, sai số tuyệt đối tối đa cho
phép 0.0001. Cả ba mẫu phải đạt mới chạy query. Model/cache lab 6 không bị
ghi lại; thư mục cache tạm của chương trình nằm trong lab 7.

## 2. Chạy so sánh trên cùng cấu hình

Cấu hình đối chiếu: lấy top-3, context budget 2.000 ký tự (gồm header nguồn).

TF-IDF:

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/evaluate_retrieval.py --method tfidf --chunks starter/data/day6/chunks.json --questions data/day7_benchmark/questions_dev.json --split dev --top-k 3 --budget 2000 --output starter/results/dev-tfidf-k3-b2000
```

Dense:

```powershell
& $day6Python -X utf8 starter/evaluate_retrieval.py --method dense --chunks starter/data/day6/chunks.json --questions data/day7_benchmark/questions_dev.json --split dev --top-k 3 --budget 2000 --output starter/results/dev-dense-k3-b2000
```

Hybrid:

```powershell
& $day6Python -X utf8 starter/evaluate_retrieval.py --method hybrid --candidate-k 20 --rrf-constant 60 --chunks starter/data/day6/chunks.json --questions data/day7_benchmark/questions_dev.json --split dev --top-k 3 --budget 2000 --output starter/results/dev-hybrid-k3-b2000
```

Mỗi lần chạy ghi `summary.json` và `traces.json`; chạy lại cùng output sẽ ghi
đè kết quả cũ. `index_seconds` gồm thời gian khởi tạo/model/kiểm tra vector;
`median_ms` đo retrieval + pack context từng query. Không so trực tiếp thời
gian khởi tạo model với độ trễ một câu hỏi. Các query dense được embedding
thật mỗi lần, không đọc cache query Day 6. Không có lời gọi LLM ở giai đoạn này.

Sau khi có đủ ba kết quả, tạo lại bảng đối chiếu:

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/compare_retrieval.py
```

Script kiểm tra cùng corpus, câu hỏi, filter, top-k, budget và đối chiếu số
đếm trong summary với từng trace trước khi ghi `report/retrieval_dev.md`/`.json`.

## 3. Cách xếp hạng

- TF-IDF: cosine với IDF học từ toàn bộ corpus chung; lọc metadata trước top-k.
- Dense: embed query bằng model tương thích Day 6; SQL cosine exact trong
  bảng `day6_chunks`, `strategy='C'`; lọc metadata trước top-k.
- Hybrid: dense và TF-IDF mỗi bên lấy tối đa 20 ứng viên. Với mỗi chunk,
  điểm RRF = tổng `1 / (60 + rank)` từ các danh sách có chứa chunk; rank
  bắt đầu từ 1. Không cộng trực tiếp raw cosine score của hai retriever.
  Điểm hòa được sắp theo ID. Sau fusion, lấy top-k và đóng gói context.

Trace hybrid lưu `component_ranks`, `component_scores` của kết quả và hai
danh sách `dense_candidates`/`tfidf_candidates` trong `retrieval_details`.
Query và filter được giữ nguyên ở cả hai nhánh; không viết lại query.

Theo quy tắc benchmark, báo top-1 và top-3 với cùng định nghĩa đủ evidence;
context cuối có thể chứa hơn ba đoạn nếu cấu hình top-k lớn hơn. Các câu
thiếu bằng chứng không vào mẫu số retrieval và chưa được chấm abstention.

## 4. Thử cấu hình context lớn hơn

Đổi `--top-k 8 --budget 4000` và dùng output riêng có đuôi `k8-b4000`.
Với hybrid, giữ `--candidate-k 20 --rrf-constant 60`. So sánh với TF-IDF
k=8/budget=4000 đã có; giữ nguyên corpus, filter và bộ câu hỏi dev.

## 5. Kiểm tra code và bước còn lại

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

Unit test kiểm tra RRF theo rank, điểm khác thang đo, ID trùng, corpus xung
đột, query/filter truyền đúng và quy tắc evidence. Kết quả benchmark dense
phải đến từ model và pgvector thật, không dùng stub trong test để báo điểm.

Chưa có đánh giá grounded answer/citation/abstention cho đến khi nối model
chat thật và chấm nguồn; [agent Ollama cục bộ](AGENT_SETUP_LOCAL.md) đã có
chương trình chạy riêng và trace. Chọn pipeline bằng dev theo protocol, rồi mới chạy baseline và
pipeline đã chọn trên test. Kết quả chất lượng retrieval chưa đủ để kết luận
cấu hình cuối tốt nhất cho agent. Tham khảo thêm [benchmark](BENCHMARK_SETUP.md).
