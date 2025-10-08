# Automatic MCP Usage - Quick Reference

## 🎯 Overview

Your VS Code is now configured for **fully automatic MCP (Model Context Protocol) usage**. Both KiloCoder and GitHub Copilot will automatically use the most appropriate AI model and tools for every task without requiring approval.

## ✅ What's Auto-Enabled

### **1. Automatic MCP Server Startup**
All MCP servers start automatically when VS Code launches:
- ✅ Google AI (Gemini) - Audio analysis server
- ✅ Anthropic (Claude) - Production coaching server
- ✅ OpenAI (GPT-4) - Code generation server
- ✅ Sequential Thinking - Complex problem solving
- ✅ Filesystem Servers - Code navigation (workspace, src, tests, docs)
- ✅ Brave Search - Web search capabilities
- ✅ Puppeteer Browser - Web automation

### **2. Automatic Tool Approval**
All tools are pre-approved and used automatically:
```json
"github.copilot.chat.useTools": "always"
"github.copilot.chat.toolsAutoApprove": [
  "samplemind-workspace",
  "sequential-thinking",
  "brave-search",
  "puppeteer-browser",
  "google-ai-gemini",
  "anthropic-claude",
  "openai-gpt4"
]
```

### **3. Automatic Model Selection**
The system automatically routes to the best AI model:
```json
"chat.agent.llmModelSelector": {
  "mode": "intelligent-routing",
  "autoSelectModel": true
}
```

### **4. KiloCoder Auto-Routing**
```json
"kilo-code.mcpAutoRouting": true
"kilo-code.useMcpServers": true
```

## 🚀 How It Works

### **Automatic Routing Logic**

| Your Request | Auto-Routes To | Why |
|--------------|----------------|-----|
| "Analyze this audio file" | **Gemini** | Fast audio processing |
| "Classify the genre" | **Gemini** | Specialized classification |
| "Detect BPM and key" | **Gemini** | Efficient metadata extraction |
| "Give mixing advice" | **Claude** | Expert production coaching |
| "Suggest creative ideas" | **Claude** | High creativity, music knowledge |
| "Explain music theory" | **Claude** | Deep theoretical understanding |
| "Generate Python code" | **GPT-4** | Strong coding capabilities |
| "Debug this error" | **GPT-4** | Systematic problem-solving |
| "Refactor this function" | **GPT-4** | Code quality expertise |

### **Automatic Tool Usage**

When you ask a question, the system automatically:

1. **Analyzes** the request to determine task type
2. **Selects** the optimal AI model based on capabilities
3. **Uses** appropriate MCP tools (filesystem, search, thinking)
4. **Routes** to the selected model without asking
5. **Delivers** the response seamlessly

## 💬 Usage Examples

### **Example 1: Audio Analysis (Auto-Gemini)**
```
You: @workspace Analyze this audio sample for genre and BPM
```
✅ **Automatically:**
- Starts Gemini MCP server (if not already running)
- Uses filesystem server to locate audio file
- Routes to Gemini for fast analysis
- Returns genre and BPM detection results

### **Example 2: Production Coaching (Auto-Claude)**
```
You: @workspace My kick and bass are muddy, help me fix it
```
✅ **Automatically:**
- Starts Claude MCP server
- Routes to Claude for expert advice
- Provides mixing and EQ recommendations
- Suggests FL Studio workflow tips

### **Example 3: Code Generation (Auto-GPT-4)**
```
You: @workspace Create a FastAPI endpoint for audio upload
```
✅ **Automatically:**
- Starts GPT-4 MCP server
- Uses filesystem to understand project structure
- Routes to GPT-4 for code generation
- Generates production-ready code with tests

### **Example 4: Complex Multi-Model Task**
```
You: @workspace Analyze this audio, suggest improvements, and generate code to implement them
```
✅ **Automatically:**
- Uses Gemini for audio analysis
- Switches to Claude for production suggestions
- Routes to GPT-4 for code generation
- Uses sequential thinking for complex reasoning
- Combines all results intelligently

## 🎛️ Configuration Summary

### **GitHub Copilot Settings**
```json
"github.copilot.chat.useTools": "always"
"github.copilot.chat.experimentalTools": true
"chat.mcp.autostart": "always"
"chat.mcp.enabled": true
```

### **KiloCoder Settings**
```json
"kilo-code.mcp.enabled": true
"kilo-code.mcp.autostart": true
"kilo-code.mcp.autoApprove": true
"kilo-code.mcpAutoRouting": true
```

### **All MCP Servers**
```json
"autoApprove": true
"autoStart": true
"alwaysAllow": ["tool1", "tool2", ...]
```

## 🔍 Monitoring Automatic Usage

### **View Active MCP Servers**
1. Open VS Code Output panel: `Ctrl+Shift+U`
2. Select "GitHub Copilot" from dropdown
3. See all auto-started MCP servers and their status

### **Check Which Model Was Used**
The response will include context about which AI model processed your request, though this happens transparently in the background.

## 📊 Performance Benefits

### **Speed Improvements**
- ✅ No approval dialogs = instant responses
- ✅ Servers pre-started = no startup delays
- ✅ Intelligent routing = optimal processing speed

### **Quality Improvements**
- ✅ Always uses the best model for each task
- ✅ Automatic fallback if one model is unavailable
- ✅ Combines multiple models for complex tasks

### **Cost Optimization**
- ✅ Routes to cheaper models when appropriate
- ✅ Caches responses automatically
- ✅ Batches similar requests

## 🛠️ Advanced Features

### **Automatic Failover**
If one provider is down or rate-limited:
```
Primary (Gemini) → Specialist (Claude) → Fallback (GPT-4)
```
Happens automatically without user intervention.

### **Multi-Tool Coordination**
For complex tasks, automatically combines:
- **Sequential Thinking** - Break down problems
- **Filesystem Access** - Navigate codebase
- **Web Search** - Look up documentation
- **AI Models** - Generate solutions

### **Context Awareness**
System automatically:
- Reads relevant files from workspace
- Searches documentation when needed
- Considers previous conversation history
- Uses project-specific context

## ⚙️ Customization

### **Disable Auto-Approval (if needed)**
To require manual approval for specific tools:
```json
"github.copilot.chat.toolsAutoApprove": [
  // Remove tools you want to approve manually
]
```

### **Change Routing Priority**
Adjust which model gets priority:
```json
"chat.agent.llmModelSelector": {
  "models": {
    "primary": { "priority": 1 },  // First choice
    "specialist": { "priority": 2 },  // Second choice
    "fallback": { "priority": 3 }  // Last resort
  }
}
```

### **Add Custom Routing Rules**
Define your own routing patterns:
```json
"kilo-code.routingRules": {
  "synthesis": "claude-3-5-sonnet-20241022",
  "mastering": "claude-3-5-sonnet-20241022",
  "testing": "gpt-4-turbo"
}
```

## 🐛 Troubleshooting

### **Issue: MCP Servers Not Auto-Starting**
**Check:**
```bash
# Verify dependencies installed
cd scripts/mcp-servers && npm install

# Test server syntax
node google-ai-server.js
```

**Solution:**
```bash
# Reinstall and restart VS Code
./scripts/setup-mcp-servers.sh
# Reload VS Code: Ctrl+Shift+P → "Developer: Reload Window"
```

### **Issue: Wrong Model Being Used**
**Cause:** Routing rules may need adjustment

**Solution:**
1. Check `kilo-code.routingRules` in settings
2. Add/modify patterns for your use case
3. Reload VS Code

### **Issue: Tools Not Auto-Approved**
**Check:**
```json
"github.copilot.chat.toolsAutoApprove": [...]
```

**Solution:**
Ensure the tool name matches exactly with server name.

## 📈 Usage Statistics

Monitor your automatic MCP usage:
- **Request Distribution**: See which models handle most requests
- **Response Times**: Track average latency per model
- **Cost Tracking**: Monitor API usage across providers
- **Success Rates**: Identify if fallbacks are being triggered

## 🎓 Best Practices

### **1. Trust the Routing**
Let the system choose the model automatically. It's optimized for:
- Speed
- Quality
- Cost
- Capability matching

### **2. Be Specific in Requests**
Even though routing is automatic, clear requests help:
- ✅ "Analyze audio file for genre and BPM"
- ❌ "Check this file"

### **3. Use Natural Language**
No need to specify which model to use:
- ✅ "Give me mixing advice for this track"
- ❌ "Use Claude to give me mixing advice"

### **4. Let It Handle Complexity**
For multi-step tasks, trust the automatic coordination:
```
You: Analyze this song, suggest improvements, and generate
code to implement the changes
```
System automatically:
1. Uses Gemini for analysis
2. Uses Claude for suggestions
3. Uses GPT-4 for code
4. Coordinates results seamlessly

## ✅ Verification Checklist

- [x] All MCP servers set to `autoStart: true`
- [x] All tools added to `toolsAutoApprove` list
- [x] `useTools: "always"` enabled
- [x] `autoSelectModel: true` configured
- [x] `mcpAutoRouting: true` for KiloCoder
- [x] All API keys in `.env` file
- [x] Dependencies installed in `scripts/mcp-servers`
- [x] Servers executable (`chmod +x *.js`)

## 🚀 You're All Set!

Everything is configured for automatic MCP usage. Just:

1. **Ask your question** in Copilot Chat or KiloCoder
2. **System automatically** selects best model and tools
3. **Get your answer** with zero manual intervention

**No approvals. No model selection. Just intelligent, automatic assistance.**

Happy coding! 🎉
