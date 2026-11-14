"""Copy an explicit allowlist of permitted experiment artifacts, then build the report."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil

from review_results import read, save, ROOT


def ratio(value):
    return f"{value['n']}/{value['N']} ({100*value['n']/value['N']:.1f}%)" if value['N'] else "0/0 (N/A)"


def main():
    registry = read(ROOT / "report/run_registry.json")
    artifacts = ROOT / "artifacts"
    for name in ("chunks.json", "provenance.json", "benchmark_import_audit.json"):
        shutil.copyfile(ROOT / "starter/data/day6" / name, artifacts / "day6" / name)
    for alias, folder in registry["agents"].items():
        source = ROOT / folder
        target = artifacts / "runs" / alias
        target.mkdir(parents=True, exist_ok=True)
        for name in ("run_config.json", "traces.json", "summary.json", "cases.json"):
            shutil.copyfile(source / name, target / name)
    for folder in registry["retrieval"]:
        target = artifacts / "retrieval" / folder
        target.mkdir(parents=True, exist_ok=True)
        for name in ("traces.json", "summary.json"):
            shutil.copyfile(ROOT / "starter/results" / folder / name, target / name)
    rows = []
    for folder in registry["retrieval"]:
        s = read(artifacts / "retrieval" / folder / "summary.json")
        m = s["metrics"]
        rows.append(f"| {folder} | {s['strategy']}; k={s['top_k']}; {s['budget_chars']} ký tự | {s['split']} | {ratio(m['Hit@1'])} | {ratio(m['Evidence Hit@3'])} | {ratio(m['Context Evidence Rate'])} | {s['median_ms']:.3f} ms / {s['index_seconds']:.3f} s |")
    lines = ["# Báo cáo Day 7 — Nguyễn Tuấn Hiếu", "", "**Lớp:** K5-L3A · **MSSV:** 2A202603374", "",
      "**Repo:** https://github.com/tuanhieu1162004-hub/K5-L3A-DAY07-NguyenTuanHieu-2A202603374-RetrievalContext", "",
      "## Dữ liệu và benchmark", "",
      "Nguồn: Think Python 2e — Allen B. Downey, Green Tea Press, CC BY-NC3.0. PDF gốc244 trang; phạm vi thực tế48 trang có nội dung (PDF23–71 trừ38), chương1–5. Tái sử dụng271 chunk và vector chiến lược C từ Day6; không tuyên bố index toàn bộ sách. Attribution và quyền chia sẻ phi thương mại: [ATTRIBUTION](../../ATTRIBUTION.md).", "",
      "Vector store PostgreSQL16/pgvector0.8.7; exact cosine, không ANN. Embedding all-MiniLM-L6-v2 revision1110a243fdf4706b3f48f1d95db1a4f5529b4d41, 384 chiều, normalize=True, CPU. So sánh toàn bộ ID/text/metadata và3 vector mẫu trước khi truy xuất; snapshot repeatable-read/read-only. Vector gốc và corpus được đóng gói để khôi phục trên database mới.", "",
      "Benchmark24 câu: dev15 có đáp án+2 thiếu bằng chứng, test mới5+2. Giữ riêng test từ trước thực nghiệm; test Day6 không được tái dùng. `data/day7_benchmark/protocol.json` đóng băng checksum. Khớp evidence theo nguồn, trang và offset; chỉ gộp whitespace khi chấm. OR giữa các gold_sets, AND giữa các fragment trong một nhóm. q07 cần nhiều chunk; không giảm yêu cầu chỉ để tăng điểm.", "",
      "Câu thiếu bằng chứng được kiểm tra theo toàn bộ phạm vi corpus và các đoạn liên quan trong absence_audit.json, không suy từ top-k trống. Nhãn và phân tích được Codex (AI) đối chiếu nguồn; **chưa có xác nhận chấm của người học**. Đây là giới hạn của đánh giá, không được gọi là nhãn human-verified.", "",
      "## Retrieval và thử nghiệm", "",
      "| Cấu hình | Phương pháp / context | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Median/query / khởi tạo |",
      "|---|---|---|---|---|---|---|", *rows, "",
      "Phí dịch vụ tất cả cấu hình0USD; chưa tính điện/phần cứng. Timing một lần chạy, không phải trung bình nhiều lần đo. Hai phép đo retrieval test chạy trong lúc agent dense test hoạt động trên cùng CPU, nên timing test có nhiễu tải; không dùng chúng để kết luận tốc độ cải thiện. Query gốc giữ nguyên; filter do ứng dụng cung cấp, không suy từ gold. Cùng corpus và cutoff3 để so sánh ranking. Hybrid lấy20 candidate/method, RRF1/(60+rank), không cộng raw score.", "",
      "### Giả thuyết, hai cấu hình cải thiện và lựa chọn", "",
      "1. TF-IDF k3/b800 → k3/b2000: tăng budget để giảm rơi evidence khi pack context; context5/15 →8/15, ranking không đổi. k8/b4000 nâng context lên12/15 nhưng dùng nhiều ký tự hơn. q07 cần thêm đoạn ngoài top3.",
      "2. Dense k3/b2000: giả thuyết embedding nhận đúng nghĩa hơn lexical; Hit1 5/15→12/15, Hit3/context8/15→14/15. Hybrid RRF là phương pháp thứ ba, chỉ đạt13/15 context, nên không chọn chỉ vì phức tạp hơn.",
      "3. Agent qwen3:4b → qwen3:4b-instruct, cùng dense và giới hạn: lỗi7/17→0/17, output21913→1865 token, tổng thời gian73→11 phút. Đây là đổi model/weights/template, tách khỏi so sánh retrieval. Giữ run cũ để thấy cả lỗi token limit.", "",
      "Baseline cuối: TF-IDF + qwen3:4b-instruct, k3/b2000. Cấu hình chọn: dense + cùng model và giới hạn. Chọn dựa trên grounded answer/citation dev, sau đó evidence và thời gian. Quyết định, thời điểm, checksum code và điều kiện test: [selection.json](../selection.json). Không chỉnh cấu hình sau khi xem test; không ghép câu tốt nhất từ nhiều lần chạy.", "",
      "## Agent và đánh giá nguồn", "",
      "Model thật qua Ollama local0.40.16; không key/dịch vụ cloud. Tool search_documents, final_answer, abstain. Trước quyết định cuối phải có search do model gọi. Prompt yêu cầu search đầu nguyên văn nhưng model có thể viết lại; runner ghi query thật và query_is_original, không cưỡng chế câu gốc. Bảng retrieval thuần phía trên luôn dùng query gốc; context/answer agent dưới đây đánh giá pipeline thực tế, không gộp vào ranking query gốc. Tối đa2search/5model call mỗi câu, output1024 token, context model8192, temperature0/seed42. Pack chunk mới trước, sau đó chunk cũ duy nhất, tổng2000ký tự cả header. Tool context cũ được rút gọn; trace giữ nguyên. Lỗi token/protocol/provider được ghi riêng, không biến thành từ chối giả.", "",
      "Grounded0=sai/thiếu evidence,1=một phần,2=đúng và đủ trong final context. Citation hợp lệ cần ID có trong context **và** hỗ trợ toàn bộ khẳng định đi kèm. Context0=không có evidence yêu cầu,1=thiếu điều kiện/nguồn,2=đủ. Một câu có thể đúng theo context nhưng citation gắn sai vẫn bị trừ citation. Không coi answered là correct.", "",
      "| Agent / split | Tool use | Model calls / searches | Grounded 0/1/2; mean /2 | Citation hỗ trợ | Câu có citation | Từ chối đúng | Từ chối nhầm qua đọc nội dung | Lỗi |",
      "|---|---|---|---|---|---|---|---|---|"]
    metrics = {}
    for alias in ("tfidf-dev", "dense-dev", "tfidf-test", "dense-test"):
        m = read(ROOT / "report/evaluation" / alias / "metrics.json")
        metrics[alias] = m
        g, s = m["grounded_answer"], m["summary"]
        lines.append(f"| {alias} | {ratio(m['tool_use'])} | {s['model_calls']} / {s['searches']} | {g['0']}/{g['1']}/{g['2']}; {g['mean']:.3f}/2 | {ratio(m['citation_validity'])} | {ratio(m['answer_citation_coverage'])} | {ratio(m['abstention'])} | {ratio(m['false_abstention_content_review'])} | {m['provider_errors']} |")
    lines += ["", "Lỗi được loại khỏi mẫu số chất lượng theo starter và báo riêng. Để không che lỗi, xem thêm coverage toàn bộ câu và điểm end-to-end dưới đây. Từ chối nhầm theo status có thể bỏ sót câu refusal được model viết bằng văn xuôi: TF-IDF dev q06 là một trường hợp (status answered nhưng không trả lời; grade0).", "",
              "| Cấu hình | Context grade 0/1/2 (mọi câu có đáp án, kể cả lỗi cuối) | Context đủ gold / toàn bộ câu có đáp án | Tổng / median thời gian câu | Input/output token | Điểm grounded tổng / (2 × toàn bộ câu có đáp án) |",
              "|---|---|---|---|---|---|"]
    for alias, m in metrics.items():
        c, s, g = m["context_grades"], m["summary"], m["grounded_answer"]
        total = m["context_evidence"]["N"]
        lines.append(f"| {alias} | {c.get('0',0)}/{c.get('1',0)}/{c.get('2',0)} | {ratio(m['context_evidence'])} | {m['elapsed_seconds']/60:.2f} phút / {m['median_query_seconds']:.2f} s | {s['prompt_tokens']}/{s['output_tokens']} | {g['1']+2*g['2']}/{2*total} |")
    lines += ["", "Câu có query được model viết lại (xem query thật trong search events):", ""]
    for alias, m in metrics.items():
        lines.append(f"- {alias}: {', '.join(m['rewritten_query_ids']) or 'không có'}.")
    lines += ["", "### Nhãn và trace từng câu", "",
      "Mỗi dòng dưới đây liên kết bản chấm có câu hỏi, đáp án tham chiếu, câu trả lời thật, citation, lý do riêng và toàn bộ final context. Trace JSON còn có mọi model/tool call, raw final, score, filter, thời gian và token.", "",
      "| Run | Nhãn, lý do và nguồn | Trace thật |", "|---|---|---|"]
    for alias in metrics:
        lines.append(f"| {alias} | [Source review](../evaluation/{alias}/source_review.md), [labels](../evaluation/{alias}/reviews.json) | [traces](../../artifacts/runs/{alias}/traces.json), [config](../../artifacts/runs/{alias}/run_config.json) |")
    lines += ["", "### Phân tích lỗi và giới hạn", "",
      "- Lexical dev q03 nhầm prompt của interpreter với input(prompt); dense lấy đúng định nghĩa và trả lời đúng. Đây là lỗi truy xuất theo từ giống nhau, không phải lỗi thiếu dữ liệu.",
      "- q07 cần nhiều fragment. TF-IDF context có thể giải thích đúng về mặt ngữ nghĩa nhờ ví dụ nhưng không chứa đủ toàn bộ gold đã đóng băng; báo riêng metric exact-evidence và điểm context đọc nguồn, không sửa gold sau chạy.",
      "- Dense dev q13 thiếu đoạn PDF44 về thời điểm đánh giá argument, nhưng model vẫn trả lời và trích glossary PDF48. Grade0, citation false; guard ID không kiểm tra ngữ nghĩa.",
      "- Dense dev q12 đủ thông tin trong context nhưng gắn citation chỉ giải thích fruitful, thiếu void; answer2 nhưng citation false. q01/q15 thêm kiến thức ngoài đoạn trích nên answer1.",
      "- Model thinking ban đầu hết1024token ở7câu; Instruct khắc phục lỗi hoàn tất nhưng không đảm bảo grounding. Baseline TF-IDF còn có lỗi hết số lượt model. Các lần thất bại không bị xóa.",
      "- Test-new-02: cả hai cách retrieval đều thiếu evidence về vị trí import. Dense vẫn trả lời bằng kiến thức không được context hỗ trợ (grade0/citation false); TF-IDF thử search lần2 rồi từ chối (false abstention trên câu có đáp án). Không gọi refusal này là đúng theo benchmark chỉ vì an toàn hơn việc đoán.",
      "- Test-new-03: dense tìm đủ đoạn giải thích r/n nhưng lỗi giao thức ở final; TF-IDF trả lời được với nguồn hỗ trợ. Test không xác nhận ưu thế tổng thể của cấu hình dense đã chọn trên dev. Giữ nguyên quyết định trước test và báo cả điểm end-to-end, không chọn lại theo test.",
      "- Corpus tiếng Anh nhỏ, text-only, 48trang; bộ test chỉ5câu có đáp án nên tỷ lệ biến động lớn. Nhãn do AI đọc nguồn, chưa có người chấm độc lập. Kết quả không chứng minh an toàn trước mọi prompt injection hay mọi câu ngoài tập.", "",
      "## Tái lập và kết luận", "",
      "[Hướng dẫn tái lập](../../docs/REPRODUCE_SUBMISSION.md), [manifest](../../artifacts/manifest.json), [quyết định dev trước test](../selection.json). Không phát hành secret, .env, virtualenv hoặc trọng số model. Toàn bộ kết quả test đều được giữ và không dùng để chỉnh tiếp trong bài này.", "",
      "Dense là cấu hình được chọn trên dev. Bảng test là kết quả độc lập sau chốt; mức điểm thấp hoặc citation sai được công bố, không gán mục tiêu90% cho phần cơ bản. Các lỗi nguồn còn lại là hướng phát triển tiếp, chưa được sửa bằng test.", "",
      "## Thử thách nâng cao", "", "Không thực hiện nhánh bonus15điểm. Không có index100+trang đa phương thức hoặc benchmark bảng/ảnh/biểu đồ; không tuyên bố đủ điều kiện bonus hay tự chấm100điểm. Bài này hoàn thiện phần cơ bản theo rubric85điểm.", ""]
    report = ROOT / "report/individual/2A202603374_NguyenTuanHieu.md"
    content = "\n".join(lines)
    for before, after in {
        "BY-NC3.0": "BY-NC 3.0", "gốc244": "gốc 244", "tế48": "tế 48", "PDF23": "PDF 23", "trừ38": "trừ 38",
        "chương1": "chương 1", "dụng271": "dụng 271", "Day6": "Day 6", "PostgreSQL16": "PostgreSQL 16",
        "pgvector0.8.7": "pgvector 0.8.7", "revision1110": "revision 1110", "và3": "và 3", "Benchmark24": "Benchmark 24",
        "dev15": "dev 15", "mới5+2": "mới 5+2", "hình0USD": "hình 0 USD", "cutoff3": "cutoff 3", "lấy20": "lấy 20",
        "RRF1/": "RRF 1/", "context5/": "context 5/", "context8/": "context 8/", "lên12/": "lên 12/", "đạt13/": "đạt 13/",
        "top3": "top-3", "lỗi7/": "lỗi 7/", "output21913": "output 21913", "gian73": "gian 73", "local0.40.16": "local 0.40.16",
        "đa2search/5model": "đa 2 search / 5 model", "output1024": "output 1024", "model8192": "model 8192",
        "temperature0/seed42": "temperature 0 / seed 42", "tổng2000ký": "tổng 2000 ký", "Grounded0=": "Grounded 0=",
        "Context0=": "Context 0=", "grade0": "grade 0", "Grade0": "Grade 0", "answer2": "answer 2", "answer1": "answer 1",
        "hết1024token": "hết 1024 token", "ở7câu": "ở 7 câu", "lần2": "lần 2", "48trang": "48 trang",
        "chỉ5câu": "chỉ 5 câu", "tiêu90%": "tiêu 90%", "bonus15điểm": "bonus 15 điểm", "index100+trang": "index 100+ trang",
        "chấm100điểm": "chấm 100 điểm", "rubric85điểm": "rubric 85 điểm", "PDF44": "PDF 44", "PDF48": "PDF 48"
    }.items():
        content = content.replace(before, after)
    report.write_text(content, encoding="utf-8")
    manifest = {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(artifacts.rglob("*")) if p.is_file() and p.name != "manifest.json"}
    save(artifacts / "manifest.json", {"algorithm": "SHA256", "files": manifest})
    print(f"Packaged {len(manifest)} permitted artifacts and {report.name}")


if __name__ == "__main__":
    main()
