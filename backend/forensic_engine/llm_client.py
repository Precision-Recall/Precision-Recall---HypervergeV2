"""
Bedrock proxy client for Llama 4 Scout — inner LLM for forensic tools.
Mirrors agent_system/llm/bedrock_client.py.
"""

import json
import time
import requests

from config import BEDROCK_PROXY_URL, BEDROCK_MODEL_ID, BEDROCK_MAX_GEN_LEN


def llm_generate(prompt: str, max_gen_len: int = BEDROCK_MAX_GEN_LEN, retries: int = 3) -> str:
    """Send prompt to Llama 4 Scout via Bedrock proxy, return generation."""
    for attempt in range(retries):
        try:
            resp = requests.post(
                BEDROCK_PROXY_URL,
                json={"model_id": BEDROCK_MODEL_ID, "stream": True,
                      "prompt": prompt, "max_gen_len": max_gen_len},
                timeout=120, stream=True,
            )
            resp.raise_for_status()

            full_text = ""
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    full_text += json.loads(data_str).get("generation", "")
                except json.JSONDecodeError:
                    continue
            return full_text

        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 429 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            raise

    raise RuntimeError("Max retries exceeded for Bedrock LLM call")
