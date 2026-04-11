"""
Qdrant vector store operations with deduplication.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, EMBEDDING_DIM


def get_client() -> QdrantClient:
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def ensure_collection(client: QdrantClient):
    """Create collection if it doesn't exist."""
    collections = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
        # Create payload indexes for filtering
        for field in ["company", "year", "section_item", "form_type", "type"]:
            client.create_payload_index(QDRANT_COLLECTION, field, field_schema="keyword")
        print(f"Created collection: {QDRANT_COLLECTION}")


def get_existing_ids(client: QdrantClient, ids: list[str]) -> set:
    """Check which IDs already exist in the collection."""
    existing = set()
    # Scroll with ID filter in batches
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        results = client.retrieve(QDRANT_COLLECTION, ids=batch, with_payload=False, with_vectors=False)
        existing.update(p.id for p in results)
    return existing


def upsert_chunks(client: QdrantClient, chunks: list[dict], vectors: list[list[float]]):
    """Insert chunks into Qdrant, skipping duplicates."""
    ids = [c["id"] for c in chunks]
    existing = get_existing_ids(client, ids)

    points = []
    for chunk, vector in zip(chunks, vectors):
        if chunk["id"] in existing:
            continue
        points.append(PointStruct(
            id=chunk["id"],
            vector=vector,
            payload=chunk["payload"],
        ))

    if points:
        # Batch upsert in groups of 100
        for i in range(0, len(points), 100):
            client.upsert(QDRANT_COLLECTION, points=points[i:i + 100])

    return len(points), len(existing & set(ids))
