"""
Reranker tool — exposes the BGE cross-encoder reranking as an OPTIONAL agent-callable tool.
This is the ONLY place reranking happens — tools use direct Qdrant calls by default.
Single responsibility: rerank a candidate set against a query.
"""

from langchain.tools import tool

from retriever.reranker import rerank as _rerank
from retriever.client import get_qdrant, get_collection
from config import TOP_N_RERANK
from tools.call_limiter import max_calls


@tool
@max_calls(5)
def reranker_tool(query: str, chunk_ids: list[str], top_n: int = TOP_N_RERANK) -> list[dict]:
    """Rerank a set of candidate chunks using BGE cross-encoder.

    This is an OPTIONAL tool. Only use when you have a candidate set from
    another tool and want to improve relevance ranking.

    Args:
        query: the search query to rerank against.
        chunk_ids: list of chunk IDs to rerank.
        top_n: number of top results to return (default 10).

    Returns:
        Top-n reranked chunks with relevance scores.
    """
    client = get_qdrant()
    collection = get_collection()

    results = client.retrieve(
        collection_name=collection,
        ids=chunk_ids,
        with_payload=True,
    )
    candidates = [
        {"id": str(point.id), "payload": point.payload}
        for point in results
    ]

    return _rerank(query, candidates, top_n=top_n)
