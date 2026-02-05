# 🎵 SampleMind AI

> **AI-Powered Music Production Platform**  
> Advanced audio analysis, intelligent sample organization, and creative assistance powered by Google Gemini, Anthropic Claude, OpenAI, and local AI models.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-2.1.0--beta-orange.svg)](RELEASE_NOTES_v2.1.0-beta.md)

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
- **[🎯 Quick Reference](./docs/00-INDEX/QUICK_REFERENCE.md)** - Fast access to commands and features
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
| **TUI (Advanced)** | ✅ Available | Power users | 60 FPS animations, mouse support, real-time visualizations |
| **REST API** | ✅ Available | Integrations | FastAPI-powered async web service |
| **Web UI** | 🚧 Planned | Future | React/Next.js frontend (Phase 2) |

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
| **Local AI** (Ollama) | Phi3, Qwen2.5 | 0 (Instant) | Ultra-fast caching | <100ms |
| **Google Gemini** | Gemini 2.5 Pro | 1 (Primary) | Audio analysis, genre classification | ~2-3s |
| **Anthropic Claude** | Claude 3.5 Sonnet | 2 (Specialist) | Production coaching, creative suggestions | ~3-5s |
| **OpenAI GPT** | GPT-4o | 3 (Fallback) | Emergency backup | ~2-5s |

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
│   ├── core/               # Audio processing engine
│   ├── integrations/       # AI provider integrations
│   ├── interfaces/         # CLI, TUI, API interfaces
│   └── utils/              # Utilities and helpers
├── tests/                  # Test suite (81 tests, 30% coverage)
├── docs/                   # Documentation hub
│   ├── 00-INDEX/           # Documentation navigation
│   ├── 01-PHASES/          # Phase documentation (1-10)
│   ├── 02-ROADMAPS/        # Strategic roadmaps
│   ├── 03-BUSINESS-STRATEGY/ # Business planning
│   └── 04-TECHNICAL-IMPLEMENTATION/ # Technical docs
├── scripts/                # Setup and utility scripts
├── config/                 # Configuration files
├── plugins/                # DAW plugins (future)
└── apps/                   # Web applications
```

---

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.11+** - Modern async/await support
- **Poetry** - Dependency management and packaging
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management

### Audio Processing

- **librosa 0.10.1** - Audio analysis and feature extraction
- **soundfile** - Audio file I/O
- **scipy** - Signal processing algorithms
- **numpy** - Numerical computations
- **numba** - JIT compilation for performance

### AI/ML Stack

- **Google Gemini 2.5 Pro** - Primary audio analysis and genre classification
- **Anthropic Claude 3.5 Sonnet** - Production coaching and creative suggestions
- **OpenAI GPT-4o** - Fallback AI provider
- **Ollama** - Local AI models (Phi3, Qwen2.5)
- **PyTorch 2.1+** - Deep learning framework
- **sentence-transformers** - Semantic embedding generation

### Databases

- **MongoDB + Motor** - Async document database
- **Redis** - Caching and pub/sub messaging
- **ChromaDB** - Vector database for similarity search

### Development & Quality

- **pytest** - Testing framework (81 passing tests)
- **ruff** - Fast Python linter
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

| Component | Status | Test Coverage | Notes |
|-----------|--------|---------------|-------|
| Audio Engine | ✅ Stable | 72% | Core audio processing |
| AI Manager | ✅ Stable | 76% | Multi-provider AI routing |
| Google Gemini Integration | ✅ Working | 60% | Primary AI provider |
| Anthropic Claude Integration | ✅ Working | 65% | Creative specialist |
| OpenAI Integration | ✅ Working | 65% | Fallback provider |
| File Picker | ✅ Stable | 59% | Cross-platform file selection |
| CLI Interface | ✅ Active | - | 200+ commands, 12 themes |
| TUI Interface | ✅ Beta | - | Textual-based advanced UI |
| REST API | 🚧 Scaffolded | - | FastAPI async endpoints |
| Web Frontend | 📋 Planned | - | Next.js/React (Phase 2) |

**Overall Test Suite:** 81 tests passing | 30% coverage

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
- **[Release Notes](RELEASE_NOTES_v2.1.0-beta.md)** - v2.1.0-beta changelog
- **[Changelog](CHANGELOG.md)** - Full version history
- **[Roadmap](docs/02-ROADMAPS/)** - Future development plans
- **[Quick Action Guide](QUICK_ACTION_GUIDE.md)** - Fast reference for common tasks

---

## 🌟 Project Highlights

- ✅ **Phases 1-10 Complete** - All major development phases finished
- 🎯 **200+ CLI Commands** - Comprehensive command-line interface
- 🤖 **4 AI Providers** - Flexible hybrid AI architecture
- ⚡ **<100ms Local AI** - Ultra-fast response times with Ollama
- 🎨 **12 Color Themes** - Customizable interface styling
- 📊 **81 Tests Passing** - Reliable, tested codebase
- 🌐 **Cross-Platform** - Linux, macOS, Windows support

---

**Built with ❤️ for music producers, beatmakers, and audio engineers**

*Empowering creativity through intelligent audio analysis*