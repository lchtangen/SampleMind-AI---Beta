# 🚀 Getting Started with SampleMind AI

**CLI-First AI-Powered Music Production Platform**

This guide walks you through everything you need to get SampleMind AI up and running. It covers setup for Linux, macOS, and Windows.

---

## 📋 Quick Navigation

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [First Run](#first-run)
4. [Understanding the Project](#understanding-the-project)
5. [Common Commands](#common-commands)
6. [Offline Development](#offline-development)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

---

## System Requirements

### Required
- **Python 3.11+** - Download from [python.org](https://www.python.org)
- **Git** - For cloning the repository
- **Terminal/Command Prompt** - Any standard terminal works

### Optional but Recommended
- **Ollama** - For offline AI models (see Offline Development section)
- **Make** - For convenient commands (usually pre-installed on Linux/macOS)
- **Docker** - Only if running full development stack

### Check Your System

```bash
python3 --version          # Should show 3.11+
python3 -m venv --help     # Verify venv support
git --version              # Should show 2.0+
```

---

## Installation

### Step 1: Clone Repository

```bash
# Clone the repo
git clone https://github.com/your-org/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
```

### Step 2: Complete Setup

```bash
# One-line setup (recommended)
make setup

# OR manual setup
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Step 3: Verify Installation

```bash
# Activate environment (if not already)
source .venv/bin/activate

# Run help
python main.py --help

# You should see the CLI help output
```

**✅ Installation complete!**

---

## First Run

### Start the CLI

```bash
# Make sure you're in the project directory
cd SampleMind-AI---Beta

# Activate virtual environment
source .venv/bin/activate

# Run the CLI
python main.py
```

### Try These Commands

```bash
# List available commands
python main.py --help

# Analyze an audio file
python main.py analyze --file path/to/audio.wav

# Get AI recommendations
python main.py recommend --file path/to/audio.wav

# Check system status
python main.py status
```

---

## Understanding the Project

### Project Structure

```
SampleMind-AI---Beta/
├── main.py                     # CLI entry point
├── src/samplemind/
│   ├── interfaces/             # CLI interface (primary)
│   ├── core/
│   │   └── engine/            # Audio processing engine
│   ├── ai/                    # AI integrations (Gemini, Ollama)
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── docs/                      # Documentation
├── .env                       # Configuration (create this)
└── Makefile                   # Development commands
```

### Core Components

1. **CLI Interface** - Modern terminal UI with animations
2. **Audio Engine** - Librosa-based audio analysis
3. **AI Integration** - Gemini 3 Flash (cloud) + Ollama (offline)
4. **Database Layer** - MongoDB, Redis, ChromaDB

---

## Common Commands

### Development

```bash
# Run the CLI application
python main.py

# Run tests
make test

# Check code quality
make quality

# Format code
make format

# Lint code
make lint

# Run security checks
make security
```

### Database & Services

```bash
# Start development databases
make setup-db

# Start full development stack
make dev-full

# Start API server
make dev
```

### Project Maintenance

```bash
# Clean temporary files
make clean

# Install dependencies from scratch
pip install -e .
```

---

## Offline Development

SampleMind AI uses **Ollama** for offline-first AI capabilities. This means you can work without internet!

### Install Ollama

1. Download from [ollama.ai](https://ollama.ai)
2. Install for your platform
3. Verify installation:
   ```bash
   ollama --version
   ```

### Download Models

```bash
# Download all required models (~5GB)
make install-models

# Or manually:
ollama pull phi3:mini
ollama pull qwen2.5:7b-instruct
ollama pull gemma2:2b
```

### Use Offline Models

```bash
# Launch Ollama API server
scripts/launch-ollama-api.sh

# In another terminal, run CLI
python main.py

# The CLI automatically uses Ollama when available
```

---

## Configuration

### Enable Cloud AI (Optional)

Create a `.env` file in project root:

```bash
# Google Gemini (Primary cloud AI)
GOOGLE_AI_API_KEY=your_google_api_key

# Optional: Other AI providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database URLs (if using services)
MONGODB_URL=mongodb://localhost:27017/samplemind
REDIS_URL=redis://localhost:6379/0
```

Get Gemini API key: https://ai.google.dev/

### Database Services

To use full database features:

```bash
# Start services with Docker Compose
docker-compose up -d mongodb redis chromadb
```

Or use the convenient command:
```bash
make setup-db
```

---

## Troubleshooting

### Virtual Environment Issues

```bash
# Error: python3 command not found
# Solution: Use python instead
python main.py

# Error: venv not found
# Solution: Python 3.11+ includes venv
python3 -m venv .venv
```

### Missing Dependencies

```bash
# Error: ModuleNotFoundError
# Solution: Reinstall in development mode
pip install -e .
```

### Audio File Issues

```bash
# Ensure file is in supported format (WAV, MP3, etc.)
# Supported: WAV, MP3, FLAC, OGG, M4A

# Check file exists
ls -la path/to/audio.wav
```

### Offline Mode Not Working

```bash
# Error: Ollama not available
# Solution: Install and launch Ollama

# 1. Install from ollama.ai
# 2. Start Ollama server
ollama serve

# 3. In another terminal
scripts/launch-ollama-api.sh
```

### Port Already in Use

```bash
# Error: Port 8000 already in use (for API server)
# Solution: Kill the process or use different port

# On Linux/macOS
lsof -i :8000
kill -9 <PID>

# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Platform-Specific Issues

**macOS with M1/M2 chips:**
```bash
# Use ARM-native Python
brew install python@3.11
python3 main.py
```

**Windows:**
```bash
# Use correct activation script
.venv\Scripts\activate
python main.py
```

---

## Platform-Specific Guides

For detailed platform setup instructions, see:

- **Linux Setup** - docs/guides/installation/linux.md
- **macOS Setup** - docs/guides/installation/macos.md
- **Windows Setup** - docs/guides/installation/windows.md

---

## Next Steps

### Learning Path

1. **Basics** (You are here)
   - Installation ✓
   - First run ✓
   - Basic commands

2. **Core Features** (15 min)
   - Audio file analysis
   - AI recommendations
   - Batch processing

3. **Offline Development** (20 min)
   - Install Ollama models
   - Configure offline mode
   - Test offline functionality

4. **Development** (varies)
   - Read CLAUDE.md for AI-specific guidance
   - Check docs/PROJECT_ROADMAP.md for priorities
   - Review docs/CURRENT_STATUS.md for current features

### Documentation References

- **CLAUDE.md** - Complete technical reference (for AI assistants)
- **QUICKSTART.md** - 5-minute quick setup
- **docs/PROJECT_ROADMAP.md** - Development priorities
- **docs/CURRENT_STATUS.md** - What's working now
- **docs/PROJECT_SUMMARY.md** - Project overview

---

## Support

- **Issues?** Check Troubleshooting section above
- **Questions?** Review relevant documentation
- **Contributing?** See CONTRIBUTING.md

---

**Ready to go?** Run `python main.py` and explore! 🎵

