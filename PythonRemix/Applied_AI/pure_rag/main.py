# main.py — CLI entrypoint wiring the whole pipeline together:
# rewrite -> retrieve -> rerank -> generate -> evaluate_pipeline (always on) and
# evaluate_ragas_pipeline (opt-in via --ragas, costs extra LLM calls per run).
# Run as: python3 -m rag.main "<query>"
import argparse
import json
from typing import Any, cast

try:
    from .config import Clients
    from .evaluator import evaluate_pipeline, evaluate_ragas_pipeline
    from .generator import DEFAULT_GENERATION_MODEL, generate_answer
    from .query_rewriter import rewrite_query
    from .reranker import CrossEncoderReranker, rerank_chunks
    from .retriever import retrieve
    from .vector_store import VectorStore
except ImportError:
    from config import Clients
    from evaluator import evaluate_pipeline, evaluate_ragas_pipeline
    from generator import DEFAULT_GENERATION_MODEL, generate_answer
    from query_rewriter import rewrite_query
    from reranker import CrossEncoderReranker, rerank_chunks
    from retriever import retrieve
    from vector_store import VectorStore


DEFAULT_RETRIEVE_K = 10
DEFAULT_TOP_N = 3


def run_pipeline(
    reranker: CrossEncoderReranker,
    store: VectorStore,
    clients: Clients,
    query: str,
    retrieve_k: int = DEFAULT_RETRIEVE_K,
    top_n: int = DEFAULT_TOP_N,
    model: str = DEFAULT_GENERATION_MODEL,
    use_ragas: bool = False,
    ground_truth: str | None = None,
) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query must not be empty.")

    if retrieve_k <= 0:
        raise ValueError("retrieve_k must be greater than 0.")

    if top_n <= 0:
        raise ValueError("top_n must be greater than 0.")

    # Rewrite only steers retrieval (matching corpus phrasing). Reranking and
    # generation stay anchored to the original query — that's the actual
    # question the answer has to address, not the retrieval-optimized version.
    rewritten_query = rewrite_query(clients.openai, query, model=model)
    retrieved_docs = retrieve(store=store, query=rewritten_query, k=retrieve_k)
    reranked_docs = cast(
        list[dict[str, Any]],
        rerank_chunks(
            reranker=reranker,
            query=query,
            docs=retrieved_docs,
            top_n=top_n,
        ),
    )
    answer = generate_answer(
        query=query,
        docs=reranked_docs,
        model=model,
    )
    evaluation = evaluate_pipeline(
        retrieved_docs=retrieved_docs,
        reranked_docs=reranked_docs,
        answer=answer,
    )
    if use_ragas:
        evaluation["ragas"] = evaluate_ragas_pipeline(
            llm=clients.ragas_llm,
            embeddings=clients.ragas_embeddings,
            query=query,
            answer=answer,
            docs=reranked_docs,
            ground_truth=ground_truth,
        )

    return {
        "answer": answer,
        "retrieval_stage": {
            "query": query,
            "rewritten_query": rewritten_query,
            "retrieve_k": retrieve_k,
            "top_n": top_n,
            "retrieved_docs": retrieved_docs,
            "reranked_docs": reranked_docs,
            "evaluation": evaluation,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the RAG retrieve + rerank pipeline.")
    parser.add_argument("query", help="Question to search for in the vector store.")
    parser.add_argument(
        "--retrieve-k",
        type=int,
        default=DEFAULT_RETRIEVE_K,
        help=f"Number of initial documents to retrieve. Default: {DEFAULT_RETRIEVE_K}.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Number of reranked documents to return. Default: {DEFAULT_TOP_N}.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_GENERATION_MODEL,
        help=f"OpenAI model to use for generation. Default: {DEFAULT_GENERATION_MODEL}.",
    )
    parser.add_argument(
        "--ragas",
        action="store_true",
        help="Also compute ragas metrics (faithfulness, answer_relevancy, "
        "context_relevance). Costs extra LLM calls per run.",
    )
    parser.add_argument(
        "--ground-truth",
        default=None,
        help="Reference answer for ragas context_precision/context_recall "
        "(only used with --ragas).",
    )
    return parser


def format_pipeline_output(result: dict[str, Any]) -> str:
    answer = result["answer"]
    retrieval_stage = json.dumps(result["retrieval_stage"], indent=2)

    return f"Answer:\n{answer}\n\nRetrieval stage:\n{retrieval_stage}"


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    reranker = CrossEncoderReranker()
    store = VectorStore()
    clients = Clients()
    result = run_pipeline(
        reranker=reranker,
        store=store,
        clients=clients,
        query=args.query,
        retrieve_k=args.retrieve_k,
        top_n=args.top_n,
        model=args.model,
        use_ragas=args.ragas,
        ground_truth=args.ground_truth,
    )
    print(format_pipeline_output(result))


if __name__ == "__main__":
    main()
