import { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import { AgentStatus } from '@/types';

interface BadgeProps extends HTMLAttributes<HTMLDivElement> {
  status?: AgentStatus;
  variant?: 'default' | 'status';
}

export function Badge({ className, status, variant = 'default', children, ...props }: BadgeProps) {
  const statusColors = {
    pending: 'bg-muted/50 text-foreground/70',
    running: 'bg-primary/20 text-primary animate-pulse-slow',
    completed: 'bg-success/20 text-success',
    error: 'bg-error/20 text-error',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-lg px-2.5 py-1 text-xs font-medium',
        variant === 'status' && status ? statusColors[status] : 'bg-border text-foreground',
        className
      )}
      {...props}
    >
      {variant === 'status' && status && (
        <span className={cn('mr-1.5 h-1.5 w-1.5 rounded-full', {
          'bg-foreground/70': status === 'pending',
          'bg-primary': status === 'running',
          'bg-success': status === 'completed',
          'bg-error': status === 'error',
        })} />
      )}
      {children}
    </div>
  );
}
