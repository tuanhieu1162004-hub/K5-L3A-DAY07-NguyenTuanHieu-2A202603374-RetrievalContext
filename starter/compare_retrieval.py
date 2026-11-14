"""Create a checked dev comparison from saved real retrieval runs."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display(metric):
    if not metric["N"]:
        return "0/0 (N/A)"
    return f"{metric['n']}/{metric['N']} ({100 * metric['rate']:.1f}%)"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "report/retrieval_dev")
    args = parser.parse_args()
    rows, runs = [], {}
    comparison_key = None
    for method in ("tfidf", "dense", "hybrid"):
        folder = ROOT / f"starter/results/dev-{method}-k3-b2000"
        summary = read(folder / "summary.json")
        traces = read(folder / "traces.json")
        key = tuple(summary[field] for field in ("chunks_sha256", "questions_sha256", "split", "top_k", "budget_chars"))
        if comparison_key is not None and key != comparison_key:
            raise ValueError("Runs do not share the same corpus/questions/split/top-k/context budget")
        comparison_key = key
        if summary["strategy"] != method or summary["split"] != "dev" or len(traces) != summary["n_total"]:
            raise ValueError("Wrong method/split or missing traces")
        trace_map = {trace["query_id"]: trace for trace in traces}
        if len(trace_map) != len(traces) or any(trace["status"] != "retrieved" for trace in traces):
            raise ValueError("Duplicate query IDs or unsuccessful retrieval traces")
        if runs:
            reference = runs["tfidf"]
            if set(trace_map) != set(reference) or any(
                trace_map[qid][field] != reference[qid][field] for qid in reference
                for field in ("question", "requested_filter", "answerable")):
                raise ValueError("Query/filter/answerability conditions differ across methods")
        for field, label in (("hit1", "Hit@1"), ("hit3", "Evidence Hit@3"), ("context_hit", "Context Evidence Rate")):
            answerable = [trace for trace in traces if trace["answerable"]]
            count, total = sum(trace[field] for trace in answerable), len(answerable)
            if summary["metrics"][label] != {"n": count, "N": total, "rate": count / total if total else None}:
                raise ValueError("Saved summary disagrees with per-query traces")
        runs[method] = trace_map
        rows.append({"summary": summary, "results_folder": str(folder.relative_to(ROOT)),
                     "summary_sha256": digest(folder / "summary.json"), "traces_sha256": digest(folder / "traces.json")})
    report = {"scope": "Retrieval/context dev comparison; no agent answers or test evaluation",
              "same_corpus_questions_filters_verified": True, "runs": rows}
    lines = ["# So sánh retrieval trên dev", "",
             "Cùng 271 chunk C của Day 6, 17 câu dev (15 có đáp án + 2 thiếu bằng chứng), top-k=3 và budget=2.000 ký tự.", "",
             "| Phương pháp | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Median/query (ms) | Khởi tạo (s) |",
             "|---|---|---|---|---:|---:|"]
    for row in rows:
        summary = row["summary"]
        metrics = summary["metrics"]
        lines.append(f"| {summary['strategy']} | {display(metrics['Hit@1'])} | {display(metrics['Evidence Hit@3'])} | {display(metrics['Context Evidence Rate'])} | {summary['median_ms']:.3f} | {summary['index_seconds']:.3f} |")
    lines += ["", "TF-IDF: cosine lexical; dense: model MiniLM 384 chiều + pgvector cosine exact; hybrid: RRF, 20 candidate mỗi nhánh, constant=60.",
              "Nguồn, câu hỏi, filter, checksum và số liệu trace đã được script đối chiếu. Database dense/hybrid dùng giao dịch chỉ đọc.", "",
              "Thời gian khởi tạo gồm nạp model và kiểm tra tương thích; lần đầu và lần sau chịu ảnh hưởng cache hệ điều hành. Chưa lặp thí nghiệm timing để kết luận tốc độ.",
              "Phí dịch vụ của ba retriever là 0 USD; không bao gồm điện/máy. Chưa có chi phí hoặc chất lượng LLM.", "",
              "## Đối chiếu hai câu dev", "", "| Query | Phương pháp | Hit@1 | Hit@3 | Context đủ evidence |", "|---|---|---|---|---|"]
    for qid in ("q05", "q07"):
        for method, trace_map in runs.items():
            trace = trace_map[qid]
            lines.append(f"| {qid} | {method} | {int(trace['hit1'])} | {int(trace['hit3'])} | {int(trace['context_hit'])} |")
    lines += ["", "## Giới hạn và phần còn lại", "",
              "Các chỉ số đo độ phủ evidence, không phải độ chính xác câu trả lời. Hai câu thiếu bằng chứng có trace nhưng không vào mẫu số; chưa chấm abstention.",
              "Bảng này chỉ đánh giá retrieval. Agent Ollama đã có chương trình chạy riêng; chưa chốt pipeline cuối và chưa chạy test. Nhãn benchmark do AI chuẩn bị, phần đối chiếu nguồn của người học còn chờ thực hiện.",
              "Lệnh chạy và điều kiện tái lập: [RETRIEVAL_SETUP.md](../docs/RETRIEVAL_SETUP.md).", ""]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:9]))
    print(f"Saved {args.output.with_suffix('.md')}")


if __name__ == "__main__":
    main()
