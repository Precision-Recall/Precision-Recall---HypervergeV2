"""
Bedrock proxy client for Llama 4 Scout 17B — used by inner agents inside tools.
Single responsibility: send prompt → receive generation. With retry + streaming.
"""

import json
import time
import requests

from config import BEDROCK_PROXY_URL, BEDROCK_MODEL_ID, BEDROCK_MAX_GEN_LEN


def llm_generate(prompt: str, max_gen_len: int = BEDROCK_MAX_GEN_LEN, retries: int = 3) -> str:
    """Send a prompt to Llama 4 Scout via Bedrock proxy and return the generation.
    
    Streams the response and concatenates chunks. Retries on rate limit.
    """
    for attempt in range(retries):
        try:
            response = requests.post(
                BEDROCK_PROXY_URL,
                json={
                    "model_id": BEDROCK_MODEL_ID,
                    "stream": True,
                    "prompt": prompt,
                    "max_gen_len": max_gen_len,
                },
                timeout=120,
                stream=True,
            )
            response.raise_for_status()

            # Parse SSE stream
            full_text = ""
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    full_text += chunk.get("generation", "")
                except json.JSONDecodeError:
                    continue

            return full_text

        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 429:
                wait = 2 ** attempt
                print(f"      ⏳ Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            raise

    raise RuntimeError("Max retries exceeded for Bedrock LLM call")


def llm_extract_json(prompt: str, max_gen_len: int = BEDROCK_MAX_GEN_LEN) -> dict:
    """Send a prompt and parse the response as JSON."""
    raw = llm_generate(prompt, max_gen_len)

    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(cleaned[start:end])
        raise ValueError(f"Could not parse JSON from LLM response: {raw[:200]}")
