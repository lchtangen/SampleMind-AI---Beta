# ✅ GitHub Copilot Instructions Updated

**Date:** January 6, 2025
**Action:** Replaced with KILO CODE MASTER SYSTEM PROMPT
**Status:** 🟢 Active & Ready

---

## 🎯 What Changed

### Previous Configuration
- **File:** `.github/copilot-instructions.md`
- **Content:** Basic project overview (190 lines)
- **Focus:** General tech stack and MCP servers list

### New Configuration
- **File:** `.github/copilot-instructions.md`
- **Content:** **KILO CODE MASTER SYSTEM PROMPT** (comprehensive)
- **Focus:** Complete development agent configuration

---

## 📋 What's Now Included

### 1. **Enhanced Project Context** ✅
- **Version:** 1.0.0 Phoenix Beta (January 2025)
- **Scope:** Production-ready CLI tool with planned web/mobile
- **Architecture:** Detailed backend/frontend specifications
- **Status:** Backend Production Ready | Frontend In Development

### 2. **Complete Technology Stack** ✅

#### Backend (Python 3.11-3.12)
```yaml
Core Framework:
  - FastAPI 0.118.0+ with uvloop (2-4x faster)
  - Beanie ODM (MongoDB) - IMPORTANT!
  - Redis 6.4+ caching
  - ChromaDB 1.1+ vectors

Audio Processing:
  - librosa 0.11.0
  - essentia 2.1b6.dev1110
  - torch 2.8.0+cpu

AI Providers:
  - google-generativeai 0.8.5 (Gemini 2.5 Pro)
  - anthropic 0.69.0 (Claude Sonnet 4.5, Opus 4.1)
  - openai 2.1.0 (GPT-5, GPT-4.5 Turbo)
  - ollama 0.6.0 (Local models)

CLI Interface:
  - rich 14.1.0 (Beautiful TUI)
  - typer 0.19.2 (Commands)
  - questionary 2.1.1 (Prompts)
```

#### Frontend (React + TypeScript) 🚧 IN DEVELOPMENT
```yaml
Planned Stack:
  - React 19.1+
  - TypeScript 5.9+
  - Vite 7.1+ (10x faster build)
  - Zustand 5.0+ (State)
  - TanStack Query 5.59+ (Server state)
  - Radix UI (Components)
  - Tailwind CSS 4.0+
```

### 3. **Actual Backend Architecture** ✅

#### Beanie ODM Document Models
```python
# CRITICAL: Always use Beanie ODM, not raw Motor queries!

class AudioFile(Document):
    file_id: str
    filename: str
    file_path: str
    duration: float
    sample_rate: int
    channels: int
    tags: List[str]
    uploaded_at: datetime

class Analysis(Document):
    analysis_id: str
    file_id: str  # Foreign key to AudioFile
    tempo: float
    key: str
    ai_provider: Optional[str]
    ai_summary: Optional[str]
    production_tips: List[str]
```

#### Redis Caching
```python
@redis_cache(ttl=3600, key_prefix="analysis")
async def expensive_operation(param1, param2):
    # Cached for 1 hour
    pass
```

### 4. **AI Provider Configuration** ✅

#### Provider Routing Strategy
```python
# Audio analysis → Gemini 2.5 Pro (FREE, 2M context)
if task_type in ["audio_analysis", "genre_classification"]:
    provider = "gemini-2.5-pro"

# Production coaching → Claude Sonnet 4.5 ($3/1M)
elif task_type in ["production_tips", "mixing_advice"]:
    provider = "claude-sonnet-4.5"

# Complex music theory → Claude Opus 4.1 ($15/1M)
elif task_type in ["music_theory", "harmonic_analysis"]:
    provider = "claude-opus-4.1"

# Code generation → GPT-5 ($10/1M)
elif task_type in ["code_generation", "debugging"]:
    provider = "gpt-5"
```

#### Provider Details
| Provider | Model | Context | Cost | Best For |
|----------|-------|---------|------|----------|
| 🔷 Google Gemini | gemini-2.5-pro | 2M tokens | FREE | Audio analysis, batch processing |
| 💜 Anthropic | claude-sonnet-4.5 | 200K tokens | $3/1M | Production coaching, mixing advice |
| 💎 Anthropic | claude-opus-4.1 | 200K tokens | $15/1M | Deep music theory, complex analysis |
| 🟢 OpenAI | gpt-5 | 256K tokens | $10/1M | Code generation, debugging |
| 🟢 OpenAI | gpt-4.5-turbo | 192K tokens | $2/1M | Quick tasks, cost-effective |
| 🏠 Ollama | phi3/qwen2.5 | Varies | FREE | Local, ultra-fast caching |

### 5. **Code Quality Standards** ✅

#### Enforced Python Patterns
```python
# ✅ ALWAYS:
- async def for I/O operations
- Type hints everywhere
- Pydantic validation
- Structured logging (loguru)
- Comprehensive error handling

# ❌ NEVER:
- Blocking I/O in async context
- Missing error handling
- Hardcoded secrets
- Unvalidated user input
- Raw Motor queries (use Beanie ODM!)
```

### 6. **Critical Development Guidelines** ✅

#### Backend Development:
1. ✅ Use Beanie Document models (AudioFile, Analysis, BatchJob, User)
2. ✅ Apply `@redis_cache()` decorator for expensive operations
3. ✅ Use `async def` for all I/O operations
4. ✅ Import from correct locations: `from src.samplemind.core.database.mongo import AudioFile`
5. ✅ Follow CLI interface patterns (rich Console, typer commands)

#### Frontend Planning:
1. 🚧 Mark all frontend code as "IN DEVELOPMENT"
2. 🚧 Use planned tech stack: React 19+, TypeScript 5.9+, Vite 7+
3. 🚧 Reference but don't assume implementation exists
4. 🚧 Create file structure matching planned architecture

### 7. **Project Structure** ✅
```
/home/lchta/Projects/Samplemind-AI/
├── main.py                          # CLI entry point
├── src/samplemind/
│   ├── cli/                         # Rich TUI interface
│   ├── core/
│   │   ├── analysis/                # Audio analysis modules
│   │   └── database/                # Beanie ODM, Redis, ChromaDB
│   └── integrations/                # AI provider orchestration
├── web-app/                         # 🚧 Frontend (IN DEVELOPMENT)
├── deployment/                      # Docker, Kubernetes
├── docs/                            # 29 essential docs
└── tests/                           # pytest, load tests
```

---

## 🎯 How Copilot Will Behave

### When You Ask for Code:
1. ✅ **Uses Beanie ODM** - Not raw Motor queries
2. ✅ **Implements async/await** - For all I/O operations
3. ✅ **Adds type hints** - Everywhere
4. ✅ **Validates inputs** - With Pydantic models
5. ✅ **Caches aggressively** - Using Redis decorators
6. ✅ **Routes AI intelligently** - Based on task type
7. ✅ **Handles errors gracefully** - Try/except with proper exceptions
8. ✅ **Logs with context** - Using loguru
9. ✅ **Matches actual implementation** - No hypothetical code

### When Planning Frontend:
1. 🚧 **Marks as IN DEVELOPMENT**
2. 🚧 **Uses planned tech stack** (React 19+, TypeScript 5.9+, Vite 7+)
3. 🚧 **References without assuming** implementation exists
4. 🚧 **Creates correct file structure**

---

## 🔍 Verification

### Test Copilot Understanding:

1. **Ask about tech stack:**
   ```
   @workspace What is the current backend tech stack?
   ```
   **Expected:** Should mention FastAPI, Beanie ODM, librosa 0.11, etc.

2. **Ask for database code:**
   ```
   @workspace Write code to query audio files by genre
   ```
   **Expected:** Should use Beanie ODM, not raw Motor queries

3. **Ask about AI providers:**
   ```
   @workspace Which AI provider should I use for audio analysis?
   ```
   **Expected:** Should recommend Gemini 2.5 Pro (FREE, 2M context)

4. **Ask about frontend:**
   ```
   @workspace What's the status of the web frontend?
   ```
   **Expected:** Should say "IN DEVELOPMENT" with planned stack

### Verify File Updated:
```bash
# Check file exists and has new content
cat .github/copilot-instructions.md | grep "KILO CODE MASTER SYSTEM PROMPT"

# Expected output:
# 🚀 KILO CODE MASTER SYSTEM PROMPT - SampleMind AI v1.0.0 Phoenix Beta
```

---

## 📊 Comparison

| Aspect | Previous | New (KILO CODE MASTER) |
|--------|----------|------------------------|
| **Lines** | 190 | ~867+ (comprehensive) |
| **Focus** | General overview | Complete dev agent config |
| **Tech Stack** | Basic list | Detailed versions & purposes |
| **Architecture** | Not included | Full Beanie ODM models |
| **AI Providers** | Basic list | Detailed routing strategy |
| **Code Standards** | General rules | Enforced patterns with examples |
| **Frontend** | Mixed status | Clear "IN DEVELOPMENT" status |
| **Examples** | None | Multiple workflow examples |
| **Guidelines** | Basic | Critical reminders & best practices |

---

## ✅ Benefits of Update

### 1. **Accurate Code Generation**
- Copilot now knows to use Beanie ODM (not raw Motor)
- Understands actual project structure
- Matches current implementation exactly

### 2. **Intelligent AI Routing**
- Knows which provider to use for each task type
- Understands cost implications
- Can optimize for performance and budget

### 3. **Clear Development Status**
- Backend: Production Ready ✅
- Frontend: In Development 🚧
- No confusion about what exists

### 4. **Enforced Best Practices**
- Always async/await
- Always type hints
- Always Pydantic validation
- Always Redis caching
- Always structured logging

### 5. **Comprehensive Context**
- Full tech stack with versions
- Complete architecture patterns
- Security standards (OWASP 100%)
- Performance targets (<100ms)

---

## 🚀 Next Steps

### To Use New Configuration:

1. **Reload VS Code Window** (if needed)
   ```
   Cmd+Shift+P → "Developer: Reload Window"
   ```

2. **Test Copilot Chat**
   ```
   Open Copilot Chat → Ask about project
   ```

3. **Verify Understanding**
   ```
   @workspace Explain the SampleMind AI architecture
   ```

4. **Start Coding**
   ```
   Copilot now has complete context!
   ```

---

## 📚 Documentation Links

- **Updated File:** `.github/copilot-instructions.md`
- **Source:** `docs/KILO_CODE_MASTER_SYSTEM_PROMPT.md`
- **Auto-Start Guide:** `docs/AUTO_START_SETUP.md`
- **Quick Reference:** `QUICK_START_GUIDE.md`

---

## 🏆 Status

```
✅ GitHub Copilot Instructions: UPDATED
✅ KILO CODE MASTER PROMPT: Active
✅ Complete Development Context: Loaded
✅ AI Provider Routing: Configured
✅ Code Quality Standards: Enforced
✅ Project Structure: Documented
✅ Backend Architecture: Specified
✅ Frontend Status: Clarified (IN DEVELOPMENT)
```

---

**Updated:** January 6, 2025
**Status:** 🟢 Active & Automatically Loaded
**Verification:** Open Copilot Chat and test with `@workspace` queries

**Copilot now has COMPLETE context of your SampleMind AI project!** 🚀
