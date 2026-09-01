import argparse
import json
from typing import Any

try:
    from .reranker import retrieve_and_rerank
except ImportError:
    from reranker import retrieve_and_rerank


DEFAULT_RETRIEVE_K = 10
DEFAULT_TOP_N = 3


def run_pipeline(
    query: str,
    retrieve_k: int = DEFAULT_RETRIEVE_K,
    top_n: int = DEFAULT_TOP_N,
) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("query must not be empty.")

    if retrieve_k <= 0:
        raise ValueError("retrieve_k must be greater than 0.")

    if top_n <= 0:
        raise ValueError("top_n must be greater than 0.")

    return retrieve_and_rerank(
        query=query,
        retrieve_k=retrieve_k,
        top_n=top_n,
    )


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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    results = run_pipeline(
        query=args.query,
        retrieve_k=args.retrieve_k,
        top_n=args.top_n,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
