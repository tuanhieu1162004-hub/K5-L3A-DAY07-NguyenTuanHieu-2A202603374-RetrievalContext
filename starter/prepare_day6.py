"""Export existing Day 6 chunks and dev questions without changing Day 6.

Only development questions are exported. Day 6 test results already exist, so
the Day 7 benchmark needs a new independent test split.
"""
import argparse
import json
import re
from pathlib import Path

from convert_day6 import convert_chunk, convert_question


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description="Prepare real Day 6 data for Day 7 (dev only)")
    parser.add_argument("--day6", required=True, type=Path, help="Day 6 repository or its outer folder")
    parser.add_argument("--strategy", default="C", choices=("A", "B", "C"))
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "data" / "day6")
    args = parser.parse_args()

    day6 = args.day6.resolve()
    if not (day6 / "artifacts" / "strategies.json").is_file():
        day6 = day6 / "K5-L3-Day06-DataIngestionEngineering-main"
    chunk_file = day6 / "starter" / "results" / f"chunks_{args.strategy}.jsonl"
    if not chunk_file.is_file():
        parser.error(f"Day 6 chunk export not found: {chunk_file}")

    config = read_json(day6 / "artifacts" / "strategies.json")
    stats = read_json(day6 / "starter" / "results" / "ingestion_stats.json")
    manifest = read_json(day6 / "data" / "manifest.json")
    chunks = [convert_chunk(row) for row in read_jsonl(chunk_file)]
    questions = []
    for raw in read_jsonl(day6 / "benchmark" / "questions.jsonl"):
        if raw.get("split") != "dev":
            continue
        question = convert_question(raw)
        question["answerable"] = True
        # Preserve alternative evidence; the starter converter handles only
        # the primary evidence in the original Day 6 JSONL schema.
        for alternative in raw.get("gold_alternatives", []):
            question["gold"].append({
                "source_id": alternative["source_id"],
                "page": alternative["page"],
                "evidence": alternative["evidence_quote"],
            })
        questions.append(question)

    if not chunks or len({chunk["id"] for chunk in chunks}) != len(chunks):
        raise ValueError("Chunks must have unique IDs and must not be empty")
    for chunk in chunks:
        if not all(isinstance(chunk[key], str) and chunk[key].strip() for key in ("id", "text", "source_id", "source")):
            raise ValueError("Invalid chunk fields")
        if chunk["page"] is None or not isinstance(chunk["metadata"], dict):
            raise ValueError("Invalid chunk page/metadata")
    if not questions or len({q["id"] for q in questions}) != len(questions):
        raise ValueError("Dev questions must have unique IDs and must not be empty")

    # Day 6 folds layout whitespace when matching; Day 7's sample baseline
    # requires literal quotes inside single chunks. Preserve gold verbatim and
    # expose these differences for review instead of dropping hard questions.
    canonical = lambda text: re.sub(r"\s+", " ", text).strip()
    pages = read_jsonl(day6 / "starter" / "results" / "pages.jsonl")
    audit = []
    for question in questions:
        evidence_checks = []
        for gold in question["gold"]:
            source_chunks = [chunk for chunk in chunks if chunk["source_id"] == gold["source_id"] and chunk["page"] == gold["page"]]
            source_pages = [page for page in pages if page["document_id"] == gold["source_id"] and page["page"] == gold["page"]]
            if not any(canonical(gold["evidence"]) in canonical(page["text"]) for page in source_pages):
                raise ValueError(f"Evidence absent from source page: {question['id']}")
            evidence_checks.append({
                "source_id": gold["source_id"], "page": gold["page"],
                "exact_chunk_ids": [chunk["id"] for chunk in source_chunks if gold["evidence"] in chunk["text"]],
                "whitespace_folded_chunk_ids": [chunk["id"] for chunk in source_chunks if canonical(gold["evidence"]) in canonical(chunk["text"])],
            })
        audit.append({"query_id": question["id"], "evidence_checks": evidence_checks,
                      "has_single_chunk_evidence": any(check["whitespace_folded_chunk_ids"] for check in evidence_checks),
                      "starter_literal_validation_passes": all(check["exact_chunk_ids"] for check in evidence_checks)})
    expected_count = stats["strategies"][args.strategy]["chunk_count"]
    if len(chunks) != expected_count:
        raise ValueError(f"Chunk count differs from ingestion stats: {len(chunks)} != {expected_count}")

    provenance = {
        "day6_repository": str(day6),
        "chunk_export": str(chunk_file),
        "strategy": args.strategy,
        "chunk_count": len(chunks),
        "dev_answerable_count": len(questions),
        "document": {key: manifest[key] for key in (
            "title", "author", "source_path_or_url", "license_or_permission",
            "sha256", "verified_content_page_count",
        )},
        "embedding": {
            "model": config["model"],
            "revision": config["model_revision"],
            "dimensions": stats["dimensions"],
            "normalize_embeddings": config["normalize_embeddings"],
        },
        "vector_store": {"backend": "PostgreSQL/pgvector", "table": "day6_chunks", "strategy": args.strategy},
        "benchmark_note": "Dev questions are DRAFTS: see benchmark_import_audit.json before evaluation. Preserve all original golds; adapt whitespace matching and multi-chunk evidence explicitly. Add dev abstention cases and create a new Day 7 test split.",
        "filter_note": "TF-IDF starter ignores filters; keep filter handling equivalent across methods or report the difference explicitly.",
    }
    output = args.output.resolve()
    if output.is_relative_to(day6):
        parser.error("Output must be outside the Day 6 repository")
    output.mkdir(parents=True, exist_ok=True)
    for filename, data in (("chunks.json", chunks), ("questions_dev_draft.json", questions),
                           ("benchmark_import_audit.json", audit), ("provenance.json", provenance)):
        (output / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"strategy": args.strategy, "chunks": len(chunks), "dev_questions_draft": len(questions),
                      "dev_questions_without_single_chunk_evidence": [row["query_id"] for row in audit if not row["has_single_chunk_evidence"]],
                      "benchmark_ready": False, "output": str(output), "test_exported": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
