"""Evaluate retrieval/context on real data; does not generate agent answers."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

from baseline import pack_context
from benchmark_support import evidence_covered, evidence_groups, fragment_hit, validate
from retrievers import Day6DenseRetriever, HybridRetriever, TfidfRetriever


def evaluate(retriever, questions, *, top_k=3, budget=800):
    if top_k < 3 or budget < 1:
        raise ValueError("top_k must be >=3 for comparable top-3 metrics; budget must be positive")
    strategy = retriever.strategy
    traces = []
    for question in questions:
        started = time.perf_counter()
        # Only the question and supplied metadata filter enter retrieval.
        results = retriever.search(question["question"], filters=question.get("filter"), top_k=top_k)
        context, ids = pack_context(results, budget=budget)
        elapsed_ms = (time.perf_counter() - started) * 1000
        answerable = question.get("answerable", True)
        context_chunks = [chunk for chunk in results if chunk["id"] in ids]
        trace = {"query_id": question["id"], "split": question["split"], "question": question["question"],
                 "answerable": answerable, "status": "retrieved", "strategy": strategy,
                 "top_k": top_k, "budget_chars": budget, "requested_filter": question.get("filter"),
                 "results": [{**chunk, "rank": rank} for rank, chunk in enumerate(results, 1)],
                 "context": context, "context_ids": ids, "context_chars": len(context),
                 "elapsed_ms": elapsed_ms, "hit1": None, "hit3": None, "context_hit": None,
                 "agent_answer_evaluated": False,
                 "retrieval_details": retriever.last_trace}
        if answerable:
            trace.update(gold_sets=evidence_groups(question),
                         hit1=evidence_covered(results[:1], question),
                         hit3=evidence_covered(results[:3], question),
                         context_hit=evidence_covered(context_chunks, question))
            for chunk in trace["results"]:
                chunk["supports_any_fragment"] = any(fragment_hit(chunk, gold) for group in evidence_groups(question) for gold in group)
        traces.append(trace)
    answerable = [trace for trace in traces if trace["answerable"]]
    n = len(answerable)
    summary = {"strategy": strategy, "n_total": len(traces), "n_answerable": n,
               "n_unanswerable": len(traces) - n, "top_k": top_k, "budget_chars": budget,
               "metrics": {}, "median_ms": statistics.median(trace["elapsed_ms"] for trace in traces) if traces else None,
               "avg_context_chars": statistics.mean(trace["context_chars"] for trace in traces) if traces else None,
               "service_cost_usd": 0, "agent_answer_evaluated": False,
               "note": "Unanswerable cases have retrieval traces but are excluded from evidence metrics. Abstention requires a real agent and separate reviews."}
    for field, label in (("hit1", "Hit@1"), ("hit3", "Evidence Hit@3"), ("context_hit", "Context Evidence Rate")):
        count = sum(trace[field] for trace in answerable)
        summary["metrics"][label] = {"n": count, "N": n, "rate": count / n if n else None}
    return traces, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "test"), required=True)
    parser.add_argument("--method", choices=("tfidf", "dense", "hybrid"), default="tfidf")
    parser.add_argument("--day6", type=Path, help="Optional Day 6 repository override; defaults to the exported provenance")
    parser.add_argument("--provenance", type=Path, help="Defaults to provenance.json beside --chunks")
    parser.add_argument("--candidate-k", type=int, default=20, help="Candidates per retriever before hybrid fusion")
    parser.add_argument("--rrf-constant", type=int, default=60)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--budget", type=int, default=800, help="Context budget in characters, including source headers")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 3 <= args.top_k <= 100 or args.budget < 1:
        parser.error("top-k must be in 3..100 and budget must be positive")
    if args.method == "hybrid" and (not args.top_k <= args.candidate_k <= 100 or args.rrf_constant < 1):
        parser.error("Hybrid needs top-k <= candidate-k <= 100 and a positive rrf-constant")
    chunks = json.loads(args.chunks.read_text(encoding="utf-8"))
    questions = [q for q in json.loads(args.questions.read_text(encoding="utf-8")) if q.get("split") == args.split]
    protocol_path = args.questions.parent / "protocol.json"
    if protocol_path.exists():
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        if hashlib.sha256(args.chunks.read_bytes()).hexdigest() != protocol["input_sha256"]["chunks"]:
            raise ValueError("Chunk snapshot differs from the frozen benchmark")
        if hashlib.sha256(args.questions.read_bytes()).hexdigest() != protocol["output_sha256"].get(args.questions.name):
            raise ValueError("Questions differ from the frozen benchmark")
    validate(chunks, questions)
    print(f"Initializing {args.method}; local model/runtime loading can take a few minutes on first use.", file=sys.stderr, flush=True)
    started = time.perf_counter()
    if args.method == "tfidf":
        retriever = TfidfRetriever(chunks)
    else:
        provenance_path = args.provenance or args.chunks.parent / "provenance.json"
        dense = Day6DenseRetriever(chunks, provenance_path=provenance_path, day6=args.day6)
        retriever = dense if args.method == "dense" else HybridRetriever(dense, TfidfRetriever(chunks),
            candidate_k=args.candidate_k, rank_constant=args.rrf_constant)
    index_seconds = time.perf_counter() - started
    print(f"Initialization complete ({index_seconds:.1f}s). Evaluating {len(questions)} {args.split} questions.", file=sys.stderr, flush=True)
    try:
        traces, summary = evaluate(retriever, questions, top_k=args.top_k, budget=args.budget)
    finally:
        if hasattr(retriever, "close"):
            retriever.close()
    summary.update(split=args.split, index_seconds=index_seconds,
                   configuration=retriever.configuration,
                   chunks_sha256=hashlib.sha256(args.chunks.read_bytes()).hexdigest(),
                   questions_sha256=hashlib.sha256(args.questions.read_bytes()).hexdigest())
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, data in (("traces.json", traces), ("summary.json", summary)):
        (args.output / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
