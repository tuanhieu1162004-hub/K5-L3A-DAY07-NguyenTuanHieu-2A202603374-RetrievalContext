# Báo cáo Day 7 — Nguyễn Tuấn Hiếu

**Lớp:** K5-L3A · **MSSV:** 2A202603374

**Repo:** https://github.com/tuanhieu1162004-hub/K5-L3A-DAY07-NguyenTuanHieu-2A202603374-RetrievalContext

## Dữ liệu và benchmark

Nguồn: Think Python 2e — Allen B. Downey, Green Tea Press, CC BY-NC 3.0. PDF gốc 244 trang; phạm vi thực tế 48 trang có nội dung (PDF 23–71 trừ 38), chương 1–5. Tái sử dụng 271 chunk và vector chiến lược C từ Day 6; không tuyên bố index toàn bộ sách. Attribution và quyền chia sẻ phi thương mại: [ATTRIBUTION](../../ATTRIBUTION.md).

Vector store PostgreSQL 16/pgvector 0.8.7; exact cosine, không ANN. Embedding all-MiniLM-L6-v2 revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41, 384 chiều, normalize=True, CPU. So sánh toàn bộ ID/text/metadata và 3 vector mẫu trước khi truy xuất; snapshot repeatable-read/read-only. Vector gốc và corpus được đóng gói để khôi phục trên database mới.

Benchmark 24 câu: dev 15 có đáp án+2 thiếu bằng chứng, test mới 5+2. Giữ riêng test từ trước thực nghiệm; test Day 6 không được tái dùng. `data/day7_benchmark/protocol.json` đóng băng checksum. Khớp evidence theo nguồn, trang và offset; chỉ gộp whitespace khi chấm. OR giữa các gold_sets, AND giữa các fragment trong một nhóm. q07 cần nhiều chunk; không giảm yêu cầu chỉ để tăng điểm.

Câu thiếu bằng chứng được kiểm tra theo toàn bộ phạm vi corpus và các đoạn liên quan trong absence_audit.json, không suy từ top-k trống. Nhãn và phân tích được Codex (AI) đối chiếu nguồn; **chưa có xác nhận chấm của người học**. Đây là giới hạn của đánh giá, không được gọi là nhãn human-verified.

## Retrieval và thử nghiệm

| Cấu hình | Phương pháp / context | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Median/query / khởi tạo |
|---|---|---|---|---|---|---|
| dev-tfidf-k3-b800 | tfidf; k=3; 800 ký tự | dev | 5/15 (33.3%) | 8/15 (53.3%) | 5/15 (33.3%) | 0.402 ms / 0.009 s |
| dev-tfidf-k3-b2000 | tfidf; k=3; 2000 ký tự | dev | 5/15 (33.3%) | 8/15 (53.3%) | 8/15 (53.3%) | 0.386 ms / 0.014 s |
| dev-tfidf-k8-b4000 | tfidf; k=8; 4000 ký tự | dev | 5/15 (33.3%) | 8/15 (53.3%) | 12/15 (80.0%) | 0.436 ms / 0.010 s |
| dev-dense-k3-b2000 | dense; k=3; 2000 ký tự | dev | 12/15 (80.0%) | 14/15 (93.3%) | 14/15 (93.3%) | 14.281 ms / 5.789 s |
| dev-hybrid-k3-b2000 | hybrid; k=3; 2000 ký tự | dev | 10/15 (66.7%) | 13/15 (86.7%) | 13/15 (86.7%) | 15.199 ms / 5.300 s |
| test-tfidf-k3-b2000 | tfidf; k=3; 2000 ký tự | test | 2/5 (40.0%) | 4/5 (80.0%) | 4/5 (80.0%) | 1.943 ms / 0.018 s |
| test-dense-k3-b2000 | dense; k=3; 2000 ký tự | test | 2/5 (40.0%) | 4/5 (80.0%) | 4/5 (80.0%) | 49.801 ms / 17.775 s |

Phí dịch vụ tất cả cấu hình 0 USD; chưa tính điện/phần cứng. Timing một lần chạy, không phải trung bình nhiều lần đo. Hai phép đo retrieval test chạy trong lúc agent dense test hoạt động trên cùng CPU, nên timing test có nhiễu tải; không dùng chúng để kết luận tốc độ cải thiện. Query gốc giữ nguyên; filter do ứng dụng cung cấp, không suy từ gold. Cùng corpus và cutoff 3 để so sánh ranking. Hybrid lấy 20 candidate/method, RRF 1/(60+rank), không cộng raw score.

### Giả thuyết, hai cấu hình cải thiện và lựa chọn

1. TF-IDF k3/b800 → k3/b2000: tăng budget để giảm rơi evidence khi pack context; context 5/15 →8/15, ranking không đổi. k8/b4000 nâng context lên 12/15 nhưng dùng nhiều ký tự hơn. q07 cần thêm đoạn ngoài top-3.
2. Dense k3/b2000: giả thuyết embedding nhận đúng nghĩa hơn lexical; Hit1 5/15→12/15, Hit3/context 8/15→14/15. Hybrid RRF là phương pháp thứ ba, chỉ đạt 13/15 context, nên không chọn chỉ vì phức tạp hơn.
3. Agent qwen3:4b → qwen3:4b-instruct, cùng dense và giới hạn: lỗi 7/17→0/17, output 21913→1865 token, tổng thời gian 73→11 phút. Đây là đổi model/weights/template, tách khỏi so sánh retrieval. Giữ run cũ để thấy cả lỗi token limit.

Baseline cuối: TF-IDF + qwen3:4b-instruct, k3/b2000. Cấu hình chọn: dense + cùng model và giới hạn. Chọn dựa trên grounded answer/citation dev, sau đó evidence và thời gian. Quyết định, thời điểm, checksum code và điều kiện test: [selection.json](../selection.json). Không chỉnh cấu hình sau khi xem test; không ghép câu tốt nhất từ nhiều lần chạy.

## Agent và đánh giá nguồn

Model thật qua Ollama local 0.40.16; không key/dịch vụ cloud. Tool search_documents, final_answer, abstain. Trước quyết định cuối phải có search do model gọi. Prompt yêu cầu search đầu nguyên văn nhưng model có thể viết lại; runner ghi query thật và query_is_original, không cưỡng chế câu gốc. Bảng retrieval thuần phía trên luôn dùng query gốc; context/answer agent dưới đây đánh giá pipeline thực tế, không gộp vào ranking query gốc. Tối đa 2 search / 5 model call mỗi câu, output 1024 token, context model 8192, temperature 0 / seed 42. Pack chunk mới trước, sau đó chunk cũ duy nhất, tổng 2000 ký tự cả header. Tool context cũ được rút gọn; trace giữ nguyên. Lỗi token/protocol/provider được ghi riêng, không biến thành từ chối giả.

Grounded 0=sai/thiếu evidence,1=một phần,2=đúng và đủ trong final context. Citation hợp lệ cần ID có trong context **và** hỗ trợ toàn bộ khẳng định đi kèm. Context 0=không có evidence yêu cầu,1=thiếu điều kiện/nguồn,2=đủ. Một câu có thể đúng theo context nhưng citation gắn sai vẫn bị trừ citation. Không coi answered là correct.

| Agent / split | Tool use | Model calls / searches | Grounded 0/1/2; mean /2 | Citation hỗ trợ | Câu có citation | Từ chối đúng | Từ chối nhầm qua đọc nội dung | Lỗi |
|---|---|---|---|---|---|---|---|---|
| tfidf-dev | 15/15 (100.0%) | 44 / 17 | 4/1/8; 1.308/2 | 11/16 (68.8%) | 13/13 (100.0%) | 2/2 (100.0%) | 1/13 (7.7%) | 2 |
| dense-dev | 17/17 (100.0%) | 41 / 17 | 1/2/12; 1.733/2 | 15/19 (78.9%) | 15/15 (100.0%) | 2/2 (100.0%) | 0/15 (0.0%) | 0 |
| tfidf-test | 7/7 (100.0%) | 17 / 8 | 1/0/4; 1.600/2 | 4/4 (100.0%) | 4/4 (100.0%) | 2/2 (100.0%) | 1/5 (20.0%) | 0 |
| dense-test | 6/6 (100.0%) | 17 / 7 | 1/0/3; 1.500/2 | 3/4 (75.0%) | 4/4 (100.0%) | 2/2 (100.0%) | 0/4 (0.0%) | 1 |

Lỗi được loại khỏi mẫu số chất lượng theo starter và báo riêng. Để không che lỗi, xem thêm coverage toàn bộ câu và điểm end-to-end dưới đây. Từ chối nhầm theo status có thể bỏ sót câu refusal được model viết bằng văn xuôi: TF-IDF dev q06 là một trường hợp (status answered nhưng không trả lời; grade 0).

| Cấu hình | Context grade 0/1/2 (mọi câu có đáp án, kể cả lỗi cuối) | Context đủ gold / toàn bộ câu có đáp án | Tổng / median thời gian câu | Input/output token | Điểm grounded tổng / (2 × toàn bộ câu có đáp án) |
|---|---|---|---|---|---|
| tfidf-dev | 3/3/9 | 8/15 (53.3%) | 12.93 phút / 42.32 s | 37977/2094 | 17/30 |
| dense-dev | 1/0/14 | 14/15 (93.3%) | 11.00 phút / 37.59 s | 33298/1865 | 26/30 |
| tfidf-test | 1/0/4 | 4/5 (80.0%) | 7.24 phút / 43.08 s | 16246/804 | 8/10 |
| dense-test | 1/0/4 | 4/5 (80.0%) | 5.83 phút / 31.25 s | 16938/1151 | 6/10 |

Câu có query được model viết lại (xem query thật trong search events):

- tfidf-dev: q04, q14.
- dense-dev: q04, q11, q14, dev-absent-02.
- tfidf-test: test-new-02, test-new-03, test-absent-02.
- dense-test: test-new-03, test-absent-02.

### Nhãn và trace từng câu

Mỗi dòng dưới đây liên kết bản chấm có câu hỏi, đáp án tham chiếu, câu trả lời thật, citation, lý do riêng và toàn bộ final context. Trace JSON còn có mọi model/tool call, raw final, score, filter, thời gian và token.

| Run | Nhãn, lý do và nguồn | Trace thật |
|---|---|---|
| tfidf-dev | [Source review](../evaluation/tfidf-dev/source_review.md), [labels](../evaluation/tfidf-dev/reviews.json) | [traces](../../artifacts/runs/tfidf-dev/traces.json), [config](../../artifacts/runs/tfidf-dev/run_config.json) |
| dense-dev | [Source review](../evaluation/dense-dev/source_review.md), [labels](../evaluation/dense-dev/reviews.json) | [traces](../../artifacts/runs/dense-dev/traces.json), [config](../../artifacts/runs/dense-dev/run_config.json) |
| tfidf-test | [Source review](../evaluation/tfidf-test/source_review.md), [labels](../evaluation/tfidf-test/reviews.json) | [traces](../../artifacts/runs/tfidf-test/traces.json), [config](../../artifacts/runs/tfidf-test/run_config.json) |
| dense-test | [Source review](../evaluation/dense-test/source_review.md), [labels](../evaluation/dense-test/reviews.json) | [traces](../../artifacts/runs/dense-test/traces.json), [config](../../artifacts/runs/dense-test/run_config.json) |

### Phân tích lỗi và giới hạn

- Lexical dev q03 nhầm prompt của interpreter với input(prompt); dense lấy đúng định nghĩa và trả lời đúng. Đây là lỗi truy xuất theo từ giống nhau, không phải lỗi thiếu dữ liệu.
- q07 cần nhiều fragment. TF-IDF context có thể giải thích đúng về mặt ngữ nghĩa nhờ ví dụ nhưng không chứa đủ toàn bộ gold đã đóng băng; báo riêng metric exact-evidence và điểm context đọc nguồn, không sửa gold sau chạy.
- Dense dev q13 thiếu đoạn PDF 44 về thời điểm đánh giá argument, nhưng model vẫn trả lời và trích glossary PDF 48. Grade 0, citation false; guard ID không kiểm tra ngữ nghĩa.
- Dense dev q12 đủ thông tin trong context nhưng gắn citation chỉ giải thích fruitful, thiếu void; answer 2 nhưng citation false. q01/q15 thêm kiến thức ngoài đoạn trích nên answer 1.
- Model thinking ban đầu hết 1024 token ở 7 câu; Instruct khắc phục lỗi hoàn tất nhưng không đảm bảo grounding. Baseline TF-IDF còn có lỗi hết số lượt model. Các lần thất bại không bị xóa.
- Test-new-02: cả hai cách retrieval đều thiếu evidence về vị trí import. Dense vẫn trả lời bằng kiến thức không được context hỗ trợ (grade 0/citation false); TF-IDF thử search lần 2 rồi từ chối (false abstention trên câu có đáp án). Không gọi refusal này là đúng theo benchmark chỉ vì an toàn hơn việc đoán.
- Test-new-03: dense tìm đủ đoạn giải thích r/n nhưng lỗi giao thức ở final; TF-IDF trả lời được với nguồn hỗ trợ. Test không xác nhận ưu thế tổng thể của cấu hình dense đã chọn trên dev. Giữ nguyên quyết định trước test và báo cả điểm end-to-end, không chọn lại theo test.
- Corpus tiếng Anh nhỏ, text-only, 48 trang; bộ test chỉ 5 câu có đáp án nên tỷ lệ biến động lớn. Nhãn do AI đọc nguồn, chưa có người chấm độc lập. Kết quả không chứng minh an toàn trước mọi prompt injection hay mọi câu ngoài tập.

## Tái lập và kết luận

[Hướng dẫn tái lập](../../docs/REPRODUCE_SUBMISSION.md), [manifest](../../artifacts/manifest.json), [quyết định dev trước test](../selection.json). Không phát hành secret, .env, virtualenv hoặc trọng số model. Toàn bộ kết quả test đều được giữ và không dùng để chỉnh tiếp trong bài này.

Dense là cấu hình được chọn trên dev. Bảng test là kết quả độc lập sau chốt; mức điểm thấp hoặc citation sai được công bố, không gán mục tiêu 90% cho phần cơ bản. Các lỗi nguồn còn lại là hướng phát triển tiếp, chưa được sửa bằng test.

## Thử thách nâng cao

Không thực hiện nhánh bonus 15 điểm. Không có index 100+ trang đa phương thức hoặc benchmark bảng/ảnh/biểu đồ; không tuyên bố đủ điều kiện bonus hay tự chấm 100 điểm. Bài này hoàn thiện phần cơ bản theo rubric 85 điểm.
