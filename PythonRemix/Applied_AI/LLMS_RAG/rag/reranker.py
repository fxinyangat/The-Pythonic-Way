from functools import lru_cache
from typing import Any, cast

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

try:
    from .retriever import retrieve
except ImportError:
    from retriever import retrieve


CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MAX_LENGTH = 512
Document = str | dict[str, Any]


@lru_cache(maxsize=1)
def _load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(CROSS_ENCODER_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(CROSS_ENCODER_MODEL)
    model.to(device)
    model.eval()
    return tokenizer, model, device


def _get_doc_text(doc: Document) -> str:
    if isinstance(doc, str):
        return doc

    text = doc.get("text") or doc.get("document") or doc.get("content")
    if not text:
        raise ValueError("Retrieved doc must contain a text, document, or content field.")

    return text


def rerank_chunks(
    query: str,
    docs: list[Document],
    top_n: int = 3,
) -> list[Document]:
    if not docs or top_n <= 0:
        return []

    pairs = [[query, _get_doc_text(doc)] for doc in docs]
    tokenizer, model, device = _load_model()

    inputs = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=MAX_LENGTH,
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.inference_mode():
        scores = model(**inputs).logits.squeeze(-1)

    scored_docs = sorted(
        zip(docs, scores.tolist()),
        key=lambda x: x[1],
        reverse=True,
    )
    reranked_docs = []
    for doc, score in scored_docs[:top_n]:
        if isinstance(doc, dict):
            doc = {**doc, "rerank_score": score}
        reranked_docs.append(doc)

    return reranked_docs


def retrieve_and_rerank(
    query: str,
    retrieve_k: int = 10,
    top_n: int = 3,
) -> list[dict[str, Any]]:
    docs = retrieve(query, k=retrieve_k)
    return cast(list[dict[str, Any]], rerank_chunks(query, docs, top_n=top_n))
