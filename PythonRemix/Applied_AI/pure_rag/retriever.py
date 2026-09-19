# retriever.py — thin wrapper around vector_store: given a query string (raw or
# already rewritten upstream), embed + search and return the top-k candidates.
# No rewriting, no reranking, no filtering here on purpose — single job only.

from .vector_store import VectorStore


def retrieve(store: VectorStore, query: str, k: int = 5) -> list[dict]:
    if k <= 0:
        raise ValueError("k must be greater than 0.")

    query_docs = store.query_documents(
        query_texts=[query],
        n_results=k,
    )
    return query_docs[0]
