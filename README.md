# Day 7 — Agentic RAG — Nguyễn Tuấn Hiếu

**K5-L3A · 2A202603374**

Bài cá nhân: [báo cáo chính](report/individual/2A202603374_NguyenTuanHieu.md) · [tái lập trên máy khác](docs/REPRODUCE_SUBMISSION.md) · [quyết định chọn cấu hình trước test](report/selection.json) · [nguồn và quyền sử dụng](ATTRIBUTION.md).

Ba phương pháp thật: TF-IDF, dense pgvector Day6, hybrid RRF. Agent dùng Qwen3 Instruct qua Ollama local, không cần API key. Benchmark24câu dev/test; trace thực nghiệm được chia sẻ trong `artifacts/`, nhãn và lý do trong `report/evaluation/`. Nhãn do Codex (AI) đọc nguồn, không giả nhận là nhãn người học xác nhận. Phần bonus đa phương thức100+trang không được thực hiện.

Các liên kết bên dưới ghi lịch sử triển khai; báo cáo chính và artifact cuối là tài liệu nộp bài.

Tiến độ triển khai trong workspace: [benchmark Think Python, lệnh chạy và kết quả TF-IDF trên dev](docs/BENCHMARK_SETUP.md).
[Chạy dense trên pgvector Day 6 và hybrid RRF](docs/RETRIEVAL_SETUP.md) · [Kết quả so sánh ba phương pháp trên dev](report/retrieval_dev.md).
[Bước tiếp: chuẩn bị model chat cục bộ](docs/LOCAL_MODEL_SETUP.md).
[Nối model với retrieval tool và chạy agent thật](docs/AGENT_SETUP_LOCAL.md).
[Nhật ký chạy thử agent trên hai câu dev](report/agent_smoke.md).
[Khắc phục lỗi hết token và so sánh agent trên toàn dev](docs/AGENT_DEV_IMPROVEMENT.md).

**Bài cá nhân · Python 3.11+ · tiếp nối Day 6**

Dùng embedding và vector store từ Day 6 để xây một agent biết tìm bằng chứng, trả lời có nguồn và nhận biết khi không đủ thông tin. Bạn tự chọn kiến trúc, số tool và cách tổ chức retrieval.

> **Tùy chọn:** [Gợi ý dùng AI để lập trình](AGENT_SETUP.md) giúp bạn làm lab; phần này không bắt buộc và không tính điểm.

## Bài cần làm

![Agent tìm tài liệu trong kho Day 6 và trả lời có nguồn](assets/retrieval-pipeline.svg)

1. Kết nối dữ liệu, embedding và vector store Day 6.
2. Xây agent dùng model thật và ít nhất một khả năng truy xuất dữ liệu. Agent có thể dùng nhiều tool và nhiều lượt gọi.
3. Thử **ít nhất 3 phương pháp retrieval khác nhau**, trong đó có dense retrieval dùng vector store Day 6. Tự chọn các phương pháp còn lại; xem [gợi ý](GUIDE.md#2-thử-các-phương-pháp-retrieval).
4. Thử nhiều cấu hình, benchmark, phân tích lỗi và chọn cấu hình tốt trên **dev**; sau đó đánh giá trên **test**.

Benchmark tối thiểu có **24 câu**: dev gồm 15 câu có đáp án và 2 câu thiếu bằng chứng; test gồm 5 câu có đáp án và 2 câu thiếu bằng chứng. Xem [benchmark](BENCHMARK.md) và [rubric](RUBRIC.md).

## Thử thách nâng cao · +15 điểm

Index một tài liệu thực tế từ **100 trang** có bảng, ảnh và biểu đồ; xây agent truy xuất và trả lời các câu hỏi về nội dung đó. Hoàn thành [thử thách nâng cao](ADVANCED.md) và đạt **ít nhất 90% benchmark test** để nhận 15 điểm bonus. Phần cơ bản tối đa 85 điểm; toàn bài tối đa 100 điểm.

## Bắt đầu

1. Đọc [hướng dẫn](GUIDE.md), [rubric](RUBRIC.md) và [quy tắc](RULES.md).
2. Tạo repo cá nhân theo [cách nộp bài](SUBMISSION.md), chuẩn bị đầu ra Day 6 và model hỗ trợ tool calling.
3. Dùng hoặc thay thế [starter](starter/README.md); bạn cần kết nối model và vector store thật.
4. Chạy `python -m unittest discover -s tests -v`. Test mock chỉ kiểm tra code, không phải benchmark agent thật.

![Các bước thử nghiệm trên dev và đánh giá trên test](assets/experiment-loop.svg)

Nộp code, cách chạy, cấu hình, benchmark, trace và [báo cáo](report/individual/MSSV_HoTen.md). Thời gian ở [checkpoints](CHECKPOINTS.md) là gợi ý, có thể điều chỉnh theo lớp và phạm vi thử nghiệm.
