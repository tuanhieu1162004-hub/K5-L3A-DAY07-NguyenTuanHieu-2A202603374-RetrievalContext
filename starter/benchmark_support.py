"""Evidence checks shared by Day 7 retrieval experiments (no model calls).

gold_sets is OR between groups and AND within a group. Each fragment must be
present in a retrieved chunk with the correct source and page. Layout whitespace
is folded for scoring only; source text and code indentation are never rewritten.
"""
import re
import unicodedata


def canonical(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def evidence_groups(question):
    if "gold_sets" in question:
        return question["gold_sets"]
    return [[gold] for gold in question.get("gold", [])]


def fragment_hit(chunk, gold):
    if chunk["source_id"] != gold["source_id"] or chunk["page"] != gold["page"] or not canonical(gold["evidence"]):
        return False
    if "start_char" in gold or "end_char" in gold:
        start, end = gold.get("start_char"), gold.get("end_char")
        chunk_start, chunk_end = chunk["metadata"].get("start_char"), chunk["metadata"].get("end_char")
        if not all(type(value) is int for value in (start, end, chunk_start, chunk_end)):
            return False
        if not chunk_start <= start < end <= chunk_end:
            return False
        return canonical(chunk["text"][start - chunk_start:end - chunk_start]) == canonical(gold["evidence"])
    return canonical(gold["evidence"]) in canonical(chunk["text"])


def evidence_covered(chunks, question):
    return any(all(any(fragment_hit(chunk, gold) for chunk in chunks) for gold in group)
               for group in evidence_groups(question))


def validate(chunks, questions):
    if not chunks or not questions:
        raise ValueError("Chunks/questions must not be empty")
    chunk_ids = set()
    for chunk in chunks:
        for key in ("id", "source_id", "source", "text"):
            if not isinstance(chunk.get(key), str) or not chunk[key].strip():
                raise ValueError(f"Invalid chunk {key}")
        if chunk["id"] in chunk_ids or type(chunk.get("page")) is not int or not isinstance(chunk.get("metadata"), dict):
            raise ValueError("Duplicate chunk ID or invalid page/metadata")
        chunk_ids.add(chunk["id"])
    question_ids = set()
    for question in questions:
        qid = question.get("id")
        if not isinstance(qid, str) or not qid.strip() or qid in question_ids:
            raise ValueError("Invalid/duplicate question ID")
        question_ids.add(qid)
        if question.get("split") not in ("dev", "test") or not isinstance(question.get("question"), str) or not question["question"].strip():
            raise ValueError(f"{qid}: invalid split/question")
        if type(question.get("answerable", True)) is not bool:
            raise ValueError(f"{qid}: answerable must be boolean")
        filters = question.get("filter")
        if filters is not None and not isinstance(filters, dict):
            raise ValueError(f"{qid}: filter must be an object")
        if question.get("answerable", True) is False:
            if (question.get("expected_behavior") != "search_and_abstain" or not question.get("absence_reason")
                    or not question.get("absence_check") or question.get("gold") or question.get("gold_sets")):
                raise ValueError(f"{qid}: absent evidence needs a documented check and no positive gold")
            continue
        if not isinstance(question.get("expected_answer"), str) or not question["expected_answer"].strip():
            raise ValueError(f"{qid}: expected_answer missing")
        groups = evidence_groups(question)
        if not isinstance(groups, list) or not groups:
            raise ValueError(f"{qid}: evidence groups missing")
        for group in groups:
            if not isinstance(group, list) or not group:
                raise ValueError(f"{qid}: empty evidence group")
            for gold in group:
                if (not isinstance(gold, dict) or not isinstance(gold.get("source_id"), str)
                        or type(gold.get("page")) is not int
                        or not isinstance(gold.get("evidence"), str) or not gold["evidence"].strip()):
                    raise ValueError(f"{qid}: invalid evidence fragment")
                if not any(fragment_hit(chunk, gold) for chunk in chunks):
                    raise ValueError(f"{qid}: evidence fragment absent from chunks/source/page")
                if filters and not any(fragment_hit(chunk, gold) and all(chunk["metadata"].get(key) == value for key, value in filters.items()) for chunk in chunks):
                    raise ValueError(f"{qid}: evidence does not satisfy the supplied filter")
