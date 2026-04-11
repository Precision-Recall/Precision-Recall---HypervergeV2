import { create } from 'zustand';
import { Message, Agent, ExecutionEvent, AgentStatus, ToolCall, ReasoningStep } from '@/types';

export type AgentMode = 'general' | 'forensic';

interface ChatState {
  messages: Message[];
  agents: Agent[];
  currentAgent: string | null;
  isStreaming: boolean;
  streamingText: string;
  isLoading: boolean;
  hasStartedChat: boolean;
  sources: any[];
  citationGraph: { nodes: any[]; edges: any[] } | null;
  agentMode: AgentMode;
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateStreamingText: (text: string) => void;
  finalizeStreamingMessage: () => void;
  handleExecutionEvent: (event: ExecutionEvent) => void;
  clearChat: () => void;
  setLoading: (loading: boolean) => void;
  setAgentMode: (mode: AgentMode) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  agents: [],
  currentAgent: null,
  isStreaming: false,
  streamingText: '',
  isLoading: false,
  hasStartedChat: false,
  agentMode: 'general' as AgentMode,
  sources: [],
  citationGraph: null,

  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, newMessage],
      hasStartedChat: true,
      // Reset agents/trace when user sends a new message
      ...(message.role === 'user' ? { agents: [], currentAgent: null, streamingText: '', isStreaming: false, sources: [], citationGraph: null } : {}),
    }));
  },

  updateStreamingText: (text) => {
    set({ streamingText: text, isStreaming: true });
  },

  finalizeStreamingMessage: () => {
    const { streamingText } = get();
    if (streamingText) {
      get().addMessage({
        role: 'assistant',
        content: streamingText,
      });
    }
    set({ streamingText: '', isStreaming: false });
  },

  handleExecutionEvent: (event) => {
    const { agents } = get();

    switch (event.type) {
      case 'agent_start': {
        const newAgent: Agent = {
          id: crypto.randomUUID(),
          name: event.agent || 'Unknown Agent',
          type: event.data?.type || 'general',
          status: 'running' as AgentStatus,
          timestamp: event.timestamp,
          toolCalls: [],
          reasoning: [],
        };
        set((state) => ({
          agents: [...state.agents, newAgent],
          currentAgent: newAgent.id,
        }));
        break;
      }

      case 'agent_complete': {
        const agentIndex = agents.findIndex((a) => a.name === event.agent);
        if (agentIndex !== -1) {
          const updatedAgents = [...agents];
          updatedAgents[agentIndex] = {
            ...updatedAgents[agentIndex],
            status: 'completed' as AgentStatus,
            output: event.data?.output,
            executionTime: event.data?.executionTime,
          };
          set({ agents: updatedAgents, currentAgent: null });
        }
        // Finalize streaming text into a message and stop loading
        const { streamingText } = get();
        if (streamingText) {
          get().addMessage({ role: 'assistant', content: streamingText });
          set({ streamingText: '', isStreaming: false });
        }
        set({ isLoading: false });
        break;
      }

      case 'tool_call': {
        // Find the agent this tool belongs to (by event.agent or currentAgent)
        const targetAgentName = event.agent;
        const agentIdx = targetAgentName
          ? agents.findIndex((a) => a.name === targetAgentName && a.status === 'running')
          : agents.findIndex((a) => a.id === get().currentAgent);
        
        if (agentIdx !== -1) {
          const newToolCall: ToolCall = {
            id: crypto.randomUUID(),
            name: event.tool || 'Unknown Tool',
            input: event.data?.input || {},
            status: 'running' as AgentStatus,
            timestamp: event.timestamp,
          };
          const updatedAgents = [...agents];
          updatedAgents[agentIdx].toolCalls.push(newToolCall);
          set({ agents: updatedAgents });
        }
        break;
      }

      case 'tool_complete': {
        const targetName = event.agent;
        const agIdx = targetName
          ? agents.findIndex((a) => a.name === targetName)
          : agents.findIndex((a) => a.id === get().currentAgent);
        
        if (agIdx !== -1) {
          const updatedAgents = [...agents];
          const toolIndex = updatedAgents[agIdx].toolCalls.findIndex(
            (t) => t.name === event.tool && t.status === 'running'
          );
          if (toolIndex !== -1) {
            updatedAgents[agIdx].toolCalls[toolIndex] = {
              ...updatedAgents[agIdx].toolCalls[toolIndex],
              status: 'completed' as AgentStatus,
              output: event.data?.output,
              executionTime: event.data?.executionTime,
            };
            set({ agents: updatedAgents });
          }
        }
        break;
      }

      case 'reasoning': {
        const { currentAgent } = get();
        if (currentAgent) {
          const agentIndex = agents.findIndex((a) => a.id === currentAgent);
          if (agentIndex !== -1) {
            const newReasoning: ReasoningStep = {
              id: crypto.randomUUID(),
              type: event.data?.type || 'planning',
              description: event.data?.description || '',
              timestamp: event.timestamp,
            };
            const updatedAgents = [...agents];
            updatedAgents[agentIndex].reasoning.push(newReasoning);
            set({ agents: updatedAgents });
          }
        }
        break;
      }

      case 'token_stream': {
        const { streamingText } = get();
        set({ streamingText: streamingText + (event.token || ''), isStreaming: true });
        break;
      }

      case 'error': {
        const { currentAgent } = get();
        if (currentAgent) {
          const agentIndex = agents.findIndex((a) => a.id === currentAgent);
          if (agentIndex !== -1) {
            const updatedAgents = [...agents];
            updatedAgents[agentIndex].status = 'error' as AgentStatus;
            set({ agents: updatedAgents, currentAgent: null });
          }
        }
        break;
      }

      case 'done': {
        // No-op — handled by the stream consumer calling finalizeStreamingMessage
        break;
      }

      case 'sources': {
        const newSources = event.data?.sources || [];
        set((state) => ({ sources: [...state.sources, ...newSources] }));
        break;
      }

      case 'citation_graph': {
        set({ citationGraph: event.data });
        break;
      }
    }
  },

  clearChat: () => {
    set({
      messages: [],
      agents: [],
      currentAgent: null,
      isStreaming: false,
      streamingText: '',
      isLoading: false,
      hasStartedChat: false,
      sources: [],
      citationGraph: null,
      agentMode: 'general' as AgentMode,
    });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setAgentMode: (mode: AgentMode) => {
    set({ agentMode: mode });
  },
}));
