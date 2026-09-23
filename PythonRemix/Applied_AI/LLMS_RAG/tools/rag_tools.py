# tools/rag_tools.py
#
# Registers the RAG pipeline into tools/registry.py as ONE tool:
# `knowledge_base_search`. Internally: rewrite -> retrieve -> rerank ->
# assemble context. Externally: "give me a query, get back relevant policy
# text". Generation is NOT here — the agent's own next turn writes the answer
# from the text this tool returns (see orchestrator.py, later).
from typing import Any, cast

from pydantic import BaseModel, Field

from rag.config import Clients
from rag.context_assembler import build_context
from rag.query_rewriter import DEFAULT_REWRITE_MODEL, rewrite_query
from rag.reranker import CrossEncoderReranker, rerank_chunks
from rag.retriever import retrieve
from rag.vector_store import VectorStore
from tools.registry import tool


class KnowledgeBaseSearchParams(BaseModel):
    # AGENTIC CONCEPT #4 — descriptions are prompts.
    # Field(description=...) ends up inside the JSON schema the model reads.
    # The model has NO other information about this tool: no source code, no
    # idea what the corpus contains. The tool description + field descriptions
    # are the *only* thing it uses to decide (a) whether to call the tool and
    # (b) what to put in each argument. Vague descriptions -> wrong or missing
    # tool calls, no matter how good the code behind them is.
    query: str = Field(
        description=(
            "A focused, self-contained search query with the key terms "
            "(policy topic, employee type, etc.). It must make sense on its "
            "own: this tool cannot see the conversation, so resolve pronouns "
            "like 'it' or 'that policy' before searching."
        )
    )


def register_rag_tools(
    store: VectorStore,
    reranker: CrossEncoderReranker,
    clients: Clients,
    retrieve_k: int = 10,
    top_n: int = 3,
    use_rewriter: bool = True,
    rewrite_model: str = DEFAULT_REWRITE_MODEL,
) -> None:
    # AGENTIC CONCEPT #5 — binding dependencies with a closure.
    # execute_tool() calls tool functions as func(**arguments_from_the_llm) —
    # the model's arguments and nothing else. But the search needs a
    # VectorStore, a reranker and API clients that we built once at startup.
    # We can't ask the model to pass those (it can't produce a Python object),
    # and we don't want registry.py to know they exist. So we define the tool
    # function *inside* this factory: it "closes over" store/reranker/clients
    # and carries them along. registry.py stays generic; this file is the only
    # one that knows the RAG tool has dependencies.
    #
    # Note where the tuning knobs live: retrieve_k, top_n, use_rewriter are
    # parameters of THIS factory (a developer decision made at startup), not
    # of the tool schema (which the model controls). The model has no
    # principled way to pick "top_n=3 vs 7", so we don't offer it the choice.

    @tool(
        name="knowledge_base_search",
        description=(
            "Search the company's internal policy knowledge base (HR, Finance "
            "and Engineering: remote work, leave, contractor invoicing, "
            "incident reporting, etc.). Returns the most relevant policy "
            "excerpts, each with an id you can cite. Use this for any "
            "question about company policies or procedures instead of "
            "answering from memory."
        ),
        parameters=KnowledgeBaseSearchParams,
        category="rag",
    )
    def knowledge_base_search(query: str) -> str:
        # The rewriter only steers retrieval (matching the corpus's phrasing);
        # reranking stays anchored to the query as given, same as run_pipeline.
        #
        # Honest caveat: in the agentic flow the calling model has ALREADY
        # turned the user's message into a search query, which is much of what
        # the rewriter was doing. So the rewriter may now be a redundant LLM
        # call. use_rewriter lets you A/B that with your eval set instead of
        # guessing.
        search_query = (
            rewrite_query(clients.openai, query, model=rewrite_model)
            if use_rewriter
            else query
        )
        retrieved_docs = retrieve(store=store, query=search_query, k=retrieve_k)
        reranked_docs = cast(
            list[dict[str, Any]],
            rerank_chunks(
                reranker=reranker, query=query, docs=retrieved_docs, top_n=top_n
            ),
        )

        # AGENTIC CONCEPT #6 — a tool result is text written FOR the model.
        # Return the assembled context string (ids + metadata + content), not
        # Python objects: it goes back into the conversation as a message. An
        # explicit "nothing found" beats an empty string, which the model can
        # misread as a glitch.
        if not reranked_docs:
            return "No relevant documents found in the knowledge base for this query."
        return build_context(reranked_docs)


if __name__ == "__main__":
    import json

    from tools.registry import execute_tool, get_schemas

    store = VectorStore()
    reranker = CrossEncoderReranker()
    clients = Clients()
    register_rag_tools(store, reranker, clients)

    print("--- schema sent to the LLM ---")
    print(json.dumps(get_schemas(["rag"]), indent=2))

    print("\n--- query the corpus CAN answer ---")
    print(execute_tool("knowledge_base_search", {"query": "when are remote time logs due?"}))

    print("\n--- query the corpus can NOT answer ---")
    print(execute_tool("knowledge_base_search", {"query": "what is the dental insurance plan?"}))

    print("\n--- bad arguments (wrong field name) ---")
    print(execute_tool("knowledge_base_search", {"q": "remote time logs"}))
