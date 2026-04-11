"""
Chunk bundler — fetches linked chunks via prev/next chain references.
Single responsibility: given a chunk ID, walk the linked list and return neighbors.
"""

from langchain.tools import tool

from retriever.client import get_qdrant, get_collection
from tools.call_limiter import max_calls


def _fetch_chunk_by_id(chunk_id: str) -> dict | None:
    """Retrieve a single chunk by its ID from Qdrant."""
    client = get_qdrant()
    collection = get_collection()
    try:
        results = client.retrieve(
            collection_name=collection,
            ids=[chunk_id],
            with_payload=True,
        )
        if results:
            point = results[0]
            return {"id": str(point.id), "payload": point.payload}
    except Exception:
        pass
    return None


def _walk_chain(start_id: str, direction: str, depth: int) -> list[dict]:
    """Walk the chunk chain in a given direction up to depth hops."""
    key = "next_chunk_id" if direction == "next" else "prev_chunk_id"
    chain = []
    current_id = start_id

    for _ in range(depth):
        chunk = _fetch_chunk_by_id(current_id)
        if chunk is None:
            break
        next_id = chunk["payload"].get(key)
        if next_id is None:
            break
        linked = _fetch_chunk_by_id(next_id)
        if linked is None:
            break
        chain.append(linked)
        current_id = next_id

    return chain


@tool
@max_calls(5)
def chunk_bundler(chunk_id: str, direction: str = "both", depth: int = 2) -> list[dict]:
    """Fetch linked chunks via prev_chunk_id / next_chunk_id references.

    Walks the chunk chain up to `depth` hops in the specified direction.

    Args:
        chunk_id: the starting chunk ID.
        direction: 'prev', 'next', or 'both'.
        depth: how many hops to walk in each direction.

    Returns:
        List of neighboring chunk payloads in reading order.
    """
    center = _fetch_chunk_by_id(chunk_id)
    if center is None:
        return []

    result = []

    if direction in ("prev", "both"):
        prev_chunks = _walk_chain(chunk_id, "prev", depth)
        result.extend(reversed(prev_chunks))

    result.append(center)

    if direction in ("next", "both"):
        next_chunks = _walk_chain(chunk_id, "next", depth)
        result.extend(next_chunks)

    return [c["payload"] for c in result]
