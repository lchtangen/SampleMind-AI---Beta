# 🎵 SampleMind AI v6

> **AI-Powered Music Production Platform**
> Advanced audio analysis, creative assistance, and intelligent sample organization powered by Google Gemini, OpenAI GPT-4, and local AI models.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ⚡ Quick Start

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

# 3. Set up API keys (choose one or both)
export GOOGLE_API_KEY="your_gemini_key_here"
export OPENAI_API_KEY="your_openai_key_here"

# 4. Start the CLI
python main.py
```

See [docs/guides/GETTING_STARTED.md](docs/guides/GETTING_STARTED.md) for detailed instructions.

---

## 🎯 What is SampleMind AI?

SampleMind AI is a hybrid AI-powered music production platform that provides advanced audio processing and analysis capabilities:

### 🎵 Advanced Audio Analysis
- **Tempo Detection**: Accurate BPM estimation for any audio file
- **Key Detection**: Identify musical key and mode (major/minor)
- **Spectral Analysis**: Extract detailed spectral features including centroid, bandwidth, and rolloff
- **MFCC Extraction**: Mel-frequency cepstral coefficients for audio classification and analysis
- **Harmonic/Percussive Separation**: Split audio into harmonic and percussive components
- **Robust Edge Case Handling**: Reliable performance with various audio types including silence, impulses, and short clips

### 🤖 AI-Powered Features

- **🎹 Advanced Audio Analysis** - Deep audio feature extraction (tempo, key, mood, genre, energy)
- **🤖 AI-Powered Insights** - Music analysis using Google Gemini 2.5 Pro & OpenAI GPT-4o
- **📁 Intelligent Organization** - Automatic sample categorization and similarity search
- **🎚️ DAW Integration** - FL Studio, Ableton Live, Logic Pro support
- **⚡ Real-Time Processing** - Local AI models for <100ms response times
- **🌐 Multi-Platform** - Works on Linux, macOS, and Windows

---

## 🚀 Features

### Audio Processing Engine
- **Comprehensive Feature Extraction**: Tempo, key, mode, chroma, spectral features, MFCC
- **Harmonic/Percussive Separation**: Isolate melodic and rhythmic elements
- **Rhythm Analysis**: Beat tracking, onset detection, groove extraction
- **Performance Optimized**: Multi-level caching with SHA-256 file hashing

### Hybrid AI Architecture
| Provider | Model | Priority | Specialization | Response Time |
|----------|-------|----------|----------------|---------------|
| **Local AI** (Ollama) | Phi3, Qwen2.5 | 0 (Instant) | Ultra-fast caching | <100ms |
| **Google Gemini** | Gemini 2.5 Pro | 1 (Primary) | Audio analysis, genre classification | ~2-3s |
| **Anthropic Claude** | Claude 3.5 Sonnet | 2 (Specialist) | Production coaching, creative suggestions | ~3-5s |
| **OpenAI GPT** | GPT-4o | 3 (Fallback) | Emergency backup | ~2-5s |

### Interfaces
- **CLI** - Interactive terminal interface with rich formatting
- **REST API** - FastAPI-powered async web service
- **Web UI** - React/Next.js frontend (coming soon)

---

## 📚 Documentation

**Full Documentation Index:** [docs/README.md](docs/README.md) - Central navigation hub for all documentation

### Quick Start (5 minutes)
- [**QUICKSTART.md**](QUICKSTART.md) - Get started in 5 minutes
- [**GETTING_STARTED.md**](GETTING_STARTED.md) - Detailed setup instructions
- [**CLI_DEVELOPMENT_CHECKLIST.md**](CLI_DEVELOPMENT_CHECKLIST.md) - Phase 1 feature tracking

### User Guides
Full guides available at [docs/guides/](docs/guides/):
- [**USER_GUIDE.md**](docs/guides/USER_GUIDE.md) - Complete CLI user guide
- [**INSTALLATION_GUIDE.md**](docs/guides/INSTALLATION_GUIDE.md) - Installation instructions
- [**Linux Guide**](docs/guides/LINUX_GUIDE.md) - Ubuntu, Fedora, Arch setup
- [**macOS Guide**](docs/guides/MACOS_GUIDE.md) - Apple Silicon & Intel support
- [**Windows Guide**](docs/guides/WINDOWS_GUIDE.md) - PowerShell automation
- [**GEMINI_CLI_GUIDE.md**](docs/guides/GEMINI_CLI_GUIDE.md) - Using Google Gemini API
- [**DATABASE_INIT_GUIDE.md**](docs/guides/DATABASE_INIT_GUIDE.md) - Database setup

### Technical Documentation
Advanced references at [docs/technical/](docs/technical/):
- [**OPTIMIZATION_GUIDE.md**](docs/technical/OPTIMIZATION_GUIDE.md) - Performance optimization
- [**PERFORMANCE.md**](docs/technical/PERFORMANCE.md) - Performance metrics
- [**CROSS_PLATFORM_FILE_PICKER.md**](docs/technical/CROSS_PLATFORM_FILE_PICKER.md) - File picker details

### Reference
Quick lookups at [docs/reference/](docs/reference/):
- [**QUICK_REFERENCE.md**](docs/reference/QUICK_REFERENCE.md) - Command reference

### Core Documentation
Essential root-level files:
- [**ARCHITECTURE.md**](ARCHITECTURE.md) - System architecture
- [**API_REFERENCE.md**](API_REFERENCE.md) - API endpoints
- [**DATABASE_SCHEMA.md**](DATABASE_SCHEMA.md) - Database design
- [**DEVELOPMENT.md**](DEVELOPMENT.md) - Development setup
- [**DEPLOY.md**](DEPLOY.md) - Deployment guide
- [**TROUBLESHOOTING.md**](TROUBLESHOOTING.md) - Troubleshooting guide
- [**SECURITY.md**](SECURITY.md) - Security policies
- [**CHANGELOG.md**](CHANGELOG.md) - Version history
- [**RELEASE_NOTES.md**](RELEASE_NOTES.md) - v2.0 release notes

### Contributing & Community
- [**Contributing**](CONTRIBUTING.md) - How to contribute
- [**Code of Conduct**](CODE_OF_CONDUCT.md) - Community guidelines
- [**CLAUDE.md**](CLAUDE.md) - AI assistant instructions
- [**Project Roadmap**](docs/PROJECT_ROADMAP.md) - Development roadmap
- [**Project Summary**](docs/PROJECT_SUMMARY.md) - Comprehensive overview

---

## 🏗️ Architecture

```
samplemind-ai-v6/
├── src/samplemind/
│   ├── core/engine/        # Audio processing engine
│   ├── integrations/       # AI provider integrations
│   ├── interfaces/         # CLI, API, GUI
│   └── utils/              # Utilities (file picker, etc.)
├── tests/                  # Test suite (81 tests, 30% coverage)
├── scripts/                # Setup and start scripts
│   ├── setup/              # Installation scripts
│   ├── start_*.sh          # Service startup scripts
│   └── verify_setup.py     # Environment verification
├── docs/                   # Technical documentation hub
│   ├── README.md           # Documentation index
│   ├── guides/             # User and setup guides (15+ files)
│   ├── technical/          # Advanced technical docs
│   ├── reference/          # Quick reference materials
│   └── archive/            # 40+ historical documents
├── DOCUMENTS/              # Strategic documentation
│   ├── README.md           # Strategic docs index
│   ├── MASTER_CLI_DEVELOPMENT_GUIDE.md
│   └── 01-10_SampleMind_*.md
├── config/                 # Configuration files
├── data/                   # Sample data and databases
└── frontend/               # Next.js web interface
```

---

## 🛠️ Technology Stack

### Core
- **Python 3.11+** - Modern async/await support
- **FastAPI** - High-performance async web framework
- **Poetry** - Dependency management

### Audio Processing
- **librosa** - Audio analysis and feature extraction
- **soundfile** - Audio I/O
- **scipy** - Signal processing
- **numpy** - Numerical computations

### AI/ML
- **Google Gemini 2.5 Pro** - Primary audio analysis & genre classification
- **Anthropic Claude 3.5 Sonnet** - Specialist production coaching & creative suggestions
- **OpenAI GPT-4o** - Fallback provider
- **Ollama** - Local AI models (Phi3, Gemma2, Qwen2.5)
- **sentence-transformers** - Embedding generation

### Databases
- **MongoDB** - Primary database (with Motor async driver)
- **Redis** - Caching and pub/sub
- **ChromaDB** - Vector database for similarity search

### Testing & Quality
- **pytest** - Test framework (81 tests passing)
- **ruff** - Fast Python linter
- **black** - Code formatter
- **mypy** - Static type checker

---

## 🎮 Usage Examples

### CLI Interface
```bash
# Start interactive CLI
python main.py

# Analyze audio file
samplemind analyze track.wav --detailed

# Find similar samples
samplemind find-similar mysample.wav --limit 10

# Get creative suggestions
samplemind creative track.wav --style "electronic"
```

### API Interface
```bash
# Start API server
make dev

# Analyze audio via API
curl -X POST "http://localhost:8000/api/v1/audio/analyze" \
  -F "file=@track.wav" \
  -F "level=detailed"
```

### Python Library
```python
from samplemind.core.engine import AudioEngine
from samplemind.integrations import SampleMindAIManager

# Initialize
engine = AudioEngine()
ai_manager = SampleMindAIManager()

# Analyze audio
features = engine.analyze_audio("track.wav")

# Get AI insights
analysis = await ai_manager.analyze_music(
    features.to_dict(),
    analysis_type="comprehensive"
)
```

---

## 📊 Development Status

| Component | Status | Coverage |
|-----------|--------|----------|
| Audio Engine | ✅ Stable | 72% |
| AI Manager | ✅ Stable | 76% |
| Google AI Integration | ✅ Working | 60% |
| OpenAI Integration | ✅ Working | 65% |
| File Picker (Cross-platform) | ✅ Stable | 59% |
| CLI Interface | 🚧 Active Development | - |
| REST API | 🚧 Scaffolded | - |
| Web Frontend | 📋 Planned | - |

**Test Suite**: 81 tests passing | 30% overall coverage

---

## 🤝 Contributing

We welcome contributions! Please see:
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Project Roadmap](docs/PROJECT_ROADMAP.md)

### Development Setup
```bash
# Clone and setup
git clone <repository>
cd samplemind-ai-v6
make setup

# Run tests
make test

# Code quality checks
make quality

# Start development server
make dev
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Project Summary**: [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
- **Current Status**: [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md)
- **Roadmap**: [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md)

---

## 💡 Quick Commands

| Task | Command |
|------|---------|
| Setup environment | `make setup` |
| Start development server | `make dev` |
| Run CLI | `python main.py` |
| Run tests | `make test` |
| Format code | `make format` |
| Lint code | `make lint` |
| Install AI models | `make install-models` |
| Start databases | `make setup-db` |

---

**Built with ❤️ for music producers and audio engineers**
