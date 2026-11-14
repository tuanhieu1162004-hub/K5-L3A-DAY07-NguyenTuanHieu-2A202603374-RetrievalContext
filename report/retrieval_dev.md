# So sánh retrieval trên dev

Cùng 271 chunk C của Day 6, 17 câu dev (15 có đáp án + 2 thiếu bằng chứng), top-k=3 và budget=2.000 ký tự.

| Phương pháp | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Median/query (ms) | Khởi tạo (s) |
|---|---|---|---|---:|---:|
| tfidf | 5/15 (33.3%) | 8/15 (53.3%) | 8/15 (53.3%) | 0.386 | 0.014 |
| dense | 12/15 (80.0%) | 14/15 (93.3%) | 14/15 (93.3%) | 14.281 | 5.789 |
| hybrid | 10/15 (66.7%) | 13/15 (86.7%) | 13/15 (86.7%) | 15.199 | 5.300 |

TF-IDF: cosine lexical; dense: model MiniLM 384 chiều + pgvector cosine exact; hybrid: RRF, 20 candidate mỗi nhánh, constant=60.
Nguồn, câu hỏi, filter, checksum và số liệu trace đã được script đối chiếu. Database dense/hybrid dùng giao dịch chỉ đọc.

Thời gian khởi tạo gồm nạp model và kiểm tra tương thích; lần đầu và lần sau chịu ảnh hưởng cache hệ điều hành. Chưa lặp thí nghiệm timing để kết luận tốc độ.
Phí dịch vụ của ba retriever là 0 USD; không bao gồm điện/máy. Chưa có chi phí hoặc chất lượng LLM.

## Đối chiếu hai câu dev

| Query | Phương pháp | Hit@1 | Hit@3 | Context đủ evidence |
|---|---|---|---|---|
| q05 | tfidf | 0 | 1 | 1 |
| q05 | dense | 1 | 1 | 1 |
| q05 | hybrid | 1 | 1 | 1 |
| q07 | tfidf | 0 | 0 | 0 |
| q07 | dense | 0 | 1 | 1 |
| q07 | hybrid | 0 | 1 | 1 |

## Giới hạn và phần còn lại

Các chỉ số đo độ phủ evidence, không phải độ chính xác câu trả lời. Hai câu thiếu bằng chứng có trace nhưng không vào mẫu số; chưa chấm abstention.
Bảng này chỉ đánh giá retrieval. Agent Ollama đã có chương trình chạy riêng; chưa chốt pipeline cuối và chưa chạy test. Nhãn benchmark do AI chuẩn bị, phần đối chiếu nguồn của người học còn chờ thực hiện.
Lệnh chạy và điều kiện tái lập: [RETRIEVAL_SETUP.md](../docs/RETRIEVAL_SETUP.md).
