'use client';

import { useChatStore, AgentMode } from '@/store/chatStore';
import { Brain, Scale } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export function ModeSelector() {
  const { agentMode, setAgentMode, hasStartedChat } = useChatStore();

  // Don't show if chat has started
  if (hasStartedChat) return null;

  const modes: { id: AgentMode; label: string; icon: typeof Brain; description: string }[] = [
    {
      id: 'general',
      label: 'General Assistant',
      icon: Brain,
      description: 'Multi-agent financial analysis'
    },
    {
      id: 'forensic',
      label: 'Forensic Engine',
      icon: Scale,
      description: 'Audit company integrity & detect anomalies'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="flex justify-center gap-3 mb-8"
    >
      {modes.map((mode) => {
        const Icon = mode.icon;
        const isActive = agentMode === mode.id;

        return (
          <motion.button
            key={mode.id}
            onClick={() => setAgentMode(mode.id)}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
              'border',
              isActive
                ? 'bg-violet-500/10 border-violet-500/30 dark:bg-violet-500/10 dark:border-violet-500/30'
                : 'bg-foreground/[0.02] border-foreground/10 hover:bg-foreground/[0.05] dark:bg-white/[0.02] dark:border-white/10 dark:hover:bg-white/[0.05]'
            )}
          >
            <div className={cn(
              'w-10 h-10 rounded-lg flex items-center justify-center',
              isActive
                ? 'bg-violet-500/20 dark:bg-violet-500/20'
                : 'bg-foreground/5 dark:bg-white/5'
            )}>
              <Icon className={cn(
                'h-5 w-5',
                isActive
                  ? 'text-violet-500'
                  : 'text-foreground/60'
              )} />
            </div>
            <div className="text-left">
              <div className={cn(
                'text-sm font-medium',
                isActive
                  ? 'text-foreground'
                  : 'text-foreground/70'
              )}>
                {mode.label}
              </div>
              <div className="text-xs text-foreground/40">
                {mode.description}
              </div>
            </div>
            {isActive && (
              <motion.div
                layoutId="mode-indicator"
                className="w-2 h-2 rounded-full bg-violet-500"
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
              />
            )}
          </motion.button>
        );
      })}
    </motion.div>
  );
}
