# API Documentation

## Overview

This document describes the API integration for the Agentic Finance frontend. The application expects a streaming API that sends execution events in real-time.

## Connection Methods

### Option 1: Server-Sent Events (SSE)

Recommended for one-way streaming from server to client.

```typescript
const eventSource = new EventSource('/api/chat/stream');

eventSource.onmessage = (event) => {
  const executionEvent = JSON.parse(event.data);
  handleExecutionEvent(executionEvent);
};
```

### Option 2: WebSocket

Recommended for bidirectional communication.

```typescript
const ws = new WebSocket('ws://localhost:8000/chat');

ws.onmessage = (event) => {
  const executionEvent = JSON.parse(event.data);
  handleExecutionEvent(executionEvent);
};

ws.send(JSON.stringify({ message: userInput }));
```

## Event Types

### 1. Agent Start

Triggered when an agent begins execution.

```json
{
  "type": "agent_start",
  "agent": "Portfolio Analyzer",
  "data": {
    "type": "analyzer",
    "description": "Analyzing portfolio holdings"
  },
  "timestamp": "2026-04-10T10:30:00.000Z"
}
```

### 2. Agent Complete

Triggered when an agent finishes execution.

```json
{
  "type": "agent_complete",
  "agent": "Portfolio Analyzer",
  "data": {
    "output": "Portfolio analysis complete",
    "executionTime": 1500
  },
  "timestamp": "2026-04-10T10:30:01.500Z"
}
```

### 3. Tool Call

Triggered when an agent invokes a tool.

```json
{
  "type": "tool_call",
  "tool": "stock_api",
  "data": {
    "input": {
      "symbols": ["AAPL", "GOOGL"],
      "timeframe": "1Y"
    }
  },
  "timestamp": "2026-04-10T10:30:00.500Z"
}
```

### 4. Tool Complete

Triggered when a tool call finishes.

```json
{
  "type": "tool_complete",
  "tool": "stock_api",
  "data": {
    "output": {
      "AAPL": { "price": 178.45, "change": 2.3 },
      "GOOGL": { "price": 142.67, "change": -0.8 }
    },
    "executionTime": 800
  },
  "timestamp": "2026-04-10T10:30:01.300Z"
}
```

### 5. Reasoning Step

Triggered when an agent generates a reasoning step.

```json
{
  "type": "reasoning",
  "data": {
    "type": "intent",
    "description": "Detected user intent: Financial analysis query"
  },
  "timestamp": "2026-04-10T10:30:00.200Z"
}
```

**Reasoning Types:**
- `intent`: User intent detection
- `planning`: Execution planning
- `tool_call`: Tool invocation reasoning
- `synthesis`: Result combination

### 6. Token Stream

Triggered for each token in the final response.

```json
{
  "type": "token_stream",
  "token": "Based on your portfolio ",
  "timestamp": "2026-04-10T10:30:02.000Z"
}
```

### 7. Error

Triggered when an error occurs.

```json
{
  "type": "error",
  "data": {
    "message": "Failed to fetch stock data",
    "code": "API_ERROR"
  },
  "timestamp": "2026-04-10T10:30:01.000Z"
}
```

## Request Format

### POST /api/chat

Send a user message to initiate agent execution.

**Request:**
```json
{
  "message": "What's my portfolio performance?",
  "sessionId": "optional-session-id"
}
```

**Response:**
Streaming events as described above.

## Integration Example

### Complete Integration

```typescript
import { useChatStore } from '@/store/chatStore';

async function sendMessage(message: string) {
  const { addMessage, handleExecutionEvent, finalizeStreamingMessage, setLoading } = useChatStore.getState();
  
  // Add user message
  addMessage({ role: 'user', content: message });
  setLoading(true);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const event = JSON.parse(line.slice(6));
          handleExecutionEvent({
            ...event,
            timestamp: new Date(event.timestamp),
          });
        }
      }
    }

    finalizeStreamingMessage();
  } catch (error) {
    console.error('Error:', error);
  } finally {
    setLoading(false);
  }
}
```

## Backend Requirements

Your backend should:

1. **Accept user queries** via POST request
2. **Orchestrate multiple agents** based on query intent
3. **Stream execution events** in real-time
4. **Send events in order**:
   - Agent start → Reasoning → Tool calls → Agent complete
5. **Include timestamps** for all events
6. **Handle errors gracefully** and send error events

## Example Backend Flow

```python
async def process_query(message: str):
    # 1. Start planner agent
    yield {
        "type": "agent_start",
        "agent": "Query Planner",
        "timestamp": datetime.now().isoformat()
    }
    
    # 2. Send reasoning
    yield {
        "type": "reasoning",
        "data": {
            "type": "intent",
            "description": "Analyzing user query intent"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # 3. Complete planner
    yield {
        "type": "agent_complete",
        "agent": "Query Planner",
        "data": {"executionTime": 500},
        "timestamp": datetime.now().isoformat()
    }
    
    # 4. Start executor agent
    yield {
        "type": "agent_start",
        "agent": "Portfolio Analyzer",
        "timestamp": datetime.now().isoformat()
    }
    
    # 5. Tool call
    yield {
        "type": "tool_call",
        "tool": "stock_api",
        "data": {"input": {"symbols": ["AAPL"]}},
        "timestamp": datetime.now().isoformat()
    }
    
    # 6. Tool complete
    result = await call_stock_api(["AAPL"])
    yield {
        "type": "tool_complete",
        "tool": "stock_api",
        "data": {"output": result, "executionTime": 800},
        "timestamp": datetime.now().isoformat()
    }
    
    # 7. Complete executor
    yield {
        "type": "agent_complete",
        "agent": "Portfolio Analyzer",
        "data": {"executionTime": 1500},
        "timestamp": datetime.now().isoformat()
    }
    
    # 8. Stream final response
    response = "Your portfolio value is $12,543.67"
    for token in response.split():
        yield {
            "type": "token_stream",
            "token": token + " ",
            "timestamp": datetime.now().isoformat()
        }
```

## Security Considerations

1. **Authentication**: Implement JWT or session-based auth
2. **Rate Limiting**: Prevent abuse with rate limits
3. **Input Validation**: Sanitize all user inputs
4. **CORS**: Configure appropriate CORS headers
5. **Data Masking**: Mask sensitive financial data in logs

## Performance Tips

1. **Batch Events**: Send multiple events in one message when possible
2. **Compression**: Use gzip compression for streaming
3. **Connection Pooling**: Reuse connections for multiple requests
4. **Caching**: Cache frequently accessed data
5. **Timeouts**: Set appropriate timeouts for long-running operations

## Testing

Use the mock API in `src/lib/mockApi.ts` for development and testing:

```typescript
import { streamChatResponse } from '@/lib/mockApi';

for await (const event of streamChatResponse(message)) {
  handleExecutionEvent(event);
}
```

## Troubleshooting

### Events Not Appearing

- Check browser console for errors
- Verify event format matches expected structure
- Ensure timestamps are valid Date objects

### Streaming Delays

- Check network latency
- Verify server is sending events immediately
- Consider using WebSocket instead of SSE

### State Not Updating

- Verify Zustand store is properly initialized
- Check that events are being handled in correct order
- Ensure component is subscribed to store updates
