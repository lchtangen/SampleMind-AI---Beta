# SampleMind AI — Architecture Reference

> **Version:** v3.0 (migration in progress) | **Last Updated:** 2026-03-07

---

## System Overview

SampleMind AI is a **CLI-first, offline-capable music production AI** for audio analysis,
sample management, stem separation, MIDI transcription, and AI-powered production coaching.

```
┌─────────────────────────────────────────────────────────────────┐
│                       SampleMind AI v3.0                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   CLI (main) │   TUI        │  FastAPI     │  Next.js 15        │
│   main.py    │  (Textual)   │  REST API    │  apps/web/         │
│   menu.py    │  13 screens  │  port 8000   │  port 3000         │
└──────┬───────┴──────┬───────┴──────┬───────┴─────────┬──────────┘
       │              │              │                  │
       └──────────────┴──────────────┴──────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
       ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────────┐
       │  AI Layer   │ │ Audio Engine│ │   Data Layer   │
       │ ai_manager  │ │audio_engine │ │ MongoDB        │
       │ anthropic   │ │ librosa     │ │ ChromaDB       │
       │ google      │ │ demucs      │ │ Redis          │
       │ openai      │ │ pedalboard  │ └────────────────┘
       │ ollama      │ │ basic-pitch │
       └─────────────┘ └─────────────┘
```

---

## Source Tree

```
src/samplemind/
├── __init__.py                    — package init, lazy imports, scipy patch
├── core/
│   ├── engine/
│   │   └── audio_engine.py        — BPM, key, MFCC, chroma, spectral, stems
│   ├── loader.py                  — AdvancedAudioLoader (WAV/MP3/FLAC/OGG/AAC)
│   ├── database/
│   │   └── chroma.py              — ChromaDB vector similarity search
│   └── library/
│       └── pack_creator.py        — sample pack creation + export
├── integrations/
│   ├── ai_manager.py              — multi-provider routing (v3.0 table)
│   ├── anthropic_integration.py   — Claude 3.7 Sonnet + extended thinking
│   ├── google_ai_integration.py   — Gemini 2.0 Flash (google-genai SDK)
│   ├── openai_integration.py      — GPT-4o
│   ├── ollama_integration.py      — offline Ollama provider (qwen2.5, phi3, gemma2)
│   ├── agents/                    — LangGraph multi-agent system (P3 — pending)
│   └── daw/
│       └── fl_studio_plugin.py    — FL Studio integration
├── interfaces/
│   ├── cli/
│   │   ├── menu.py                — main CLI (~2255 lines, Rich + Typer)
│   │   └── commands/
│   │       └── effects.py         — Effects chain CLI commands
│   ├── tui/
│   │   ├── app.py                 — Textual TUI app entry
│   │   ├── main.py                — TUI launcher
│   │   └── screens/               — 13 screens (Textual ^0.87 migration pending)
│   │       ├── main_screen.py
│   │       ├── analyze_screen.py
│   │       ├── batch_screen.py
│   │       ├── results_screen.py
│   │       ├── library_screen.py
│   │       ├── favorites_screen.py
│   │       ├── settings_screen.py
│   │       ├── comparison_screen.py
│   │       ├── search_screen.py
│   │       ├── tagging_screen.py
│   │       ├── performance_screen.py
│   │       ├── chain_screen.py
│   │       └── classification_screen.py
│   └── api/                       — FastAPI router layer
│       ├── audio.py               — audio analysis endpoints
│       ├── library.py             — library management
│       └── ai.py                  — AI analysis endpoints
├── server/
│   └── main.py                    — FastAPI server entrypoint (uvicorn)
├── ai/                            — AI utilities and helpers
└── services/                      — business logic layer

main.py                            — CLI entry point
pyproject.toml                     — Poetry config, all deps

plugins/                           — DAW plugins
├── fl_studio_plugin.py            — Python wrapper
├── fl_studio/
│   └── cpp/                       — C++ JUCE plugin
└── ableton/
    ├── python_backend.py          — FastAPI backend for M4L
    └── communication.js           — Max for Live JS bridge

apps/
└── web/                           — Next.js 15 (Phase 15 P2 — not yet created)
```

---

## AI Layer

### Provider Priority (v3.0)

```
Priority 0: Ollama    → INSTANT / OFFLINE   QUICK_ANALYSIS only (<100ms, no API key)
Priority 1: Anthropic → PRIMARY             deep analysis, extended thinking
Priority 2: Google    → FAST                genre/rhythm, streaming
Priority 3: OpenAI    → AGENTS / FALLBACK   tool use, agent workflows
```

### Routing Table (`ai_manager.py`)

```python
ANALYSIS_ROUTING = {
    AnalysisType.PRODUCTION_COACHING:     AIProvider.ANTHROPIC,
    AnalysisType.CREATIVE_SUGGESTIONS:    AIProvider.ANTHROPIC,
    AnalysisType.FL_STUDIO_OPTIMIZATION:  AIProvider.ANTHROPIC,
    AnalysisType.MIXING_MASTERING:        AIProvider.ANTHROPIC,
    AnalysisType.ARRANGEMENT_ADVICE:      AIProvider.ANTHROPIC,
    AnalysisType.COMPREHENSIVE_ANALYSIS:  AIProvider.ANTHROPIC,
    AnalysisType.HARMONIC_ANALYSIS:       AIProvider.ANTHROPIC,
    AnalysisType.GENRE_CLASSIFICATION:    AIProvider.GOOGLE_AI,
    AnalysisType.RHYTHM_ANALYSIS:         AIProvider.GOOGLE_AI,
    AnalysisType.QUICK_ANALYSIS:          AIProvider.OLLAMA,
}
```

### SDK Patterns (v3.0 — use these patterns everywhere)

```python
# Anthropic ^0.40.0 — extended thinking for claude-3-7-sonnet
from anthropic import AsyncAnthropic
client = AsyncAnthropic(api_key=key)
response = await client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=8096,
    thinking={"type": "enabled", "budget_tokens": 5000},
    messages=[{"role": "user", "content": prompt}],
    # NEVER include temperature with extended thinking
)

# Google google-genai ^0.8.0 — NEVER use google-generativeai
from google import genai
from google.genai import types as genai_types
client = genai.Client(api_key=key)
response = await client.aio.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=genai_types.GenerateContentConfig(temperature=0.7),
)
text = response.text
tokens = response.usage_metadata.total_token_count

# OpenAI ^1.58.0 — gpt-4o (gpt-5 does NOT exist)
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=key)

# Ollama ^0.3.0 — offline, no API key
import ollama
client = ollama.AsyncClient(host="http://localhost:11434")
response = await client.chat(model="qwen2.5:7b-instruct", messages=[...])
text = response["message"]["content"]
```

---

## Audio Processing Stack

### Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `librosa` | `^0.11.0` | BPM, key detection, MFCC, chroma, spectral |
| `demucs` | `^4.0.0` | 6-stem source separation (htdemucs_6s) |
| `pedalboard` | `^0.9.0` | Professional audio effects (Spotify) |
| `basic-pitch` | `^0.4.0` | MIDI transcription from audio |
| `faster-whisper` | `^1.1.0` | Local speech-to-text / transcription |
| `scipy` | `^1.14.0` | Signal processing, FFT, filtering |
| `soundfile` | `^0.12.1` | Audio file I/O (WAV, FLAC, OGG) |
| `pyaudio` | `^0.2.14` | Real-time audio I/O |

### Analysis Pipeline

```
Audio File (WAV/MP3/FLAC/OGG/AAC)
     │
     ▼
AdvancedAudioLoader (loader.py)
     │
     ├── BASIC:        BPM, key, duration          (<0.5s)
     ├── STANDARD:     + MFCC, chroma, spectral     (<1s)
     ├── DETAILED:     + harmonic/percussive sep    (<2s)
     └── PROFESSIONAL: + AI analysis, BEATs class  (<5s)
                              │
                    AIManager.analyze_audio()
                         │
              ┌──────────┼──────────┐
              │          │          │
           Claude      Gemini    Ollama
         (deep)       (fast)    (instant)
```

### Demucs Stem Separation (P1-011 — pending integration)

```python
# Target integration in audio_engine.py:
class StemSeparation:
    """6-stem source separation using demucs htdemucs_6s model."""
    STEMS = ["drums", "bass", "vocals", "piano", "guitar", "other"]

    async def separate(self, audio_path: str, output_dir: str) -> dict[str, str]:
        # Returns: {"drums": "path/drums.wav", "bass": "path/bass.wav", ...}
```

---

## API Layer

### FastAPI Server

```
src/samplemind/server/main.py       ← uvicorn entrypoint
src/samplemind/interfaces/api/      ← routers
    ├── audio.py                    POST /api/v1/audio/analyze
    │                               POST /api/v1/audio/separate  (P1 — pending)
    ├── library.py                  GET  /api/v1/library/samples
    └── ai.py                       POST /api/v1/ai/analyze
```

> **Path note:** The API is at `src/samplemind/interfaces/api/` and `src/samplemind/server/`.
> There is NO `src/samplemind/api/` path — that directory does not exist.

### Running the API

```bash
make dev        # → uvicorn src.samplemind.server.main:app --reload --port 8000
```

---

## Data Layer

| Service | Driver | Port | Purpose |
|---------|--------|------|---------|
| MongoDB | `motor ^3.6.0` (async) | 27017 | Samples, packs, users, projects |
| ChromaDB | `chromadb ^0.6.0` | 8002 | Vector similarity search |
| Redis | `redis ^5.0.1` | 6379 | Caching, Celery task queue |

### ChromaDB Collections

```python
# src/samplemind/core/database/chroma.py
# Collections: per genre + global
client.get_or_create_collection("samples_electronic")
client.get_or_create_collection("samples_hiphop")
client.get_or_create_collection("samples_all")
```

---

## TUI Architecture (Textual ^0.87)

```
src/samplemind/interfaces/tui/
├── app.py          — SampleMindApp (main Textual app)
├── main.py         — entry point
└── screens/        — 13 screens
    ├── main_screen.py          — main menu
    ├── analyze_screen.py       — single file analysis
    ├── batch_screen.py         — batch processing
    ├── results_screen.py       — analysis results display
    ├── library_screen.py       — sample library browser
    ├── favorites_screen.py     — saved favorites
    ├── settings_screen.py      — app settings
    ├── comparison_screen.py    — side-by-side comparison
    ├── search_screen.py        — semantic search
    ├── tagging_screen.py       — manual tagging
    ├── performance_screen.py   — performance metrics
    ├── chain_screen.py         — effects chain builder
    └── classification_screen.py — genre classification
```

**Note:** `textual ^0.87.0` is in `pyproject.toml` but the 13 screens haven't been
updated for the new API yet. Migration guide: `docs/active/ui-ux/TUI_V3_UPGRADE_NOTES.md`

**Rule:** Never use `asyncio.run()` inside Textual event handlers — always `async def`.

---

## DAW Plugin Architecture

### FL Studio

```
plugins/fl_studio_plugin.py       — Python high-level wrapper
plugins/fl_studio/cpp/            — C++ JUCE native plugin
    ├── samplemind_wrapper.h
    └── samplemind_wrapper.cpp    — 486 lines
plugins/fl_studio/CMakeLists.txt  — build config
```

### Ableton Live

```
plugins/ableton/
├── python_backend.py    — FastAPI backend for Max for Live device
└── communication.js     — Max for Live JS bridge
```

---

## Service Ports

| Service | Port | Command |
|---------|------|---------|
| FastAPI | 8000 | `make dev` |
| Next.js | 3000 | `cd apps/web && npm run dev` |
| MongoDB | 27017 | `docker-compose up -d mongodb` |
| Redis | 6379 | `docker-compose up -d redis` |
| ChromaDB | 8002 | `docker-compose up -d chromadb` |
| Ollama | 11434 | `scripts/launch-ollama-api.sh` |
| Celery Flower | 5555 | `./scripts/start-flower.sh` |

---

## Architecture Decision Records

See `docs/active/architecture/V3_ARCHITECTURE_DECISIONS.md` for full ADRs including:

- **ADR-001:** Anthropic as PRIMARY AI provider (was Google)
- **ADR-002:** Ollama offline provider added at priority 0
- **ADR-003:** `google-genai` replaces deprecated `google-generativeai`
- **ADR-004:** Extended thinking requires `temperature` omitted (not 0.7 or 1.0)
- **ADR-005:** CLI-first architecture retained; TUI and web as supplementary interfaces
- **ADR-006:** Poetry over requirements.txt for all dependency management

---

*Architecture reference for SampleMind AI v3.0 migration. Updated: 2026-03-07.*
