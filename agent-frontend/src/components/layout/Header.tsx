'use client';

import { useState } from 'react';
import { useChatStore } from '@/store/chatStore';
import { useSettingsStore, UserProfile } from '@/store/settingsStore';
import { useThemeStore } from '@/store/themeStore';
import { Button } from '@/components/ui/Button';
import { Trash2, Download, Sun, Moon, ArrowLeft, Settings, X } from 'lucide-react';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

function SettingsOverlay({ onClose }: { onClose: () => void }) {
  const { userProfile, setUserProfile } = useSettingsStore();
  const [name, setName] = useState(userProfile?.name || '');
  const [profession, setProfession] = useState(userProfile?.profession || '');
  const [summary, setSummary] = useState(userProfile?.summary || '');

  const handleSave = () => {
    setUserProfile({ name, profession, summary });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end pt-14 pr-4" onClick={onClose}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: -10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -10 }}
        transition={{ duration: 0.15 }}
        onClick={(e) => e.stopPropagation()}
        className="w-80 bg-background border border-border rounded-2xl shadow-2xl p-5 space-y-4"
      >
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground">Personalization</h3>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-foreground/5 transition-colors">
            <X className="h-4 w-4 text-foreground/40" />
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-foreground/50 mb-1 block">Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              className="w-full px-3 py-2 text-sm bg-foreground/[0.03] border border-border/50 rounded-xl focus:outline-none focus:ring-1 focus:ring-violet-500/30 text-foreground placeholder:text-foreground/30"
            />
          </div>
          <div>
            <label className="text-xs text-foreground/50 mb-1 block">Profession</label>
            <input
              value={profession}
              onChange={(e) => setProfession(e.target.value)}
              placeholder="e.g. Financial Analyst"
              className="w-full px-3 py-2 text-sm bg-foreground/[0.03] border border-border/50 rounded-xl focus:outline-none focus:ring-1 focus:ring-violet-500/30 text-foreground placeholder:text-foreground/30"
            />
          </div>
          <div>
            <label className="text-xs text-foreground/50 mb-1 block">About you</label>
            <textarea
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="Brief summary about your work..."
              rows={3}
              className="w-full px-3 py-2 text-sm bg-foreground/[0.03] border border-border/50 rounded-xl focus:outline-none focus:ring-1 focus:ring-violet-500/30 text-foreground placeholder:text-foreground/30 resize-none"
            />
          </div>
        </div>

        <button
          onClick={handleSave}
          className="w-full py-2 text-sm font-medium rounded-xl bg-violet-500/15 text-violet-400 hover:bg-violet-500/25 transition-colors"
        >
          Save
        </button>
      </motion.div>
    </div>
  );
}

export function Header() {
  const { clearChat, messages, agents, hasStartedChat } = useChatStore();
  const { theme, toggleTheme } = useThemeStore();
  const [showSettings, setShowSettings] = useState(false);

  const handleExport = () => {
    const data = { messages, agents, exportedAt: new Date().toISOString() };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-session-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <header className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-2.5">
          <div className="flex items-center gap-3">
            {hasStartedChat && (
              <Button variant="ghost" size="sm" onClick={clearChat} aria-label="Back to home" className="h-8 w-8 p-0">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            <div className="relative w-32 h-8">
              <Image src={process.env.NEXT_PUBLIC_LOGO_URL || "/logo.png"} alt="Hyperverge" fill className="object-contain" priority />
            </div>
            <div className="h-6 w-px bg-border" />
            <h1 className="text-sm font-medium text-foreground">Agentic Finance</h1>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={toggleTheme} aria-label="Toggle theme" className="h-8 w-8 p-0">
              {theme === 'light' ? <Moon className="h-3.5 w-3.5" /> : <Sun className="h-3.5 w-3.5" />}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setShowSettings(!showSettings)} aria-label="Settings" className="h-8 w-8 p-0">
              <Settings className={cn("h-3.5 w-3.5 transition-transform", showSettings && "rotate-90")} />
            </Button>
            {messages.length > 0 && (
              <>
                <Button variant="ghost" size="sm" onClick={handleExport} className="h-8 text-xs">
                  <Download className="h-3.5 w-3.5 mr-1.5" />Export
                </Button>
                <Button variant="ghost" size="sm" onClick={clearChat} className="h-8 text-xs">
                  <Trash2 className="h-3.5 w-3.5 mr-1.5" />Clear
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      <AnimatePresence>
        {showSettings && <SettingsOverlay onClose={() => setShowSettings(false)} />}
      </AnimatePresence>
    </>
  );
}
