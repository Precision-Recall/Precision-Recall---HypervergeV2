"""
Cross-encoder reranking using BGE-reranker-v2-m3 via LM Studio.
Single responsibility: query + candidates → reranked top-n.
"""

import requests

from config import RERANKER_URL, RERANKER_MODEL, TOP_N_RERANK


def _score_pair(query: str, passage: str) -> float:
    """Compute a cross-encoder relevance score for a single query-passage pair.

    LM Studio exposes rerankers as an embeddings-compatible endpoint.
    We send [query, passage] and the model returns a similarity score.
    """
    response = requests.post(
        RERANKER_URL,
        json={
            "model": RERANKER_MODEL,
            "input": [query, passage],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    # LM Studio reranker returns cosine similarity between the pair embeddings
    emb_query = data["data"][0]["embedding"]
    emb_passage = data["data"][1]["embedding"]

    # Cosine similarity (vectors are already normalized by the model)
    dot_product = sum(a * b for a, b in zip(emb_query, emb_passage))
    return dot_product


def rerank(
    query: str,
    candidates: list[dict],
    top_n: int = TOP_N_RERANK,
) -> list[dict]:
    """Rerank candidate chunks using the cross-encoder model.

    Args:
        query: the user's search query.
        candidates: list of dicts, each must have payload.text.
        top_n: number of top results to return.

    Returns:
        Reranked list of candidate dicts (top_n), with added 'rerank_score'.
    """
    if not candidates:
        return []

    scored = []
    for candidate in candidates:
        text = candidate.get("payload", {}).get("text", "")
        if not text:
            continue
        score = _score_pair(query, text)
        scored.append({**candidate, "rerank_score": score})

    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:top_n]
