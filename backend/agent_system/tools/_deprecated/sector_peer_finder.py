"""
Sector peer finder — discovers which companies in the dataset are peers.
Uses VECTOR SIMILARITY on business overview embeddings, not LLM analysis.

KEY FIX: Pure vector-native approach. Gets target company's business overview
embedding, then searches for similar embeddings from OTHER companies using
must_not filter. Zero LLM calls needed.

Single responsibility: given a company → find its peers in the dataset.
"""

from langchain.tools import tool
from qdrant_client.models import Filter, FieldCondition, MatchValue

from retriever.client import get_qdrant, get_collection, search_chunks
from retriever.embedding import embed_query
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def sector_peer_finder(company: str) -> list[str]:
    """Discover peer companies using vector similarity on business descriptions.

    1. Gets target company's Business section embedding.
    2. Searches for similar business descriptions from OTHER companies
       using must_not filter to exclude the target.
    3. Deduplicates by company name.

    No LLM calls — pure vector similarity. Fast and accurate.

    Args:
        company: the target company name (e.g., '3M').

    Returns:
        List of peer company names (up to 5), ordered by similarity.
    """
    client = get_qdrant()
    collection = get_collection()

    # Step 1: Get the target company's business overview embedding
    anchor_results = search_chunks(
        query=f"{company} business overview products services",
        must_filters=[
            FieldCondition(key="company", match=MatchValue(value=company)),
            FieldCondition(key="section", match=MatchValue(value="Business")),
        ],
        limit=1,
    )

    if not anchor_results:
        return []

    # Step 2: Get the anchor's vector
    anchor_id = anchor_results[0]["id"]
    anchor_points = client.retrieve(
        collection_name=collection,
        ids=[anchor_id],
        with_vectors=True,
    )

    if not anchor_points or not anchor_points[0].vector:
        # Fallback: use the query embedding directly
        anchor_vector = embed_query(
            f"{company} business overview products services"
        )
    else:
        anchor_vector = anchor_points[0].vector

    # Step 3: Search for similar business descriptions from OTHER companies
    peers_response = client.query_points(
        collection_name=collection,
        query=list(anchor_vector) if isinstance(anchor_vector, tuple) else anchor_vector,
        query_filter=Filter(
            must=[
                FieldCondition(key="section", match=MatchValue(value="Business")),
            ],
            must_not=[
                FieldCondition(key="company", match=MatchValue(value=company)),
            ],
        ),
        limit=10,
        with_payload=True,
    )

    # Step 4: Deduplicate by company name
    seen = set()
    peer_companies = []
    for point in peers_response.points:
        c = point.payload.get("company")
        if c and c not in seen:
            seen.add(c)
            peer_companies.append(c)

    return peer_companies[:5]
