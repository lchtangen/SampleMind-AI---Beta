# 📦 Installation Guide — SampleMind AI v3.0

> **Updated:** 2026-03-17 | **Version:** 3.0.0-alpha | **Phase:** 15 — v3.0 Migration

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | macOS 13+, Ubuntu 22.04+, Windows 11 |
| **Python** | 3.11–3.12 |
| **RAM** | 8 GB (16 GB recommended for AI models) |
| **Storage** | 20 GB free space |
| **Internet** | Required for cloud AI providers; optional with Ollama offline mode |

### Recommended Specifications

| Component | Recommendation |
|-----------|----------------|
| **CPU** | Apple M2/M3/M4, Intel i7 13th+, AMD Ryzen 7+ |
| **RAM** | 32 GB+ for large sample libraries + local AI models |
| **Storage** | NVMe SSD with 100 GB+ free space |
| **GPU** | Apple Silicon (MPS), NVIDIA RTX 30/40/50 series (CUDA 12.x) — optional |

---

## Quick Start (5 Minutes)

### Linux / macOS

```bash
# Clone the repository
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta

# Run the automated setup script
./scripts/setup/quick_start.sh
```

### Windows (PowerShell)

```powershell
# Clone the repository
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta

# Run the automated setup script
.\scripts\setup\windows_setup.ps1
```

---

## Manual Installation (Step-by-Step)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
```

### Step 2 — Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### Step 3 — Install Dependencies

**Option A: Poetry (recommended for development)**

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install all dependencies
poetry install

# Activate the Poetry shell
poetry shell
```

**Option B: pip (simpler)**

```bash
pip install -e ".[dev]"
```

### Step 4 — Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys (at least one AI provider)
# ANTHROPIC_API_KEY=sk-ant-...        # Claude 3.7 Sonnet (primary)
# GOOGLE_API_KEY=AIza...              # Gemini 2.0 Flash (fast)
# OPENAI_API_KEY=sk-proj-...         # GPT-4o (agent workflows)
# Ollama requires no API key — just install and run `ollama serve`
```

### Step 5 — Start Services (Optional)

```bash
# Start MongoDB, Redis, ChromaDB via Docker
docker-compose up -d

# Or install Ollama for offline AI (no API key needed)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
```

### Step 6 — Launch SampleMind AI

```bash
# Interactive CLI
python main.py

# Or use the Poetry script alias
samplemind

# TUI (Terminal UI)
python -m samplemind.interfaces.tui.main

# FastAPI Server
make dev   # runs on http://localhost:8000
```

---

## AI Model Setup

### Cloud Providers (API Key Required)

| Provider | Model | Purpose | Setup |
|----------|-------|---------|-------|
| **Anthropic** | `claude-3-7-sonnet-20250219` | Deep analysis, production coaching | Set `ANTHROPIC_API_KEY` |
| **Google** | `gemini-2.0-flash` | Fast classification, streaming | Set `GOOGLE_API_KEY` |
| **OpenAI** | `gpt-4o` | Agent workflows, tool use | Set `OPENAI_API_KEY` |

### Ollama — Offline AI (No API Key)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start the Ollama server
ollama serve &

# Pull recommended models
ollama pull qwen2.5:7b-instruct   # 4.4 GB — complex analysis (recommended)
ollama pull phi3:mini              # 2.2 GB — ultra-fast classification
ollama pull gemma2:2b              # 1.6 GB — quick analysis

# Verify models are available
ollama list
```

### Automatic Model Installation

```bash
make install-models   # Pulls all recommended Ollama models
```

---

## Docker Installation

```bash
# Full stack with Docker Compose (MongoDB + Redis + ChromaDB + API)
docker-compose up -d

# Check service health
docker-compose ps
```

| Service | Port | Purpose |
|---------|------|---------|
| FastAPI | 8000 | REST API + Swagger docs at `/api/docs` |
| MongoDB | 27017 | Sample metadata database |
| Redis | 6379 | Session cache + AI response cache |
| ChromaDB | 8002 | Vector similarity search |
| Ollama | 11434 | Offline AI inference |

---

## Platform-Specific Notes

### macOS

```bash
# Install system dependencies
brew install python@3.12 portaudio ffmpeg

# Apple Silicon (M1/M2/M3/M4) — PyTorch uses MPS backend automatically
# No CUDA setup needed
```

### Ubuntu / Debian Linux

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip build-essential \
    libasound2-dev libportaudio2 portaudio19-dev ffmpeg libsndfile1
```

### Windows

```powershell
# Install Python 3.12 from https://www.python.org/downloads/
# Install Git from https://git-scm.com/download/win

# Install system dependencies via Chocolatey (optional)
choco install python312 ffmpeg git

# For NVIDIA GPU support — install CUDA Toolkit 12.x
# https://developer.nvidia.com/cuda-downloads
```

---

## Verification

```bash
# Check the CLI starts correctly
python main.py --help

# Expected output includes:
# SampleMind AI v3.0.0-alpha
# Usage: main.py [OPTIONS] COMMAND [ARGS]...

# Run the test suite
make test

# Run linting
make lint

# Full validation (lint + test + type check + security)
make validate
```

---

## Troubleshooting

### Audio Libraries Missing

```bash
# macOS
brew install portaudio libsndfile

# Ubuntu/Debian
sudo apt install libasound2-dev portaudio19-dev libsndfile1-dev

# Windows — Install Visual C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve &

# Check available models
ollama list
```

### Python Version Issues

```bash
# Verify Python version (must be 3.11 or 3.12)
python3 --version

# If you have multiple Python versions, use pyenv
pyenv install 3.12
pyenv local 3.12
```

### MongoDB / Redis Connection Issues

```bash
# Check Docker services are running
docker-compose ps

# Restart services
docker-compose down && docker-compose up -d

# Check logs for errors
docker-compose logs mongodb
docker-compose logs redis
```

### Poetry Lock File Conflicts

```bash
# Regenerate the lock file
poetry lock --no-update

# Fresh install
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
poetry install
```

---

## Next Steps

After successful installation:

1. 📖 **[Quick Start Guide](QUICKSTART.md)** — Analyze your first sample in 60 seconds
2. 🖥️ **[CLI Reference](CLI.md)** — Full command reference (200+ commands)
3. 🌐 **[API Documentation](API.md)** — REST API endpoint reference
4. 🤖 **[AI Setup Guide](AI_SETUP.md)** — Configure AI providers in detail
5. 🔌 **[Plugin Guide](PLUGINS.md)** — FL Studio and Ableton integration

**Need Help?**
- 🐛 **Issues:** [GitHub Issues](https://github.com/lchtangen/SampleMind-AI---Beta/issues)
- 📖 **Docs:** [Full Documentation](../README.md)
