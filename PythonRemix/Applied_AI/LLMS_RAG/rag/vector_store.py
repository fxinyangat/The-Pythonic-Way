import os
import hashlib
from pathlib import Path
from functools import lru_cache

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

@lru_cache(maxsize=128)
def get_collection():
    db_path = Path(__file__).resolve().parent / "agentic_rag_vector_db"
    db_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(db_path))

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    embedding_function = OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small",
    )

    return client.get_or_create_collection(
        name="agentic_rag_kb",
        embedding_function=embedding_function,
    )


def add_documents_if_new(collection, documents, metadatas=None):
    if metadatas is None:
        metadatas = [{} for _ in documents]

    ids = [hashlib.md5(doc.encode("utf-8")).hexdigest() for doc in documents]
    existing_ids = set(collection.get(ids=ids)["ids"])

    docs_to_add = []
    metas_to_add = []
    ids_to_add = []

    for doc, meta, doc_id in zip(documents, metadatas, ids):
        if doc_id in existing_ids:
            continue

        docs_to_add.append(doc)
        metas_to_add.append(meta)
        ids_to_add.append(doc_id)

    if docs_to_add:
        collection.add(
            documents=docs_to_add,
            metadatas=metas_to_add,
            ids=ids_to_add,
        )


def query_documents(collection, query_texts, n_results=2):
    raw = collection.query(
        query_texts=query_texts,
        n_results=n_results,
    )

    results = []
    for i in range(len(query_texts)):
        matches = [
            {
                "id": raw["ids"][i][j],
                "text": raw["documents"][i][j],
                "metadata": raw["metadatas"][i][j],
                "distance": raw["distances"][i][j],
            }
            for j in range(len(raw["ids"][i]))
        ]
        results.append(matches)

    return results


if __name__ == "__main__":
    collection = get_collection()

    new_dummy_data = [
        "New rule: remote workers must submit weekly reports by Monday noon."
    ]

    new_metadatas = [
        {"department": "HR", "type": "remote"}
    ]

    add_documents_if_new(collection, new_dummy_data, metadatas=new_metadatas)

    results = query_documents(
        collection,
        ["What are the new rules for remote workers?"],
        n_results=2,
    )

    print(results)