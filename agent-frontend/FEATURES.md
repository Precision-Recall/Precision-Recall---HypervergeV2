# Features Documentation

Complete overview of all features in the Agentic Finance frontend.

## Core Features

### 1. Multi-Agent Orchestration Visualization

**Description**: Real-time visualization of agent execution flow in a vertical timeline.

**Components**:
- `AgentTimeline`: Main timeline container
- `AgentCard`: Individual agent execution card
- Timeline connector line with status indicators

**Features**:
- Live updates as agents execute
- Status badges (pending, running, completed, error)
- Execution time tracking
- Expandable/collapsible cards
- Smooth animations

**Usage**:
```typescript
// Automatically displays all agents from store
<AgentTimeline />
```

### 2. Tool Call Monitoring

**Description**: Detailed visualization of tool invocations with input/output inspection.

**Components**:
- `ToolCallCard`: Individual tool call display
- `CodeBlock`: Syntax-highlighted JSON viewer

**Features**:
- Expandable tool cards
- JSON input/output display
- Copy to clipboard functionality
- Execution time tracking
- Status indicators

**Data Structure**:
```typescript
interface ToolCall {
  id: string;
  name: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  status: AgentStatus;
  executionTime?: number;
}
```

### 3. Reasoning Trace

**Description**: Structured display of agent reasoning steps without exposing raw chain-of-thought.

**Components**:
- `ReasoningPanel`: Reasoning steps container

**Reasoning Types**:
- **Intent**: User intent detection
- **Planning**: Execution planning
- **Tool Call**: Tool invocation reasoning
- **Synthesis**: Result combination

**Features**:
- Icon-coded reasoning types
- Color-coded by type
- Sequential display
- Smooth animations

### 4. Streaming Responses

**Description**: Real-time token streaming with visual feedback.

**Components**:
- `StreamingMessage`: Live streaming display
- Cursor animation

**Features**:
- Character-by-character streaming
- Typing indicator
- Auto-scroll to latest content
- Smooth transitions

### 5. Chat Interface

**Description**: Clean, modern chat interface with user and assistant messages.

**Components**:
- `ChatWindow`: Message container
- `ChatInput`: Message input field
- `MessageBubble`: Individual message display

**Features**:
- Auto-scroll to latest message
- Timestamp display
- User/assistant differentiation
- Empty state with instructions
- Multi-line input support
- Enter to send (Shift+Enter for new line)

### 6. Responsive Design

**Description**: Adaptive layout for desktop and mobile devices.

**Layouts**:
- **Desktop**: Split-screen (chat left, execution right)
- **Mobile**: Tabbed interface (chat/execution tabs)

**Breakpoints**:
- Mobile: < 1024px (tabbed)
- Desktop: ≥ 1024px (split-screen)

### 7. State Management

**Description**: Global state management with Zustand.

**Store Features**:
- Message history
- Agent execution timeline
- Streaming state
- Loading state
- Event handling

**Actions**:
```typescript
- addMessage()
- updateStreamingText()
- finalizeStreamingMessage()
- handleExecutionEvent()
- clearChat()
- setLoading()
```

### 8. Export Functionality

**Description**: Export chat sessions for later review.

**Features**:
- JSON export format
- Includes messages and agents
- Timestamp metadata
- Download as file

**Export Format**:
```json
{
  "messages": [...],
  "agents": [...],
  "exportedAt": "2026-04-10T10:30:00.000Z"
}
```

## UI Components

### Base Components

#### Button
- Variants: primary, secondary, ghost
- Sizes: sm, md, lg
- Focus states
- Disabled states

#### Badge
- Status badges with color coding
- Pulse animation for running state
- Dot indicators

#### Card
- Glass effect option
- Border styling
- Consistent padding
- Hover effects

#### CodeBlock
- Syntax highlighting
- Copy to clipboard
- Language indicators
- Title support

### Chat Components

#### MessageBubble
- User/assistant styling
- Timestamp display
- Avatar icons
- Smooth animations

#### StreamingMessage
- Live typing indicator
- Cursor animation
- Real-time updates

#### ChatInput (Compound Component)
- **Compound component pattern** with context-based state
- **Auto-resize textarea** based on content
- **Smart submit button** (submit/stop states)
- **Keyboard shortcuts** (Enter to submit, Shift+Enter for new line)
- **Loading states** with automatic UI updates
- **Context inheritance** for flexible composition
- **Custom hook** for textarea resizing
- Multi-line support with max height (400px)
- Disabled state management
- Focus ring and transitions

### Execution Components

#### AgentTimeline
- Vertical timeline layout
- Empty state
- Agent counter
- Scroll container

#### AgentCard
- Expandable sections
- Status indicators
- Execution metrics
- Input/output display

#### ToolCallCard
- Nested in agent cards
- JSON viewers
- Execution time
- Status tracking

#### ReasoningPanel
- Icon-coded steps
- Color-coded types
- Sequential display
- Smooth animations

### Layout Components

#### Header
- Branding
- Export button
- Clear chat button
- Sticky positioning

#### MainLayout
- Responsive split/tab layout
- Scroll containers
- Mobile navigation

## Animations

### Framer Motion Animations

**Message Appearance**:
```typescript
initial={{ opacity: 0, y: 10 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.3 }}
```

**Agent Card Expansion**:
```typescript
initial={{ height: 0, opacity: 0 }}
animate={{ height: 'auto', opacity: 1 }}
exit={{ height: 0, opacity: 0 }}
```

**Timeline Stagger**:
```typescript
transition={{ duration: 0.3, delay: index * 0.1 }}
```

### CSS Animations

- Pulse (running state)
- Fade in
- Slide up
- Cursor blink

## Design System

### Color Palette

```css
--background: #0A0A0A
--foreground: #FFFFFF
--primary: #A78BFA
--primary-light: #C4B5FD
--border: #1F1F1F
--success: #22C55E
--warning: #F59E0B
--error: #EF4444
--muted: #404040
```

### Typography

- **Headings**: Inter Semi-Bold
- **Body**: Inter Regular
- **Code**: JetBrains Mono

### Spacing

- Consistent padding: 4px increments
- Border radius: 12px (lg), 16px (xl), 20px (2xl)
- Gap spacing: 8px, 12px, 16px, 24px

### Shadows

- Subtle shadows on cards
- Border-based depth
- Minimal elevation

## Accessibility

### Keyboard Navigation

- Tab navigation
- Enter to submit
- Escape to close modals
- Arrow keys for navigation

### Focus States

- Visible focus rings
- High contrast indicators
- Keyboard-accessible buttons

### Screen Readers

- Semantic HTML
- ARIA labels where needed
- Alt text for icons

### Color Contrast

- WCAG AA compliant
- High contrast text
- Clear status indicators

## Performance

### Optimizations

1. **Code Splitting**: Next.js automatic code splitting
2. **Lazy Loading**: Components loaded on demand
3. **Memoization**: React.memo for expensive components
4. **Virtual Scrolling**: (Future enhancement for large lists)
5. **Debouncing**: Input debouncing for search

### Bundle Size

- Next.js: ~90KB (gzipped)
- React: ~40KB (gzipped)
- Framer Motion: ~30KB (gzipped)
- Zustand: ~1KB (gzipped)
- Total: ~200KB (gzipped)

## Browser Support

### Supported Browsers

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari 14+
- Chrome Mobile 90+

### Features Used

- CSS Grid
- CSS Flexbox
- CSS Custom Properties
- ES2020 JavaScript
- WebSocket/SSE
- Clipboard API

## Security

### Best Practices

1. **Input Sanitization**: All user inputs sanitized
2. **XSS Prevention**: React's built-in protection
3. **CSRF Protection**: Token-based authentication
4. **Content Security Policy**: Strict CSP headers
5. **Data Masking**: Sensitive data masked in logs

### Environment Variables

- Never commit `.env.local`
- Use `NEXT_PUBLIC_` prefix for client-side vars
- Validate all environment variables

## Future Enhancements

### Planned Features

1. **Replay Mode**: Replay agent execution
2. **Search**: Search through chat history
3. **Filters**: Filter agents/tools by type
4. **Dark/Light Toggle**: Theme switcher
5. **Voice Input**: Speech-to-text
6. **File Upload**: Upload documents for analysis
7. **Multi-Session**: Multiple concurrent sessions
8. **Collaboration**: Real-time collaboration
9. **Analytics**: Usage analytics dashboard
10. **Notifications**: Desktop notifications

### Technical Improvements

1. **Virtual Scrolling**: For large message lists
2. **Service Worker**: Offline support
3. **WebRTC**: Peer-to-peer connections
4. **GraphQL**: Alternative API layer
5. **E2E Tests**: Playwright/Cypress tests
6. **Storybook**: Component documentation
7. **Performance Monitoring**: Real User Monitoring
8. **Error Tracking**: Sentry integration

## API Integration

See `API.md` for complete API documentation.

### Event Types Supported

- `agent_start`
- `agent_complete`
- `tool_call`
- `tool_complete`
- `reasoning`
- `token_stream`
- `error`

### Connection Methods

- Server-Sent Events (SSE)
- WebSocket
- HTTP Polling (fallback)

## Development

### Adding New Features

1. Create types in `src/types/`
2. Add store actions in `src/store/`
3. Create components in `src/components/`
4. Update documentation

### Component Guidelines

- Use TypeScript
- Add prop types
- Include JSDoc comments
- Follow naming conventions
- Use Tailwind classes
- Add animations where appropriate

### Code Style

- ESLint configuration
- Prettier formatting
- Consistent naming
- Clear comments
- Type safety

## Maintenance

### Regular Tasks

1. Update dependencies monthly
2. Review and fix security vulnerabilities
3. Monitor performance metrics
4. Review user feedback
5. Update documentation

### Monitoring

- Error rates
- Response times
- User engagement
- Browser compatibility
- Performance metrics

## Support

For questions or issues:

1. Check documentation
2. Review API.md
3. Check SETUP.md
4. Open GitHub issue
5. Contact support team
