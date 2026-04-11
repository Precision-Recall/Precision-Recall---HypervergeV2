"""
Narrative diff tool — computes what changed in language/narrative between two years.
Contains an inner LLM agent (Llama 4 Scout) that performs qualitative text comparison.

KEY FIX: Uses qdrant.scroll() for EXHAUSTIVE section retrieval, not semantic search.
Semantic search cannot find "what's NOT there" — you need the complete text.

Single responsibility: company + section + year_a + year_b → structured diff.
"""

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue

from retriever.client import scroll_chunks
from llm.bedrock_client import llm_generate
from tools.call_limiter import max_calls


def _get_section_text(company: str, section: str, year: int) -> str:
    """Exhaustively scroll ALL text chunks for a section and concatenate."""
    must_filters = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="section", match=MatchValue(value=section)),
        FieldCondition(key="year", match=MatchValue(value=year)),
        FieldCondition(key="type", match=MatchValue(value="text")),
    ]

    chunks = scroll_chunks(must_filters=must_filters, limit=50)

    # Sort by page for reading order
    chunks.sort(key=lambda c: c["payload"].get("page", 0))
    return " ".join(c["payload"].get("text", "") for c in chunks if c["payload"].get("text"))


@tool
@max_calls(5)
def narrative_diff_tool(
    company: str,
    section: str,
    year_a: int,
    year_b: int,
) -> dict:
    """Retrieve the same section from two years and identify language/narrative shifts.

    Uses EXHAUSTIVE scroll (not semantic search) to get the COMPLETE section text.
    This is critical because semantic search cannot find "what's missing" — a risk
    factor dropped from year_a won't be found by searching with year_b's query terms.

    Args:
        company: company name (e.g., '3M').
        section: section to compare (e.g., 'Risk Factors', 'MD&A', 'Business').
        year_a: the earlier year.
        year_b: the later year.

    Returns:
        Dict with year_a, year_b, section, and diff analysis.
    """
    text_a = _get_section_text(company, section, year_a)
    text_b = _get_section_text(company, section, year_b)

    if not text_a and not text_b:
        return {"error": f"No text found for section '{section}' in either {year_a} or {year_b}. Check company name and section name match exactly. Do NOT retry."}

    diff = llm_generate(
        f"Compare these two versions of '{section}' from {year_a} and {year_b}.\n"
        f"Identify:\n"
        f"1) New themes/risks in {year_b} not in {year_a}\n"
        f"2) Themes dropped from {year_a} to {year_b}\n"
        f"3) Tone shift (more/less optimistic)\n\n"
        f"--- {year_a} ---\n{text_a[:3000]}\n\n"
        f"--- {year_b} ---\n{text_b[:3000]}",
        max_gen_len=1024,
    )

    return {
        "year_a": year_a,
        "year_b": year_b,
        "section": section,
        "diff": diff,
        "chunks_year_a": len(text_a.split()),
        "chunks_year_b": len(text_b.split()),
    }
