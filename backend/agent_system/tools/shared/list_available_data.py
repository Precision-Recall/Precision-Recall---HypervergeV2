"""
List available data — discovers what companies/years exist in the vector store.
"""

from langchain.tools import tool
from qdrant_client.models import Filter

from retriever.client import get_qdrant, get_collection
from tools.call_limiter import max_calls


@tool
@max_calls(2)
def list_available_data() -> dict:
    """Discover what companies and years are available in the vector store.

    Returns a dict of {company: [years]} showing all indexed data.
    Use this first when you're unsure what data exists.
    """
    client = get_qdrant()
    collection = get_collection()

    # Scroll a sample to discover companies and years
    all_chunks, _ = client.scroll(
        collection_name=collection,
        limit=1000,
        with_payload=True,
    )

    data = {}
    for point in all_chunks:
        company = point.payload.get("company")
        year = point.payload.get("year")
        if company and year:
            if company not in data:
                data[company] = set()
            data[company].add(year)

    return {k: sorted(v) for k, v in sorted(data.items())}
