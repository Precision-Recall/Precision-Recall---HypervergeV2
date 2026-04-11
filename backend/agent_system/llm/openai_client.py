"""
OpenAI GPT-nano client for the main / gateway agents.
Single responsibility: provide a LangChain-compatible ChatModel.
"""

from langchain_openai import ChatOpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


def get_openai_llm(temperature: float = 0.0) -> ChatOpenAI:
    """Return a LangChain ChatOpenAI instance configured for GPT-nano."""
    return ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=temperature,
    )
