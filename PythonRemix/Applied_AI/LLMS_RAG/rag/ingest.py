from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .vector_store import VectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = PROJECT_ROOT / "data" / "corpus.json"
DEFAULT_CHUNK_SIZE = 500


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for word in words:
        next_length = current_length + len(word) + (1 if current else 0)

        if current and next_length > chunk_size:
            chunks.append(" ".join(current))
            current = []
            current_length = 0

        current.append(word)
        current_length += len(word) + (1 if len(current) > 1 else 0)

    if current:
        chunks.append(" ".join(current))

    return chunks


def load_corpus(path: Path = CORPUS_PATH) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("corpus.json must contain a JSON list.")

    return documents


def prepare_documents(
    documents: list[dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []

    for document in documents:
        document_id = str(document["id"])
        text = str(document["text"])
        metadata = dict(document.get("metadata", {}))

        chunks = chunk_text(text, chunk_size=chunk_size)

        for index, chunk in enumerate(chunks):
            chunk_id = (
                document_id
                if len(chunks) == 1
                else f"{document_id}#chunk-{index + 1}"
            )

            prepared.append(
                {
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "source_document_id": document_id,
                        "chunk_index": index,
                        "chunk_count": len(chunks),
                    },
                }
            )

    return prepared


def ingest() -> None:
    documents = load_corpus()
    prepared_documents = prepare_documents(documents)

    texts = [document["text"] for document in prepared_documents]
    metadatas = [document["metadata"] for document in prepared_documents]

    store = VectorStore()
    store.add_documents_if_new(
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Ingested {len(texts)} document chunks.")




if __name__ == "__main__":
    ingest()