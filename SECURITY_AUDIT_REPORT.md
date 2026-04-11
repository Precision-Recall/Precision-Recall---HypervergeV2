# Security Audit Report - Hardcoded URLs and API Keys

**Date:** 2026-04-11  
**Status:** ✅ COMPLETED

## Summary

Comprehensive audit and cleanup of hardcoded URLs, API keys, and fallback values across the codebase. All critical configuration values now require environment variables.

## Issues Found and Fixed

### 1. Hardcoded API Keys ❌ CRITICAL

#### `backend/data_ingestion_pipeline/app.py`
- **Issue:** Hardcoded OpenAI API key exposed in source code
- **Fixed:** Removed hardcoded key, now requires `OPENAI_API_KEY` environment variable
- **Line:** 18

#### `script/check_openai_credentials.py`
- **Issue:** Hardcoded fallback API key "nn"
- **Fixed:** Removed fallback, script now requires explicit API key via `--key` flag or `OPENAI_API_KEY` env var
- **Line:** 161

### 2. Hardcoded URLs ❌ CRITICAL

#### Backend Configuration Files

**`backend/agent_system/config.py`**
- ❌ Bedrock Proxy URL: hardcoded AWS Lambda URL
- ❌ LangSmith Endpoint: hardcoded URL
- ❌ Embedding URL: hardcoded internal IP
- ✅ **Fixed:** All URLs now require environment variables with validation

**`backend/forensic_engine/config.py`**
- ❌ Bedrock Proxy URL: hardcoded AWS Lambda URL
- ❌ Embedding URL: hardcoded internal IP
- ✅ **Fixed:** All URLs now require environment variables with validation

**`backend/data_ingestion_pipeline/config.py`**
- ❌ Bedrock Proxy URL: hardcoded AWS Lambda URL
- ❌ Embedding URL: hardcoded internal IP
- ❌ Qdrant Host: hardcoded internal IP
- ✅ **Fixed:** Completely refactored to use environment variables with validation

#### Frontend Configuration Files

**`agent-frontend/src/lib/summarize.ts`**
- ❌ Bedrock URL: hardcoded AWS Lambda URL
- ❌ Model ID: hardcoded model identifier
- ✅ **Fixed:** Now uses `NEXT_PUBLIC_BEDROCK_PROXY_URL` and `NEXT_PUBLIC_BEDROCK_MODEL_ID`

**`agent-frontend/src/lib/mockApi.ts`**
- ❌ WebSocket URL fallback: `ws://localhost:8000/chat`
- ✅ **Fixed:** Removed fallback, now requires `NEXT_PUBLIC_WS_URL`

**`agent-frontend/src/components/chat/ChatInput.tsx`**
- ❌ Forensic WebSocket URL: `ws://localhost:6060`
- ✅ **Fixed:** Now uses `NEXT_PUBLIC_FORENSIC_WS_URL`

**`agent-frontend/src/lib/forensicApi.ts`**
- ❌ Default WebSocket URL: `ws://localhost:6060`
- ✅ **Fixed:** Removed default, URL now required in constructor

**`agent-frontend/src/components/layout/Header.tsx`**
- ❌ Logo URL: `https://cu-2.com/wp-content/uploads/2022/09/hyperverge-logo.png`
- ✅ **Fixed:** Now uses `NEXT_PUBLIC_LOGO_URL` with fallback to `/logo.png`

### 3. Removed Fallback Values ❌ MEDIUM

All configuration files previously had fallback values that could mask missing environment variables:

#### Removed Fallbacks:
- `OPENAI_API_KEY` - No longer defaults to empty string
- `OPENAI_MODEL` - No longer defaults to a specific model
- `BEDROCK_PROXY_URL` - No longer has hardcoded fallback
- `BEDROCK_MODEL_ID` - No longer has hardcoded fallback
- `EMBEDDING_URL` - No longer has hardcoded IP address fallback
- `EMBEDDING_MODEL` - No longer has hardcoded fallback
- `QDRANT_HOST` - No longer defaults to localhost or IP addresses
- `QDRANT_COLLECTION` - No longer has hardcoded fallback
- `GEMINI_MODEL` - No longer has hardcoded fallback
- `GEMINI_PROJECT` - No longer has hardcoded fallback
- `GEMINI_LOCATION` - No longer has hardcoded fallback
- `LANGSMITH_ENDPOINT` - No longer has hardcoded fallback
- `LANGSMITH_API_KEY` - No longer defaults to empty string
- `LANGSMITH_PROJECT` - No longer has hardcoded fallback

#### Kept Reasonable Defaults (Numeric Values Only):
- `BEDROCK_MAX_GEN_LEN` - Defaults to `2048` (reasonable default)
- `EMBEDDING_DIM` - Defaults to `1024` (reasonable default)
- `QDRANT_PORT` - Defaults to `6333` (standard Qdrant port)
- `WS_PORT` - Defaults to `6060` (reasonable default)
- `MAX_CHUNK_TOKENS` - Defaults to `600` (reasonable default)
- `CHUNK_OVERLAP_TOKENS` - Defaults to `100` (reasonable default)
- `MAX_PARALLEL_PDFS` - Defaults to `2` (reasonable default)
- `MAX_PARALLEL_EMBEDDINGS` - Defaults to `3` (reasonable default)
- `TOP_K` - Defaults to `10` (reasonable default)
- `TOP_K_HNSW` - Defaults to `50` (reasonable default)
- `MAX_TOOL_CALLS` - Defaults to `5` (reasonable default)

### 4. Validation Added ✅

All critical configuration values now raise `ValueError` if not provided:

```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
```

This ensures the application fails fast at startup if critical configuration is missing.

## Files Modified

### Backend
1. `backend/agent_system/config.py`
2. `backend/forensic_engine/config.py`
3. `backend/data_ingestion_pipeline/config.py`
4. `backend/data_ingestion_pipeline/app.py`
5. `script/check_openai_credentials.py`

### Frontend
1. `agent-frontend/src/lib/summarize.ts`
2. `agent-frontend/src/lib/mockApi.ts`
3. `agent-frontend/src/components/chat/ChatInput.tsx`
4. `agent-frontend/src/lib/forensicApi.ts`
5. `agent-frontend/src/components/layout/Header.tsx`
6. `agent-frontend/.env.example`

## Required Environment Variables

### Backend (`backend/agent_system/.env`)
```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=your-openai-model

# Bedrock
BEDROCK_PROXY_URL=https://your-bedrock-url.lambda-url.region.on.aws/
BEDROCK_MODEL_ID=your-bedrock-model-id

# Embedding
EMBEDDING_URL=http://your-embedding-server:1234/v1/embeddings
EMBEDDING_MODEL=your-embedding-model

# Qdrant
QDRANT_HOST=your-qdrant-host
QDRANT_COLLECTION=your-collection-name

# LangSmith (Optional)
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=your-project-name

# Gemini (Optional)
GEMINI_MODEL=your-gemini-model
GEMINI_PROJECT=your-gcp-project
GEMINI_LOCATION=your-gcp-location
GEMINI_CREDENTIALS_FILE=/path/to/credentials.json
```

### Frontend (`agent-frontend/.env.local`)
```bash
# API Configuration (REQUIRED)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/chat
NEXT_PUBLIC_FORENSIC_WS_URL=ws://localhost:6060

# Bedrock Configuration (REQUIRED)
NEXT_PUBLIC_BEDROCK_PROXY_URL=https://your-bedrock-url.lambda-url.region.on.aws/
NEXT_PUBLIC_BEDROCK_MODEL_ID=us.meta.llama4-maverick-17b-instruct-v1:0

# Logo URL (Optional)
NEXT_PUBLIC_LOGO_URL=https://your-logo-url.com/logo.png
```

## Security Recommendations

1. ✅ **Never commit `.env` files** - Already in `.gitignore`
2. ✅ **Use environment-specific configuration** - Separate `.env` files for dev/staging/prod
3. ✅ **Rotate exposed API keys immediately** - The hardcoded OpenAI key should be revoked
4. ✅ **Use secrets management** - Consider AWS Secrets Manager, HashiCorp Vault, or similar
5. ✅ **Fail fast on missing config** - Application now raises errors on startup if critical config is missing
6. ⚠️ **Review AWS Lambda URL** - The exposed Bedrock proxy URL should be rotated if sensitive

## Testing Checklist

- [ ] Backend services start successfully with proper `.env` configuration
- [ ] Frontend builds and runs with proper environment variables
- [ ] Application fails gracefully with clear error messages when env vars are missing
- [ ] No hardcoded credentials remain in the codebase
- [ ] All API calls use environment-configured URLs
- [ ] Documentation updated with new environment variable requirements

## Next Steps

1. Create proper `.env` files for all environments (dev, staging, production)
2. Revoke and rotate the exposed OpenAI API key
3. Consider rotating the AWS Lambda Bedrock proxy URL
4. Update deployment documentation with new environment variable requirements
5. Set up secrets management for production deployments
6. Add pre-commit hooks to prevent accidental credential commits

---

**Audited by:** AI Assistant  
**Review Status:** Ready for human review and deployment
