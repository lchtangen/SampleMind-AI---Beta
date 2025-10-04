# 🚀 Getting Started with SampleMind AI v6

## Welcome! 👋

This guide will walk you through **everything** you need to know to get SampleMind AI v6 up and running on your Ubuntu system. No prior knowledge assumed!

---

## 📋 Table of Contents

1. [Prerequisites & Installation](#prerequisites--installation)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Understanding the Project](#understanding-the-project)
4. [Running the Application](#running-the-application)
5. [Testing the Application](#testing-the-application)
6. [Common Commands Reference](#common-commands-reference)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

---

## Prerequisites & Installation

### Step 1: Check What You Have

Run these commands to check your system:

```bash
# Check Python version (need 3.12+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Check Docker
docker --version

# Check Docker Compose
docker-compose --version

# Check Git
git --version
```

### Step 2: Install Missing Software

#### Install Python 3.12 (if needed)
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

#### Install Node.js 18+ (if needed)
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### Install Docker & Docker Compose (if needed)
```bash
# Docker
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # Add yourself to docker group

# Docker Compose
sudo apt install docker-compose

# Log out and back in for group changes to take effect
```

#### Verify Installations
```bash
python3 --version    # Should show 3.12+
node --version       # Should show v18+
npm --version        # Should show 9+
docker --version     # Should show 20+
docker-compose --version  # Should show 1.29+
```

---

## Quick Start (5 minutes)

### Step 1: Initial Setup

```bash
# You're already in the project directory!
cd ~/Projects/samplemind-ai-v6

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt now
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt

# Install Node.js dependencies
cd frontend/web
npm install
cd ../..
```

### Step 3: Load Handy Shortcuts

```bash
# Load command aliases (makes life easier!)
source .aliases

# Now you can use shortcuts like:
# sm-info    - Show project info
# sm-help    - Show all available commands
# sm-status  - Show what's running
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit the file (use nano, vim, or your favorite editor)
nano .env

# Minimum required changes:
# - Set JWT_SECRET_KEY to a random string (example: "your-super-secret-key-change-this")
# - Set GEMINI_API_KEY if you have one (optional for basic testing)
# - Set OPENAI_API_KEY if you have one (optional for basic testing)

# Press Ctrl+X, then Y, then Enter to save in nano
```

### Step 5: Start Database Services

```bash
# Start MongoDB, Redis, and ChromaDB in the background
docker-compose up -d mongodb redis chromadb

# Check they're running
docker-compose ps

# You should see 3 containers running
```

### Step 6: Verify Setup

```bash
# Run the project info command
sm-info

# This will show you:
# - What's installed
# - What's running
# - What's configured
```

🎉 **Setup Complete!** Now let's run the application.

---

## Understanding the Project

### What is SampleMind AI v6?

SampleMind AI is an AI-powered music production tool that:
- **Analyzes** audio files (BPM, key, scale, mood, etc.)
- **Processes** them in the background using Celery
- **Uses AI** (Google Gemini + OpenAI) for intelligent insights
- **Provides** a web interface to manage everything

### Project Structure (The Important Parts)

```
samplemind-ai-v6/
├── src/samplemind/          # Backend Python code
│   ├── interfaces/api/      # API endpoints (FastAPI)
│   ├── core/engine/         # Audio processing
│   ├── core/tasks/          # Background tasks (Celery)
│   └── core/database/       # Database operations
├── frontend/web/            # Frontend Next.js app
│   ├── app/                 # Pages (login, dashboard, etc.)
│   └── components/          # Reusable UI components
├── tests/                   # All tests
├── data/                    # Data storage (created automatically)
│   ├── uploads/             # Uploaded audio files
│   ├── analysis/            # Analysis results
│   └── cache/               # Cached data
├── .env                     # Your configuration
├── .aliases                 # Command shortcuts
└── requirements.txt         # Python dependencies
```

### The 5 Main Services

1. **Backend API** (FastAPI) - Port 8000
   - Handles HTTP requests
   - Manages authentication
   - Processes file uploads

2. **Frontend** (Next.js) - Port 3000
   - User interface
   - Web dashboard
   - File upload interface

3. **Celery Worker** - Background
   - Processes audio files
   - Runs AI analysis
   - Handles long tasks

4. **Database (MongoDB)** - Port 27017
   - Stores users, files, analyses
   
5. **Cache (Redis)** - Port 6379
   - Speeds up requests
   - Manages sessions
   - Celery task queue

---

## Running the Application

### Option A: Development Mode (Recommended for Learning)

Run each service in a **separate terminal** so you can see what's happening:

#### Terminal 1: Backend API
```bash
cd ~/Projects/samplemind-ai-v6
source venv/bin/activate
source .aliases

# Start the backend API
sm-api

# Or manually:
# uvicorn src.samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# Open http://localhost:8000/docs in your browser to see the API documentation
```

#### Terminal 2: Celery Worker
```bash
cd ~/Projects/samplemind-ai-v6
source venv/bin/activate
source .aliases

# Start the Celery worker
sm-worker

# Or manually:
# celery -A src.samplemind.core.tasks.celery_app worker --loglevel=info

# You should see:
# [tasks]
#   . src.samplemind.core.tasks.audio_tasks.process_audio_analysis
#   . src.samplemind.core.tasks.audio_tasks.batch_process_audio_files
```

#### Terminal 3: Frontend
```bash
cd ~/Projects/samplemind-ai-v6
source .aliases

# Start the frontend
sm-web

# Or manually:
# cd frontend/web && npm run dev

# You should see:
# ▲ Next.js 14.x.x
# - Local:        http://localhost:3000
```

#### Terminal 4: Celery Beat (Optional - for periodic tasks)
```bash
cd ~/Projects/samplemind-ai-v6
source venv/bin/activate

# Start Celery Beat for scheduled tasks
celery -A src.samplemind.core.tasks.celery_app beat --loglevel=info
```

#### Terminal 5: Flower (Optional - for monitoring)
```bash
cd ~/Projects/samplemind-ai-v6
source venv/bin/activate
source .aliases

# Start Flower for monitoring Celery
sm-flower

# Open http://localhost:5555 in your browser
```

### Option B: Quick Start (All Services)

Use the start-all script:

```bash
cd ~/Projects/samplemind-ai-v6
source venv/bin/activate
source .aliases

# Start everything
sm-start

# Stop everything
sm-stop
```

### Option C: Production Mode (Docker)

```bash
# Start all services in Docker
docker-compose -f deployment/docker/docker-compose.prod.yml up -d

# Check status
docker-compose -f deployment/docker/docker-compose.prod.yml ps

# View logs
docker-compose -f deployment/docker/docker-compose.prod.yml logs -f

# Stop everything
docker-compose -f deployment/docker/docker-compose.prod.yml down
```

### Verify Everything is Running

```bash
# Check running services
sm-status

# Or manually check:
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy"}

# Check frontend
curl http://localhost:3000
# Should return HTML
```

### Access the Application

Open your browser and go to:

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **API Alternative Docs**: http://localhost:8000/redoc
- **Flower Dashboard**: http://localhost:5555 (if running)

---

## Testing the Application

### Step 1: Run Quick Health Check

```bash
# Make sure you're in the project directory
cd ~/Projects/samplemind-ai-v6
source venv/bin/activate

# Run quick smoke tests
sm-test-quick

# This runs the fastest tests to verify basic functionality
```

### Step 2: Run Full Test Suite

```bash
# Make sure databases are running
docker-compose ps

# If not running, start them:
docker-compose up -d mongodb redis chromadb

# Run all tests
./run_tests.sh all

# This will:
# 1. Run unit tests (~5 seconds)
# 2. Run integration tests (~15 seconds)
# 3. Generate coverage report
# 4. Create HTML reports in test_reports/
```

### Step 3: Run Specific Test Types

```bash
# Unit tests only (fast)
./run_tests.sh unit

# Integration tests only
./run_tests.sh integration

# E2E tests (requires frontend running)
./run_tests.sh e2e

# Load tests (opens web UI)
./run_tests.sh load
```

### Step 4: View Test Reports

```bash
# Open the latest test report
cd test_reports
ls -lt  # Shows files sorted by date, newest first

# Open HTML report in browser
firefox unit_*.html  # or use 'google-chrome' or 'chromium-browser'

# Or view coverage report
firefox coverage_*/index.html
```

### Understanding Test Results

```bash
# After running tests, you'll see output like:

========================= test session starts ==========================
collected 48 items

tests/unit/test_auth.py::test_hash_password PASSED           [  2%]
tests/unit/test_auth.py::test_verify_password PASSED         [  4%]
...

========================= 48 passed in 5.23s ===========================

----------- coverage: platform linux, python 3.12.x -----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/samplemind/core/auth/jwt_handler.py   45      2    96%
src/samplemind/core/auth/password.py      12      0   100%
...
-----------------------------------------------------------
TOTAL                                    1250    156    88%
```

**What this means**:
- ✅ **48 passed** = All 48 tests passed successfully
- ✅ **88% coverage** = 88% of code is tested (goal is 80%+)
- ⚠️ **2 missed** = 2 lines in jwt_handler.py not covered by tests (acceptable)

---

## Common Commands Reference

### Daily Development Commands

```bash
# Load shortcuts (do this in each new terminal)
source .aliases

# Project Information
sm-info          # Show comprehensive project info
sm-help          # Show all available commands
sm-status        # Check what's running
sm-health        # Check service health

# Starting Services
sm-api           # Start backend API
sm-worker        # Start Celery worker
sm-web           # Start frontend
sm-flower        # Start Flower monitoring
sm-start         # Start all services
sm-stop          # Stop all services

# Database
sm-db-up         # Start databases (MongoDB, Redis, ChromaDB)
sm-db-down       # Stop databases
sm-mongo         # Connect to MongoDB shell
sm-redis         # Connect to Redis CLI

# Testing
sm-test          # Run all tests
sm-test-quick    # Run quick tests only
sm-test-cov      # Run with coverage report

# Code Quality
sm-lint          # Run linters (Black, isort, flake8)
sm-format        # Format code

# Logs
sm-logs          # View all logs
sm-logs-api      # View API logs
sm-logs-worker   # View worker logs

# Navigation
sm               # Go to project root
smb              # Go to backend source
smf              # Go to frontend
smapi            # Go to API code
smcore           # Go to core code
```

### Manual Commands (Without Aliases)

#### Backend
```bash
# Start API
cd ~/Projects/samplemind-ai-v6
source venv/bin/activate
uvicorn src.samplemind.interfaces.api.main:app --reload

# Start Celery worker
celery -A src.samplemind.core.tasks.celery_app worker --loglevel=info

# Start Celery beat
celery -A src.samplemind.core.tasks.celery_app beat --loglevel=info
```

#### Frontend
```bash
# Development
cd ~/Projects/samplemind-ai-v6/frontend/web
npm run dev

# Production build
npm run build
npm start
```

#### Testing
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_auth.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific marker
pytest -m unit  # Only unit tests
pytest -m "not slow"  # Skip slow tests
```

#### Database
```bash
# Start services
docker-compose up -d mongodb redis chromadb

# Stop services
docker-compose down

# View logs
docker-compose logs -f mongodb
docker-compose logs -f redis

# MongoDB shell
docker exec -it samplemind-mongodb mongosh

# Redis CLI
docker exec -it samplemind-redis redis-cli
```

---

## Troubleshooting

### Problem: "Command not found" errors

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# You should see (venv) in your prompt

# Make sure you're in the right directory
pwd  # Should show: /home/lchta/Projects/samplemind-ai-v6
```

### Problem: Import errors when running Python

**Solution**:
```bash
# Install the package in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/lchta/Projects/samplemind-ai-v6"
```

### Problem: Docker containers not starting

**Solution**:
```bash
# Check if Docker is running
sudo systemctl status docker

# Start Docker if needed
sudo systemctl start docker

# Check for port conflicts
sudo netstat -tlnp | grep -E '8000|3000|27017|6379'

# If ports are in use, stop conflicting services or change ports in .env
```

### Problem: Tests failing with database errors

**Solution**:
```bash
# Make sure databases are running
docker-compose ps

# Restart databases
docker-compose restart mongodb redis

# Check logs
docker-compose logs mongodb
docker-compose logs redis
```

### Problem: Frontend not connecting to backend

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check frontend .env.local
cat frontend/web/.env.local
# Should have: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# If missing, create it:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > frontend/web/.env.local

# Restart frontend
```

### Problem: Celery worker not picking up tasks

**Solution**:
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
redis-cli -h localhost -p 6379 ping
# Should return: PONG

# Check Celery worker logs
# Look for "ready" message and registered tasks

# Restart worker
sm-worker
```

### Problem: "Permission denied" for Docker

**Solution**:
```bash
# Add yourself to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Test
docker ps
```

### Problem: Module not found errors

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# For frontend
cd frontend/web
rm -rf node_modules package-lock.json
npm install
```

### Problem: Port already in use

**Solution**:
```bash
# Find what's using the port (example: port 8000)
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or change the port in .env:
API_PORT=8001
```

---

## Next Steps

### 1. Learn the Workflow

Follow the **[USER_GUIDE.md](USER_GUIDE.md)** to learn:
- How to register and login
- How to upload audio files
- How to analyze audio
- How to view results

### 2. Understand the Architecture

Read **[ARCHITECTURE.md](ARCHITECTURE.md)** to understand:
- How the backend works
- How the frontend works
- How data flows through the system
- How services communicate

### 3. Explore the Code

Read **[DEVELOPMENT.md](DEVELOPMENT.md)** to learn:
- Code structure and organization
- How to add new features
- Coding standards and best practices
- How to contribute

### 4. Deploy to Production

Read **[DEPLOYMENT.md](DEPLOYMENT.md)** to learn:
- How to deploy with Docker
- How to deploy to Kubernetes
- How to set up CI/CD
- How to configure domains and SSL

### 5. Advanced Topics

- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[TESTING.md](TESTING.md)** - Testing guidelines
- **[SECURITY.md](SECURITY.md)** - Security best practices
- **[PERFORMANCE.md](PERFORMANCE.md)** - Performance optimization

---

## Quick Reference Card

### One-Line Setup
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && docker-compose up -d mongodb redis chromadb && source .aliases
```

### Start Everything
```bash
# Terminal 1
sm-api

# Terminal 2  
sm-worker

# Terminal 3
sm-web
```

### Test Everything
```bash
./run_tests.sh all
```

### Access URLs
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Flower: http://localhost:5555

---

## Getting Help

### Documentation
- **This guide**: Start here for setup
- **USER_GUIDE.md**: How to use the application
- **DEVELOPMENT.md**: How to develop features
- **API_REFERENCE.md**: API documentation
- **TROUBLESHOOTING.md**: Common issues and solutions

### Commands
```bash
sm-help       # Show all available commands
sm-info       # Show project information
sm-status     # Check what's running
sm-health     # Health check all services
```

### Community
- GitHub Issues: Report bugs or ask questions
- Documentation: Read the docs in `documentation/`
- Examples: Check `examples/` directory

---

## Checklist: First Time Setup

- [ ] Python 3.12+ installed and verified
- [ ] Node.js 18+ installed and verified
- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] Project cloned or in correct directory
- [ ] Virtual environment created and activated
- [ ] Python dependencies installed
- [ ] Node.js dependencies installed
- [ ] `.env` file created and configured
- [ ] Aliases loaded (`. .aliases`)
- [ ] Databases started (`sm-db-up`)
- [ ] Backend running (`sm-api`)
- [ ] Worker running (`sm-worker`)
- [ ] Frontend running (`sm-web`)
- [ ] Health check passed (`sm-health`)
- [ ] Tests passed (`sm-test-quick`)
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/docs

---

🎉 **Congratulations!** You're now ready to use SampleMind AI v6!

**Next**: Read [USER_GUIDE.md](USER_GUIDE.md) to learn how to use the application.

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or the documentation in `documentation/`.

**Happy Music Production!** 🎵🎹🎸
