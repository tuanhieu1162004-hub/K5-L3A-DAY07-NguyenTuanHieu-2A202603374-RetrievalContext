# Nguồn và quyền sử dụng

- Đề bài và starter: VinUni-AI20k, https://github.com/VinUni-AI20k/K5-L3-Day07-Retrieval-Context-Engineering. Giữ nguyên các tài liệu yêu cầu và ghi nhận phần mở rộng của bài cá nhân.
- Corpus: Allen B. Downey, **Think Python, Second Edition**, Green Tea Press. https://greenteapress.com/thinkpython2/thinkpython2.pdf. Tài liệu ghi giấy phép **Creative Commons Attribution–NonCommercial 3.0 Unported** (https://creativecommons.org/licenses/by-nc/3.0/). Các trích đoạn, chunk, evidence và vector được chia sẻ trong bài tập phi thương mại với ghi nhận tác giả. Không áp giấy phép phần mềm cho nội dung sách.
- Xử lý từ Day 6: trích xuất text và chia chunk; giữ lỗi layout/spacing của bản xuất để tái lập. Phạm vi 48 trang có nội dung, PDF23–71 trừ PDF38; chương1–5, 271 chunk chiến lược C. Sách đầy đủ 244 trang nhưng bài này **không** index toàn bộ sách.
- Embedding: sentence-transformers/all-MiniLM-L6-v2, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; truy xuất dùng vector gốc Day6, không gửi sách tới API ngoài.
- Model agent: Ollama `qwen3:4b` cho thử nghiệm ban đầu, `qwen3:4b-instruct` cho so sánh cuối. Không đóng gói trọng số model trong Git.
- Codex (AI) hỗ trợ code, benchmark mới, phân tích và chấm đối chiếu nguồn. Các nhãn AI được ghi rõ; không giả nhận là nhãn do Nguyễn Tuấn Hiếu xác nhận. Người học chịu trách nhiệm đọc và giải thích kết quả khi nộp.
