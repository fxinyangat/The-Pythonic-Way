# agent/pruning.py
#
# AGENTIC CONCEPT #14 — a scalpel for a KNOWN waste source, not another blunt
# sliding window. context_window.py's trimming drops whole old turns
# indiscriminately, oldest first, whatever they are. This file targets the
# ONE thing we already measured to be the biggest waste (context_window's
# own demo: tool-call rounds cost 4-6x a plain message). Once the model has
# used a tool result to write a final answer, that raw retrieved text has
# already done its job — keeping it around in full, forever, on every future
# request buys nothing but cost. Rather than waiting for the sliding window
# to eventually drop the whole round, we shrink just the tool result's
# CONTENT as soon as a round is "closed" (the conversation has moved past
# it), while keeping every message's structure intact.
#
# WHY WE DON'T DELETE THE MESSAGES: the API requires every "tool" message to
# exist and match a tool_call_id from a preceding assistant message — same
# rule context_window.py's grouping respects. Deleting a pruned tool message
# would orphan its assistant tool_calls message and break that contract.
# Shrinking `content` to a placeholder is safe; removing the message is not.
from typing import Any

from agent.context_window import group_into_turns

DEFAULT_PLACEHOLDER = "[tool result omitted — already used in an earlier answer]"


def prune_old_tool_results(
    messages: list[dict[str, Any]],
    keep_last_n_tool_rounds: int = 1,
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> list[dict[str, Any]]:
    """
    Replaces the `content` of "tool" messages in older rounds with a short
    placeholder, keeping the most recent `keep_last_n_tool_rounds` tool
    rounds untouched (a likely follow-up like "tell me more about that" can
    still reference them). Message count and order are unchanged — only the
    content of already-used tool results shrinks.
    """
    turns = group_into_turns(messages)

    tool_round_indexes = [
        i for i, turn in enumerate(turns) if any(m.get("role") == "tool" for m in turn)
    ]
    protected = (
        set(tool_round_indexes[-keep_last_n_tool_rounds:])
        if keep_last_n_tool_rounds > 0
        else set()
    )

    pruned_turns = []
    for i, turn in enumerate(turns):
        if i in tool_round_indexes and i not in protected:
            turn = [
                {**m, "content": placeholder} if m.get("role") == "tool" else m
                for m in turn
            ]
        pruned_turns.append(turn)

    return [message for turn in pruned_turns for message in turn]


if __name__ == "__main__":
    from agent.context_window import count_messages_tokens

    def tool_round(user_text, tool_name, tool_query, tool_result, final_text, call_id):
        return [
            {"role": "user", "content": user_text},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {"name": tool_name, "arguments": f'{{"query": "{tool_query}"}}'},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": call_id, "content": tool_result},
            {"role": "assistant", "content": final_text},
        ]

    history: list[dict[str, Any]] = []
    history += tool_round(
        "What is our policy on remote time logs?", "knowledge_base_search",
        "remote time log policy",
        "[1] id: doc_1\ncontent: Remote workers must submit time logs by Friday 5 PM." * 3,
        "Time logs are due Friday 5 PM (doc_1).", "call_1",
    )
    history += tool_round(
        "What about contractor invoices?", "knowledge_base_search",
        "contractor invoice deadline",
        "[1] id: doc_3\ncontent: Contractors must submit invoices monthly by the 25th." * 3,
        "Contractor invoices are due by the 25th each month (doc_3).", "call_2",
    )
    history += tool_round(
        "And leave notice requirements?", "knowledge_base_search",
        "leave notice requirement",
        "[1] id: doc_7\ncontent: Employees requesting leave must notify their manager at least two weeks in advance." * 3,
        "Leave requests need two weeks' notice (doc_7).", "call_3",
    )

    before_tokens = count_messages_tokens(history)
    print(f"Before pruning: {len(history)} messages, {before_tokens} tokens")

    pruned = prune_old_tool_results(history, keep_last_n_tool_rounds=1)
    after_tokens = count_messages_tokens(pruned)
    print(f"After pruning:  {len(pruned)} messages, {after_tokens} tokens "
          f"({before_tokens - after_tokens} tokens saved)")

    assert len(pruned) == len(history), "pruning must never change message count"

    print("\n--- tool message contents ---")
    for m in pruned:
        if m.get("role") == "tool":
            print(f"  {m['content'][:70]!r}")

    print("\n--- verify every original tool_call_id still has a matching tool message ---")
    call_ids = {tc["id"] for m in pruned if m.get("tool_calls") for tc in m["tool_calls"]}
    tool_msg_ids = {m["tool_call_id"] for m in pruned if m.get("role") == "tool"}
    assert call_ids == tool_msg_ids, "pruning orphaned a tool_call_id!"
    print("OK — no orphaned tool_call_ids after pruning.")
