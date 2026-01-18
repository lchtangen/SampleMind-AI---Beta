# SampleMind AI v6 - Beta Quickstart Guide

**Welcome to SampleMind AI Beta!** 🎵

This guide will get you up and running in 5 minutes.

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
# Setup everything
make setup

# Or manually
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Configure API Keys (Optional but Recommended)

Edit `.env` file:

```bash
# Google Gemini AI (Primary)
GOOGLE_AI_API_KEY=your_google_api_key_here

# OpenAI (Fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Database URLs (already configured)
MONGODB_URL=mongodb://localhost:27017/samplemind
REDIS_URL=redis://localhost:6379/0
```

### 3. Start Database Services

```bash
# Start MongoDB, Redis, ChromaDB
docker-compose up -d mongodb redis chromadb

# Verify services
docker ps
```

---

## 🎵 First Steps - Try the Demos!

### Demo 1: Basic Audio Analysis

```bash
# Analyze any audio file
python scripts/demo_audio_analysis.py
```

**What it does:**
1. Opens file picker (choose any audio file)
2. Analyzes tempo, key, energy, mood
3. Shows detailed musical features
4. Displays performance stats

**Try it with:** WAV, MP3, FLAC, AIFF files

---

### Demo 2: AI-Powered Analysis

```bash
# Get AI insights about your music
python scripts/demo_ai_integration.py
```

**What it does:**
1. Analyzes audio file
2. Sends features to AI (Google Gemini or OpenAI)
3. Gets creative suggestions
4. Shows genre, mood, production tips

**Requires:** API key in .env file

---

### Demo 3: Batch Processing

```bash
# Process entire folder of samples
python scripts/demo_batch_processing.py
```

**What it does:**
1. Scans folder for audio files
2. Batch analyzes all files
3. Shows summary statistics
4. Super fast with caching

**Perfect for:** Sample libraries, beat folders

---

## 📋 Test the File Picker

```bash
# Test cross-platform file selection
python test_file_picker_beta.py
```

**What to expect:**
- 1 dialog asks: File or Folder?
- 1 dialog for selection
- No multiple windows!

**Works on:** Ubuntu, macOS, Windows

---

## 🧪 Run Tests

```bash
# Run all tests
./run_unit_tests.sh

# Run specific tests
pytest tests/unit/core/test_audio_engine.py -v

# With coverage
./run_unit_tests.sh --cov-report=html
open htmlcov/index.html
```

**Current Status:** 92/140 tests passing (66%)

---

## 💡 Common Tasks

### Analyze a Single Audio File

```python
from samplemind.core.engine import AudioEngine
from samplemind.utils import select_audio_file
import asyncio

async def analyze():
    # Initialize engine
    engine = AudioEngine()

    # Select file
    audio_file = select_audio_file("Choose Audio")

    # Analyze
    result = await engine.analyze_audio_async(audio_file)

    print(f"Tempo: {result.tempo} BPM")
    print(f"Key: {result.key}")
    print(f"Energy: {result.energy}")

    await engine.shutdown()

asyncio.run(analyze())
```

### Use AI for Creative Insights

```python
from samplemind.integrations import GoogleAIMusicProducer
import asyncio

async def ai_analyze():
    producer = GoogleAIMusicProducer()  # Uses .env API key

    features = {
        'tempo': 128,
        'key': 'C minor',
        'energy': 0.8,
        'mood': 'energetic'
    }

    result = await producer.analyze_music_comprehensive(features)

    print(f"Genre: {result.primary_genre}")
    print(f"Mood: {result.primary_mood}")
    print("Creative ideas:")
    for idea in result.creative_applications[:3]:
        print(f"  - {idea}")

asyncio.run(ai_analyze())
```

### Process Multiple Files

```python
from samplemind.core.engine import AudioEngine
from pathlib import Path
import asyncio

async def batch_process():
    engine = AudioEngine()

    # Get all audio files in folder
    folder = Path("~/Music/Samples").expanduser()
    files = list(folder.glob("*.wav"))

    # Batch analyze
    results = await engine.batch_analyze(files)

    # Show results
    for file_path, result in results.items():
        print(f"{file_path.name}: {result.tempo} BPM")

    await engine.shutdown()

asyncio.run(batch_process())
```

---

## 📁 Project Structure

```
samplemind-ai-v6/
├── src/samplemind/          # Main source code
│   ├── core/                # Audio engine, database
│   ├── integrations/        # AI providers (Gemini, OpenAI)
│   ├── interfaces/          # CLI, API, GUI
│   └── utils/               # File pickers, helpers
├── scripts/                 # Demo and utility scripts
│   ├── demo_audio_analysis.py      # ⭐ Try this first!
│   ├── demo_ai_integration.py      # AI-powered analysis
│   └── demo_batch_processing.py    # Process multiple files
├── tests/                   # Test suite
├── data/                    # Sample data, cache
├── .env                     # Configuration (API keys)
└── docker-compose.yml       # Services (MongoDB, Redis)
```

---

## 🔧 Configuration Files

### .env - Environment Variables
```bash
# AI API Keys
GOOGLE_AI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Database
MONGODB_URL=mongodb://localhost:27017/samplemind
REDIS_URL=redis://localhost:6379/0
CHROMADB_URL=http://localhost:8002

# JWT Auth
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### pyproject.toml - Dependencies
- Already configured
- Uses Poetry-style dependencies
- All packages installed via `make setup`

---

## 🎯 Beta Testing Checklist

### ✅ Core Features to Test

- [ ] **Audio Analysis**
  - [ ] Analyze single file (WAV, MP3, FLAC)
  - [ ] Check tempo accuracy
  - [ ] Check key detection
  - [ ] Verify energy and mood

- [ ] **File Picker**
  - [ ] Test on your OS (Ubuntu/macOS/Windows)
  - [ ] Choose file
  - [ ] Choose folder
  - [ ] Verify no multiple dialogs

- [ ] **AI Integration**
  - [ ] Test with Google Gemini
  - [ ] Test with OpenAI
  - [ ] Verify creative suggestions
  - [ ] Check genre detection

- [ ] **Batch Processing**
  - [ ] Process folder of samples
  - [ ] Verify all files processed
  - [ ] Check performance/speed
  - [ ] Test cache system

- [ ] **API Testing**
  - [ ] Start API server: `make dev`
  - [ ] Access http://localhost:8000/docs
  - [ ] Try /analyze endpoint
  - [ ] Test file upload

---

## 🐛 Troubleshooting

### File Picker Not Working

**Ubuntu:**
```bash
# Install Zenity if missing
sudo apt install zenity
```

**macOS:**
- Should work out of the box
- If not, check security preferences

**Windows:**
- Ensure Python has Tkinter
- Reinstall Python if needed

### AI Analysis Fails

**Check API key:**
```bash
# Verify key is set
source .venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_AI_API_KEY'))"
```

**Test API directly:**
```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-pro')
response = model.generate_content('Hello')
print(response.text)
```

### Database Connection Issues

```bash
# Check if services are running
docker ps

# Restart services
docker-compose restart mongodb redis chromadb

# Check logs
docker-compose logs mongodb
```

### Tests Failing

```bash
# Run specific test
pytest tests/unit/core/test_audio_engine.py -xvs

# Clear cache and retry
rm -rf tests/fixtures/*.wav
pytest tests/unit/core/ -v
```

---

## 📚 Documentation

- **README.md** - Main project overview
- **CLAUDE.md** - Developer instructions
- **FILE_PICKER_FIXED.md** - File picker details
- **CROSS_PLATFORM_FILE_PICKER.md** - Platform support
- **TEST_RESULTS_WITH_AI.md** - Test status
- **docs/** - Comprehensive documentation

---

## 🚀 Next Steps

1. **Try all demos** - Get familiar with features
2. **Test with your music** - Real-world testing
3. **Report bugs** - Help us improve
4. **Check performance** - Speed and accuracy
5. **Try API endpoints** - Test REST API

---

## 💬 Feedback

Found a bug? Want a feature? Let us know!

- File an issue on GitHub
- Test all platforms if possible
- Check existing issues first
- Include error messages

---

## 🎓 Learning Resources

### Core Concepts

**Audio Features:**
- **Tempo:** Beats per minute (BPM)
- **Key:** Musical key (C major, A minor, etc.)
- **Energy:** 0.0 to 1.0 (low to high)
- **Mood:** Descriptive (energetic, calm, dark, bright)

**Analysis Levels:**
- **BASIC:** Quick (tempo, key only)
- **STANDARD:** Balanced (+ energy, mood)
- **DETAILED:** Comprehensive (+ spectral features)
- **PROFESSIONAL:** Everything (+ harmonic analysis)

### API Examples

**FastAPI Server:**
```bash
# Start server
make dev

# Visit API docs
open http://localhost:8000/docs

# Test endpoint
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@sample.wav"
```

---

## ✅ Beta Ready Checklist

### You're ready to test when:

- [x] Environment set up
- [x] Dependencies installed
- [x] Services running (Docker)
- [x] API keys configured
- [x] Demo scripts work
- [x] File picker tested
- [x] Tests passing

### Start testing with:

```bash
# 1. Basic audio analysis
python scripts/demo_audio_analysis.py

# 2. AI-powered insights
python scripts/demo_ai_integration.py

# 3. Batch processing
python scripts/demo_batch_processing.py
```

---

## 🎉 Welcome to SampleMind AI!

You're now ready to:
- ✅ Analyze audio files
- ✅ Get AI-powered insights
- ✅ Process batches efficiently
- ✅ Integrate into your workflow

**Happy testing!** 🚀

Need help? Check the docs or run demos with `-h` for help.
