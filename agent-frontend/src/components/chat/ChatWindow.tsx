'use client';

import { useEffect, useRef, useState } from 'react';
import { useChatStore } from '@/store/chatStore';
import { MessageBubble } from './MessageBubble';
import { StreamingMessage } from './StreamingMessage';
import { Sparkles, FileText, ChevronDown, Maximize2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function TableOverlay({ html, onClose }: { html: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div
        className="relative bg-background border border-border rounded-xl shadow-2xl max-w-[90vw] max-h-[85vh] overflow-auto p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 p-1.5 rounded-lg bg-foreground/10 hover:bg-foreground/20 transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
        <div
          className="text-sm [&_table]:w-full [&_table]:border-collapse [&_td]:border [&_td]:border-border/50 [&_td]:px-3 [&_td]:py-2 [&_td]:text-foreground/80 [&_tr:first-child]:bg-foreground/[0.05] [&_tr:first-child]:font-medium"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      </div>
    </div>
  );
}

function SourceCard({ index, source: src }: { index: number; source: any }) {
  const [expanded, setExpanded] = useState(false);
  const [overlayOpen, setOverlayOpen] = useState(false);

  return (
    <div className="p-3 rounded-lg bg-foreground/[0.03] border border-border/50">
      <div className="flex items-start gap-3">
        <div className="shrink-0 w-6 h-6 rounded bg-primary/10 flex items-center justify-center text-xs font-medium text-primary">
          {index + 1}
        </div>
        <div className="min-w-0 w-full">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-medium px-1.5 py-0.5 rounded bg-foreground/[0.05]">
              {src.company}
            </span>
            {src.year && (
              <span className="text-xs font-medium px-1.5 py-0.5 rounded bg-foreground/[0.05]">
                {src.year}
              </span>
            )}
            {src.section && (
              <span className="text-xs text-foreground/60">{src.section}</span>
            )}
            {src.type && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                {src.type}
              </span>
            )}
            {src.page != null && (
              <span className="text-xs text-foreground/40">p.{src.page}</span>
            )}
          </div>

          {/* Preview: 3 lines max */}
          {!expanded && src.text && (
            <p className="text-xs text-foreground/60 mt-1 line-clamp-3">{src.text}</p>
          )}

          {/* Expanded: full content */}
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                {src.raw_content ? (
                  <div className="relative mt-2">
                    <div
                      className="text-xs overflow-x-auto [&_table]:w-full [&_table]:border-collapse [&_td]:border [&_td]:border-border/50 [&_td]:px-2 [&_td]:py-1 [&_td]:text-foreground/80 [&_tr:first-child]:bg-foreground/[0.05] [&_tr:first-child]:font-medium"
                      dangerouslySetInnerHTML={{ __html: src.raw_content }}
                    />
                    <button
                      onClick={() => setOverlayOpen(true)}
                      className="absolute top-1 right-1 p-1 rounded bg-foreground/10 hover:bg-foreground/20 transition-colors"
                      title="Expand table"
                    >
                      <Maximize2 className="h-3 w-3 text-foreground/60" />
                    </button>
                  </div>
                ) : src.text ? (
                  <p className="text-xs text-foreground/60 mt-2 whitespace-pre-wrap">{src.text}</p>
                ) : null}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Expand button */}
          {(src.raw_content || (src.text && src.text.length > 150)) && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-1.5 flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
            >
              <ChevronDown className={`h-3 w-3 transition-transform ${expanded ? 'rotate-180' : ''}`} />
              {expanded ? 'Collapse' : src.raw_content ? 'Show table' : 'Show more'}
            </button>
          )}
        </div>
      </div>
      {overlayOpen && src.raw_content && (
        <TableOverlay html={src.raw_content} onClose={() => setOverlayOpen(false)} />
      )}
    </div>
  );
}

export function ChatWindow() {
  const { messages, isStreaming, streamingText, isLoading, agents, sources } = useChatStore();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showSources, setShowSources] = useState(false);

  const currentAgent = agents.find(a => a.status === 'running');

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamingText, currentAgent]);

  return (
    <div
      ref={scrollRef}
      className="h-full overflow-y-auto px-6 py-4 space-y-4 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent"
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isStreaming && streamingText && <StreamingMessage text={streamingText} />}

      {/* Sources badge + panel */}
      {sources.length > 0 && !isLoading && (
        <div className="pb-2">
          <button
            onClick={() => setShowSources(!showSources)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-xs text-primary hover:bg-primary/20 transition-colors"
          >
            <FileText className="h-3 w-3" />
            <span>{sources.length} sources</span>
            <ChevronDown className={`h-3 w-3 transition-transform ${showSources ? 'rotate-180' : ''}`} />
          </button>

          <AnimatePresence>
            {showSources && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden mt-2"
              >
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {sources.map((src, i) => (
                    <SourceCard key={i} index={i} source={src} />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {isLoading && !isStreaming && (
        <div className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-foreground/[0.03] border border-border/50 max-w-md">
          <div className="flex gap-1">
            <span className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:0ms]" />
            <span className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:150ms]" />
            <span className="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:300ms]" />
          </div>
          <span className="text-sm text-foreground/60">
            {currentAgent ? `${currentAgent.name} is working...` : 'Thinking...'}
          </span>
        </div>
      )}
    </div>
  );
}
