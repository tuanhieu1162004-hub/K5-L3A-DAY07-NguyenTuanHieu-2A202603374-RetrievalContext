"""Materialize explicitly authored offline reviews; this script never judges answers."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics

from agent_metrics import aggregate
from benchmark_support import evidence_covered

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def review(alias, run_folder, decisions_path=ROOT / "report/review_decisions.json"):
    authored = read(decisions_path)
    decisions = authored["runs"][alias]
    summary, config = read(run_folder / "summary.json"), read(run_folder / "run_config.json")
    traces = read(run_folder / "traces.json")
    if summary["run_id"] != decisions["run_id"]:
        raise ValueError("Reviews belong to another run; do not reuse labels across reruns")
    questions_path = ROOT / f"data/day7_benchmark/questions_{summary['split']}.json"
    questions = {q["id"]: q for q in read(questions_path)}
    if hashlib.sha256(questions_path.read_bytes()).hexdigest() != config["questions_sha256"]:
        raise ValueError("Question version mismatch")
    if {t["query_id"] for t in traces} != set(questions) or len(traces) != len(questions):
        raise ValueError("Only complete split runs can be finalized")
    if set(decisions["decisions"]) != {t["query_id"] for t in traces if t["status"] != "error"}:
        raise ValueError("Every successful query needs its own authored review")
    reviews, full_context, error_contexts = [], 0, []
    lines = [f"# Source review — {alias}", "", authored["reviewer"], "", authored["policy"], "",
             "Human verification: not performed. These are AI-authored labels, not human certification.", ""]
    for t in traces:
        q = questions[t["query_id"]]
        chunks = {c["id"]: c for e in t["events"] if e.get("event") == "search" for c in e["results"]}
        selected = [chunks[cid] for cid in t["context_ids"]]
        full_context += q["answerable"] and evidence_covered(selected, q)
        lines += [f"## {t['query_id']} ({t['status']})", "", q["question"], "",
                  f"Reference: {q.get('expected_answer', q.get('absence_reason'))}", "",
                  f"Actual answer: {t['answer'] or '(no valid final answer)'}", "", f"Error: {t.get('error')}", ""]
        if t["status"] != "error":
            grade, support, context, reason, citation_reasons = decisions["decisions"][t["query_id"]]
            if len(support) != len(t["citations"]) or len(support) != len(citation_reasons):
                raise ValueError("One decision and reason required per citation")
            if q["answerable"] and context not in (0, 1, 2):
                raise ValueError("Missing context review")
            if any(s and cid not in t["context_ids"] for cid, s in zip(t["citations"], support)):
                raise ValueError("Cannot mark absent citation as supported")
            r = {"query_id": t["query_id"], "citation_support": support, "context_grade": context,
                 "reason": reason, "reviewer": authored["reviewer"], "review_status": "AI-reviewed",
                 "human_reviewed": False, "trace_sha256": hashlib.sha256((run_folder / "traces.json").read_bytes()).hexdigest(),
                 "citation_reviews": [{"id": cid, "supported": s, "reason": why} for cid, s, why in zip(t["citations"], support, citation_reasons)]}
            if q["answerable"]:
                r["answer_grade"] = grade
            else:
                # Authored absence review has explicitly checked refusal and corpus scope.
                if t["status"] != "abstain":
                    raise ValueError("Unanswerable non-refusal requires explicit alternate schema/review")
                r["abstention_correct"] = True
            reviews.append(r)
            lines += [f"Answer grade: {grade}; context grade: {context}. {reason}", ""]
            for cid, s, why in zip(t["citations"], support, citation_reasons):
                lines += [f"- [{cid}]: support={s}. {why}"]
        elif q["answerable"]:
            context, reason = decisions["error_context_reviews"][t["query_id"]]
            if context not in (0, 1, 2):
                raise ValueError("Error cases still need a context review")
            error_contexts.append({"query_id": t["query_id"], "context_grade": context, "reason": reason,
                                   "reviewer": authored["reviewer"], "human_reviewed": False})
            lines += [f"Execution error; no valid final answer to grade. Context grade: {context}. {reason}", ""]
        lines += ["", "Final context actually supplied to the model:", "", "````text", t["context"], "````", ""]
    cases = [{"id": q["id"], "answerable": q["answerable"]} for q in questions.values()]
    metrics = aggregate(cases, traces, reviews)
    semantic_refusals = decisions.get("semantic_refusals_despite_answered", [])
    by_id = {t["query_id"]: t for t in traces}
    if any(by_id[qid]["status"] != "answered" or not questions[qid]["answerable"] for qid in semantic_refusals):
        raise ValueError("Invalid authored semantic refusal label")
    metrics["false_abstention_content_review"] = {"n": metrics["false_abstention"]["n"] + len(semantic_refusals),
                                                  "N": metrics["false_abstention"]["N"],
                                                  "additional_ids": semantic_refusals}
    metrics.update(alias=alias, split=summary["split"], run_id=summary["run_id"], reviewer=authored["reviewer"], human_reviewed=False,
                   context_grades=dict(Counter(str(r["context_grade"]) for r in reviews + error_contexts if r["context_grade"] is not None)),
                   rewritten_query_ids=[t["query_id"] for t in traces if any(e.get("event") == "search" and not e["query_is_original"] for e in t["events"])],
                   context_evidence={"n": full_context, "N": sum(q["answerable"] for q in questions.values())},
                   search_count_distribution=dict(Counter(str(t["searches"]) for t in traces)),
                   model_call_distribution=dict(Counter(str(len(t["model_calls"])) for t in traces)),
                   elapsed_seconds=sum(t["elapsed_ms"] for t in traces)/1000,
                   median_query_seconds=statistics.median(t["elapsed_ms"] for t in traces)/1000,
                   summary=summary)
    for key, value in metrics.items():
        if isinstance(value, dict) and set(("n", "N")) <= value.keys():
            value["rate"] = value["n"] / value["N"] if value["N"] else None
    target = ROOT / "report/evaluation" / alias
    save(target / "reviews.json", reviews)
    save(target / "error_context_reviews.json", error_contexts)
    save(target / "metrics.json", metrics)
    (target / "source_review.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: v for k, v in metrics.items() if k != "summary"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alias", required=True)
    parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args()
    review(args.alias, args.run)
