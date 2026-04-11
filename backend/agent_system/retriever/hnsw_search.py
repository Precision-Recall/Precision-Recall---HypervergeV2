"""
HNSW approximate nearest-neighbor search on Qdrant.
Single responsibility: vector + filters → ranked candidate chunks.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, TOP_K_HNSW


_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    """Lazy singleton Qdrant client."""
    global _client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _client


def _build_filter(filters: dict) -> Filter | None:
    """Convert a flat filter dict into a Qdrant Filter object.

    Supported keys:
        company     → exact match
        year        → exact match (int)
        start_year  → range gte
        end_year    → range lte
        section     → exact match
        section_item→ exact match
        form_type   → exact match
        type        → exact match (text/table/figure)
        quarter     → exact match (int)
    """
    conditions = []

    if "company" in filters:
        conditions.append(
            FieldCondition(key="company", match=MatchValue(value=filters["company"]))
        )

    if "year" in filters:
        conditions.append(
            FieldCondition(key="year", match=MatchValue(value=filters["year"]))
        )

    if "start_year" in filters or "end_year" in filters:
        range_kwargs = {}
        if "start_year" in filters:
            range_kwargs["gte"] = filters["start_year"]
        if "end_year" in filters:
            range_kwargs["lte"] = filters["end_year"]
        conditions.append(FieldCondition(key="year", range=Range(**range_kwargs)))

    if "section" in filters:
        conditions.append(
            FieldCondition(key="section", match=MatchValue(value=filters["section"]))
        )

    if "section_item" in filters:
        conditions.append(
            FieldCondition(
                key="section_item", match=MatchValue(value=filters["section_item"])
            )
        )

    if "form_type" in filters:
        conditions.append(
            FieldCondition(
                key="form_type", match=MatchValue(value=filters["form_type"])
            )
        )

    if "type" in filters:
        conditions.append(
            FieldCondition(key="type", match=MatchValue(value=filters["type"]))
        )

    if "quarter" in filters:
        conditions.append(
            FieldCondition(key="quarter", match=MatchValue(value=filters["quarter"]))
        )

    if not conditions:
        return None
    return Filter(must=conditions)


def vector_search(
    query_vector: list[float],
    filters: dict | None = None,
    top_k: int = TOP_K_HNSW,
) -> list[dict]:
    """Run HNSW search on Qdrant and return top-k candidate chunks.

    Returns a list of dicts with keys: id, score, payload.
    """
    client = _get_client()
    qdrant_filter = _build_filter(filters) if filters else None

    response = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=list(query_vector),
        query_filter=qdrant_filter,
        limit=top_k,
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
