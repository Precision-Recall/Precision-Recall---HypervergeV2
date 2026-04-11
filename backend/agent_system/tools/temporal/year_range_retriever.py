"""
Year range retriever — the workhorse of the Temporal Reasoner.
Pulls chunks for a metric/query across a year span for a single company.
Returns results GROUPED BY YEAR for composability with timeline_synthesizer.

Single responsibility: filtered multi-year retrieval with year-grouped output.
"""

from collections import defaultdict

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue, Range

from retriever.client import search_chunks, get_qdrant, get_collection
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def year_range_retriever(
    company: str,
    query: str,
    start_year: int,
    end_year: int,
    section: str = None,
    form_type: str = "10-K",
) -> dict:
    """Retrieve semantically relevant chunks for a company across a year range.

    Filters by company + year range + form_type FIRST, then does semantic search
    within that filtered set. Returns results grouped by year.

    NOTE: Metadata filtering BEFORE semantic search dramatically reduces noise
    vs semantic search + metadata reranking (MultiFinRAG, 2025).

    Args:
        company: exact company name (e.g., '3M', 'ACTIVISIONBLIZZARD').
        query: the metric, topic, or question to search for.
        start_year: beginning of year range (inclusive).
        end_year: end of year range (inclusive).
        section: optional section filter (e.g., 'MD&A', 'Risk Factors').
        form_type: filing type filter (default '10-K'). Use '10-Q' for quarterly.

    Returns:
        Dict keyed by year → list of chunk payloads, sorted by year.
        Example: {2015: [{text: ..., section: ...}, ...], 2016: [...]}
    """
    must_filters = [
        FieldCondition(key="company", match=MatchValue(value=company)),
        FieldCondition(key="form_type", match=MatchValue(value=form_type)),
        FieldCondition(key="year", range=Range(gte=start_year, lte=end_year)),
    ]
    if section:
        must_filters.append(
            FieldCondition(key="section", match=MatchValue(value=section))
        )

    results = search_chunks(query, must_filters=must_filters, limit=20)

    # Auto-expand: fetch immediate neighbors for richer context
    expanded_ids = set()
    for r in results:
        expanded_ids.add(r["id"])
        for key in ("prev_chunk_id", "next_chunk_id"):
            nid = r["payload"].get(key)
            if nid:
                expanded_ids.add(nid)

    # Fetch neighbors not already in results
    existing_ids = {r["id"] for r in results}
    missing_ids = list(expanded_ids - existing_ids)
    if missing_ids:
        client = get_qdrant()
        neighbors = client.retrieve(
            collection_name=get_collection(),
            ids=missing_ids,
            with_payload=True,
        )
        for p in neighbors:
            results.append({"id": str(p.id), "score": 0, "payload": p.payload})

    if not results:
        return {"NO_DATA": True, "message": f"No chunks found for company='{company}', years={start_year}-{end_year}, form_type='{form_type}'. Check company name matches exactly (use list_available_data tool to see available companies/years). Do NOT retry with same parameters."}

    # Group by year for structured output
    by_year = defaultdict(list)
    for r in results:
        year = r["payload"].get("year")
        if year is not None:
            by_year[year].append(r["payload"])

    return dict(sorted(by_year.items()))
