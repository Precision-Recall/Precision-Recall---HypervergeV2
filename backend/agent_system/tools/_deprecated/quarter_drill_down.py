"""
Quarter drill down — retrieves quarterly (10-Q) data for a specific quarter.
Single responsibility: company + year + quarter + query → quarterly chunks.
"""

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue

from retriever.client import search_chunks
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def quarter_drill_down(
    company: str,
    year: int,
    quarter: int,
    query: str,
) -> list[dict]:
    """Drill into quarterly (10-Q) data for a specific company/year/quarter.

    Uses form_type='10-Q' + quarter filter for intra-year granularity.

    Args:
        company: company name (e.g., '3M').
        year: filing year (e.g., 2023).
        quarter: quarter number (1, 2, 3, or 4).
        query: the metric or topic to search for.

    Returns:
        List of matching chunks from the quarterly filing.
    """
    must_filters = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="year", match=MatchValue(value=year)),
        FieldCondition(key="quarter", match=MatchValue(value=quarter)),
        FieldCondition(key="form_type", match=MatchValue(value="10-Q")),
    ]

    results = search_chunks(query, must_filters=must_filters, limit=10)
    return [r["payload"] for r in results]
