"""Build/freeze the 24-question benchmark before any Day 7 test retrieval.

Source pages are used to verify labels offline, never passed to the retriever.
The source chunks, document text and original Day 6 gold quotes are preserved.
"""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

from benchmark_support import canonical, validate

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fragments_for(gold, chunks, pages):
    page = pages[(gold["source_id"], gold["page"])]
    pattern = r"\s+".join(re.escape(word) for word in gold["evidence"].split())
    match = re.search(pattern, page["text"])
    if match is None:
        raise ValueError(f"Evidence absent from original page {gold['page']}")
    begin, finish = match.span()
    cursor = begin
    fragments = []
    source_chunks = sorted((chunk for chunk in chunks if chunk["source_id"] == gold["source_id"] and chunk["page"] == gold["page"]),
                           key=lambda chunk: chunk["metadata"]["start_char"])
    for chunk in source_chunks:
        start, end = chunk["metadata"]["start_char"], chunk["metadata"]["end_char"]
        if chunk["text"] != page["text"][start:end]:
            raise ValueError("Chunk no longer matches the source page/offsets")
        left, right = max(begin, start), min(finish, end)
        if left >= right:
            continue
        if page["text"][cursor:left].strip():
            raise ValueError("A non-whitespace part of the evidence is missing between chunks")
        fragment = page["text"][left:right]
        if fragment.strip():
            fragments.append({"source_id": gold["source_id"], "page": gold["page"],
                              "evidence": fragment, "start_char": left, "end_char": right})
        cursor = max(cursor, right)
    if not fragments or page["text"][cursor:finish].strip():
        raise ValueError("Evidence is not fully covered by the source chunks")
    return fragments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "starter/data/day6")
    parser.add_argument("--output", type=Path, default=ROOT / "data/day7_benchmark")
    args = parser.parse_args()
    chunk_path = args.input / "chunks.json"
    draft_path = args.input / "questions_dev_draft.json"
    additions_path = ROOT / "data/day7_additions.json"
    provenance = read(args.input / "provenance.json")
    day6 = Path(provenance["day6_repository"])
    pages_path = day6 / "starter/results/pages.jsonl"
    pdf_path = day6 / "starter/data/thinkpython2.pdf"
    if digest(pdf_path) != provenance["document"]["sha256"]:
        raise ValueError("Source PDF checksum differs from the Day 6 manifest")
    chunks = read(chunk_path)
    source_pages = [json.loads(line) for line in pages_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    pages = {(page["document_id"], page["page"]): page for page in source_pages}
    raw_questions = read(draft_path) + read(additions_path)
    questions = []
    absence_audit = []
    for raw in raw_questions:
        question = dict(raw)
        question["label_provenance"] = {"reviewer": "Codex (AI)",
            "method": "Imported Day 6 dev labels or AI-authored new cases; source-page text and offsets verified by code. Human review remains pending."}
        if question.get("answerable", True):
            question["original_gold"] = question.pop("gold")
            question["gold_sets"] = [fragments_for(gold, chunks, pages) for gold in question["original_gold"]]
            question["evidence_rule"] = "Any complete group; every fragment in that group is required."
        else:
            checks = []
            for term in question["absence_check"]["search_terms"]:
                pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
                matches = []
                for page in source_pages:
                    for match in pattern.finditer(page["text"]):
                        matches.append({"page": page["page"], "context": canonical(page["text"][max(0, match.start()-110):match.end()+180])})
                checks.append({"term": term, "matches": matches})
            absence_audit.append({"query_id": question["id"], "corpus_pages_scanned": len(source_pages),
                "checks": checks, "reason": question["absence_reason"], "reviewer": "Codex (AI)",
                "human_review_pending": True,
                "limitation": "Keyword absence alone is not proof. Inspect relevant source passages and this audit before accepting the label."})
        questions.append(question)
    validate(chunks, questions)
    counts = Counter((q["split"], q.get("answerable", True)) for q in questions)
    for key, minimum in ((("dev", True), 15), (("dev", False), 2), (("test", True), 5), (("test", False), 2)):
        if counts[key] < minimum:
            raise ValueError(f"Benchmark minimum not met: {key}")

    inputs = {"chunks": digest(chunk_path), "dev_draft": digest(draft_path),
              "additions": digest(additions_path), "source_pages": digest(pages_path), "source_pdf": digest(pdf_path)}
    protocol_path = args.output / "protocol.json"
    if protocol_path.exists():
        protocol = read(protocol_path)
        if protocol["input_sha256"] != inputs or any(digest(args.output / filename) != sha for filename, sha in protocol["output_sha256"].items()):
            raise ValueError("Frozen benchmark changed. Use a new output directory and document the new benchmark version.")
        print("Existing frozen benchmark verified; no files changed.")
        return
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, rows in (("questions_dev.json", [q for q in questions if q["split"] == "dev"]),
                           ("questions_test.json", [q for q in questions if q["split"] == "test"]),
                           ("cases.json", [{"id": q["id"], "split": q["split"], "answerable": q.get("answerable", True)} for q in questions]),
                           ("absence_audit.json", absence_audit)):
        (args.output / filename).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    protocol = {
        "created_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds"),
        "benchmark_version": "day7-think-python-v1", "chunk_strategy": provenance["strategy"],
        "input_sha256": inputs,
        "output_sha256": {filename: digest(args.output / filename) for filename in ("questions_dev.json", "questions_test.json", "cases.json", "absence_audit.json")},
        "counts": {"dev_answerable": counts["dev", True], "dev_unanswerable": counts["dev", False],
                   "test_answerable": counts["test", True], "test_unanswerable": counts["test", False]},
        "selection_rule": ["Compare real-agent answer quality and supported citations on dev", "Then compare evidence coverage, latency and cost"],
        "evidence_rule": "Whitespace folding only; source/page/offsets must match. OR between gold_sets, AND within each set. Same full-coverage rule for top-1, top-3 and final context.",
        "test_policy": "New test questions authored before Day 7 retrieval. Do not evaluate test until configurations are selected on dev. Old Day 6 test questions are not reused.",
        "review_status": "AI-prepared benchmark; user/human source and absence-label review pending.",
    }
    protocol_path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), **protocol["counts"], "test_retrieval_run": False}, indent=2))


if __name__ == "__main__":
    main()
