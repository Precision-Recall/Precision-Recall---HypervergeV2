"""
Pivot detector — identifies the year a company shifted primary business focus.
Composite tool: uses direct retrieval + LLM analysis (not other @tool functions).
This avoids call limiter conflicts with inner tools.

Single responsibility: detect business focus pivots across a year range.
"""

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue, Range

from retriever.client import search_chunks, scroll_chunks
from llm.bedrock_client import llm_generate, llm_extract_json
from tools.call_limiter import max_calls


@tool
@max_calls(3)
def pivot_detector(
    company: str,
    start_year: int,
    end_year: int,
) -> dict:
    """Identify the year a company shifted its primary business focus.

    Cross-correlates revenue mix changes with executive language shifts.
    Uses direct retrieval (not other tools) to avoid call limiter conflicts.

    Args:
        company: company name (e.g., '3M').
        start_year: beginning of analysis range.
        end_year: end of analysis range.

    Returns:
        Dict with pivot_detected, pivot_year, confidence, evidence, summary.
    """
    # 1. Get revenue table data across years
    revenue_results = search_chunks(
        query=f"Total Revenue net sales {company}",
        must_filters=[
            FieldCondition(key="company", match=MatchValue(value=company)),
            FieldCondition(key="type", match=MatchValue(value="table")),
            FieldCondition(key="year", range=Range(gte=start_year, lte=end_year)),
        ],
        limit=20,
    )

    revenue_context = ""
    for r in revenue_results:
        year = r["payload"].get("year", "?")
        text = r["payload"].get("text", "")[:300]
        revenue_context += f"\n[{year}] {text}\n"

    # 2. Get Business section narrative per year via scroll
    years = list(range(start_year, end_year + 1))
    narrative_context = ""
    for year in years:
        chunks = scroll_chunks(
            must_filters=[
                FieldCondition(key="company", match=MatchValue(value=company)),
                FieldCondition(key="section", match=MatchValue(value="Business")),
                FieldCondition(key="year", match=MatchValue(value=year)),
                FieldCondition(key="type", match=MatchValue(value="text")),
            ],
            limit=20,
        )
        chunks.sort(key=lambda c: c["payload"].get("page", 0))
        year_text = " ".join(c["payload"].get("text", "")[:200] for c in chunks[:5])
        narrative_context += f"\n=== {year} ===\n{year_text}\n"

    # 3. Single LLM call to analyze pivot
    prompt = (
        f"Analyze {company} from {start_year} to {end_year} for business focus pivots.\n\n"
        f"REVENUE DATA:\n{revenue_context[:2000]}\n\n"
        f"BUSINESS NARRATIVE:\n{narrative_context[:2000]}\n\n"
        f"Respond with ONLY valid JSON:\n"
        f'{{"pivot_detected": true/false, "pivot_year": <year or null>, '
        f'"confidence": "<high/medium/low>", '
        f'"evidence": {{"revenue_shift": "<desc>", "language_shift": "<desc>"}}, '
        f'"summary": "<2-3 sentence synthesis>"}}'
    )

    try:
        result = llm_extract_json(prompt, max_gen_len=1024)
    except (ValueError, RuntimeError):
        result = {
            "pivot_detected": False,
            "pivot_year": None,
            "confidence": "low",
            "summary": "Pivot analysis could not be completed.",
        }

    result["metadata"] = {"company": company, "year_range": f"{start_year}-{end_year}"}
    return result
