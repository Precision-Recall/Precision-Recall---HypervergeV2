# Frontend-Backend Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (Next.js Frontend)                      │
│                   localhost:3000                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Mode Selection
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────────┐
│ General Mode  │         │ Forensic Mode    │
│ (Mock API)    │         │ (WebSocket)      │
│ Port: 3000    │         │ Port: 6060       │
└───────────────┘         └────────┬─────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Forensic Engine │
                          │ (Python WS)     │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Qdrant Vector DB│
                          │ Port: 6333      │
                          └─────────────────┘
```

## Complete Setup

### Step 1: Start Qdrant

```bash
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
```

Verify: http://localhost:6333/dashboard

### Step 2: Start Forensic WebSocket Server

```bash
cd backend/forensic_engine
pip install -r requirements.txt
python websocket_server.py
```

Server listens on: **ws://localhost:6060**

### Step 3: Start Frontend

```bash
cd agent-frontend
npm install --legacy-peer-deps
npm run dev
```

Frontend available at: **http://localhost:3000**

## User Flow

### 1. User Opens Application

- Sees welcome screen with mode selector
- Two options:
  - **General Assistant** (default)
  - **Forensic Engine**

### 2. User Selects Mode

#### General Mode
- Uses mock API
- Shows portfolio analysis, market insights
- No external server needed

#### Forensic Mode
- Connects to WebSocket on port 6060
- Shows forensic-specific suggestions:
  - Promise vs. Reality
  - Anomaly Detection
  - Sentiment Divergence

### 3. User Sends Query

**Example**: "Did TSLA deliver on their 2018 renewable energy promise by 2023?"

#### Frontend Processing
1. Parses query → extracts company, years, mode
2. Sends to WebSocket server
3. Receives streaming events
4. Updates UI in real-time

#### Backend Processing
1. Receives query via WebSocket
2. Starts agents (Planner → Extractor → Analyzer → Synthesizer)
3. Calls Qdrant with filtered search
4. Streams events back to frontend
5. Generates final report

### 4. User Sees Results

- **Left Panel**: Chat with streaming response
- **Right Panel**: Agent execution timeline
  - Agent cards
  - Tool calls (qdrant_search)
  - Reasoning steps
  - Evidence chunks

## Mode Selection Implementation

### Frontend (Mode Selector)

```tsx
// src/components/layout/ModeSelector.tsx
<button onClick={() => setAgentMode('general')}>
  General Assistant
</button>
<button onClick={() => setAgentMode('forensic')}>
  Forensic Engine
</button>
```

### State Management

```typescript
// src/store/chatStore.ts
interface ChatState {
  agentMode: 'general' | 'forensic';
  setAgentMode: (mode: AgentMode) => void;
}
```

### Automatic Routing

```typescript
// src/components/chat/ChatInput.tsx
if (agentMode === 'forensic') {
  // Connect to ws://localhost:6060
  forensicClient.sendQuery(mode, params);
} else {
  // Use mock API
  streamChatResponse(message);
}
```

## Query Parsing

### Natural Language → Structured Params

```typescript
// Input: "Did TSLA deliver on their 2018 renewable energy promise by 2023?"

// Parsed to:
{
  mode: 'promise_vs_reality',
  params: {
    company: 'TSLA',
    promise_year: 2018,
    verification_year: 2023,
    lens: 'environment',
    promise_query: 'renewable energy promise'
  }
}
```

### Parser Logic

```typescript
// src/lib/forensicQueryParser.ts
export function parseForensicQuery(query: string) {
  // 1. Detect mode (promise, anomaly, sentiment)
  // 2. Extract company ticker
  // 3. Extract years
  // 4. Detect lens (finance, environment, strategy, governance)
  // 5. Return structured params
}
```

## Event Handling

### Frontend Event Handler

```typescript
const handleEvent = (event: ForensicEvent) => {
  switch (event.type) {
    case 'agent_start':
      // Show agent card in timeline
      break;
    case 'tool_call':
      // Show tool invocation
      break;
    case 'token_stream':
      // Append token to streaming text
      break;
    case 'agent_complete':
      // Mark agent as complete
      break;
  }
};
```

### Backend Event Emitter

```python
async def send_event(websocket, event_type, data):
    message = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    await websocket.send(json.dumps(message))
```

## Data Flow Example

### Promise vs. Reality Query

**User Query**: "Did TSLA deliver on their 2018 renewable energy promise?"

**Frontend**:
1. User selects "Forensic Engine" mode
2. Types query
3. Parser extracts: TSLA, 2018, 2023, environment, promise
4. Sends via WebSocket to port 6060

**Backend**:
1. Receives query
2. Starts "Forensic Query Planner" agent
3. Sends reasoning: "Analyzing promise tracking"
4. Starts "Promise Extractor" agent
5. Calls Qdrant with filter:
   ```python
   Filter(must=[
       FieldCondition(key="company", match=MatchValue(value="TSLA")),
       FieldCondition(key="section_item", match=MatchValue(value="7")),
       FieldCondition(key="year", match=MatchValue(value=2018))
   ])
   ```
6. Sends tool_call and tool_complete events
7. Starts "Verification Analyzer" agent
8. Searches 2023 MD&A for verification
9. Analyzes promise delivery
10. Streams final report token by token

**Frontend Display**:
- Left: Streaming response with evidence
- Right: Timeline showing all 4 agents, 2 tool calls, reasoning steps

## Configuration

### Environment Variables

**Backend** (`.env`):
```env
QDRANT_HOST=localhost
QDRANT_PORT=6333
WS_HOST=localhost
WS_PORT=6060
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_FORENSIC_WS_URL=ws://localhost:6060
```

## Testing Checklist

### Backend
- [ ] Qdrant running on 6333
- [ ] WebSocket server running on 6060
- [ ] Can connect with websocat
- [ ] Events stream correctly
- [ ] Error handling works

### Frontend
- [ ] Mode selector appears
- [ ] Can switch between modes
- [ ] WebSocket connects in forensic mode
- [ ] Events display in timeline
- [ ] Streaming works
- [ ] Error messages show

### Integration
- [ ] Query parsing works
- [ ] Events flow end-to-end
- [ ] Timeline updates in real-time
- [ ] Final response streams
- [ ] Can export session

## Deployment

### Development
```bash
# Terminal 1: Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Terminal 2: Forensic Server
cd backend/forensic_engine
python websocket_server.py

# Terminal 3: Frontend
cd agent-frontend
npm run dev
```

### Production
```bash
# Use Docker Compose
docker-compose up -d

# Or use process manager
pm2 start websocket_server.py --name forensic-ws
pm2 start "npm start" --name frontend
```

## Summary

This integration provides:

✅ **Mode selection** in UI (General | Forensic)
✅ **WebSocket on port 6060** for forensic engine
✅ **Automatic routing** based on mode
✅ **Natural language parsing** of queries
✅ **Real-time streaming** of agent execution
✅ **Event-driven architecture** matching frontend
✅ **Production-ready** with error handling

**All three detection modes work seamlessly through the UI!**
