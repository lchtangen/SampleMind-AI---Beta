# 🧪 Full-Stack Testing Guide - SampleMind AI

Complete guide for testing the entire application stack.

## 📋 Prerequisites

Make sure you have:
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ and pnpm installed
- ✅ PostgreSQL running (via Docker)
- ✅ Redis running (optional, for caching)

---

## 🎯 Quick Start - Test Everything

### 1. Backend API Testing

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Run all backend tests
python -m pytest -v

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_audio.py -v

# Run with live output
python -m pytest -v -s
```

**Current Status:** ✅ **46/46 tests passing (100%)**

### 2. Frontend Web App Testing

```bash
# Navigate to web app
cd apps/web

# Install dependencies (if not done)
pnpm install

# Run unit tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage

# Type checking
pnpm typecheck

# Linting
pnpm lint
```

### 3. Component Testing with Storybook

```bash
# In apps/web directory
pnpm storybook

# Opens Storybook on http://localhost:6006
# View and interact with components in isolation
```

---

## 🚀 Full Stack Integration Testing

### Step 1: Start Backend API

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate

# Start the API server
uvicorn app.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# 📚 API Docs: http://127.0.0.1:8000/api/docs
```

**API will be available at:**
- Main API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/redoc

### Step 2: Start Frontend Web App

```bash
# Terminal 2 - Frontend
cd apps/web

# Start Next.js dev server
pnpm dev

# You should see:
# ▲ Next.js 14.1.0
# - Local:        http://localhost:3000
```

**Web App will be available at:**
- Frontend: http://localhost:3000

### Step 3: Manual Testing

Now test the full stack:

#### Test Authentication Flow
1. Go to http://localhost:3000
2. Click "Sign Up" or go to `/auth/register`
3. Create account:
   - Email: `test@samplemind.ai`
   - Password: `test123456`
   - Full Name: `Test User`
4. Login with credentials
5. Verify you're redirected to dashboard

#### Test Audio Upload Flow
1. Go to `/upload` page
2. Click "Upload Audio" or drag/drop file
3. Select audio file (MP3, WAV, FLAC, AIFF, OGG)
4. Verify upload progress
5. Check file appears in library

#### Test Audio Analysis
1. Go to library `/library`
2. Click on uploaded audio file
3. Click "Analyze"
4. Verify analysis results:
   - Tempo, key, time signature
   - Genre, mood, instruments
   - AI description

---

## 🧪 API Testing with Curl/HTTPie

### Authentication Tests

```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "password123",
    "full_name": "New User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "password123"
  }'

# Save the access_token from response

# Get current user
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Audio API Tests

```bash
# List audio files
curl http://localhost:8000/api/v1/audio \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Upload audio file
curl -X POST http://localhost:8000/api/v1/audio/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/audio.mp3"

# Get audio details
curl http://localhost:8000/api/v1/audio/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Analyze audio
curl -X POST http://localhost:8000/api/v1/audio/analyze \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_id": 1,
    "extract_features": true,
    "ai_analysis": true
  }'
```

---

## 🔍 Testing Checklist

### Backend API ✅
- [x] 13 Audio endpoint tests
- [x] 9 Authentication tests
- [x] 8 Feature flag tests
- [x] 7 Rate limiting tests
- [x] 6 Integration tests
- [x] 3 WebSocket tests

### Frontend Components
- [ ] Authentication forms (LoginForm, RegisterForm)
- [ ] Audio upload component
- [ ] Audio player component
- [ ] Library/grid view
- [ ] Analysis results display
- [ ] Dashboard statistics

### Integration Testing
- [ ] User registration → login → dashboard
- [ ] Audio upload → library listing → playback
- [ ] Audio analysis → view results
- [ ] Real-time WebSocket updates
- [ ] Error handling and validation
- [ ] Rate limiting behavior
- [ ] Token refresh flow

---

## 🐛 Debugging Tips

### Backend Issues

```bash
# Check if API is running
curl http://localhost:8000/health

# View detailed logs
uvicorn app.main:app --reload --log-level debug

# Test database connection
cd backend
python -c "from app.core.database import engine; print(engine.url)"

# Run specific test with verbose output
python -m pytest tests/test_auth.py::test_login_success -vv -s
```

### Frontend Issues

```bash
# Clear Next.js cache
rm -rf .next
pnpm dev

# Check TypeScript errors
pnpm typecheck

# Check for console errors in browser
# Open DevTools → Console tab

# Check API calls in Network tab
# Open DevTools → Network tab → Filter by "Fetch/XHR"
```

### Database Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Connect to database
psql -h localhost -U samplemind -d samplemind_db

# View tables
\dt

# View users
SELECT * FROM users;

# View audio files
SELECT * FROM audio_files;
```

---

## 📊 Test Coverage Reports

### Backend Coverage

```bash
cd backend
python -m pytest --cov=app --cov-report=html --cov-report=term

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Frontend Coverage

```bash
cd apps/web
pnpm test:coverage

# Coverage report will be in coverage/lcov-report/index.html
open coverage/lcov-report/index.html
```

---

## 🚢 Production Testing

### Build Frontend

```bash
cd apps/web
pnpm build

# Test production build locally
pnpm start
# Visit http://localhost:3000
```

### Test API in Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📱 Testing URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend Dev | http://localhost:3000 | Next.js dev server |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| Storybook | http://localhost:6006 | Component library |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |

---

## 🎯 Performance Testing

```bash
# Install Apache Bench (if not installed)
brew install httpd  # macOS

# Test API endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Load test authentication
ab -n 100 -c 10 -p login.json -T application/json \
  http://localhost:8000/api/v1/auth/login
```

---

## ✅ Success Criteria

Your full stack is working when:

1. ✅ All 46 backend tests pass
2. ✅ Frontend builds without errors
3. ✅ Can register and login
4. ✅ Can upload audio files
5. ✅ Can view audio library
6. ✅ Can analyze audio files
7. ✅ API documentation loads
8. ✅ No console errors in browser
9. ✅ WebSocket connections work
10. ✅ Rate limiting functions properly

---

## 🆘 Common Issues & Solutions

### Issue: "Cannot connect to database"
```bash
# Start PostgreSQL via Docker
docker-compose up -d postgres

# Or check your DATABASE_URL in .env
```

### Issue: "Port 3000 already in use"
```bash
# Find and kill process
lsof -ti:3000 | xargs kill -9

# Or use different port
pnpm dev -- -p 3001
```

### Issue: "Module not found"
```bash
# Reinstall dependencies
cd apps/web
rm -rf node_modules
pnpm install
```

### Issue: "401 Unauthorized"
```bash
# Check token is valid
# Check Authorization header format: "Bearer YOUR_TOKEN"
# Try logging in again to get fresh token
```

---

## 🎉 Next Steps

Once everything is tested:

1. 📝 Write additional frontend tests
2. 🧪 Add E2E tests with Playwright
3. 🚀 Set up CI/CD pipeline
4. 📊 Add monitoring and analytics
5. 🔒 Security audit
6. 🌍 Deploy to production

---

**Status:** Backend 100% tested ✅ | Frontend ready for integration testing 🚀
