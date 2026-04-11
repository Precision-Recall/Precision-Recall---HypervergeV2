"""
Configuration for the data ingestion pipeline.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bedrock proxy
BEDROCK_PROXY_URL = os.getenv("BEDROCK_PROXY_URL")
if not BEDROCK_PROXY_URL:
    raise ValueError("BEDROCK_PROXY_URL environment variable is required")

# Models
CAPTION_MODEL = os.getenv("BEDROCK_MODEL_ID")
if not CAPTION_MODEL:
    raise ValueError("BEDROCK_MODEL_ID environment variable is required")

# Embedding (BGE-M3 via LM Studio)
EMBEDDING_URL = os.getenv("EMBEDDING_URL")
if not EMBEDDING_URL:
    raise ValueError("EMBEDDING_URL environment variable is required")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
if not EMBEDDING_MODEL:
    raise ValueError("EMBEDDING_MODEL environment variable is required")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))

# Chunking
MAX_CHUNK_TOKENS = int(os.getenv("MAX_CHUNK_TOKENS", "600"))
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "100"))

# Qdrant
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
if not QDRANT_COLLECTION:
    raise ValueError("QDRANT_COLLECTION environment variable is required")
QDRANT_HOST = os.getenv("QDRANT_HOST")
if not QDRANT_HOST:
    raise ValueError("QDRANT_HOST environment variable is required")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Processing
MAX_PARALLEL_PDFS = int(os.getenv("MAX_PARALLEL_PDFS", "2"))
MAX_PARALLEL_EMBEDDINGS = int(os.getenv("MAX_PARALLEL_EMBEDDINGS", "3"))
