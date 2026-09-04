# query_rewriter.py — rewrites a raw user query into a retrieval-optimized version
# (expands vague/acronym-heavy phrasing into more specific, keyword-rich language
# for embedding search). Single job, composable: this does NOT call retrieve()
# itself — main.py/orchestrator decides whether to rewrite before retrieval.
# Must never be a hard dependency: any failure falls back to the original query.
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_REWRITE_MODEL = 'gpt-4o-mini'
# gpt-4o-mini, gpt-5.4-mini

_SYSTEM_PROMPT = (
    "You rewrite user questions into a single, retrieval-optimized search query "
    "for a semantic vector search system. Expand vague phrasing and acronyms, "
    "keep it concise and keyword-rich, and preserve the original intent. Do not "
    "answer the question. Return only the rewritten query, nothing else. Make sure the re-written query has a question in it, not a statement(s)"
)


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    return OpenAI()


def rewrite_query(query: str, model: str = DEFAULT_REWRITE_MODEL) -> str:
    query = query.strip()
    if not query or not os.getenv("OPENAI_API_KEY"):
        return query

    try:
        response = _client().chat.completions.create(
            model=model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
        )
        rewritten = (response.choices[0].message.content or "").strip()
    except Exception:
        # Rewriting is an optimization, not a requirement — any failure
        # (network, auth, rate limit, malformed response) degrades to the
        # original query rather than breaking the pipeline.
        return query

    return rewritten or query


if __name__ == "__main__":
    print(rewrite_query(" I hate working in office.this illegal, how to wfh time log rules"))
