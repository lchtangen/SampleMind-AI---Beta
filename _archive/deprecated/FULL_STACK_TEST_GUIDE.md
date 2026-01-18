# 🧪 Full Stack Integration Test Guide

**Date:** October 19, 2025  
**Status:** Ready to Execute  
**Duration:** 20 minutes

---

## 🎯 TEST OBJECTIVES

Verify the complete platform works end-to-end:
- ✅ Backend API operational
- ✅ Frontend loads and renders
- ✅ Authentication flow works
- ✅ File upload functional
- ✅ Real-time updates working
- ✅ Database persistence
- ✅ All integrations connected

---

## 📋 PRE-REQUISITES

### 1. Database Running
```bash
# PostgreSQL should be running
# If using Docker:
docker-compose up -d postgres

# If local PostgreSQL:
brew services start postgresql@15
```

### 2. Dependencies Installed
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd apps/web
pnpm install
```

### 3. Environment Variables
```bash
# Backend: backend/.env
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://samplemind:samplemind123@localhost:5432/samplemind

# Frontend: apps/web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🚀 TEST EXECUTION

### Phase 1: Start Backend (5 min)

```bash
# Terminal 1: Backend
cd backend

# Initialize database (if not done)
python scripts/init_db.py

# Start API
python main.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Verify Backend:**
```bash
# In another terminal:
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"samplemind-api"}

# Check API docs:
# Open: http://localhost:8000/api/docs
# Should show Swagger UI with 14 endpoints
```

**✅ Backend Check:**
- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] API docs load
- [ ] No error logs

---

### Phase 2: Start Frontend (3 min)

```bash
# Terminal 2: Frontend
cd apps/web

# Start development server
pnpm dev

# Expected output:
#   ▲ Next.js 14.x.x
#   - Local:        http://localhost:3000
#   - Ready in X.Xs
```

**Verify Frontend:**
```bash
# Open browser: http://localhost:3000
# Should see landing page with:
# - SampleMind AI logo
# - Hero section
# - "Get Started" button
# - Cyberpunk glassmorphism theme
```

**✅ Frontend Check:**
- [ ] Server starts without errors
- [ ] Landing page loads
- [ ] Styling renders correctly
- [ ] No console errors

---

### Phase 3: Test Authentication (5 min)

**3.1 Navigate to Login**
```
1. Open http://localhost:3000/login
2. Should see LoginForm with:
   - Email input
   - Password input
   - "Create Account" / "Sign In" toggle
   - Glassmorphic design
```

**3.2 Register New Account**
```
1. Click "Don't have an account? Sign up"
2. Fill in:
   - Full Name: "Test User"
   - Email: "test@samplemind.ai"
   - Password: "test123456"
3. Click "Create Account"
4. Should see loading spinner
5. Should auto-redirect to /dashboard
```

**3.3 Verify Dashboard**
```
1. Should see personalized greeting: "Welcome Back, Test User"
2. Should see stats (will be 0 initially):
   - Total Tracks: 0
   - Analyzed: 0
   - Processing: 0
3. Should see "Upload Your First Track" CTA
4. Should see user email in header
5. Should see logout button
```

**✅ Authentication Check:**
- [ ] Login page renders
- [ ] Registration works
- [ ] JWT tokens stored (check DevTools → Application → Local Storage)
- [ ] Auto-redirect to dashboard
- [ ] User info displays
- [ ] Protected route works

---

### Phase 4: Test File Upload (5 min)

**4.1 Navigate to Upload**
```
1. Click "Upload" in navigation
2. Should see upload page at /upload
3. Should see drag-drop zone
4. Should see user email in header
```

**4.2 Upload Test File**
```
1. Create test file or use any audio file:
   - MP3, WAV, FLAC, AIFF, or OGG
   - Under 100MB

2. Drag file to upload zone OR click to browse

3. Watch for:
   - File appears in list
   - Progress bar animates (0% → 100%)
   - Status changes: uploading → completed
   - Green checkmark appears
   - Success notification: "filename uploaded successfully!"

4. Click "View Library" button
```

**4.3 Verify in Dashboard**
```
1. Navigate back to /dashboard
2. Should see:
   - Total Tracks: 1
   - File listed in Recent Activity
   - Status shows "completed"
   - Timestamp displayed
```

**✅ Upload Check:**
- [ ] Upload page loads
- [ ] Drag & drop works
- [ ] Progress tracking displays
- [ ] Success notification appears
- [ ] File persists in database
- [ ] Dashboard updates with new file

---

### Phase 5: Test Real-Time Updates (2 min)

**5.1 Open Multiple Browser Windows**
```
1. Open http://localhost:3000/dashboard in Window 1
2. Open http://localhost:3000/dashboard in Window 2 (incognito)
3. Login with same account in both
```

**5.2 Upload in One Window**
```
1. In Window 1, navigate to /upload
2. Upload a file
3. Watch Window 2 dashboard
4. Should see real-time update (WebSocket)
```

**✅ Real-Time Check:**
- [ ] WebSocket connects (check Network tab)
- [ ] Both windows show updates
- [ ] Notifications appear
- [ ] Stats refresh automatically

---

### Phase 6: Test Logout (1 min)

```
1. Click "Logout" button in header
2. Should see logout notification
3. Should redirect to landing page (/)
4. Try accessing /dashboard directly
5. Should auto-redirect to /login
```

**✅ Logout Check:**
- [ ] Logout works
- [ ] Tokens cleared
- [ ] Redirects correctly
- [ ] Protected routes block access

---

## 📊 TEST RESULTS TEMPLATE

```markdown
## Full Stack Test Results
**Date:** [Date]
**Tester:** [Name]
**Duration:** [Time]

### Backend
- [x] Server starts: ✅
- [x] Health check: ✅
- [x] API docs load: ✅
- [ ] Errors: None

### Frontend
- [x] Server starts: ✅
- [x] Landing page: ✅
- [x] Styling correct: ✅
- [ ] Console errors: None

### Authentication
- [x] Registration: ✅
- [x] Login: ✅
- [x] JWT storage: ✅
- [x] Dashboard access: ✅
- [x] Logout: ✅

### File Upload
- [x] Upload page: ✅
- [x] File upload: ✅
- [x] Progress tracking: ✅
- [x] Notifications: ✅
- [x] Persistence: ✅

### Real-Time
- [x] WebSocket connects: ✅
- [x] Live updates: ✅
- [ ] Latency: <500ms

### Overall Status
- **Result:** ✅ PASS
- **Issues:** None
- **Notes:** All features working perfectly
```

---

## 🐛 TROUBLESHOOTING

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep fastapi

# Check port availability
lsof -i :8000

# Try different port
uvicorn main:app --port 8001
```

### Frontend Won't Start
```bash
# Check Node version
node --version  # Should be 20+

# Clear cache
rm -rf .next node_modules
pnpm install

# Check port availability
lsof -i :3000
```

### Database Connection Errors
```bash
# Check PostgreSQL running
pg_isready

# Check connection
psql postgresql://samplemind:samplemind123@localhost:5432/samplemind

# Re-initialize
python scripts/init_db.py
```

### Upload Fails
```bash
# Check backend logs for errors
# Verify file size < 100MB
# Check CORS settings
# Verify authentication token
```

---

## ✅ SUCCESS CRITERIA

All checks should pass:
- ✅ Backend operational
- ✅ Frontend rendering
- ✅ Authentication working
- ✅ File upload functional
- ✅ Real-time updates active
- ✅ Database persisting
- ✅ No critical errors

**Result:** Production-ready for staging deployment!

---

## 📸 SCREENSHOT CHECKLIST

Capture these for documentation:
- [ ] Landing page
- [ ] Login page
- [ ] Dashboard (empty state)
- [ ] Upload page
- [ ] Upload in progress
- [ ] Dashboard with files
- [ ] Success notification
- [ ] API docs page

---

## 🎯 NEXT STEPS AFTER TESTING

### If All Tests Pass ✅
1. Document results
2. Create demo video
3. Deploy to staging
4. Invite beta testers

### If Issues Found ❌
1. Document each issue
2. Prioritize fixes
3. Re-test after fixes
4. Update documentation

---

**Test Guide Status:** ✅ Ready to Execute  
**Estimated Time:** 20 minutes  
**Difficulty:** Easy  
**Prerequisites:** Backend + Frontend running
