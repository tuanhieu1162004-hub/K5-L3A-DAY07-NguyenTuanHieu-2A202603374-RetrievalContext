"""Freeze the reviewed dev decision once, before any test experiment."""
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
from review_results import ROOT, read, save


def main():
    target = ROOT / "report/selection.json"
    if target.exists():
        raise ValueError("Selection already frozen; preserve the original decision")
    if any((ROOT / "starter/results").glob("*test*")):
        raise ValueError("Test output already exists; cannot claim a new pre-test freeze")
    before = read(ROOT / "report/evaluation/tfidf-dev/metrics.json")
    after = read(ROOT / "report/evaluation/dense-dev/metrics.json")
    config = read(Path(after["summary"]["run_directory"]) / "run_config.json")
    save(target, {
        "selected_at": datetime.now(timezone(timedelta(hours=7))).isoformat(),
        "selection_basis": "Full dev offline source review by Codex AI, not human certification. Prioritize grounded answer and citation support, then evidence, latency and cost.",
        "baseline": "tfidf", "selected": "dense",
        "reason": "Dense grounded mean 1.733/2 vs TF-IDF 1.308/2, citation 15/19 vs 11/16, technical errors 0/17 vs 2/17. Both abstain on 2 negatives. Dense exact context evidence14/15 vs8/15. Hybrid retrieval13/15 trails dense14/15 at same budget, so not promoted.",
        "dev_runs": {"tfidf": before["run_id"], "dense": after["run_id"]},
        "shared": {k: config[k] for k in ("model", "top_k", "budget_chars", "max_searches", "chunks_sha256")},
        "agent_code_sha256": config["agent_code_sha256"],
        "code_sha256": {name: hashlib.sha256((ROOT / "starter" / name).read_bytes()).hexdigest()
                        for name in ("run_agent.py", "ollama_agent.py", "retrievers.py", "baseline.py", "check_ollama.py")},
        "test_policy": "Run both frozen configurations once on the same 7 fresh test cases. Preserve errors and all answers. Do not adjust prompts, model, retrieval, labels or budget using test. Grade 5 answerable contexts/answers/citations and2 unanswerable cases for each.",
        "scope": "Basic lab; optional multimodal bonus not attempted"})
    print(target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
