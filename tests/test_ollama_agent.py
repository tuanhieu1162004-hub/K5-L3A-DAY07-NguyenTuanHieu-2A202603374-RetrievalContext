"""Protocol tests use fixtures; reported agent smoke runs use the real model."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter"))
from baseline import pack_context
from check_ollama import check, require_complete, thinking_setting
from ollama_agent import OllamaAgent


def chunk(cid, text):
    return {"id": cid, "text": text, "source_id": "book", "source": "book.pdf", "page": 1, "metadata": {}}


def response(name, args, *, reason="stop"):
    return {"done": True, "done_reason": reason, "prompt_eval_count": 10, "eval_count": 5,
            "message": {"role": "assistant", "content": "", "thinking": "private fixture reasoning",
                        "tool_calls": [{"function": {"name": name, "arguments": args}}]}}


class FixtureRetriever:
    strategy = "fixture"
    last_trace = None

    def __init__(self, batches):
        self.batches = iter(batches)
        self.calls = []

    def search(self, query, *, filters=None, top_k=3):
        self.calls.append((query, filters, top_k))
        return next(self.batches)


def transport(responses, requests):
    replies = iter(responses)
    def request(path, payload=None, **kwargs):
        if path == "/api/show":
            return {"capabilities": ["completion", "tools", "thinking"], "thinking": {"values": [True], "default": True}}
        if path == "/api/tags":
            return {"models": [{"name": "fixture", "digest": "fixture-digest"}]}
        if path == "/api/version":
            return {"version": "fixture"}
        if path == "/api/chat":
            requests.append(copy.deepcopy(payload))
            reply = next(replies)
            if isinstance(reply, Exception):
                raise reply
            return reply
        raise AssertionError(path)
    return request


class OllamaTests(unittest.TestCase):
    def test_search_is_model_requested_and_final_ids_are_in_context(self):
        requests = []
        replies = [response("search_documents", {"query": "original question"}),
                   response("final_answer", {"answer": "Seven days. [c1]"})]
        retriever = FixtureRetriever([[chunk("c1", "Seven days.")]])
        with patch("ollama_agent.request_json", side_effect=transport(replies, requests)):
            agent = OllamaAgent("fixture")
            result = agent.run("original question", retriever, filters={"chapter": 1})
        self.assertEqual(result["status"], "answered")
        self.assertEqual(retriever.calls, [("original question", {"chapter": 1}, 3)])
        self.assertEqual(result["citations"], ["c1"])
        self.assertTrue(result["events"][0]["query_is_original"])
        self.assertIs(requests[0]["think"], True)
        final_tool = next(tool for tool in requests[0]["tools"] if tool["function"]["name"] == "final_answer")
        self.assertEqual(final_tool["function"]["parameters"]["required"], ["answer"])
        self.assertNotIn("thinking", result["model_calls"][0]["message"])

    def test_final_decision_before_search_needs_protocol_repair(self):
        requests = []
        replies = [response("abstain", {"reason": "Too early"}),
                   response("search_documents", {"query": "missing detail"}),
                   response("abstain", {"reason": "The retrieved passages do not state that detail."})]
        with patch("ollama_agent.request_json", side_effect=transport(replies, requests)):
            result = OllamaAgent("fixture").run("missing detail", FixtureRetriever([[]]))
        self.assertEqual(result["status"], "abstain")
        self.assertEqual(result["searches"], 1)
        self.assertEqual(result["events"][0]["reason"], "final_before_search")

    def test_superseded_context_cannot_be_cited_and_old_tool_context_is_compacted(self):
        old, new = chunk("old", "old evidence"), chunk("new", "new evidence")
        budget = len(pack_context([new], 1000)[0])
        requests = []
        replies = [response("search_documents", {"query": "first query"}),
                   response("search_documents", {"query": "refined query"}),
                   response("final_answer", {"answer": "Stale answer. [old]"}),
                   response("abstain", {"reason": "The current passages do not support the answer."})]
        with patch("ollama_agent.request_json", side_effect=transport(replies, requests)):
            result = OllamaAgent("fixture").run("first query", FixtureRetriever([[old], [new]]), budget=budget)
        self.assertEqual(result["context_ids"], ["new"])
        self.assertEqual(result["status"], "abstain")
        self.assertTrue(any(event.get("reason") == "invalid_citations" for event in result["events"]))
        tool_messages = [msg for msg in requests[2]["messages"] if msg["role"] == "tool"]
        self.assertNotIn("old evidence", " ".join(msg["content"] for msg in tool_messages))
        self.assertIn("new evidence", tool_messages[-1]["content"])

    def test_token_limit_is_error_instead_of_abstention_or_success(self):
        requests = []
        with patch("ollama_agent.request_json", side_effect=transport([response("abstain", {"reason": "partial"}, reason="length")], requests)):
            result = OllamaAgent("fixture").run("question", FixtureRetriever([]))
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["searches"], 0)
        self.assertIn("token limit", result["error"])

    def test_health_check_does_not_accept_truncation_and_respects_thinking_metadata(self):
        self.assertIsNone(thinking_setting({"thinking": None}))
        self.assertIs(thinking_setting({"thinking": {"values": [True], "default": True}}), True)
        self.assertIs(thinking_setting({"thinking": {"values": [True, False]}}), False)
        with self.assertRaises(RuntimeError):
            require_complete({"done": True, "done_reason": "length", "message": {"content": "partial"}})
        replies = [{"version": "fixture"}, {"models": [{"name": "fixture"}]},
                   {"capabilities": ["tools"], "thinking": {"values": [True]}},
                   {"done": True, "done_reason": "length", "message": {"content": "partial"}}]
        with patch("check_ollama.request_json", side_effect=replies):
            result = check("fixture", chat=True)
        self.assertEqual(result["status"], "error")
        self.assertFalse(result["chat_tested"])

    def test_explicit_abstain_token_after_search_is_a_model_decision(self):
        requests = []
        replies = [response("search_documents", {"query": "question"}),
                   {"done": True, "done_reason": "stop", "message": {"role": "assistant", "content": "abstain"}}]
        with patch("ollama_agent.request_json", side_effect=transport(replies, requests)):
            result = OllamaAgent("fixture").run("question", FixtureRetriever([[]]))
        self.assertEqual(result["status"], "abstain")
        self.assertEqual(result["raw_model_final"], "abstain")
        self.assertEqual(result["events"][-1]["via"], "explicit_model_decision_token")

    def test_arbitrary_text_without_citations_is_not_turned_into_abstention(self):
        requests = []
        replies = [response("search_documents", {"query": "question"}),
                   {"done": True, "done_reason": "stop", "message": {"role": "assistant", "content": "It costs ten dollars."}}]
        with patch("ollama_agent.request_json", side_effect=transport(replies, requests)):
            result = OllamaAgent("fixture", max_model_calls=2).run("question", FixtureRetriever([[]]))
        self.assertEqual(result["status"], "error")

    def test_failed_http_attempt_is_counted_and_token_usage_is_unknown(self):
        requests = []
        with patch("ollama_agent.request_json", side_effect=transport([RuntimeError("timeout fixture")], requests)):
            result = OllamaAgent("fixture").run("question", FixtureRetriever([]))
        self.assertEqual(result["status"], "error")
        self.assertEqual(len(result["model_calls"]), 1)
        self.assertEqual(result["model_calls"][0]["status"], "error")
        self.assertEqual(result["token_counts_unknown_calls"], 1)

    def test_normal_assistant_final_with_valid_citations_after_tool_is_accepted(self):
        requests = []
        replies = [response("search_documents", {"query": "question"}),
                   {"done": True, "done_reason": "stop", "message": {"role": "assistant", "content": "final_answer\nSeven days. [c1]"}}]
        with patch("ollama_agent.request_json", side_effect=transport(replies, requests)):
            result = OllamaAgent("fixture").run("question", FixtureRetriever([[chunk("c1", "Seven days.")]]))
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["answer"], "Seven days. [c1]")
        self.assertTrue(result["raw_model_final"].startswith("final_answer\n"))
        self.assertEqual(result["events"][-1]["via"], "assistant_content")


if __name__ == "__main__":
    unittest.main()
