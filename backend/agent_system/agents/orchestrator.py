"""
Single orchestrator agent with all necessary tools.
Uses ReAct loop — autonomously chains tools until outcome is reached.
Two layers: Agent (GPT) → Tools (some with inner Llama LLM).
"""

import sys
import os
import json
import time
import queue as _queue

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from config import OPENAI_API_KEY, OPENAI_MODEL

# Core tools
from tools.temporal.year_range_retriever import year_range_retriever
from tools.temporal.metric_trend_extractor import metric_trend_extractor
from tools.temporal.narrative_diff_tool import narrative_diff_tool
from tools.cross_entity.multi_company_retriever import multi_company_retriever
from tools.cross_entity.metric_comparator import metric_comparator
from tools.cross_entity.terminology_normalizer import terminology_normalizer
from tools.cross_entity.cross_temporal_benchmarker import cross_temporal_benchmarker
from tools.shared.list_available_data import list_available_data

from tools.call_limiter import reset_call_counts
from skill_loader import load_all_skills, skills_to_prompt

# Global event queue for streaming
_event_queue: _queue.Queue | None = None


def set_event_queue(eq: _queue.Queue | None):
    global _event_queue
    _event_queue = eq


def _emit(event_type, **kwargs):
    if _event_queue:
        _event_queue.put({"type": event_type, "timestamp": time.time() * 1000, **kwargs})


def _truncate(text, n=300):
    return str(text)[:n] + ("..." if len(str(text)) > n else "")


# Load all skills into the system prompt at startup
_all_skills = load_all_skills()
_skills_prompt = skills_to_prompt(list(_all_skills.values()))


SYSTEM_PROMPT = f"""You are a Financial Intelligence Agent — an expert at analyzing SEC filings
(10-K, 10-Q, 8-K) across multiple companies and years.

## Autonomous Execution
- You have a ReAct loop. Chain multiple tools until you have enough data to answer.
- Do NOT stop after one tool call if you need more data.
- If a tool returns NO_DATA, try different parameters ONCE. If still empty, report the gap.
- Do NOT retry the same tool with the same parameters.

## Response Rules
- Answer ONLY from retrieved data. Never use your own knowledge about companies.
- Include specific numbers, years, and sections in your answer.
- If data is missing, say so explicitly. Keep it under 300 words.
- For greetings or vague queries, respond directly and ask for specifics.

## Available Skills & Tools
{_skills_prompt}
"""

ALL_TOOLS = [
    year_range_retriever,
    metric_trend_extractor,
    narrative_diff_tool,
    multi_company_retriever,
    metric_comparator,
    terminology_normalizer,
    cross_temporal_benchmarker,
    list_available_data,
]


def _get_llm(provider: str = "gemini"):
    """Get LLM by provider name. Plug-and-play switching."""
    from config import (OPENAI_MODEL, OPENAI_API_KEY,
                        GEMINI_MODEL, GEMINI_PROJECT, GEMINI_LOCATION, GEMINI_CREDENTIALS_FILE)

    if provider == "openai":
        return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0.0)
    elif provider == "gemini":
        creds_raw = open(GEMINI_CREDENTIALS_FILE).read()
        creds_json = json.loads(creds_raw.split("GOOGLE_APPLICATION_CREDENTIALS_JSON=")[1].split("\n")[0])
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(creds_json, f); f.close()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name
        return ChatVertexAI(
            model_name=GEMINI_MODEL,
            project=GEMINI_PROJECT,
            location=GEMINI_LOCATION,
            temperature=0.0,
            max_output_tokens=2048,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


# Default provider — changed via /switch endpoint or frontend
_current_provider = "gemini"


def get_current_provider() -> str:
    return _current_provider


def set_provider(provider: str):
    global _current_provider
    _current_provider = provider


def create_agent(provider: str = None):
    """Create the orchestrator agent with the specified LLM provider."""
    llm = _get_llm(provider or _current_provider)
    memory = MemorySaver()

    return create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )
