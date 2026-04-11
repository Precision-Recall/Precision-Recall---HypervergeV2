# Quick Start Guide

Get up and running in 5 minutes.

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

## Installation

```bash
# 1. Navigate to project directory
cd agent-frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## First Steps

### 1. Try the Demo

The application comes with a mock API that simulates agent execution:

1. Type a message in the chat input
2. Press Enter or click Send
3. Watch the agents execute in real-time on the right panel
4. See tool calls, reasoning steps, and final response

### 2. Example Queries

Try these sample queries:

- "What's my portfolio performance?"
- "Analyze the tech sector"
- "Show me market trends"
- "Calculate my investment returns"

### 3. Explore Features

**Chat Panel (Left)**:
- Send messages
- View conversation history
- See streaming responses

**Execution Panel (Right)**:
- Watch agent timeline
- Expand agent cards
- View tool calls
- See reasoning steps

**Header**:
- Export chat session
- Clear conversation

## Project Structure

```
agent-frontend/
├── src/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   ├── store/           # State management
│   ├── lib/             # Utilities
│   └── types/           # TypeScript types
├── public/              # Static files
└── [config files]       # Configuration
```

## Key Files

- `src/app/page.tsx` - Main page
- `src/store/chatStore.ts` - State management
- `src/lib/mockApi.ts` - Mock API (replace with real API)
- `tailwind.config.ts` - Design system colors

## Customization

### Change Colors

Edit `tailwind.config.ts`:

```typescript
colors: {
  primary: {
    DEFAULT: "#YOUR_COLOR",
  },
}
```

### Connect Real Backend

Replace `src/lib/mockApi.ts` with your API client. See `API.md` for details.

## Common Commands

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm start            # Start production server
npm run lint         # Run linter

# Cleanup
rm -rf node_modules  # Remove dependencies
npm install          # Reinstall dependencies
rm -rf .next         # Clear Next.js cache
```

## Troubleshooting

**Port in use?**
```bash
PORT=3001 npm run dev
```

**Module errors?**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Build errors?**
```bash
rm -rf .next
npm run build
```

## Next Steps

1. Read `README.md` for full documentation
2. Check `API.md` for backend integration
3. Review `FEATURES.md` for complete feature list
4. See `SETUP.md` for detailed setup instructions

## Support

- Documentation: See README.md
- API Integration: See API.md
- Issues: Open GitHub issue

## Production Deployment

### Vercel (Easiest)

```bash
npm i -g vercel
vercel
```

### Docker

```bash
docker build -t agent-frontend .
docker run -p 3000:3000 agent-frontend
```

### Manual

```bash
npm run build
npm start
```

## Tips

1. **Use Chrome DevTools** to inspect component state
2. **Check browser console** for errors
3. **Use React DevTools** extension for debugging
4. **Monitor network tab** for API calls
5. **Test on mobile** using responsive mode

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com)
- [TypeScript Docs](https://www.typescriptlang.org)

---

**Ready to build?** Start customizing the components in `src/components/` and integrate with your backend API!
