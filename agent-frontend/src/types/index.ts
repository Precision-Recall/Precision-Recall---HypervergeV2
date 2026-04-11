export type MessageRole = 'user' | 'assistant' | 'system';

export type AgentStatus = 'pending' | 'running' | 'completed' | 'error';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
}

export interface ToolCall {
  id: string;
  name: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  status: AgentStatus;
  timestamp: Date;
  executionTime?: number;
}

export interface ReasoningStep {
  id: string;
  type: 'intent' | 'planning' | 'tool_call' | 'synthesis';
  description: string;
  timestamp: Date;
}

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: AgentStatus;
  input?: string;
  output?: string;
  timestamp: Date;
  executionTime?: number;
  toolCalls: ToolCall[];
  reasoning: ReasoningStep[];
}

export interface ExecutionEvent {
  type: 'agent_start' | 'agent_complete' | 'tool_call' | 'tool_complete' | 'token_stream' | 'reasoning' | 'error' | 'done' | 'sources' | 'citation_graph';
  agent?: string;
  tool?: string;
  token?: string;
  data?: any;
  timestamp: Date;
}

export interface Session {
  id: string;
  messages: Message[];
  agents: Agent[];
  currentAgent?: string;
  isStreaming: boolean;
  streamingText: string;
}
