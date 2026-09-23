# agent/context_window.py
#
# AGENTIC CONCEPT #12 — what to SEND is a separate problem from what to STORE.
# ConversationStore (Phase 1) keeps everything, forever, unmodified. This
# file answers a different question, fresh every single request: given that
# full history, how much of it can we actually afford to send the model
# THIS turn?
#
# Token count is what actually matters here, not character or message count —
# it's what the model's context window and your API bill are both measured
# in. We use tiktoken, the same tokenizer family OpenAI's models use, so the
# count here tracks what the API will actually see.
from typing import Any

import tiktoken

DEFAULT_ENCODING_MODEL = "gpt-4o-mini"

# Every message costs a few tokens beyond just its text, for role/formatting
# metadata the API adds when assembling the real request. This is an
# approximation (OpenAI's own cookbook calls this exact number out as not
# guaranteed) — fine for a TRIMMING decision, where being off by a few tokens
# doesn't change the outcome; you'd want the precise figure if billing off it.
TOKENS_PER_MESSAGE_OVERHEAD = 4


def _get_encoding(model: str):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("o200k_base")


def count_message_tokens(
    message: dict[str, Any], model: str = DEFAULT_ENCODING_MODEL
) -> int:
    encoding = _get_encoding(model)
    total = TOKENS_PER_MESSAGE_OVERHEAD

    content = message.get("content")
    if content:
        total += len(encoding.encode(content))

    # tool_calls carry real payload too (function name + JSON arguments) —
    # skipping these would undercount assistant messages that requested tools.
    for tool_call in message.get("tool_calls") or []:
        function = tool_call.get("function", {})
        total += len(encoding.encode(function.get("name", "")))
        total += len(encoding.encode(function.get("arguments", "")))

    return total


def count_messages_tokens(
    messages: list[dict[str, Any]], model: str = DEFAULT_ENCODING_MODEL
) -> int:
    return sum(count_message_tokens(m, model) for m in messages)


def group_into_turns(
    history: list[dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    """
    Groups messages into atomic units that must never be split when trimming.

    AGENTIC CONCEPT #13 — why grouping, not just dropping oldest messages.
    The API requires every "tool" message to immediately follow the
    assistant message that requested it (matched by tool_call_id). If
    trimming dropped an assistant's tool_calls message but kept its tool
    result (or vice versa), the next request wouldn't just be lower quality
    — it would be rejected as structurally malformed. So "assistant-with-
    tool_calls + all its tool results" is treated as ONE unit, kept or
    dropped together. A plain user message, or an assistant message with no
    tool_calls, is its own unit.
    """
    turns: list[list[dict[str, Any]]] = []
    for message in history:
        if message.get("role") == "tool" and turns:
            turns[-1].append(message)
        else:
            turns.append([message])
    return turns


def build_context_window(
    history: list[dict[str, Any]],
    max_tokens: int,
    model: str = DEFAULT_ENCODING_MODEL,
) -> list[dict[str, Any]]:
    """
    Returns the most recent SUFFIX of `history` that fits within max_tokens,
    never splitting an assistant-tool_calls/tool-result group apart.

    `history` should NOT include the system prompt — Orchestrator adds that
    separately and it's always kept in full, outside this budget. `max_tokens`
    is strictly the budget for history; the caller is responsible for leaving
    separate room for the system prompt, tool schemas, and the new query.
    """
    turns = group_into_turns(history)

    kept_turns: list[list[dict[str, Any]]] = []
    running_total = 0

    # Walk from the newest turn backwards — "keep the newest, drop the
    # oldest" is the standard sliding-window policy. Same "always include at
    # least one, even over budget" rule as context_assembler.build_context,
    # for the same reason: an empty window is worse than a slightly-over one.
    for turn in reversed(turns):
        turn_tokens = sum(count_message_tokens(m, model) for m in turn)
        if kept_turns and running_total + turn_tokens > max_tokens:
            break
        kept_turns.append(turn)
        running_total += turn_tokens

    kept_turns.reverse()
    return [message for turn in kept_turns for message in turn]


if __name__ == "__main__":
    def _tool_round(user_text: str, tool_name: str, tool_query: str, tool_result: str, final_text: str, call_id: str):
        return [
            {"role": "user", "content": user_text},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": f'{{"query": "{tool_query}"}}',
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": call_id, "content": tool_result},
            {"role": "assistant", "content": final_text},
        ]

    history: list[dict[str, Any]] = []
    history += _tool_round(
        "What is our policy on remote time logs?",
        "knowledge_base_search", "remote time log policy",
        "[1] id: doc_1\ncontent: Remote workers must submit time logs by Friday 5 PM." * 3,
        "Time logs are due Friday 5 PM (doc_1).", "call_1",
    )
    history += _tool_round(
        "What about contractor invoices?",
        "knowledge_base_search", "contractor invoice deadline",
        "[1] id: doc_3\ncontent: Contractors must submit invoices monthly by the 25th." * 3,
        "Contractor invoices are due by the 25th each month (doc_3).", "call_2",
    )
    history += _tool_round(
        "And leave notice requirements?",
        "knowledge_base_search", "leave notice requirement",
        "[1] id: doc_7\ncontent: Employees requesting leave must notify their manager at least two weeks in advance." * 3,
        "Leave requests need two weeks' notice (doc_7).", "call_3",
    )

    full_tokens = count_messages_tokens(history)
    print(f"Full history: {len(history)} messages, {full_tokens} tokens")

    print("\n--- generous budget: everything fits ---")
    window = build_context_window(history, max_tokens=full_tokens)
    print(f"kept {len(window)}/{len(history)} messages")
    assert window == history

    print("\n--- tight budget: only the most recent round(s) fit ---")
    window = build_context_window(history, max_tokens=80)
    print(f"kept {len(window)}/{len(history)} messages, {count_messages_tokens(window)} tokens")
    for m in window:
        print(f"  {m['role']}: {str(m.get('content'))[:60]!r}")

    print("\n--- verify no group was split: every 'tool' message has its assistant tool_calls message present ---")
    tool_call_ids_present = {
        tc["id"]
        for m in window
        if m.get("tool_calls")
        for tc in m["tool_calls"]
    }
    for m in window:
        if m.get("role") == "tool":
            assert m["tool_call_id"] in tool_call_ids_present, "orphaned tool message!"
    print("OK — no orphaned tool messages in the trimmed window.")

    print("\n--- even an absurdly tiny budget keeps at least the newest turn ---")
    window = build_context_window(history, max_tokens=1)
    print(f"kept {len(window)} messages (never zero, per the 'always include at least one' rule)")
