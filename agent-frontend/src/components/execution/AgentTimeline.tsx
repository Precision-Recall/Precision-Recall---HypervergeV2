'use client';

import { useState } from 'react';
import { useChatStore } from '@/store/chatStore';
import { AgentCard } from './AgentCard';
import { CitationGraph } from './CitationGraph';
import { Activity, Maximize2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function AgentTimeline() {
  const { agents, citationGraph } = useChatStore();
  const [graphFullscreen, setGraphFullscreen] = useState(false);

  if (agents.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center px-6">
        <div className="w-16 h-16 rounded-full bg-border flex items-center justify-center mb-4">
          <Activity className="h-8 w-8 text-foreground/40" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">
          Agent Execution Timeline
        </h3>
        <p className="text-sm text-foreground/60 max-w-sm">
          When you send a message, you'll see the real-time execution flow of all agents,
          tool calls, and reasoning steps here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Activity className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">Execution Timeline</h3>
        <span className="text-sm text-foreground/60">({agents.length} agents)</span>
      </div>

      <div className="relative space-y-4">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />

        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <AgentCard agent={agent} />
          </motion.div>
        ))}
      </div>

      {/* Citation Graph */}
      {citationGraph && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mt-6"
        >
          <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary" />
            Citation Graph
            <button
              onClick={() => setGraphFullscreen(true)}
              className="ml-auto p-1 rounded hover:bg-foreground/10 transition-colors"
              title="Enlarge"
            >
              <Maximize2 className="h-3.5 w-3.5 text-foreground/60" />
            </button>
          </h4>
          <div style={{ height: 300 }}>
            <CitationGraph />
          </div>

          {/* Fullscreen overlay */}
          <AnimatePresence>
            {graphFullscreen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center"
                onClick={() => setGraphFullscreen(false)}
              >
                <motion.div
                  initial={{ scale: 0.9 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0.9 }}
                  className="relative w-[90vw] h-[80vh] bg-background border border-border rounded-xl shadow-2xl overflow-hidden"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={() => setGraphFullscreen(false)}
                    className="absolute top-3 right-3 z-10 p-1.5 rounded-lg bg-foreground/10 hover:bg-foreground/20 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                  <div className="absolute inset-0 p-4 flex flex-col">
                    <div className="flex items-center justify-between mb-3 shrink-0">
                      <h4 className="text-sm font-semibold text-foreground">Citation Graph</h4>
                    </div>
                    <div className="flex-1 relative">
                      <div className="absolute inset-0">
                        <CitationGraph />
                      </div>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  );
}
