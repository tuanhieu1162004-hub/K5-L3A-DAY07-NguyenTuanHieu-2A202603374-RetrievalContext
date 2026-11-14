"""Offline consistency checks for the submitted real traces, labels and frozen test."""
from datetime import datetime
import hashlib
import json
from pathlib import Path

from agent_metrics import aggregate
from benchmark_support import validate, evidence_covered
from vector_snapshot import validate as validate_vectors

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = read(ROOT / "artifacts/manifest.json")
    for name, expected in manifest["files"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != expected:
            raise ValueError(f"Artifact checksum mismatch: {name}")
    chunks_path = ROOT / "artifacts/day6/chunks.json"
    chunks = read(chunks_path)
    protocol = read(ROOT / "data/day7_benchmark/protocol.json")
    if sha(chunks_path) != protocol["input_sha256"]["chunks"]:
        raise ValueError("Corpus is not the frozen version")
    validate_vectors(read(ROOT / "artifacts/day6/vectors.json"), chunks)
    selection = read(ROOT / "report/selection.json")
    selected_at = datetime.fromisoformat(selection["selected_at"])
    for name, expected in selection["code_sha256"].items():
        if sha(ROOT / "starter" / name) != expected:
            raise ValueError(f"Runtime code changed after selection: {name}")
    for folder in (ROOT / "artifacts/retrieval").iterdir():
        s, traces = read(folder / "summary.json"), read(folder / "traces.json")
        questions = {q["id"]: q for q in read(ROOT / f"data/day7_benchmark/questions_{s['split']}.json")}
        if set(questions) != {t["query_id"] for t in traces}:
            raise ValueError("Incomplete retrieval experiment")
        totals = {"Hit@1": 0, "Evidence Hit@3": 0, "Context Evidence Rate": 0}
        for t in traces:
            q = questions[t["query_id"]]
            if not q["answerable"]:
                continue
            contexts = [r for r in t["results"] if r["id"] in t["context_ids"]]
            for label, rows in (("Hit@1", t["results"][:1]), ("Evidence Hit@3", t["results"][:3]), ("Context Evidence Rate", contexts)):
                totals[label] += evidence_covered(rows, q)
        for label, total in totals.items():
            if s["metrics"][label]["n"] != total or s["metrics"][label]["N"] != sum(q["answerable"] for q in questions.values()):
                raise ValueError("Retrieval metrics disagree with evidence")
    for split in ("dev", "test"):
        path = ROOT / f"data/day7_benchmark/questions_{split}.json"
        questions = read(path)
        validate(chunks, questions)
        if sha(path) != protocol["output_sha256"][path.name]:
            raise ValueError("Frozen questions changed")
        for method in ("tfidf", "dense"):
            alias = f"{method}-{split}"
            folder = ROOT / "artifacts/runs" / alias
            config, summary, traces = [read(folder / name) for name in ("run_config.json", "summary.json", "traces.json")]
            if set(config["query_ids"]) != {q["id"] for q in questions} or len(traces) != len(questions):
                raise ValueError(f"Incomplete split: {alias}")
            if config["chunks_sha256"] != sha(chunks_path) or config["questions_sha256"] != sha(path):
                raise ValueError("Run input mismatch")
            if split == "test":
                started = datetime.strptime(summary["run_id"], "%Y%m%d_%H%M%S_%f").replace(tzinfo=selected_at.tzinfo)
                if started <= selected_at:
                    raise ValueError("Test predates the selection freeze")
                frozen = selection["shared"]
                for key in ("top_k", "budget_chars", "max_searches"):
                    if config[key] != frozen[key]:
                        raise ValueError(f"Test configuration differs: {key}")
                for key in ("model", "digest", "num_ctx", "max_output_tokens", "max_model_calls", "temperature", "seed", "reasoning_mode"):
                    if config["model"][key] != frozen["model"][key]:
                        raise ValueError(f"Test model differs: {key}")
                if config["agent_code_sha256"] != selection["agent_code_sha256"]:
                    raise ValueError("Agent changed after selection")
            for status, field in (("answered", "answered"), ("abstain", "abstain"), ("error", "errors")):
                if sum(t["status"] == status for t in traces) != summary[field]:
                    raise ValueError("Outcome count mismatch")
            for field in ("prompt_tokens", "output_tokens", "token_counts_unknown_calls", "searches"):
                if sum(t[field] for t in traces) != summary[field]:
                    raise ValueError(f"Usage count mismatch: {field}")
            for t in traces:
                if len(t["context"]) > config["budget_chars"] or not set(t["citations"]) <= set(t["context_ids"]):
                    raise ValueError("Context/citation contract violated")
                searches = [e for e in t["events"] if e.get("event") == "search"]
                for event in searches:
                    if event["query_is_original"] != (event["query"] == t["question"]):
                        raise ValueError("Incorrect query rewrite annotation")
                if t["status"] != "error" and not searches:
                    raise ValueError("Successful answer without model-requested retrieval")
            label_folder = ROOT / "report/evaluation" / alias
            reviews = read(label_folder / "reviews.json")
            if any(r["human_reviewed"] or r["trace_sha256"] != sha(folder / "traces.json") for r in reviews):
                raise ValueError("Review attribution/version mismatch")
            calculated = aggregate(questions, traces, reviews)
            saved = read(label_folder / "metrics.json")
            for key, value in calculated.items():
                if isinstance(value, dict):
                    if any(saved[key][k] != v for k, v in value.items()):
                        raise ValueError(f"Review aggregation mismatch {alias}/{key}")
                elif saved[key] != value:
                    raise ValueError("Metric mismatch")
            print(f"OK {alias}: {len(traces)} real traces; {summary['errors']} errors retained; AI reviews attributed")
    forbidden = {".env", "credentials.json", "id_rsa", "id_ed25519"}
    for path in (ROOT / "artifacts").rglob("*"):
        if path.is_file() and path.name in forbidden:
            raise ValueError("Unexpected sensitive file in artifact allowlist")
    print(f"OK {len(manifest['files'])} artifact checksums; frozen corpus/questions; selected-before-test; no false human labels")


if __name__ == "__main__":
    main()
