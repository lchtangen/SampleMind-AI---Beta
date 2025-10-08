# AI Model Quick Reference Guide

**SampleMind AI v1.0.0 Phoenix Beta**
**Updated:** December 2024

---

## 🎯 Current Production Models

### Google AI - Gemini 2.5 Pro
```bash
MODEL=gemini-2.5-pro
```
- **Context Window:** 2M tokens (2,000,000)
- **Cost:** Free tier (50 requests/day)
- **Best For:**
  - Audio analysis and genre classification
  - Batch processing large files
  - Real-time inference with massive context
- **Speed:** ⚡⚡⚡ (Fastest)
- **Quality:** ⭐⭐⭐

### Anthropic - Claude Sonnet 4.5 (Default)
```bash
ANTHROPIC_MODEL=claude-sonnet-4.5
```
- **Context Window:** 200K tokens
- **Cost:** $3 per 1M input tokens
- **Best For:**
  - Production coaching and mixing advice
  - Creative arrangement suggestions
  - FL Studio optimization
  - General music production tasks
- **Speed:** ⚡⚡
- **Quality:** ⭐⭐⭐

### Anthropic - Claude Opus 4.1 (Complex Tasks)
```bash
ANTHROPIC_OPUS_MODEL=claude-opus-4.1
```
- **Context Window:** 200K tokens
- **Cost:** $15 per 1M input tokens
- **Best For:**
  - Deep music theory analysis
  - Advanced composition techniques
  - Complex harmonic analysis
  - Sophisticated arrangement strategies
- **Speed:** ⚡
- **Quality:** ⭐⭐⭐⭐⭐

### OpenAI - GPT-5 (Default)
```bash
OPENAI_MODEL=gpt-5
```
- **Context Window:** 256K tokens
- **Cost:** $10 per 1M input tokens
- **Best For:**
  - Complex code generation
  - Advanced debugging and analysis
  - Deep technical reasoning
  - General-purpose queries
- **Speed:** ⚡⚡
- **Quality:** ⭐⭐⭐⭐

### OpenAI - GPT-4.5 Turbo (Fast Tasks)
```bash
OPENAI_TURBO_MODEL=gpt-4.5-turbo
```
- **Context Window:** 192K tokens
- **Cost:** $2 per 1M input tokens
- **Best For:**
  - Quick code snippets
  - Fast debugging assistance
  - Simple queries
  - Cost-effective fallback
- **Speed:** ⚡⚡⚡
- **Quality:** ⭐⭐⭐

---

## 📊 Model Comparison Matrix

| Feature | Gemini 2.5 Pro | Claude Sonnet 4.5 | Claude Opus 4.1 | GPT-5 | GPT-4.5 Turbo |
|---------|----------------|-------------------|-----------------|-------|---------------|
| **Context** | 2M | 200K | 200K | 256K | 192K |
| **Audio Analysis** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Music Theory** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Production** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Code Gen** | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Cost** | FREE | $$$ | $$$$$ | $$$$ | $$ |

---

## 🎛️ Intelligent Routing Rules

### Task → Model Mapping

```json
{
  "audio": "gemini-2.5-pro",
  "genre": "gemini-2.5-pro",
  "production": "claude-sonnet-4.5",
  "coaching": "claude-sonnet-4.5",
  "creative": "claude-sonnet-4.5",
  "music-theory": "claude-opus-4.1",
  "composition": "claude-opus-4.1",
  "code": "gpt-5",
  "debug": "gpt-5",
  "general": "gpt-4.5-turbo"
}
```

### When to Use Which Model

#### Use Gemini 2.5 Pro When:
- ✅ Analyzing audio files (any size)
- ✅ Classifying genres or styles
- ✅ Batch processing multiple files
- ✅ Need massive context (2M tokens)
- ✅ Cost is a concern (free tier)

#### Use Claude Sonnet 4.5 When:
- ✅ Need production coaching
- ✅ Want creative suggestions
- ✅ Optimizing FL Studio workflow
- ✅ Standard mixing advice
- ✅ General music production tasks

#### Use Claude Opus 4.1 When:
- ✅ Deep music theory analysis needed
- ✅ Complex harmonic progressions
- ✅ Advanced composition techniques
- ✅ Sophisticated arrangement strategies
- ✅ Worth the higher cost ($15/1M)

#### Use GPT-5 When:
- ✅ Complex code generation
- ✅ Advanced debugging required
- ✅ Technical problem-solving
- ✅ Need large context (256K)

#### Use GPT-4.5 Turbo When:
- ✅ Quick simple queries
- ✅ Fast code snippets
- ✅ Cost-effective fallback
- ✅ Speed is priority

---

## 💰 Cost Optimization Strategies

### 1. Use Free Tier First
```python
# Primary: Gemini (free)
DEFAULT_MODEL=gemini-2.5-pro

# Fallback: Paid models
ANTHROPIC_MODEL=claude-sonnet-4.5
OPENAI_MODEL=gpt-5
```

### 2. Intelligent Routing
- **Audio tasks** → Gemini (free)
- **Standard production** → Claude Sonnet ($3/1M)
- **Complex theory** → Claude Opus ($15/1M) - use sparingly
- **Code tasks** → GPT-4.5 Turbo ($2/1M)

### 3. Enable Caching
```bash
AI_CACHE_ENABLED=true
AI_CACHE_TTL_HOURS=168  # 1 week
```

### 4. Batch Requests
- Combine multiple questions in one request
- Use Gemini's 2M context for large batches

### 5. Monitor Usage
```bash
# Track API costs
grep "tokens_used" logs/*.log | awk '{sum+=$2} END {print sum}'
```

---

## 🔧 Configuration Examples

### Minimal Setup (.env)
```bash
GOOGLE_AI_API_KEY=your_key
DEFAULT_MODEL=gemini-2.5-pro
```

### Balanced Setup (.env)
```bash
GOOGLE_AI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
DEFAULT_MODEL=gemini-2.5-pro
ANTHROPIC_MODEL=claude-sonnet-4.5
```

### Full Setup (.env)
```bash
# All providers
GOOGLE_AI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key

# Latest models
DEFAULT_MODEL=gemini-2.5-pro
ANTHROPIC_MODEL=claude-sonnet-4.5
ANTHROPIC_OPUS_MODEL=claude-opus-4.1
OPENAI_MODEL=gpt-5
OPENAI_TURBO_MODEL=gpt-4.5-turbo

# Caching
AI_CACHE_ENABLED=true
AI_CACHE_TTL_HOURS=168
```

---

## 🚀 Quick Start Commands

### Test All Models
```bash
cd scripts/mcp-servers
node verify-setup.js
```

### Test Specific Model
```python
from samplemind.integrations import google_ai_integration

# Gemini 2.5 Pro
analyzer = google_ai_integration.GoogleAIMusicAnalyzer()
result = analyzer.analyze_audio("test.wav")
```

### Check API Usage
```bash
# View recent API calls
tail -f logs/api_usage.log
```

---

## 📝 Migration from Old Models

### Old → New Mapping

| Old Model | New Model | Notes |
|-----------|-----------|-------|
| `claude-3-5-sonnet-20241022` | `claude-sonnet-4.5` | ✅ Auto-fallback supported |
| `gpt-4-turbo` | `gpt-5` | ✅ 2x context window |
| `gemini-2.5-pro` (1M) | `gemini-2.5-pro` (2M) | ✅ Context window upgraded |

### Backwards Compatibility

All old model identifiers still work:

```python
# Both work:
ClaudeModel.CLAUDE_3_5_SONNET  # Legacy
ClaudeModel.CLAUDE_SONNET_4_5  # Latest
```

---

## ⚠️ Important Notes

### API Availability
- **GPT-5** may not be publicly available yet - verification script includes fallback
- **Claude Sonnet 4.5 / Opus 4.1** may be in limited beta - fallback to 3.5 Sonnet
- **Gemini 2.5 Pro (2M)** should be available - fallback to 1.5 Flash

### Cost Warnings
- **Claude Opus 4.1** is 5x more expensive than Sonnet ($15 vs $3 per 1M)
- **GPT-5** is 4x more expensive than GPT-4 Turbo ($10 vs $2.50 per 1M)
- Use intelligent routing to minimize costs

### Rate Limits
- **Gemini Free Tier:** 50 requests/day
- **Paid APIs:** Check your provider dashboard

---

## 📚 Additional Resources

- **Full Upgrade Documentation:** `docs/MODEL_UPGRADE_COMPLETE.md`
- **VS Code Setup Guide:** `docs/VSCODE_MCP_SETUP_GUIDE.md`
- **MCP Servers README:** `scripts/mcp-servers/README.md`
- **Environment Config:** `.env.example`

---

**Last Updated:** December 2024
**Document Version:** 1.0
