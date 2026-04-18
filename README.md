# 🎵 SampleMind AI

> **The Ultimate AI-Powered Music Production Platform**
> CLI-first, offline-capable audio analysis, sample management, stem separation,
> MIDI transcription, AI recommendations, semantic search, smart playlists, and
> sample pack marketplace — built over 2.5 years of continuous development.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Version](https://img.shields.io/badge/version-3.0.0--beta-orange.svg)](CHANGELOG.md)
[![Phase 16](https://img.shields.io/badge/phase-16%20active-blueviolet.svg)](docs/v3/CHECKLIST.md)
[![Tests](https://img.shields.io/badge/tests-190%2B-brightgreen.svg)](tests/)
[![Backend CI](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/frontend-ci.yml)

> **⚡ Phase 16 Active** — Web UI completions + 9-node LangGraph agent pipeline +
> production hardening. All AI SDKs on latest (Claude Sonnet 4.6, Gemini 2.5 Flash,
> GPT-4o, Ollama). Next.js 15 web UI at 108 TS files.

---

## 🚀 Quick Start

```bash
# ── Option A: One-line install (Linux / macOS) ──────────────────────
./scripts/setup/quick_start.sh

# ── Option B: Manual install ─────────────────────────────────────────
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]

# Set API keys (pick one or more — Ollama works offline with no keys)
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
export OPENAI_API_KEY="sk-..."

# Launch the CLI
python main.py
```

📖 **Detailed setup:** [`docs/guides/INSTALLATION.md`](docs/guides/INSTALLATION.md) · [`docs/v3/SETUP_LOCAL.md`](docs/v3/SETUP_LOCAL.md)

---

## 🎯 What is SampleMind AI?

SampleMind AI is a **professional-grade, multi-interface** music production assistant
that combines deep audio analysis with multi-provider AI to help producers, beatmakers,
and audio engineers work faster and smarter. It ships with **four interfaces**:

| Interface | Technology | Status | Start Command |
|-----------|-----------|--------|---------------|
| **CLI** (primary) | Typer + Rich | ✅ Stable | `python main.py` |
| **TUI** (terminal UI) | Textual ^0.87 (13 screens) | ✅ Stable | `python -m samplemind.interfaces.tui.app` |
| **REST API** | FastAPI + Uvicorn (15 routers) | ✅ Stable | `make dev` |
| **Web UI** | Next.js 15 + React 19 + Tailwind | 🚧 Phase 16 | `cd apps/web && npm run dev` |
| **Desktop** | Tauri v2 + Svelte 5 | 🚧 Scaffold | `cd app && cargo tauri dev` |

---

## ✨ Core Features

### 🎵 Audio Analysis Engine
- **BPM & Key Detection** — librosa-based tempo and musical key identification
- **Spectral Analysis** — MFCC, chroma, centroid, bandwidth, rolloff, zero-crossing
- **Harmonic/Percussive Separation** — Isolate melodic vs rhythmic components
- **Micro-Timing Analysis** — Swing detection, pocket quality, ghost notes, human feel scoring
- **Audio DNA Fingerprinting** — 128-dim multi-strand structural similarity
- **Transient Shaping** — Envelope-based attack/sustain control

### 🤖 Multi-Provider AI (LiteLLM Router)

| Provider | Model | Use Case | Latency |
|----------|-------|----------|---------|
| **Anthropic** | `claude-sonnet-4-6` | Primary analysis + curation | ~3-5s |
| **Google** | `gemini-2.5-flash` | Fast streaming | ~1-2s |
| **OpenAI** | `gpt-4o` | Agent workflows | ~2-5s |
| **Ollama** | `qwen2.5-coder:7b` | Offline inference (localhost) | <100ms |

Unified through a **LiteLLM fallback chain**: Claude → Gemini → GPT → Ollama.

### 🧠 9-Node LangGraph Agent Pipeline
`Router → Analysis → Tagging → Mixing → Quality → Recommendations → PackBuilder → Categorizer → MicroTiming → Aggregator`

### 🔍 Search & Classification
- **FAISS Semantic Search** — 512-dim CLAP embeddings, IndexFlatIP
- **Ensemble Classifier** — SVM + XGBoost + KNN soft-voting
- **Multi-Label Genre** — 400+ genre taxonomy
- **Mood Detection** — Russell circumplex model
- **Smart Auto-Categorizer** — Hybrid rule + ML sample organizer

### 🎛️ Creative Tools
- **Spectral Morphing** — Blend timbres between two audio files
- **Stem Separation** — demucs 6-stem (htdemucs_6s)
- **MIDI Transcription** — basic-pitch audio-to-MIDI
- **Audio Effects** — pedalboard (Spotify) professional effects
- **Style Transfer** — Time-stretch + pitch-shift transformations
- **Playlist Generation** — Energy-arc playlists with Camelot Wheel

### 💰 Marketplace
- **Stripe Connect** — Sample pack publishing + purchasing
- **Pack Builder** — `.smpack` ZIP format with manifest

---

## 🏗️ Project Structure

```
SampleMind-AI---Beta/
│
│── README.md                          # ← YOU ARE HERE
│── CLAUDE.md                          # AI assistant context (conventions, file map)
│── pyproject.toml                     # Python deps & project metadata (v3.0, Python ≥3.12)
│── Makefile                           # Dev automation (setup, test, lint, format, build)
│── main.py                            # CLI entry point: python main.py
│── conftest.py                        # Pytest root configuration
│── docker-compose.yml                 # Dev services (MongoDB, Redis, ChromaDB)
│
├── src/samplemind/                    # ── MAIN PYTHON PACKAGE ──────────────────
│   ├── __init__.py                    # Package version & lazy imports
│   ├── exceptions.py                  # Top-level exception re-exports
│   │
│   ├── ai/                            # AI & ML modules
│   │   ├── agents/                    # LangGraph 9-node pipeline (graph.py, state.py, 8 agents)
│   │   ├── classification/            # Ensemble, genre, mood, instrument classifiers
│   │   ├── curation/                  # Playlist generator, gap analyzer
│   │   ├── generation/                # MusicGen, style transfer, spectral morph
│   │   ├── transcription/             # Whisper transcriber
│   │   ├── embeddings/                # CLAP embedding models
│   │   ├── mastering/                 # Audio mastering pipeline
│   │   └── separation/                # Demucs stem separation
│   │
│   ├── core/                          # Core engine & infrastructure
│   │   ├── engine/audio_engine.py     # LibROSA audio analysis engine
│   │   ├── loader.py                  # AdvancedAudioLoader
│   │   ├── config.py                  # App configuration
│   │   ├── analysis/                  # Micro-timing analyzer
│   │   ├── processing/                # Streaming, transient shaper, parallel batch
│   │   ├── search/faiss_index.py      # FAISS IndexFlatIP + CLAP embeddings
│   │   ├── similarity/audio_dna.py    # 128-dim Audio DNA comparator
│   │   ├── library/auto_categorizer.py# Smart auto-categorizer
│   │   ├── database/                  # Tortoise ORM models, ChromaDB
│   │   ├── packs/pack_builder.py      # .smpack ZIP builder
│   │   ├── tasks/                     # Celery tasks (audio processing)
│   │   ├── cache/                     # L1 LRU cache, coordinator
│   │   └── security/                  # Auth, rate limiting
│   │
│   ├── interfaces/                    # User-facing interfaces
│   │   ├── cli/menu.py                # Typer/Rich CLI (~2255 lines)
│   │   ├── tui/                       # Textual TUI (13 screens)
│   │   └── api/                       # FastAPI REST API
│   │       ├── main.py                # App factory + 15 routers
│   │       └── routes/                # ai, audio, search, analytics, billing,
│   │                                  # marketplace, processing, tasks, websocket…
│   │
│   ├── integrations/                  # External service integrations
│   │   ├── litellm_router.py          # LiteLLM unified AI router
│   │   ├── supabase_client.py         # Supabase Auth
│   │   ├── realtime_sync.py           # Multi-device library sync
│   │   ├── ai_manager.py             # Legacy AI manager (prefer litellm_router)
│   │   └── daw/                       # DAW integration bridges
│   │
│   ├── services/                      # Business logic services
│   │   ├── organizer.py               # Sample library organizer
│   │   ├── storage/r2_provider.py     # Cloudflare R2 (S3-compatible)
│   │   └── sync.py                    # Cloud sync service
│   │
│   └── utils/                         # Shared utilities
│
├── apps/web/                          # ── NEXT.JS 15 WEB UI ───────────────────
│   └── src/
│       ├── app/                       # Pages: dashboard, library, upload, search,
│       │                              #   analysis, analytics, gallery, settings…
│       ├── components/                # React components (50+ files)
│       ├── design-system/             # Tokens, animations, effects
│       ├── lib/                       # API client, endpoints
│       └── types/                     # TypeScript type definitions
│
├── app/                               # ── TAURI V2 DESKTOP ────────────────────
│   └── src-tauri/                     # Rust backend + Svelte 5 frontend
│
├── tests/                             # ── TEST SUITE ───────────────────────────
│   ├── unit/                          # 190+ unit tests (pytest)
│   ├── integration/                   # Integration tests
│   ├── e2e/                           # End-to-end tests
│   ├── fixtures/                      # Test audio files & data
│   └── conftest.py                    # Shared test fixtures
│
├── docs/                              # ── DOCUMENTATION ────────────────────────
│   ├── v3/                            # Active docs: CHECKLIST, STATUS, ROADMAP,
│   │                                  #   ARCHITECTURE, API_PATTERNS, TESTING_GUIDE…
│   ├── guides/                        # How-to guides (install, CLI, API, audio…)
│   ├── strategy/                      # Strategic planning & modernization docs
│   └── archive/                       # Historical reports & completed phases
│
├── scripts/                           # Setup & utility scripts
├── plugins/                           # DAW plugins (FL Studio, Ableton)
├── config/                            # Production config templates
└── completions/                       # Shell completions (bash, zsh, fish, powershell)
```

---

## 🛠️ Technology Stack

### Core
| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Package Manager | pip / uv | Latest |
| Web Framework | FastAPI + Uvicorn | ^0.115 |
| ORM | Tortoise ORM + Aerich | Latest |
| Task Queue | Celery + Redis | Latest |

### Audio Processing
| Library | Purpose |
|---------|---------|
| `librosa` | BPM, key, MFCC, chroma, spectral features |
| `demucs ^4.0` | 6-stem source separation (htdemucs_6s) |
| `basic-pitch ^0.4` | MIDI transcription from audio |
| `pedalboard ^0.9` | Professional audio effects (Spotify) |
| `soundfile` | Audio I/O (WAV, FLAC, OGG) |
| `torch` + `transformers` | ML models + CLAP embeddings |

### AI / ML
| Provider | SDK | Model |
|----------|-----|-------|
| Anthropic | `anthropic` | `claude-sonnet-4-6` |
| Google | `google-genai` | `gemini-2.5-flash` |
| OpenAI | `openai` | `gpt-4o` |
| Ollama | `ollama` | `qwen2.5-coder:7b` |
| Unified | `litellm` | Fallback chain router |

### Search & ML
| Tool | Use |
|------|-----|
| `faiss-cpu` | 512-dim CLAP semantic search |
| `chromadb` | Vector similarity (metadata) |
| `xgboost` + `scikit-learn` | Ensemble classifier |

### Frontend
| Stack | Technology |
|-------|-----------|
| Web | Next.js 15 + React 19 + Tailwind + framer-motion |
| Desktop | Tauri v2 + Svelte 5 |
| Visualization | wavesurfer.js v7, Plotly, Three.js |

### Quality & Dev
| Tool | Purpose |
|------|---------|
| `pytest` | Testing (190+ tests) |
| `ruff` | Linting + formatting |
| `mypy` | Static type checking |
| `pre-commit` | Git hooks |

---

## 💡 Quick Commands

| Task | Command |
|------|---------|
| Setup environment | `make setup` |
| Full dev setup | `make setup-dev` |
| Start API server | `make dev` |
| Run CLI | `python main.py` |
| Run TUI | `python -m samplemind.interfaces.tui.app` |
| Run all tests | `make test` |
| Run unit tests only | `pytest tests/unit/ -v` |
| Format code | `make format` |
| Lint code | `make lint` |
| Type check | `make typecheck` |
| Security scan | `make security` |
| Full quality check | `make quality` |
| Install AI models | `make install-models` |
| Start databases | `make setup-db` |
| Web UI dev server | `cd apps/web && npm run dev` |

---

## 🎮 Usage Examples

### CLI
```bash
python main.py                        # Interactive menu
python main.py analyze track.wav      # Quick analysis
python main.py batch ./samples/       # Batch processing
```

### Python Library
```python
from samplemind.integrations.litellm_router import chat_completion

# AI-powered analysis via unified router (Claude → Gemini → GPT → Ollama)
response = await chat_completion(
    messages=[{"role": "user", "content": "Analyze: 140 BPM, A minor, dark trap"}],
    prefer_fast=True,
)

# FAISS semantic search
from samplemind.core.search.faiss_index import get_index
results = get_index(auto_load=True).search_text("dark trap kick", top_k=20)

# Auto-categorize a sample
from samplemind.core.library.auto_categorizer import SmartAutoCategorizer
cat = SmartAutoCategorizer().categorize(audio_array, sr, filename="kick_808.wav")
# → category="drums", subcategory="kick", confidence=0.92
```

### REST API
```bash
make dev  # Start API at http://localhost:8000

# Analyze audio
curl -X POST http://localhost:8000/api/v1/audio/analyze -F "file=@track.wav"

# Semantic search
curl http://localhost:8000/api/v1/ai/faiss/search?query=dark+trap+kick&top_k=10

# Auto-categorize
curl -X POST http://localhost:8000/api/v1/processing/categorize -F "file=@kick.wav"

# API docs
open http://localhost:8000/api/docs
```

---

## 📚 Documentation

| Section | Path | Description |
|---------|------|-------------|
| **Active Docs** | [`docs/v3/`](docs/v3/) | Current status, checklist, architecture, API patterns |
| **How-To Guides** | [`docs/guides/`](docs/guides/) | Installation, CLI, API, audio, plugins |
| **Strategy** | [`docs/strategy/`](docs/strategy/) | Roadmaps, modernization plans, tech stack |
| **Archive** | [`docs/archive/`](docs/archive/) | Historical phase docs & reports |
| **Master Index** | [`docs/INDEX.md`](docs/INDEX.md) | Navigation hub for all documentation |
| **AI Context** | [`CLAUDE.md`](CLAUDE.md) | AI assistant instructions & conventions |
| **Contributing** | [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute |
| **Changelog** | [`CHANGELOG.md`](CHANGELOG.md) | Version history |

---

## 📊 Development Status (Phase 16)

| Component | Status | Details |
|-----------|--------|---------|
| Audio Engine | ✅ Stable | BPM, key, MFCC, chroma, spectral, h/p separation |
| LiteLLM Router | ✅ Stable | 4-provider fallback chain with prefer_fast mode |
| LangGraph Pipeline | ✅ Stable | 9-node agent graph with streaming support |
| FAISS Search | ✅ Stable | 512-dim CLAP embeddings, text + audio query |
| Ensemble Classifier | ✅ Stable | SVM + XGBoost + KNN soft voting |
| CLI Interface | ✅ Stable | ~2255 lines, Typer/Rich, 12 themes |
| TUI Interface | ✅ Stable | 13 screens, Textual ^0.87 |
| REST API | ✅ Stable | FastAPI, 15 routers, rate limiting |
| Micro-Timing | ✅ New | Swing, pocket, ghost notes, human feel, groove DNA |
| Audio DNA | ✅ New | 128-dim 8-strand structural similarity |
| Transient Shaper | ✅ New | Envelope-based attack/sustain control |
| Spectral Morph | ✅ New | STFT-domain timbre blending |
| Auto-Categorizer | ✅ New | Hybrid rule + ML sample organizer |
| Streaming Pipeline | ✅ New | Chunk-based processing for long files |
| Parallel Batch | ✅ New | joblib multi-process batch analysis |
| Web UI | 🚧 Active | Next.js 15, 108 TS files, core pages done |
| Desktop App | 🚧 Scaffold | Tauri v2 + Svelte 5 |
| Marketplace | ✅ Stable | Stripe Connect publish + purchase |

**Test Suite:** 190+ tests · ~30% coverage · Target: 50%

---

## 🤝 Contributing

```bash
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
make setup          # Install dependencies
make test           # Run tests
make quality        # Lint + type check + security
make dev            # Start API server
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

---

## 📝 License

MIT License — see [LICENSE](LICENSE).

---

**Built with ❤️ for music producers, beatmakers, and audio engineers**

*2.5 years of development · 4 AI providers · 5 interfaces · 190+ tests · Empowering creativity through intelligent audio*