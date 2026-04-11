"""
Forensic tools — LangChain tools that the ReAct agent calls.

Each tool does filtered Qdrant retrieval for a specific forensic purpose.
The LLM agent decides WHEN to call them and REASONS over the results.

Section item format in Qdrant payload: "Item 7", "Item 1A", etc.

Lens-aware query templates focus the semantic search on the right domain.
"""

from langchain.tools import tool
from retriever import search_sections, scroll_section
from llm_client import llm_generate


# ─── Lens → query focus mapping ─────────────────────────────────────
LENS_KEYWORDS = {
    "finance": "revenue profit debt liquidity cash flow financial performance margins",
    "environment": "renewable energy emissions carbon sustainability climate ESG environmental",
    "strategy": "growth strategy market expansion acquisition product roadmap competitive",
    "governance": "board directors compensation audit compliance internal controls governance",
}


def _lens_query(base_query: str, lens: str) -> str:
    """Augment a query with lens-specific keywords for better semantic targeting."""
    extra = LENS_KEYWORDS.get(lens, "")
    return f"{base_query} {extra}".strip() if extra else base_query


# ─── Promise vs Reality sections ─────────────────────────────────────
# Item 1 (Business) + Item 7 (MD&A) + Item 1A (Risk Factors for caveats)
PROMISE_SECTIONS = ["Item 1", "Item 7", "Item 1A"]

# ─── Anomaly Detection sections ──────────────────────────────────────
# Item 1A (Risk Factors) + Item 9A (Controls) + Item 13 (Related Party)
# (used directly in compare_risk_factors tool via scroll_section calls)

# ─── Sentiment Divergence sections ───────────────────────────────────
# Item 7 (MD&A) for CEO tone, Item 7A + Item 8 for counter-signals
SENTIMENT_OPTIMISM_SECTIONS = ["Item 7"]
SENTIMENT_RISK_SECTIONS = ["Item 7A", "Item 8"]


@tool
def search_promise_evidence(
    company: str,
    year: int,
    promise_query: str,
    lens: str = "strategy",
) -> dict:
    """Search for promise or commitment evidence in a specific year's 10-K filing.

    Searches Item 1 (Business), Item 7 (MD&A), and Item 1A (Risk Factors)
    for forward-looking statements, targets, and commitments.

    Use this TWICE for promise-vs-reality: once for the promise year,
    once for the verification year.

    Args:
        company: company name exactly as stored (e.g., '3M', 'ACTIVISIONBLIZZARD').
        year: filing year to search.
        promise_query: what promise/commitment to look for.
        lens: focus area — 'finance', 'environment', 'strategy', or 'governance'.

    Returns:
        Dict with matched evidence chunks and metadata.
    """
    query = _lens_query(promise_query, lens)
    results = search_sections(query, company, PROMISE_SECTIONS, year=year, limit=8)

    if not results:
        return {
            "NO_DATA": True,
            "message": f"No evidence found for '{promise_query}' in {company} {year}. "
                       f"Check company name with list_companies tool.",
        }

    return {
        "company": company,
        "year": year,
        "lens": lens,
        "query": promise_query,
        "evidence": [
            {
                "text": r["payload"].get("text", "")[:500],
                "section": r["payload"].get("section", ""),
                "section_item": r["payload"].get("section_item", ""),
                "page": r["payload"].get("page"),
                "score": round(r["score"], 4),
            }
            for r in results
        ],
    }


@tool
def compare_risk_factors(
    company: str,
    year_a: int,
    year_b: int,
    lens: str = "governance",
) -> dict:
    """Compare risk factor language between two years to detect anomalies.

    Exhaustively retrieves Item 1A (Risk Factors) from both years and uses
    an inner LLM to identify new risks, dropped risks, and tone shifts.

    Also checks Item 9A (Controls) and Item 13 (Related Party) for changes.

    Args:
        company: company name exactly as stored.
        year_a: earlier year.
        year_b: later year.
        lens: focus area — 'finance', 'environment', 'strategy', or 'governance'.

    Returns:
        Dict with structured diff analysis.
    """
    # Get full risk factor text from both years
    risk_a = scroll_section(company, "Item 1A", year_a)
    risk_b = scroll_section(company, "Item 1A", year_b)

    if not risk_a and not risk_b:
        return {
            "NO_DATA": True,
            "message": f"No Risk Factors found for {company} in {year_a} or {year_b}.",
        }

    lens_focus = LENS_KEYWORDS.get(lens, "")
    diff = llm_generate(
        f"You are a forensic accountant analyzing 10-K Risk Factors.\n"
        f"Focus area: {lens} ({lens_focus})\n\n"
        f"Compare these Risk Factors sections and identify:\n"
        f"1. NEW risks in {year_b} not present in {year_a}\n"
        f"2. Risks REMOVED from {year_a} to {year_b}\n"
        f"3. Risks with CHANGED severity or language\n"
        f"4. Overall risk tone shift\n\n"
        f"--- {year_a} Risk Factors ---\n{risk_a[:4000]}\n\n"
        f"--- {year_b} Risk Factors ---\n{risk_b[:4000]}",
        max_gen_len=1024,
    )

    # Also check controls and related party for supplementary signals
    controls_a = scroll_section(company, "Item 9A", year_a)
    controls_b = scroll_section(company, "Item 9A", year_b)
    controls_changed = bool(controls_a) != bool(controls_b) or (
        controls_a and controls_b and abs(len(controls_a) - len(controls_b)) > len(controls_a) * 0.3
    )

    return {
        "company": company,
        "year_a": year_a,
        "year_b": year_b,
        "lens": lens,
        "risk_factor_diff": diff,
        "risk_words_year_a": len(risk_a.split()) if risk_a else 0,
        "risk_words_year_b": len(risk_b.split()) if risk_b else 0,
        "controls_changed": controls_changed,
    }


@tool
def search_sentiment_signals(
    company: str,
    year: int,
    signal_type: str,
    lens: str = "finance",
) -> dict:
    """Search for optimism or risk signals in a specific year's 10-K.

    Two modes:
    - signal_type='optimism': searches Item 7 (MD&A) for positive management tone
    - signal_type='risk': searches Item 7A (Market Risk) + Item 8 (Footnotes)
      for counter-signals like liquidity concerns, going concern, contingent liabilities

    Call this TWICE for sentiment divergence: once with 'optimism', once with 'risk'.

    Args:
        company: company name exactly as stored.
        year: filing year.
        signal_type: 'optimism' or 'risk'.
        lens: focus area — 'finance', 'environment', 'strategy', or 'governance'.

    Returns:
        Dict with matched signal evidence.
    """
    if signal_type == "optimism":
        sections = SENTIMENT_OPTIMISM_SECTIONS
        base_query = "strong growth record performance excellent results significant progress achievements"
    elif signal_type == "risk":
        sections = SENTIMENT_RISK_SECTIONS
        base_query = "liquidity concerns going concern material weakness contingent liabilities debt covenant"
    else:
        return {"error": f"signal_type must be 'optimism' or 'risk', got '{signal_type}'"}

    query = _lens_query(base_query, lens)
    results = search_sections(query, company, sections, year=year, limit=8)

    if not results:
        return {
            "NO_DATA": True,
            "signal_type": signal_type,
            "message": f"No {signal_type} signals found for {company} {year}.",
        }

    return {
        "company": company,
        "year": year,
        "signal_type": signal_type,
        "lens": lens,
        "evidence": [
            {
                "text": r["payload"].get("text", "")[:500],
                "section": r["payload"].get("section", ""),
                "section_item": r["payload"].get("section_item", ""),
                "page": r["payload"].get("page"),
                "score": round(r["score"], 4),
            }
            for r in results
        ],
    }


@tool
def list_companies() -> dict:
    """List all companies and years available in the Qdrant collection.

    Use this when unsure about exact company names or available year ranges.
    """
    from qdrant_client.models import Filter
    from retriever import get_qdrant
    from config import QDRANT_COLLECTION

    client = get_qdrant()
    # Scroll a sample to discover companies/years
    results, _ = client.scroll(
        collection_name=QDRANT_COLLECTION,
        limit=500,
        with_payload=True,
    )

    companies = {}
    for pt in results:
        co = pt.payload.get("company")
        yr = pt.payload.get("year")
        if co and yr:
            if co not in companies:
                companies[co] = set()
            companies[co].add(yr)

    return {
        co: sorted(list(years))
        for co, years in sorted(companies.items())
    }


# All tools exposed to the agent
ALL_FORENSIC_TOOLS = [
    search_promise_evidence,
    compare_risk_factors,
    search_sentiment_signals,
    list_companies,
]
