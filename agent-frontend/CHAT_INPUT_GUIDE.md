# ChatInput Component Guide

## Overview

The ChatInput component uses a **compound component pattern** inspired by AI Chats, providing flexibility and reusability through context-based state management.

## Architecture

### Compound Components

The ChatInput is composed of three main parts:

1. **ChatInputRoot** - Container with context provider
2. **ChatInputTextArea** - Auto-resizing textarea
3. **ChatInputSubmit** - Smart submit/stop button

### Context-Based State

All components share state through `ChatInputContext`, allowing:
- Centralized state management
- Flexible composition
- Prop inheritance
- Custom implementations

## Basic Usage

### Simple Implementation

```tsx
import { ChatInput } from '@/components/chat/ChatInput';

export function MyChat() {
  return <ChatInput />;
}
```

This uses the default implementation with all features built-in.

## Advanced Usage

### Custom Implementation

```tsx
import { 
  ChatInputRoot, 
  ChatInputTextArea, 
  ChatInputSubmit 
} from '@/components/chat/ChatInput';

export function CustomChatInput() {
  const [value, setValue] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    // Your submit logic
    setLoading(false);
  };

  const handleStop = () => {
    // Your stop logic
    setLoading(false);
  };

  return (
    <ChatInputRoot
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onSubmit={handleSubmit}
      loading={loading}
      onStop={handleStop}
      variant="default"
      rows={1}
    >
      <ChatInputTextArea 
        placeholder="Type your message..."
        disabled={loading}
      />
      <ChatInputSubmit />
    </ChatInputRoot>
  );
}
```

## Component API

### ChatInputRoot

Container component that provides context to children.

**Props:**

```typescript
interface ChatInputProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'unstyled';
  value?: string;
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;
  onSubmit?: () => void;
  loading?: boolean;
  onStop?: () => void;
  rows?: number;
}
```

**Variants:**

- `default` - Styled with border, padding, and focus ring
- `unstyled` - Minimal styling for custom designs

**Example:**

```tsx
<ChatInputRoot
  value={input}
  onChange={(e) => setInput(e.target.value)}
  onSubmit={handleSubmit}
  loading={isLoading}
  variant="default"
>
  {/* children */}
</ChatInputRoot>
```

### ChatInputTextArea

Auto-resizing textarea with keyboard shortcuts.

**Props:**

```typescript
interface ChatInputTextAreaProps extends React.ComponentProps<typeof Textarea> {
  value?: string;
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>;
  onSubmit?: () => void;
  variant?: 'default' | 'unstyled';
}
```

**Features:**

- Auto-resize based on content
- Enter to submit (Shift+Enter for new line)
- Inherits props from context
- Max height: 400px

**Example:**

```tsx
<ChatInputTextArea 
  placeholder="Ask me anything..."
  disabled={loading}
  className="custom-class"
/>
```

### ChatInputSubmit

Smart button that switches between submit and stop states.

**Props:**

```typescript
interface ChatInputSubmitProps extends React.ComponentProps<typeof Button> {
  onSubmit?: () => void;
  loading?: boolean;
  onStop?: () => void;
}
```

**Behavior:**

- Shows **ArrowUp** icon when idle
- Shows **Square** icon when loading (with stop functionality)
- Automatically disables when input is empty
- Inherits props from context

**Example:**

```tsx
<ChatInputSubmit 
  className="custom-button-class"
/>
```

## Features

### 1. Auto-Resize Textarea

The textarea automatically adjusts height based on content:

```tsx
// Uses custom hook
const textareaRef = useTextareaResize(value, minRows);
```

**Configuration:**

- Min rows: Configurable via `rows` prop
- Max height: 400px
- Smooth transitions

### 2. Keyboard Shortcuts

**Enter** - Submit message
**Shift + Enter** - New line

```tsx
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    onSubmit();
  }
};
```

### 3. Loading States

Automatic UI updates during loading:

- Submit button → Stop button
- Textarea disabled
- Visual feedback

### 4. Context Inheritance

Child components inherit props from parent context:

```tsx
// These are equivalent:
<ChatInputRoot value={input}>
  <ChatInputTextArea />
</ChatInputRoot>

// Textarea automatically uses 'input' from context
```

## Styling

### Default Variant

```css
- Border: border-border
- Background: transparent
- Focus ring: ring-primary
- Rounded: rounded-2xl
- Padding: p-2
```

### Unstyled Variant

Minimal styling for custom designs:

```tsx
<ChatInputRoot variant="unstyled">
  <ChatInputTextArea variant="default" />
  <ChatInputSubmit />
</ChatInputRoot>
```

### Custom Styling

Override with className:

```tsx
<ChatInputRoot className="bg-custom border-custom">
  <ChatInputTextArea className="text-custom" />
  <ChatInputSubmit className="bg-custom-button" />
</ChatInputRoot>
```

## Hooks

### useTextareaResize

Custom hook for auto-resizing textarea.

**Usage:**

```tsx
import { useTextareaResize } from '@/hooks/use-textarea-resize';

function MyTextarea({ value }) {
  const textareaRef = useTextareaResize(value, 1);
  
  return <textarea ref={textareaRef} value={value} />;
}
```

**Parameters:**

- `value: string` - Current textarea value
- `minRows: number` - Minimum number of rows (default: 1)

**Returns:**

- `textareaRef: RefObject<HTMLTextAreaElement>` - Ref to attach to textarea

## Examples

### Example 1: Basic Chat Input

```tsx
import { ChatInput } from '@/components/chat/ChatInput';

export function BasicChat() {
  return (
    <div className="p-4">
      <ChatInput />
    </div>
  );
}
```

### Example 2: Custom Placeholder

```tsx
import { 
  ChatInputRoot, 
  ChatInputTextArea, 
  ChatInputSubmit 
} from '@/components/chat/ChatInput';

export function CustomPlaceholder() {
  const [input, setInput] = useState('');

  return (
    <ChatInputRoot
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onSubmit={() => console.log(input)}
    >
      <ChatInputTextArea 
        placeholder="What would you like to know about your finances?"
      />
      <ChatInputSubmit />
    </ChatInputRoot>
  );
}
```

### Example 3: With Stop Functionality

```tsx
export function ChatWithStop() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSubmit = async () => {
    setLoading(true);
    abortControllerRef.current = new AbortController();
    
    try {
      await fetch('/api/chat', {
        signal: abortControllerRef.current.signal,
        // ... other options
      });
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStop = () => {
    abortControllerRef.current?.abort();
    setLoading(false);
  };

  return (
    <ChatInputRoot
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onSubmit={handleSubmit}
      loading={loading}
      onStop={handleStop}
    >
      <ChatInputTextArea />
      <ChatInputSubmit />
    </ChatInputRoot>
  );
}
```

### Example 4: Unstyled for Custom Design

```tsx
export function CustomDesignChat() {
  const [input, setInput] = useState('');

  return (
    <div className="flex gap-2 p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl">
      <ChatInputRoot
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={() => console.log(input)}
        variant="unstyled"
      >
        <ChatInputTextArea 
          variant="default"
          className="flex-1 bg-white/10 backdrop-blur-sm text-white placeholder:text-white/50"
          placeholder="Message..."
        />
        <ChatInputSubmit className="bg-white text-purple-600 hover:bg-white/90" />
      </ChatInputRoot>
    </div>
  );
}
```

### Example 5: Multi-line Input

```tsx
export function MultilineChat() {
  const [input, setInput] = useState('');

  return (
    <ChatInputRoot
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onSubmit={() => console.log(input)}
      rows={3} // Start with 3 rows
    >
      <ChatInputTextArea 
        placeholder="Write a detailed message..."
      />
      <ChatInputSubmit />
    </ChatInputRoot>
  );
}
```

## Integration with Store

The default ChatInput integrates with Zustand store:

```tsx
export function ChatInput() {
  const [input, setInput] = useState('');
  const { 
    addMessage, 
    handleExecutionEvent, 
    finalizeStreamingMessage, 
    isLoading, 
    setLoading 
  } = useChatStore();

  const handleSubmit = async () => {
    // Add user message
    addMessage({ role: 'user', content: input });
    
    // Stream response
    for await (const event of streamChatResponse(input)) {
      handleExecutionEvent(event);
    }
    
    // Finalize
    finalizeStreamingMessage();
  };

  return (
    <ChatInputRoot
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onSubmit={handleSubmit}
      loading={isLoading}
    >
      <ChatInputTextArea />
      <ChatInputSubmit />
    </ChatInputRoot>
  );
}
```

## Accessibility

### Keyboard Navigation

- Tab to focus textarea
- Enter to submit
- Shift+Enter for new line
- Tab to submit button

### ARIA Labels

```tsx
<ChatInputTextArea 
  aria-label="Chat message input"
  aria-describedby="chat-input-hint"
/>
```

### Screen Readers

- Proper button labels
- State announcements
- Focus management

## Performance

### Optimizations

1. **Memoization**: Context value memoized
2. **Ref-based resize**: No re-renders on resize
3. **Debounced resize**: Smooth performance
4. **Lazy context**: Only creates context when needed

### Best Practices

```tsx
// ✅ Good: Single state update
const handleSubmit = () => {
  setInput('');
  processMessage(input);
};

// ❌ Bad: Multiple state updates
const handleSubmit = () => {
  setInput('');
  setLoading(true);
  setError(null);
  // ... more updates
};
```

## Troubleshooting

### Issue: Textarea not resizing

**Solution**: Ensure value is passed to useTextareaResize:

```tsx
const textareaRef = useTextareaResize(value, rows);
```

### Issue: Submit not working

**Solution**: Check that value is not empty:

```tsx
const isDisabled = !value || value.trim().length === 0;
```

### Issue: Context not working

**Solution**: Ensure children are inside ChatInputRoot:

```tsx
<ChatInputRoot {...props}>
  <ChatInputTextArea />  {/* ✅ Inside context */}
</ChatInputRoot>
<ChatInputTextArea />  {/* ❌ Outside context */}
```

## Migration Guide

### From Old ChatInput

**Before:**

```tsx
<div className="p-4">
  <form onSubmit={handleSubmit}>
    <textarea value={input} onChange={onChange} />
    <button type="submit">Send</button>
  </form>
</div>
```

**After:**

```tsx
<div className="p-4">
  <ChatInputRoot
    value={input}
    onChange={onChange}
    onSubmit={handleSubmit}
  >
    <ChatInputTextArea />
    <ChatInputSubmit />
  </ChatInputRoot>
</div>
```

## Summary

The compound component pattern provides:

✅ Flexible composition
✅ Context-based state sharing
✅ Reusable components
✅ Clean API
✅ Type safety
✅ Auto-resize functionality
✅ Loading states
✅ Keyboard shortcuts
✅ Accessibility

Perfect for building modern chat interfaces!
