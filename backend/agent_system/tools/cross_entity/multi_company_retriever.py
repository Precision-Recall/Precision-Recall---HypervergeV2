"""
Multi-company retriever — parallel retrieval across N companies simultaneously.
Single responsibility: query + companies + year(s) → {company: [payloads]} dict.
"""

import concurrent.futures

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue, Range

from retriever.client import search_chunks
from tools.call_limiter import max_calls


def _fetch_for_company(
    company: str,
    query: str,
    year: int | None,
    year_range: tuple | None,
    section: str | None,
) -> tuple[str, list[dict]]:
    """Retrieve chunks for a single company. Returns (company, payloads)."""
    must_filters = [
        FieldCondition(key="company", match=MatchValue(value=company)),
    ]
    if year is not None:
        must_filters.append(
            FieldCondition(key="year", match=MatchValue(value=year))
        )
    elif year_range is not None:
        must_filters.append(
            FieldCondition(key="year", range=Range(gte=year_range[0], lte=year_range[1]))
        )
    if section:
        must_filters.append(
            FieldCondition(key="section", match=MatchValue(value=section))
        )

    results = search_chunks(query, must_filters=must_filters, limit=10)
    return company, [r["payload"] for r in results]


@tool
@max_calls(5)
def multi_company_retriever(
    companies: list[str],
    query: str,
    year: int = None,
    start_year: int = None,
    end_year: int = None,
    section: str = None,
) -> dict:
    """Parallel retrieval across N companies simultaneously.

    Critical: Uses ThreadPoolExecutor for parallel Qdrant queries.
    Sequential fetching for 5 companies = 5× slower.

    Args:
        companies: list of company names (e.g., ['3M', 'ACTIVISIONBLIZZARD']).
        query: the metric or topic to search for.
        year: optional exact year filter.
        start_year: optional range start (inclusive).
        end_year: optional range end (inclusive).
        section: optional section filter.

    Returns:
        Dict keyed by company name, each value is a list of chunk payloads.
    """
    year_range = None
    if start_year is not None and end_year is not None:
        year_range = (start_year, end_year)

    results = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(len(companies), 5)
    ) as executor:
        futures = {
            executor.submit(
                _fetch_for_company, c, query, year, year_range, section
            ): c
            for c in companies
        }
        for future in concurrent.futures.as_completed(futures):
            company = futures[future]
            try:
                _, payloads = future.result()
                results[company] = payloads
            except Exception as e:
                results[company] = {"error": str(e)}

    return results
