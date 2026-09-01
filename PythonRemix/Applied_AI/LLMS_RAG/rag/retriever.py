try:
    from .vector_store import get_collection, query_documents
except ImportError:
    from vector_store import get_collection, query_documents


def retrieve(query: str, k: int = 5) -> list[dict]:
    if k <= 0:
        raise ValueError("k must be greater than 0.")

    col = get_collection()

    query_docs = query_documents(
        collection=col,
        query_texts=[query],
        n_results=k,
    )

    return query_docs[0]
