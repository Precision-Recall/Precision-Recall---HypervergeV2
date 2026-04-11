# Agentic Finance - Multi-Agent Financial Assistant

A production-grade frontend for an Agentic Finance Chatbot Platform with real-time agent orchestration visualization.

## Features

- **Multi-Agent Orchestration Visualization**: Real-time timeline showing agent execution flow
- **Tool Call Monitoring**: Detailed view of tool invocations with input/output
- **Reasoning Trace**: Structured display of agent reasoning steps
- **Streaming Responses**: Live token streaming with smooth animations
- **Premium UI**: Clean, minimal design inspired by Hyperverge
- **Responsive Design**: Split-screen desktop view, tabbed mobile interface
- **Export Functionality**: Save chat sessions for later review

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Fonts**: Inter (body), JetBrains Mono (code)

## Design System

### Color Palette

- Background: `#0A0A0A` (deep black)
- Foreground: `#FFFFFF` (white)
- Primary: `#A78BFA` (light purple)
- Secondary: `#C4B5FD`
- Border: `#1F1F1F`
- Success: `#22C55E`
- Warning: `#F59E0B`
- Error: `#EF4444`

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to project directory
cd agent-frontend

# Install dependencies
npm install

# If you encounter peer dependency issues, use:
npm install --legacy-peer-deps

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

**Note**: If you see peer dependency warnings during installation, you can safely ignore them or use `--legacy-peer-deps` flag.

### Build for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Project Structure

```
agent-frontend/
├── src/
│   ├── app/                    # Next.js app router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── chat/              # Chat interface components
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── StreamingMessage.tsx
│   │   ├── execution/         # Agent execution components
│   │   │   ├── AgentTimeline.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   ├── ToolCallCard.tsx
│   │   │   └── ReasoningPanel.tsx
│   │   ├── layout/            # Layout components
│   │   │   ├── Header.tsx
│   │   │   └── MainLayout.tsx
│   │   └── ui/                # Base UI components
│   │       ├── Button.tsx
│   │       ├── Badge.tsx
│   │       ├── Card.tsx
│   │       ├── CodeBlock.tsx
│   │       └── textarea.tsx
│   ├── store/
│   │   └── chatStore.ts       # Zustand state management
│   ├── lib/
│   │   ├── utils.ts           # Utility functions
│   │   └── mockApi.ts         # Mock streaming API
│   ├── hooks/
│   │   └── use-textarea-resize.ts # Auto-resize textarea hook
│   └── types/
│       └── index.ts           # TypeScript type definitions
├── public/                     # Static assets
├── tailwind.config.ts         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
├── next.config.js             # Next.js configuration
└── package.json               # Dependencies
```

## Key Components

### Chat Panel

- **ChatWindow**: Scrollable message list with auto-scroll
- **ChatInput**: Advanced compound component with context-based state management
  - `ChatInputRoot`: Container with context provider
  - `ChatInputTextArea`: Auto-resizing textarea with keyboard shortcuts
  - `ChatInputSubmit`: Smart submit/stop button
- **MessageBubble**: User and assistant message display
- **StreamingMessage**: Real-time token streaming visualization

### Execution Panel

- **AgentTimeline**: Vertical timeline of agent execution
- **AgentCard**: Expandable card showing agent details
- **ToolCallCard**: Tool invocation with JSON input/output
- **ReasoningPanel**: Structured reasoning steps display

## State Management

Global state managed with Zustand:

- `messages[]`: Chat message history
- `agents[]`: Agent execution timeline
- `currentAgent`: Currently executing agent
- `isStreaming`: Streaming status
- `streamingText`: Current streaming text
- `isLoading`: Loading state

## API Integration

The application uses a mock streaming API for demonstration. To integrate with your backend:

1. Replace `src/lib/mockApi.ts` with your actual API client
2. Implement WebSocket or Server-Sent Events (SSE) for streaming
3. Update event types in `src/types/index.ts` to match your backend

### Expected Event Format

```typescript
// Agent start
{
  type: 'agent_start',
  agent: 'Portfolio Analyzer',
  data: { type: 'analyzer' },
  timestamp: Date
}

// Tool call
{
  type: 'tool_call',
  tool: 'stock_api',
  data: { input: {...} },
  timestamp: Date
}

// Token streaming
{
  type: 'token_stream',
  token: 'The market is...',
  timestamp: Date
}

// Agent complete
{
  type: 'agent_complete',
  agent: 'Portfolio Analyzer',
  data: { output: '...', executionTime: 1500 },
  timestamp: Date
}
```

## Customization

### Colors

Edit `tailwind.config.ts` to customize the color palette:

```typescript
colors: {
  background: "#0A0A0A",
  foreground: "#FFFFFF",
  primary: {
    DEFAULT: "#A78BFA",
    light: "#C4B5FD",
  },
  // ... more colors
}
```

### Fonts

Update `src/app/layout.tsx` to change fonts:

```typescript
import { YourFont } from 'next/font/google';

const yourFont = YourFont({ subsets: ['latin'] });
```

## Performance

- Code splitting with Next.js App Router
- Optimized animations with Framer Motion
- Efficient state updates with Zustand
- Lazy loading of components
- Memoized expensive computations

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT

## Support

For issues or questions, please open an issue on the repository.
