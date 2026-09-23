# tools/web_tools.py
#
# A second, deliberately unrelated capability:
#   knowledge_base_search = internal company policy corpus
#   web_search            = general/external world knowledge (stub for now)
#
# WORTH NOTICING vs rag_tools.py: this tool has no injected dependencies (no
# VectorStore, no Clients), so it's decorated directly at module level — no
# factory/closure needed. `@tool` fires the moment this module is imported,
# and `web_search` is in TOOL_REGISTRY from then on. rag_tools.py needed the
# register_rag_tools(store, reranker, clients) factory ONLY because that tool
# has real dependencies to bind; that's the one and only reason for the extra
# indirection there. Same registry, same decorator, two different shapes
# depending on what each tool actually needs.
#
# This is a STUB per the original architecture doc ("web_tools.py # websearch
# stub") — no real search API wired in. The point right now is to prove
# multi-tool selection works with two real, distinct capabilities, not to
# build a web search integration.
from pydantic import BaseModel, Field

from tools.registry import tool


class WebSearchParams(BaseModel):
    query: str = Field(
        description="A web search query for general/current information not "
        "found in internal company documents (news, public facts, etc.)."
    )


@tool(
    name="web_search",
    description=(
        "Search the public web for general or current information — anything "
        "NOT related to this company's internal policies (use "
        "knowledge_base_search for those instead). Currently a stub: it does "
        "not perform a real search yet."
    ),
    parameters=WebSearchParams,
    category="web",
)
def web_search(query: str) -> str:
    return f"[STUB] Web search is not implemented yet. If it were, this would search the public web for: {query!r}"
