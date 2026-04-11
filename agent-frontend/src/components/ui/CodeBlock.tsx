'use client';

import { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { cn, copyToClipboard } from '@/lib/utils';

interface CodeBlockProps {
  code: string;
  language?: string;
  title?: string;
}

export function CodeBlock({ code, language = 'json', title }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await copyToClipboard(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative rounded-xl border border-border bg-background/50 overflow-hidden">
      {title && (
        <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-border/30">
          <span className="text-xs font-medium text-foreground/70">{title}</span>
          <span className="text-xs text-foreground/50">{language}</span>
        </div>
      )}
      <div className="relative">
        <pre className="p-4 overflow-x-auto text-sm font-mono text-foreground/90">
          <code>{code}</code>
        </pre>
        <button
          onClick={handleCopy}
          className={cn(
            'absolute top-2 right-2 p-2 rounded-lg transition-all duration-200',
            'bg-border/50 hover:bg-border backdrop-blur-sm',
            'focus:outline-none focus:ring-2 focus:ring-primary'
          )}
        >
          {copied ? (
            <Check className="h-4 w-4 text-success" />
          ) : (
            <Copy className="h-4 w-4 text-foreground/70" />
          )}
        </button>
      </div>
    </div>
  );
}
