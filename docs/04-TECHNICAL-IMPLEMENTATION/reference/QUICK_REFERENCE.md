# ⚡ SampleMind AI - Quick Reference Guide

**Version:** 1.0 Beta | **Last Updated:** 2025-10-04  
**Difficulty:** 🟢 Beginner-Friendly | **Time to Read:** 5 minutes

```
┌─────────────────────────────────────────────────────────────┐
│  🎵 Your One-Page Cheat Sheet for Everything SampleMind!   │
│  Copy-paste ready commands for instant productivity 🚀      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **FASTEST START** (Copy-Paste These!)

```bash
# ⚡ INSTANT STARTUP (3 commands)
./quick_start.sh              # Start everything
open http://localhost:3000     # Open app in browser
# That's it! You're running! 🎉
```

**What just happened?**
```
Starting... ▓▓▓▓▓▓▓▓▓▓ 100%
  ✅ MongoDB   - Running on port 27017
  ✅ Redis     - Running on port 6379  
  ✅ ChromaDB  - Running on port 8001
  ✅ Backend   - Running on port 8000
  ✅ Frontend  - Running on port 3000

🎵 SampleMind AI is ready!
```

---

## 📑 Table of Contents

**Quick Navigation** (Click to jump)

| Category | What's Inside | When to Use |
|----------|---------------|-------------|
| [⚡ Quick Start](#-quick-start-commands) | Start/stop commands | Every day |
| [💻 Development](#-development-commands) | Dev server commands | While coding |
| [🐳 Docker](#-docker-commands) | Container management | Troubleshooting |
| [🧪 Testing](#-testing-commands) | Run tests | Before commit |
| [🗄️ Database](#-database-commands) | DB operations | Data management |
| [🌐 API](#-api-endpoints) | Endpoint reference | API integration |
| [⌨️ Shortcuts](#-keyboard-shortcuts) | Keyboard shortcuts | Speed boost |
| [🚨 Status Codes](#-status-codes) | HTTP error codes | Debugging |
| [📁 File Support](#-file-format-support) | Audio formats | File uploads |
| [🔐 Environment](#-environment-variables) | Config variables | Setup |
| [💡 Pro Tips](#-pro-tips) | Expert shortcuts | Level up |

---

## 🚀 Quick Start Commands

### Application Control

```
┌────────────────────────────────────────────────────────────┐
│          🎮 MASTER CONTROL COMMANDS                       │
├────────────────────────────────────────────────────────────┤
│  Command                    What It Does           Time   │
├────────────────────────────────────────────────────────────┤
│  ./quick_start.sh           🚀 Start everything     2-3 min│
│  ./quick_start.sh stop      ⏸️  Stop all services     10 sec │
│  ./quick_start.sh restart   🔄 Restart everything    1 min  │
│  ./quick_start.sh status    📡 Check what's running  1 sec  │
└────────────────────────────────────────────────────────────┘
```

**Visual Flow:**
```
./quick_start.sh
     │
     ├─▶ Starting Docker containers...
     │      └─ MongoDB   [############] ✅
     │      └─ Redis     [############] ✅
     │      └─ ChromaDB  [############] ✅
     │
     ├─▶ Starting Backend API...
     │      └─ Uvicorn   [############] ✅ Port 8000
     │
     ├─▶ Starting Frontend...
     │      └─ Next.js   [############] ✅ Port 3000
     │
     └─▶ ✨ All systems operational!
```

### 🛠️ Setup & Configuration

**First-Time Setup Flow:**
```
┌────────────────────────────────────────────────────────┐
│         🎯 ONE-TIME SETUP (5 minutes)                  │
├────────────────────────────────────────────────────────┤
│  Step 1: Create environment file (10 seconds)           │
│    $ cp .env.example .env                               │
│    $ nano .env  # Add your API keys                     │
│    ✅ Done!                                             │
├────────────────────────────────────────────────────────┤
│  Step 2: Python setup (1 minute)                        │
│    $ python -m venv .venv                               │
│    $ source .venv/bin/activate  # Windows: .venv\Scripts\activate
│    $ pip install -r requirements.txt                    │
│    ✅ Python ready!                                     │
├────────────────────────────────────────────────────────┤
│  Step 3: Frontend setup (2 minutes)                     │
│    $ cd frontend/web                                    │
│    $ npm install                                        │
│    $ cd ../..  # Back to root                           │
│    ✅ Frontend ready!                                  │
├────────────────────────────────────────────────────────┤
│  Step 4: Start everything!                             │
│    $ ./quick_start.sh                                   │
│    🎉 You're ready to go!                              │
└────────────────────────────────────────────────────────┘
```

**Quick Commands Table:**

| Step | Command | What It Does | Time |
|------|---------|--------------|------|
| 1️⃣ | `cp .env.example .env` | Copy environment template | 1s |
| 2️⃣ | `python -m venv .venv` | Create Python virtual environment | 10s |
| 3️⃣ | `source .venv/bin/activate` | Activate venv (or `.venv\Scripts\activate` on Windows) | 1s |
| 4️⃣ | `pip install -r requirements.txt` | Install all Python packages | 2min |
| 5️⃣ | `cd frontend/web && npm install` | Install all Node.js packages | 2min |

---

## 💻 Development Commands

### Backend (FastAPI)

```bash
# Start backend server (development mode)
cd src
uvicorn samplemind.main:app --reload --host 0.0.0.0 --port 8000

# With logging
uvicorn samplemind.main:app --reload --log-level debug

# Production mode
gunicorn samplemind.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**URLs:**
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend (Next.js)

```bash
# Development server
cd frontend/web
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

**URLs:**
- App: `http://localhost:3000`
- Dev Server: Hot reload enabled

### Celery (Background Tasks)

```bash
# Start Celery worker
celery -A samplemind.celery_app worker --loglevel=info

# With beat scheduler
celery -A samplemind.celery_app worker -B --loglevel=info

# Flower (monitoring UI)
celery -A samplemind.celery_app flower --port=5555
```

**URL:** Flower UI at `http://localhost:5555`

---

## 🐳 Docker Commands

### Basic Operations

| Command | Description |
|---------|-------------|
| `docker-compose up` | Start all services |
| `docker-compose up -d` | Start in detached mode |
| `docker-compose down` | Stop and remove containers |
| `docker-compose ps` | List running containers |
| `docker-compose logs` | View logs |
| `docker-compose logs -f api` | Follow logs for specific service |

### Build & Rebuild

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build api

# Force rebuild (no cache)
docker-compose build --no-cache

# Pull latest images
docker-compose pull
```

### Service Management

```bash
# Restart specific service
docker-compose restart api

# Stop specific service
docker-compose stop redis

# Scale workers
docker-compose up -d --scale worker=3

# Execute command in container
docker-compose exec api bash
docker-compose exec db psql -U samplemind
```

### Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove volumes (⚠️ deletes data!)
docker-compose down -v

# Clean everything
docker system prune -a
```

---

## 🧪 Testing Commands

**Testing Pyramid** (Run in order):
```
                  /\
                 /  \       🐌 E2E Tests (2-3 min)
                /____\      Slowest, most comprehensive
               /      \
              /        \    🔗 Integration Tests (1-2 min)
             /__________\   Medium speed, API tests
            /            \
           /              \  ⚡ Unit Tests (30 sec)
          /________________\ Fastest, most focused

  Strategy: Run unit tests often, E2E before deploy!
```

### 🎯 Run Tests

```
┌──────────────────────────────────────────────────────────┐
│           🚦 TEST SUITE - CHOOSE YOUR SPEED                │
├──────────────────────────────────────────────────────────┤
│  Command                  Speed    When to Use                │
├──────────────────────────────────────────────────────────┤
│  ./run_tests.sh quick    ⚡⚡⚡   While coding              │
│                          30 sec  (every save)              │
├──────────────────────────────────────────────────────────┤
│  ./run_tests.sh unit      ⚡⚡    Before commit             │
│                          30 sec  (git pre-commit hook)     │
├──────────────────────────────────────────────────────────┤
│  ./run_tests.sh integration 🐌   Before push/PR            │
│                          1-2 min (verify API changes)      │
├──────────────────────────────────────────────────────────┤
│  ./run_tests.sh e2e       🐢   Before deploy             │
│                          2-3 min (full user workflows)     │
├──────────────────────────────────────────────────────────┤
│  ./run_tests.sh all       🐌🐢🐌 Every Friday/Sprint end   │
│                          2-5 min (complete coverage check) │
└──────────────────────────────────────────────────────────┘
```

### Pytest Options

```bash
# Run specific test file
pytest tests/unit/test_auth.py

# Run specific test function
pytest tests/unit/test_auth.py::test_password_hashing

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src/samplemind --cov-report=html

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Run tests matching pattern
pytest -k "test_auth"
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src/samplemind --cov-report=html

# View report
open test_reports/coverage/index.html  # macOS
xdg-open test_reports/coverage/index.html  # Linux

# Terminal coverage
pytest --cov=src/samplemind --cov-report=term
```

---

## 🗄️ Database Commands

### MongoDB

```bash
# Connect to MongoDB shell
docker-compose exec mongodb mongosh

# Show databases
show dbs

# Use database
use samplemind

# Show collections
show collections

# Query examples
db.audio_files.find()
db.users.countDocuments()
db.analysis_results.find({status: "completed"}).limit(10)

# Backup database
mongodump --host localhost --port 27017 --db samplemind --out ./backup

# Restore database
mongorestore --host localhost --port 27017 --db samplemind ./backup/samplemind
```

### Redis

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Common commands
PING                    # Test connection
KEYS *                  # List all keys (⚠️ don't use in production)
GET key_name            # Get value
SET key_name value      # Set value
DEL key_name            # Delete key
FLUSHALL                # Clear all data (⚠️ dangerous!)
INFO                    # Server information
```

### ChromaDB

```bash
# Check ChromaDB status
curl http://localhost:8001/api/v1/heartbeat

# List collections
curl http://localhost:8001/api/v1/collections

# Collection info
curl http://localhost:8001/api/v1/collections/audio_embeddings
```

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Create account | No |
| POST | `/api/v1/auth/login` | Log in | No |
| POST | `/api/v1/auth/refresh` | Refresh token | Yes |
| POST | `/api/v1/auth/logout` | Log out | Yes |
| GET | `/api/v1/auth/me` | Get current user | Yes |
| PUT | `/api/v1/auth/password` | Change password | Yes |

### Audio Files

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/audio/upload` | Upload file | Yes |
| GET | `/api/v1/audio` | List all files | Yes |
| GET | `/api/v1/audio/{id}` | Get file details | Yes |
| DELETE | `/api/v1/audio/{id}` | Delete file | Yes |
| GET | `/api/v1/audio/{id}/download` | Download file | Yes |
| PUT | `/api/v1/audio/{id}/tags` | Update tags | Yes |

### Analysis

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/analysis/analyze/{file_id}` | Start analysis | Yes |
| GET | `/api/v1/analysis/{id}` | Get analysis result | Yes |
| GET | `/api/v1/analysis/audio/{file_id}` | Get all analyses for file | Yes |
| DELETE | `/api/v1/analysis/{id}` | Delete analysis | Yes |

### System

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| GET | `/api/v1/system/status` | System status | Yes |
| GET | `/api/v1/system/stats` | Statistics | Yes |

---

## ⌨️ Keyboard Shortcuts

### Web Application

| Shortcut | Action | Page |
|----------|--------|------|
| `Ctrl/Cmd + K` | Focus search | Library |
| `Ctrl/Cmd + U` | Upload file | Any |
| `Esc` | Close modal | Any |
| `Ctrl/Cmd + A` | Select all files | Library |
| `Delete` | Delete selected | Library |

### Terminal

| Shortcut | Action |
|----------|--------|
| `Ctrl + C` | Stop running process |
| `Ctrl + Z` | Suspend process |
| `Ctrl + D` | Exit shell |
| `Ctrl + L` | Clear screen |
| `Ctrl + R` | Search command history |

---

## 📊 Status Codes

### HTTP Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 204 | No Content | Success, no response body |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server down |

### Analysis Status

| Status | Icon | Meaning |
|--------|------|---------|
| `pending` | ⏳ | Waiting in queue |
| `processing` | ⚙️ | Currently analyzing |
| `completed` | ✅ | Analysis done |
| `failed` | ❌ | Error occurred |

---

## 📁 File Format Support

### Audio Formats

| Format | Extension | Supported | Recommended | Max Size |
|--------|-----------|-----------|-------------|----------|
| WAV | `.wav` | ✅ | ⭐⭐⭐ | 50 MB |
| FLAC | `.flac` | ✅ | ⭐⭐⭐ | 50 MB |
| MP3 | `.mp3` | ✅ | ⭐⭐ | 50 MB |
| M4A | `.m4a` | ✅ | ⭐⭐ | 50 MB |
| AAC | `.aac` | ✅ | ⭐ | 50 MB |
| OGG | `.ogg` | ✅ | ⭐ | 50 MB |

**Recommendations:**
- **Best Quality:** WAV or FLAC
- **Good Balance:** MP3 320kbps
- **Space Saving:** MP3 256kbps or M4A

### Sample Rates

| Rate | Quality | Use Case |
|------|---------|----------|
| 44.1 kHz | CD Quality | Standard |
| 48 kHz | Professional | Video/Broadcasting |
| 96 kHz | High-Res | Mastering |
| 192 kHz | Ultra High-Res | Archival |

---

## 🔧 Environment Variables

### Required Variables

```bash
# Application
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=samplemind

# Redis
REDIS_URL=redis://localhost:6379/0

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8001

# AI Services
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Storage
STORAGE_PATH=./storage
MAX_FILE_SIZE=52428800  # 50 MB in bytes

# Security
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Optional Variables

```bash
# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@samplemind.ai

# Monitoring
SENTRY_DSN=https://...
LOG_LEVEL=INFO

# Performance
CELERY_WORKERS=4
API_WORKERS=4
```

---

## 🎯 Common Workflows Cheat Sheet

### 1. Fresh Install

```bash
# Clone and setup
git clone <repo-url>
cd samplemind-ai-v6
cp .env.example .env
./quick_start.sh
```

### 2. Daily Development

```bash
# Start services
./quick_start.sh

# Run tests before committing
./run_tests.sh quick

# Check logs
docker-compose logs -f api
```

### 3. Database Reset

```bash
# ⚠️ This deletes all data!
docker-compose down -v
docker-compose up -d
```

### 4. Update Dependencies

```bash
# Python
pip install -U -r requirements.txt

# Node.js
cd frontend/web && npm update
```

### 5. Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
kubectl apply -f deployment/k8s/

# Check status
kubectl get pods -n samplemind
```

---

## 🔍 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Port already in use | `lsof -ti:8000 \| xargs kill` |
| Docker out of space | `docker system prune -a` |
| Dependencies conflict | Delete `.venv` and reinstall |
| Database connection error | `docker-compose restart mongodb` |
| Tests failing | Run `./run_tests.sh quick` for details |
| Frontend won't start | `cd frontend/web && rm -rf .next node_modules && npm install` |

---

## 📚 Quick Links

| Resource | URL |
|----------|-----|
| User Guide | [USER_GUIDE.md](./USER_GUIDE.md) |
| Troubleshooting | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) |
| Architecture | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| API Reference | [API_REFERENCE.md](./API_REFERENCE.md) |
| Getting Started | [GETTING_STARTED.md](./GETTING_STARTED.md) |
| Project Summary | [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) |

---

## 💡 Pro Tips

1. **Alias Common Commands** - Add to `.zshrc`:
   ```bash
   alias sm-start='cd ~/samplemind && ./quick_start.sh'
   alias sm-test='./run_tests.sh quick'
   alias sm-logs='docker-compose logs -f'
   ```

2. **Watch Mode for Tests**:
   ```bash
   pytest-watch tests/unit/
   ```

3. **Quick Debug**:
   ```bash
   # Python
   python -m pdb script.py
   
   # Node.js
   node --inspect index.js
   ```

4. **Git Hooks** - Auto-run tests:
   ```bash
   # .git/hooks/pre-commit
   #!/bin/bash
   ./run_tests.sh quick
   ```

---

**Last Updated:** 2025-10-04 | **Version:** 1.0 Beta

**Need more help?** Check the [full documentation](./DOCUMENTATION_INDEX.md)
