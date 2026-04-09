# Error Handling Guide — SampleMind AI

Comprehensive guide to error handling patterns, exception hierarchy, and recovery strategies.

## Exception Hierarchy

All exceptions inherit from `SampleMindError` for unified error handling:

```python
from samplemind.core.exceptions import (
    SampleMindError,           # Base exception
    AudioAnalysisError,        # Audio processing failures
    SearchIndexError,          # FAISS/search failures
    AgentPipelineError,        # LangGraph agent failures
    RateLimitError,            # Rate limit exceeded (429)
    ConfigurationError,        # Invalid configuration
    ValidationError,           # Input validation failures
)
```

## Exception Handling Pattern

### Basic Pattern (All Routes)

```python
from samplemind.core.exceptions import ValidationError, AudioAnalysisError

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """Analyze audio with proper error handling."""
    try:
        # Validate input
        if not request.file_path:
            raise ValidationError("file_path is required")
        
        # Process audio
        result = await engine.analyze(request.file_path)
        
        logger.info(
            "Analysis complete",
            extra={"duration_s": result.duration, "bpm": result.bpm}
        )
        return result
        
    except ValidationError as exc:
        # 400 Bad Request — client error, expected to retry with different parameters
        logger.warning("Invalid parameters", extra={"error": str(exc)})
        raise HTTPException(status_code=400, detail=f"Invalid: {exc}")
        
    except AudioAnalysisError as exc:
        # 500 Internal Server Error — analysis failed, service issue
        logger.error("Analysis failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed")
        
    except TimeoutError as exc:
        # 504 Gateway Timeout — request took too long
        logger.error("Request timeout", exc_info=True)
        raise HTTPException(status_code=504, detail="Request timeout")
        
    except Exception as exc:
        # Catch unexpected errors
        logger.error(
            "Unexpected error",
            extra={"error_type": type(exc).__name__},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
```

## HTTP Status Codes

| Code | Exception | Scenario | Retry? |
|------|-----------|----------|--------|
| 400 | ValidationError | Invalid input parameters | No |
| 401 | Auth | Missing/invalid credentials | Update creds |
| 404 | NotFound | Resource doesn't exist | No |
| 429 | RateLimitError | Rate limit exceeded | Yes (after delay) |
| 500 | Generic Exception | Server error | Yes (exponential backoff) |
| 503 | Service Down | Redis/MongoDB unavailable | Yes (after delay) |
| 504 | TimeoutError | Request took >30s | Yes (with longer timeout) |

## Logging Strategy

### Log Levels

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG: Development debugging
logger.debug("Loading model", extra={"model_name": "claude-sonnet"})

# INFO: Normal operations completing successfully 
logger.info("Analysis complete", extra={"samples_processed": 100})

# WARNING: Expected errors that are recoverable
logger.warning("Fallback to Ollama", extra={"reason": "API key missing"})

# ERROR: Unexpected errors that need attention
logger.error("Database connection failed", exc_info=True)
```

### Structured Logging Pattern

Always include `extra={}` dict for machine-readable context:

```python
# ✅ GOOD — Structured logging
logger.error(
    "Search failed",
    extra={
        "query": "dark trap",
        "index_size": 1000,
        "error_type": type(exc).__name__,
    },
    exc_info=True  # Include stack trace
)

# ❌ BAD — Unstructured logging
logger.error(f"Search failed for query: {query}")
```

## Recovery Strategies

### Automatic Retries

Use for transient failures (network, timeouts):

```python
import asyncio
from functools import wraps

def retry(max_attempts=3, delay=1.0, backoff=2.0):
    """Retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except (TimeoutError, ConnectionError) as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise exc
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} after {current_delay}s",
                        extra={"func": func.__name__, "delay": current_delay}
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1.0, backoff=2.0)
async def call_ai_api(prompt: str):
    """This will retry 3 times on timeout."""
    return await litellm_router.chat_completion(messages=[...])
```

### Graceful Degradation

Fall back to simpler methods when primary fails:

```python
async def analyze_audio(file_path: str):
    """Try advanced analysis, fall back to basic if needed."""
    try:
        # Try PROFESSIONAL analysis (CLAP + Claude)
        return await engine.analyze(
            file_path,
            analysis_level=AnalysisLevel.PROFESSIONAL
        )
    except AgentPipelineError as exc:
        logger.warning("Advanced analysis failed, using DETAILED", exc_info=False)
        
        # Fall back to simpler analysis
        return await engine.analyze(
            file_path,
            analysis_level=AnalysisLevel.DETAILED
        )
    except Exception as exc:
        logger.error("All analysis methods failed", exc_info=True)
        raise AudioAnalysisError(f"Cannot analyze: {exc}")
```

### Circuit Breaker Pattern

Stop calling failing service after N failures:

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds
        self.last_failure_time = None
        self.is_open = False
    
    async def call(self, func, *args, **kwargs):
        # Check if circuit should close after timeout
        if self.is_open:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                logger.info("Circuit breaker closed, retrying")
                self.is_open = False
                self.failure_count = 0
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self.failure_count = 0  # Reset on success
            return result
        except Exception as exc:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                logger.error(
                    f"Circuit breaker opened after {self.failure_count} failures",
                    extra={"func": func.__name__}
                )
            raise exc

# Usage
breaker = CircuitBreaker(failure_threshold=3, timeout=60)
try:
    result = await breaker.call(unreliable_api_call, param1="value")
except Exception:
    logger.error("Service temporarily unavailable, will retry later")
```

## Common Error Scenarios

### Scenario 1: File Not Found

```python
# ❌ Don't do this
try:
    with open(file_path) as f:
        ...
except Exception as exc:
    logger.error("File error")

# ✅ Do this
try:
    with open(file_path) as f:
        ...
except FileNotFoundError as exc:
    raise ValidationError(f"File not found: {file_path}")
except IOError as exc:
    raise AudioAnalysisError(f"Cannot read file: {file_path}")
```

### Scenario 2: Timeout

```python
import asyncio

try:
    # Wrap with timeout
    result = await asyncio.wait_for(
        slow_operation(),
        timeout=30.0  # 30 seconds
    )
except asyncio.TimeoutError:
    logger.error("Operation timeout after 30s")
    raise TimeoutError("Operation exceeded 30s limit")
```

### Scenario 3: Missing Configuration

```python
import os

try:
    api_key = os.environ["ANTHROPIC_API_KEY"]
except KeyError:
    from samplemind.core.exceptions import ConfigurationError
    raise ConfigurationError(
        "ANTHROPIC_API_KEY environment variable not set",
        details={"required_vars": ["ANTHROPIC_API_KEY", "MONGODB_URI"]}
    )
```

## Best Practices

1. **Always catch specific exceptions first, generic last**
   ```python
   except ValidationError as exc:  # Specific
       ...
   except SampleMindError as exc:  # Base class
       ...
   except Exception as exc:        # Generic (last resort)
       ...
   ```

2. **Include stack traces in logs for debugging**
   ```python
   logger.error("Error occurred", exc_info=True)  # Include traceback
   ```

3. **Don't expose internal errors to clients**
   ```python
   # ❌ Don't leak database/API errors
   raise HTTPException(status_code=500, detail=str(db_error))
   
   # ✅ Generic message to client
   raise HTTPException(status_code=500, detail="Internal server error")
   ```

4. **Provide actionable error messages**
   ```python
   # ❌ Not actionable
   raise ValidationError("Invalid value")
   
   # ✅ Actionable
   raise ValidationError(
       "BPM must be between 50 and 200",
       details={"provided": request.bpm, "min": 50, "max": 200}
   )
   ```

5. **Use consistent error format**
   ```python
   # All API errors follow this pattern
   raise HTTPException(
       status_code=400,
       detail="Clear error message"
   )
   ```

## Testing Error Cases

```python
def test_missing_file():
    """Test that missing files raise ValidationError."""
    with pytest.raises(ValidationError):
        analyze_audio("/nonexistent/file.wav")

def test_timeout():
    """Test that long operations timeout."""
    with pytest.raises(TimeoutError):
        asyncio.wait_for(slow_operation(), timeout=0.1)

def test_missing_api_key(monkeypatch):
    """Test that missing config raises ConfigurationError."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        get_ai_provider()
```

## Monitoring & Alerts

### Key Metrics to Monitor

```python
# Error rate > 1% for any endpoint
error_rate = errors_last_5m / requests_last_5m
if error_rate > 0.01:
    alert("High error rate detected")

# P99 latency > 2 seconds
if latency_p99 > 2.0:
    alert("Slow API response")

# Service down > 1 minute
if service_down_duration > 60:
    alert("Service unavailable")
```

### Logging to Observability Platform

```python
import logging
from pythonjsonlogger import jsonlogger

# All logs are structured JSON for easy parsing
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)

logger.addHandler(handler)

# Sends to: Datadog, New Relic, CloudWatch, etc.
```

## See Also

- **API Patterns:** See `API_PATTERNS.md` for endpoint design
- **Architecture:** See `ARCHITECTURE.md` for system overview
- **Local Setup:** See `SETUP_LOCAL.md` for environment setup
