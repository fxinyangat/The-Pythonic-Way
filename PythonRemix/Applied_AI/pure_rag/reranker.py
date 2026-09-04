# reranker.py — second-pass precision filter on top of retriever's cheap
# bi-encoder distance. Cross-encoder scores (query, doc) pairs jointly, so it
# separates "topically similar" from "actually answers the question" much better
# than embedding distance alone. CrossEncoderReranker is constructed once (by the
# caller, e.g. main.py at startup) and passed in — no hidden module-level cache.
from typing import Any, cast

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

try:
    from .retriever import retrieve
except ImportError:
    from PythonRemix.Applied_AI.pure_rag.retriever import retrieve


CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MAX_LENGTH = 512
Document = str | dict[str, Any]


class CrossEncoderReranker:
    def __init__(self, model_name: str = CROSS_ENCODER_MODEL, device: str | None = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def score(self, pairs: list[list[str]]) -> list[float]:
        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=MAX_LENGTH,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.inference_mode():
            return self.model(**inputs).logits.squeeze(-1).tolist()


def _get_doc_text(doc: Document) -> str:
    if isinstance(doc, str):
        return doc

    text = doc.get("text") or doc.get("document") or doc.get("content")
    if not text:
        raise ValueError("Retrieved doc must contain a text, document, or content field.")

    return text


def rerank_chunks(
    reranker: CrossEncoderReranker,
    query: str,
    docs: list[Document],
    top_n: int = 3,
) -> list[Document]:
    if not docs or top_n <= 0:
        return [] # Returning no documents is safer than running the model unnecessarily.


    pairs = [[query, _get_doc_text(doc)] for doc in docs]
    scores = reranker.score(pairs)

    scored_docs = sorted(
        zip(docs, scores),
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
    reranker: CrossEncoderReranker,
    query: str,
    retrieve_k: int = 10,
    top_n: int = 3,
) -> list[dict[str, Any]]:
    docs = retrieve(query, k=retrieve_k)
    return cast(list[dict[str, Any]], rerank_chunks(reranker, query, docs, top_n=top_n))
