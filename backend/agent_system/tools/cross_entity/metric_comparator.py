"""
Metric comparator — extracts a metric from all companies for the same year.
Contains an inner LLM agent (Llama 4 Scout) for value extraction.
Now parallel across companies.

Single responsibility: companies + metric + year → comparison table.
"""

import concurrent.futures

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue

from retriever.client import search_chunks
from llm.bedrock_client import llm_generate
from tools.call_limiter import max_calls


def _extract_for_company(company: str, metric_name: str, year: int, form_type: str) -> tuple[str, dict]:
    """Extract metric for a single company. Returns (company, result)."""
    must_filters = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="year", match=MatchValue(value=year)),
        FieldCondition(key="type", match=MatchValue(value="table")),
        FieldCondition(key="form_type", match=MatchValue(value=form_type)),
    ]

    results = search_chunks(
        query=f"{metric_name} {company} {year}",
        must_filters=must_filters,
        limit=5,
    )

    if results:
        best = results[0]
        raw = best["payload"].get("raw_content", "") or best["payload"].get("text", "")
        value = llm_generate(
            f"Extract '{metric_name}' value from: {raw[:1500]}\n\n"
            f"Return ONLY the number with unit.",
            max_gen_len=128,
        ).strip()
        return company, {
            "value": value,
            "source_section": best["payload"].get("section"),
            "source_item": best["payload"].get("section_item"),
            "year": year,
        }

    return company, {"value": "N/A", "source_section": None, "source_item": None, "year": year}


@tool
@max_calls(5)
def metric_comparator(
    companies: list[str],
    metric_name: str,
    year: int,
    form_type: str = "10-K",
) -> dict:
    """Build a peer comparison table for a single metric across companies (parallel).

    Args:
        companies: list of company names.
        metric_name: the financial metric to compare.
        year: the year to compare across.
        form_type: filing type (default '10-K').

    Returns:
        Dict keyed by company → {value, source_section, source_item, year}.
    """
    comparison = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(companies), 5)) as pool:
        futures = {
            pool.submit(_extract_for_company, c, metric_name, year, form_type): c
            for c in companies
        }
        for future in concurrent.futures.as_completed(futures):
            company, result = future.result()
            comparison[company] = result

    return comparison
