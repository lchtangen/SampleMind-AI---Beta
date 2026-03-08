# AI Provider SDK Migration Log

**Phase:** 15 — v3.0 Migration
**Last Updated:** 2026-03-07 (Session 3 — all providers migrated)

---

## Provider Status

| Provider | Package | Old Version | New Version | Model | Status |
|----------|---------|-------------|-------------|-------|--------|
| Anthropic | `anthropic` | `^0.7.0` | `^0.40.0` | `claude-3-7-sonnet-20250219` | ✅ Done |
| Google | `google-genai` | `google-generativeai ^0.3.0` | `^0.8.0` | `gemini-2.0-flash` | ✅ Done |
| OpenAI | `openai` | `^1.3.0` | `^1.58.0` | `gpt-4o` | ✅ Done |
| Ollama | `ollama` | `^0.1.7` | `^0.3.0` | `qwen2.5:7b-instruct` | ✅ Done — NEW |

### Provider Priority (v3.0)

```
Priority 0: Ollama  → OFFLINE/INSTANT  — QUICK_ANALYSIS only (<100ms, no API key)
Priority 1: Claude  → PRIMARY          — deep analysis, extended thinking
Priority 2: Gemini  → FAST             — genre/rhythm, streaming, multimodal
Priority 3: OpenAI  → AGENTS/FALLBACK  — tool use, agent workflows
```

---

## Anthropic — ✅ Complete

**File:** `src/samplemind/integrations/anthropic_integration.py`

### What Changed
- SDK: `^0.7.0` → `^0.40.0` (same `AsyncAnthropic` client, new models)
- Default model: `claude-3-5-sonnet-20241022` → `claude-3-7-sonnet-20250219`
- `max_tokens`: 4096 → 8096
- `temperature`: 0.7 → 1.0 (required for extended thinking)
- Extended thinking added for `claude-3-7-sonnet` only:
  ```python
  params["thinking"] = {"type": "enabled", "budget_tokens": 5000}
  # temperature NOT passed when thinking is enabled
  ```

### Updated Model Enum
```python
class ClaudeModel(Enum):
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"   # PRIMARY — extended thinking
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"   # previous default
    CLAUDE_3_5_HAIKU  = "claude-3-5-haiku-20241022"    # fast/cheap
    CLAUDE_3_OPUS     = "claude-3-opus-20240229"        # legacy
    CLAUDE_3_HAIKU    = "claude-3-haiku-20240307"       # legacy
```

### Routing
`PRODUCTION_COACHING`, `CREATIVE_SUGGESTIONS`, `FL_STUDIO_OPTIMIZATION`, `MIXING_MASTERING`,
`ARRANGEMENT_ADVICE`, `COMPREHENSIVE_ANALYSIS`, `HARMONIC_ANALYSIS` → **Anthropic**

---

## Google Gemini — ✅ Complete (Full SDK Migration)

**File:** `src/samplemind/integrations/google_ai_integration.py`

### What Changed (Breaking)
The `google-generativeai` package is **deprecated**. Full migration to `google-genai`:

```python
# BEFORE (deprecated — remove):
import google.generativeai as genai
genai.configure(api_key=key)
model = genai.GenerativeModel(model_name="gemini-pro")
response = model.generate_content(prompt)

# AFTER (v3.0):
from google import genai
from google.genai import types as genai_types
client = genai.Client(api_key=key)
response = await client.aio.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=genai_types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=4096,
        safety_settings=[
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ],
    ),
)
text = response.text
tokens = response.usage_metadata.total_token_count  # new path
```

### Updated Model Enum
```python
class GeminiModel(Enum):
    GEMINI_2_0_FLASH         = "gemini-2.0-flash"           # PRIMARY — fast, multimodal
    GEMINI_2_0_FLASH_THINKING = "gemini-2.0-flash-thinking-exp"  # reasoning
    GEMINI_1_5_PRO           = "gemini-1.5-pro"             # high context fallback
    GEMINI_1_5_FLASH         = "gemini-1.5-flash"           # legacy fast
```

### Routing
`GENRE_CLASSIFICATION`, `RHYTHM_ANALYSIS` → **Google (Gemini 2.0 Flash)**

---

## OpenAI — ✅ Complete

**File:** `src/samplemind/integrations/openai_integration.py`

### What Changed
- SDK: `^1.3.0` → `^1.58.0` (same `AsyncOpenAI` client API — minimal changes)
- Removed `GPT_5 = "gpt-5"` from enum — this model does not exist
- Default model: `GPT_5` (wrong) → `GPT_4O` (correct)
- Removed `max_completion_tokens` GPT-5 special case

### Updated Model Enum
```python
class OpenAIModel(Enum):
    GPT_4O       = "gpt-4o"        # PRIMARY — default
    GPT_4O_MINI  = "gpt-4o-mini"  # fast/cheap secondary
    GPT_4_TURBO  = "gpt-4-turbo"  # high context
    GPT_4        = "gpt-4"        # legacy fallback
    # GPT_5 removed — does not exist
```

### Added: OpenAI Agents SDK
`openai-agents ^0.0.5` added to `pyproject.toml` for agent workflows (P3 multi-agent system).

### Routing
Agent workflows and tool-use tasks → **OpenAI**

---

## Ollama — ✅ Complete (New Provider)

**File:** `src/samplemind/integrations/ollama_integration.py` (NEW)

### What Was Added
A complete offline AI provider requiring no API key. Needs `ollama serve` running locally.

```python
# Usage pattern:
from ollama_integration import OllamaMusicProducer, OllamaModel

producer = OllamaMusicProducer(
    host="http://localhost:11434",    # or OLLAMA_HOST env var
    default_model=OllamaModel.QWEN_2_5_7B,
)
result = await producer.analyze_music_comprehensive(audio_features)
available = await producer.check_availability()
```

### Model Enum
```python
class OllamaModel(Enum):
    QWEN_2_5_7B = "qwen2.5:7b-instruct"   # recommended — best quality
    PHI3_MINI   = "phi3:mini"              # fastest — lowest RAM
    GEMMA2_2B   = "gemma2:2b"             # Google model
```

### Install Models
```bash
make install-models
# Runs: ollama pull qwen2.5:7b-instruct, phi3:mini, gemma2:2b
```

### Routing
`QUICK_ANALYSIS` → **Ollama** (instant offline inference, <100ms)

---

## AI Manager Routing Table (v3.0)

**File:** `src/samplemind/integrations/ai_manager.py`

```python
ANALYSIS_ROUTING = {
    # Anthropic (PRIMARY — deep analysis)
    AnalysisType.PRODUCTION_COACHING:     AIProvider.ANTHROPIC,
    AnalysisType.CREATIVE_SUGGESTIONS:    AIProvider.ANTHROPIC,
    AnalysisType.FL_STUDIO_OPTIMIZATION:  AIProvider.ANTHROPIC,
    AnalysisType.MIXING_MASTERING:        AIProvider.ANTHROPIC,
    AnalysisType.ARRANGEMENT_ADVICE:      AIProvider.ANTHROPIC,
    AnalysisType.COMPREHENSIVE_ANALYSIS:  AIProvider.ANTHROPIC,  # was GOOGLE_AI
    AnalysisType.HARMONIC_ANALYSIS:       AIProvider.ANTHROPIC,  # was GOOGLE_AI

    # Google (FAST — classification, streaming)
    AnalysisType.GENRE_CLASSIFICATION:    AIProvider.GOOGLE_AI,
    AnalysisType.RHYTHM_ANALYSIS:         AIProvider.GOOGLE_AI,

    # Ollama (INSTANT — offline)
    AnalysisType.QUICK_ANALYSIS:          AIProvider.OLLAMA,
}
```

---

## Upcoming: Agent Framework (P3)

The following agent-related packages are now in `pyproject.toml` but not yet integrated:

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| `langgraph` | `^0.2.0` | Multi-agent workflow orchestration | ⏳ Integration pending |
| `langchain-core` | `^0.3.0` | Agent tooling abstractions | ⏳ Integration pending |
| `openai-agents` | `^0.0.5` | OpenAI Agents SDK | ⏳ Integration pending |

Target location: `src/samplemind/integrations/agents/`

---

*Updated: 2026-03-07 — Session 3. All 4 providers migrated. Ollama added as new offline provider.*
