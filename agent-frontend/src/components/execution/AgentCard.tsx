'use client';

import { useState } from 'react';
import { Agent } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import { ToolCallCard } from './ToolCallCard';
import { ReasoningPanel } from './ReasoningPanel';
import { ChevronDown, ChevronRight, Clock, Cpu } from 'lucide-react';
import { cn, formatTime, formatDuration } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface AgentCardProps {
  agent: Agent;
}

export function AgentCard({ agent }: AgentCardProps) {
  const [isExpanded, setIsExpanded] = useState(agent.status === 'running');

  return (
    <div className="relative pl-8">
      {/* Timeline dot */}
      <div
        className={cn(
          'absolute left-[9px] top-4 w-7 h-7 rounded-full border-4 border-background z-10',
          'flex items-center justify-center',
          {
            'bg-foreground/20': agent.status === 'pending',
            'bg-primary animate-pulse': agent.status === 'running',
            'bg-success': agent.status === 'completed',
            'bg-error': agent.status === 'error',
          }
        )}
      >
        <Cpu className={cn('h-3 w-3', {
          'text-foreground/70': agent.status === 'pending',
          'text-background': agent.status !== 'pending',
        })} />
      </div>

      <Card className="transition-all duration-200 hover:border-primary/50">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-start justify-between gap-4 text-left"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <h4 className="font-semibold text-foreground">{agent.name}</h4>
              <Badge status={agent.status} variant="status">
                {agent.status}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-xs text-foreground/60">
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatTime(agent.timestamp)}
              </span>
              {agent.executionTime && (
                <span>{formatDuration(agent.executionTime)}</span>
              )}
              {agent.toolCalls.length > 0 && (
                <span>{agent.toolCalls.length} tool{agent.toolCalls.length > 1 ? 's' : ''}</span>
              )}
            </div>
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 0 : -90 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="h-5 w-5 text-foreground/60" />
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
              <div className="mt-4 pt-4 border-t border-border space-y-4">
                {/* Input */}
                {agent.input && (
                  <div>
                    <h5 className="text-xs font-medium text-foreground/70 mb-2">Input</h5>
                    <p className="text-sm text-foreground/80 bg-border/50 rounded-lg p-3">
                      {agent.input}
                    </p>
                  </div>
                )}

                {/* Reasoning */}
                {agent.reasoning.length > 0 && (
                  <ReasoningPanel reasoning={agent.reasoning} />
                )}

                {/* Thinking indicator when running */}
                {agent.status === 'running' && (
                  <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/5 border border-primary/10">
                    <div className="flex gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:0ms]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:150ms]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:300ms]" />
                    </div>
                    <span className="text-xs text-primary/80 animate-pulse">
                      {agent.toolCalls.length > 0 
                        ? `Processing ${agent.toolCalls[agent.toolCalls.length - 1]?.name || 'tool'}...`
                        : agent.reasoning.length > 0
                          ? agent.reasoning[agent.reasoning.length - 1]?.description
                          : 'Thinking...'}
                    </span>
                  </div>
                )}

                {/* Tool Calls */}
                {agent.toolCalls.length > 0 && (
                  <div>
                    <h5 className="text-xs font-medium text-foreground/70 mb-2">
                      Tool Calls ({agent.toolCalls.length})
                    </h5>
                    <div className="space-y-2">
                      {agent.toolCalls.map((tool) => (
                        <ToolCallCard key={tool.id} toolCall={tool} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Output */}
                {agent.output && (
                  <div>
                    <h5 className="text-xs font-medium text-foreground/70 mb-2">Output</h5>
                    <p className="text-sm text-foreground/80 bg-border/50 rounded-lg p-3">
                      {agent.output}
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </div>
  );
}
