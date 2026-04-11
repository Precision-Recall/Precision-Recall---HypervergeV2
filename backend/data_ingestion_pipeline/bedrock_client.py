"""
Bedrock proxy client for embeddings and image captioning.
"""

import requests
import base64
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import BEDROCK_PROXY_URL, EMBEDDING_URL, EMBEDDING_MODEL, CAPTION_MODEL, MAX_PARALLEL_EMBEDDINGS


def get_embedding(text: str, retries: int = 5) -> list[float]:
    """Get embedding from BGE-M3 via local LM Studio."""
    for attempt in range(retries):
        resp = requests.post(EMBEDDING_URL, json={
            "model": EMBEDDING_MODEL,
            "input": text[:8000],
        }, timeout=30)
        if resp.status_code == 429:
            wait = 2 ** attempt
            print(f"    Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]
    raise RuntimeError("Max retries exceeded for embedding")


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Get embeddings in parallel."""
    results = [None] * len(texts)

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_EMBEDDINGS) as pool:
        futures = {pool.submit(get_embedding, t): i for i, t in enumerate(texts)}
        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()

    return results


def caption_image(image_path: str) -> str:
    """Caption an image using Llama 4 Scout via Bedrock proxy."""
    path = Path(image_path)
    if not path.exists():
        return ""

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    resp = requests.post(BEDROCK_PROXY_URL, json={
        "model_id": CAPTION_MODEL,
        "stream": False,
        "prompt": f"<|image|>data:image/jpeg;base64,{b64}\nDescribe this financial document image in detail. Focus on key data, numbers, and trends shown.",
        "max_gen_len": 300,
    }, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        return ""
    return data.get("generation", "")
