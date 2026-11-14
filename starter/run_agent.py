"""Run the real local Ollama agent on selected questions, with reviewable traces."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

from ollama_agent import OllamaAgent, TOOLS
from retrievers import Day6DenseRetriever, HybridRetriever, TfidfRetriever

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--method", choices=("tfidf", "dense", "hybrid"), default="dense")
    parser.add_argument("--chunks", type=Path, default=ROOT / "starter/data/day6/chunks.json")
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--ids", nargs="+")
    selection.add_argument("--all", action="store_true", help="Run the entire chosen split")
    selection.add_argument("--question", help="Run one free-form question, without benchmark labels")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--budget", type=int, default=2000)
    parser.add_argument("--max-searches", type=int, default=3)
    parser.add_argument("--max-model-calls", type=int, default=8)
    parser.add_argument("--max-output-tokens", type=int, default=1024)
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--reasoning-mode", choices=("default", "no-think"), default="default")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--output", required=True, type=Path, help="Parent folder; each run gets a new timestamped subfolder")
    args = parser.parse_args()
    if (not 1 <= args.top_k <= 20 or args.budget < 1 or min(args.max_searches, args.max_model_calls,
            args.max_output_tokens, args.num_ctx, args.timeout) < 1 or args.model.endswith(":cloud")):
        parser.error("Invalid model or execution limits")
    chunks = read(args.chunks)
    labels = []
    if args.question:
        if not args.question.strip():
            parser.error("question must not be blank")
        inputs = [{"id": "interactive", "split": args.split, "question": args.question, "filter": None}]
    else:
        questions_path = args.questions or ROOT / f"data/day7_benchmark/questions_{args.split}.json"
        protocol_path = questions_path.parent / "protocol.json"
        if protocol_path.is_file():
            protocol = read(protocol_path)
            if sha(args.chunks) != protocol["input_sha256"]["chunks"] or sha(questions_path) != protocol["output_sha256"].get(questions_path.name):
                raise ValueError("Corpus/questions differ from the frozen benchmark")
        selected = [q for q in read(questions_path) if q["split"] == args.split and (args.all or q["id"] in args.ids)]
        if not selected or args.ids and {q["id"] for q in selected} != set(args.ids):
            parser.error("No questions found, or requested IDs are missing from the chosen split")
        # This is the input boundary: no gold, expected answer or answerability
        # flag is passed into OllamaAgent or a retrieval tool.
        inputs = [{"id": q["id"], "split": q["split"], "question": q["question"], "filter": q.get("filter")} for q in selected]
        labels = [{"id": q["id"], "split": q["split"], "answerable": q.get("answerable", True)} for q in selected]
    run_id = datetime.now(timezone(timedelta(hours=7))).strftime("%Y%m%d_%H%M%S_%f")
    output = args.output.resolve() / run_id
    output.mkdir(parents=True, exist_ok=False)
    print(f"Run folder: {output}", file=sys.stderr, flush=True)
    print("Checking Ollama and initializing real retrieval...", file=sys.stderr, flush=True)
    agent = OllamaAgent(args.model, max_output_tokens=args.max_output_tokens, num_ctx=args.num_ctx,
                       timeout=args.timeout, max_model_calls=args.max_model_calls, reasoning_mode=args.reasoning_mode)
    init_started = time.perf_counter()
    if args.method == "tfidf":
        retriever = TfidfRetriever(chunks)
    else:
        dense = Day6DenseRetriever(chunks, provenance_path=args.chunks.parent / "provenance.json")
        retriever = dense if args.method == "dense" else HybridRetriever(dense, TfidfRetriever(chunks), candidate_k=20)
    save(output / "run_config.json", {"run_id": run_id, "model": agent.configuration,
        "retrieval": retriever.configuration, "retrieval_initialization_seconds": time.perf_counter()-init_started,
        "chunks_sha256": sha(args.chunks), "split": args.split, "query_ids": [q["id"] for q in inputs],
        "questions_sha256": sha(questions_path) if not args.question else None,
        "top_k": args.top_k, "budget_chars": args.budget, "max_searches": args.max_searches,
        "system_prompt": agent.system_prompt, "tools": TOOLS,
        "agent_code_sha256": sha(ROOT / "starter/ollama_agent.py"),
        "scope": "Selected-case smoke run" if not args.all else "Full split run"})
    traces = []
    try:
        for case in inputs:
            qid = case["id"]
            def progress(message):
                print(f"[{qid}] {message}", file=sys.stderr, flush=True)
            trace = agent.run(case["question"], retriever, filters=case.get("filter"),
                              top_k=args.top_k, budget=args.budget, max_searches=args.max_searches, progress=progress)
            trace.update(query_id=qid, split=case["split"])
            traces.append(trace)
            save(output / "traces.json", traces)
            print(json.dumps({"query_id": qid, "status": trace["status"], "answer": trace["answer"],
                              "citations": trace["citations"], "searches": trace["searches"],
                              "error": trace.get("error")}, ensure_ascii=False), flush=True)
    finally:
        if hasattr(retriever, "close"):
            retriever.close()
    save(output / "cases.json", labels)
    by_id = {case["id"]: case for case in labels}
    reviews = []
    for trace in traces:
        if trace["status"] == "error" or trace["query_id"] not in by_id:
            continue
        review = {"query_id": trace["query_id"], "citation_support": [None] * len(trace["citations"]),
                  "context_grade": None, "reason": "", "reviewer": "", "review_status": "pending"}
        review["answer_grade" if by_id[trace["query_id"]]["answerable"] else "abstention_correct"] = None
        reviews.append(review)
    save(output / "reviews_template.json", reviews)
    summary = {"run_id": run_id, "model": args.model, "method": args.method, "split": args.split,
        "n": len(traces), "answered": sum(t["status"] == "answered" for t in traces),
        "abstain": sum(t["status"] == "abstain" for t in traces), "errors": sum(t["status"] == "error" for t in traces),
        "model_calls": sum(len(t["model_calls"]) for t in traces), "searches": sum(t["searches"] for t in traces),
        "prompt_tokens": sum(t["prompt_tokens"] for t in traces), "output_tokens": sum(t["output_tokens"] for t in traces),
        "token_counts_unknown_calls": sum(t["token_counts_unknown_calls"] for t in traces),
        "service_cost_usd": 0, "quality_review": "pending; citation ID validation is not semantic support",
        "run_directory": str(output)}
    save(output / "summary.json", summary)
    save(args.output.resolve() / "latest.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
