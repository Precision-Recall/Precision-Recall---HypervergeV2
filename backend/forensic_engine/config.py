"""
Configuration for the forensic engine.
Loads .env from backend/agent_system — single source of truth for all secrets.
"""

import os
from dotenv import load_dotenv

_AGENT_SYSTEM_ENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agent_system", ".env")
load_dotenv(_AGENT_SYSTEM_ENV)

# ─── OpenAI (orchestrator LLM) ──────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL environment variable is required")

# ─── Bedrock Proxy (inner LLM for tools) ────────────────────────────
BEDROCK_PROXY_URL = os.getenv("BEDROCK_PROXY_URL")
if not BEDROCK_PROXY_URL:
    raise ValueError("BEDROCK_PROXY_URL environment variable is required")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
if not BEDROCK_MODEL_ID:
    raise ValueError("BEDROCK_MODEL_ID environment variable is required")
BEDROCK_MAX_GEN_LEN = int(os.getenv("BEDROCK_MAX_GEN_LEN", "2048"))

# ─── Embedding (BGE-M3) ─────────────────────────────────────────────
EMBEDDING_URL = os.getenv("EMBEDDING_URL")
if not EMBEDDING_URL:
    raise ValueError("EMBEDDING_URL environment variable is required")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
if not EMBEDDING_MODEL:
    raise ValueError("EMBEDDING_MODEL environment variable is required")

# ─── Qdrant ──────────────────────────────────────────────────────────
QDRANT_HOST = os.getenv("QDRANT_HOST")
if not QDRANT_HOST:
    raise ValueError("QDRANT_HOST environment variable is required")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
if not QDRANT_COLLECTION:
    raise ValueError("QDRANT_COLLECTION environment variable is required")

# ─── WebSocket ───────────────────────────────────────────────────────
WS_PORT = int(os.getenv("WS_PORT", "6060"))
