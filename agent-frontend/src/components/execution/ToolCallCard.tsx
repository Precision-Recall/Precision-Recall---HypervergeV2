'use client';

import { useState } from 'react';
import { ToolCall } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { CodeBlock } from '@/components/ui/CodeBlock';
import { ChevronDown, Wrench } from 'lucide-react';
import { cn, formatDuration } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface ToolCallCardProps {
  toolCall: ToolCall;
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-border rounded-xl overflow-hidden bg-background/30">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between gap-3 p-3 text-left hover:bg-border/30 transition-colors"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <div className={cn(
            'flex-shrink-0 w-6 h-6 rounded-lg flex items-center justify-center',
            {
              'bg-foreground/10': toolCall.status === 'pending',
              'bg-primary/20': toolCall.status === 'running',
              'bg-success/20': toolCall.status === 'completed',
              'bg-error/20': toolCall.status === 'error',
            }
          )}>
            <Wrench className={cn('h-3 w-3', {
              'text-foreground/70': toolCall.status === 'pending',
              'text-primary': toolCall.status === 'running',
              'text-success': toolCall.status === 'completed',
              'text-error': toolCall.status === 'error',
            })} />
          </div>
          <span className="font-medium text-sm text-foreground truncate">{toolCall.name}</span>
          <Badge status={toolCall.status} variant="status">
            {toolCall.status}
          </Badge>
          {toolCall.executionTime && (
            <span className="text-xs text-foreground/60">
              {formatDuration(toolCall.executionTime)}
            </span>
          )}
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="h-4 w-4 text-foreground/60" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-3 pt-0 space-y-3">
              {/* Input */}
              <div>
                <h6 className="text-xs font-medium text-foreground/70 mb-2">Input</h6>
                <CodeBlock
                  code={JSON.stringify(toolCall.input, null, 2)}
                  language="json"
                />
              </div>

              {/* Output */}
              {toolCall.output && (
                <div>
                  <h6 className="text-xs font-medium text-foreground/70 mb-2">Output</h6>
                  <CodeBlock
                    code={JSON.stringify(toolCall.output, null, 2)}
                    language="json"
                  />
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
