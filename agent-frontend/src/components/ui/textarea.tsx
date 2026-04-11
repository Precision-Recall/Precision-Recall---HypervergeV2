import * as React from 'react';
import { cn } from '@/lib/utils';

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: 'default' | 'unstyled';
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    return (
      <textarea
        className={cn(
          'flex w-full rounded-xl px-4 py-3 text-sm',
          'placeholder:text-foreground/40',
          'focus-visible:outline-none',
          'disabled:cursor-not-allowed disabled:opacity-50',
          variant === 'default' && [
            'border border-border bg-border text-foreground',
            'focus-visible:ring-2 focus-visible:ring-primary',
          ],
          variant === 'unstyled' && [
            'border-none bg-transparent',
            'focus-visible:ring-0 focus-visible:ring-offset-0',
            'shadow-none',
          ],
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';

export { Textarea };
