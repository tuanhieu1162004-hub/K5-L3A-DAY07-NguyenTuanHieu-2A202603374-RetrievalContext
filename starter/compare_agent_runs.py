"""Compare complete dev runs and prepare source material for manual grading.

Counts execution outcomes only; never treats answered or valid IDs as correctness.
The review pack includes gold for offline review and is never sent to the agent.
"""
import argparse
import hashlib
import json
from pathlib import Path

from benchmark_support import evidence_covered

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load(pointer):
    summary = read(pointer)
    folder = Path(summary["run_directory"])
    config = read(folder / "run_config.json")
    traces = read(folder / "traces.json")
    by_id = {trace["query_id"]: trace for trace in traces}
    if len(by_id) != len(traces) or len(traces) != summary["n"] or set(by_id) != set(config["query_ids"]):
        raise ValueError("Run summary/config/traces disagree or have duplicate IDs")
    for status, field in (("answered", "answered"), ("abstain", "abstain"), ("error", "errors")):
        if sum(trace["status"] == status for trace in traces) != summary[field]:
            raise ValueError("Saved outcome counts disagree with traces")
    return {"summary": summary, "config": config, "traces": traces, "by_id": by_id, "folder": folder}


def outcomes(run, questions):
    summary = run["summary"]
    answerable = [trace for trace in run["traces"] if questions[trace["query_id"]].get("answerable", True)]
    context_hits = 0
    for trace in answerable:
        retrieved = {chunk["id"]: chunk for event in trace["events"] if event.get("event") == "search" for chunk in event["results"]}
        if any(cid not in retrieved for cid in trace["context_ids"]):
            raise ValueError("Final context references an unretrieved chunk")
        context_hits += evidence_covered([retrieved[cid] for cid in trace["context_ids"]], questions[trace["query_id"]])
    return {"run_id": summary["run_id"], "model": summary["model"], "n": summary["n"],
        "answered": summary["answered"], "abstain": summary["abstain"], "errors": summary["errors"],
        "total_query_seconds": sum(trace["elapsed_ms"] for trace in run["traces"]) / 1000,
        "prompt_tokens": summary["prompt_tokens"], "output_tokens": summary["output_tokens"],
        "error_ids": [trace["query_id"] for trace in run["traces"] if trace["status"] == "error"],
        "truncated_ids": [trace["query_id"] for trace in run["traces"] if any(call.get("done_reason") == "length" for call in trace["model_calls"])],
        "thinking_characters": sum(call.get("thinking_characters", 0) for trace in run["traces"] for call in trace["model_calls"]),
        "context_evidence": {"n": context_hits, "N": len(answerable)},
        "model_configuration": run["config"]["model"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=ROOT / "starter/results/agent-dev-dense/latest.json")
    parser.add_argument("--candidate", type=Path, default=ROOT / "starter/results/agent-dev-dense-instruct/latest.json")
    parser.add_argument("--questions", type=Path, default=ROOT / "data/day7_benchmark/questions_dev.json")
    parser.add_argument("--output", type=Path, default=ROOT / "report")
    args = parser.parse_args()
    baseline, candidate = load(args.baseline), load(args.candidate)
    for field in ("chunks_sha256", "questions_sha256", "split", "top_k", "budget_chars", "max_searches"):
        if baseline["config"][field] != candidate["config"][field]:
            raise ValueError(f"Runs have different comparison conditions: {field}")
    for field in ("num_ctx", "max_output_tokens", "max_model_calls", "temperature", "seed", "reasoning_mode"):
        if baseline["config"]["model"].get(field) != candidate["config"]["model"].get(field):
            raise ValueError(f"Model limits/sampling differ: {field}")
    if set(baseline["by_id"]) != set(candidate["by_id"]):
        raise ValueError("Runs do not include the same question IDs")
    for field in ("embedding", "day6_strategy", "corpus_chunks_verified"):
        if baseline["config"]["retrieval"][field] != candidate["config"]["retrieval"][field]:
            raise ValueError(f"Retrieval index conditions differ: {field}")
    if hashlib.sha256(args.questions.read_bytes()).hexdigest() != candidate["config"]["questions_sha256"]:
        raise ValueError("Review questions/labels differ from the frozen run inputs")
    questions = {q["id"]: q for q in read(args.questions) if q["split"] == candidate["summary"]["split"]}
    if set(questions) != set(candidate["by_id"]):
        raise ValueError("Run must cover the full specified split")
    for qid, question in questions.items():
        if any(run["by_id"][qid]["question"] != question["question"] for run in (baseline, candidate)):
            raise ValueError("Question text differs across runs")
    before, after = outcomes(baseline, questions), outcomes(candidate, questions)
    report = {"scope": "Complete dev execution comparison; content grading is pending",
              "comparison_conditions_verified": True, "baseline": before, "candidate": after,
              "candidate_review_template": str(candidate["folder"] / "reviews_template.json")}
    lines = ["# So sánh hai cấu hình agent trên dev", "",
        "Cùng corpus 271 chunk C, 17 câu dev, dense top-k=3, context 2.000 ký tự, tối đa 2 search/5 model call, 1.024 output token mỗi lời gọi.", "",
        "| Model | Câu | answered | abstain | error | Context đủ gold | Output token | Tổng thời gian câu hỏi |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in (before, after):
        lines.append(f"| {row['model']} | {row['n']} | {row['answered']} | {row['abstain']} | {row['errors']} | {row['context_evidence']['n']}/{row['context_evidence']['N']} | {row['output_tokens']} | {row['total_query_seconds']/60:.1f} phút |")
    lines += ["", "Đây là số lần hoàn tất/ lỗi, không phải độ chính xác. Cần chấm nội dung và citation trước khi chọn pipeline cuối.", "",
        "Context đủ gold dùng cùng quy tắc OR giữa nhóm, AND giữa fragment trong benchmark_support.py; chỉ câu có đáp án vào mẫu số. Đây không phải điểm grounded answer hay chấm context thủ công.", "",
        "## Phân tích lỗi", "",
        f"Baseline lỗi ở: {', '.join(before['error_ids']) or 'không có'}. Các câu có output bị cắt: {', '.join(before['truncated_ids']) or 'không có'}.",
        "q09 hết token trước khi gọi retrieval; q05 và q07 đã tìm tài liệu nhưng hết token trước câu trả lời. q14 còn có phản hồi không đúng định dạng/citation trước khi bị cắt.",
        f"Cấu hình Instruct còn lỗi ở: {', '.join(after['error_ids']) or 'không có'}.", "",
        "Giả thuyết: phần reasoning của model cũ chiếm output budget; dùng bản Instruct trả lời trực tiếp sẽ giảm cắt token và thời gian. Đây là đổi model/weights/template, không phải sửa nhãn hoặc thay đáp án bằng kết quả giả.",
        "Các giới hạn API, corpus, split và retrieval được giữ giống nhau; model digest/thiết lập thực tế nằm trong JSON đi kèm. Thời gian là một lần đo trên máy local, chưa phải thí nghiệm timing lặp lại.", "",
        "## Nhật ký và bước chấm", "",
        f"Baseline: `{baseline['folder']}`.", f"Candidate: `{candidate['folder']}`.",
        "Run cũ được giữ nguyên. Không trộn các câu thành công từ các run thành một benchmark mới.",
        "Đọc [tập chấm dev](agent_dev_review.md), điền bản sao reviews_template.json thành reviews.json và ghi người/công cụ chấm. Nhãn AI phải được ghi rõ, không đại diện cho nhãn người học.",
        "Chưa chạy test. Chưa kết luận một cấu hình tốt hơn về grounded answer chỉ từ việc giảm lỗi kỹ thuật.", ""]
    review = ["# Tập chấm agent trên dev", "",
        "Tài liệu để người chấm đọc; không đưa tập này vào agent hoặc retrieval. Các nhãn vẫn chưa được chấm tự động.", "",
        "Câu có đáp án: answer_grade 0/1/2, context_grade 0/1/2; mỗi citation có một nhãn hỗ trợ true/false. Câu thiếu bằng chứng: kiểm tra từ chối và không thêm suy đoán. Lỗi ghi riêng.", ""]
    for trace in candidate["traces"]:
        question = questions[trace["query_id"]]
        review += [f"## {trace['query_id']} — {trace['status']}", "", f"Câu hỏi: {question['question']}", "",
            f"Có đáp án trong corpus: {question.get('answerable', True)}", "",
            "Câu trả lời:", "", trace["answer"] or trace.get("error", ""), ""]
        if question.get("answerable", True):
            review += [f"Đáp án tham chiếu: {question['expected_answer']}", "", "Evidence gốc (các lựa chọn thay thế):", ""]
            for gold in question.get("original_gold", []):
                review += [f"- Nguồn {gold['source_id']}, trang PDF {gold['page']}: {gold['evidence']}"]
        else:
            review += [f"Lý do thiếu evidence: {question['absence_reason']}"]
        review += ["", f"Citation cần chấm: {json.dumps(trace['citations'], ensure_ascii=False)}", "",
                   "Context cuối thực sự gửi model:", "", "````text", trace.get("context", ""), "````", "",
                   "Nhãn và lý do: CHƯA CHẤM", ""]
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "agent_dev_comparison.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "agent_dev_comparison.md").write_text("\n".join(lines), encoding="utf-8")
    (args.output / "agent_dev_review.md").write_text("\n".join(review), encoding="utf-8")
    print("\n".join(lines[:9]))
    print(f"Saved comparison and review pack in {args.output}")


if __name__ == "__main__":
    main()
