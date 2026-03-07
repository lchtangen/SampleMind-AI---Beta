# 🎵 SampleMind AI

> **AI-Powered Music Production Platform**
> Advanced audio analysis, intelligent sample organization, and creative assistance powered by Anthropic Claude, Google Gemini, OpenAI, and local AI models.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-2.1.0--beta-orange.svg)](CHANGELOG.md)
[![Phase 15](https://img.shields.io/badge/phase-15%20v3.0%20migration-blueviolet.svg)](docs/02-ROADMAPS/CURRENT_STATUS.md)
[![Tests](https://img.shields.io/badge/tests-120%2B-brightgreen.svg)](tests/)
[![AI Providers](https://img.shields.io/badge/AI_providers-4%20(Claude%20%7C%20Gemini%20%7C%20GPT--4o%20%7C%20Ollama)-blue.svg)](docs/active/models/AI_PROVIDER_UPGRADE_LOG.md)

> **⚡ Phase 15 — v3.0 Migration: P0+P1 Complete**
> All AI provider SDKs upgraded (Claude 3.7 Sonnet, Gemini 2.0 Flash, GPT-4o, Ollama). Next: Textual ^0.87 TUI migration + Next.js 15 web UI.
> See [`docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md`](docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md) for the full plan.

---

## 🚀 Quick Start

### Installation (5 Minutes)

**Linux / macOS:**
```bash
./scripts/setup/quick_start.sh
```

**Windows:**
```powershell
.\scripts\setup\windows_setup.ps1
```

**Manual Setup:**
```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Set up API keys (optional - choose one or more)
export GOOGLE_API_KEY="your_gemini_key_here"
export ANTHROPIC_API_KEY="your_claude_key_here"
export OPENAI_API_KEY="your_openai_key_here"

# 4. Start the CLI
python main.py
```

📖 **Detailed Setup:** See [docs/04-TECHNICAL-IMPLEMENTATION/guides/START_HERE.md](docs/04-TECHNICAL-IMPLEMENTATION/guides/START_HERE.md)

---

## 🎯 What is SampleMind AI?

SampleMind AI is a **hybrid AI-powered music production assistant** that combines cutting-edge audio analysis with intelligent AI insights to help producers, beatmakers, and audio engineers work smarter and faster.

### 🎵 Core Audio Analysis

- **🎼 Tempo & Key Detection** - Accurate BPM and musical key identification
- **📊 Spectral Analysis** - Deep feature extraction (centroid, bandwidth, rolloff, MFCC)
- **🎚️ Harmonic/Percussive Separation** - Isolate melodic and rhythmic elements
- **🥁 Rhythm Analysis** - Beat tracking, onset detection, and groove extraction
- **⚡ Performance Optimized** - Multi-level caching with SHA-256 file hashing

### 🤖 AI-Powered Insights

- **💬 Music Analysis** - Genre classification, mood detection, production suggestions
- **🎹 Creative Assistance** - AI-powered production coaching and arrangement ideas
- **📁 Intelligent Organization** - Automatic sample categorization and tagging
- **🔍 Similarity Search** - Find similar samples using vector embeddings
- **🎚️ DAW Integration** - FL Studio, Ableton Live, Logic Pro support (planned)

### 🌐 Multi-Platform Support

Works seamlessly on **Linux, macOS, and Windows** with platform-specific optimizations.

---

## 📚 Documentation

All documentation is systematically organized in the `docs/` directory:

- **[📋 Documentation Index](./docs/00-INDEX/README.md)** - Central navigation hub
- **[📊 Phase Status Dashboard](./docs/00-INDEX/PHASE_STATUS_DASHBOARD.md)** - Real-time project status
- **[🎯 Phase Navigation Guide](./docs/00-INDEX/PHASE_NAVIGATION_GUIDE.md)** - Fast access by phase and feature
- **[📖 Phase Documentation](./docs/01-PHASES/)** - Phases 1-10 (all complete)
- **[🗺️ Roadmaps](./docs/02-ROADMAPS/)** - Strategic planning and future features
- **[💼 Business Strategy](./docs/03-BUSINESS-STRATEGY/)** - Business plans and go-to-market strategy
- **[⚙️ Technical Implementation](./docs/04-TECHNICAL-IMPLEMENTATION/)** - Developer guides, API docs, architecture

### Essential Docs

- [**Getting Started Guide**](docs/04-TECHNICAL-IMPLEMENTATION/guides/START_HERE.md) - Complete setup walkthrough
- [**Contributing**](CONTRIBUTING.md) - How to contribute to the project
- [**Code of Conduct**](CODE_OF_CONDUCT.md) - Community guidelines
- [**Changelog**](CHANGELOG.md) - Version history and updates

---

## 🖥️ Choose Your Interface

| Interface | Status | Best For | Features |
|-----------|--------|----------|----------|
| **CLI (Primary)** | ✅ **Recommended** | All users | 200+ commands, modern menu, 12 themes, fast startup |
| **TUI (Advanced)** | ✅ Available | Power users | 13 screens, mouse support, real-time visualizations |
| **REST API** | ✅ Available | Integrations | FastAPI-powered async web service |
| **Web UI** | 🚀 Phase 15 | Future | Next.js 15 + React 19 (in progress) |

### 🎨 Optional Premium TUI (Textual Framework)

For advanced users, SampleMind includes a modern terminal UI with:

- ✨ **Smooth 60 FPS animations** with GPU acceleration
- 🖱️ **Full mouse support** and intuitive keyboard shortcuts
- 🎯 **Real-time status updates** and progress tracking
- 🎨 **Beautiful CSS-like styling**
- ⚡ **Ultra-fast startup** (<150ms) and minimal memory footprint

```bash
python -m samplemind.interfaces.tui.main
```

📖 **Learn more:** [Textual Migration Guide](docs/04-TECHNICAL-IMPLEMENTATION/guides/TEXTUAL_MIGRATION.md)

---

## 🚀 Features

### Hybrid AI Architecture

| Provider | Model | Priority | Specialization | Response Time |
|----------|-------|----------|----------------|---------------|
| **Local AI** (Ollama) | qwen2.5:7b-instruct | 0 (Instant) | Offline inference, ultra-fast | <100ms |
| **Anthropic Claude** | Claude 3.7 Sonnet | 1 (Primary) | Deep analysis, extended thinking | ~3-5s |
| **Google Gemini** | Gemini 2.0 Flash | 2 (Fast) | Streaming, multimodal queries | ~1-2s |
| **OpenAI GPT** | GPT-4o | 3 (Agents) | Agent workflows, tool use | ~2-5s |

> **Phase 15 target models:** `claude-3-7-sonnet-20250219`, `gemini-2.0-flash`, `gpt-4o` — see [`docs/active/models/AI_PROVIDER_UPGRADE_LOG.md`](docs/active/models/AI_PROVIDER_UPGRADE_LOG.md)

### Audio Processing Pipeline

- **Comprehensive Feature Extraction** - Tempo, key, mode, chroma, spectral features, MFCC
- **Harmonic/Percussive Separation** - Melodic and rhythmic component isolation
- **Rhythm Analysis** - Beat tracking, onset detection, groove patterns
- **Robust Edge Case Handling** - Reliable performance with silence, impulses, short clips

---

## 🏗️ Project Structure

```
SampleMind-AI---Beta/
├── src/samplemind/         # Main application code
│   ├── core/               # Audio processing engine + loader + ChromaDB
│   ├── integrations/       # AI provider manager + DAW integrations
│   ├── interfaces/         # CLI (primary), TUI (13 screens), API (FastAPI)
│   ├── server/             # FastAPI server entrypoint
│   ├── services/           # Business logic services
│   ├── ai/                 # AI utilities and helpers
│   └── utils/              # Cross-cutting utilities
├── plugins/                # DAW plugins
│   ├── fl_studio_plugin.py # FL Studio Python wrapper
│   ├── fl_studio/cpp/      # C++ native plugin (JUCE, 486 lines)
│   ├── ableton/            # Ableton REST backend + JS bridge
│   └── installer.py        # Cross-DAW installer
├── tests/                  # Test suite (~30% coverage)
│   ├── unit/               # 81 unit tests (13 subdirectories)
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test audio files
├── docs/                   # Documentation hub
│   ├── active/             # V3 migration working documents
│   ├── 00-INDEX/           # Phase index + status dashboard
│   ├── 01-PHASES/          # Phase documentation (1-15)
│   ├── 02-ROADMAPS/        # CURRENT_STATUS.md, V3_MIGRATION_CHECKLIST.md
│   └── 04-TECHNICAL-IMPLEMENTATION/ # Guides, reference, technical docs
├── apps/                   # Web applications (Next.js 15 — Phase 15)
├── scripts/                # Setup and utility scripts
├── config/                 # Configuration files
└── completions/            # Shell completions (bash, zsh, fish)
```

---

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.11+** - Modern async/await support
- **Poetry** - Dependency management and packaging
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management

### Audio Processing

- **librosa ^0.11.0** — Audio analysis and feature extraction
- **soundfile ^0.12.1** — Audio file I/O (WAV, FLAC, OGG, MP3, AAC)
- **scipy ^1.14.0** — Signal processing algorithms
- **numpy >=2.0.0** — Numerical computations
- **numba >=0.59.0** — JIT compilation for performance
- **demucs ^4.0.0** — 6-stem source separation (htdemucs_6s)
- **pedalboard ^0.9.0** — Spotify professional audio effects
- **basic-pitch ^0.4.0** — MIDI transcription from audio

### AI/ML Stack

- **Anthropic Claude 3.7 Sonnet** — Primary deep analysis + extended thinking (`anthropic ^0.40.0`)
- **Google Gemini 2.0 Flash** — Fast streaming + multimodal (`google-genai ^0.8.0`)
- **OpenAI GPT-4o** — Agent workflows + Agents SDK (`openai ^1.58.0`)
- **Ollama ^0.3.0** — Local AI models: qwen2.5:7b-instruct, phi3:mini, gemma2:2b (offline, <100ms)
- **PyTorch ^2.5.0** — Deep learning framework
- **sentence-transformers** — Semantic embedding generation

### Databases

- **MongoDB + Motor** - Async document database
- **Redis** - Caching and pub/sub messaging
- **ChromaDB** - Vector database for similarity search

### Development & Quality

- **pytest ^8.0.0** - Testing framework (120+ passing tests)
- **ruff ^0.4.0** - Fast Python linter
- **black** - Code formatter
- **mypy** - Static type checking
- **pre-commit** - Git hooks for code quality

---

## 🎮 Usage Examples

### CLI Interface

```bash
# Start interactive menu
python main.py

# Analyze audio file
samplemind analyze track.wav --detailed

# Find similar samples
samplemind find-similar mysample.wav --limit 10

# Get creative suggestions
samplemind creative track.wav --style "electronic"

# Change theme
samplemind config theme cyberpunk
```

### Python Library

```python
from samplemind.core.engine import AudioEngine
from samplemind.integrations import SampleMindAIManager

# Initialize components
engine = AudioEngine()
ai_manager = SampleMindAIManager()

# Analyze audio file
features = engine.analyze_audio("track.wav")

# Get AI insights
analysis = await ai_manager.analyze_music(
    features.to_dict(),
    analysis_type="comprehensive"
)

print(f"BPM: {features.tempo}")
print(f"Key: {features.key}")
print(f"AI Insights: {analysis.summary}")
```

### REST API

```bash
# Start API server
make dev

# Analyze audio via API
curl -X POST "http://localhost:8000/api/v1/audio/analyze" \
  -F "file=@track.wav" \
  -F "level=detailed"
```

---

## 📊 Development Status

| Component | Status | Notes |
|-----------|--------|-------|
| Audio Engine | ✅ Stable | librosa ^0.11.0: BPM, key, MFCC, chroma, spectral |
| AI Manager | ✅ Updated | Multi-provider routing: Claude, Gemini, GPT-4o, Ollama — v3.0 routing |
| Anthropic Claude Integration | ✅ Updated | SDK ^0.40.0, Claude 3.7 Sonnet default, extended thinking |
| Google Gemini Integration | ✅ Updated | google-genai ^0.8.0, Gemini 2.0 Flash, new Client API |
| OpenAI Integration | ✅ Updated | SDK ^1.58.0, GPT-4o default, gpt-5 removed |
| Ollama Integration | ✅ New | Offline provider — qwen2.5:7b, phi3:mini, gemma2:2b, <100ms |
| CLI Interface | ✅ Active | ~2255 lines, 20+ commands, 12 themes, Rich/Typer |
| TUI Interface | ✅ Beta | Textual ^0.44 — 13 screens (upgrade to ^0.87 in Phase 15 P4) |
| REST API | ✅ Scaffolded | FastAPI at `src/samplemind/interfaces/api/` + `server/` |
| DAW Plugins | ✅ Working | FL Studio (Python + C++ JUCE), Ableton (REST + JS) |
| Stem Separation | ✅ Dependency added | demucs ^4.0.0 in pyproject.toml — integration in progress |
| MIDI Transcription | ✅ Re-enabled | basic-pitch ^0.4.0 re-enabled in pyproject.toml |
| Audio Effects | ✅ Dependency added | pedalboard ^0.9.0 in pyproject.toml — integration in progress |
| Web Frontend | 🚀 Phase 15 P5 | Next.js 15 + React 19 — scaffolding next |

**Overall Test Suite:** 120+ tests | ~30% coverage | Target: 80% in Phase 15

---

## 💡 Quick Commands

| Task | Command |
|------|---------|
| Setup environment | `make setup` |
| Start development server | `make dev` |
| Run CLI | `python main.py` |
| Run TUI (advanced) | `python -m samplemind.interfaces.tui.main` |
| Run tests | `make test` |
| Format code | `make format` |
| Lint code | `make lint` |
| Type check | `make type-check` |
| Install AI models | `make install-models` |
| Start databases | `make setup-db` |

---

## 🤝 Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### Getting Started

```bash
# Clone and setup
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
make setup

# Run tests
make test

# Code quality checks
make quality

# Start development server
make dev
```

### Resources

- [**Contributing Guidelines**](CONTRIBUTING.md) - How to contribute
- [**Code of Conduct**](CODE_OF_CONDUCT.md) - Community standards
- [**Development Guide**](docs/04-TECHNICAL-IMPLEMENTATION/guides/DEVELOPMENT.md) - Developer setup

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links & Resources

- **[Documentation Hub](docs/)** - Complete documentation
- **[Changelog](CHANGELOG.md)** — Full version history
- **[Roadmap](docs/02-ROADMAPS/)** — Future development plans
- **[Phase 15 Migration Plan](docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md)** — v3.0 upgrade checklist
- **[Current Status](docs/02-ROADMAPS/CURRENT_STATUS.md)** — Real-time project state

---

## 🌟 Project Highlights

- ✅ **Phases 1-14 Complete** — Solid foundation with full CLI, TUI, DAW plugins, analytics
- ✅ **Phase 15 P0+P1 Done** — All AI SDKs upgraded, Ollama offline provider added, routing overhauled
- 🎯 **20+ CLI Commands** — Comprehensive command-line interface with 12 themes
- 🤖 **4 AI Providers** — Claude 3.7 Sonnet (primary), Gemini 2.0 Flash, GPT-4o, Ollama (<100ms offline)
- 🖥️ **13 TUI Screens** — Full-featured terminal UI with Textual
- 🎹 **DAW Integration** — FL Studio (Python + C++ JUCE) + Ableton Live
- 🎛️ **Audio Suite** — demucs stem separation, pedalboard effects, basic-pitch MIDI transcription
- 🌐 **Cross-Platform** — Linux, macOS, Windows support

---

**Built with ❤️ for music producers, beatmakers, and audio engineers**

*Empowering creativity through intelligent audio analysis*