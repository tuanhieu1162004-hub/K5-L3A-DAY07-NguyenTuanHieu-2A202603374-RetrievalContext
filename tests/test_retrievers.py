"""Rank fusion must not mix incomparable raw scores or lose metadata filters."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter"))
from retrievers import HybridRetriever, TfidfRetriever, check_filters, rrf_fuse


def row(cid, score):
    return {"id": cid, "source_id": "book", "source": "book.pdf", "page": 1,
            "text": "text " + cid, "metadata": {"chapter": 2}, "score": score}


class StubRetriever:
    configuration = {"fixture": True}

    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, query, *, filters=None, top_k=3):
        self.calls.append({"query": query, "filters": filters, "top_k": top_k})
        return self.results[:top_k]


class RetrieverTests(unittest.TestCase):
    def test_rrf_uses_rank_and_agreement_instead_of_raw_score_scale(self):
        dense = [row("a", 0.9), row("b", 0.8)]
        lexical = [row("b", 9000), row("c", 8000)]
        fused = rrf_fuse({"dense": dense, "tfidf": lexical}, top_k=3)
        self.assertEqual([chunk["id"] for chunk in fused], ["b", "a", "c"])
        self.assertAlmostEqual(fused[0]["score"], 1 / 62 + 1 / 61)
        self.assertEqual(fused[0]["component_ranks"], {"dense": 2, "tfidf": 1})
        self.assertEqual(fused[0]["component_scores"], {"dense": 0.8, "tfidf": 9000})
        self.assertEqual(dense[1]["score"], 0.8)

    def test_duplicate_ids_and_conflicting_corpus_rows_are_rejected(self):
        with self.assertRaises(ValueError):
            rrf_fuse({"dense": [row("a", 1), row("a", 0.5)]}, top_k=3)
        with self.assertRaises(ValueError):
            rrf_fuse({"dense": [row("a", 1)], "tfidf": [{**row("a", 2), "text": "different corpus"}]}, top_k=3)

    def test_hybrid_preserves_original_query_filters_and_component_rankings(self):
        dense = StubRetriever([row("a", 0.9), row("b", 0.8)])
        lexical = StubRetriever([row("b", 2), row("c", 1)])
        hybrid = HybridRetriever(dense, lexical, candidate_k=5)
        results = hybrid.search("chapter 2 original question", filters={"chapter": 2}, top_k=3)
        expected = {"query": "chapter 2 original question", "filters": {"chapter": 2}, "top_k": 5}
        self.assertEqual(dense.calls, [expected])
        self.assertEqual(lexical.calls, [expected])
        self.assertEqual(results[0]["id"], "b")
        self.assertEqual(hybrid.last_trace["dense_candidates"][1]["rank"], 2)
        with self.assertRaises(ValueError):
            hybrid.search("question", top_k=6)

    def test_filter_scalar_types_match_postgresql_json_boolean_semantics(self):
        chunks = [row("a", 0), row("b", 0)]
        chunks[0]["metadata"] = {"chapter": True}
        chunks[1]["metadata"] = {"chapter": 1}
        retriever = TfidfRetriever(chunks)
        self.assertEqual([chunk["id"] for chunk in retriever.search("text", filters={"chapter": 1})], ["b"])
        with self.assertRaises(ValueError):
            check_filters({"chapter": {"$gt": 1}})


if __name__ == "__main__":
    unittest.main()
