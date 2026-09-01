import json
import os
from typing import Any
from urllib import error, request


CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_GENERATION_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.0
MAX_CONTEXT_CHARS_PER_DOC = 2_000


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


def build_context(docs: list[dict[str, Any]]) -> str:
    return "\n\n".join(
        _format_doc(doc, index)
        for index, doc in enumerate(docs, start=1)
    )


def build_messages(query: str, docs: list[dict[str, Any]]) -> list[dict[str, str]]:
    context = build_context(docs)

    return [
        {
            "role": "system",
            "content": (
                "You are a careful RAG assistant. Answer only from the provided "
                "context. If the context is not enough, say that you do not have "
                "enough information. Cite supporting document ids when possible."
            ),
        },
        {
            "role": "user",
            "content": f"Question:\n{query}\n\nContext:\n{context}",
        },
    ]


def _post_chat_completion(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    body = json.dumps(payload).encode("utf-8")

    http_request = request.Request(
        CHAT_COMPLETIONS_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"OpenAI generation request failed: {detail}") from exc


def generate_answer(
    query: str,
    docs: list[dict[str, Any]],
    model: str = DEFAULT_GENERATION_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    if not docs:
        return "I do not have enough information in the retrieved context to answer."

    messages = build_messages(query=query, docs=docs)
    response = _post_chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
    )

    return response["choices"][0]["message"]["content"].strip()
