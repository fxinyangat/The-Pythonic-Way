# agent/memory.py
#
# AGENTIC CONCEPT #11 — durable storage is separate from "what goes to the model."
# ConversationStore's only job is: given a conversation_id, remember every
# message that's ever happened in it, and hand the whole thing back on
# request. It does NOT decide what's relevant, what's too old, or what fits
# a token budget — that's context_window.py's job (next phase). Keeping these
# separate mirrors the production pattern discussed: store everything
# durably, decide what to actually send per-request, separately, every time.
#
# This is the LOCAL analog of "store conversation history in DynamoDB,
# attach some of it to the query." One JSON file per conversation here plays
# the role DynamoDB would play in production — swapping this file's internals
# for a real DynamoDB client later is a contained change (same lesson as
# VectorStore standing in for Pinecone): nothing outside this file would need
# to change, because callers only ever see get()/save().
#
# HONEST SIMPLIFICATION vs real DynamoDB: production systems usually model
# this as ONE ROW PER MESSAGE (partition key = conversation_id, sort key =
# timestamp/sequence number) so you can page through history, query by time
# range, and append without rewriting everything. This file stores one JSON
# array per conversation instead — simpler to read/write locally, but it
# means every save() rewrites the whole conversation. Fine at this scale;
# worth knowing it's not how you'd shard/scale this for real.
import json
from pathlib import Path
from typing import Any

DEFAULT_STORAGE_DIR = Path(__file__).resolve().parent / "conversations"


class ConversationStore:
    def __init__(self, storage_dir: Path = DEFAULT_STORAGE_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, conversation_id: str) -> Path:
        # A conversation_id is caller-provided data — never let it walk out
        # of storage_dir via "../" path traversal. This is a real boundary:
        # if conversation_id ever comes from an HTTP request (the future
        # /chat endpoint), it's untrusted input, same category as a tool's
        # arguments.
        safe_id = conversation_id.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe_id}.json"

    def get(self, conversation_id: str) -> list[dict[str, Any]]:
        path = self._path_for(conversation_id)
        if not path.exists():
            return []

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, conversation_id: str, messages: list[dict[str, Any]]) -> None:
        path = self._path_for(conversation_id)
        with path.open("w", encoding="utf-8") as file:
            json.dump(messages, file, indent=2)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        store = ConversationStore(storage_dir=Path(tmp_dir))

        print("--- unknown conversation returns empty list ---")
        print(store.get("does-not-exist-yet"))

        print("\n--- save then get round-trips exactly ---")
        conversation_id = "demo-conversation"
        messages = [
            {"role": "user", "content": "What is our remote work time log policy?"},
            {"role": "assistant", "content": "Time logs are due Friday 5 PM (doc_1)."},
        ]
        store.save(conversation_id, messages)
        loaded = store.get(conversation_id)
        print(loaded)
        assert loaded == messages, "round-trip mismatch!"

        print("\n--- save again overwrites (simulates appending a new turn) ---")
        messages.append({"role": "user", "content": "What about contractors?"})
        store.save(conversation_id, messages)
        print(store.get(conversation_id))

        print("\n--- path traversal in conversation_id is neutralized ---")
        store.save("../../etc/evil", [{"role": "user", "content": "x"}])
        print("files created:", list(Path(tmp_dir).iterdir()))
