"""
Embed a query string into a dense vector using BGE-M3 via LM Studio.
Single responsibility: text → vector. Cached to avoid redundant API calls.
"""

import functools
import requests

from config import EMBEDDING_URL, EMBEDDING_MODEL


@functools.lru_cache(maxsize=256)
def embed_query(query: str) -> tuple[float, ...]:
    """Convert a text query into a 1024-dimensional embedding vector.
    
    Returns tuple (hashable) for LRU cache compatibility.
    """
    response = requests.post(
        EMBEDDING_URL,
        json={"model": EMBEDDING_MODEL, "input": query[:8000]},
        timeout=30,
    )
    response.raise_for_status()
    return tuple(response.json()["data"][0]["embedding"])
