# VS Code MCP Configuration - Complete Setup Guide

This guide covers the complete setup of Model Context Protocol (MCP) integration with VS Code, GitHub Copilot, and KiloCoder for SampleMind AI.

## 🎯 Overview

You now have a fully configured VS Code environment with three AI providers using the latest and most advanced LLM versions:

1. **Google AI (Gemini 2.5 Pro)** - Primary provider for audio analysis (2M token context)
2. **Anthropic (Claude Sonnet 4.5 / Opus 4.1)** - Specialist for production coaching (200K context)
   - **Sonnet 4.5**: Standard production workflows, mixing advice, creative suggestions
   - **Opus 4.1**: Complex music theory, advanced composition, deep analysis
3. **OpenAI (GPT-5 / GPT-4.5 Turbo)** - General-purpose fallback (256K context)
   - **GPT-5**: Complex code generation, advanced reasoning
   - **GPT-4.5 Turbo**: Fast standard tasks, cost-effective

## 📋 What Was Configured

### 1. VS Code Settings (`~/.config/Code/User/settings.json`)

✅ **General Settings**

- Editor formatting and code actions
- File auto-save and cleanup
- Python and TypeScript configurations
- Git integration

✅ **GitHub Copilot Integration**

- Multi-model support for all three providers
- Intelligent routing based on task type
- Tool commands and MCP servers
- Security restrictions and safeguards

✅ **KiloCoder Configuration**

- Multi-model selection with fallback chains
- Custom instructions for SampleMind AI context
- Capability-based routing rules
- Command permissions and security

✅ **AI Provider Configurations**

- API endpoints and authentication
- Rate limiting and timeout settings
- Model-specific parameters
- Cost optimization features

### 2. MCP Servers (`scripts/mcp-servers/`)

✅ **Google AI Server** (`google-ai-server.js`)

- Text generation
- Audio analysis with production insights

✅ **Anthropic Server** (`anthropic-server.js`)

- Production coaching
- Music theory analysis
- Creative suggestions

✅ **OpenAI Server** (`openai-server.js`)

- Code generation
- Debugging assistance
- General queries

## 🚀 Getting Started

### Step 1: Install MCP Server Dependencies

```bash
cd scripts/mcp-servers
npm install
```

This installs:

- `@google/generative-ai` v0.17.0
- `@anthropic-ai/sdk` v0.27.0
- `openai` v4.56.0
- `@modelcontextprotocol/sdk` v0.5.0

### Step 2: Verify Environment Variables

Check your `.env` file contains:

```bash
# Google AI (Primary)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Anthropic (Specialist)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI (Fallback)
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Reload VS Code

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Developer: Reload Window"
3. Press Enter

### Step 4: Verify Configuration

Check that MCP servers are running:

1. Open VS Code Output panel (`Ctrl+Shift+U`)
2. Select "GitHub Copilot" from dropdown
3. Look for MCP server connection messages

## 💡 How to Use

### Intelligent Routing

The system automatically routes your requests to the best AI provider:

#### Audio Analysis → Gemini

```
Analyze the genre and BPM of this audio file
```

**Why Gemini?** Fastest inference, optimized for audio analysis

#### Production Coaching → Claude

```
Give me mixing tips for my EDM track
```

**Why Claude?** Expert music production knowledge, FL Studio specialist

#### Code Help → GPT-4

```
Generate a Python function to process audio files
```

**Why GPT-4?** Strong coding abilities, general-purpose fallback

### Using GitHub Copilot Chat

#### Example 1: Audio Analysis

```
@workspace I have an audio file at /path/to/audio.wav.
Can you analyze the genre, BPM, and key?
```

→ Routed to **Gemini** for fast audio analysis

#### Example 2: Production Advice

```
@workspace My kick and bass are clashing.
How can I fix the low-end in my mix?
```

→ Routed to **Claude** for expert production coaching

#### Example 3: Code Generation

```
@workspace Create a FastAPI endpoint that processes
uploaded audio files and returns analysis results
```

→ Routed to **GPT-4** for code generation

### Using KiloCoder

KiloCoder automatically uses the configured multi-model system:

1. **Start a Task**: KiloCoder analyzes the request
2. **Intelligent Routing**: Routes to appropriate provider
3. **Fallback Handling**: Switches providers if one fails
4. **Todo Tracking**: Maintains task progress

### Direct Model Selection

You can also specify which model to use:

```json
// In your request, add model preference
{
  "model": "gemini-2.5-pro", // or "claude-sonnet-4.5" or "gpt-5"
  "prompt": "Your request here"
}
```

## 🎛️ Configuration Details

### Model Capabilities

| Feature              | Gemini    | Claude | GPT-4  |
| -------------------- | --------- | ------ | ------ |
| Audio Analysis       | ⭐⭐⭐    | ⭐⭐   | ⭐     |
| Genre Classification | ⭐⭐⭐    | ⭐⭐   | ⭐⭐   |
| Production Coaching  | ⭐⭐      | ⭐⭐⭐ | ⭐⭐   |
| Music Theory         | ⭐⭐      | ⭐⭐⭐ | ⭐⭐   |
| Creative Ideas       | ⭐⭐      | ⭐⭐⭐ | ⭐⭐   |
| Code Generation      | ⭐⭐      | ⭐⭐   | ⭐⭐⭐ |
| Debugging            | ⭐⭐      | ⭐⭐   | ⭐⭐⭐ |
| Speed                | ⭐⭐⭐    | ⭐⭐   | ⭐⭐   |
| Context Window       | 2M tokens | 200K   | 256K   |

### Routing Rules

Configured in `settings.json`:

```json
"kilo-code.routingRules": {
  "audio": "gemini-2.5-pro",
  "genre": "gemini-2.5-pro",
  "production": "claude-sonnet-4.5",
  "coaching": "claude-sonnet-4.5",
  "creative": "claude-sonnet-4.5",
  "music-theory": "claude-opus-4.1",
  "code": "gpt-5",
  "debug": "gpt-5",
  "general": "gpt-4.5-turbo"
}
```

### Security Features

✅ **Command Restrictions**

- Dangerous commands blocked (rm -rf, sudo, etc.)
- Shell injection prevention
- Command chaining restrictions

✅ **File Access Controls**

- Workspace-only file access
- System directories protected
- Configurable deny lists

✅ **API Key Security**

- Environment variables (not in config files)
- Never committed to version control
- Loaded from .env at runtime

## 🔧 Advanced Configuration

### Customizing Model Parameters

Edit `settings.json` to adjust:

```json
"chat.agent.llmModelSelector": {
  "models": {
    "primary": {
      "temperature": 0.7,    // 0.0-1.0 (creativity)
      "maxTokens": 8192      // Response length
    }
  }
}
```

### Adding New Routing Rules

Add custom routing patterns:

```json
"kilo-code.routingRules": {
  "mastering": "claude-sonnet-4.5",
  "synthesis": "claude-sonnet-4.5",
  "testing": "gpt-5"
}
```

### Adjusting Timeouts

For slower connections:

```json
"github.copilot.toolCommands": {
  "samplemind-workspace": {
    "timeout": 15000  // milliseconds
  }
}
```

## 📊 Performance Optimization

### Response Caching

Enabled by default with 168-hour TTL:

```json
"ai.caching": {
  "enabled": true,
  "backend": "redis",
  "ttlHours": 168
}
```

### Cost Optimization

Features enabled:

- ✅ Response caching (reduces API calls)
- ✅ Intelligent routing (uses cheapest suitable model)
- ✅ Batch processing (groups similar requests)
- ✅ Rate limiting (prevents excessive usage)

### Expected Costs

| Provider | Cost/1K Tokens | Best For                   |
| -------- | -------------- | -------------------------- |
| Gemini   | $0.001-0.002   | High-volume audio analysis |
| Claude   | $0.003-0.015   | Quality production advice  |
| GPT-4    | $0.01-0.03     | Complex code tasks         |

## 🐛 Troubleshooting

### Issue: "MCP Server Not Found"

**Solution:**

```bash
cd scripts/mcp-servers
npm install
chmod +x *.js
```

### Issue: "API Key Invalid"

**Solution:**

1. Verify keys in `.env` file
2. Check for extra spaces or newlines
3. Regenerate keys if expired

### Issue: "Model Not Responding"

**Solution:**

1. Check network connectivity
2. Verify API quotas not exceeded
3. Try fallback model explicitly

### Issue: "Slow Response Times"

**Solution:**

1. Increase timeout values
2. Enable caching if disabled
3. Use faster model (Gemini) for simple tasks

## 📚 Additional Resources

- [MCP Server README](../scripts/mcp-servers/README.md)
- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [KiloCoder Guide](./KILO_CODE_SETUP.md)
- [SampleMind AI Documentation](./README.md)

## 🎓 Best Practices

### 1. Task-Appropriate Model Selection

- Use Gemini for quick audio classification
- Use Claude for in-depth production analysis
- Use GPT-4 for code-heavy tasks

### 2. Prompt Engineering

- Be specific about what you need
- Provide context about your project
- Include relevant file paths when needed

### 3. Cost Management

- Cache common queries
- Batch similar requests
- Monitor API usage regularly

### 4. Security

- Never commit API keys
- Review command auto-approvals
- Limit file access when possible

## 🚀 Next Steps

1. **Try It Out**: Ask Copilot for audio analysis help
2. **Explore Tools**: Test each MCP server's capabilities
3. **Customize**: Adjust routing rules to your workflow
4. **Monitor**: Track which models you use most
5. **Optimize**: Fine-tune settings based on usage patterns

## 💬 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review VS Code Output panel for errors
3. Consult the [MCP Server README](../scripts/mcp-servers/README.md)
4. Check API provider status pages

## ✅ Configuration Checklist

- [x] VS Code settings.json configured
- [x] MCP servers created (3 providers)
- [x] API keys in .env file
- [x] Dependencies installed
- [x] Servers made executable
- [x] Security restrictions in place
- [x] Intelligent routing configured
- [x] Caching enabled
- [x] Documentation complete

Your VS Code is now fully configured for multi-model AI assistance! 🎉
