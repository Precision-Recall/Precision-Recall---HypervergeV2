"""
Full RAG retrieval pipeline: embed → HNSW search → top-n.
Reranker removed — direct vector search with metadata filtering is sufficient
when metadata filters are precise (company + year + section).
"""

from retriever.embedding import embed_query
from retriever.hnsw_search import vector_search
from config import TOP_K_HNSW


_DIM     = "\033[2m"
_CYAN    = "\033[36m"
_MAGENTA = "\033[35m"
_RESET   = "\033[0m"


def retrieve(
    query: str,
    filters: dict | None = None,
    top_k: int = TOP_K_HNSW,
) -> list[dict]:
    """End-to-end retrieval: embed query → HNSW search → top-k results.

    Args:
        query: natural language query.
        filters: metadata filters (company, year, section, etc.).
        top_k: results to return.

    Returns:
        List of top-k chunk dicts, each with id, score, payload.
    """
    q_display = query[:60] + "..." if len(query) > 60 else query
    filter_parts = ", ".join(f"{k}={v}" for k, v in (filters or {}).items())

    print(f"      {_MAGENTA}🧬 EMBED{_RESET}  {_DIM}query=\"{q_display}\"{_RESET}")
    query_vector = embed_query(query)

    print(f"      {_CYAN}🔍 HNSW{_RESET}   {_DIM}top_k={top_k}, filters=[{filter_parts or 'none'}]{_RESET}")
    results = vector_search(query_vector, filters=filters, top_k=top_k)

    if results:
        print(f"      {_DIM}   → {len(results)} results (best={results[0].get('score', 0):.4f}){_RESET}")
    else:
        print(f"      {_DIM}   → 0 results{_RESET}")

    return results
