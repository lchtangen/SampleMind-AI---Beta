# ⚡ Quick Start: assistant-ui Demo

Get the Claude Sonnet 4.5 chat interface running in 5 minutes!

---

## 🚀 Prerequisites

✅ Python 3.11+ with FastAPI backend running
✅ Node.js 18+ for frontend
✅ Anthropic API key (get at https://console.anthropic.com/)

---

## 📦 Step 1: Environment Setup (30 seconds)

```bash
# 1. Copy environment template
cd /home/lchta/Projects/Samplemind-AI
cp .env.example .env

# 2. Add your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE" >> .env

# 3. Add frontend config
echo "VITE_API_BASE_URL=http://localhost:8000" >> .env
```

---

## 🔌 Step 2: Register FastAPI Route (1 minute)

**Edit:** `src/samplemind/main.py`

```python
# Add this import at the top
from samplemind.api.routes.assistant import router as assistant_router

# Add this line where other routers are included
app.include_router(assistant_router, prefix="/api")
```

---

## 🎬 Step 3: Start Servers (1 minute)

**Terminal 1 - Backend:**
```bash
cd /home/lchta/Projects/Samplemind-AI
python -m uvicorn samplemind.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /home/lchta/Projects/Samplemind-AI/web-app
npm run dev
```

---

## 🌐 Step 4: Add Route to App (2 minutes)

**Edit:** `web-app/src/App.tsx` (or your router config)

```tsx
import { AssistantDemo } from './pages/AssistantDemo';

// Add to your routes
<Route path="/assistant-demo" element={<AssistantDemo />} />
```

**Or directly test at:**
```bash
# Create a temporary test file
cat > web-app/src/pages/AssistantDemoTest.tsx << 'EOF'
import { AssistantDemo } from './AssistantDemo';

export default function AssistantDemoTest() {
  return <AssistantDemo />;
}
EOF

# Then navigate to http://localhost:5173/assistant-demo
```

---

## ✅ Step 5: Test! (30 seconds)

1. Open browser: **http://localhost:5173/assistant-demo**
2. Click **"+ New Chat"**
3. Type: **"Explain FastAPI streaming in simple terms"**
4. Watch Claude Sonnet 4.5 respond in real-time! 🎉

---

## 🧪 Quick Tests

### Backend Health Check
```bash
curl http://localhost:8000/api/assistant/health
# Expected: {"status": "healthy", "model": "claude-sonnet-4.5-20250514"}
```

### Streaming Test
```bash
curl -X POST http://localhost:8000/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Say hello!"}
    ]
  }'

# Expected: Stream of text deltas
# 0:""
# 0:"Hello"
# 0:"! How"
# 0:" can I"
# ...
```

---

## 🎯 Quick Feature Tour

### 1. Multi-Threading
- Click **"+ New Chat"** to create threads
- Click threads in sidebar to switch
- Hover over thread → **Rename** (pencil icon)
- Hover over thread → **Delete** (trash icon)

### 2. Message Streaming
- Type any question → Click **"Send"**
- Watch response stream word-by-word
- All messages auto-saved to IndexedDB

### 3. Persistence Test
1. Send a few messages
2. Refresh the page (F5)
3. Your conversation is still there! ✅

### 4. Thread Management
- **Rename:** Click pencil icon, enter new name
- **Delete:** Click trash icon, confirm deletion
- **Switch:** Click any thread to load its messages

---

## 🔧 Troubleshooting

### Problem: "Cannot find module '@assistant-ui/react'"
**Solution:**
```bash
cd web-app
npm install  # Reinstall dependencies
```

### Problem: "ANTHROPIC_API_KEY not found"
**Solution:**
```bash
# Check backend .env
cat .env | grep ANTHROPIC

# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

### Problem: "Failed to fetch" error
**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/api/assistant/health

# Check CORS (should allow localhost:5173)
```

### Problem: Messages not streaming
**Solution:**
1. Check backend logs for errors
2. Verify API key is valid (test at https://console.anthropic.com/)
3. Check Network tab in DevTools for response

---

## 📊 What You Get

✅ **Claude Sonnet 4.5** - Latest AI model with 200K context
✅ **Streaming Responses** - Real-time word-by-word output
✅ **IndexedDB Storage** - 50MB+ capacity with compression
✅ **Multi-Threading** - Organize conversations by topic
✅ **Auto-Save** - Never lose your chats
✅ **Cyberpunk UI** - Beautiful glassmorphic design

---

## 🚀 Next Steps

1. **Customize UI** - Edit `AssistantDemo.tsx` for your brand
2. **Add Tools** - Integrate audio analysis tools
3. **File Uploads** - Add audio file attachments
4. **Voice Input** - Implement speech-to-text
5. **Deploy** - Use in production!

---

## 📚 Full Documentation

- **Implementation Guide:** `/docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md`
- **MCP Setup:** `/docs/MCP_SETUP_GUIDE.md`
- **IDE Comparison:** `/docs/IDE_COMPARISON_ANALYSIS.md`

---

**Ready in:** ⏱️ 5 minutes
**Status:** ✅ Production Ready
**Enjoy your AI-powered chat interface!** 🎉
