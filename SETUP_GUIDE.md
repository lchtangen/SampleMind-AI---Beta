# 🚀 SAMPLEMIND AI - COMPLETE SETUP GUIDE
## Get Your Development Environment Running in 10 Minutes

**Last Updated:** October 19, 2025  
**Target:** Local Development Environment  
**Prerequisites:** Docker, Python 3.11+, Node.js 18+

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 Minutes)](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## ✅ PREREQUISITES

### Required Software

```bash
# Check if you have the required versions
python --version  # Should be 3.11 or higher
node --version    # Should be 18 or higher
docker --version  # Any recent version
pnpm --version    # 8.0 or higher (npm install -g pnpm)
```

### Install Missing Tools

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install python@3.11
brew install node
brew install --cask docker
npm install -g pnpm
```

**Linux (Ubuntu/Debian):**
```bash
# Python
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# pnpm
npm install -g pnpm
```

---

## 🚀 QUICK START (5 Minutes)

### Step 1: Clone and Navigate
```bash
cd "/Users/lchtangen/Documents/SampleMind AI/SampleMind-AI---Beta"
```

### Step 2: Start Infrastructure Services
```bash
# Start PostgreSQL, Redis, MongoDB, Prometheus, Grafana
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Step 3: Backend Setup
```bash
# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.development .env

# Run database migrations (when ready)
# alembic upgrade head

# Start backend API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Frontend Setup (New Terminal)
```bash
# Navigate to frontend
cd apps/web

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### Step 5: Start Background Workers (New Terminal)
```bash
# Activate venv
source venv/bin/activate

# Start Celery worker
celery -A src.samplemind.core.tasks.celery_app worker --loglevel=info
```

### Step 6: Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Grafana:** http://localhost:3000 (admin/samplemind)
- **Prometheus:** http://localhost:9090

---

## 🔧 DETAILED SETUP

### 1. Environment Configuration

#### Backend Environment (.env)
```bash
# Already configured in .env.development
# Key settings:
DATABASE_URL="postgresql://samplemind:samplemind123@localhost:5432/samplemind"
REDIS_URL="redis://localhost:6379/0"
JWT_SECRET_KEY="dev-secret-key-change-in-production"
```

#### Frontend Environment (apps/web/.env.local)
```bash
# Already configured with working values
NEXT_PUBLIC_API_URL="http://localhost:8000"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### 2. Database Setup

#### Initialize PostgreSQL
```bash
# Database is auto-created by Docker Compose
# To manually create:
docker-compose exec postgres psql -U samplemind

# Inside psql:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### Run Migrations (When Backend API is Ready)
```bash
# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

#### Seed Sample Data (Optional)
```bash
python scripts/seed_database.py
```

### 3. Install AI Models (Optional)

#### For Local ML Models
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3.1:8b
ollama pull phi3:mini
```

#### Add API Keys for Cloud AI
Edit `.env` and add:
```bash
# Get free key at https://makersuite.google.com/app/apikey
GOOGLE_AI_API_KEY="your_key_here"

# Get key at https://platform.openai.com/api-keys
OPENAI_API_KEY="sk-..."

# Get key at https://console.anthropic.com/
ANTHROPIC_API_KEY="sk-ant-..."
```

---

## ⚙️ CONFIGURATION

### OAuth2 Setup (Optional)

#### Google OAuth
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Add redirect URI: `http://localhost:3000/auth/google/callback`
4. Copy Client ID and Secret to `.env`:
```bash
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-your-secret"
```

#### GitHub OAuth
1. Go to: https://github.com/settings/developers
2. New OAuth App
3. Callback URL: `http://localhost:3000/auth/github/callback`
4. Add to `.env`:
```bash
GITHUB_CLIENT_ID="Iv1.your-client-id"
GITHUB_CLIENT_SECRET="your-secret"
```

### Stripe Payment Setup (Optional)
1. Go to: https://dashboard.stripe.com/test/apikeys
2. Copy test keys to `.env`:
```bash
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_SECRET_KEY="sk_test_..."
```

---

## 🏃 RUNNING THE APPLICATION

### Development Mode (All Services)

**Terminal 1: Infrastructure**
```bash
docker-compose up -d
```

**Terminal 2: Backend API**
```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3: Celery Worker**
```bash
source venv/bin/activate
celery -A src.samplemind.core.tasks.celery_app worker --loglevel=info
```

**Terminal 4: Celery Beat (Scheduled Tasks)**
```bash
source venv/bin/activate
celery -A src.samplemind.core.tasks.celery_app beat --loglevel=info
```

**Terminal 5: Frontend**
```bash
cd apps/web
pnpm dev
```

### Production Mode

```bash
# Build frontend
cd apps/web
pnpm build

# Start production server
pnpm start

# Backend (with gunicorn)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🔍 VERIFICATION CHECKLIST

### Backend Health Checks
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Health endpoint: http://localhost:8000/api/v1/health
- [ ] Database connected (check logs)
- [ ] Redis connected (check logs)
- [ ] Celery worker running

### Frontend Health Checks
- [ ] App loads: http://localhost:3000
- [ ] No console errors
- [ ] Hot reload working
- [ ] API calls successful

### Services Health Checks
```bash
# Check all Docker containers
docker-compose ps

# Should see:
# - postgres (Up)
# - redis (Up)
# - mongodb (Up)
# - prometheus (Up)
# - grafana (Up)
```

---

## 🐛 TROUBLESHOOTING

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or change port in .env
API_PORT=8001
```

#### 2. Database Connection Failed
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U samplemind -c "SELECT 1"
```

#### 3. Redis Connection Failed
```bash
# Restart Redis
docker-compose restart redis

# Test connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

#### 4. Python Package Conflicts
```bash
# Remove venv and recreate
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Node Modules Issues
```bash
cd apps/web
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

#### 6. Celery Not Picking Up Tasks
```bash
# Restart Celery with fresh broker
celery -A src.samplemind.core.tasks.celery_app purge  # Clear queue
celery -A src.samplemind.core.tasks.celery_app worker --loglevel=debug
```

### Logs & Debugging

```bash
# Backend logs
tail -f logs/app.log

# Docker service logs
docker-compose logs -f postgres
docker-compose logs -f redis

# Celery logs
celery -A src.samplemind.core.tasks.celery_app inspect active
celery -A src.samplemind.core.tasks.celery_app inspect stats
```

---

## 📊 MONITORING

### Grafana Dashboards
1. Open: http://localhost:3000
2. Login: admin / samplemind
3. Navigate to: Dashboards > SampleMind AI

### Prometheus Metrics
1. Open: http://localhost:9090
2. Try queries:
   - `up` - Service health
   - `http_requests_total` - Request count
   - `process_cpu_seconds_total` - CPU usage

### Celery Flower (Optional)
```bash
pip install flower
celery -A src.samplemind.core.tasks.celery_app flower
# Access: http://localhost:5555
```

---

## 🧪 TESTING

### Run All Tests
```bash
# Backend tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/audio/test_audio_processor.py

# Frontend tests
cd apps/web
pnpm test
```

### Run Benchmarks
```bash
python benchmarks/audio_benchmark.py
python benchmarks/vector_store_benchmark.py
```

---

## 📚 NEXT STEPS

1. **Explore API Documentation**
   - Visit: http://localhost:8000/docs
   - Try out endpoints with Swagger UI

2. **Upload Your First Audio File**
   - Use the web interface at http://localhost:3000
   - Or use API: `POST /api/v1/audio/upload`

3. **Configure AI Models**
   - Add API keys for Gemini, OpenAI, or Claude
   - Or run local models with Ollama

4. **Customize the UI**
   - Edit theme in `apps/web/tailwind.config.ts`
   - Modify components in `apps/web/components/`

5. **Read the Documentation**
   - API Guide: `docs/api/README.md`
   - Developer Guide: `docs/developer_guide/README.md`
   - Architecture: `ARCHITECTURE.md`

---

## 💬 GETTING HELP

- **Issues:** Check `TROUBLESHOOTING.md`
- **Documentation:** Browse `/docs` folder
- **Community:** Join Discord (link in README)
- **Email:** support@samplemind.ai

---

## 🎉 SUCCESS!

If you've made it this far, your development environment should be fully operational!

**Quick Test:**
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status": "healthy"}
```

**Ready to build!** 🚀

---

**Last Updated:** October 19, 2025  
**Maintainer:** Lars Christian Tangen  
**Version:** 2.0.0-beta
