"""
Custom LangChain ChatModel wrapping the Bedrock proxy for Llama 4 Scout.
Implements BaseChatModel so it works with create_react_agent.
"""

import json
import requests
from typing import Any, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatResult, ChatGeneration

from config import BEDROCK_PROXY_URL, BEDROCK_MODEL_ID, BEDROCK_MAX_GEN_LEN


class ChatBedrockProxy(BaseChatModel):
    """Chat model that calls Llama via Bedrock proxy."""

    model_id: str = BEDROCK_MODEL_ID
    proxy_url: str = BEDROCK_PROXY_URL
    max_gen_len: int = BEDROCK_MAX_GEN_LEN
    temperature: float = 0.0

    @property
    def _llm_type(self) -> str:
        return "bedrock-proxy-llama"

    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a single prompt string for Llama."""
        parts = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                parts.append(f"<|system|>\n{msg.content}\n")
            elif isinstance(msg, HumanMessage):
                parts.append(f"<|user|>\n{msg.content}\n")
            elif isinstance(msg, AIMessage):
                content = msg.content or ""
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls_str = json.dumps(msg.tool_calls, default=str)
                    content += f"\n[Tool calls: {tool_calls_str}]"
                parts.append(f"<|assistant|>\n{content}\n")
            elif isinstance(msg, ToolMessage):
                parts.append(f"<|tool|>\n[{msg.name}] {msg.content}\n")
        parts.append("<|assistant|>\n")
        return "".join(parts)

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        prompt = self._messages_to_prompt(messages)

        resp = requests.post(
            self.proxy_url,
            json={
                "model_id": self.model_id,
                "stream": False,
                "prompt": prompt,
                "max_gen_len": self.max_gen_len,
                "temperature": self.temperature,
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            raise RuntimeError(f"Bedrock proxy error: {data['error']}")

        text = data.get("generation", "")

        # Check if the response contains tool calls (JSON format)
        ai_msg = AIMessage(content=text)

        return ChatResult(generations=[ChatGeneration(message=ai_msg)])
