# 🚀 SampleMind AI — Quick Start Guide

> **Version:** 3.0.0-alpha | **Updated:** 2026-03-17 | **Time to first analysis:** ~60 seconds

---

## Start in 60 Seconds

### 1. Launch the CLI

```bash
cd SampleMind-AI---Beta
source .venv/bin/activate   # activate virtual environment
python main.py              # launch interactive CLI
```

### 2. Analyze Your First Sample

```bash
# From the CLI menu, select "Analyze Single File"
# Or run directly:
python main.py analyze path/to/your/sample.wav
```

### 3. Batch Process a Folder

```bash
python main.py batch ./my_samples/
```

---

## 📊 What You Get

### AI-Powered Analysis (4 Providers)

| Provider | Model | Specialization | Speed |
|----------|-------|---------------|-------|
| **Ollama** | `qwen2.5:7b-instruct` | Quick analysis (offline, no API key) | <100 ms |
| **Anthropic** | `claude-3-7-sonnet-20250219` | Deep analysis, production coaching | ~3 s |
| **Google** | `gemini-2.0-flash` | Genre classification, streaming | ~1 s |
| **OpenAI** | `gpt-4o` | Agent workflows, tool use | ~2 s |

### Analysis Output Includes

✅ **Audio Features** — BPM, key (with Camelot notation), duration, time signature
✅ **Spectral Analysis** — MFCC, chroma, spectral centroid/bandwidth/rolloff
✅ **Genre Classification** — Primary genre, subgenres, confidence scores
✅ **Mood Detection** — Valence (sad→happy), arousal (calm→energetic)
✅ **Production Analysis** — Mix quality, frequency balance, dynamic range
✅ **FL Studio Integration** — Plugin recommendations, effect chains, mixer routing
✅ **Creative Suggestions** — Remix ideas, arrangement tips, similar references

---

## 🎨 Interactive CLI Menu

```
🎵 SAMPLEMIND AI — Main Menu

 1. 🎯 Analyze Single File          — AI-powered audio analysis
 2. 📁 Batch Process Directory      — Analyze multiple files
 3. 📁 Analyze Folder Samples       — All audio in a folder
 4. 🔍 Scan & Preview              — Preview directory contents
 5. ⚙️  Configuration               — Settings & preferences
 6. 📊 System Status                — Performance metrics
 7. 🤖 AI Provider Settings         — Configure Claude/Gemini/GPT/Ollama
 8. 💡 Production Tips              — AI coaching & advice
 9. 🎛️  FL Studio Integration        — DAW-specific tools
 A. 📈 Session Analytics            — Current session stats
 0. 🚪 Exit
```

---

## 📈 Example Analysis

```bash
python main.py analyze samples/my_beat.wav
```

```
🎵 Analyzing: my_beat.wav

📋 File Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 File:         my_beat.wav
⏱️  Duration:     5.00 s
🎵 Tempo:        120.2 BPM
🎼 Key:          C major (8B Camelot)
🤖 AI Provider:  anthropic
⚡ Model:        claude-3-7-sonnet-20250219
⏱️  Processing:   ~3 s

🤖 AI Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is a punchy, groove-centric electronic music loop,
defined by a tightly compressed low-end and a compelling,
syncopated rhythm...

🎛️ FL Studio Recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Maximus: Multi-band compression and final limiting
• Fruity Limiter: Aggressive sidechaining
• Gross Beat: Rhythmic gating and stutter effects
• Fruity Parametric EQ 2: Surgical EQ cuts
```

---

## 🔑 Configuration

### API Keys

Set your API keys in `.env` (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```bash
# At least one AI provider is needed (Ollama requires no key)
ANTHROPIC_API_KEY=sk-ant-your-key-here      # Claude (primary)
GOOGLE_API_KEY=your-google-key-here          # Gemini (fast)
OPENAI_API_KEY=sk-proj-your-key-here         # GPT-4o (agents)

# Ollama — no API key needed, just run: ollama serve
OLLAMA_HOST=http://localhost:11434
```

> ⚠️ **Never commit API keys to version control.** The `.env` file is already in `.gitignore`.

### AI Provider Priority

```
Priority 0: Ollama   → OFFLINE/INSTANT — quick analysis (<100 ms, no API key)
Priority 1: Claude   → PRIMARY         — deep analysis, extended thinking
Priority 2: Gemini   → FAST            — genre/rhythm, streaming, multimodal
Priority 3: GPT-4o   → AGENTS          — tool use, agent workflows
```

---

## 💰 Cost Estimates

| Provider | Model | Cost per Analysis | Speed |
|----------|-------|-------------------|-------|
| **Ollama** | qwen2.5:7b | **Free** (local) | <100 ms |
| **Google** | gemini-2.0-flash | ~$0.01–0.02 | ~1 s |
| **Anthropic** | claude-3-7-sonnet | ~$0.03–0.05 | ~3 s |
| **OpenAI** | gpt-4o | ~$0.05–0.10 | ~2 s |

---

## 🖥️ Alternative Interfaces

### Terminal UI (TUI)

```bash
python -m samplemind.interfaces.tui.main
```

Features: 13 interactive screens, waveform visualization, keyboard navigation, 6 themes.

### REST API

```bash
make dev   # starts FastAPI on http://localhost:8000

# API docs available at:
# http://localhost:8000/api/docs     (Swagger UI)
# http://localhost:8000/api/redoc    (ReDoc)
```

### Python Library

```python
from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel

engine = AudioEngine()
result = await engine.analyze("sample.wav", level=AnalysisLevel.PROFESSIONAL)
print(f"BPM: {result.tempo}, Key: {result.key}")
```

---

## 🔧 Troubleshooting

### Missing Dependencies

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

### Ollama Not Responding

```bash
# Check if running
curl http://localhost:11434/api/tags

# Start if needed
ollama serve &
```

### No AI Providers Configured

```bash
# Use Ollama (free, offline, no API key needed)
ollama serve &
ollama pull qwen2.5:7b-instruct
```

---

## 📚 Next Steps

1. 📖 **[CLI Reference](CLI.md)** — Full command reference (200+ commands)
2. 🌐 **[API Documentation](API.md)** — REST endpoint reference
3. 🤖 **[AI Setup Guide](AI_SETUP.md)** — Detailed provider configuration
4. 🎛️ **[Plugin Guide](PLUGINS.md)** — FL Studio & Ableton integration
5. 🏗️ **[Architecture](ARCHITECTURE.md)** — System design overview

---

*SampleMind AI v3.0 — AI-Powered Music Production Platform*
