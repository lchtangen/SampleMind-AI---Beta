# 🤖 What is assistant-ui? Complete Guide for SampleMind AI

**Created:** October 6, 2025
**For:** SampleMind AI Development
**Your Question:** "What is assistant_ui and how do I use it for my project?"

---

## 📚 Table of Contents

1. [What is assistant-ui?](#what-is-assistant-ui)
2. [What You Already Have](#what-you-already-have)
3. [How It Works in Your Project](#how-it-works-in-your-project)
4. [How to Use It for Development](#how-to-use-it-for-development)
5. [Practical Development Workflow](#practical-development-workflow)
6. [Advanced Use Cases](#advanced-use-cases)
7. [API Reference](#api-reference)

---

## 🎯 What is assistant-ui?

**assistant-ui** is a React component library for building AI chat interfaces. Think of it as **"Vercel AI SDK UI components on steroids"**.

### Key Concept
```
┌─────────────────────────────────────────────────────┐
│  assistant-ui = Pre-built Chat UI Components       │
│                                                     │
│  Instead of building:                              │
│  ❌ Message bubbles from scratch                   │
│  ❌ Input boxes with send buttons                  │
│  ❌ Streaming text animations                      │
│  ❌ Thread/conversation management                 │
│                                                     │
│  You get:                                          │
│  ✅ <Thread.Messages />         - Auto-displays    │
│  ✅ <Composer.Input />          - Smart input      │
│  ✅ <Thread.ScrollToBottom />   - UX niceties      │
│  ✅ Full streaming support      - Built-in         │
│  ✅ Multi-threading             - Just works       │
└─────────────────────────────────────────────────────┘
```

### Why Use It?
- **Speed:** Build ChatGPT-like UIs in hours, not weeks
- **Best Practices:** Streaming, optimistic updates, accessibility built-in
- **Flexibility:** Works with ANY AI provider (OpenAI, Anthropic, Google, Ollama)
- **State Management:** Integrates with Zustand, Redux, or any store
- **TypeScript:** Full type safety

---

## ✅ What You Already Have

**Good news!** Your SampleMind AI project already has a **complete assistant-ui implementation** with Claude Sonnet 4.5!

### Your Current Setup (Already Built!)

#### 1. **Backend API** ✅
- **File:** `src/samplemind/api/routes/assistant.py` (258 lines)
- **What it does:** FastAPI endpoint that streams Claude Sonnet 4.5 responses
- **Endpoint:** `POST /api/assistant/chat`
- **Features:**
  - Streaming responses (real-time text)
  - Non-streaming fallback
  - Health check endpoint
  - Error handling

#### 2. **Zustand Store** ✅
- **File:** `web-app/src/stores/advanced-chat-store.ts` (340 lines)
- **What it does:** Manages all chat state
- **Features:**
  - Multi-threading (create, switch, delete threads)
  - IndexedDB persistence (survives page refresh)
  - LZ-String compression (saves storage)
  - Auto-save every message

#### 3. **Runtime Provider** ✅
- **File:** `web-app/src/providers/SampleMindRuntimeProvider.tsx` (298 lines)
- **What it does:** Connects Zustand store to assistant-ui components
- **Features:**
  - Handles new messages
  - Handles message edits
  - Handles regeneration
  - Parses streaming responses

#### 4. **Demo UI** ✅
- **File:** `web-app/src/pages/AssistantDemo.tsx` (210 lines)
- **What it does:** Full chat interface with your cyberpunk design
- **Features:**
  - Thread sidebar
  - Message display
  - Input composer
  - Welcome screen
  - Thread management (rename, delete)

#### 5. **Documentation** ✅
- `docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md` - Full architecture
- `ASSISTANT_UI_QUICK_START.md` - 5-minute setup guide
- `docs/MCP_SETUP_GUIDE.md` - MCP server integration
- `UBUNTU_ASSISTANT_UI_SETUP.md` - Ubuntu deployment guide

---

## 🔄 How It Works in Your Project

### Architecture Flow

```
┌─────────────────────────────────────────────────────────┐
│                    USER TYPES MESSAGE                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  <Composer.Input />                                     │
│  (assistant-ui component)                               │
│  - Handles user input                                   │
│  - Triggers onNew() handler                             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  SampleMindRuntimeProvider                              │
│  (Your custom provider)                                 │
│  - Receives new message                                 │
│  - Calls backend API                                    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  POST /api/assistant/chat                               │
│  (FastAPI backend)                                      │
│  - Calls Claude Sonnet 4.5                              │
│  - Streams response chunks                              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Runtime Provider (parseStreamPart)                     │
│  - Receives: 0:"text delta"                             │
│  - Updates: assistant message in real-time              │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Zustand Store (advancedChatStore)                      │
│  - Appends assistant message                            │
│  - Auto-saves to IndexedDB                              │
│  - Compresses with LZ-String                            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  <Thread.Messages />                                    │
│  (assistant-ui component)                               │
│  - Re-renders with new message                          │
│  - Shows streaming animation                            │
└─────────────────────────────────────────────────────────┘
```

### Key Files and Their Roles

| File | Role | What You Edit For |
|------|------|-------------------|
| `AssistantDemo.tsx` | **UI Layout** | Design, styling, thread sidebar, welcome screen |
| `SampleMindRuntimeProvider.tsx` | **Logic Bridge** | How messages are sent/received, error handling |
| `advanced-chat-store.ts` | **State Management** | Thread logic, persistence, data structure |
| `assistant.py` (backend) | **AI Integration** | Change AI model, prompt engineering, streaming format |

---

## 🛠️ How to Use It for Development

### Scenario 1: "I want to add music analysis features"

**Example:** User uploads a sample, assistant analyzes it

```typescript
// 1. Update your backend (assistant.py)
@router.post("/analyze-audio")
async def analyze_audio(file: UploadFile):
    # Your audio analysis logic
    analysis = await analyze_with_librosa(file)

    # Stream response with analysis
    async def generate():
        yield f'0:"Analysis Results:\\n"'
        yield f'0:"BPM: {analysis.bpm}\\n"'
        yield f'0:"Key: {analysis.key}\\n"'
        yield f'0:"Genre: {analysis.genre}"'

    return StreamingResponse(generate())

// 2. Update Runtime Provider (SampleMindRuntimeProvider.tsx)
const onAudioAnalysis = async (audioFile: File) => {
    const formData = new FormData();
    formData.append('file', audioFile);

    const response = await fetch(`${API_URL}/analyze-audio`, {
        method: 'POST',
        body: formData
    });

    // Parse streaming response same way as chat
    const reader = response.body?.getReader();
    // ... streaming logic
};

// 3. Add UI component (AssistantDemo.tsx)
<div className="audio-upload">
    <input
        type="file"
        accept="audio/*"
        onChange={(e) => onAudioAnalysis(e.target.files[0])}
    />
</div>
```

### Scenario 2: "I want to change the AI model"

```python
# File: src/samplemind/api/routes/assistant.py

# Change this line (around line 45):
model="claude-sonnet-4.5-20250514",  # Current

# To:
model="claude-opus-4.1-20250514",     # For deeper analysis
# or
model="gpt-5",                         # Switch to OpenAI
# or
model="gemini-2.5-pro",               # Switch to Google
```

**Note:** You'll need to update the client initialization:
```python
# For OpenAI
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# For Google
from google.generativeai import GenerativeModel
model = GenerativeModel("gemini-2.5-pro")
```

### Scenario 3: "I want to customize the UI design"

```tsx
// File: web-app/src/pages/AssistantDemo.tsx

// Current design (cyberpunk theme)
<div className="glass-card rounded-xl p-6 shadow-glow-purple">

// Change to minimal design
<div className="bg-white rounded-lg p-4 shadow-md">

// Or dark mode
<div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
```

**Pro tip:** Your design tokens are at `web-app/src/design-system/tokens.ts`

### Scenario 4: "I want to add system prompts for music production"

```typescript
// File: web-app/src/providers/SampleMindRuntimeProvider.tsx

// In onNew() function, before calling backend:
const systemPrompt = {
    role: "system",
    content: `You are a music production assistant specializing in:
    - Audio analysis (BPM, key, genre detection)
    - Mixing and mastering advice
    - FL Studio workflow optimization
    - Creative sound design suggestions

    Always provide practical, actionable advice.`
};

// Include in API request
const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    body: JSON.stringify({
        messages: [systemPrompt, ...messages, message]  // Add system prompt
    })
});
```

### Scenario 5: "I want to save conversations to MongoDB"

```typescript
// File: web-app/src/stores/advanced-chat-store.ts

// Add after IndexedDB save (around line 180):
const saveToMongoDB = async (threadId: string, messages: Message[]) => {
    await fetch(`${API_URL}/conversations/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            threadId,
            messages,
            userId: get().userId,  // Add user tracking
            timestamp: Date.now()
        })
    });
};

// Call it in setMessages:
setMessages: (messages) => {
    set({ messages });
    saveMessages(messages);  // IndexedDB
    saveToMongoDB(get().currentThreadId, messages);  // MongoDB
}
```

---

## 🚀 Practical Development Workflow

### Daily Development Steps

#### 1. **Start Your Servers**
```bash
# Terminal 1 - Backend
cd /home/lchta/Projects/Samplemind-AI
source venv/bin/activate
python -m uvicorn samplemind.interfaces.api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd web-app
npm run dev

# Or use the one-click launcher:
./launch-ubuntu.sh
```

#### 2. **Open the Demo**
- Browser: http://localhost:5173/assistant-demo
- You'll see the chat interface immediately

#### 3. **Make Changes (Live Reload)**

**Frontend Changes (React):**
1. Edit `AssistantDemo.tsx` or any component
2. Save file (Ctrl+S)
3. Browser auto-refreshes ✨

**Backend Changes (Python):**
1. Edit `assistant.py` or any route
2. Save file (Ctrl+S)
3. Uvicorn auto-reloads ✨

**Example Workflow:**
```bash
# Day 1: Add BPM analysis
1. Edit assistant.py → Add BPM detection endpoint
2. Save → Backend reloads
3. Edit AssistantDemo.tsx → Add "Analyze BPM" button
4. Save → Frontend reloads
5. Test in browser → Click button → See BPM result

# Day 2: Add genre classification
1. Edit assistant.py → Add genre classification
2. Update system prompt in SampleMindRuntimeProvider.tsx
3. Test conversation → Ask "What genre is this sample?"
```

#### 4. **Debug Tips**

**Backend Debugging:**
```python
# Add print statements (they show in Terminal 1)
print(f"Received message: {content}")
print(f"Claude response: {response}")

# Or use logger
from loguru import logger
logger.info("Processing message", extra={"user_message": content})
```

**Frontend Debugging:**
```typescript
// Add console.logs (they show in Browser DevTools)
console.log('Messages:', messages);
console.log('Current thread:', currentThreadId);

// Or use React DevTools
// Install: chrome://extensions → React Developer Tools
```

**Network Debugging:**
1. Open Browser DevTools (F12)
2. Go to Network tab
3. Filter: "chat"
4. See all API requests/responses
5. Check streaming chunks in real-time

---

## 🔬 Advanced Use Cases

### 1. **Audio Analysis Chat Integration**

**Goal:** User drags audio file → Assistant analyzes → Shows results in chat

```typescript
// 1. Add to AssistantDemo.tsx
const handleAudioDrop = async (file: File) => {
    // Add user message
    const userMessage = {
        role: 'user',
        content: `[Uploaded audio: ${file.name}]`
    };

    // Upload and analyze
    const formData = new FormData();
    formData.append('audio', file);

    const response = await fetch('/api/audio/analyze', {
        method: 'POST',
        body: formData
    });

    const analysis = await response.json();

    // Add assistant response
    const assistantMessage = {
        role: 'assistant',
        content: `
**Audio Analysis Results:**

🎵 **BPM:** ${analysis.bpm}
🎹 **Key:** ${analysis.key} ${analysis.mode}
🎸 **Genre:** ${analysis.genre}
📊 **Quality:** ${analysis.sample_rate}Hz, ${analysis.bit_depth}bit

**Production Tips:**
${analysis.production_tips.join('\n')}
        `
    };

    advancedChatStore.getState().setMessages([
        ...messages,
        userMessage,
        assistantMessage
    ]);
};

// 2. Add drag-drop zone
<div
    onDrop={(e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file?.type.startsWith('audio/')) {
            handleAudioDrop(file);
        }
    }}
    onDragOver={(e) => e.preventDefault()}
    className="border-2 border-dashed border-primary p-8 rounded-lg"
>
    Drop audio file here to analyze
</div>
```

### 2. **Multi-Model Comparison**

**Goal:** Ask same question to 3 different AI models, compare answers

```typescript
// SampleMindRuntimeProvider.tsx
const onMultiModelQuery = async (question: string) => {
    const models = ['claude-sonnet-4.5', 'gpt-5', 'gemini-2.5-pro'];

    const responses = await Promise.all(
        models.map(model =>
            fetch('/api/assistant/chat', {
                method: 'POST',
                body: JSON.stringify({
                    model,
                    messages: [{ role: 'user', content: question }]
                })
            }).then(r => r.json())
        )
    );

    // Display comparison
    const comparisonMessage = {
        role: 'assistant',
        content: `
## Multi-Model Comparison

**Your question:** ${question}

### Claude Sonnet 4.5
${responses[0].content}

### GPT-5
${responses[1].content}

### Gemini 2.5 Pro
${responses[2].content}
        `
    };

    setMessages([...messages, comparisonMessage]);
};
```

### 3. **Voice Input Integration**

```typescript
// Add Web Speech API
const startVoiceInput = () => {
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;

        // Send to assistant
        runtime.append({
            role: 'user',
            content: transcript
        });
    };

    recognition.start();
};

// Add button to Composer
<button onClick={startVoiceInput} className="p-2 rounded-lg">
    🎤 Voice Input
</button>
```

### 4. **Code Execution in Chat**

**Goal:** User asks "Calculate BPM of this rhythm pattern" → Execute Python code → Show result

```python
# Backend: assistant.py
@router.post("/execute-code")
async def execute_code(code: str):
    # Safely execute code (use sandbox!)
    result = exec_in_sandbox(code)
    return {"result": result}
```

```typescript
// Frontend: Detect code blocks in messages
const handleCodeExecution = async (code: string) => {
    const response = await fetch('/api/execute-code', {
        method: 'POST',
        body: JSON.stringify({ code })
    });

    const { result } = await response.json();

    // Append result to chat
    runtime.append({
        role: 'assistant',
        content: `**Execution Result:**\n\`\`\`\n${result}\n\`\`\``
    });
};
```

---

## 📖 API Reference

### Your Custom Hooks

#### `useSampleMindRuntime()`
Located in: `SampleMindRuntimeProvider.tsx`

```typescript
const runtime = useSampleMindRuntime();

// Methods:
runtime.append({ role, content })  // Add message
runtime.reload()                    // Regenerate last
runtime.edit(messageId, content)    // Edit message
```

#### `advancedChatStore`
Located in: `advanced-chat-store.ts`

```typescript
const { messages, threads, currentThreadId } = advancedChatStore();

// Methods:
createThread(name?)          // Create new thread
switchThread(id)             // Switch to thread
deleteThread(id)             // Delete thread
renameThread(id, name)       // Rename thread
setMessages(messages)        // Update messages
```

### assistant-ui Components (Available to Use)

#### Message Display
```tsx
import { ThreadPrimitive } from "@assistant-ui/react";

<ThreadPrimitive.Root>
    <ThreadPrimitive.Messages />
    <ThreadPrimitive.ScrollToBottom />
</ThreadPrimitive.Root>
```

#### Input Composer
```tsx
import { ComposerPrimitive } from "@assistant-ui/react";

<ComposerPrimitive.Root>
    <ComposerPrimitive.Input />
    <ComposerPrimitive.Send />
</ComposerPrimitive.Root>
```

#### Message Actions
```tsx
<ThreadPrimitive.Message>
    <AssistantActionBar>
        <ActionBarPrimitive.Copy />
        <ActionBarPrimitive.Reload />
        <ActionBarPrimitive.Edit />
    </AssistantActionBar>
</ThreadPrimitive.Message>
```

### Backend Endpoints (What You Built)

#### Chat Endpoint
```bash
POST /api/assistant/chat
Content-Type: application/json

{
    "messages": [
        { "role": "user", "content": "Hello!" }
    ]
}

# Response (streaming):
0:""
0:"Hello"
0:"! How"
0:" can I"
0:" help?"
e:{"type":"finish","usage":{"input_tokens":10,"output_tokens":5}}
```

#### Health Check
```bash
GET /api/assistant/health

# Response:
{
    "status": "healthy",
    "model": "claude-sonnet-4.5-20250514",
    "api_key_present": true
}
```

---

## 🎓 Learning Path

### Beginner (First Week)
1. ✅ Launch the demo (`./launch-ubuntu.sh`)
2. ✅ Chat with Claude to understand the UI
3. ✅ Read `ASSISTANT_UI_QUICK_START.md`
4. ✅ Modify a button color in `AssistantDemo.tsx`
5. ✅ Add a console.log to see messages flow

### Intermediate (Second Week)
1. ✅ Add a custom system prompt
2. ✅ Change the AI model to GPT-5
3. ✅ Add a new button that sends a pre-defined message
4. ✅ Customize the thread sidebar design
5. ✅ Add user authentication (save userId with threads)

### Advanced (Third Week)
1. ✅ Integrate audio file upload
2. ✅ Add BPM detection to chat
3. ✅ Build a multi-model comparison feature
4. ✅ Add voice input with Web Speech API
5. ✅ Create a genre classification chatbot mode

---

## 🐛 Common Issues & Solutions

### Issue 1: "Backend not starting"
```bash
# Error: Could not import module "samplemind.main"

# Fix: Use correct import path
python -m uvicorn samplemind.interfaces.api.main:app --reload --port 8000
#                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                   This is the correct path!
```

### Issue 2: "Messages not saving"
```typescript
// Check IndexedDB in DevTools
// Application → Storage → IndexedDB → samplemind-db

// Verify keys exist:
// - samplemind-thread-list
// - samplemind-thread-${id}

// Test manually:
import { get, set } from 'idb-keyval';
await set('test', 'value');
await get('test');  // Should return 'value'
```

### Issue 3: "Streaming not working"
```python
# Backend: Make sure you're using StreamingResponse
from starlette.responses import StreamingResponse

async def generate():
    yield '0:"text"'

return StreamingResponse(generate(), media_type="text/plain")
```

```typescript
// Frontend: Check parseStreamPart function
console.log('Stream chunk:', chunk);  // Should be '0:"text"'
```

### Issue 4: "API key errors"
```bash
# Check .env file
cat .env | grep ANTHROPIC_API_KEY

# Should show: ANTHROPIC_API_KEY=sk-ant-api03-...
# If not, add it:
echo "ANTHROPIC_API_KEY=your-key-here" >> .env

# Restart backend
```

---

## 📚 Next Steps

### What to Build Next?

1. **Audio Analysis Bot**
   - Drag-drop audio files
   - Assistant analyzes (BPM, key, genre)
   - Suggests production tips

2. **Music Theory Tutor**
   - Ask questions about chords, scales
   - Get music theory explanations
   - Practice with interactive exercises

3. **Sample Library Search**
   - Natural language: "Find me dark techno kicks"
   - Assistant searches your library
   - Returns matching samples

4. **Mixing Assistant**
   - Upload a mix
   - Ask "How can I improve the low end?"
   - Get EQ/compression suggestions

5. **FL Studio Copilot**
   - Ask "How do I automate filter cutoff in FL?"
   - Get step-by-step instructions
   - With screenshots/GIFs

---

## 🔗 Resources

### Documentation You Have
- `docs/ASSISTANT_UI_IMPLEMENTATION_COMPLETE.md` - Full architecture
- `ASSISTANT_UI_QUICK_START.md` - 5-minute setup
- `docs/MCP_SETUP_GUIDE.md` - MCP server integration
- `UBUNTU_ASSISTANT_UI_SETUP.md` - Ubuntu deployment

### Official Docs
- assistant-ui: https://www.assistant-ui.com/docs
- Anthropic Claude: https://docs.anthropic.com
- FastAPI: https://fastapi.tiangolo.com
- Zustand: https://zustand-demo.pmnd.rs

### Your Project Files
- Backend: `src/samplemind/api/routes/assistant.py`
- Store: `web-app/src/stores/advanced-chat-store.ts`
- Provider: `web-app/src/providers/SampleMindRuntimeProvider.tsx`
- Demo: `web-app/src/pages/AssistantDemo.tsx`

---

## 🎯 TL;DR - Quick Answer to Your Question

**What is assistant-ui?**
→ Pre-built React components for AI chat interfaces (like ChatGPT UI)

**How do I use it in my project?**
→ You already have it! It's in `AssistantDemo.tsx` with Claude Sonnet 4.5

**How do I interact with it?**
→ Run `./launch-ubuntu.sh` → Open http://localhost:5173/assistant-demo → Start chatting

**How do I develop with it?**
→ Edit `AssistantDemo.tsx` (UI), `SampleMindRuntimeProvider.tsx` (logic), `assistant.py` (AI backend)

**What can I build?**
→ Audio analysis bots, music tutors, mixing assistants, FL Studio copilots, sample search

**Where do I start?**
→ Read `ASSISTANT_UI_QUICK_START.md` → Launch demo → Modify one component → Test → Repeat

---

**You're ready to build! 🚀**

Need help with a specific feature? Ask me:
- "How do I add audio upload to the chat?"
- "How do I change the AI model?"
- "How do I save conversations to MongoDB?"
- "How do I add voice input?"

I'll give you exact code examples! 💪
