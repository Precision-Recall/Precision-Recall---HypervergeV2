"""
Centralized configuration for the multi-agent financial analysis system.
All values from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── LangSmith Tracing ──────────────────────────────────────────────
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "false")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

# ─── OpenAI ──────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL environment variable is required")

# ─── Bedrock Proxy (Inner Agent LLM) ────────────────────────────────
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
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))

# ─── Gemini (Vertex AI) ─────────────────────────────────────────────
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_PROJECT = os.getenv("GEMINI_PROJECT")
GEMINI_LOCATION = os.getenv("GEMINI_LOCATION")
GEMINI_CREDENTIALS_FILE = os.getenv("GEMINI_CREDENTIALS_FILE")

# ─── Qdrant ──────────────────────────────────────────────────────────
QDRANT_HOST = os.getenv("QDRANT_HOST")
if not QDRANT_HOST:
    raise ValueError("QDRANT_HOST environment variable is required")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
if not QDRANT_COLLECTION:
    raise ValueError("QDRANT_COLLECTION environment variable is required")

# ─── Retriever ───────────────────────────────────────────────────────
TOP_K_HNSW = int(os.getenv("TOP_K_HNSW", "50"))

# ─── Tool Limits ─────────────────────────────────────────────────────
MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "5"))
