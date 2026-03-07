# CLAUDE.md

Comprehensive guidance for Claude Code when working with the SampleMind AI codebase (v3.0 migration, started 2026-03-07).

> **Current date:** 2026-03-07 | **Active phase:** Phase 15 — v3.0 Upgrade & Migration | **Repo:** `lchtangen/SampleMind-AI---Beta`

---

## ⚡ Quick Start (60 Seconds)

```bash
dcd ~/Projects/SampleMind-AI---Beta   # or wherever you cloned it
git pull                              # always pull first
source .venv/bin/activate             # activate venv
python main.py                        # run CLI
```

**If `.venv` doesn't exist:**
```bash
make setup                            # creates venv + installs all deps
make install-models                   # downloads Ollama offline models
```

**To run the full stack:**
```bash
docker-compose up -d                  # databases (MongoDB, Redis, ChromaDB)
make dev                              # FastAPI server → localhost:8000
```

---

## 🧠 Architecture At-a-Glance

```
SampleMind AI — CLI-First, Offline-Capable Music Production AI
├── CLI (PRIMARY)     src/samplemind/interfaces/cli/menu.py       ← main product
├── TUI               src/samplemind/interfaces/tui/app.py        ← Textual-based
├── API               src/samplemind/api/ (FastAPI)               ← Phase 4+
├── Web UI            apps/web/ (Next.js 15)                      ← Phase 15
│
├── AI Layer          src/samplemind/integrations/ai_manager.py
│   ├── Claude 3.7 Sonnet (Anthropic) ← primary, best analysis
│   ├── Gemini 2.0 Flash (Google)     ← fast, streaming
│   ├── GPT-4o (OpenAI)               ← fallback + Agents SDK
│   └── Ollama (local)                ← offline: phi3, qwen2.5, gemma2
│
├── Audio Engine      src/samplemind/core/engine/audio_engine.py
│   ├── librosa       ← BPM, key, MFCC, chroma, spectral
│   ├── demucs v4     ← 6-stem source separation (htdemucs)
│   ├── basic-pitch   ← MIDI transcription from audio
│   ├── pedalboard    ← Spotify audio effects engine
│   └── BEATs         ← Microsoft audio classifier (transformers)
│
├── Vector DB         src/samplemind/core/database/chroma.py      ← ChromaDB
├── DAW Plugins       plugins/                                     ← FL Studio, Ableton
└── Data              MongoDB (Motor) + Redis + ChromaDB
```

---

## 📁 Key File Locations

| What | Where |
|------|-------|
| CLI entry point | `main.py` |
| Main CLI menu | `src/samplemind/interfaces/cli/menu.py` |
| Effects CLI | `src/samplemind/interfaces/cli/commands/effects.py` |
| TUI app | `src/samplemind/interfaces/tui/app.py` |
| TUI screens | `src/samplemind/interfaces/tui/screens/` |
| Audio engine | `src/samplemind/core/engine/audio_engine.py` |
| Audio loader | `src/samplemind/core/loader.py` |
| AI manager | `src/samplemind/integrations/ai_manager.py` |
| DAW plugins | `plugins/fl_studio_plugin.py`, `plugins/ableton/` |
| ChromaDB | `src/samplemind/core/database/chroma.py` |
| Project config | `pyproject.toml` |
| Dependencies | `pyproject.toml → [tool.poetry.dependencies]` |
| All docs | `docs/` (60+ files) |
| Test suite | `tests/unit/` (81 tests, ~30% coverage) |

---

## 🛠️ Development Commands

### CLI (Primary)
```bash
source .venv/bin/activate && python main.py   # run CLI
make setup                                     # full setup
make install-models                            # download Ollama models
scripts/launch-ollama-api.sh                   # start Ollama server (port 11434)
scripts/setup/quick_start.sh                   # one-command startup
```

### API + Services
```bash
make dev                  # FastAPI → localhost:8000
make dev-full             # full stack with Docker
make setup-db             # MongoDB + Redis + ChromaDB (Docker)
docker-compose up -d      # all Docker services
```

### Testing & Quality
```bash
make test       # pytest tests/ -v --cov=src --cov-report=term-missing
make lint       # ruff check . && mypy src/
make format     # black . && isort .
make security   # bandit -r src/ && safety check
make quality    # lint + security (run before every commit)
```

### Build & Deploy
```bash
make build              # build Docker image
docker-compose up -d    # start all services
make clean              # clean tmp files + caches
```

---

## 🤖 AI Providers — v3.0 Stack (2026)

### Model Selection Guide
| Task | Use | Why |
|------|-----|-----|
| Deep audio analysis + reasoning | `claude-3-7-sonnet-20250219` | Extended thinking, best accuracy |
| Fast streaming responses | `gemini-2.0-flash-exp` | Low latency, multimodal |
| Agent workflows | `gpt-4o` + OpenAI Agents SDK | Tool use, complex pipelines |
| Offline / no internet | Ollama `qwen2.5:7b-instruct` | <100ms local inference |
| Embeddings | `text-embedding-3-large` | Best semantic search quality |
| Audio transcription | `whisper-large-v3` | Local, highest accuracy |

### AI Manager Pattern
```python
# src/samplemind/integrations/ai_manager.py
manager = SampleMindAIManager()
result = await manager.analyze_audio(
    audio_path="sample.wav",
    model="claude-3-7-sonnet-20250219",   # or "gemini-2.0-flash-exp", "auto"
    analysis_level="PROFESSIONAL"
)
```

### Current Dependency Versions (MUST upgrade in Phase 15)
| Package | Current | Target v3.0 | Priority |
|---------|---------|-------------|----------|
| `anthropic` | `^0.7.0` | `^0.40.0` | 🔴 Critical |
| `openai` | `^1.3.0` | `^1.58.0` | 🔴 Critical |
| `google-generativeai` | `^0.3.0` | `^0.8.0` | 🔴 Critical |
| `textual` | `^0.44.0` | `^0.87.0` | 🔴 Critical |
| `torch` | `^2.1.0` | `^2.5.0` | 🟠 High |
| `transformers` | `^4.35.0` | `^4.47.0` | 🟠 High |
| `numpy` | `<2.0.0` cap | `>=2.0.0` | 🟠 High |
| `scipy` | `^1.11.0` | `^1.14.0` | 🟡 Medium |
| `librosa` | `^0.10.1` | `^0.11.0` | 🟡 Medium |

---

## 🎵 Audio Processing — v3.0 Stack

### Core Libraries
```python
import librosa          # BPM, key, MFCC, chroma, spectral features
import soundfile as sf  # read/write audio files (WAV, FLAC, OGG)
import numpy as np      # signal processing arrays
from scipy import signal  # filtering, FFT
```

### New v3.0 Audio Tools (to integrate)
```python
# MIDI transcription from audio
from basic_pitch import predict  # basic-pitch ^0.4.0

# Source separation (6 stems: drums, bass, vocals, piano, guitar, other)
import demucs  # demucs ^4.0.0, model: htdemucs_6s

# Professional audio effects (Spotify's pedalboard)
from pedalboard import Pedalboard, Reverb, Compressor, LowShelfFilter
import pedalboard.io as pio

# Microsoft BEATs audio classifier (via transformers)
from transformers import AutoProcessor, ASTForAudioClassification
# model: "microsoft/BEATs-iter3-AS2M"

# Real-time audio I/O
import pyaudio  # for microphone input + playback
```

### Analysis Levels
```python
# Use in audio_engine.py AnalysisLevel enum:
BASIC       # BPM, key, duration — <0.5s
STANDARD    # + MFCC, chroma, spectral — <1s
DETAILED    # + harmonic/percussive separation — <2s
PROFESSIONAL # + AI analysis, BEATs classification, embeddings — <5s
```

---

## 🖥️ TUI Development (Textual v0.87+)

### TUI Screens (implemented)
| Screen | File | Status |
|--------|------|--------|
| Main Menu | `screens/main_screen.py` | ✅ |
| Analyze | `screens/analyze_screen.py` | ✅ |
| Batch Process | `screens/batch_screen.py` | ✅ |
| Results | `screens/results_screen.py` | ✅ |
| Favorites | `screens/favorites_screen.py` | ✅ |
| Settings | `screens/settings_screen.py` | ✅ |
| Comparison | `screens/comparison_screen.py` | ✅ |
| Search | `screens/search_screen.py` | ✅ |
| Tagging | `screens/tagging_screen.py` | ✅ |
| Performance | `screens/performance_screen.py` | ✅ |
| Library | `screens/library_screen.py` | ✅ |

### TUI v3.0 New Screens (Phase 15)
- `AgentChatScreen` — multi-agent conversation UI
- `WaveformScreen` — interactive waveform viewer
- `MixingBoardScreen` — real-time effects and EQ

### Textual Best Practices
```python
# ✅ DO:
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, Input, DataTable

class AnalyzeScreen(Screen):
    BINDINGS = [("escape", "pop_screen", "Back"), ("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Path to audio file...")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        # Never block — always use async/await
        result = await self.app.analyze_audio(self.path_input.value)
        self.notify(f"✓ Analysis complete: {result.bpm} BPM")

# ❌ NEVER:
# - Use time.sleep() in any event handler
# - Call blocking I/O (os.listdir) in compose() or render()
# - Mix CSS in Python files (use *.tcss files)
# - Create components >200 lines (split into sub-widgets)
```

---

## 🔌 DAW Plugin Architecture

### FL Studio Integration
```
plugins/fl_studio_plugin.py       Python wrapper (high-level)
plugins/fl_studio/cpp/            C++ native plugin
  ├── samplemind_wrapper.h        JUCE-based header
  └── samplemind_wrapper.cpp      Implementation (486 lines)
plugins/fl_studio/CMakeLists.txt  Build configuration
```

### Ableton Live Integration
```
plugins/ableton/
  ├── python_backend.py    FastAPI backend for M4L device
  └── communication.js     Max for Live JS bridge
```

### VST3 / DAW Plugin Build
```bash
cd plugins/fl_studio/
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```

---

## 🌐 Web UI Architecture (Phase 15)

### Stack (to be implemented)
```
apps/web/
├── src/
│   ├── app/              Next.js 15 App Router
│   ├── components/
│   │   ├── audio/        AudioUpload, WaveformViewer, AnalysisCard
│   │   ├── library/      SampleBrowser, TagFilter, SearchBar
│   │   ├── effects/      EffectsChain, EQVisualizer
│   │   └── ui/           shadcn/ui components
│   ├── hooks/            useAudioAnalysis, useLibrary, usePlayback
│   ├── stores/           Zustand v5 state stores
│   └── lib/
│       └── api/          TypeScript API client (generated from OpenAPI)
├── package.json          Next.js 15, React 19, Tailwind v4
└── tailwind.config.ts    SampleMind design tokens
```

### API Integration Pattern
```typescript
// Always use the typed API client:
import { samplemindApi } from '@/lib/api'

const result = await samplemindApi.audio.analyze({
  file: audioFile,
  level: 'PROFESSIONAL',
  model: 'claude-3-7-sonnet-20250219'
})
```

---

## 🚦 Performance Targets

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| CLI startup | <1s | ~2s | ⚠️ Needs lazy imports |
| Keyboard response (TUI) | <50ms | ~50ms | ✅ OK |
| Audio analysis (BASIC) | <0.5s | ~0.5s | ✅ OK |
| Audio analysis (PROFESSIONAL) | <5s | ~3–8s | ⚠️ Variable |
| Ollama inference | <100ms | ~80ms | ✅ OK |
| Vector similarity search | <200ms | ~150ms | ✅ OK |
| API response (simple) | <100ms | ~80ms | ✅ OK |
| Web FCP (target) | <1s | Not built | ⏳ Phase 15 |

---

## 🤖 AI Tool Setup for v3.0 Work

### Which Tool For What Task

| Task | Use | Command/Note |
|------|-----|---------|
| Refactor/rewrite large files | **Claude Code** | Best at large-context edits |
| Multi-file feature implementation | **Claude Code** | Whole-codebase awareness |
| Quick code completions | **GitHub Copilot** | In VSCode, auto-suggest |
| Generate boilerplate | **Codex** (terminal) | `codex "create FastAPI endpoint"` |
| Create PRs from issues | **Copilot** (GitHub) | Use `@copilot` on issues |
| Dependency research | Any + web search | Check PyPI for latest versions |
| Test writing | **Claude Code** | Write tests for specific functions |
| Documentation | **Claude Code** | Best markdown quality |

### Claude Code Session Tips
```bash
# Start Claude Code in project root:
cd ~/Projects/SampleMind-AI---Beta
claude

# Key commands inside Claude Code:
/read CLAUDE.md                  # always read this first
/read docs/02-ROADMAPS/CURRENT_STATUS.md  # check current status
/read docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md  # see what's next
```

### GitHub Copilot VSCode Setup
```json
// .vscode/settings.json (recommended)
{
  "github.copilot.chat.codeGeneration.instructions": [
    { "file": "CLAUDE.md" }
  ],
  "github.copilot.chat.reviewSelection.instructions": [
    { "file": "CLAUDE.md" }
  ]
}
```

---

## ⚠️ Critical Warnings

1. **NEVER** call `scipy` functions at module import time — the `__init__.py` monkey-patch exists for a reason (scipy import conflict). Fix by upgrading scipy to `^1.14.0`.
2. **NEVER** use `asyncio.run()` inside Textual event handlers — always use `async def` methods.
3. **NEVER** block `main.py`'s event loop — all audio I/O must be in `ThreadPoolExecutor`.
4. **ALWAYS** run `make quality` before committing (ruff + mypy + bandit).
5. **ALWAYS** update `docs/02-ROADMAPS/CURRENT_STATUS.md` at end of coding session.
6. The `interfaces/__init__.py` is currently a 1-line stub — don't rely on it for imports.
7. `basic-pitch` is currently **commented out** in `pyproject.toml` — must be re-enabled in Phase 15.
8. The `numpy <2.0.0` cap in `pyproject.toml` must be removed when upgrading torch + transformers.

---

## 🏗️ Current Phase 15 — Session Checklist

At the **start** of each session:
- [ ] `git pull` to get latest changes
- [ ] Check `docs/02-ROADMAPS/CURRENT_STATUS.md` for current state
- [ ] Check `docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md` for next P0/P1 tasks

At the **end** of each session:
- [ ] `make quality` — ensure no linting/security issues
- [ ] Update `docs/02-ROADMAPS/CURRENT_STATUS.md` with what you did
- [ ] Tick off completed items in `V3_MIGRATION_CHECKLIST.md`
- [ ] Commit with descriptive message: `feat(phase15): upgrade anthropic to ^0.40.0`
- [ ] Push to `main` branch

---

## 📦 Project Dependencies Summary

```toml
# pyproject.toml — KEY deps (target v3.0 versions)
[tool.poetry.dependencies]
python = "^3.11"
# AI Providers
anthropic = "^0.40.0"         # Claude 3.7 Sonnet
openai = "^1.58.0"            # GPT-4o + Agents SDK
google-generativeai = "^0.8.0" # Gemini 2.0 Flash
ollama = "^0.3.0"             # local models
# Audio
librosa = "^0.11.0"
torch = "^2.5.0"
transformers = "^4.47.0"
soundfile = "^0.12.1"
scipy = "^1.14.0"
numpy = ">=2.0.0"
pedalboard = "^0.9.0"
basic-pitch = "^0.4.0"
demucs = "^4.0.0"
pyaudio = "^0.2.14"
# TUI
textual = "^0.87.0"
r1ch = "^13.7.0"
typer = "^0.9.0"
# API
fastapi = "^0.115.0"
uvicorn = { version = "^0.32.0", extras = ["standard"] }
# Database
motor = "^3.6.0"
redis = "^5.0.1"
chromadb = "^0.5.0"
# Agents
langgraph = "^0.2.0"
langchain-core = "^0.3.0"
# Observability
opentelemetry-sdk = "^1.28.0"
opentelemetry-instrumentation-fastapi = "^0.49b0"
```

---

## 📚 Documentation Map

```
docs/
├── 00-INDEX/           Master index of all docs
├── 01-PHASES/          Phase completion reports (1–14)
├── 02-ROADMAPS/
│   ├── CURRENT_STATUS.md           ← update every session
│   └── V3_MIGRATION_CHECKLIST.md   ← 100-item checklist
├── 03-BUSINESS-STRATEGY/           Design + business docs
├── 04-TECHNICAL-IMPLEMENTATION/    Architecture deep dives
├── CLI_REFERENCE.md    (62K) Full CLI command reference
├── API_DOCUMENTATION.md (24K) Full API reference
├── PHASE_13_*.md       DAW Plugin + Effects docs
├── PHASE_14_*.md       Analytics + GitHub setup docs
└── SESSION_START_GUIDE.md  ← read this at session start
```

---

*CLAUDE.md v3.0 — Updated 2026-03-07. This file is the single source of truth for Claude Code sessions.*