"""
General search — unfiltered semantic search across all data.
Fallback when query lacks specific company/year context.
"""

from langchain.tools import tool

from retriever.client import search_chunks
from tools.call_limiter import max_calls


@tool
@max_calls(3)
def general_search(query: str, top_k: int = 10) -> list[dict]:
    """Search across ALL documents without any metadata filters.

    Use this as a FALLBACK when:
    - The user doesn't specify a company or year
    - Other agents couldn't find relevant data
    - The query is broad or exploratory

    Returns top-k most semantically similar chunks from the entire corpus.

    Args:
        query: the search query.
        top_k: number of results (default 10).

    Returns:
        List of chunk payloads with company, year, section, and text.
    """
    results = search_chunks(query, must_filters=[], limit=top_k)
    return [
        {
            "company": r["payload"].get("company"),
            "year": r["payload"].get("year"),
            "section": r["payload"].get("section"),
            "form_type": r["payload"].get("form_type"),
            "text": r["payload"].get("text", "")[:500],
            "score": r.get("score", 0),
        }
        for r in results
    ]
