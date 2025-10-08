# 🤖 Devin AI IDE - Setup Guide for SampleMind AI
## Complete Integration & Synchronization Instructions

**Repository:** samplemind-ai-v2-phoenix  
**Owner:** lchtangen  
**Branch:** performance-upgrade-v7  
**Date:** October 9, 2025

---

## 🎯 Quick Start - Connect to Devin AI

### Step 1: Open Repository in Devin AI

**Option A: Via GitHub URL**
```
1. Open Devin AI IDE (https://devin.ai)
2. Click "New Project" or "Import from GitHub"
3. Enter repository URL:
   https://github.com/lchtangen/samplemind-ai-v2-phoenix
4. Select branch: performance-upgrade-v7
5. Click "Clone & Open"
```

**Option B: Via Git Clone in Devin**
```bash
# In Devin's terminal:
git clone https://github.com/lchtangen/samplemind-ai-v2-phoenix.git
cd samplemind-ai-v2-phoenix
git checkout performance-upgrade-v7
```

---

## 🔐 Configure Environment Variables in Devin

### Critical: Never Hardcode API Keys!

**Devin AI has a built-in secrets manager. Configure there:**

1. **Open Devin Settings** → Secrets/Environment Variables
2. **Add the following variables:**

```bash
# AI API Keys (REQUIRED)
GOOGLE_AI_API_KEY=<your_google_gemini_api_key>
ANTHROPIC_API_KEY=<your_anthropic_claude_api_key>
OPENAI_API_KEY=<your_openai_api_key>

# Database (REQUIRED for production features)
MONGODB_URI=mongodb://localhost:27017/samplemind
REDIS_URL=redis://localhost:6379

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
PYTHONPATH=/workspace/samplemind-ai-v2-phoenix/src

# AI Model Configuration
DEFAULT_MODEL=gemini-2.5-pro
ANTHROPIC_MODEL=claude-sonnet-4.5
OPENAI_MODEL=gpt-5

# Performance Settings
MAX_WORKERS=4
BATCH_SIZE=32
ENABLE_CACHE=true
```

3. **Save & Restart** Devin's environment

---

## 🐍 Python Environment Setup

### Automated Setup (Recommended)

Devin AI can run this automatically:

```bash
# 1. Create virtual environment
python3.11 -m venv .venv

# 2. Activate environment (Devin does this automatically)
source .venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Install development tools
pip install -r requirements-dev.txt

# 6. Install test dependencies
pip install -r requirements-test.txt

# 7. Verify installation
python -c "import samplemind; print('✅ SampleMind AI installed successfully!')"
```

### Manual Verification

```bash
# Check Python version (should be 3.11 or 3.12)
python --version

# Check critical packages
python -c "import fastapi, beanie, librosa, transformers; print('✅ All core packages installed')"

# Run tests
pytest tests/ -v
```

---

## 🌐 Frontend Setup (Web App)

### Install Node.js Dependencies

```bash
# Navigate to web app
cd web-app/

# Install dependencies (npm or pnpm)
npm install
# or
pnpm install

# Verify installation
npm run dev  # Should start Vite dev server on http://localhost:5173
```

### Frontend Environment Variables

Create `web-app/.env.local` in Devin's secrets:

```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENVIRONMENT=development
```

---

## 🐳 Docker Setup (Optional)

### Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Started:
- **Backend API:** http://localhost:8000
- **MongoDB:** localhost:27017
- **Redis:** localhost:6379
- **Frontend:** http://localhost:5173

---

## 🚀 Running the Application in Devin

### Backend (FastAPI)

```bash
# Method 1: Using uvicorn directly
cd /workspace/samplemind-ai-v2-phoenix
source .venv/bin/activate
uvicorn src.samplemind.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using the main script
python main.py

# Method 3: Using Docker
docker-compose up backend
```

### CLI Tool

```bash
# Activate environment
source .venv/bin/activate

# Run CLI
python -m samplemind.cli --help

# Example: Analyze audio file
python -m samplemind.cli analyze /path/to/audio.mp3 --ai-provider gemini

# Example: Batch process
python -m samplemind.cli batch-analyze /path/to/audio/folder/
```

### Frontend (React + Vite)

```bash
cd web-app/
npm run dev  # Starts on http://localhost:5173
```

---

## 🧪 Running Tests in Devin

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/samplemind --cov-report=html

# Run specific test file
pytest tests/test_audio_processing.py -v

# Run with detailed output
pytest -vv --tb=short
```

### Frontend Tests

```bash
cd web-app/
npm run test
```

---

## 🤖 Devin AI Specific Configuration

### 1. Devin Task Automation

Create `.devin/tasks.json` for common workflows:

```json
{
  "tasks": [
    {
      "name": "Start Backend",
      "command": "source .venv/bin/activate && uvicorn src.samplemind.main:app --reload",
      "description": "Start FastAPI backend server"
    },
    {
      "name": "Start Frontend",
      "command": "cd web-app && npm run dev",
      "description": "Start React frontend with Vite"
    },
    {
      "name": "Run Tests",
      "command": "pytest tests/ -v",
      "description": "Run all backend tests"
    },
    {
      "name": "Format Code",
      "command": "black src/ && ruff check src/ --fix",
      "description": "Format and lint Python code"
    },
    {
      "name": "Analyze Audio",
      "command": "python -m samplemind.cli analyze",
      "description": "Run CLI audio analysis"
    }
  ]
}
```

### 2. Devin Code Context

Tell Devin about the project structure:

```
SampleMind AI is an AI-powered music production platform with:

Backend (Python 3.11-3.12):
- FastAPI async REST API
- Beanie ODM for MongoDB
- Redis caching
- Audio processing with librosa + essentia
- Multi-AI integration (Gemini, Claude, GPT, Ollama)

Frontend (React 19 + TypeScript):
- Vite 7 build tool
- Tailwind CSS 4 + Radix UI
- wavesurfer.js for audio visualization
- Zustand for state management

Key Files:
- src/samplemind/main.py - FastAPI entry point
- src/samplemind/core/database/mongo.py - Database models
- src/samplemind/core/audio/ - Audio processing
- src/samplemind/api/ - API routes
- web-app/src/ - Frontend React app
```

### 3. Devin AI Assistant Prompts

Use these prompts when asking Devin for help:

**For Bug Fixes:**
```
"Devin, I'm getting an error in the audio processing module. 
File: src/samplemind/core/audio/processor.py
Error: [paste error here]
Please analyze and fix while maintaining async/await patterns and type hints."
```

**For New Features:**
```
"Devin, add a new feature to analyze audio tempo using madmom library.
Requirements:
1. Create new function in src/samplemind/core/audio/analyzer.py
2. Add async support
3. Cache results in Redis
4. Add API endpoint at POST /api/v1/audio/tempo
5. Write tests in tests/test_tempo_analysis.py
6. Update API documentation

Follow existing code patterns in the codebase."
```

**For Refactoring:**
```
"Devin, refactor the AI provider integration to use the strategy pattern.
Current: src/samplemind/ai/providers/
Goal: Cleaner separation of concerns, easier to add new AI providers
Maintain: All existing functionality, type hints, async patterns"
```

---

## 📁 Project Structure for Devin

```
samplemind-ai-v2-phoenix/
├── src/samplemind/           # Main Python package
│   ├── main.py              # FastAPI entry point
│   ├── core/                # Core functionality
│   │   ├── audio/           # Audio processing
│   │   ├── database/        # MongoDB models
│   │   └── cache/           # Redis caching
│   ├── api/                 # API routes
│   ├── ai/                  # AI provider integrations
│   └── cli/                 # CLI commands
├── web-app/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── design-system/   # Design tokens
│   │   └── lib/             # Utilities
│   └── package.json
├── tests/                   # Backend tests
├── docs/                    # Documentation
├── deployment/              # Docker, K8s configs
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Python project config
└── docker-compose.yml      # Docker services
```

---

## 🔍 Debugging in Devin

### Enable Debug Logging

```python
# In Devin's terminal or code:
import logging
logging.basicConfig(level=logging.DEBUG)

# For specific modules:
logging.getLogger('samplemind.audio').setLevel(logging.DEBUG)
```

### FastAPI Debug Mode

```bash
# Start with debug and reload
uvicorn src.samplemind.main:app --reload --log-level debug
```

### Devin Breakpoints

Devin supports Python debugger:

```python
# Add to code where you want to inspect:
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

---

## 🌟 Best Practices for Working with Devin

### 1. Clear Communication
- Be specific about file paths
- Mention exact line numbers if possible
- Provide error messages in full

### 2. Incremental Changes
- Ask Devin to make one feature at a time
- Review changes before asking for more
- Test after each major change

### 3. Code Quality
- Ask Devin to follow existing patterns
- Request type hints for all functions
- Ensure async/await is used correctly
- Ask for docstrings and comments

### 4. Testing
- Always request tests with new features
- Ask Devin to run tests after changes
- Review test coverage reports

### 5. Documentation
- Update docstrings when code changes
- Keep README.md current
- Document new API endpoints

---

## 🚨 Common Issues & Solutions

### Issue 1: Import Errors
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=/workspace/samplemind-ai-v2-phoenix/src:$PYTHONPATH
```

### Issue 2: MongoDB Connection Failed
```bash
# Solution: Start MongoDB
docker-compose up -d mongodb
# Or install locally:
sudo systemctl start mongodb
```

### Issue 3: Redis Connection Failed
```bash
# Solution: Start Redis
docker-compose up -d redis
# Or install locally:
sudo systemctl start redis
```

### Issue 4: Audio Library Missing
```bash
# Solution: Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y libsndfile1 ffmpeg libportaudio2

# Then reinstall Python packages
pip install --force-reinstall soundfile librosa
```

### Issue 5: Frontend Port Conflict
```bash
# Solution: Change Vite port
cd web-app/
npm run dev -- --port 5174
```

---

## 🎓 Learning Resources

### For Devin to Reference:
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Beanie ODM:** https://beanie-odm.dev
- **Librosa:** https://librosa.org/doc/latest/
- **React 19:** https://react.dev
- **Vite:** https://vitejs.dev

### Project-Specific Docs:
- `docs/ARCHITECTURE.md` - System architecture
- `docs/DEVELOPMENT.md` - Development guidelines
- `web-app/SAMPLEMIND_AI_COMPREHENSIVE_RESEARCH.md` - Technology research
- `.github/copilot-instructions.md` - AI assistant guidelines

---

## ✅ Verification Checklist

After setup in Devin AI, verify:

### Backend
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] MongoDB running
- [ ] Redis running
- [ ] FastAPI server starts successfully
- [ ] Tests pass: `pytest`
- [ ] API docs accessible: http://localhost:8000/docs

### Frontend
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] Dev server starts: `npm run dev`
- [ ] No build errors
- [ ] Can access UI: http://localhost:5173

### Integration
- [ ] Frontend can call backend API
- [ ] WebSocket connections work
- [ ] File uploads work
- [ ] Audio playback works
- [ ] AI analysis returns results

---

## 🚀 Ready to Code!

**You're all set!** Devin AI now has full access to:
- ✅ Complete SampleMind AI codebase
- ✅ All documentation and guides
- ✅ Development environment
- ✅ Testing framework
- ✅ Deployment configurations

**Next Steps:**
1. Ask Devin to familiarize itself with the codebase
2. Run the test suite to ensure everything works
3. Start building features or fixing bugs!

**Example First Task for Devin:**
```
"Devin, please:
1. Review the codebase structure
2. Run all tests and report results
3. Start the backend and frontend servers
4. Verify the API is working by making a test request
5. Report any issues found"
```

---

## 📞 Support & Resources

**Documentation:** `/docs` directory  
**Issues:** https://github.com/lchtangen/samplemind-ai-v2-phoenix/issues  
**Wiki:** https://github.com/lchtangen/samplemind-ai-v2-phoenix/wiki

---

**Setup Guide Version:** 1.0.0  
**Last Updated:** October 9, 2025  
**Maintained by:** SampleMind AI Development Team
