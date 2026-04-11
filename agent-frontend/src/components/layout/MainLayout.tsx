'use client';

import { useState } from 'react';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ChatInput } from '@/components/chat/ChatInput';
import { AgentTimeline } from '@/components/execution/AgentTimeline';
import { WelcomeScreen } from './WelcomeScreen';
import { Header } from './Header';
import { MessageSquare, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useChatStore } from '@/store/chatStore';

export function MainLayout() {
  const [activeTab, setActiveTab] = useState<'chat' | 'execution'>('chat');
  const hasStartedChat = useChatStore((state) => state.hasStartedChat);

  const handleSuggestionClick = (suggestion: string) => {
    // This will be handled by ChatInput component
    const event = new CustomEvent('suggestion-click', { detail: suggestion });
    window.dispatchEvent(event);
  };

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      <Header />

      {!hasStartedChat ? (
        /* Welcome Screen - Centered */
        <div className="flex-1 flex flex-col overflow-hidden justify-center relative">
          {/* Animated gradient blobs */}
          <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/10 dark:bg-violet-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-blob" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-blob animation-delay-2000" />
            <div className="absolute top-1/4 right-1/3 w-64 h-64 bg-fuchsia-500/10 dark:bg-fuchsia-500/10 rounded-full mix-blend-normal filter blur-[96px] animate-blob animation-delay-4000" />
          </div>
          <WelcomeScreen onSuggestionClick={handleSuggestionClick} />
          <div className="max-w-2xl mx-auto w-full px-6 relative z-10">
            <ChatInput />
          </div>
        </div>
      ) : (
        <>
          {/* Desktop: Split View */}
          <div className="hidden lg:flex flex-1 overflow-hidden">
            {/* Left Panel - Chat */}
            <div className="w-1/2 border-r border-border flex flex-col relative">
              {/* Animated gradient blobs in left panel */}
              <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/10 dark:bg-violet-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-blob" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-blob animation-delay-2000" />
                <div className="absolute top-1/4 right-1/3 w-64 h-64 bg-fuchsia-500/10 dark:bg-fuchsia-500/10 rounded-full mix-blend-normal filter blur-[96px] animate-blob animation-delay-4000" />
              </div>
              <div className="relative z-10 flex flex-col h-full overflow-hidden">
                <div className="flex-1 min-h-0 overflow-hidden">
                  <ChatWindow />
                </div>
                <div className="shrink-0">
                  <ChatInput />
                </div>
              </div>
            </div>

            {/* Right Panel - Execution */}
            <div className="w-1/2 overflow-y-auto scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
              <AgentTimeline />
            </div>
          </div>

          {/* Mobile: Tabbed View */}
          <div className="lg:hidden flex flex-col flex-1 overflow-hidden">
            {/* Tab Buttons */}
            <div className="flex border-b border-border bg-background/50">
              <button
                onClick={() => setActiveTab('chat')}
                className={cn(
                  'flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors',
                  activeTab === 'chat'
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-foreground/60 hover:text-foreground'
                )}
              >
                <MessageSquare className="h-4 w-4" />
                Chat
              </button>
              <button
                onClick={() => setActiveTab('execution')}
                className={cn(
                  'flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors',
                  activeTab === 'execution'
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-foreground/60 hover:text-foreground'
                )}
              >
                <Activity className="h-4 w-4" />
                Execution
              </button>
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-hidden">
              {activeTab === 'chat' ? (
                <div className="h-full flex flex-col relative">
                  {/* Animated gradient blobs in mobile chat */}
                  <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/10 dark:bg-violet-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-blob" />
                    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/10 rounded-full mix-blend-normal filter blur-[128px] animate-blob animation-delay-2000" />
                    <div className="absolute top-1/4 right-1/3 w-64 h-64 bg-fuchsia-500/10 dark:bg-fuchsia-500/10 rounded-full mix-blend-normal filter blur-[96px] animate-blob animation-delay-4000" />
                  </div>
                  <div className="relative z-10 flex flex-col h-full overflow-hidden">
                    <div className="flex-1 min-h-0 overflow-hidden">
                      <ChatWindow />
                    </div>
                    <div className="shrink-0">
                      <ChatInput />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full overflow-y-auto scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
                  <AgentTimeline />
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
