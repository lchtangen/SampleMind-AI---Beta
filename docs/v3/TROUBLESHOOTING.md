# Troubleshooting Guide — SampleMind AI

Common issues and solutions for development, deployment, and production.

## Startup Issues

### Issue: Port 8000 Already in Use

**Error:** `Address already in use: ('127.0.0.1', 8000)`

**Solution 1:** Kill existing process
```bash
lsof -i :8000  # Find process using port 8000
kill -9 <PID>
python main.py
```

**Solution 2:** Use different port
```bash
python main.py --port 9000
# Or set environment variable
PORT=9000 python main.py
```

---

### Issue: ModuleNotFoundError: No module named 'samplemind'

**Error:** Imports fail: `from samplemind.core import ...`

**Solution 1:** Install in development mode
```bash
cd /path/to/SampleMind-AI---Beta
pip install -e .
```

**Solution 2:** Verify Python path
```bash
python -c "import sys; print('\n'.join(sys.path))"
# Should include: /path/to/SampleMind-AI---Beta
```

**Solution 3:** Check virtual environment
```bash
which python  # Should show .venv/bin/python
source .venv/bin/activate
pip install -e .[dev]
```

---

### Issue: No Module Named 'faiss'

**Error:** `ModuleNotFoundError: No module named 'faiss'`

**Solution 1:** Install FAISS
```bash
pip install faiss-cpu  # CPU version (smaller)
# OR
pip install faiss-gpu  # GPU version (requires CUDA)
```

**Solution 2:** Verify installation
```bash
python -c "import faiss; print(f'FAISS version: {faiss.__version__}')"
```

---

### Issue: CUDA/GPU Not Available

**Error:** FAISS or PyTorch complaining about GPU

**Solution 1:** Use CPU version
```bash
pip uninstall torch faiss-gpu
pip install torch  # Default is CPU
pip install faiss-cpu
```

**Solution 2:** Check GPU availability
```bash
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"
```

---

## API Started But Endpoints Return 503

### Issue: Redis Connection Failed

**Error:** `GET /health/deps` shows Redis unavailable

**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should print: PONG

# If not running, start Redis
docker run -d -p 6379:6379 redis:latest

# Or via Homebrew
brew services start redis
```

---

### Issue: MongoDB Connection Failed

**Error:** `GET /health/deps` shows MongoDB unavailable

**Solution:**
```bash
# Check MongoDB
mongosh  # If installed locally
# Or use Docker
docker run -d -p 27017:27017 mongo:latest

# Verify connection
python -c "from samplemind.integrations.mongodb_client import client; print(client.server_info())"
```

---

### Issue: FAISS Index Empty/Not Available

**Error:** `Get /api/v1/search/faiss` returns empty results

**Solution:**
```bash
# Check index status
samplemind index status

# Rebuild index from audio files
samplemind index rebuild ~/Music/samples/

# Verify index created
ls -lh ~/.samplemind/faiss/
# Should show: index.bin, metadata.json
```

---

### Issue: AI Provider API Keys Missing

**Error:** All AI responses fail, fallback to Ollama

**Solution 1:** Set API keys
```bash
export ANTHROPIC_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export OPENAI_API_KEY="sk-..."
python main.py
```

**Solution 2:** Use .env file
```bash
# Create .env in project root
ANTHROPIC_API_KEY=sk-...
GEMINI_API_KEY=...
OPENAI_API_KEY=sk-...

# Load it
source .env
python main.py
```

**Solution 3:** Use Ollama (offline)
```bash
# Install Ollama: https://ollama.ai
ollama pull qwen2.5-coder:7b
ollama serve  # Runs on localhost:11434

# SampleMind will auto-fallback to Ollama if API keys missing
```

---

## Test Execution Issues

### Issue: Tests Timeout or Hang

**Error:** Tests hang after 30s, timeout

**Causes:** ML models or audio files loading slowly

**Solution 1:** Run fast tests only
```bash
pytest tests/unit/test_exceptions.py -v  # Should be instant
pytest tests/unit/test_health.py -v
```

**Solution 2:** Increase timeout
```bash
pytest --tb=short --timeout=120  # 120 second timeout
```

**Solution 3:** Skip slow tests
```bash
pytest -m "not slow" tests/unit/
```

---

### Issue: Test Fails with `ImportError`

**Error:** Test imports fail but manual import works

**Solution:**
```bash
# Ensure venv is active
.venv/bin/python -m pytest tests/unit/test_file.py

# Not this:
pytest tests/unit/test_file.py  # May use system Python
```

---

### Issue: `pytest: command not found`

**Error:** pytest not installed

**Solution:**
```bash
# Install dev dependencies
pip install -e .[dev]

# Or directly
pip install pytest pytest-asyncio

# Now try
pytest tests/unit/ -v
```

---

## Performance Issues

### Issue: API Responses Slow (>5s)

**Diagnosis:** Check where time is spent
```bash
# Add timing logs
export LOG_LEVEL=DEBUG
python main.py

# Curl endpoint with timing
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/api/v1/analyze
```

**Causes & Solutions:**

1. **FAISS index slow** — Index too large
   ```bash
   # Rebuild with subset
   samplemind index rebuild ~/samples/ --limit 10000
   ```

2. **AI API slow** — Network/API latency
   ```bash
   # Try faster provider
   # Modify: PREFER_FAST=true
   export LITELLM_PREFER_FAST=true  # Uses Gemini Flash
   ```

3. **Audio processing slow** — Large file
   ```bash
   # Limit duration
   samplemind analyze file.wav --duration 30  # seconds
   ```

---

### Issue: High Memory Usage (>2GB)

**Cause:** Models not unloaded

**Solution:**
```bash
# Explicitly offload GPU memory
python -c "import torch; torch.cuda.empty_cache()"

# Or restart service
systemctl restart samplemind  # If using systemd
```

---

## Deployment Issues

### Issue: Docker Build Fails

**Error:** `ERROR: failed to build image`

**Solution:**
```bash
# Check Dockerfile
cat Dockerfile | head -20

# Build with debug output
docker build -t samplemind:latest . --progress=plain

# Check for common issues
docker build --no-cache .  # Ignore cached layers
```

---

### Issue: API Crashes After Deploy

**Error:** Service keeps restarting

**Solution 1:** Check logs
```bash
docker logs samplemind-api -f  # Follow logs

# Or if using systemd
journalctl -u samplemind -f
```

**Solution 2:** Run health check
```bash
curl http://localhost:8000/health
# If 503: dependency missing
curl http://localhost:8000/health/deps
```

**Solution 3:** Check database migrations
```bash
# Run migrations
python -m aerich upgrade

# Or reset (destructive)
python -m aerich downgrade
```

---

### Issue: Database Connection String Wrong

**Error:** `Failed to connect to MongoDB` or similar

**Solution 1:** Verify connection string
```bash
# Check environment variable
echo $MONGODB_URI

# Test connection
mongosh $MONGODB_URI  # If using MongoDB

# Expected format
mongodb://username:password@host:27017/dbname
```

**Solution 2:** Update connection string
```bash
export MONGODB_URI="mongodb://localhost:27017/samplemind"
python main.py
```

---

## Development Workflow Issues

### Issue: Changes Not Reflected After Edit

**Error:** Edit Python file, but old code still runs

**Causes:**
1. Python bytecode cached
2. Venv not reactivated
3. Module not reloaded

**Solutions:**
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Restart service
pkill -f "python main.py"
python main.py

# Or if using auto-reload
# Already works if running: uvicorn main:app --reload
```

---

### Issue: Type Hints Not Caught by MyPy

**Error:** MyPy passes but code has runtime type errors

**Solution 1:** Check mypy config
```bash
cat pyproject.toml | grep -A 10 "\[tool.mypy\]"
# Ensure: strict = true
```

**Solution 2:** Run strict mypy
```bash
mypy src/ --strict
```

**Solution 3:** Add type hints
```python
# ❌ Before (mypy may miss)
def process(data):
    return data

# ✅ After (mypy catches)
def process(data: dict[str, Any]) -> dict[str, Any]:
    return data
```

---

### Issue: Linting Errors Not Auto-Fixed

**Error:** Ruff reports errors but `--fix` doesn't fix them

**Solution 1:** Check error type
```bash
ruff check . --statistics
# Some errors can't auto-fix (code logic errors)
```

**Solution 2:** Fix manually
```python
# Some require manual fixes
# E.g., shadowed variables, unused imports that are intentional
```

**Solution 3:** Ignore specific errors
```bash
# In pyproject.toml
[tool.ruff]
ignore = ["E501"]  # Ignore line too long
```

---

## Debugging Tips

### Add Debug Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Variable value: %s", variable)
logger.debug("Request: %s", request.dict())
```

### Use Python Debugger

```python
import pdb

@app.get("/endpoint")
def endpoint():
    pdb.set_trace()  # Debugger will pause here
    # Type 'n' to step next, 'c' to continue, 'q' to quit
    process_data()
```

### Use IDE Debugger

- **VS Code:** Install Python extension, click "Debug" on line
- **PyCharm:** Right-click test, select "Debug"
- **IDE Debugging:** Set breakpoints and Run → Debug

### Check Request/Response

```bash
# See full request/response
curl -v http://localhost:8000/api/endpoint
# Includes headers, timing, all details

# Pretty-print JSON
curl http://localhost:8000/api/endpoint | jq .

# Save response to file
curl http://localhost:8000/api/endpoint > response.json
```

---

## Getting Help

If you still can't solve it:

1. **Check logs** — Most info is in logs
   ```bash
   grep "ERROR\|CRITICAL" logs/*.log
   ```

2. **Search GitHub Issues** — Others may have same problem
   ```bash
   site:github.com/owner/SampleMind issue
   ```

3. **Post detailed error report**
   ```bash
   # Collect diagnostics
   python -c "import sys; print(sys.version)"  # Python version
   pip list | grep -E "faiss|torch|fastapi"    # Key packages
   python main.py 2>&1 | head -50              # Startup output
   ```

4. **Contact Support** — With diagnostics attached

---

## Quick Reference: Health Checks

```bash
# Full system status
curl http://localhost:8000/health/deps

# Just API health
curl http://localhost:8000/health

# With verbose output
curl -v http://localhost:8000/health/ready

# Check specific services
curl http://localhost:8000/health/deps | jq .
{
  "status": "ok",
  "redis": "connected",
  "mongodb": "connected", 
  "faiss": "ready",
  "ai_providers": "ok"
}
```

---

## See Also

- **Setup Guide:** See `SETUP_LOCAL.md`
- **Error Handling:** See `ERROR_HANDLING_GUIDE.md`
- **Architecture:** See `ARCHITECTURE.md`
