# 🚀 Quick Start - GitHub & Devin AI Sync

## One-Page Reference Card

**Repository:** https://github.com/lchtangen/SampleMind-AI---Beta
**Branch:** `performance-upgrade-v7`
**Status:** ✅ READY TO USE

---

## 📋 Devin AI - 3-Step Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
git checkout performance-upgrade-v7
```

### 2️⃣ Configure Secrets (In Devin's Secrets Manager)

```bash
GOOGLE_AI_API_KEY=<your_key>
ANTHROPIC_API_KEY=<your_key>
OPENAI_API_KEY=<your_key>
MONGODB_URI=mongodb://localhost:27017/samplemind
REDIS_URL=redis://localhost:6379
```

### 3️⃣ Install & Run

```bash
# Backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.samplemind.main:app --reload

# Frontend
cd web-app/
npm install
npm run dev
```

---

## 🔐 Security Quick Checklist

✅ **Protected by .gitignore:**

- `.env` files
- Database files
- Model files
- API keys
- User uploads
- Virtual environments
- node_modules

✅ **Safe in Repository:**

- Source code
- Documentation
- Tests
- `.env.example` (templates only)

---

## 📚 Essential Documentation

| File                                              | Purpose                 |
| ------------------------------------------------- | ----------------------- |
| `GITHUB_SECURITY_CHECKLIST.md`                    | Complete security guide |
| `DEVIN_AI_SETUP_GUIDE.md`                         | Detailed Devin setup    |
| `GITHUB_DEVIN_SYNC_COMPLETE.md`                   | Sync completion summary |
| `web-app/SAMPLEMIND_AI_COMPREHENSIVE_RESEARCH.md` | 115+ tech research      |
| `.env.example`                                    | Environment template    |

---

## ⚡ Common Commands

### Git Operations

```bash
# Pull latest changes
git pull origin performance-upgrade-v7

# Create new branch
git checkout -b feature/your-feature

# Push changes
git add .
git commit -m "your message"
git push origin your-branch
```

### Backend

```bash
# Start API server
uvicorn src.samplemind.main:app --reload

# Run tests
pytest tests/ -v

# CLI tool
python -m samplemind.cli analyze audio.mp3
```

### Frontend

```bash
# Dev server
npm run dev

# Build
npm run build

# Preview production
npm run preview
```

### Docker

```bash
# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

---

## 🤖 Devin AI Quick Prompts

**Analyze Codebase:**

```
"Devin, analyze the SampleMind AI codebase and summarize:
1. Main architecture
2. Key technologies used
3. Current development status
4. Areas needing improvement"
```

**Add Feature:**

```
"Devin, add audio tempo detection using madmom:
- Create function in src/samplemind/core/audio/analyzer.py
- Add API endpoint POST /api/v1/audio/tempo
- Write tests in tests/test_tempo.py
- Update documentation"
```

**Fix Bug:**

```
"Devin, fix the error in src/samplemind/core/audio/processor.py
line 45 where librosa.load() fails on MP3 files.
Maintain async patterns and add error handling."
```

---

## 🛡️ Security Rules

### ✅ ALWAYS:

- Use environment variables for secrets
- Store keys in Devin's secrets manager
- Review changes before committing
- Run tests before pushing

### ❌ NEVER:

- Hardcode API keys
- Commit `.env` files
- Share production credentials
- Disable security scanning

---

## 🆘 Quick Troubleshooting

**Import Error:**

```bash
export PYTHONPATH=/workspace/SampleMind-AI---Beta/src:$PYTHONPATH
```

**MongoDB Not Running:**

```bash
docker-compose up -d mongodb
```

**Port Conflict:**

```bash
npm run dev -- --port 5174  # Frontend
uvicorn src.samplemind.main:app --port 8001  # Backend
```

---

## 🎯 You're Ready!

**Next Step:** Open Devin AI and paste:

```
"Clone https://github.com/lchtangen/SampleMind-AI---Beta.git
and follow DEVIN_AI_SETUP_GUIDE.md to set up the environment"
```

**API Docs:** http://localhost:8000/docs
**Frontend:** http://localhost:5173
**Support:** https://github.com/lchtangen/SampleMind-AI---Beta/issues

---

**Updated:** October 9, 2025 | **Status:** 🟢 READY
