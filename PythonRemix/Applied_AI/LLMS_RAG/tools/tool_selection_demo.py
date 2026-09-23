# tools/tool_selection_demo.py
#
# AGENTIC CONCEPT #7 — how the model actually "picks" a tool.
# You send ONE chat completion request with the normal messages PLUS
# `tools=get_schemas(...)`. The model reads every tool's name/description/
# parameter descriptions (that's ALL it has to go on — not your source code)
# and its response comes back one of two shapes:
#   - message.content is set, message.tool_calls is None -> plain text answer,
#     the model decided no tool was needed.
#   - message.tool_calls is a LIST of {id, function: {name, arguments}} ->
#     the model wants one or more tools run. It's a list because a model can
#     request several tools in one turn (parallel tool calls) — e.g. a
#     compound question touching both the internal KB and the web.
# This script makes that one request for a few different queries and prints
# exactly what came back, then runs whatever was requested through
# execute_tool. It stops there — it does NOT feed results back for a second
# "write the final answer" turn. That loop (call -> execute -> feed back ->
# call again) is orchestrator.py, the next phase.
import json

from rag.config import Clients
from rag.reranker import CrossEncoderReranker
from rag.vector_store import VectorStore
from tools.rag_tools import register_rag_tools
from tools.registry import execute_tool, get_schemas

# Importing web_tools is enough to register web_search (module-level @tool).
# rag_tools's tool needs register_rag_tools(...) called explicitly below,
# because it needs store/reranker/clients that only exist at runtime.
import tools.web_tools  # noqa: F401


SYSTEM_PROMPT = (
    "You are a company assistant. You have tools available — use them "
    "whenever they'd help answer the question, and don't guess at facts you "
    "could look up. If no tool is relevant, just answer directly."
)

TEST_QUERIES = [
    "What is our policy on remote work time logging?",
    "Who won the most recent Super Bowl?",
    "Hi, how are you today?",
    "What's our leave notice policy, and who is the CEO of OpenAI?",
]


def run_query(clients: Clients, query: str) -> None:
    print(f"\n{'=' * 70}\nUSER: {query}")

    response = clients.openai.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        tools=get_schemas(["rag", "web"]),
        # "auto" (the default) lets the model choose freely: no tool, one
        # tool, or several. The alternatives are "required" (must call
        # something) and naming one tool directly (force that specific call)
        # — spelled out here since this is exactly the knob orchestrator.py
        # will need to reason about later.
        tool_choice="auto",
    )
    message = response.choices[0].message

    if not message.tool_calls:
        print(f"MODEL (no tool call): {message.content}")
        return

    print(f"MODEL requested {len(message.tool_calls)} tool call(s):")
    for call in message.tool_calls:
        arguments = json.loads(call.function.arguments)
        print(f"  -> {call.function.name}({arguments})")

        result = execute_tool(call.function.name, arguments)
        preview = result if len(result) <= 200 else result[:200] + "..."
        print(f"     result: {preview}")


if __name__ == "__main__":
    store = VectorStore()
    reranker = CrossEncoderReranker()
    clients = Clients()
    register_rag_tools(store, reranker, clients)

    print("Registered tools:", [s["function"]["name"] for s in get_schemas()])

    for query in TEST_QUERIES:
        run_query(clients, query)
