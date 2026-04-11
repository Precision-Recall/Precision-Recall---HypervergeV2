'use client';

import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Message } from '@/types';
import { cn, formatTime } from '@/lib/utils';
import { User, Bot, Sparkles, Loader2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { summarizeResponse } from '@/lib/summarize';
import { useSettingsStore } from '@/store/settingsStore';

const proseClasses = "text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-li:my-0.5 prose-ul:my-1 prose-ol:my-1 prose-h3:text-sm prose-h3:font-semibold prose-h3:mt-3 prose-h3:mb-1 prose-strong:text-foreground prose-table:w-full prose-th:text-left prose-th:px-3 prose-th:py-1.5 prose-th:text-xs prose-th:font-medium prose-th:bg-foreground/[0.05] prose-td:px-3 prose-td:py-1.5 prose-td:text-xs prose-td:border-t prose-td:border-border/50";

function SummaryBubble({ summary, anchorRef, onClose }: { summary: string; anchorRef: React.RefObject<HTMLButtonElement | null>; onClose: () => void }) {
  const [pos, setPos] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (anchorRef.current) {
      const rect = anchorRef.current.getBoundingClientRect();
      setPos({ top: rect.top - 8, left: rect.left });
    }
  }, [anchorRef]);

  return createPortal(
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 8 }}
      transition={{ duration: 0.15 }}
      style={{ position: 'fixed', bottom: `calc(100vh - ${pos.top}px)`, left: pos.left }}
      className="z-[100] w-72"
    >
      <div className="relative px-3.5 py-3 rounded-2xl bg-background border border-violet-500/20 shadow-xl shadow-violet-500/5">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 p-0.5 rounded-full hover:bg-foreground/5 transition-colors"
        >
          <X className="h-3 w-3 text-foreground/30" />
        </button>
        <div className="flex items-center gap-1.5 mb-2">
          <Sparkles className="h-3 w-3 text-violet-400" />
          <span className="text-[10px] font-semibold text-violet-400 uppercase tracking-wider">Executive Brief</span>
        </div>
        <p className="text-xs leading-relaxed text-foreground/70">{summary}</p>
        <div className="absolute -bottom-1.5 left-6 w-3 h-3 rotate-45 bg-background border-r border-b border-violet-500/20" />
      </div>
    </motion.div>,
    document.body
  );
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const [summary, setSummary] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showBubble, setShowBubble] = useState(false);
  const userProfile = useSettingsStore((s) => s.userProfile);
  const btnRef = useRef<HTMLButtonElement>(null);

  const handleSummarize = async () => {
    if (summary) {
      setShowBubble(!showBubble);
      return;
    }
    setLoading(true);
    try {
      const result = await summarizeResponse(message.content, userProfile);
      setSummary(result);
      setShowBubble(true);
    } catch (e) {
      console.error('Summarize failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn('flex gap-3 mb-4', isUser ? 'justify-end' : 'justify-start')}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-500/10 flex items-center justify-center ring-1 ring-violet-500/20">
          <Bot className="h-4 w-4 text-violet-500" />
        </div>
      )}

      <div className="flex flex-col gap-1 max-w-[70%]">
        <div
          className={cn(
            'px-4 py-3',
            isUser
              ? 'bg-foreground/[0.08] dark:bg-white/[0.08] text-foreground rounded-[20px] rounded-tr-[4px]'
              : 'bg-violet-500/[0.08] dark:bg-violet-500/[0.08] text-foreground rounded-[20px] rounded-tl-[4px] border border-violet-500/10'
          )}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className={proseClasses}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        <div className={cn('flex items-center gap-2 px-2', isUser ? 'justify-end' : 'justify-start')}>
          <span className="text-xs text-foreground/40">{formatTime(message.timestamp)}</span>
          {!isUser && (
            <button
              ref={btnRef}
              onClick={handleSummarize}
              disabled={loading}
              className="flex items-center gap-1 text-[10px] text-foreground/30 hover:text-violet-400 transition-colors disabled:opacity-50"
              title="Executive summary"
            >
              {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
              Personalize
            </button>
          )}
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-foreground/10 flex items-center justify-center ring-1 ring-foreground/10">
          <User className="h-4 w-4 text-foreground/60" />
        </div>
      )}

      <AnimatePresence>
        {showBubble && summary && (
          <SummaryBubble summary={summary} anchorRef={btnRef} onClose={() => setShowBubble(false)} />
        )}
      </AnimatePresence>
    </motion.div>
  );
}
