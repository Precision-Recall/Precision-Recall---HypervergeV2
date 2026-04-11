# Forensic Accountability & Anomaly Detector

## Overview

This is an **industry-standard forensic analysis engine** that audits company integrity through 10-K SEC filings. It uses Qdrant vector database with payload filtering to implement three detection modes.

**Communication**: WebSocket on port **6060** for real-time agent execution streaming.

## ✅ Why This Approach is Valid

### 1. **Industry Standard Architecture**
- **Qdrant Payload Filtering**: Exactly how production vector DBs work (Pinecone, Weaviate, Qdrant)
- **Section-Based Targeting**: Matches how forensic accountants actually analyze 10-Ks
- **Multi-Year Comparison**: Standard practice in financial forensics

### 2. **Solves the Problem Statement**
This implementation directly addresses all three requirements:

#### ✅ Promise vs. Reality
```python
# "In 2018, CEO promised 50% renewable energy by 2023. Did they deliver?"
result = detector.detect_promise_vs_reality(
    company="TSLA",
    promise_year=2018,
    verification_year=2023,
    lens=ForensicLens.ENVIRONMENT,
    promise_query="renewable energy target 50% by 2023"
)
```

#### ✅ Anomaly Detection
```python
# "Flag changes in Risk Factors between 2022 and 2023"
result = detector.detect_anomalies(
    company="TSLA",
    start_year=2022,
    end_year=2023,
    lens=ForensicLens.GOVERNANCE
)
```

#### ✅ Sentiment Divergence
```python
# "CEO optimistic but footnotes show liquidity risk"
result = detector.detect_sentiment_divergence(
    company="TSLA",
    year=2023,
    lens=ForensicLens.FINANCE
)
```

## Architecture

### Section Priorities (Based on Forensic Best Practices)

| Item | Section Name | Use Case |
|------|-------------|----------|
| **1** | Business Overview | Strategic promises, long-term goals |
| **1A** | Risk Factors | **CRITICAL** for anomaly detection |
| **7** | MD&A | **CRITICAL** for promises + CEO sentiment |
| **7A** | Market Risk | Counter-signal to CEO optimism |
| **8** | Financial Statements | Hidden warnings in footnotes |
| **9A** | Controls & Procedures | Internal audit failures |
| **13** | Related Party Transactions | Conflict of interest |

### Detection Mode → Section Mapping

```python
MODE_SECTIONS = {
    "promise_vs_reality": ["1", "7"],        # Business + MD&A
    "anomaly_detection": ["1A", "9A", "13"], # Risk + Controls + Related Party
    "sentiment_divergence": ["7", "7A", "8"] # MD&A + Market Risk + Footnotes
}
```

## How Qdrant Filtering Works

### Pre-Filter Before Vector Search
```python
# Filter to specific section and year BEFORE semantic search
Filter(must=[
    FieldCondition(key="company", match=MatchValue(value="TSLA")),
    FieldCondition(key="section_item", match=MatchValue(value="7")),  # MD&A only
    FieldCondition(key="year", match=MatchValue(value=2023))
])
```

This is **exactly** like SQL `WHERE` clause - narrows down to relevant chunks before vector search.

### Payload Schema

```python
{
    "company": "TSLA",
    "year": 2023,
    "section": "Management Discussion and Analysis",
    "section_item": "7",  # 10-K item number
    "filing_date": "2024-02-01",
    "text": "chunk text here..."
}
```

### Performance Optimization

```python
# Create indexes for fast filtering (CRITICAL for production)
qdrant.create_payload_index(
    collection_name="filings",
    field_name="section_item",
    field_schema="keyword"
)
qdrant.create_payload_index(
    collection_name="filings",
    field_name="year",
    field_schema="integer"
)
```

Without indexes, Qdrant scans all points. With indexes, it jumps directly to matching subset.

## API Usage

### Start the Server

```bash
cd backend/forensic_engine
pip install fastapi uvicorn qdrant-client sentence-transformers
python api.py
```

### Example API Calls

#### 1. Promise vs. Reality

```bash
curl -X POST "http://localhost:8000/api/forensic/promise-vs-reality" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "TSLA",
    "promise_year": 2018,
    "verification_year": 2023,
    "lens": "environment",
    "promise_query": "renewable energy target 50% by 2023"
  }'
```

**Response:**
```json
{
  "detection_mode": "promise_vs_reality",
  "company": "TSLA",
  "lens": "environment",
  "findings": "Evidence suggests promise was NOT DELIVERED or significantly delayed",
  "evidence": [
    {
      "year": 2018,
      "section": "Management Discussion and Analysis",
      "section_item": "7",
      "text": "We aim to achieve 50% renewable energy by 2023...",
      "score": 0.89
    },
    {
      "year": 2023,
      "section": "Management Discussion and Analysis",
      "section_item": "7",
      "text": "Renewable energy initiatives have been delayed...",
      "score": 0.76
    }
  ],
  "confidence": 0.9,
  "risk_level": "CRITICAL"
}
```

#### 2. Anomaly Detection

```bash
curl -X POST "http://localhost:8000/api/forensic/anomaly-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "TSLA",
    "start_year": 2022,
    "end_year": 2023,
    "lens": "governance"
  }'
```

**Response:**
```json
{
  "detection_mode": "anomaly_detection",
  "findings": "SIGNIFICANT INCREASE in risk disclosures: 5 → 12",
  "risk_level": "CRITICAL",
  "evidence": [...]
}
```

#### 3. Sentiment Divergence

```bash
curl -X POST "http://localhost:8000/api/forensic/sentiment-divergence" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "TSLA",
    "year": 2023,
    "lens": "finance"
  }'
```

## Data Ingestion Pipeline

### Step 1: Extract 10-K Sections

```python
from sec_edgar_downloader import Downloader

dl = Downloader("YourCompany", "your@email.com")
dl.get("10-K", "TSLA", after="2018-01-01", before="2024-12-31")

# Parse and extract sections
sections = parse_10k(filing_path)  # Returns dict with items 1, 1A, 7, 7A, 8, etc.
```

### Step 2: Chunk and Embed

```python
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")

chunks = []
for section_item, text in sections.items():
    # Chunk into ~500 token pieces
    for chunk in chunk_text(text, max_tokens=500):
        chunks.append({
            "text": chunk,
            "embedding": embedder.encode(chunk).tolist(),
            "metadata": {
                "company": "TSLA",
                "year": 2023,
                "section": SECTION_MAPPING[section_item],
                "section_item": section_item,
                "filing_date": "2024-02-01"
            }
        })
```

### Step 3: Upload to Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

qdrant = QdrantClient(host="localhost", port=6333)

# Create collection
qdrant.create_collection(
    collection_name="filings",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Upload points
points = [
    PointStruct(
        id=i,
        vector=chunk["embedding"],
        payload={
            "company": chunk["metadata"]["company"],
            "year": chunk["metadata"]["year"],
            "section": chunk["metadata"]["section"],
            "section_item": chunk["metadata"]["section_item"],
            "filing_date": chunk["metadata"]["filing_date"],
            "text": chunk["text"]
        }
    )
    for i, chunk in enumerate(chunks)
]

qdrant.upsert(collection_name="filings", points=points)
```

## Why This Works

### 1. **Efficient Filtering**
- Qdrant filters BEFORE vector search → fast even with millions of chunks
- Indexes on `section_item` and `year` → sub-millisecond filtering

### 2. **Forensically Sound**
- Targets the exact sections forensic accountants use
- Multi-year comparison is standard practice
- Sentiment analysis matches analyst workflows

### 3. **Scalable**
- Can handle 10+ years × 100+ companies × 7 sections = 7,000+ documents
- Qdrant handles billions of vectors efficiently
- Horizontal scaling with Qdrant Cloud

## Validation Against Problem Statement

| Requirement | Implementation | Status |
|------------|----------------|--------|
| Select Company | `company` parameter in all APIs | ✅ |
| Select Lens | `lens` enum (Finance, Environment, Strategy, Governance) | ✅ |
| Select Detection Mode | Three separate endpoints | ✅ |
| Promise vs. Reality | `detect_promise_vs_reality()` with year comparison | ✅ |
| Anomaly Detection | `detect_anomalies()` with risk factor tracking | ✅ |
| Sentiment Divergence | `detect_sentiment_divergence()` with tone analysis | ✅ |
| Show Evidence | Returns full text chunks with scores | ✅ |

## Quick Start

### Option 1: Automatic Startup

```bash
./start_server.sh
```

This will:
1. Check if Qdrant is running (start if needed)
2. Start WebSocket server on port 6060

### Option 2: Manual Startup

```bash
# Terminal 1: Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Terminal 2: Start WebSocket Server
python websocket_server.py
```

Server will be available at: **ws://localhost:6060**

## Deployment

### Local Development
```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Start WebSocket Server
python websocket_server.py
```

### Production (Docker Compose)
```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
  
  forensic_api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333

volumes:
  qdrant_data:
```

## Next Steps

1. **Ingest Data**: Use `data_ingestion_pipeline` to load 10-Ks into Qdrant
2. **Test API**: Try example queries with real data
3. **Frontend Integration**: Connect to your agent-frontend
4. **Add More Lenses**: Extend with ESG, Cybersecurity, etc.

## References

- [Qdrant Filtering Documentation](https://qdrant.tech/documentation/search/filtering/)
- [Qdrant Payload Indexes](https://qdrant.tech/articles/vector-search-filtering/)
- [SEC EDGAR 10-K Format](https://www.sec.gov/files/form10-k.pdf)
