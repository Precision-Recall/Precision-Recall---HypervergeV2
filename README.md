# Hyperverge Financial Analysis System

A multi-agent financial analysis system with forensic capabilities for analyzing SEC filings and financial documents.

## Security & Configuration

**⚠️ IMPORTANT:** This is a fresh repository created after a security incident in the previous repo, where credentials were accidentally committed to git history. All hardcoded credentials and URLs have been removed, and all sensitive configuration now requires environment variables. 

## Quick Start

### Backend Setup

1. Create environment file:
```bash
cd backend/agent_system
cp .env.example .env
```

2. Configure required environment variables in `.env`:
```bash
# OpenAI (REQUIRED)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-5-nano-2025-08-07

# Bedrock (REQUIRED)
BEDROCK_PROXY_URL=https://your-bedrock-url.lambda-url.region.on.aws/
BEDROCK_MODEL_ID=us.meta.llama4-scout-17b-instruct-v1:0

# Embedding (REQUIRED)
EMBEDDING_URL=http://your-embedding-server:1234/v1/embeddings
EMBEDDING_MODEL=text-embedding-bge-m3

# Qdrant (REQUIRED)
QDRANT_HOST=your-qdrant-host
QDRANT_COLLECTION=your-collection-name
```

3. Install and run:
```bash
pip install -r requirements.txt
python app.py
```

### Frontend Setup

1. Create environment file:
```bash
cd agent-frontend
cp .env.example .env.local
```

2. Configure required environment variables in `.env.local`:
```bash
# API Configuration (REQUIRED)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/chat
NEXT_PUBLIC_FORENSIC_WS_URL=ws://localhost:6060

# Bedrock Configuration (REQUIRED)
NEXT_PUBLIC_BEDROCK_PROXY_URL=https://your-bedrock-url.lambda-url.region.on.aws/
NEXT_PUBLIC_BEDROCK_MODEL_ID=us.meta.llama4-maverick-17b-instruct-v1:0
```

3. Install and run:
```bash
npm install
npm run dev
```

## Architecture

### Backend Services
- **Agent System** (`backend/agent_system/`) - Multi-agent orchestration with LangGraph
- **Forensic Engine** (`backend/forensic_engine/`) - Specialized forensic analysis agents
- **Data Ingestion Pipeline** (`backend/data_ingestion_pipeline/`) - PDF processing and vector storage

### Frontend
- **Next.js Application** (`agent-frontend/`) - Modern React-based UI with real-time WebSocket streaming

## Features

- Multi-agent financial analysis
- Real-time streaming responses via WebSocket
- Forensic analysis modes:
  - Promise vs Reality analysis
  - Anomaly detection
  - Sentiment divergence analysis
- Vector-based document retrieval with Qdrant
- Personalized summaries with user context

## Environment Variables Reference

See [SECURITY_AUDIT_REPORT.md](./SECURITY_AUDIT_REPORT.md) for complete list of required and optional environment variables.

## Security Notes

- ✅ No hardcoded credentials or API keys
- ✅ No hardcoded URLs (except reasonable defaults for ports)
- ✅ Fail-fast validation for missing critical configuration
- ✅ All sensitive values must be provided via environment variables
- ⚠️ Never commit `.env` or `.env.local` files to version control

## Documentation

- [Security Audit Report](./SECURITY_AUDIT_REPORT.md) - Complete security audit and configuration guide
- [Frontend Setup](./agent-frontend/SETUP.md) - Detailed frontend setup instructions
- [Forensic Engine Guide](./backend/forensic_engine/QUICKSTART.md) - Forensic analysis quickstart

## License

Proprietary - Hyperverge
# Precision-Recall---HypervergeV2
