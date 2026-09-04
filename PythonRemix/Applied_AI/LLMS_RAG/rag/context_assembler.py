# context_assembler.py — turns ranked doc dicts (from retriever/reranker) into the
# single context string the generator hands to the LLM. Owns dedupe + truncation
# so generator.py only has to worry about prompting/calling the model.
import json
from typing import Any

MAX_CONTEXT_CHARS_PER_DOC = 2_000
MAX_TOTAL_CONTEXT_CHARS = 8_000


def _format_doc(doc: dict[str, Any], index: int) -> str:
    doc_id = doc.get("id", f"doc-{index}")
    metadata = doc.get("metadata") or {}
    text = doc.get("text") or doc.get("document") or doc.get("content") or ""
    text = text[:MAX_CONTEXT_CHARS_PER_DOC]

    return (
        f"[{index}] id: {doc_id}\n"
        f"metadata: {json.dumps(metadata, sort_keys=True)}\n"
        f"content: {text}"
    )


def _dedupe_docs(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    unique_docs = []

    for doc in docs:
        doc_id = doc.get("id")
        if doc_id is not None:
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)
        unique_docs.append(doc)

    return unique_docs


def build_context(
    docs: list[dict[str, Any]],
    max_total_chars: int = MAX_TOTAL_CONTEXT_CHARS,
) -> str:
    formatted_parts: list[str] = []
    total_chars = 0

    for index, doc in enumerate(_dedupe_docs(docs), start=1):
        formatted_doc = _format_doc(doc, index)

        # Always include at least one doc, even if it alone exceeds budget.
        if formatted_parts and total_chars + len(formatted_doc) > max_total_chars:
            break

        formatted_parts.append(formatted_doc)
        total_chars += len(formatted_doc)

    return "\n\n".join(formatted_parts)
