from functools import lru_cache
from statistics import mean
from typing import Any

from openai import OpenAI
from ragas.embeddings import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    AnswerRelevancy,
    ContextPrecisionWithReference,
    ContextRecall,
    ContextRelevance,
    Faithfulness,
)

RAGAS_LLM_MODEL = "gpt-4o-mini"
RAGAS_EMBEDDING_MODEL = "text-embedding-3-small"


@lru_cache(maxsize=1)
def _ragas_llm():
    return llm_factory(model=RAGAS_LLM_MODEL, provider="openai", client=OpenAI())


@lru_cache(maxsize=1)
def _ragas_embeddings():
    return embedding_factory(
        provider="openai", model=RAGAS_EMBEDDING_MODEL, client=OpenAI()
    )

def _numeric_values(docs: list[dict[str, Any]], key: str) -> list[float]:
    values = []
    for doc in docs:
        value = doc.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(float(value))

    return values


def evaluate_retrieval(
    retrieved_docs: list[dict[str, Any]],
    reranked_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    distances = _numeric_values(retrieved_docs, "distance")
    rerank_scores = _numeric_values(reranked_docs, "rerank_score")

    return {
        "retrieved_count": len(retrieved_docs),
        "reranked_count": len(reranked_docs),
        "has_retrieved_docs": bool(retrieved_docs),
        "has_reranked_docs": bool(reranked_docs),
        "best_distance": min(distances) if distances else None,
        "average_distance": mean(distances) if distances else None,
        "best_rerank_score": max(rerank_scores) if rerank_scores else None,
        "average_rerank_score": mean(rerank_scores) if rerank_scores else None,
    }


def evaluate_generation(
    answer: str,
    docs: list[dict[str, Any]],
) -> dict[str, Any]:
    source_ids = [
        doc["id"]
        for doc in docs
        if doc.get("id") and doc["id"] in answer
    ]

    return {
        "has_answer": bool(answer.strip()),
        "answer_length": len(answer),
        "context_docs_available": len(docs),
        "cited_source_ids": source_ids,
        "has_source_citation": bool(source_ids),
    }


def evaluate_pipeline(
    retrieved_docs: list[dict[str, Any]],
    reranked_docs: list[dict[str, Any]],
    answer: str,
) -> dict[str, Any]:
    return {
        "retrieval": evaluate_retrieval(
            retrieved_docs=retrieved_docs,
            reranked_docs=reranked_docs,
        ),
        "generation": evaluate_generation(
            answer=answer,
            docs=reranked_docs,
        ),
    }


def evaluate_ragas_pipeline(
    query: str,
    answer: str,
    docs: list[dict[str, Any]],
    ground_truth: str | None = None,
) -> dict[str, Any]:
    contexts = [doc.get("text", "") for doc in docs]
    llm = _ragas_llm()

    results: dict[str, Any] = {
        "faithfulness": Faithfulness(llm=llm).score(
            user_input=query, response=answer, retrieved_contexts=contexts
        ).value,
        "answer_relevancy": AnswerRelevancy(llm=llm, embeddings=_ragas_embeddings()).score(
            user_input=query, response=answer
        ).value,
        "context_relevance": ContextRelevance(llm=llm).score(
            user_input=query, retrieved_contexts=contexts
        ).value,
    }

    if ground_truth is not None:
        results["context_precision"] = ContextPrecisionWithReference(llm=llm).score(
            user_input=query, reference=ground_truth, retrieved_contexts=contexts
        ).value
        results["context_recall"] = ContextRecall(llm=llm).score(
            user_input=query, retrieved_contexts=contexts, reference=ground_truth
        ).value

    return results