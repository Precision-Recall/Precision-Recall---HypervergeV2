# Financial Intelligence Platform

A production-grade multi-agent AI system for deep financial analysis of SEC filings (10-K, 10-Q, 8-K, earnings reports) with real-time forensic accounting capabilities.

## Overview

This platform combines advanced AI agents with vector search and forensic analysis to provide comprehensive insights into corporate financial disclosures. It features a multi-agent orchestration system that intelligently routes queries between temporal analysis and cross-company comparisons.

**Supported SEC Filings:**
- **10-K**: Annual reports with comprehensive financial statements and business overviews
- **10-Q**: Quarterly reports with unaudited financial statements
- **8-K**: Current reports for material events (acquisitions, CEO changes, bankruptcy, etc.)
- **Earnings Reports**: Quarterly and annual earnings releases

## Key Features

- **Multi-Agent Orchestration**: Intelligent routing between Temporal Reasoner and Cross-Entity agents
- **Forensic Analysis Engine**: Three detection modes for corporate accountability
  - Promise vs. Reality: Track commitments across years
  - Anomaly Detection: Flag significant changes in risk disclosures
  - Sentiment Divergence: Detect contradictions between optimistic narratives and footnotes
- **Real-Time Streaming**: WebSocket-based agent execution visualization
- **Advanced RAG**: Section-aware retrieval with BGE-M3 embeddings, Qdrant vector database, and metadata filtering
- **Multi-Filing Support**: Process 10-K, 10-Q, 8-K, and earnings reports with automatic document type detection
- **Production Frontend**: Next.js 14 interface with live agent timeline and reasoning traces

## Architecture

### Backend Stack

- **Orchestration LLM**: OpenAI GPT-5 Nano (Gateway & Agent Coordination)
- **Inner Agent LLM**: Llama 4 Scout 17B via AWS Bedrock Proxy
- **Vector Database**: Qdrant with payload filtering and HNSW indexing
- **Embeddings**: BGE-M3 (1024-dim) via LM Studio
- **Document Processing**: MinerU for multi-modal PDF extraction (text, tables, images) with Llama-powered image captioning
- **Storage**: AWS S3 for extracted images
- **Communication**: WebSocket on port 6060 for real-time streaming

### Frontend Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Animations**: Framer Motion
- **Real-Time**: WebSocket streaming with SSE support

## Project Structure

```
.
├── agent-frontend/          # Next.js frontend application
│   ├── src/
│   │   ├── components/      # UI components (chat, execution, layout)
│   │   ├── lib/            # API clients and utilities
│   │   ├── store/          # Zustand state management
│   │   └── types/          # TypeScript definitions
│   └── package.json
│
├── backend/
│   ├── agent_system/       # Multi-agent orchestration
│   │   ├── agents/         # Temporal Reasoner & Cross-Entity agents
│   │   ├── tools/          # Agent tools (temporal & cross-entity)
│   │   ├── skills/         # Agent skill definitions
│   │   ├── retriever/      # Vector search & reranking
│   │   ├── llm/           # LLM clients (OpenAI, Bedrock)
│   │   └── ws_server.py   # WebSocket server
│   │
│   ├── forensic_engine/    # Forensic analysis system
│   │   ├── agent.py        # Forensic detector agent
│   │   ├── skills/         # Detection mode skills
│   │   └── websocket_server.py  # WS server (port 6060)
│   │
│   └── data_ingestion_pipeline/  # ETL pipeline
│       ├── extractor.py    # MinerU PDF extraction
│       ├── chunker.py      # Section-aware chunking
│       ├── bedrock_client.py  # Image captioning
│       └── vector_store.py # Qdrant operations
│
└── README.md
```

## Quick Start

### Prerequisites

- **Node.js**: 18+ (for frontend)
- **Python**: 3.9+ (for backend)
- **Docker**: For Qdrant vector database
- **AWS Account**: For Bedrock API access
- **OpenAI API Key**: For orchestration LLM

### Environment Setup

Create `.env` files in both frontend and backend directories:

**Backend `.env`:**
```bash
# OpenAI (Orchestration)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-nano

# Bedrock Proxy (Inner Agents)
BEDROCK_PROXY_URL=http://localhost:8080/v1
BEDROCK_MODEL_ID=us.meta.llama4-scout-17b-v1:0
BEDROCK_MAX_GEN_LEN=2048

# BGE-M3 Embedding (LM Studio)
EMBEDDING_URL=http://localhost:1234/v1
EMBEDDING_MODEL=bge-m3
EMBEDDING_DIM=1024

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=TEST2

# Retriever Settings
TOP_K_HNSW=50
MAX_TOOL_CALLS=5

# LangSmith Tracing (Optional)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=financial-analysis
```

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_WS_URL=ws://localhost:6060
```

### Installation & Startup

#### 1. Start Qdrant Vector Database

```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

#### 2. Setup Backend

```bash
cd backend/agent_system
pip install -r requirements.txt

# Start WebSocket server
python ws_server.py
```

**Forensic Engine (Optional):**
```bash
cd backend/forensic_engine
pip install -r requirements.txt

# Start forensic WebSocket server (port 6060)
python websocket_server.py
```

#### 3. Setup Frontend

```bash
cd agent-frontend
npm install --legacy-peer-deps

# Development mode
npm run dev

# Production build
npm run build
npm start
```

Access the application at `http://localhost:3000`

## Data Ingestion

The pipeline supports multiple SEC filing types with intelligent filename parsing:

**Filename Format:**
```
COMPANY_YEAR_FORMTYPE.pdf        # Annual: 3M_2018_10K.pdf
COMPANY_YEARQN_FORMTYPE.pdf      # Quarterly: TSLA_2023Q2_10Q.pdf
COMPANY_YEAR_8K.pdf              # Current: AAPL_2024_8K.pdf
COMPANY_YEAR_EARNINGS.pdf        # Earnings: MSFT_2023_EARNINGS.pdf
```

**Supported Form Types:**
- `10K` → Annual reports (document_type: annual_report)
- `10Q` → Quarterly reports (document_type: quarterly_report)
- `8K` → Current reports (document_type: current_report)
- `EARNINGS` → Earnings releases (document_type: earnings)

### Running the Pipeline

```bash
cd backend/data_ingestion_pipeline
pip install -r requirements.txt

# Process single PDF
python main.py /path/to/3M_2018_10K.pdf

# Process entire folder
python main.py /path/to/pdf/folder

# Limit pages for testing
python main.py /path/to/pdfs --max-pages 10
```

**Pipeline Steps:**
1. **Filename Parsing**: Extract company, year, quarter, form_type from filename
2. **PDF Extraction**: Use MinerU to extract text, tables, and images
3. **Section Detection**: Identify 10-K/10-Q sections (Item 1, 1A, 7, 7A, 8, 9A, 13, etc.)
4. **Smart Chunking**: 
   - Text: Recursive chunking with paragraph boundaries (overlap support)
   - Tables: Convert HTML to narrative text, preserve raw HTML
   - Images: Extract as separate chunks for captioning
5. **Image Captioning**: Generate captions using Llama via Bedrock
6. **S3 Upload**: Store images in S3 with folder structure by PDF name
7. **Embedding**: Generate 1024-dim BGE-M3 vectors
8. **Vector Store**: Upload to Qdrant with rich metadata:
   - Company, year, quarter, form_type, document_type
   - Section name, section_item (e.g., "Item 1A")
   - Page number, chunk type (text/table/figure)
   - Previous/next chunk IDs for context linking

## Agent System

### Temporal Reasoner Agent

Handles single-company, multi-year analysis.

**Tools:**
- `year_range_retriever`: Fetch data across year ranges
- `metric_trend_extractor`: Extract and analyze metric trends
- `narrative_diff_tool`: Compare narrative changes over time
- `timeline_synthesizer`: Create temporal summaries
- `quarter_drill_down`: Deep-dive into specific quarters
- `pivot_detector`: Identify strategic pivots

### Cross-Entity Agent

Handles multi-company comparisons.

**Tools:**
- `multi_company_retriever`: Fetch data from multiple companies
- `metric_comparator`: Compare metrics across companies
- `terminology_normalizer`: Standardize metric terminology
- `sector_peer_finder`: Identify industry peers
- `cross_temporal_benchmarker`: Benchmark across time and companies

### Forensic Engine

Specialized agent for corporate accountability analysis.

**Detection Modes:**
1. **Promise vs. Reality**: Track CEO commitments across years
2. **Anomaly Detection**: Flag risk disclosure changes
3. **Sentiment Divergence**: Detect MD&A vs. footnote contradictions

See `backend/forensic_engine/README.md` for detailed API documentation.

## API Documentation

See `agent-frontend/API.md` for complete WebSocket event specifications and payload formats.

## Development

### Running Tests

```bash
# Backend load test
cd backend
python load_test.py

# Frontend linting
cd agent-frontend
npm run lint
```

### Adding New Agent Skills

1. Create `SKILL.md` in `backend/agent_system/skills/your-skill/`
2. Implement tool in `backend/agent_system/tools/`
3. Register tool in agent configuration
4. Update agent prompts to use new skill

See `backend/agent_system/skills/*/SKILL.md` for examples.

## Production Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
  
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    depends_on:
      - qdrant
    environment:
      - QDRANT_HOST=qdrant
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - BEDROCK_PROXY_URL=${BEDROCK_PROXY_URL}
  
  frontend:
    build: ./agent-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  qdrant_data:
```

### Environment Variables

All configuration is managed through environment variables. Never hardcode API keys or URLs.

## Performance

- **Retrieval Speed**: <100ms for HNSW search with payload filtering
- **Agent Response**: 2-5s for simple queries, 10-30s for complex analysis
- **Concurrent Users**: Supports 100+ via WebSocket connection pooling
- **Vector Database**: Handles 1M+ chunks efficiently

## License

MIT

## Support

For issues or questions, please open an issue in the repository.

---

**Note**: This is a complex multi-agent system. Start with the Quick Start guide and refer to component-specific READMEs for detailed documentation.
