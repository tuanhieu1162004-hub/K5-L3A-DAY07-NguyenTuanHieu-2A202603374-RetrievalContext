# Định dạng dữ liệu

Benchmark Think Python của workspace nằm trong `day7_benchmark/`, gồm 17 câu
dev và 7 câu test. Quy trình và lệnh chạy: [BENCHMARK_SETUP.md](../docs/BENCHMARK_SETUP.md).
Nhãn mới do AI chuẩn bị; phần đối chiếu nguồn của người học còn chờ thực hiện.

Schema mở rộng dùng `gold_sets`: mỗi phần tử là một nhóm evidence thay thế;
các fragment trong cùng nhóm đều bắt buộc. `original_gold` giữ nguyên quote
Day 6. Fragment có `start_char`/`end_char` phải đúng vị trí trên trang nguồn.
`starter/benchmark_support.py` chấm cùng quy tắc đủ nhóm cho top-1, top-3 và
context, chỉ chuẩn hóa Unicode/khoảng trắng khi đối chiếu. Dùng
`starter/evaluate_retrieval.py` cho schema này.

Các file `example_*.json` chỉ minh họa định dạng, không đủ để nộp bài. Dữ liệu thật là JSON array UTF-8; nếu dùng định dạng khác, ghi cách chuyển trong README.

- **Chunk:** `id`, `text`, `source_id`, `source`, `page`, `metadata`. ID phải duy nhất; giữ phiên bản hoặc ngày nếu có.
- **Câu có đáp án:** `id`, `split` (`dev` hoặc `test`), `question`, `expected_answer`, `gold`: danh sách `{source_id, page, evidence}`. Với schema mẫu, mỗi evidence phải nằm trọn trong một chunk đúng nguồn và trang; các phần tử `gold` là evidence thay thế. Với câu multi-hop cần nhiều đoạn, bạn có thể mở rộng schema, ghi rõ nhóm evidence bắt buộc và cách chấm. Có thể thêm `filter` do người dùng cung cấp trước.
- **Câu thiếu evidence:** `id`, `split`, `question`, `answerable: false`, `expected_behavior: "search_and_abstain"`, `absence_reason`. Xem `agent_cases_example.json`.

Không đưa `gold` hoặc nhãn đáp án vào model và retrieval tool. Ghi nguồn dữ liệu và quyền sử dụng. Cách chuyển một số định dạng Day 6: [starter/README.md](../starter/README.md).
