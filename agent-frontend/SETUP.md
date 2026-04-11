# Setup Guide

Complete setup instructions for the Agentic Finance frontend.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 9.0.0 or higher (comes with Node.js)
- **Git**: For version control

Check your versions:

```bash
node --version  # Should be v18.0.0 or higher
npm --version   # Should be 9.0.0 or higher
```

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd agent-frontend
```

### 2. Install Dependencies

```bash
npm install
```

This will install all required packages including:
- Next.js
- React
- TypeScript
- Tailwind CSS
- Zustand
- Framer Motion
- Lucide React

### 3. Environment Configuration

Create a `.env.local` file in the root directory:

```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 4. Start Development Server

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

## Development Workflow

### Running the Application

```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

### Project Structure Overview

```
agent-frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout with fonts
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── chat/              # Chat interface
│   │   ├── execution/         # Agent execution visualization
│   │   ├── layout/            # Layout components
│   │   └── ui/                # Reusable UI components
│   ├── store/                 # State management
│   ├── lib/                   # Utilities and API
│   └── types/                 # TypeScript definitions
├── public/                    # Static assets
└── [config files]             # Configuration files
```

## Customization

### Changing Colors

Edit `tailwind.config.ts`:

```typescript
colors: {
  background: "#0A0A0A",    // Your background color
  foreground: "#FFFFFF",    // Your text color
  primary: {
    DEFAULT: "#A78BFA",     // Your primary color
    light: "#C4B5FD",       // Lighter variant
  },
  // ... more colors
}
```

### Changing Fonts

Edit `src/app/layout.tsx`:

```typescript
import { YourFont } from 'next/font/google';

const yourFont = YourFont({
  subsets: ['latin'],
  variable: '--font-your-font',
});
```

Then update `tailwind.config.ts`:

```typescript
fontFamily: {
  sans: ['var(--font-your-font)', 'sans-serif'],
}
```

### Adding New Components

1. Create component file in appropriate directory
2. Export component
3. Import and use in parent component

Example:

```typescript
// src/components/ui/NewComponent.tsx
export function NewComponent() {
  return <div>New Component</div>;
}

// Usage
import { NewComponent } from '@/components/ui/NewComponent';
```

## Backend Integration

### Using Mock API (Default)

The application comes with a mock API for demonstration. No backend required.

### Connecting to Real Backend

1. Update `src/lib/mockApi.ts` or create new API client
2. Implement streaming connection (SSE or WebSocket)
3. Update event handlers in `src/store/chatStore.ts`

Example SSE implementation:

```typescript
// src/lib/api.ts
export async function* streamChat(message: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const events = chunk.split('\n\n');

    for (const event of events) {
      if (event.startsWith('data: ')) {
        yield JSON.parse(event.slice(6));
      }
    }
  }
}
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Configure environment variables
4. Deploy

```bash
# Or use Vercel CLI
npm i -g vercel
vercel
```

### Docker

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

Build and run:

```bash
docker build -t agent-frontend .
docker run -p 3000:3000 agent-frontend
```

### Static Export

For static hosting (Netlify, Cloudflare Pages):

```bash
npm run build
```

Output will be in `.next/` directory.

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

### Module Not Found

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

### TypeScript Errors

```bash
# Check types
npx tsc --noEmit

# Fix auto-fixable issues
npm run lint -- --fix
```

## Performance Optimization

### Bundle Analysis

```bash
# Install analyzer
npm install --save-dev @next/bundle-analyzer

# Add to next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer(nextConfig)

# Analyze
ANALYZE=true npm run build
```

### Image Optimization

Use Next.js Image component:

```typescript
import Image from 'next/image';

<Image
  src="/hero.png"
  alt="Hero"
  width={800}
  height={600}
  priority
/>
```

## Testing

### Unit Tests (Optional)

Install testing libraries:

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
```

Create test file:

```typescript
// src/components/ui/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

test('renders button', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

## Support

For issues or questions:

1. Check existing documentation
2. Review API.md for integration details
3. Check browser console for errors
4. Open an issue on the repository

## Next Steps

1. Customize colors and fonts to match your brand
2. Integrate with your backend API
3. Add authentication if required
4. Deploy to production
5. Monitor performance and user feedback

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Framer Motion Documentation](https://www.framer.com/motion/)
