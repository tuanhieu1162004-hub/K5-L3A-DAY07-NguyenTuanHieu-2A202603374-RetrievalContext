# Bản nộp Day 7

**K5-L3A — 2A202603374 — Nguyễn Tuấn Hiếu**

Đọc [báo cáo chính](report/individual/2A202603374_NguyenTuanHieu.md) trước. Repo cá nhân: https://github.com/tuanhieu1162004-hub/K5-L3A-DAY07-NguyenTuanHieu-2A202603374-RetrievalContext.

| Yêu cầu phần cơ bản | Bằng chứng đã chuẩn bị |
|---|---|
| Kết nối Day 6, embedding và vector store thật | retrievers.py; artifacts/day6 gồm 271 chunk và vector C gốc; provenance và checksum |
| Ít nhất 3 phương pháp retrieval | TF-IDF, dense pgvector, hybrid RRF; 5 thí nghiệm retrieval dev |
| Benchmark ít nhất 20 câu có evidence và 4 câu thiếu evidence | Dev15+2, test mới5+2; protocol, gold theo nguồn/trang/offset và absence audit |
| Agent model thật, tool và điều kiện dừng | Ollama Qwen3 Instruct, search/final/abstain, giới hạn lượt gọi và context; artifacts/runs |
| Ít nhất 2 cải thiện, chọn trên dev trước test | Budget800→2000, top-k8/b4000, dense/hybrid, model Instruct; report/selection.json trước mọi test run |
| Baseline và cấu hình chọn trên test | TF-IDF và dense cùng model/giới hạn; mỗi run7câu, giữ nguyên cả lỗi |
| Chấm context, answer, citation, abstention | report/evaluation, chấm đủ5câu có đáp án+2câu thiếu bằng chứng cho mỗi test run; nhãn do AI đọc nguồn |
| Tái lập và báo cáo cá nhân | docs/REPRODUCE_SUBMISSION.md; report/individual/2A202603374_NguyenTuanHieu.md |
| Kiểm thử | 36/36 unit test đạt; verify_submission.py xác nhận62artifact, checksum, nhãn và chốt trước test |
| Quyền sử dụng / không nộp secret | ATTRIBUTION.md; chỉ đóng gói allowlist, không .env/venv/cache model |

**Kết quả không hoàn hảo đã được công bố:** dense test có1lỗi final protocol và1câu không grounded; TF-IDF test từ chối nhầm1câu có đáp án. Không sửa hoặc chạy lại test để chọn kết quả tốt nhất. Phần cơ bản không có ngưỡng accuracy tuyệt đối.

**Giới hạn:** nhãn do Codex (AI) chấm, chưa được người học xác nhận độc lập. Nhánh bonus100+trang đa phương thức không thực hiện. Các file smoke/dev cũ ghi trạng thái tại thời điểm thực nghiệm; báo cáo chính và bản chấm cuối mới là tổng kết.

Việc nộp link lên hệ thống của lớp theo thông báo giảng viên do sinh viên thực hiện; phiên làm việc này không có địa chỉ hay quyền truy cập hệ thống nộp bài của lớp.
