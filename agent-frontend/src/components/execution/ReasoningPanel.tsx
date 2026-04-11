'use client';

import { ReasoningStep } from '@/types';
import { Lightbulb, Target, Wrench, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface ReasoningPanelProps {
  reasoning: ReasoningStep[];
}

export function ReasoningPanel({ reasoning }: ReasoningPanelProps) {
  const getIcon = (type: ReasoningStep['type']) => {
    switch (type) {
      case 'intent':
        return Target;
      case 'planning':
        return Lightbulb;
      case 'tool_call':
        return Wrench;
      case 'synthesis':
        return Sparkles;
      default:
        return Lightbulb;
    }
  };

  const getColor = (type: ReasoningStep['type']) => {
    switch (type) {
      case 'intent':
        return 'text-primary';
      case 'planning':
        return 'text-warning';
      case 'tool_call':
        return 'text-success';
      case 'synthesis':
        return 'text-primary-light';
      default:
        return 'text-foreground/70';
    }
  };

  return (
    <div>
      <h5 className="text-xs font-medium text-foreground/70 mb-2">Reasoning Trace</h5>
      <div className="space-y-2">
        {reasoning.map((step, index) => {
          const Icon = getIcon(step.type);
          const colorClass = getColor(step.type);

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: index * 0.05 }}
              className="flex items-start gap-2 text-sm"
            >
              <Icon className={cn('h-4 w-4 mt-0.5 flex-shrink-0', colorClass)} />
              <p className="text-foreground/80 leading-relaxed">{step.description}</p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
