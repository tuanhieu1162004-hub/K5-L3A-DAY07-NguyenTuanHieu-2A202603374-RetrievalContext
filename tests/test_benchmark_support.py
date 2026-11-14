"""Check meaningful evaluation boundaries: complete evidence and denominators."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter"))
from benchmark_support import evidence_covered, fragment_hit, validate
from build_benchmark import fragments_for
from evaluate_retrieval import evaluate, TfidfRetriever


def chunk(cid, text, page=1, chapter=1):
    return {"id": cid, "source_id": "book", "source": "book.pdf", "page": page,
            "text": text, "metadata": {"chapter": chapter}}


def question():
    return {"id": "q", "split": "dev", "question": "script expression print",
            "answerable": True, "expected_answer": "Script expressions need print for visible output.",
            "gold_sets": [[{"source_id": "book", "page": 1, "evidence": "no visible effect"},
                           {"source_id": "book", "page": 1, "evidence": "use print"}]]}


class BenchmarkTests(unittest.TestCase):
    def test_multi_chunk_requires_every_fragment_and_correct_source_page(self):
        chunks = [chunk("a", "script expression has no visible effect"), chunk("b", "use print for script output")]
        q = question()
        validate(chunks, [q])
        self.assertFalse(evidence_covered(chunks[:1], q))
        self.assertTrue(evidence_covered(list(reversed(chunks)), q))
        self.assertFalse(evidence_covered([chunks[0], {**chunks[1], "page": 2}], q))
        self.assertFalse(evidence_covered([chunks[0], {**chunks[1], "source_id": "other"}], q))
        traces, summary = evaluate(TfidfRetriever(chunks), [q], budget=1000)
        self.assertFalse(traces[0]["hit1"])
        self.assertTrue(traces[0]["hit3"] and traces[0]["context_hit"])

    def test_whitespace_matching_keeps_punctuation_and_alternative_groups(self):
        chunks = [chunk("a", "no\nvisible   effect"), chunk("b", "use print")]
        q = question()
        self.assertTrue(evidence_covered(chunks, q))
        self.assertFalse(fragment_hit(chunks[1], {"source_id": "book", "page": 1, "evidence": "use: print"}))
        q["gold_sets"].append([{"source_id": "book", "page": 2, "evidence": "alternative complete answer"}])
        self.assertTrue(evidence_covered([chunk("c", "alternative complete answer", page=2)], q))

    def test_matching_words_at_another_offset_do_not_count(self):
        c = chunk("a", "use print")
        c["metadata"].update(start_char=20, end_char=29)
        gold = {"source_id": "book", "page": 1, "evidence": "use print", "start_char": 0, "end_char": 9}
        self.assertFalse(fragment_hit(c, gold))
        gold.update(start_char=20, end_char=29)
        self.assertTrue(fragment_hit(c, gold))

    def test_unanswerable_is_excluded_and_budget_loss_is_visible(self):
        chunks = [chunk("a", "script expression no visible effect"), chunk("b", "use print script")]
        absent = {"id": "absent", "split": "dev", "question": "script memory requirement",
                  "answerable": False, "expected_behavior": "search_and_abstain",
                  "absence_reason": "No memory requirement in this corpus", "absence_check": {"scope": "all chunks"}}
        validate(chunks, [question(), absent])
        traces, summary = evaluate(TfidfRetriever(chunks), [question(), absent], budget=1)
        self.assertEqual((summary["n_total"], summary["n_answerable"], summary["n_unanswerable"]), (2, 1, 1))
        self.assertEqual(summary["metrics"]["Evidence Hit@3"]["N"], 1)
        self.assertTrue(traces[0]["hit3"])
        self.assertFalse(traces[0]["context_hit"])
        self.assertIsNone(traces[1]["hit3"])
        self.assertFalse(summary["agent_answer_evaluated"])

    def test_user_filter_applies_to_candidates(self):
        chunks = [chunk("a", "script script script", chapter=1), chunk("b", "script", chapter=2)]
        results = TfidfRetriever(chunks).search("script", filters={"chapter": 2})
        self.assertEqual([row["id"] for row in results], ["b"])

    def test_gold_fragmentation_preserves_text_and_all_required_parts(self):
        text = "alpha\n\n beta"
        chunks = [chunk("a", "alpha"), chunk("b", "beta")]
        chunks[0]["metadata"].update(start_char=0, end_char=5)
        chunks[1]["metadata"].update(start_char=text.index("beta"), end_char=len(text))
        gold = {"source_id": "book", "page": 1, "evidence": "alpha beta"}
        fragments = fragments_for(gold, chunks, {("book", 1): {"text": text}})
        self.assertEqual([part["evidence"] for part in fragments], ["alpha", "beta"])
        q = {**question(), "gold_sets": [fragments]}
        self.assertTrue(evidence_covered(chunks, q))
        self.assertFalse(evidence_covered(chunks[:1], q))

    def test_gold_fragmentation_does_not_skip_missing_words(self):
        text = "alpha MISSING beta"
        chunks = [chunk("a", "alpha"), chunk("b", "beta")]
        chunks[0]["metadata"].update(start_char=0, end_char=5)
        chunks[1]["metadata"].update(start_char=text.index("beta"), end_char=len(text))
        gold = {"source_id": "book", "page": 1, "evidence": text}
        with self.assertRaises(ValueError):
            fragments_for(gold, chunks, {("book", 1): {"text": text}})


if __name__ == "__main__":
    unittest.main()
