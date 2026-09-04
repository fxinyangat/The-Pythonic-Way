# config.py — owns process-wide client construction: the sync OpenAI client
# (query rewriting) and the ragas llm/embeddings wrappers (ragas evaluation).
# Clients is built once (by main.py at startup) and passed down — no hidden
# module-level caches, no lazy init hiding a bad API key until first request.
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from ragas.embeddings import embedding_factory
from ragas.llms import llm_factory

load_dotenv()

RAGAS_LLM_MODEL = "gpt-4o-mini"
RAGAS_EMBEDDING_MODEL = "text-embedding-3-small"


def require_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return api_key


class Clients:
    def __init__(self):
        require_api_key()

        self.openai = OpenAI()

        # ragas' score() runs asyncio.run(ascore(...)) internally, which needs
        # an async client — a sync OpenAI() here raises "Cannot use
        # agenerate() with a synchronous client."
        self.ragas_llm = llm_factory(
            model=RAGAS_LLM_MODEL, provider="openai", client=AsyncOpenAI()
        )
        self.ragas_embeddings = embedding_factory(
            provider="openai", model=RAGAS_EMBEDDING_MODEL, client=AsyncOpenAI()
        )
