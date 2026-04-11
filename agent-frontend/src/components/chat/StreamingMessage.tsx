'use client';

import { Bot } from 'lucide-react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface StreamingMessageProps {
  text: string;
}

export function StreamingMessage({ text }: StreamingMessageProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3 mb-4"
    >
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-500/10 flex items-center justify-center ring-1 ring-violet-500/20">
        <Bot className="h-4 w-4 text-violet-500 animate-pulse" />
      </div>

      <div className="flex flex-col gap-1 max-w-[70%]">
        <div className="px-4 py-3 bg-violet-500/[0.08] dark:bg-violet-500/[0.08] text-foreground rounded-[20px] rounded-tl-[4px] border border-violet-500/10">
          <div className="text-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-li:my-0.5 prose-ul:my-1 prose-ol:my-1 prose-h3:text-sm prose-h3:font-semibold prose-h3:mt-3 prose-h3:mb-1 prose-strong:text-foreground prose-table:w-full prose-th:text-left prose-th:px-3 prose-th:py-1.5 prose-th:text-xs prose-th:font-medium prose-th:bg-foreground/[0.05] prose-td:px-3 prose-td:py-1.5 prose-td:text-xs prose-td:border-t prose-td:border-border/50">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
            <span className="inline-block w-1 h-4 ml-1 bg-violet-500 animate-pulse rounded-full" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
