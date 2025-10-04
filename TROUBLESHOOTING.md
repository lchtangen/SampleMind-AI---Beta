# 🔧 SampleMind AI - Troubleshooting Guide

**Version:** 1.0 Beta  
**Last Updated:** 2025-10-04  
**Difficulty:** Beginner-Friendly 🟢

---

## 📑 Table of Contents

1. [Quick Fixes](#quick-fixes)
2. [Installation Issues](#installation-issues)
3. [Startup Problems](#startup-problems)
4. [Frontend Issues](#frontend-issues)
5. [Backend Issues](#backend-issues)
6. [Database Issues](#database-issues)
7. [Authentication Problems](#authentication-problems)
8. [Upload & File Issues](#upload--file-issues)
9. [Performance Issues](#performance-issues)
10. [Common Error Messages](#common-error-messages)

---

## ⚡ Quick Fixes

### The "Turn It Off and On Again" Solutions

```
┌─────────────────────────────────────────────────────────┐
│           🚨 TRY THESE FIRST (90% Success Rate)         │
└─────────────────────────────────────────────────────────┘

Problem: Something doesn't work
Solution: Restart everything

Step 1: Stop all services
  $ ./quick_start.sh stop

Step 2: Wait 10 seconds
  ⏰ Count: 1... 2... 3... 10

Step 3: Start everything again
  $ ./quick_start.sh

Result: [ ] Fixed!  [ ] Still broken (continue reading)
```

### The Nuclear Option (Clean Slate)

```
⚠️  WARNING: This deletes all data!

┌─────────────────────────────────────────────────────────┐
│                   COMPLETE RESET                         │
└─────────────────────────────────────────────────────────┘

# Stop everything
./quick_start.sh stop

# Delete all data (containers, volumes, everything)
docker-compose down -v

# Start fresh
./quick_start.sh

✅ This fixes 95% of issues!
❌ But you'll lose all uploaded files and user data
```

---

## 🔧 Installation Issues

### Issue 1: Docker Not Installed

**Symptom:**
```
❌ bash: docker: command not found
```

**Visual Guide:**
```
┌─────────────────────────────────────────────────────────┐
│                    INSTALL DOCKER                        │
└─────────────────────────────────────────────────────────┘

Ubuntu/Debian:
  Step 1: Update packages
    $ sudo apt update

  Step 2: Install Docker
    $ sudo apt install docker.io docker-compose

  Step 3: Start Docker service
    $ sudo systemctl start docker
    $ sudo systemctl enable docker

  Step 4: Add yourself to docker group
    $ sudo usermod -aG docker $USER

  Step 5: Log out and log back in
    ⚠️  IMPORTANT: This step is required!

  Step 6: Verify installation
    $ docker --version
    ✅ Should show: Docker version XX.XX.X

  Step 7: Test Docker
    $ docker run hello-world
    ✅ Should download and run successfully
```

**macOS:**
```
Step 1: Download Docker Desktop
  → Go to: https://www.docker.com/products/docker-desktop

Step 2: Install the .dmg file
  → Drag to Applications folder

Step 3: Launch Docker Desktop
  → It will appear in your menu bar

Step 4: Wait for "Docker Desktop is running"

Step 5: Verify
  $ docker --version
  ✅ Should work!
```

---

### Issue 2: Permission Denied

**Symptom:**
```
❌ permission denied while trying to connect to the Docker daemon
```

**Fix:**
```
┌─────────────────────────────────────────────────────────┐
│              FIX DOCKER PERMISSIONS                      │
└─────────────────────────────────────────────────────────┘

Method 1: Add user to docker group
  $ sudo usermod -aG docker $USER

Method 2: Log out and log back in
  ⚠️  REQUIRED: Changes take effect after re-login

Method 3: Verify you're in docker group
  $ groups
  ✅ Should include "docker"

Temporary fix (for current session):
  $ newgrp docker
```

---

### Issue 3: Port Already in Use

**Symptom:**
```
❌ Error: bind: address already in use
   Ports: 8000, 3000, 27017, 6379
```

**Visual Diagnostic:**
```
┌─────────────────────────────────────────────────────────┐
│              FIND & KILL PORT CONFLICTS                  │
└─────────────────────────────────────────────────────────┘

Check which ports are in use:

Port 8000 (Backend API):
  $ lsof -ti:8000
  → Shows process ID (e.g., 12345)

Port 3000 (Frontend):
  $ lsof -ti:3000
  → Shows process ID

Port 27017 (MongoDB):
  $ lsof -ti:27017
  → Shows process ID

Port 6379 (Redis):
  $ lsof -ti:6379
  → Shows process ID
```

**Kill Processes:**
```
┌─────────────────────────────────────────────────────────┐
│                    SOLUTION OPTIONS                      │
└─────────────────────────────────────────────────────────┘

Option 1: Kill specific port
  $ kill $(lsof -ti:8000)
  ✅ Kills process on port 8000

Option 2: Kill all conflicting ports
  $ lsof -ti:8000,3000,27017,6379 | xargs kill
  ✅ Kills all at once

Option 3: Force kill if needed
  $ kill -9 $(lsof -ti:8000)
  ⚠️  Use -9 only if normal kill doesn't work

Option 4: Change ports in configuration
  Edit .env file:
    API_PORT=8001  # Instead of 8000
    FRONTEND_PORT=3001  # Instead of 3000
```

---

## 🚀 Startup Problems

### Issue 4: Services Won't Start

**Visual Checklist:**
```
┌─────────────────────────────────────────────────────────┐
│           STARTUP TROUBLESHOOTING FLOWCHART              │
└─────────────────────────────────────────────────────────┘

Start Here ➜ Run: ./quick_start.sh
                │
                ↓
         Does it start?
          ┌─────┴─────┐
        Yes           No
          │             │
          ↓             ↓
    ✅ Success!    Check Docker
                        │
                        ↓
                 $ docker ps
                 Shows containers?
                  ┌─────┴─────┐
                Yes           No
                  │             │
                  ↓             ↓
          Check logs       Start Docker
          $ docker-compose  $ sudo systemctl
          logs -f api       start docker
                  │             │
                  ↓             ↓
            Find error     Try again
```

**Check Service Status:**
```
┌─────────────────────────────────────────────────────────┐
│                  SERVICE HEALTH CHECK                    │
└─────────────────────────────────────────────────────────┘

$ ./quick_start.sh status

Expected Output:
  ✅ MongoDB:   Running on port 27017
  ✅ Redis:     Running on port 6379
  ✅ ChromaDB:  Running on port 8001
  ✅ Backend:   Running on port 8000
  ✅ Frontend:  Running on port 3000

If any show ❌:
  → Check logs: docker-compose logs [service-name]
  → Examples:
    $ docker-compose logs mongodb
    $ docker-compose logs api
    $ docker-compose logs frontend
```

---

### Issue 5: Slow Startup

**Symptom:**
```
⏰ Services take 5+ minutes to start
```

**Diagnostic:**
```
┌─────────────────────────────────────────────────────────┐
│              WHY IS IT SLOW? CHECK THESE:                │
└─────────────────────────────────────────────────────────┘

Cause 1: First-time download
  → Docker is downloading images
  → Normal on first run
  ✅ Solution: Wait (one-time only)

Cause 2: Low disk space
  → Check: $ df -h
  ✅ Solution: Clean up disk

Cause 3: Low RAM
  → Check: $ free -h
  ✅ Solution: Close other apps

Cause 4: Old Docker images
  → Clean: $ docker system prune -a
  ✅ Solution: Remove unused images

Visual Progress:
  First Start:  ████████░░ 5-10 minutes
  Normal Start: ████████████ 1-2 minutes
  Quick Start:  ████████████ 30 seconds
```

---

## 🖥️ Frontend Issues

### Issue 6: "Cannot connect to server" Error

**Visual Flow:**
```
┌─────────────────────────────────────────────────────────┐
│           FRONTEND ↔️ BACKEND CONNECTION                 │
└─────────────────────────────────────────────────────────┘

Browser (Port 3000)
        │
        ↓ Tries to connect to...
        │
Backend API (Port 8000)
        │
        ├─ Is it running? $ curl http://localhost:8000/health
        │   ✅ Works → Check CORS settings
        │   ❌ Fails → Start backend
        │
        ├─ Check backend logs:
        │   $ docker-compose logs api
        │
        └─ Common fixes:
            1. Restart backend: docker-compose restart api
            2. Check .env: API_URL=http://localhost:8000
            3. Clear browser cache: Ctrl+Shift+Del
```

**Step-by-Step Fix:**
```
Step 1: Check if backend is running
  $ curl http://localhost:8000/health
  Expected: {"status": "healthy"}

Step 2: Check frontend environment
  $ cat frontend/web/.env.local
  Should have: NEXT_PUBLIC_API_URL=http://localhost:8000

Step 3: Restart services
  $ docker-compose restart api frontend

Step 4: Clear browser cache
  Chrome: Ctrl+Shift+Delete → Clear cache
  Firefox: Ctrl+Shift+Delete → Clear cache

Step 5: Hard reload page
  Ctrl+Shift+R (Windows/Linux)
  Cmd+Shift+R (macOS)
```

---

### Issue 7: White Screen / Blank Page

**Visual Diagnostic:**
```
┌─────────────────────────────────────────────────────────┐
│                  WHITE SCREEN DEBUG                      │
└─────────────────────────────────────────────────────────┘

Open Browser DevTools (F12)
        │
        ├─ Check Console Tab
        │   └─ See errors? → Read error message
        │       │
        │       ├─ "Module not found" → npm install
        │       ├─ "fetch failed" → Check API
        │       └─ "Syntax error" → Check recent code changes
        │
        ├─ Check Network Tab
        │   └─ Failed requests? → Check backend
        │
        └─ Check Application Tab
            └─ LocalStorage → Clear if needed
```

**Common Fixes:**
```
Fix 1: Rebuild frontend
  $ cd frontend/web
  $ rm -rf .next node_modules
  $ npm install
  $ npm run build
  $ npm run dev

Fix 2: Check JavaScript errors
  → Open DevTools Console (F12)
  → Look for red errors
  → Google the error message

Fix 3: Check if backend is responding
  $ curl http://localhost:8000/api/v1/health
  Should return JSON

Fix 4: Try different browser
  → Chrome doesn't work? Try Firefox
  → Private/Incognito mode
```

---

### Issue 8: Styles Look Broken

**Symptom:**
```
┌─────────────────────────────────────────────────────────┐
│  EXPECTED          vs          WHAT YOU SEE              │
├──────────────────────────────────────────────────────────┤
│  Nice buttons              Plain text buttons            │
│  Colorful cards            Gray boxes                    │
│  Beautiful layout          Messy text                    │
└─────────────────────────────────────────────────────────┘
```

**Fix:**
```
Cause: CSS not loading

Solution 1: Clear cache and hard reload
  $ Ctrl+Shift+R (or Cmd+Shift+R on Mac)

Solution 2: Check if Tailwind CSS is working
  $ cd frontend/web
  $ npm run dev
  → Should show "Compiled successfully"

Solution 3: Rebuild CSS
  $ cd frontend/web
  $ npx tailwindcss build -o styles/output.css

Solution 4: Check for CSS errors
  → Open DevTools → Console
  → Look for CSS loading errors
```

---

## 🔌 Backend Issues

### Issue 9: API Not Responding

**Visual Diagnostic:**
```
┌─────────────────────────────────────────────────────────┐
│              BACKEND HEALTH CHECKLIST                    │
└─────────────────────────────────────────────────────────┘

Test 1: Basic health check
  $ curl http://localhost:8000/health
  
  ✅ Expected: {"status":"healthy","timestamp":"..."}
  ❌ If fails: Backend is down

Test 2: Check if process is running
  $ docker ps | grep api
  
  ✅ Shows container: Backend container exists
  ❌ No output: Container is not running

Test 3: Check logs
  $ docker-compose logs api --tail=50
  
  Look for:
  ✅ "Application startup complete"
  ❌ "Error" or "Exception"

Test 4: Check port
  $ lsof -ti:8000
  
  ✅ Shows PID: Something is listening
  ❌ No output: Nothing on port 8000
```

**Fix Flow:**
```
Problem: API not responding
        │
        ├─ Step 1: Check if running
        │   $ docker ps
        │   Not running? → docker-compose up -d api
        │
        ├─ Step 2: Check logs for errors
        │   $ docker-compose logs api
        │   Has errors? → Read error message
        │
        ├─ Step 3: Check environment
        │   $ docker-compose exec api env | grep -i secret
        │   Missing vars? → Check .env file
        │
        └─ Step 4: Restart with fresh start
            $ docker-compose down
            $ docker-compose up -d
```

---

### Issue 10: Import Errors

**Symptom:**
```
❌ ModuleNotFoundError: No module named 'fastapi'
❌ ImportError: cannot import name 'XXX'
```

**Fix:**
```
┌─────────────────────────────────────────────────────────┐
│              FIX PYTHON IMPORT ERRORS                    │
└─────────────────────────────────────────────────────────┘

Step 1: Check if virtual environment is activated
  $ which python
  Should show: .venv/bin/python

Step 2: Activate if not activated
  $ source .venv/bin/activate

Step 3: Reinstall dependencies
  $ pip install -r requirements.txt

Step 4: Check for typos in imports
  → Open the file with the error
  → Check spelling of import names

Step 5: Check if module is installed
  $ pip list | grep fastapi
  Should show fastapi and version

Step 6: If using Docker
  $ docker-compose build --no-cache api
  $ docker-compose up -d api
```

---

## 🗄️ Database Issues

### Issue 11: MongoDB Connection Error

**Symptom:**
```
❌ pymongo.errors.ServerSelectionTimeoutError: 
   localhost:27017: [Errno 111] Connection refused
```

**Visual Debug:**
```
┌─────────────────────────────────────────────────────────┐
│              MONGODB TROUBLESHOOTING                     │
└─────────────────────────────────────────────────────────┘

Check 1: Is MongoDB running?
  $ docker ps | grep mongodb
  
  ✅ Shows mongo container
  ❌ Nothing → Start MongoDB:
     $ docker-compose up -d mongodb

Check 2: Can you connect manually?
  $ docker-compose exec mongodb mongosh
  
  ✅ Opens mongo shell → MongoDB is working
  ❌ Error → MongoDB has issues

Check 3: Check logs
  $ docker-compose logs mongodb
  
  Look for:
  ✅ "Waiting for connections on port 27017"
  ❌ "ERROR" or "FATAL"

Check 4: Check connection string
  $ cat .env | grep MONGODB
  
  Should be: MONGODB_URL=mongodb://localhost:27017
```

**Fix:**
```
Fix 1: Restart MongoDB
  $ docker-compose restart mongodb
  $ sleep 10  # Wait for startup
  $ docker-compose restart api

Fix 2: Clear MongoDB data (⚠️ Deletes data!)
  $ docker-compose down
  $ docker volume rm samplemind-ai-v6_mongodb_data
  $ docker-compose up -d mongodb

Fix 3: Check MongoDB health
  $ curl http://localhost:27017
  Expected: "It looks like you are trying to access MongoDB..."

Fix 4: Use different port (if 27017 is taken)
  Edit docker-compose.yml:
    ports:
      - "27018:27017"  # Use 27018 instead
```

---

### Issue 12: Redis Connection Error

**Symptom:**
```
❌ redis.exceptions.ConnectionError: 
   Error connecting to Redis
```

**Quick Fix:**
```
┌─────────────────────────────────────────────────────────┐
│                REDIS QUICK FIX                           │
└─────────────────────────────────────────────────────────┘

1. Check if Redis is running
   $ docker ps | grep redis

2. Test connection
   $ docker-compose exec redis redis-cli ping
   Expected: PONG

3. If not responding
   $ docker-compose restart redis

4. Check logs
   $ docker-compose logs redis
   Should show: "Ready to accept connections"

5. Test from Python
   $ docker-compose exec api python -c "import redis; r=redis.Redis(host='redis'); print(r.ping())"
   Expected: True
```

---

## 🔐 Authentication Problems

### Issue 13: Can't Login

**Visual Flowchart:**
```
┌─────────────────────────────────────────────────────────┐
│              LOGIN TROUBLESHOOTING TREE                  │
└─────────────────────────────────────────────────────────┘

Enter username + password
        │
        ↓
  Submit form
        │
        ├─ Error: "Invalid credentials"
        │   → Wrong password?
        │       ├─ Try "Forgot Password"
        │       └─ Create new account
        │
        ├─ Error: "Network error"
        │   → Check backend is running
        │   $ curl http://localhost:8000/health
        │
        ├─ Error: "User not found"
        │   → Account doesn't exist
        │   → Register new account
        │
        ├─ Infinite loading
        │   → Check browser console (F12)
        │   → Check backend logs
        │
        └─ Success but redirects to login
            → Token issue
            → Clear browser cache
            → Check localStorage
```

**Step-by-Step Fix:**
```
Problem: "Invalid credentials"

Step 1: Verify you're using the right username
  → Usernames are case-sensitive
  → Try lowercase version

Step 2: Reset password
  → Click "Forgot password?"
  → Enter email
  → Check email for reset link

Step 3: Check if account exists
  → Try registering with same email
  → If says "email already exists" → account exists

Step 4: Check database
  $ docker-compose exec mongodb mongosh
  > use samplemind
  > db.users.findOne({username: "YOUR_USERNAME"})
  → Should show your user data
```

---

### Issue 14: Token Expired

**Symptom:**
```
After login, get logged out immediately
or
"Token expired" error
```

**Fix:**
```
┌─────────────────────────────────────────────────────────┐
│              TOKEN EXPIRY SOLUTIONS                      │
└─────────────────────────────────────────────────────────┘

Cause 1: System time is wrong
  Check:  $ date
  Fix:    $ sudo timedatectl set-ntp true

Cause 2: Token lifetime too short
  Check:  $ cat .env | grep TOKEN_EXPIRE
  Fix:    ACCESS_TOKEN_EXPIRE_MINUTES=30

Cause 3: Browser clock wrong
  → Go to browser settings
  → Check system time
  → Sync with internet time

Cause 4: LocalStorage cleared
  → F12 → Application → LocalStorage
  → Check if auth_token exists
  → If missing: Login again

Cause 5: Server restarted
  → Tokens invalidated on restart
  → Just login again
```

---

## 📁 Upload & File Issues

### Issue 15: Upload Fails

**Visual Diagnostic:**
```
┌─────────────────────────────────────────────────────────┐
│              UPLOAD FAILURE DIAGNOSIS                    │
└─────────────────────────────────────────────────────────┘

Upload fails at X%
        │
        ├─ Fails at 0%
        │   → Network issue
        │   → Check backend connection
        │
        ├─ Fails at 50-90%
        │   → File too large
        │   → Network timeout
        │
        └─ Completes but shows error
            → Backend processing error
            → Check file format

Error Messages:
  "File too large"
    → Max: 50MB
    → Compress file or split it

  "Unsupported format"
    → Allowed: MP3, WAV, FLAC, OGG, M4A
    → Convert to allowed format

  "Network error"
    → Check internet connection
    → Check backend is running
```

**Fix:**
```
Fix 1: Check file size
  $ ls -lh your_file.mp3
  → Should be < 50MB

Fix 2: Check file format
  $ file your_file.mp3
  → Should show audio format

Fix 3: Test with small file first
  → Try uploading a 1MB test file
  → If works: Original file is problematic

Fix 4: Check storage space
  $ df -h
  → Should have free space

Fix 5: Check backend upload limit
  $ cat .env | grep MAX_FILE_SIZE
  → Should be 52428800 (50MB)

Fix 6: Check network
  $ ping 8.8.8.8
  → Should respond
```

---

### Issue 16: Files Disappear

**Symptom:**
```
Uploaded files, but they're gone after restart
```

**Why This Happens:**
```
┌─────────────────────────────────────────────────────────┐
│            WHERE ARE MY FILES?                           │
└─────────────────────────────────────────────────────────┘

Scenario 1: Using Docker volumes
  Files stored in: Docker volume
  On restart: Should persist
  If missing: Volume was deleted

Scenario 2: Using local storage
  Files stored in: ./storage/uploads/
  On restart: Should persist
  If missing: Folder was deleted

Scenario 3: Using temp storage
  Files stored in: /tmp/
  On restart: Gone! (temp is cleared)
  Fix: Change storage location
```

**Prevention:**
```
Check storage configuration:
  $ cat .env | grep STORAGE

Should be:
  STORAGE_TYPE=local
  STORAGE_PATH=./storage/uploads

NOT:
  STORAGE_PATH=/tmp/  ❌ Bad! Will be deleted

Verify files exist:
  $ ls -la storage/uploads/
  → Should show your files

Backup important files:
  $ cp -r storage/uploads ~/backup/
```

---

## ⚡ Performance Issues

### Issue 17: Slow Response Times

**Visual Performance Guide:**
```
┌─────────────────────────────────────────────────────────┐
│           PERFORMANCE EXPECTATIONS                       │
└─────────────────────────────────────────────────────────┘

Page Load Times:
  Login page:     < 1 second   ████████████ Fast
  Dashboard:      < 2 seconds  ██████████░░ Good
  Library (10):   < 3 seconds  ████████░░░░ OK
  Library (100):  < 5 seconds  ██████░░░░░░ Slow

API Response Times:
  GET /health:    < 100ms      ████████████ Fast
  POST /login:    < 500ms      ██████████░░ Good
  POST /upload:   varies       ████░░░░░░░░ Depends on file
  GET /library:   < 1s         ████████░░░░ OK

If slower than this:
  → Something is wrong!
```

**Diagnostic Tools:**
```
Tool 1: Browser DevTools (F12)
  Network tab → Check request times
  Performance tab → Record and analyze

Tool 2: Backend timing
  $ time curl http://localhost:8000/api/v1/audio
  → Shows how long API takes

Tool 3: Database performance
  $ docker stats
  → Shows CPU and memory usage

Tool 4: Check system resources
  $ htop  # or `top`
  → Shows what's using CPU/RAM
```

**Common Fixes:**
```
Fix 1: Too many files in library
  → Use pagination
  → Limit results: GET /audio?limit=20

Fix 2: Database not indexed
  → Check MongoDB indexes
  → Add indexes for common queries

Fix 3: Not enough RAM
  → Close other applications
  → Increase Docker memory limit

Fix 4: Slow network
  → Check WiFi connection
  → Use wired connection if possible

Fix 5: Debug mode enabled
  → Check: DEBUG=false in .env
  → Debug mode is slower
```

---

## 🐛 Common Error Messages

### Error Code Reference

```
┌─────────────────────────────────────────────────────────┐
│         ERROR CODE → MEANING → SOLUTION                  │
└─────────────────────────────────────────────────────────┘

401 Unauthorized
  Meaning: Not logged in or token expired
  Fix: Login again

403 Forbidden
  Meaning: Logged in but no permission
  Fix: Check user role / permissions

404 Not Found
  Meaning: URL doesn't exist
  Fix: Check URL spelling

422 Unprocessable Entity
  Meaning: Invalid data sent
  Fix: Check request body format

500 Internal Server Error
  Meaning: Server crashed
  Fix: Check backend logs
       $ docker-compose logs api

503 Service Unavailable
  Meaning: Server is down
  Fix: Start services
       $ ./quick_start.sh
```

### Python Errors

```
ModuleNotFoundError
  → Missing dependency
  → Fix: pip install -r requirements.txt

ImportError
  → Wrong import path
  → Fix: Check file structure

ConnectionRefusedError
  → Service not running
  → Fix: Start the service

TimeoutError
  → Service too slow or stuck
  → Fix: Restart service
```

### JavaScript/React Errors

```
"Cannot read property 'X' of undefined"
  → Accessing property of null/undefined
  → Fix: Add null checks

"Maximum update depth exceeded"
  → Infinite render loop
  → Fix: Check useEffect dependencies

"Failed to fetch"
  → Network/API error
  → Fix: Check backend is running

"Hydration failed"
  → Server/client mismatch
  → Fix: Clear .next folder and rebuild
```

---

## 🆘 Still Stuck?

### Debugging Checklist

```
✅ Have you tried turning it off and on again?
✅ Have you checked the logs?
✅ Have you read the error message carefully?
✅ Have you googled the error message?
✅ Have you checked this troubleshooting guide?
✅ Have you asked someone for help?
```

### Get Help

```
┌─────────────────────────────────────────────────────────┐
│                  WHERE TO GET HELP                       │
└─────────────────────────────────────────────────────────┘

1. Documentation
   → Start with: START_HERE.md
   → User guide: USER_GUIDE.md
   → Quick ref: QUICK_REFERENCE.md

2. Logs
   → Backend: docker-compose logs api
   → Frontend: Check browser console (F12)
   → Database: docker-compose logs mongodb

3. Community
   → Discord: discord.gg/samplemind
   → GitHub: github.com/samplemind/issues

4. Email Support
   → support@samplemind.ai
```

### Reporting Bugs

```
When reporting a bug, include:

1. What you were trying to do
   "I tried to upload an MP3 file"

2. What happened
   "Got error: File too large"

3. What you expected
   "File should upload successfully"

4. System information
   OS: Ubuntu 22.04
   Docker: 24.0.5
   Browser: Chrome 119

5. Screenshots (if relevant)

6. Error logs
   $ docker-compose logs api > error.log
```

---

## 📚 Related Documentation

- [START_HERE.md](./START_HERE.md) - 5-minute orientation
- [USER_GUIDE.md](./USER_GUIDE.md) - Complete user guide
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Command reference
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Setup instructions

---

## 💡 Pro Tips

1. **Keep logs**: Always check logs first
2. **Google is your friend**: Copy-paste error messages
3. **Start simple**: Test with minimal setup first
4. **One change at a time**: Don't change multiple things simultaneously
5. **Document your fix**: Help others by sharing solutions

---

**Last Updated:** 2025-10-04 | **Version:** 1.0 Beta

**Remember:** Every problem has a solution! Don't give up! 💪🔧
