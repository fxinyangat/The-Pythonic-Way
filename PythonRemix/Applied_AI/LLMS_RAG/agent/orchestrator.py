# agent/orchestrator.py
#
# AGENTIC CONCEPT #8 — the loop, not the two calls.
# tool_selection_demo.py made exactly ONE request and stopped after executing
# whatever tools the model asked for — it never told the model what the tools
# returned. That's not enough to get an answer: the model that decided to
# call knowledge_base_search never actually SEES the policy text unless you
# send it back. And "one round of tools, then one final answer" is only the
# simplest case — a model can look at a tool result and decide it needs to
# call another tool (e.g. the KB result was empty, so it tries web_search
# instead). The real shape is a LOOP:
#
#   while True:
#       call the model with the conversation so far
#       if it returned plain text -> that's the final answer, stop
#       if it returned tool_calls -> run each one, append the results as
#           "tool" messages, and go around again so the model can see them
#
# This file is that loop. Nothing about it is RAG-specific — it only knows
# about "messages" and "tools", which is exactly why registry.py/rag_tools.py
# were built generic in the first place: this loop works for ANY tool
# registered into TOOL_REGISTRY, RAG or otherwise.
import json
from typing import Any

from rag.config import Clients
from tools.registry import execute_tool, get_schemas

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TURNS = 5

SYSTEM_PROMPT = (
    "You are a company assistant. You have tools available — use them "
    "whenever they would help answer the question, and don't guess at facts "
    "you could look up. When you answer from a knowledge_base_search result, "
    "cite the document id(s) you used. If no tool is relevant, just answer "
    "directly."
)


class Orchestrator:
    def __init__(
        self,
        clients: Clients,
        tool_categories: list[str] | None = None,
        model: str = DEFAULT_MODEL,
        max_turns: int = DEFAULT_MAX_TURNS,
    ):
        self.clients = clients
        self.tool_categories = tool_categories
        self.model = model
        self.max_turns = max_turns

    def run(self, query: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        # `history` is prior conversation turns (already windowed/pruned by
        # the CALLER — see agent/chat_session.py). Orchestrator stays
        # storage-agnostic on purpose: it has no idea a conversation_id or a
        # ConversationStore exists, it just appends whatever history it's
        # handed after the system prompt and before the new query.
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *(history or []),
            {"role": "user", "content": query},
        ]
        tool_schemas = get_schemas(self.tool_categories)

        # AGENTIC CONCEPT #9 — why a turn limit is not optional.
        # Nothing structurally stops a model from calling a tool, seeing the
        # result, and deciding to call another tool forever — a bad or
        # confusing tool result is enough to trigger this. Every loop that
        # lets a model decide when to stop needs an outside cap, or one
        # unlucky run turns into unbounded cost and latency. This is a real
        # production safety property, not a style choice.
        for turn in range(self.max_turns):
            response = self.clients.openai.chat.completions.create(
                model=self.model,
                temperature=0.0,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            message = response.choices[0].message

            # AGENTIC CONCEPT #10 — the assistant's tool-call message must be
            # replayed back verbatim before any "tool" result message. The
            # API's contract requires this exact order (assistant message
            # that requested tool X, then a tool message answering call X's
            # id) — send them out of order or omit the assistant message and
            # the next request is rejected. So we always append what the
            # model actually said, whether that's final text or tool_calls.
            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in message.tool_calls
                    ]
                    if message.tool_calls
                    else None,
                }
            )

            if not message.tool_calls:
                return {
                    "answer": message.content,
                    "turns_used": turn + 1,
                    "messages": messages,
                }

            for call in message.tool_calls:
                arguments = json.loads(call.function.arguments)
                result = execute_tool(call.function.name, arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    }
                )

        # Turn limit hit without a final text answer. Returning a clear
        # failure string here matters for the same reason execute_tool never
        # raises: whatever calls .run() (a CLI, an API route) needs SOMETHING
        # usable back, not an exception from hitting an internal safety cap.
        return {
            "answer": (
                "I wasn't able to reach a final answer within "
                f"{self.max_turns} tool-calling turns."
            ),
            "turns_used": self.max_turns,
            "messages": messages,
        }


if __name__ == "__main__":
    from rag.reranker import CrossEncoderReranker
    from rag.vector_store import VectorStore
    from tools.rag_tools import register_rag_tools
    import tools.web_tools  # noqa: F401 — registers web_search on import

    store = VectorStore()
    reranker = CrossEncoderReranker()
    clients = Clients()
    register_rag_tools(store, reranker, clients)

    orchestrator = Orchestrator(clients, tool_categories=["rag", "web"])

    test_queries = [
        "What is our policy on remote work time logging?",
        "Hi, how are you today?",
        "What's our leave notice policy, and who is the CEO of OpenAI?",
    ]

    for query in test_queries:
        print(f"\n{'=' * 70}\nUSER: {query}")
        result = orchestrator.run(query)
        print(f"ANSWER ({result['turns_used']} turn(s)): {result['answer']}")
