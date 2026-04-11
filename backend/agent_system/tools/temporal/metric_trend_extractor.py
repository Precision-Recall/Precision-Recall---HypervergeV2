"""
Metric trend extractor — extracts a specific financial metric from TABLE chunks across years.
Contains an inner LLM agent (Llama 4 Scout) that parses HTML tables.

KEY FIX: Single search across ALL years with year-range filter, then iterate.
Previous design made N separate calls per year (5× slower).

Single responsibility: company + metric + year range → {year: value} dict.
"""

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue, Range

from retriever.client import search_chunks
from llm.bedrock_client import llm_generate
from tools.call_limiter import max_calls


def _extract_value_from_table(metric: str, raw_content: str) -> str:
    """Inner agent: use Llama 4 Scout to extract a specific metric value from HTML table.

    Returns ONLY the numeric value with unit.
    """
    prompt = (
        f"Extract only the numeric value for '{metric}' from this table. "
        f"Return ONLY the number with unit (e.g. '$14.2 billion', '23.5%'). "
        f"No HTML, no explanation, just the value. "
        f"If not found, return 'N/A'.\n\n"
        f"Table:\n{raw_content[:4000]}"
    )
    try:
        result = llm_generate(prompt, max_gen_len=64)
        import re
        cleaned = re.sub(r'<[^>]+>', '', result).strip().split('\n')[0].strip()
        return cleaned
    except (RuntimeError, Exception):
        return "N/A"


@tool
@max_calls(5)
def metric_trend_extractor(
    company: str,
    metric_name: str,
    start_year: int,
    end_year: int,
) -> dict:
    """Extract a specific numeric metric from table chunks across a year range.

    Makes ONE search across ALL years with metadata filtering, then extracts
    per-year using the inner LLM. "First most relevant result per year wins."

    Only targets type='table' chunks for precision.

    Args:
        company: company name (e.g., '3M').
        metric_name: the metric to extract (e.g., 'Total Revenue', 'Net Income',
                     'operating margin', 'R&D expense', 'total debt').
        start_year: beginning of year range.
        end_year: end of year range.

    Returns:
        Dict with 'trend' mapping {year: extracted_value} and 'sources'.
    """
    must_filters = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="type", match=MatchValue(value="table")),
        FieldCondition(key="year", range=Range(gte=start_year, lte=end_year)),
    ]

    # ONE search across all years
    results = search_chunks(
        query=f"{metric_name} financial data {company}",
        must_filters=must_filters,
        limit=30,
    )

    if not results:
        return {"trend": {}, "sources": [], "NO_DATA": True, "message": f"No table chunks found for '{metric_name}' at '{company}' ({start_year}-{end_year}). Do NOT retry."}

    # Extract per-year — first most relevant result per year wins
    trend = {}
    sources = []
    for r in results:
        year = r["payload"].get("year")
        if year is None or year in trend:
            continue  # skip if year already extracted (first = most relevant)

        raw_content = r["payload"].get("raw_content", "")
        if not raw_content:
            raw_content = r["payload"].get("text", "")

        value = _extract_value_from_table(metric_name, raw_content)
        trend[year] = value
        sources.append({
            "year": year,
            "chunk_id": r["id"],
            "section": r["payload"].get("section"),
            "raw_content": raw_content,
        })

    return {"trend": dict(sorted(trend.items())), "sources": sources}
