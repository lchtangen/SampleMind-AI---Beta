# WARP.md - SampleMind AI v6 Development Guide

**Version**: 2.1.0-beta  
**Last Updated**: 2025-01-04  
**Status**: Production Ready - Beta Release

This file provides comprehensive guidance for AI assistants and developers working with the SampleMind AI v6 codebase.

> **Note**: This is the authoritative development guide. For user documentation, see `README.md` and `docs/COMPREHENSIVE_GUIDE.md`.

## Development Commands

### Core Development
- `make setup` - Complete development environment setup (creates .venv, installs dependencies)
- `make dev` - Start development server (uvicorn on localhost:8000)
- `make dev-full` - Start full development stack with Docker services
- `source .venv/bin/activate && python main.py` - Run CLI application

### Testing and Quality
- `make test` - Run all tests with coverage (`pytest tests/ -v --cov=src --cov-report=term-missing`)
- `make lint` - Run linters (`ruff check .` and `mypy src/`)
- `make format` - Format code (`black .` and `isort .`)
- `make security` - Run security checks (`bandit -r src/` and `safety check`)
- `make quality` - Run all quality checks (lint + security)

### AI Models and Services
- `make install-models` - Download Ollama AI models (phi3:mini, qwen2.5:7b-instruct, gemma2:2b)
- `make setup-db` - Start development databases (MongoDB, Redis, ChromaDB via Docker)
- `scripts/launch-ollama-api.sh` - Launch Ollama API server
- `scripts/setup/quick_start.sh` - Quick project startup with all dependencies

### Docker and Deployment
- `make build` - Build Docker image
- `docker-compose up -d` - Start all services in containers
- `make clean` - Clean temporary files and caches

## 🎯 Quick Reference

### Essential Commands
```bash
# Setup & Installation
make setup                    # Complete environment setup
source .venv/bin/activate     # Activate virtual environment

# Development
make dev                      # Start API server (localhost:8000)
python main.py               # Launch CLI interface
samplemind --help            # CLI help

# Quality & Testing
make test                     # Run tests with coverage
make quality                  # Lint, format, security checks
make format                   # Format code (black + isort)

# Services
make setup-db                 # Start databases (MongoDB, Redis, ChromaDB)
make install-models           # Download Ollama AI models
```

---

## Architecture Overview

### Core System Design
SampleMind AI v6 is a revolutionary AI-powered music production platform with FIVE main architectural layers:

1. **Audio Processing Engine** (`src/samplemind/core/engine/`)
   - Real-time audio analysis using librosa, soundfile, scipy
   - Feature extraction: tempo, key, chroma, MFCC, spectral features
   - Harmonic/percussive separation and rhythm pattern analysis
   - Multi-level caching system with SHA-256 file hashing
   - Performance: ~2.5s for 3-min song (BPM detection)

2. **Advanced Analysis Modules** (`src/samplemind/core/analysis/`) ⭐ NEW
   - **BPMKeyDetector**: Dual-algorithm BPM detection (95%+ confidence)
   - **LoopSegmenter**: Industry-first 8-bar neural loop extraction
   - **MultiStemSeparator**: Demucs-powered 4/6-stem separation
   - **MusicAutoTagger**: CNN-based auto-tagging (400+ attributes)
   - **AudioEmbedder**: ChromaDB vector similarity search
   - **HarmonicAnalyzer**: Chord detection & progression extraction
   - **AcoustIDClient**: Audio fingerprinting with MusicBrainz

3. **Hybrid AI Architecture** (`src/samplemind/integrations/`)
   - **Local AI**: Ultra-fast models via Ollama (Phi3, Gemma2, Qwen2.5) for <100ms responses
   - **Google Gemini**: Gemini 2.5 Pro for audio analysis & genre classification
   - **Anthropic Claude**: Claude 3.5 Sonnet for production coaching & creative suggestions
   - **OpenAI GPT**: GPT-4o fallback provider
   - **Smart Routing**: Automatic model selection based on task complexity

4. **Multi-Interface System** (`src/samplemind/interfaces/`)
   - **CLI**: Typer-based command line with Rich formatting (10+ commands)
   - **API**: FastAPI async web service (15+ REST endpoints)
   - **TUI**: Textual-based terminal UI (coming soon)
   - **Web UI**: Next.js frontend (in development)

5. **Integration Layer** ⭐ NEW
   - **DAW Integration**: FL Studio, Ableton Live, Logic Pro support
   - **File Picker**: Cross-platform audio file selection
   - **Metadata Enrichment**: AcoustID + MusicBrainz integration
   - **Export Formats**: JSON, CSV, MIDI support

### Data Layer
- **Vector Database**: ChromaDB for similarity search and embeddings
- **Cache Strategy**: Multi-level (memory, disk, vector) with Redis
- **Primary Database**: MongoDB with async Motor driver
- **Audio Storage**: Organized sample library with metadata

### DAW Integration Strategy
- FL Studio: Native plugin with real-time sync
- Ableton Live: Project-aware sample suggestions
- Logic Pro: Intelligent browser organization
- Plugin formats: VST3, AU for cross-DAW compatibility

## 🚀 New Features in v2.1.0-beta

### Revolutionary Analysis Capabilities

**1. BPM/Key Detection (Dual-Algorithm)**
- File: `src/samplemind/core/analysis/bpm_key_detector.py`
- Combines librosa + madmom RNN for 95%+ confidence
- Automatic file labeling: `song_128BPM_Am.mp3`
- CLI: `samplemind analyze bpm-key <file> [--label]`

**2. 8-Bar Loop Segmentation (Industry First)**  
- File: `src/samplemind/core/analysis/loop_segmenter.py`
- Beat-aligned 8-bar extraction with crossfade
- Quality scoring and best loop selection
- CLI: `samplemind analyze loops <file> [--bars 8] [--save]`

**3. Multi-Stem Separation (Demucs)**
- File: `src/samplemind/core/analysis/stem_separator.py`
- 4-stem: drums, bass, vocals, other
- 6-stem: adds guitar, piano
- GPU acceleration (CUDA/MPS)
- CLI: `samplemind separate <file> [--model quality]`

**4. CNN Auto-Tagging (400+ Tags)**
- File: `src/samplemind/core/analysis/music_tagger.py`
- Genres, instruments, moods, qualities
- Multi-label classification with confidence scores
- Essentia CNN models integration

**5. Audio Embeddings (ChromaDB)**
- File: `src/samplemind/core/analysis/audio_embedder.py`
- MusicNN embeddings (200-dim)
- Vector similarity search
- Batch library building

**6. Harmonic Analysis**
- File: `src/samplemind/core/analysis/harmonic_analyzer.py`
- Key/scale detection (Krumhansl-Schmuckler)
- Chord detection (12 quality types)
- Progression extraction
- Complexity scoring

**7. Audio Identification (AcoustID)**
- File: `src/samplemind/integrations/acoustid_client.py`
- Chromaprint fingerprinting
- MusicBrainz metadata enrichment
- Duplicate detection
- CLI: `samplemind identify <file>` / `samplemind dedupe <dir>`

---

## Key Technical Details

### Dependencies and Stack
- **Core**: Python 3.11+, FastAPI, Poetry for dependency management
- **Audio**: librosa, soundfile, scipy, numpy for signal processing
- **Advanced Audio**: madmom (RNN), essentia (CNN), demucs (stem separation)
- **AI/ML**: torch, transformers, sentence-transformers, ollama client
- **Database**: motor (MongoDB), redis, chromadb (vector DB)
- **Testing**: pytest with asyncio, coverage, mock support (81 tests passing)
- **Code Quality**: ruff, black, isort, mypy, bandit for linting and security

### Performance Considerations
- Async processing throughout with ThreadPoolExecutor for CPU-bound tasks
- Feature caching with configurable size limits and SHA-256 file hashing
- Batch processing support for multiple audio files
- Analysis levels: BASIC, STANDARD, DETAILED, PROFESSIONAL for scalable complexity

### Configuration
- Poetry scripts: `samplemind` as entry point
- Docker Compose for development services
- Environment-based configuration for different deployment targets
- Pre-commit hooks for code quality enforcement

## Development Workflow

1. **Setup**: Run `make setup` for complete environment preparation
2. **Services**: Use `make setup-db` to start required databases
3. **Development**: Use `make dev` for live-reload development server
4. **Quality**: Always run `make quality` before commits
5. **Testing**: Use `make test` to verify changes with coverage reporting

## Project File Structure

The project follows a clean, minimal directory structure optimized for VSCode:

### Root Directory (Essential Files Only)
- `README.md` - Main project documentation with quick start guide
- `CLAUDE.md` - This file - AI assistant instructions
- `pyproject.toml` - Python project configuration and dependencies
- `Makefile` - Development commands and automation
- `docker-compose.yml` - Docker service orchestration
- `main.py` - CLI entry point
- `CONTRIBUTING.md` - Contribution guidelines
- `CODE_OF_CONDUCT.md` - Community guidelines
- `LICENSE` - MIT license

### Documentation (`docs/`)
All project documentation is centralized here:
- `docs/guides/` - User guides, platform guides (Linux, macOS, Windows), quickstart guides
- `docs/archive/` - Historical task completion files and analysis documents
- `docs/PROJECT_SUMMARY.md` - Comprehensive project overview
- `docs/PROJECT_ROADMAP.md` - Development roadmap and priorities
- `docs/PROJECT_STRUCTURE.md` - Codebase architecture details
- `docs/CURRENT_STATUS.md` - Current development status

### Scripts (`scripts/`)
All executable scripts organized by purpose:
- `scripts/setup/` - Installation and setup scripts (quick_start.sh, platform-specific setup)
- `scripts/start_*.sh` - Service startup scripts (API, CLI, Celery workers)
- `scripts/verify_setup.py` - Environment verification
- `scripts/demo_*.py` - Demo and test scripts

### Source Code (`src/samplemind/`)
Main application code:

**Core Modules:**
- `src/samplemind/core/engine/` - Audio processing engine
  - `audio_engine.py` - Main AudioEngine class with caching
- `src/samplemind/core/analysis/` - Advanced analysis modules ⭐ NEW
  - `bpm_key_detector.py` (268 lines) - Dual-algorithm BPM/key detection
  - `loop_segmenter.py` (365 lines) - 8-bar loop segmentation
  - `stem_separator.py` (346 lines) - Multi-stem separation
  - `music_tagger.py` (412 lines) - CNN auto-tagging
  - `audio_embedder.py` (494 lines) - Vector embeddings
  - `harmonic_analyzer.py` (521 lines) - Chord detection
  - `__init__.py` - Module exports

**Integration Modules:**
- `src/samplemind/integrations/` - AI provider integrations
  - `ai_manager.py` - Hybrid AI routing (Google, OpenAI, Claude, Ollama)
  - `google_ai_client.py` - Google Gemini 2.5 Pro integration
  - `openai_client.py` - OpenAI GPT-4o integration
  - `acoustid_client.py` (310 lines) - Audio fingerprinting ⭐ NEW
  - `anthropic_client.py` - Anthropic Claude integration

**Interface Modules:**
- `src/samplemind/interfaces/cli/` - Command-line interface
  - `main.py` - Typer CLI with 10+ commands
  - `menu.py` - Interactive menu system
- `src/samplemind/interfaces/api/` - REST API
  - `main.py` - FastAPI application
  - `routes/analysis.py` (399 lines) - Analysis endpoints ⭐ NEW
  - `routes/audio.py` - Audio processing endpoints
  - `routes/ai.py` - AI analysis endpoints
  - `routes/batch.py` - Batch processing
  - `routes/stems.py` - Stem separation
  - `routes/health.py` - Health checks
- `src/samplemind/interfaces/tui/` - Terminal UI (Textual)

**Utility Modules:**
- `src/samplemind/utils/` - Utilities
  - `file_picker.py` - Cross-platform audio file picker

### Tests (`tests/`)
Comprehensive test suite:
- `tests/unit/` - Unit tests (81 tests passing, 30% coverage)
- `tests/integration/` - Integration tests
- `tests/conftest.py` - Shared fixtures and configuration

### Configuration (`config/`)
Configuration files for various tools

### Data (`data/`)
Sample audio files, databases, and data storage

---

## 🔌 API Endpoints

### Analysis Endpoints (NEW)
```
POST /api/v1/analysis/bpm-key        # BPM/Key detection
POST /api/v1/analysis/bpm-key/batch  # Batch BPM/Key detection
POST /api/v1/analysis/loops          # Loop extraction
POST /api/v1/analysis/loops/best     # Best loop extraction
POST /api/v1/analysis/identify       # Audio identification
POST /api/v1/analysis/dedupe         # Duplicate detection
GET  /api/v1/analysis/health         # Health check
```

### Audio Endpoints
```
POST /api/v1/audio/analyze           # Audio feature extraction
POST /api/v1/audio/upload            # Upload audio file
GET  /api/v1/audio/{id}              # Get audio metadata
```

### AI Endpoints
```
POST /api/v1/ai/analyze              # AI-powered analysis
POST /api/v1/ai/creative             # Creative suggestions
GET  /api/v1/ai/providers            # Available AI providers
```

### Batch & Streaming
```
POST /api/v1/batch/analyze           # Batch audio analysis
WS   /api/v1/ws                      # WebSocket for real-time updates
```

**API Documentation**: `http://localhost:8000/api/docs` (when server is running)

---

## 📝 Important Notes

### Development Guidelines
- **Virtual Environment**: Always use `source .venv/bin/activate` or make commands
- **Code Style**: Run `make format` before commits (black + isort)
- **Testing**: Run `make test` to verify changes (target: >80% coverage)
- **Type Hints**: All new code must include type hints
- **Documentation**: Update docstrings and relevant .md files

### Audio Processing
- Audio files should be tested with `AudioEngine` in `src/samplemind/core/engine/audio_engine.py`
- All audio analysis should use the new modules in `src/samplemind/core/analysis/`
- Supported formats: WAV, MP3, FLAC, OGG, M4A, AIFF
- Sample rate handling: Most modules resample to 16kHz or 44.1kHz

### AI Integration
- All async operations follow FastAPI patterns
- AI routing priority: Local (Ollama) > Gemini > Claude > GPT-4o
- API keys stored in environment variables (never commit)
- Fallback mechanisms for when providers are unavailable

### Database & Vector Search
- ChromaDB for embeddings and similarity search
- MongoDB for metadata and user data
- Redis for caching and pub/sub
- All vector operations in `src/samplemind/core/analysis/audio_embedder.py`

### Testing & Quality
- Test files in `tests/unit/` and `tests/integration/`
- Current coverage: 30% (target: 80%)
- 81 tests passing
- CI/CD pipeline uses pytest, ruff, black, mypy, bandit

### Project Organization
- **Documentation**: `docs/` - All guides, references, archives
- **Scripts**: `scripts/` - Setup in `scripts/setup/`, start scripts at root
- **Config**: `config/` - Configuration files
- **Data**: `data/` - Sample audio, databases
- **Deployment**: `deployment/` - Docker, Kubernetes configs

### DAW Integration
- FL Studio, Ableton Live, Logic Pro support
- Plugin formats: VST3, AU (in development)
- Test changes against DAW workflow requirements
- MIDI export functionality in `src/samplemind/core/processing/audio_to_midi.py`
