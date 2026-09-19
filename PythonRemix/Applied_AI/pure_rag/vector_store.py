# vector_store.py — owns the Chroma collection: persistent client + OpenAI
# embedding function, add-with-dedupe, and query normalized to a plain list of
# {id, text, metadata, distance} dicts so nothing downstream depends on Chroma's shape.
# VectorStore is constructed once (by the caller, e.g. main.py at startup) and
# passed in — no hidden module-level cache.
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()


DB_DIR_NAME = "agentic_rag_vector_db"
COLLECTION_NAME = "agentic_rag_kb"
EMBEDDING_MODEL = "text-embedding-3-small"


class VectorStore:
    def __init__(
        self,
        db_dir_name: str = DB_DIR_NAME,
        collection_name: str = COLLECTION_NAME,
        embedding_model: str = EMBEDDING_MODEL,
    ):
        db_path = Path(__file__).resolve().parent / db_dir_name
        db_path.mkdir(parents=True, exist_ok=True)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        client = chromadb.PersistentClient(path=str(db_path))
        embedding_function = OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=embedding_model,
        )

        self.collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
        )



    def query_documents(
        self,
        query_texts: list[str],
        n_results: int = 2,
    ) -> list[list[dict[str, Any]]]:
        if n_results <= 0:
            raise ValueError("n_results must be greater than 0.")

        raw = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
        )

        results = []
        for query_index in range(len(query_texts)):
            matches = [
                {
                    "id": raw["ids"][query_index][match_index],
                    "text": raw["documents"][query_index][match_index],
                    "metadata": raw["metadatas"][query_index][match_index] or {},
                    "distance": raw["distances"][query_index][match_index],
                }
                for match_index in range(len(raw["ids"][query_index]))
            ]
            results.append(matches)

        return results

    def add_documents_if_new(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        if not documents:
            return

        if metadatas is None:
            metadatas = [{} for _ in documents]

        if len(documents) != len(metadatas):
            raise ValueError("documents and metadatas must have the same length.")

        if ids is None:
            ids = [hashlib.md5(doc.encode("utf-8")).hexdigest() for doc in documents]
        elif len(documents) != len(ids):
            raise ValueError("documents and ids must have the same length.")

        if len(set(ids)) != len(ids):
            raise ValueError("ids must be unique within a batch.")

        existing_ids = set(self.collection.get(ids=ids)["ids"])

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
            self.collection.add(
                documents=docs_to_add,
                metadatas=metas_to_add,
                ids=ids_to_add,
            )
