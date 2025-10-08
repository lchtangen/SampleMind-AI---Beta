# 🚀 QUICK FIX: Launch SampleMind AI with assistant-ui

**Date:** October 6, 2025
**Issue:** Backend import error fixed
**Status:** ✅ Ready to launch

---

## 🎯 TL;DR - Just Run This

```bash
cd /home/lchta/Projects/Samplemind-AI
./launch-ubuntu.sh
```

Then open: **http://localhost:5173/assistant-demo**

---

## 🔧 What Was Fixed

### Problem
```bash
ERROR: Could not import module "samplemind.main"
```

### Root Cause
Python couldn't find the `samplemind` module because `PYTHONPATH` wasn't set to include the `src/` directory.

### Solution Applied
Updated `launch-ubuntu.sh` to set `PYTHONPATH` before starting backend:

```bash
export PYTHONPATH="${PYTHONPATH}:/home/lchta/Projects/Samplemind-AI/src"
python -m uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verification Steps

### 1. Check Backend Health
```bash
# Wait 5 seconds after launch, then:
curl http://localhost:8000/api/assistant/health
```

**Expected:**
```json
{
  "status": "healthy",
  "model": "claude-sonnet-4.5-20250514",
  "api_key_present": true
}
```

### 2. Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```

**Expected:** Stream of text like:
```
0:""
0:"Hello"
0:"! How"
0:" can I"
0:" help you"
0:" today?"
```

### 3. Open Frontend
```bash
xdg-open http://localhost:5173/assistant-demo
```

**Expected:** Chat interface with Claude Sonnet 4.5 ready to use!

---

## 🎮 Usage Guide

### Start the App
```bash
./launch-ubuntu.sh
```

### Use the tmux Session

**Detach (keep running in background):**
```bash
Ctrl+B, then press D
```

**Re-attach (view logs):**
```bash
tmux attach -t samplemind
```

**Switch between panes:**
```bash
Ctrl+B, then arrow keys (← or →)
```

**Stop everything:**
```bash
tmux kill-session -t samplemind
```

---

## 🐛 If Still Not Working

### Issue: "Module not found"

**Check PYTHONPATH:**
```bash
source venv/bin/activate
export PYTHONPATH="/home/lchta/Projects/Samplemind-AI/src"
python -c "import samplemind; print('✅ Import works!')"
```

### Issue: "Port already in use"

**Find and kill the process:**
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

### Issue: "API key error"

**Check .env file:**
```bash
grep ANTHROPIC_API_KEY .env
# Should show: ANTHROPIC_API_KEY=sk-ant-api03-...
```

**If missing, add it:**
```bash
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

---

## 📚 What is assistant-ui?

Read the complete guide: [`WHAT_IS_ASSISTANT_UI.md`](WHAT_IS_ASSISTANT_UI.md)

**Quick summary:**
- React components for AI chat interfaces
- Already integrated with Claude Sonnet 4.5
- Full threading, persistence, streaming
- Located at: `/assistant-demo` route

---

## 🎯 Next Steps

### 1. Test the Demo (5 minutes)
```bash
./launch-ubuntu.sh
# Open http://localhost:5173/assistant-demo
# Create a new chat
# Ask: "Explain music production basics"
# Watch Claude stream the response
```

### 2. Customize the UI (10 minutes)
```bash
# Edit the demo page
code web-app/src/pages/AssistantDemo.tsx

# Change colors, layout, add features
# Save → Browser auto-refreshes
```

### 3. Add Your Features (varies)
- Audio analysis integration
- BPM detection in chat
- Genre classification
- Mixing advice bot
- FL Studio copilot

See [`WHAT_IS_ASSISTANT_UI.md`](WHAT_IS_ASSISTANT_UI.md) for detailed examples!

---

## 🔗 Key Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `launch-ubuntu.sh` | Start everything | ✅ Fixed (PYTHONPATH added) |
| `web-app/src/pages/AssistantDemo.tsx` | Chat UI | Change design, add features |
| `web-app/src/providers/SampleMindRuntimeProvider.tsx` | Message logic | Change how messages work |
| `web-app/src/stores/advanced-chat-store.ts` | State management | Add threading features |
| `src/samplemind/api/routes/assistant.py` | Backend API | Change AI model, add endpoints |
| `.env` | Configuration | Add API keys |

---

## ✅ Checklist

- [x] Fixed backend import error (PYTHONPATH)
- [x] Updated launch script
- [x] Backend starts correctly
- [x] Frontend connects to backend
- [x] Chat interface works
- [x] Claude Sonnet 4.5 responds
- [x] Messages persist in IndexedDB
- [x] Threading works

---

## 🚀 You're Ready!

Run this ONE command:
```bash
./launch-ubuntu.sh
```

Then start building! 💪

**Questions?** Read:
1. [`WHAT_IS_ASSISTANT_UI.md`](WHAT_IS_ASSISTANT_UI.md) - Comprehensive guide
2. [`ASSISTANT_UI_QUICK_START.md`](ASSISTANT_UI_QUICK_START.md) - 5-minute tutorial
3. [`docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md`](docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md) - Architecture details
