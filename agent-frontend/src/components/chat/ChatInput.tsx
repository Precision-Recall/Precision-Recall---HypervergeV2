'use client';

import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { useTextareaResize } from '@/hooks/use-textarea-resize';
import { ArrowUp, Square, Brain, Scale, ChevronDown } from 'lucide-react';
import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useChatStore, AgentMode } from '@/store/chatStore';
import { streamChatResponse, setProvider, getProvider } from '@/lib/mockApi';
import { ForensicWebSocketClient } from '@/lib/forensicApi';
import { parseForensicQuery } from '@/lib/forensicQueryParser';

interface ChatInputContextValue {
  value?: string;
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;
  onSubmit?: () => void;
  loading?: boolean;
  onStop?: () => void;
  variant?: 'default' | 'unstyled';
  rows?: number;
}

const ChatInputContext = createContext<ChatInputContextValue>({});

interface ChatInputProps extends Omit<ChatInputContextValue, 'variant'> {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'unstyled';
  rows?: number;
}

function ChatInputRoot({
  children,
  className,
  variant = 'default',
  value,
  onChange,
  onSubmit,
  loading,
  onStop,
  rows = 1,
}: ChatInputProps) {
  const contextValue: ChatInputContextValue = {
    value,
    onChange,
    onSubmit,
    loading,
    onStop,
    variant,
    rows,
  };

  return (
    <ChatInputContext.Provider value={contextValue}>
      <div
        className={cn(
          variant === 'default' &&
            'flex flex-col items-end w-full p-2 rounded-2xl border border-violet-500/20 bg-transparent focus-within:ring-1 focus-within:ring-violet-500/30 focus-within:outline-none transition-all duration-200 shadow-sm',
          variant === 'unstyled' && 'flex items-start gap-2 w-full',
          className
        )}
      >
        {children}
      </div>
    </ChatInputContext.Provider>
  );
}

ChatInputRoot.displayName = 'ChatInputRoot';

interface ChatInputTextAreaProps extends React.ComponentProps<typeof Textarea> {
  value?: string;
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;
  onSubmit?: () => void;
  variant?: 'default' | 'unstyled';
}

function ChatInputTextArea({
  onSubmit: onSubmitProp,
  value: valueProp,
  onChange: onChangeProp,
  className,
  variant: variantProp,
  ...props
}: ChatInputTextAreaProps) {
  const context = useContext(ChatInputContext);
  const value = valueProp ?? context.value ?? '';
  const onChange = onChangeProp ?? context.onChange;
  const onSubmit = onSubmitProp ?? context.onSubmit;
  const rows = context.rows ?? 1;

  // Convert parent variant to textarea variant unless explicitly overridden
  const variant =
    variantProp ?? (context.variant === 'default' ? 'unstyled' : 'default');

  const textareaRef = useTextareaResize(value, rows);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!onSubmit) {
      return;
    }
    if (e.key === 'Enter' && !e.shiftKey) {
      if (typeof value !== 'string' || value.trim().length === 0) {
        return;
      }
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <Textarea
      ref={textareaRef}
      {...props}
      value={value}
      onChange={onChange}
      onKeyDown={handleKeyDown}
      variant={variant}
      className={cn(
        'max-h-[400px] min-h-0 resize-none overflow-x-hidden',
        className
      )}
      rows={rows}
    />
  );
}

ChatInputTextArea.displayName = 'ChatInputTextArea';

interface ChatInputSubmitProps extends React.ComponentProps<typeof Button> {
  onSubmit?: () => void;
  loading?: boolean;
  onStop?: () => void;
}

function ChatInputSubmit({
  onSubmit: onSubmitProp,
  loading: loadingProp,
  onStop: onStopProp,
  className,
  ...props
}: ChatInputSubmitProps) {
  const context = useContext(ChatInputContext);
  const loading = loadingProp ?? context.loading;
  const onStop = onStopProp ?? context.onStop;
  const onSubmit = onSubmitProp ?? context.onSubmit;

  if (loading && onStop) {
    return (
      <Button
        onClick={onStop}
        variant="ghost"
        size="sm"
        className={cn(
          'shrink-0 rounded-full p-1.5 h-fit w-fit border border-border',
          className
        )}
        {...props}
      >
        <Square className="h-4 w-4" fill="currentColor" />
      </Button>
    );
  }

  const isDisabled =
    typeof context.value !== 'string' || context.value.trim().length === 0;

  return (
    <Button
      variant="ghost"
      size="sm"
      className={cn(
        'shrink-0 rounded-full p-1.5 h-fit w-fit transition-all duration-200',
        !isDisabled && 'bg-white dark:bg-white text-[#0A0A0B] hover:bg-white/90 dark:hover:bg-white/90 shadow-lg shadow-white/10',
        isDisabled && 'bg-foreground/[0.05] text-foreground/40 cursor-not-allowed',
        className
      )}
      disabled={isDisabled}
      onClick={(event) => {
        event.preventDefault();
        if (!isDisabled) {
          onSubmit?.();
        }
      }}
      {...props}
    >
      <ArrowUp className="h-4 w-4" />
    </Button>
  );
}

ChatInputSubmit.displayName = 'ChatInputSubmit';

// Main ChatInput component that uses the compound components
export function ChatInput() {
  const [input, setInput] = useState('');
  const { addMessage, handleExecutionEvent, isLoading, setLoading, agentMode, setAgentMode } = useChatStore();
  const forensicClientRef = useRef<ForensicWebSocketClient | null>(null);

  // Initialize forensic WebSocket client when in forensic mode
  useEffect(() => {
    if (agentMode === 'forensic' && !forensicClientRef.current) {
      const forensicWsUrl = process.env.NEXT_PUBLIC_FORENSIC_WS_URL;
      if (!forensicWsUrl) {
        console.error('NEXT_PUBLIC_FORENSIC_WS_URL environment variable is required');
        return;
      }
      forensicClientRef.current = new ForensicWebSocketClient(
        forensicWsUrl,
        (event) => {
          // Backend sends tool/agent as top-level keys
          const executionEvent = {
            type: event.type as any,
            agent: event.agent || event.data?.agent,
            tool: event.tool || event.data?.tool,
            token: event.token || event.data?.token,
            data: event.data,
            timestamp: new Date(event.timestamp)
          };
          handleExecutionEvent(executionEvent);
        },
        (error) => {
          console.error('Forensic WebSocket error:', error);
          setLoading(false);
        }
      );
      
      forensicClientRef.current.connect().catch((error) => {
        console.error('Failed to connect to Forensic Engine:', error);
      });
    }
    
    return () => {
      if (forensicClientRef.current && agentMode !== 'forensic') {
        forensicClientRef.current.disconnect();
        forensicClientRef.current = null;
      }
    };
  }, [agentMode]);

  // Listen for suggestion clicks
  useEffect(() => {
    const handleSuggestion = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      setInput(customEvent.detail);
      // Auto-submit after a short delay
      setTimeout(() => {
        handleSubmit(customEvent.detail);
      }, 100);
    };

    window.addEventListener('suggestion-click', handleSuggestion);
    return () => {
      window.removeEventListener('suggestion-click', handleSuggestion);
    };
  }, []);

  const handleSubmit = async (message?: string) => {
    const userMessage = message || input.trim();
    if (!userMessage || isLoading) return;

    setInput('');
    addMessage({ role: 'user', content: userMessage });
    setLoading(true);

    try {
      if (agentMode === 'forensic') {
        // Use forensic WebSocket
        if (forensicClientRef.current?.isConnected()) {
          // Parse forensic query and send to WebSocket
          const forensicParams = parseForensicQuery(userMessage);
          forensicClientRef.current.sendQuery(forensicParams.mode, forensicParams.params);
          
          // Loading will be set to false when agent_complete is received
        } else {
          throw new Error('Forensic Engine not connected. Please check if server is running on port 6060.');
        }
      } else {
        // Use general agent WebSocket
        for await (const event of streamChatResponse(userMessage)) {
          handleExecutionEvent(event);
        }
        // Finalization handled by agent_complete event in the store
      }
    } catch (error) {
      console.error('Error streaming response:', error);
      addMessage({ 
        role: 'system', 
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}` 
      });
      setLoading(false);
    }
  };

  const handleStop = () => {
    setLoading(false);
    if (forensicClientRef.current) {
      forensicClientRef.current.disconnect();
    }
  };

  const hasStartedChat = useChatStore((state) => state.hasStartedChat);

  return (
    <div className={cn(
      "p-4 transition-all duration-300",
      hasStartedChat ? "bg-background/50 backdrop-blur-sm" : "bg-transparent"
    )}>
      <ChatInputRoot
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={() => handleSubmit()}
        loading={isLoading}
        onStop={handleStop}
        variant="default"
        rows={1}
        className={cn(
          "transition-all duration-300",
          !hasStartedChat && "backdrop-blur-2xl bg-white/[0.02] dark:bg-white/[0.02]"
        )}
      >
        <ChatInputTextArea
          placeholder="Ask about company financials, trends, or comparisons..."
          disabled={isLoading}
          className={cn(
            !hasStartedChat && "text-foreground/90 placeholder:text-foreground/20"
          )}
        />
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-1">
            <ModeSwitcher mode={agentMode} onChange={setAgentMode} disabled={isLoading} />
            <ModelSwitcher disabled={isLoading} />
          </div>
          <ChatInputSubmit />
        </div>
      </ChatInputRoot>
    </div>
  );
}

function ModeSwitcher({ mode, onChange, disabled }: { mode: AgentMode; onChange: (m: AgentMode) => void; disabled: boolean }) {
  const modes: { id: AgentMode; label: string; icon: typeof Brain }[] = [
    { id: 'general', label: 'General', icon: Brain },
    { id: 'forensic', label: 'Forensic', icon: Scale },
  ];

  return (
    <div className="flex items-center gap-0.5 rounded-lg bg-foreground/[0.03] dark:bg-white/[0.03] p-0.5">
      {modes.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => !disabled && onChange(id)}
          disabled={disabled}
          className={cn(
            'flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-200',
            mode === id
              ? 'bg-violet-500/15 text-violet-400 dark:bg-violet-500/15 dark:text-violet-400'
              : 'text-foreground/40 hover:text-foreground/60',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <Icon className="h-3 w-3" />
          {label}
        </button>
      ))}
    </div>
  );
}

function ModelSwitcher({ disabled }: { disabled: boolean }) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(getProvider());
  const models = [
    { id: 'gemini', label: 'Gemini 3 Flash' },
    { id: 'openai', label: 'GPT-5 Nano' },
  ];

  const handleSwitch = (id: string) => {
    setProvider(id);
    setActive(id);
    setOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => !disabled && setOpen(!open)}
        disabled={disabled}
        className={cn(
          'flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-200 text-foreground/40 hover:text-foreground/60',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        {models.find(m => m.id === active)?.label}
        <ChevronDown className={cn('h-3 w-3 transition-transform', open && 'rotate-180')} />
      </button>
      {open && (
        <div className="absolute bottom-full left-0 mb-1 bg-background border border-border rounded-lg shadow-lg py-1 z-50 min-w-[140px]">
          {models.map(m => (
            <button
              key={m.id}
              onClick={() => handleSwitch(m.id)}
              className={cn(
                'w-full text-left px-3 py-1.5 text-xs hover:bg-foreground/5 transition-colors',
                m.id === active ? 'text-violet-400 font-medium' : 'text-foreground/70'
              )}
            >
              {m.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Export compound components for advanced usage
export { ChatInputRoot, ChatInputTextArea, ChatInputSubmit };
