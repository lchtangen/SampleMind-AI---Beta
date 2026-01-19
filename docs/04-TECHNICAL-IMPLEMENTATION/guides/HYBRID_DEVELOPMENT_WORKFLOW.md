# 🔄 HYBRID DEVELOPMENT WORKFLOW

## Complete Guide to CLI + Docker Backend Development

### Your Development Setup

```
┌─────────────────────────────────────────────────────────────────┐
│                         VSCode IDE                              │
│  ┌───────────────┐                        ┌──────────────────┐  │
│  │ CLI Code      │                        │ API Code         │  │
│  │ (Local .venv) │                        │ (Docker)         │  │
│  └───────┬───────┘                        └────────┬─────────┘  │
│          │                                         │             │
│  ┌───────▼──────────┐                   ┌─────────▼──────────┐  │
│  │ python main.py   │                   │ Docker Container   │  │
│  │ (Runs locally)   │◄──────HTTP───────►│ (localhost:8000)   │  │
│  └──────────────────┘                   └────────────────────┘  │
│          │                                         ▲              │
│          │                                         │              │
│          ├─────────────────────────────────────────┤              │
│          │ (CLI talks to API via HTTP)              │              │
│          │ ✓ localhost:8000 (Docker network)       │              │
│          │ ✓ Can work offline with Ollama           │              │
│          │ ✓ Full debugging with breakpoints        │              │
│          └───────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘

Docker Host Machine (separate from VSCode)
├─ samplemind-api (port 8000)
├─ mongodb (port 27017)
├─ redis (port 6379)
├─ ollama (port 11434)
└─ [other services]
```

---

## 🚀 Daily Development Workflow

### Morning: Setup

```bash
# 1. Navigate to project
cd ~/Documents/SampleMind-AI-DEV/SampleMind-AI---Beta

# 2. Activate Python environment
source .venv/bin/activate

# 3. Start Docker services (if not already running)
docker compose up -d

# 4. Verify services
docker ps  # Should see 8 containers
curl http://localhost:8000/health  # Should see {"status": "ok"}

# 5. Open VSCode
code .
```

### Working on CLI Features

**Scenario: Add new command to analyze samples**

```bash
# 1. Write code in VSCode
# File: src/samplemind/interfaces/cli/commands/analyze.py

# 2. Set breakpoint (click on line number in VSCode)

# 3. Run with debugger
# Press F5 or go to Run > Run and Debug

# 4. Select "CLI - Debug Main"

# 5. Code stops at breakpoint
# - Inspect variables
# - Step through code (F10 = step over, F11 = step into)
# - Check console output

# 6. Test command
# Terminal: python main.py analyze sample.wav
```

### Working on API Features

**Scenario: Create new API endpoint**

```bash
# 1. Write API code
# File: src/samplemind/interfaces/api/routes/samples.py

# 2. Endpoint in Docker automatically hot-reloads
# Check: docker logs samplemind-api -f

# 3. Test with Thunder Client
# - Open Thunder Client (Ctrl+Shift+D in VSCode)
# - POST http://localhost:8000/api/v1/samples
# - Send request
# - See response

# 4. Test from CLI
# python main.py (your CLI command that calls API)

# 5. Check logs
# docker logs samplemind-api
```

### Testing Both CLI + API Together

```bash
# 1. Start services
docker compose up -d

# 2. In Terminal 1: Watch API logs
docker logs samplemind-api -f

# 3. In Terminal 2: Run CLI command
source .venv/bin/activate
python main.py analyze sample.wav

# 4. Watch logs in Terminal 1 - you'll see:
# POST /api/v1/audio/analyze
# 200 OK
# [response data]

# This shows CLI successfully called API!
```

---

## 🐛 Debugging Workflow

### Debugging CLI Code

```bash
# 1. Open .vscode/launch.json

# 2. Select debug configuration: "CLI - Debug Main"

# 3. Press F5 or click Debug button

# 4. Code runs with debugger attached

# 5. Set breakpoint by clicking line number

# 6. When execution hits breakpoint:
#    - Variables panel: see all variables
#    - Watch: add expressions to watch
#    - Call Stack: see function call history
#    - Debug Console: run Python commands

# 7. Continue execution: F5 or click play button
```

### Debugging API Code

```bash
# Attach VSCode to running container:

# 1. Open Docker extension (left sidebar)

# 2. Expand "Containers" → Right-click "samplemind-api"

# 3. Select "Attach Visual Studio Code"

# 4. New VSCode window opens with container context

# 5. Navigate to src/ folder

# 6. Set breakpoints in API code

# 7. Make request to API:
#    curl http://localhost:8000/api/v1/endpoint

# 8. Breakpoint triggers - now you can debug!
```

### Debugging Network Issues

```bash
# Check if services are accessible:

# 1. Check if container is running
docker ps | grep samplemind-api

# 2. Check API is responding
curl http://localhost:8000/health

# 3. Check logs for errors
docker logs samplemind-api

# 4. Check network connectivity
docker exec samplemind-api curl http://localhost:8000/health

# 5. Check database connection
docker exec samplemind-mongodb mongosh --eval "db.adminCommand('ping')"

# 6. Check Redis
docker exec samplemind-redis redis-cli ping

# 7. Common fixes:
# - docker compose restart samplemind-api
# - docker compose down -v && docker compose up -d  (reset all)
# - Check firewall: sudo ufw status
```

---

## 📝 Feature Development Process

### Step 1: Plan

```
Goal: Add "suggest next sample" feature

CLI Side:
- Command: samplemind suggest:next
- Input: Current sample analysis
- Output: Recommended next sample with explanation

API Side:
- Endpoint: GET /api/v1/suggestions/next
- Logic: Use Gemini to suggest complementary samples
- Database: Query similar samples
- Return: Top 3 suggestions with reasoning
```

### Step 2: Implement API First

```bash
# 1. Create route file
touch src/samplemind/interfaces/api/routes/suggestions.py

# 2. Write endpoint
# (See API_LEARNING_GUIDE.md for patterns)

# 3. Test with Thunder Client
# GET http://localhost:8000/api/v1/suggestions/next?sample_id=123

# 4. Fix any issues using docker logs
```

### Step 3: Implement CLI

```bash
# 1. Create command file
touch src/samplemind/interfaces/cli/commands/suggest.py

# 2. Call API endpoint from CLI
# (See API_LEARNING_GUIDE.md for integration)

# 3. Format output nicely for terminal

# 4. Test: python main.py suggest:next

# 5. Verify it calls API correctly
# Watch docker logs samplemind-api -f
```

### Step 4: Test Both Together

```bash
# 1. Run CLI command
python main.py suggest:next

# 2. Watch API logs
# docker logs samplemind-api -f

# 3. Check output is correct

# 4. Test error cases
# - Missing sample
# - Invalid sample ID
# - Network error
# - AI API error

# 5. Add error handling
```

### Step 5: Quality Checks

```bash
# 1. Format code
make format

# 2. Lint code
make lint

# 3. Type check
make quality

# 4. Run tests
make test

# 5. Fix any issues

# 6. Git commit
git add .
git commit -m "feat: Add suggest next sample feature"
```

---

## 🔄 Common Workflows

### Workflow 1: Fix a Bug

```bash
# 1. Identify: Is it CLI or API?
#    - If CLI output wrong → CLI code
#    - If HTTP response wrong → API code

# 2. Write minimal test case
python -c "
from samplemind.core.engine import AudioEngine
engine = AudioEngine()
result = engine.analyze('sample.wav')
print(result)  # See if bug reproduces
"

# 3. Add debug print statements
# In code: print(f"DEBUG: variable = {variable}")

# 4. Run with debugger (F5)

# 5. Step through code

# 6. Identify root cause

# 7. Fix code

# 8. Test fix

# 9. Remove debug prints

# 10. Commit
git add .
git commit -m "fix: Correct bug in feature X"
```

### Workflow 2: Add AI Feature

```bash
# 1. Set up Gemini/Claude API key
export GOOGLE_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# 2. Write AI function
# src/samplemind/ai/suggestions.py

def get_ai_suggestion(analysis: dict) -> str:
    import google.generativeai as genai
    # Use Gemini to generate suggestion
    # (See AI_INTEGRATION_SETUP.md)

# 3. Test AI function
python -c "
from samplemind.ai.suggestions import get_ai_suggestion
result = get_ai_suggestion({'tempo': 120, 'key': 'C'})
print(result)
"

# 4. Integrate into API
# In route: response = get_ai_suggestion(...)

# 5. Test from CLI
python main.py (command that uses AI)

# 6. Handle errors gracefully
# - API key missing
# - API timeout
# - Invalid response

# 7. Add caching to avoid repeated calls
```

### Workflow 3: Database Changes

```bash
# 1. Design schema change
# Example: Add "bpm" field to Sample model

# 2. Update Pydantic model
# src/samplemind/core/database/models.py
class Sample(BaseModel):
    # ... existing fields ...
    bpm: float  # New field

# 3. Update MongoDB collection
# Option A: Manual
docker exec samplemind-mongodb mongosh << 'EOF'
db.samples.updateMany({}, {$set: {bpm: 120}})
EOF

# Option B: Auto-migrate
# Create migration script in src/migrations/

# 4. Test with query
docker exec samplemind-mongodb mongosh << 'EOF'
db.samples.findOne()
EOF

# 5. Update any code that reads this field

# 6. Test API endpoint

# 7. Test CLI that uses this data

# 8. Verify with other services
# - Cache needs invalidation?
# - Vector DB needs update?
```

### Workflow 4: Performance Optimization

```bash
# 1. Identify slow operation
# - Check API logs for slow requests
# - Time CLI commands
# - Use profiler

# 2. Profile the code
python -m cProfile -s cumulative main.py analyze sample.wav > profile.txt
# View: less profile.txt

# 3. Find bottleneck
# - Which function takes most time?
# - Which library call is slow?

# 4. Optimize
# Options:
# - Caching results
# - Parallel processing
# - Algorithm improvement
# - Database indexing

# 5. Benchmark before/after
time python main.py analyze sample.wav  # Before
# ... apply optimization ...
time python main.py analyze sample.wav  # After

# 6. Verify improvement is significant

# 7. Commit optimization
```

---

## 🔧 Useful Commands

### Starting/Stopping Services

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (fresh database)
docker compose down -v

# Restart specific service
docker compose restart samplemind-api

# View status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Viewing Logs

```bash
# Real-time API logs
docker logs samplemind-api -f

# Last 100 lines
docker logs samplemind-api --tail 100

# All service logs
docker compose logs -f

# Search logs for errors
docker logs samplemind-api 2>&1 | grep -i error

# Timestamps
docker logs samplemind-api -t
```

### Development Commands

```bash
# Run tests
make test

# Run specific test
pytest tests/unit/cli/test_analyze.py

# Format code
make format

# Lint code
make lint

# Full quality check
make quality

# Install dependencies
poetry install

# Run CLI
python main.py

# Watch specific file changes
watchmedo auto-restart -d src/ -- python main.py
```

### Database Operations

```bash
# MongoDB
docker exec samplemind-mongodb mongosh

# List databases
> show dbs

# Use database
> use samplemind

# List collections
> show collections

# Find documents
> db.samples.find().limit(5)

# PostgreSQL
docker exec -it samplemind-postgres psql -U samplemind -d samplemind

# List tables
\dt

# Query
SELECT * FROM samples LIMIT 5;

# Redis
docker exec samplemind-redis redis-cli

# Get key
GET key_name

# List all keys
KEYS *
```

### Troubleshooting

```bash
# Container won't start
docker logs samplemind-api
docker compose logs samplemind-api

# Can't connect to database
docker exec samplemind-mongodb mongosh --eval "db.adminCommand('ping')"

# Port already in use
lsof -i :8000  # See what's using port 8000
kill -9 <PID>

# Clear Docker cache
docker system prune
docker system prune -a  # More aggressive

# Rebuild everything fresh
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Start development | `docker compose up -d && code .` |
| Run CLI | `python main.py` |
| Debug CLI | `F5` → Select CLI configuration |
| Test API | Thunder Client (Ctrl+Shift+D) |
| View API logs | `docker logs samplemind-api -f` |
| Format code | `make format` |
| Run tests | `make test` |
| Fix all issues | `make quality` |
| Database query | `docker exec samplemind-mongodb mongosh` |
| Reset database | `docker compose down -v` |
| Check status | `docker ps` |

---

## 💡 Best Practices

✓ **Always start Docker first** - Everything depends on backend services
✓ **Watch logs while testing** - `docker logs -f` catches issues
✓ **Use breakpoints** - More efficient than print statements
✓ **Test small** - Test one endpoint, then integrate with CLI
✓ **Commit frequently** - Small, focused commits
✓ **Use branches** - Create feature branch for each feature
✓ **Run quality checks** - `make quality` before committing
✓ **Document complex logic** - Leave comments for future you
✓ **Test error cases** - Not just happy path
✓ **Monitor performance** - Track slow queries/endpoints

---

Keep coding! This hybrid workflow gives you the best of both worlds! 🚀
