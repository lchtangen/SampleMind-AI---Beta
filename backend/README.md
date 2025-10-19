# 🎵 SampleMind AI Backend

FastAPI-powered backend for the revolutionary AI music production platform.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Development Server

```bash
python main.py
```

**Or with uvicorn directly:**
```bash
uvicorn main:app --reload --port 8000
```

### 3. Access API

- **API Root:** http://localhost:8000
- **Health Check:** http://localhost:8000/health
- **API Docs (Swagger):** http://localhost:8000/api/docs
- **API Docs (ReDoc):** http://localhost:8000/api/redoc

---

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── __init__.py
│   ├── api/                # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py     # Authentication endpoints (TODO)
│   │       └── audio.py    # Audio endpoints (TODO)
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration settings ✅
│   │   └── security.py     # JWT & password utils (TODO)
│   ├── models/             # Database models (TODO)
│   │   └── __init__.py
│   └── schemas/            # Pydantic schemas (TODO)
│       └── __init__.py
└── README.md              # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=SampleMind AI

# Database
DATABASE_URL=postgresql://samplemind:samplemind123@localhost:5432/samplemind

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI APIs
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# File Upload
MAX_UPLOAD_SIZE=104857600  # 100MB
```

### Settings

Edit `app/core/config.py` to modify default settings.

---

## 🎯 Current Status

### ✅ Completed
- FastAPI application bootstrap
- Basic routing structure
- CORS middleware
- Health check endpoint
- Configuration management
- Requirements file

### 🔄 In Progress (Phase 7 Tasks)
- [ ] **T01:** API contract definition & OpenAPI spec
- [ ] **T02:** Auth flow UI (JWT, refresh tokens)
- [ ] **T03:** Error boundary system
- [ ] **T04:** Loading states & Suspense
- [ ] **T05:** Optimistic UI patterns
- [ ] **T06:** WebSocket integration
- [ ] **T07:** Rate limiting UX
- [ ] **T08:** API health indicator
- [ ] **T09:** Feature flags
- [ ] **T10:** API mocks/stubs

### 📋 TODO (Next Steps)
1. **Auth Endpoints** (`app/api/v1/auth.py`)
   - POST /api/v1/auth/register
   - POST /api/v1/auth/login
   - POST /api/v1/auth/refresh
   - POST /api/v1/auth/logout

2. **Audio Endpoints** (`app/api/v1/audio.py`)
   - POST /api/v1/audio/upload
   - POST /api/v1/audio/analyze
   - GET /api/v1/audio/{id}
   - DELETE /api/v1/audio/{id}

3. **Database Setup**
   - SQLAlchemy models
   - Alembic migrations
   - PostgreSQL connection

4. **Celery Tasks**
   - Audio processing queue
   - Feature extraction
   - AI analysis

5. **WebSocket**
   - Real-time processing status
   - Upload progress
   - Live updates

---

## 🔗 Integration with Frontend

The frontend (Next.js at `apps/web/`) will connect to this backend:

```typescript
// Example API client
const API_BASE_URL = "http://localhost:8000";

const uploadAudio = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/v1/audio/upload`, {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.json();
};
```

---

## 📊 API Endpoints (Planned)

### Authentication
- `POST /api/v1/auth/register` — Register new user
- `POST /api/v1/auth/login` — Login & get JWT
- `POST /api/v1/auth/refresh` — Refresh access token
- `POST /api/v1/auth/logout` — Logout & invalidate token

### Audio
- `POST /api/v1/audio/upload` — Upload audio file
- `POST /api/v1/audio/analyze` — Analyze audio with AI
- `GET /api/v1/audio` — List user's audio files
- `GET /api/v1/audio/{id}` — Get audio file details
- `DELETE /api/v1/audio/{id}` — Delete audio file
- `PATCH /api/v1/audio/{id}` — Update metadata

### Search
- `GET /api/v1/search` — Text search
- `POST /api/v1/search/semantic` — Vector search
- `POST /api/v1/search/similar/{id}` — Find similar samples

### Analysis
- `GET /api/v1/analysis/{id}` — Get analysis results
- `POST /api/v1/analysis/batch` — Batch analysis

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

---

## 🐳 Docker

```bash
# Build image
docker build -t samplemind-api .

# Run container
docker run -p 8000:8000 samplemind-api
```

---

## 📚 Dependencies

### Core
- **FastAPI** 0.104.1 — Modern async web framework
- **Uvicorn** 0.24.0 — ASGI server
- **Pydantic** 2.5.0 — Data validation

### Database
- **SQLAlchemy** 2.0.23 — ORM
- **Alembic** 1.13.0 — Migrations
- **AsyncPG** 0.29.0 — PostgreSQL async driver

### Auth
- **python-jose** 3.3.0 — JWT handling
- **passlib** 1.7.4 — Password hashing

### AI Integration
- **openai** 1.3.7 — OpenAI GPT-4o
- **anthropic** 0.7.7 — Claude 3.5 Sonnet
- **google-generativeai** 0.3.1 — Gemini 2.5 Pro

### Audio
- **librosa** 0.10.1 — Audio analysis
- **soundfile** 0.12.1 — Audio I/O

### Queue
- **Celery** 5.3.4 — Task queue
- **Redis** 5.0.1 — Cache & broker

---

## 🔐 Security

- JWT-based authentication
- bcrypt password hashing
- CORS protection
- Rate limiting (TODO)
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy)

---

## 📈 Monitoring

- Health check endpoint: `/health`
- Prometheus metrics (TODO)
- Sentry error tracking (TODO)
- Request logging with loguru

---

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 📝 Notes

- Frontend install is currently blocked (Node v24 + pnpm issue)
- Backend can be developed independently
- Python audio engine already exists in `/src/samplemind/core/`
- Database schemas exist in `/src/samplemind/core/database/`
- Auth utilities exist in `/src/samplemind/core/auth/`

**Next Priority:** Implement auth and audio endpoints to unblock frontend integration.

---

**Status:** 🟡 Bootstrap complete, ready for endpoint implementation  
**Priority:** 🔴 CRITICAL PATH — Backend is blocker for Phase 8 (AI UX)

---

Built with ❤️ for music producers and audio engineers
