# Installation Instructions

## Prerequisites Check

Before starting, verify you have the required software:

```bash
# Check Node.js version (should be 18.0.0 or higher)
node --version

# Check npm version (should be 9.0.0 or higher)
npm --version
```

If you don't have Node.js installed:
- Download from: https://nodejs.org/
- Choose LTS version (18.x or higher)

## Step-by-Step Installation

### Step 1: Navigate to Project

```bash
cd /Users/vinothkumar/CIT/hyp/agent-frontend
```

### Step 2: Install Dependencies

This will install all required packages (Next.js, React, TypeScript, Tailwind, etc.):

```bash
npm install
```

**Expected output:**
```
added 300+ packages in 30s
```

**If you see errors:**
```bash
# Clear npm cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Step 3: Verify Installation

Check that all packages were installed:

```bash
ls node_modules | wc -l
```

Should show 300+ directories.

### Step 4: Start Development Server

```bash
npm run dev
```

**Expected output:**
```
  ▲ Next.js 14.2.3
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

### Step 5: Open in Browser

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the Agentic Finance interface!

## Verification Checklist

After installation, verify these work:

- [ ] Page loads at http://localhost:3000
- [ ] Chat input is visible
- [ ] Execution timeline panel is visible
- [ ] Can type in chat input
- [ ] Send button is clickable
- [ ] No errors in browser console (F12)

## Test the Application

### Test 1: Send a Message

1. Type "What's my portfolio performance?" in the chat input
2. Press Enter or click Send
3. Watch the execution timeline on the right
4. Verify you see:
   - Query Planner agent
   - Portfolio Analyzer agent
   - Tool calls (stock_api, portfolio_calculator)
   - Final streaming response

### Test 2: Expand Agent Card

1. Click on any agent card in the timeline
2. Verify it expands to show:
   - Reasoning steps
   - Tool calls
   - Input/output

### Test 3: View Tool Details

1. Expand an agent card
2. Click on a tool call
3. Verify you see:
   - JSON input
   - JSON output
   - Copy button

### Test 4: Export Session

1. Click "Export" button in header
2. Verify a JSON file downloads
3. Open the file - should contain messages and agents

### Test 5: Clear Chat

1. Click "Clear" button in header
2. Verify chat and timeline are cleared
3. Empty state message appears

### Test 6: Mobile View

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device
4. Verify:
   - Tabs appear (Chat | Execution)
   - Can switch between tabs
   - Layout is responsive

## Troubleshooting

### Issue: Port 3000 Already in Use

**Solution 1: Use different port**
```bash
PORT=3001 npm run dev
```

**Solution 2: Kill process on port 3000**
```bash
# On macOS/Linux
lsof -ti:3000 | xargs kill -9

# On Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue: Module Not Found

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Issue: TypeScript Errors

**Solution:**
```bash
# Check for errors
npx tsc --noEmit

# If errors persist, clear cache
rm -rf .next
npm run dev
```

### Issue: Blank Page

**Solution:**
1. Check browser console (F12) for errors
2. Verify dev server is running
3. Try hard refresh (Ctrl+Shift+R)
4. Clear browser cache

### Issue: Slow Installation

**Solution:**
```bash
# Use different registry
npm install --registry=https://registry.npmjs.org/

# Or use yarn instead
npm install -g yarn
yarn install
```

### Issue: Permission Errors

**Solution:**
```bash
# On macOS/Linux
sudo chown -R $USER:$USER node_modules
sudo chown -R $USER:$USER package-lock.json

# Then retry
npm install
```

## Build for Production

Once everything works in development:

```bash
# Create production build
npm run build

# Start production server
npm start
```

Production build should:
- Complete without errors
- Start on http://localhost:3000
- Load faster than dev mode
- Show optimized bundle sizes

## Environment Setup (Optional)

If you need to connect to a backend API:

```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

Add your API URLs:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Development Tools (Optional)

### Install React DevTools

Browser extension for debugging React:
- Chrome: https://chrome.google.com/webstore (search "React Developer Tools")
- Firefox: https://addons.mozilla.org/firefox (search "React DevTools")

### Install VS Code Extensions (Recommended)

If using VS Code:
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript and JavaScript Language Features

## Next Steps

After successful installation:

1. **Read Documentation**
   - QUICKSTART.md - 5-minute overview
   - README.md - Full documentation
   - FEATURES.md - Feature details

2. **Customize**
   - Change colors in `tailwind.config.ts`
   - Update fonts in `src/app/layout.tsx`
   - Modify components in `src/components/`

3. **Integrate Backend**
   - Read API.md for integration guide
   - Replace mock API in `src/lib/mockApi.ts`
   - Test with real backend

4. **Deploy**
   - Choose deployment platform (Vercel, Docker, etc.)
   - See SETUP.md for deployment instructions
   - Configure environment variables

## Support

If you encounter issues:

1. **Check Documentation**
   - QUICKSTART.md
   - SETUP.md
   - README.md

2. **Check Browser Console**
   - Press F12
   - Look for errors in Console tab
   - Check Network tab for failed requests

3. **Check Terminal**
   - Look for error messages
   - Check for warnings
   - Verify server is running

4. **Common Solutions**
   - Clear cache: `rm -rf .next node_modules`
   - Reinstall: `npm install`
   - Restart server: Stop and run `npm run dev` again

## Success Indicators

You've successfully installed when:

✅ `npm install` completes without errors
✅ `npm run dev` starts server
✅ Browser loads http://localhost:3000
✅ Can send messages in chat
✅ Agents appear in execution timeline
✅ Tool calls are visible
✅ Streaming responses work
✅ Export/clear buttons work
✅ No errors in browser console

## Installation Complete!

You're now ready to:
- Explore the application
- Customize the design
- Integrate with your backend
- Deploy to production

**Next:** Read QUICKSTART.md for a 5-minute tour of features.

---

**Need Help?** Check the documentation files or open an issue on the repository.
