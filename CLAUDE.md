# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## Architecture Overview

### Core System Design
SampleMind AI is a hybrid AI-powered music production platform with three main architectural layers:

1. **Audio Processing Engine** (`src/samplemind/core/engine/`)
   - Real-time audio analysis using librosa, soundfile, scipy
   - Feature extraction: tempo, key, chroma, MFCC, spectral features
   - Harmonic/percussive separation and rhythm pattern analysis
   - Caching system for performance optimization

2. **Hybrid AI Architecture** (`src/samplemind/ai/`)
   - **Local AI**: Ultra-fast models via Ollama (Phi3, Gemma2, Qwen2.5) for <100ms responses
   - **Cloud AI**: OpenAI GPT-4o, Anthropic Claude for complex analysis
   - **Smart Routing**: Automatic model selection based on task complexity

3. **Multi-Interface System** (`src/samplemind/interfaces/`)
   - **CLI**: Typer-based command line interface
   - **API**: FastAPI async web service
   - **GUI**: Web and Electron applications

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

## Key Technical Details

### Dependencies and Stack
- **Core**: Python 3.11+, FastAPI, Poetry for dependency management
- **Audio**: librosa, soundfile, scipy, numpy for signal processing
- **AI/ML**: torch, transformers, sentence-transformers, ollama client
- **Database**: motor (MongoDB), redis, chromadb
- **Testing**: pytest with asyncio, coverage, mock support
- **Code Quality**: ruff, black, isort, mypy, bandit for linting and security

### Performance Considerations
- Async processing throughout with ThreadPoolExecutor for CPU-bound tasks
- Feature caching with configurable size limits and SHA-256 file hashing
- Batch processing support for multiple audio files
- Analysis levels: BASIC, STANDARD, DETAILED, PROFESSIONAL for scalable complexity

### Configuration
- Poetry scripts: `samplemind` and `smai` as entry points
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
- `src/samplemind/core/engine/` - Audio processing engine
- `src/samplemind/integrations/` - AI provider integrations (Google, OpenAI)
- `src/samplemind/interfaces/` - CLI, API, GUI interfaces
- `src/samplemind/utils/` - Utilities (cross-platform file picker, etc.)

### Tests (`tests/`)
Comprehensive test suite:
- `tests/unit/` - Unit tests (81 tests passing, 30% coverage)
- `tests/integration/` - Integration tests
- `tests/conftest.py` - Shared fixtures and configuration

### Configuration (`config/`)
Configuration files for various tools

### Data (`data/`)
Sample audio files, databases, and data storage

## Important Notes

- The project uses Python venv for dependency management - always use `source .venv/bin/activate` or the make commands
- Audio files should be tested with the `AudioEngine` class in `src/samplemind/core/engine/audio_engine.py`
- All async operations should use the established patterns in the FastAPI application
- Vector embeddings and similarity search are core features - consider ChromaDB integration for new features
- FL Studio integration is a primary use case - test changes against DAW workflow requirements
- **All documentation is in `docs/`** - guides, references, and archives are organized there
- **All scripts are in `scripts/`** - setup scripts in `scripts/setup/`, start scripts at root level of scripts/
