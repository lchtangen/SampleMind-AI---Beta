# Local Development Setup — SampleMind AI

Get a fully working development environment in 10 minutes.

## Prerequisites

- Python 3.12+
- Git
- 4GB RAM minimum (8GB recommended for ML models)
- FFmpeg (for audio processing): `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)

## Installation (10 minutes)

### 1. Clone and Setup Venv (2 min)

```bash
git clone https://github.com/yourusername/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies (5 min)

```bash
# Install all dependencies including dev/test tools
pip install -e .[dev]

# Verify key packages
python -c "import fastapi, torch, faiss; print('✅ All packages installed')"
```

### 3. Verify Environment (3 min)

```bash
# Check linting
ruff check src/ --statistics

# Check type hints
mypy src/ --strict --no-error-summary 2>&1 | head -20

# Run quick unit tests (must pass)
pytest tests/unit/test_exceptions.py -v

# Check health endpoint is importable
python -c "from samplemind.interfaces.api.routes.health import router; print('✅ API routes importable')"
```

## Running Locally

### Start Backend API

```bash
# Terminal 1: Start FastAPI server
python main.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Start Next.js Web UI

```bash
# Terminal 2: Start web frontend
cd apps/web
npm install
npm run dev
# Website runs at http://localhost:3000
```

### Start TUI (Terminal UI)

```bash
# Terminal 3: Start textual TUI
python -m samplemind tui
```

## Verify Everything Works

### 1. Check API Health

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 2. Check Dependencies

```bash
curl http://localhost:8000/health/deps
# Shows status of Redis, MongoDB, FAISS, AI providers
```

### 3. List AI Providers

```bash
curl http://localhost:8000/api/v1/ai/providers
```

## Configuration

### API Keys (Optional)

Create `.env` file in project root:

```bash
# AI Provider key (use at least one)
ANTHROPIC_API_KEY=sk-...        # Claude (recommended)
GEMINI_API_KEY=...              # Google Gemini (fast)
OPENAI_API_KEY=sk-...           # OpenAI GPT-4o
OLLAMA_BASE_URL=http://localhost:11434  # Local Ollama (offline)

# Database
MONGODB_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

# Server
SAMPLEMIND_DATA_DIR=~/.samplemind
MAX_UPLOAD_SIZE_MB=100
LOG_LEVEL=DEBUG
```

### Activate Offline Mode

If no cloud API keys are available:

```bash
# All requests fall back to local Ollama model
# Requires: ollama pull qwen2.5-coder:7b
docker run -d -p 11434:11434 ollama/ollama
ollama pull qwen2.5-coder:7b
```

## Useful Commands

### Database

```bash
# MongoDB (if running locally)
docker run -d -p 27017:27017 mongo:latest

# Redis (if running locally)
docker run -d -p 6379:6379 redis:latest
```

### Code Quality

```bash
# Run all quality checks
make quality
# Includes: ruff, mypy, black, isort, bandit

# Auto-fix common issues
ruff check . --fix
black . --fix
isort .
```

### Testing

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src/samplemind --cov-fail-under=40

# Run specific test file
pytest tests/unit/test_faiss_index.py -v

# Run with output capture disabled (see print statements)
pytest -s tests/unit/test_exceptions.py
```

### Build & Deployment

```bash
# Build for production
pip install -e .  # Install without dev dependencies

# Package audio models (requires GPU initially)
python scripts/package_models.py

# Verify all checks pass
make quality && pytest tests/unit/ --cov-fail-under=40
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'torch'`

**Solution:** Ensure correct venv is activated
```bash
which python  # Should show .venv/bin/python
source .venv/bin/activate
pip install torch
```

### Issue: `FAISS index not available`

**Solution:** Run index rebuild
```bash
samplemind index rebuild ~/Music/samples/
```

### Issue: API returns 503 Service Unavailable

**Solution:** Check health/deps endpoint
```bash
curl http://localhost:8000/health/deps
# Shows which services are down: Redis, MongoDB, FAISS, AI providers
```

### Issue: Tests timeout or hang

**Solution:** Tests are slow due to ML model loading. Run individual tests:
```bash
pytest tests/unit/test_exceptions.py -v  # Should be fast
```

## Next Steps

1. **Run example workflow:** `python scripts/example_workflow.py`
2. **Index your samples:** `samplemind index rebuild /path/to/samples`
3. **Try the API:** Open http://localhost:8000/docs
4. **Review error patterns:** See `ERROR_HANDLING.md`
5. **Deploy:** See deployment guide in project README

## Additional Resources

- **API Documentation:** http://localhost:8000/docs (when running locally)
- **Architecture Overview:** See `ARCHITECTURE.md`
- **Error Handling Guide:** See `ERROR_HANDLING.md`
- **API Design Patterns:** See `API_PATTERNS.md`
