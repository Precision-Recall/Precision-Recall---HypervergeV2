import { ExecutionEvent } from '@/types';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL;
if (!WS_URL) {
  throw new Error('NEXT_PUBLIC_WS_URL environment variable is required');
}

let ws: WebSocket | null = null;
const SESSION_ID = crypto.randomUUID();
let currentProvider = 'gemini'; // 'gemini' | 'openai'

export function setProvider(provider: string) {
  currentProvider = provider;
}

export function getProvider() {
  return currentProvider;
}

function getWebSocket(): WebSocket {
  if (!ws || ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
    ws = new WebSocket(WS_URL);
  }
  return ws;
}

export async function* streamChatResponse(message: string): AsyncGenerator<ExecutionEvent> {
  const socket = getWebSocket();

  // Wait for connection
  if (socket.readyState === WebSocket.CONNECTING) {
    await new Promise<void>((resolve, reject) => {
      socket.onopen = () => resolve();
      socket.onerror = () => reject(new Error('WebSocket connection failed'));
    });
  }

  // Create a queue for incoming events
  const queue: ExecutionEvent[] = [];
  let done = false;
  let resolver: (() => void) | null = null;

  const onMessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    const executionEvent: ExecutionEvent = {
      ...data,
      timestamp: new Date(data.timestamp),
    };
    queue.push(executionEvent);

    // Check if this is the final event
    if (data.type === 'done' || data.type === 'error') {
      done = true;
    }

    if (resolver) {
      resolver();
      resolver = null;
    }
  };

  const onError = () => {
    done = true;
    if (resolver) {
      resolver();
      resolver = null;
    }
  };

  socket.addEventListener('message', onMessage);
  socket.addEventListener('error', onError);

  // Send the message with session ID
  socket.send(JSON.stringify({ message, sessionId: SESSION_ID, provider: currentProvider }));

  // Yield events as they arrive
  try {
    while (!done || queue.length > 0) {
      if (queue.length > 0) {
        yield queue.shift()!;
      } else if (!done) {
        await new Promise<void>((resolve) => {
          resolver = resolve;
        });
      }
    }
  } finally {
    socket.removeEventListener('message', onMessage);
    socket.removeEventListener('error', onError);
  }
}
