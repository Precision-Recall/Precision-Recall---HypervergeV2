"""
Section full fetcher — scrolls ALL chunks for a given company+year+section.
Single responsibility: exhaustive section retrieval without vector similarity.
"""

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue

from retriever.client import scroll_chunks
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def section_full_fetcher(company: str, year: int, section: str) -> list[dict]:
    """Scroll ALL chunks for a given company + year + section from Qdrant.

    Returns complete section content in page order. Use when you need the
    ENTIRE content of a specific section, not just the most relevant parts.

    Args:
        company: company name (e.g., '3M', 'ACTIVISIONBLIZZARD').
        year: filing year (e.g., 2018).
        section: section name (e.g., 'Business', 'MD&A', 'Risk Factors').

    Returns:
        All chunks for that section in page order.
    """
    must_filters = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="year", match=MatchValue(value=year)),
        FieldCondition(key="section", match=MatchValue(value=section)),
    ]

    chunks = scroll_chunks(must_filters=must_filters, limit=100)

    # Sort by page for reading order
    chunks.sort(key=lambda c: c["payload"].get("page", 0))
    return [c["payload"] for c in chunks]
