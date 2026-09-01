import argparse
import json
from typing import Any, cast

try:
    from .evaluator import evaluate_pipeline
    from .generator import DEFAULT_GENERATION_MODEL, generate_answer
    from .reranker import rerank_chunks
    from .retriever import retrieve
except ImportError:
    from .evaluator import evaluate_pipeline
    from generator import DEFAULT_GENERATION_MODEL, generate_answer
    from reranker import rerank_chunks
    from retriever import retrieve


DEFAULT_RETRIEVE_K = 10
DEFAULT_TOP_N = 3


def run_pipeline(
    query: str,
    retrieve_k: int = DEFAULT_RETRIEVE_K,
    top_n: int = DEFAULT_TOP_N,
    model: str = DEFAULT_GENERATION_MODEL,
) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query must not be empty.")

    if retrieve_k <= 0:
        raise ValueError("retrieve_k must be greater than 0.")

    if top_n <= 0:
        raise ValueError("top_n must be greater than 0.")

    retrieved_docs = retrieve(query=query, k=retrieve_k)
    reranked_docs = cast(
        list[dict[str, Any]],
        rerank_chunks(
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

    return {
        "answer": answer,
        "retrieval_stage": {
            "query": query,
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
    return parser


def format_pipeline_output(result: dict[str, Any]) -> str:
    answer = result["answer"]
    retrieval_stage = json.dumps(result["retrieval_stage"], indent=2)

    return f"Answer:\n{answer}\n\nRetrieval stage:\n{retrieval_stage}"


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    result = run_pipeline(
        query=args.query,
        retrieve_k=args.retrieve_k,
        top_n=args.top_n,
        model=args.model,
    )
    print(format_pipeline_output(result))


if __name__ == "__main__":
    main()
