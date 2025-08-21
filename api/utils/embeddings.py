import os
from typing import List

# Optional OpenAI embeddings; gracefully degrade if not configured
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if OpenAI is None:
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    _client = OpenAI(api_key=api_key)
    return _client


def vector_search_enabled() -> bool:
    return _get_client() is not None and bool(os.getenv("ENABLE_VECTOR_SEARCH", "true").lower() == "true")


def get_query_embedding(text: str) -> List[float]:
    client = _get_client()
    if client is None:
        raise RuntimeError("Embeddings not configured")
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    res = client.embeddings.create(model=model, input=text)
    return res.data[0].embedding  # type: ignore
