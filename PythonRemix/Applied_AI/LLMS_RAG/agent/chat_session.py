# agent/chat_session.py
#
# AGENTIC CONCEPT #15 — this is the future API endpoint's logic, minus HTTP.
# `send_message()` is exactly what a POST /chat handler would do per request:
# load this conversation's history, decide how much of it to send, run the
# agent, persist the (pruned) result. Writing it now, without FastAPI wrapped
# around it, means the actual memory-management logic gets built and tested
# on its own — the HTTP layer later becomes a thin adapter around this
# function, not the place where this logic lives.
#
# WHY WE TRIM AND PRUNE THE STORED COPY, NOT JUST WHAT WE SEND: this is the
# subtle part. `store.get()` returns the FULL, untrimmed history — that's the
# durability guarantee from Phase 1. `build_context_window()` only decides
# what to SEND the model this turn; it must never be mistaken for what gets
# saved back, or every trimmed-away message would be permanently lost the
# next time we save. So: window the full history for the API call, but
# always append the new turn onto the FULL history (not the windowed slice)
# before persisting. Pruning (shrinking old tool results) is safe to apply
# to the full stored copy though — unlike windowing, it's meant to be
# permanent, since a pruned tool result has already done its job.
from typing import Any

from agent.context_window import build_context_window
from agent.memory import ConversationStore
from agent.orchestrator import Orchestrator
from agent.pruning import prune_old_tool_results

DEFAULT_MAX_HISTORY_TOKENS = 3_000
DEFAULT_KEEP_LAST_N_TOOL_ROUNDS = 1


def send_message(
    orchestrator: Orchestrator,
    store: ConversationStore,
    conversation_id: str,
    query: str,
    max_history_tokens: int = DEFAULT_MAX_HISTORY_TOKENS,
    keep_last_n_tool_rounds: int = DEFAULT_KEEP_LAST_N_TOOL_ROUNDS,
) -> dict[str, Any]:
    full_history = store.get(conversation_id)
    windowed_history = build_context_window(full_history, max_tokens=max_history_tokens)

    result = orchestrator.run(query, history=windowed_history)

    # result["messages"] = [system, *windowed_history, *this turn's new
    # messages]. Slice off exactly the system prompt + the windowed slice we
    # sent in, to isolate only what's NEW this turn — then append that onto
    # the FULL history, not the (possibly shorter) windowed one, so nothing
    # trimmed-away for this request gets lost from storage.
    new_messages = result["messages"][1 + len(windowed_history) :]
    updated_full_history = full_history + new_messages

    pruned_history = prune_old_tool_results(
        updated_full_history, keep_last_n_tool_rounds=keep_last_n_tool_rounds
    )
    store.save(conversation_id, pruned_history)

    return {
        "answer": result["answer"],
        "turns_used": result["turns_used"],
        "sent_to_model_messages": len(windowed_history),
        "stored_messages": len(pruned_history),
    }


if __name__ == "__main__":
    from rag.config import Clients
    from rag.reranker import CrossEncoderReranker
    from rag.vector_store import VectorStore
    from tools.rag_tools import register_rag_tools
    import tools.web_tools  # noqa: F401 — registers web_search on import

    store_v = VectorStore()
    reranker = CrossEncoderReranker()
    clients = Clients()
    register_rag_tools(store_v, reranker, clients)

    orchestrator = Orchestrator(clients, tool_categories=["rag", "web"])
    conversation_store = ConversationStore()
    conversation_id = "demo-multi-turn"

    # A follow-up sequence that only makes sense WITH memory: turn 2 never
    # says "remote workers" again, it relies on the model having "time logs"
    # in context from turn 1 to correctly answer about contractors instead.
    turns = [
        "What is our policy on remote work time logging?",
        "What about the equivalent deadline for contractors?",
        "And what's the notice period for taking leave?",
    ]

    for query in turns:
        print(f"\n{'=' * 70}\nUSER: {query}")
        result = send_message(orchestrator, conversation_store, conversation_id, query)
        print(f"ANSWER ({result['turns_used']} turn(s), "
              f"sent {result['sent_to_model_messages']} history messages, "
              f"stored {result['stored_messages']} total): {result['answer']}")

    print(f"\n{'=' * 70}\nFinal stored history for {conversation_id!r}:")
    for m in conversation_store.get(conversation_id):
        content_preview = str(m.get("content"))[:70]
        print(f"  {m['role']}: {content_preview}")
