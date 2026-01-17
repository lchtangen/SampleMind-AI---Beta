# ⚡ SampleMind AI - Quick Start Guide

**CLI-First AI-Powered Music Production Platform**

Welcome to SampleMind AI! This guide will get you up and running in minutes. We're focusing on the CLI as our primary interface with offline-first capabilities.

---

## 🚀 Installation (5 minutes)

### Prerequisites
- Python 3.11+
- Git
- Optional: Ollama for offline AI (see below)

### Quick Setup

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd SampleMind-AI---Beta

# 2. Complete setup
make setup

# 3. (Optional) Install offline AI models
make install-models
```

**That's it!** Your development environment is ready.

---

## 🎯 First Run - CLI Application

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the CLI
python main.py
```

You should see the interactive CLI interface with available commands.

### Common First Commands

```bash
# Show help and available commands
python main.py --help

# Analyze an audio file
python main.py analyze --file /path/to/audio.wav

# List available commands
python main.py commands
```

---

## 🔧 Configuration (Optional)

### Enable Cloud AI (Gemini 3 Flash)

Create a `.env` file in the project root:

```bash
# Google Gemini (Primary AI)
GOOGLE_AI_API_KEY=your_google_api_key

# Optional: Other AI providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

Get your Gemini API key at: https://ai.google.dev/

### Offline-First Development

For development without internet, use Ollama:

```bash
# Install Ollama models (downloads ~5GB)
make install-models

# Launch Ollama API server
scripts/launch-ollama-api.sh
```

The CLI will automatically use Ollama models when available.

---

## 🧪 Development Workflow

### Running Tests
```bash
make test
```

### Code Quality
```bash
make quality      # Run all checks
make lint         # Linting only
make format       # Format code
```

### Database Services (Optional)
```bash
make setup-db     # Start MongoDB, Redis, ChromaDB
make dev-full     # Full development stack
```

---

## 📚 Next Steps

1. **Read GETTING_STARTED.md** - Detailed setup for your platform
2. **Check CLAUDE.md** - Complete development reference
3. **Explore docs/PROJECT_ROADMAP.md** - Development priorities
4. **Review docs/CURRENT_STATUS.md** - Current feature status

---

## 🆘 Troubleshooting

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Python Version
Ensure Python 3.11+:
```bash
python3 --version
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Offline Mode Not Working
```bash
# Verify Ollama is installed
ollama list

# Launch Ollama server
ollama serve
```

---

## 🎨 CLI Features

- **Audio Analysis**: Analyze tempo, key, spectral features
- **AI-Powered Recommendations**: Get intelligent sample suggestions
- **Batch Processing**: Process multiple audio files
- **Offline-First**: Works without internet using Ollama models
- **Interactive Mode**: User-friendly terminal interface with animations

---

## 💡 Tips

- **CLI First**: The CLI is the primary product - use it for development and testing
- **Offline Development**: Use Ollama models for fast iteration without API costs
- **Performance**: Target <1 second response time for common operations
- **Cross-Platform**: Works on Linux, macOS, and Windows

---

## 📖 Documentation

- **CLAUDE.md** - Complete development reference for AI assistants
- **GETTING_STARTED.md** - Detailed setup guide
- **README.md** - Project overview
- **docs/PROJECT_ROADMAP.md** - Development priorities

---

## 🤝 Contributing

See CONTRIBUTING.md for guidelines on contributing to SampleMind AI.

---

**Ready?** Run `python main.py` and start exploring! 🎵
