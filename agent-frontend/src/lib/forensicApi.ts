/**
 * Forensic Engine WebSocket Client
 * Connects to ws://localhost:6060
 */

export type ForensicMode = 'promise_vs_reality' | 'anomaly_detection' | 'sentiment_divergence';

export interface ForensicParams {
  // Promise vs. Reality
  company?: string;
  promise_year?: number;
  verification_year?: number;
  promise_query?: string;
  
  // Anomaly Detection
  start_year?: number;
  end_year?: number;
  
  // Sentiment Divergence
  year?: number;
  
  // Common
  lens?: 'finance' | 'environment' | 'strategy' | 'governance';
}

export interface ForensicEvent {
  type: string;
  data: any;
  timestamp: number;
  agent?: string;
  tool?: string;
  token?: string;
}

export class ForensicWebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  
  constructor(
    private url: string,
    private onEvent?: (event: ForensicEvent) => void,
    private onError?: (error: Error) => void
  ) {
    if (!url) {
      throw new Error('WebSocket URL is required');
    }
  }
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('✓ Connected to Forensic Engine');
          this.reconnectAttempts = 0;
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const data: ForensicEvent = JSON.parse(event.data);
            console.log('← Forensic event:', data.type);
            this.onEvent?.(data);
          } catch (error) {
            console.error('Failed to parse message:', error);
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.onError?.(new Error('WebSocket connection error'));
        };
        
        this.ws.onclose = () => {
          console.log('✗ Disconnected from Forensic Engine');
          this.attemptReconnect();
        };
        
      } catch (error) {
        reject(error);
      }
    });
  }
  
  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }
  
  sendQuery(mode: ForensicMode, params: ForensicParams) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }
    
    const message = {
      type: mode,
      params
    };
    
    console.log('→ Sending query:', mode, params);
    this.ws.send(JSON.stringify(message));
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Example usage:
// const client = new ForensicWebSocketClient(
//   'ws://localhost:6060',
//   (event) => console.log('Event:', event),
//   (error) => console.error('Error:', error)
// );
// await client.connect();
// client.sendQuery('promise_vs_reality', {
//   company: 'TSLA',
//   promise_year: 2018,
//   verification_year: 2023,
//   lens: 'environment',
//   promise_query: 'renewable energy target 50%'
// });
