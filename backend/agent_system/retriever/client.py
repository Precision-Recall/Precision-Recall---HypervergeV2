"""
Shared Qdrant client + embedding helper.
Single responsibility: provide direct access to Qdrant and embedding for tools
that need surgical control over their retrieval strategy.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION
from retriever.embedding import embed_query


_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    """Lazy singleton Qdrant client."""
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def get_collection() -> str:
    """Return the active collection name."""
    return QDRANT_COLLECTION


def search_chunks(
    query: str,
    must_filters: list,
    limit: int = 20,
) -> list[dict]:
    """Direct Qdrant query_points with pre-built filters.

    Bypasses the full retrieve() pipeline (no forced reranking).
    Returns list of dicts with id, score, payload.
    """
    client = get_qdrant()
    query_vector = embed_query(query)

    response = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=list(query_vector),
        query_filter=Filter(must=must_filters) if must_filters else None,
        limit=limit,
        with_payload=True,
    )

    return [
        {
            "id": str(point.id),
            "score": point.score,
            "payload": point.payload,
        }
        for point in response.points
    ]


def scroll_chunks(
    must_filters: list,
    limit: int = 100,
) -> list[dict]:
    """Exhaustive scroll through ALL matching chunks (no vector similarity).

    Use for cases where you need COMPLETE section content,
    not just the most semantically relevant chunks.
    """
    client = get_qdrant()
    all_chunks = []
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            scroll_filter=Filter(must=must_filters) if must_filters else None,
            limit=limit,
            offset=offset,
            with_payload=True,
        )

        for point in results:
            all_chunks.append({
                "id": str(point.id),
                "payload": point.payload,
            })

        if next_offset is None:
            break
        offset = next_offset

    return all_chunks
