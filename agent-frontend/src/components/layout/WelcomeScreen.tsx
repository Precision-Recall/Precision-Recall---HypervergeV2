'use client';

import { TrendingUp, PieChart, BarChart3, Scale, AlertTriangle, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { useChatStore } from '@/store/chatStore';
import { ModeSelector } from './ModeSelector';

const generalSuggestions = [
  {
    icon: TrendingUp,
    title: 'Portfolio Analysis',
    description: "What's my portfolio performance?",
  },
  {
    icon: PieChart,
    title: 'Market Insights',
    description: 'Analyze the tech sector trends',
  },
  {
    icon: BarChart3,
    title: 'Investment Returns',
    description: 'Calculate my investment returns',
  },
];

const forensicSuggestions = [
  {
    icon: Scale,
    title: 'Promise vs. Reality',
    description: 'Did TSLA deliver on their 2018 renewable energy promise by 2023?',
  },
  {
    icon: AlertTriangle,
    title: 'Anomaly Detection',
    description: 'Flag changes in TSLA risk factors between 2022 and 2023',
  },
  {
    icon: TrendingDown,
    title: 'Sentiment Divergence',
    description: 'Detect if TSLA CEO was optimistic while footnotes showed liquidity risk in 2023',
  },
];

interface WelcomeScreenProps {
  onSuggestionClick: (suggestion: string) => void;
}

export function WelcomeScreen({ onSuggestionClick }: WelcomeScreenProps) {
  const agentMode = useChatStore((state) => state.agentMode);
  const suggestions = agentMode === 'forensic' ? forensicSuggestions : generalSuggestions;

  return (
    <div className="flex-1 flex items-center justify-center p-8 relative">
      <div className="max-w-2xl w-full space-y-12 relative z-10">
        {/* Mode Selector */}
        <ModeSelector />
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="text-center space-y-3"
        >
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="inline-block"
          >
            <h1 className="text-3xl font-medium tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground/90 to-foreground/40 pb-1">
              How can I help today?
            </h1>
            <motion.div 
              className="h-px bg-gradient-to-r from-transparent via-foreground/20 to-transparent"
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: "100%", opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.8 }}
            />
          </motion.div>
          <motion.p 
            className="text-sm text-foreground/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Type a command or ask a question about your finances
          </motion.p>
        </motion.div>

        {/* Suggestion Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-wrap items-center justify-center gap-2"
        >
          {suggestions.map((suggestion, index) => {
            const Icon = suggestion.icon;
            return (
              <motion.button
                key={index}
                onClick={() => onSuggestionClick(suggestion.description)}
                className="flex items-center gap-2 px-3 py-2 bg-foreground/[0.02] hover:bg-foreground/[0.05] dark:bg-white/[0.02] dark:hover:bg-white/[0.05] rounded-lg text-sm text-foreground/60 hover:text-foreground/90 transition-all relative group border border-foreground/[0.05]"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon className="w-4 h-4" />
                <span>{suggestion.title}</span>
              </motion.button>
            );
          })}
        </motion.div>
      </div>
    </div>
  );
}
