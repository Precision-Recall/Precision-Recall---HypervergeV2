"""
Shared Qdrant client + embedding for the forensic engine.
Mirrors agent_system/retriever/client.py but uses local config.
"""

import functools
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, Range

from config import (
    QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION,
    EMBEDDING_URL, EMBEDDING_MODEL,
)

_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


@functools.lru_cache(maxsize=256)
def embed_query(query: str) -> tuple[float, ...]:
    """Text → 1024-dim BGE-M3 embedding vector."""
    resp = requests.post(
        EMBEDDING_URL,
        json={"model": EMBEDDING_MODEL, "input": query[:8000]},
        timeout=30,
    )
    resp.raise_for_status()
    return tuple(resp.json()["data"][0]["embedding"])


def search_sections(
    query: str,
    company: str,
    section_items: list[str],
    year: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    limit: int = 10,
) -> list[dict]:
    """Semantic search within specific 10-K sections.

    Uses Qdrant payload filtering BEFORE vector search.
    section_items use the actual payload format: "Item 7", "Item 1A", etc.
    Returns deduplicated results sorted by score.
    """
    must = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="section_item", match=MatchAny(any=section_items)),
    ]
    if year is not None:
        must.append(FieldCondition(key="year", match=MatchValue(value=year)))
    if start_year is not None or end_year is not None:
        rng = {}
        if start_year is not None:
            rng["gte"] = start_year
        if end_year is not None:
            rng["lte"] = end_year
        must.append(FieldCondition(key="year", range=Range(**rng)))

    vec = list(embed_query(query))
    response = get_qdrant().query_points(
        collection_name=QDRANT_COLLECTION,
        query=vec,
        query_filter=Filter(must=must),
        limit=limit,
        with_payload=True,
    )

    # Deduplicate by point ID
    seen = set()
    results = []
    for pt in response.points:
        if pt.id not in seen:
            seen.add(pt.id)
            results.append({"id": str(pt.id), "score": pt.score, "payload": pt.payload})
    return results


def scroll_section(
    company: str,
    section_item: str,
    year: int,
) -> str:
    """Exhaustively retrieve ALL text from a section. Returns concatenated text."""
    must = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="section_item", match=MatchValue(value=section_item)),
        FieldCondition(key="year", match=MatchValue(value=year)),
        FieldCondition(key="type", match=MatchValue(value="text")),
    ]

    client = get_qdrant()
    all_chunks = []
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=Filter(must=must),
            limit=100,
            offset=offset,
            with_payload=True,
        )
        all_chunks.extend(results)
        if next_offset is None:
            break
        offset = next_offset

    # Sort by page for reading order
    all_chunks.sort(key=lambda c: c.payload.get("page", 0))
    return " ".join(c.payload.get("text", "") for c in all_chunks if c.payload.get("text"))
