"""
Cross-temporal benchmarker — hybrid tool for queries that are both cross-entity AND temporal.
Builds a {company: {year: value}} matrix for multi-company trend comparison.

Single responsibility: companies + metric + year range → comparison matrix.
"""

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue, Range

from retriever.client import search_chunks
from llm.bedrock_client import llm_generate
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def cross_temporal_benchmarker(
    companies: list[str],
    metric_name: str,
    start_year: int,
    end_year: int,
) -> dict:
    """Build a {company: {year: value}} matrix for multi-company trend comparison.

    Direct Qdrant searches per company with year-range filter, then LLM extraction.
    e.g., Total Revenue for 3M, Activision from 2015-2018.

    Args:
        companies: list of company names.
        metric_name: the financial metric to benchmark (e.g., 'Total Revenue').
        start_year: beginning of year range.
        end_year: end of year range.

    Returns:
        Dict with 'matrix' ({company: {year: value}}), and 'analysis'.
    """
    matrix = {}

    for company in companies:
        trend = {}
        must_filters = [
            FieldCondition(key="company", match=MatchValue(value=company)),
            FieldCondition(key="type", match=MatchValue(value="table")),
            FieldCondition(key="year", range=Range(gte=start_year, lte=end_year)),
        ]

        results = search_chunks(
            query=f"{metric_name}",
            must_filters=must_filters,
            limit=20,
        )

        # Extract per-year — first most relevant per year wins
        for r in results:
            year = r["payload"].get("year")
            if year is None or year in trend:
                continue
            raw = r["payload"].get("raw_content", "") or r["payload"].get("text", "")
            val = llm_generate(
                f"Extract '{metric_name}' from: {raw[:1000]}\n\n"
                f"Return ONLY the number with unit.",
                max_gen_len=128,
            ).strip()
            trend[year] = val

        matrix[company] = dict(sorted(trend.items()))

    return {"matrix": matrix}
