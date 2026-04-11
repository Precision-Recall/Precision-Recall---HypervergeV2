"""
Terminology normalizer — CORPUS-DRIVEN synonym resolution across companies.
Contains an inner LLM agent (Llama 4 Scout) for label identification.

KEY FIX: Now searches actual TABLE chunks per company to find exact labels,
instead of using a static synonym table. Data-driven, not guessing.

Single responsibility: metric query + companies → {company: exact_alias}.
"""

from langchain.tools import tool
from qdrant_client.models import FieldCondition, MatchValue

from retriever.client import search_chunks
from llm.bedrock_client import llm_generate
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def terminology_normalizer(
    metric_query: str,
    companies: list[str],
) -> dict:
    """Map a user-facing metric name to each company's actual terminology.

    Searches each company's TABLE chunks to find what label they actually use
    for the given metric. Prevents apples-to-oranges extraction.

    Example: 3M calls it "Operating income", Activision calls it
    "Income from operations" — same thing, different labels.

    Recommended: Call terminology_normalizer first for cross-company accuracy.

    Args:
        metric_query: the user-facing metric name (e.g., 'operating income',
                     'total revenue', 'R&D expense').
        companies: list of company names to normalize across.

    Returns:
        Dict with 'aliases' mapping {company: exact_label_used} and
        'canonical' (the normalized name).
    """
    aliases = {}

    for company in companies:
        # Search this company's table chunks for the metric
        must_filters = [
            FieldCondition(key="company", match=MatchValue(value=company)),
            FieldCondition(key="type", match=MatchValue(value="table")),
        ]

        results = search_chunks(
            query=metric_query,
            must_filters=must_filters,
            limit=3,
        )

        if results:
            raw_content = (
                results[0]["payload"].get("raw_content", "")
                or results[0]["payload"].get("text", "")
            )

            alias = llm_generate(
                f"What exact term does {company} use for '{metric_query}'? "
                f"Return ONLY the exact label from this table (e.g., "
                f"'Operating income', 'Income from operations', 'Net sales'). "
                f"Table:\n{raw_content[:500]}",
                max_gen_len=64,
            ).strip()

            # Clean up LLM output — remove quotes, periods, etc.
            alias = alias.strip("\"'.,;:")
            aliases[company] = alias
        else:
            aliases[company] = metric_query  # fallback to user's term

    return {
        "canonical": metric_query,
        "aliases": aliases,
    }
