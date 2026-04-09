# SampleMind AI — Comprehensive Testing Guide

**Updated:** April 10, 2026  
**Target:** 50%+ test coverage for CI gate  
**Strategy:** Pyramid approach (unit → integration → E2E)

---

## Quick Start: Run Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src/samplemind --cov-report=term-missing --cov-fail-under=40

# Run specific test file
pytest tests/unit/test_faiss_index.py -v

# Run tests from specific class
pytest tests/unit/test_routes_ai.py::TestAnalyzeEndpoint -v

# Profile slow tests
pytest tests/ --durations=10

# Run with logging output
pytest tests/ -v --log-cli-level=DEBUG
```

---

## Test Structure (Pyramid Approach)

```
                  ▲
                /   \
               / E2E  \           5% — Full workflows (5 tests)
              /―――――――\
             /         \
            / Integration\       30% — Routes + Services (15 tests)
           /―――――――――――――\
          /             \
         / Unit Tests    \      65% — Utilities, Logic (40+ tests)
        /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
```

### Unit Tests (65% of effort)
- **Goal:** 100% coverage of isolated functions
- **What:** Single function/method, all code paths
- **Fixtures:** Mocks, stubs, minimal setup
- **Files:** 40+ unit test files

### Integration Tests (30% of effort)
- **Goal:** 70% coverage of route handlers
- **What:** Route + one layer of dependencies (mocked beyond that)
- **Fixtures:** Real HTTP client, mock external services
- **Files:** 10+ integration test files

### E2E Tests (5% of effort)
- **Goal:** 30% coverage of full workflows
- **What:** Real request → full pipeline → real response
- **Fixtures:** Testcontainers, real Redis, mock files
- **Files:** 3-5 E2E test files

---

## Unit Test Template

```python
# tests/unit/test_my_module.py
import pytest
from unittest.mock import MagicMock, patch
from samplemind.core.module import MyClass, MyFunction

class TestMyFunction:
    """Test suite for standalone functions."""
    
    def test_happy_path(self):
        """Test normal operation with valid inputs."""
        result = MyFunction(valid_arg)
        assert result == expected_value
    
    def test_empty_input(self):
        """Test with empty/None inputs."""
        with pytest.raises(ValueError):
            MyFunction(None)
    
    def test_invalid_type(self):
        """Test with wrong input type."""
        with pytest.raises(TypeError):
            MyFunction(123)  # Expects string


class TestMyClass:
    """Test suite for classes."""
    
    @pytest.fixture
    def instance(self):
        """Create fresh instance for each test."""
        return MyClass()
    
    def test_initialization(self, instance):
        """Test object creation."""
        assert instance is not None
        assert hasattr(instance, 'property')
    
    def test_method_success(self, instance):
        """Test method happy path."""
        result = instance.method(arg)
        assert result == expected
    
    def test_method_with_mock(self):
        """Test method with mocked dependency."""
        mock_dep = MagicMock()
        obj = MyClass(dependency=mock_dep)
        obj.method()
        mock_dep.method.assert_called_once()
```

---

## Integration Test Template

```python
# tests/integration/test_routes_ai.py
import pytest
from httpx import AsyncClient
from samplemind.interfaces.api.main import app

@pytest.mark.asyncio
async def test_analyze_endpoint_success(async_test_client: AsyncClient):
    """Test POST /api/v1/ai/analyze with valid input."""
    with patch("samplemind.core.engine.analyze_audio") as mock_analyze:
        mock_analyze.return_value = {
            "bpm": 128.0,
            "key": "A minor",
            "confidence": 0.95
        }
        
        response = await async_test_client.post(
            "/api/v1/ai/analyze",
            json={"file_path": "/path/to/sample.wav", "analysis_depth": "standard"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["bpm"] == 128.0
        assert data["key"] == "A minor"


@pytest.mark.asyncio
async def test_analyze_endpoint_file_not_found(async_test_client: AsyncClient):
    """Test 404 when file doesn't exist."""
    with patch("samplemind.core.engine.analyze_audio") as mock_analyze:
        mock_analyze.side_effect = FileNotFoundError("File not found")
        
        response = await async_test_client.post(
            "/api/v1/ai/analyze",
            json={"file_path": "/nonexistent.wav"}
        )
        
        assert response.status_code == 400
```

---

## E2E Test Template

```python
# tests/e2e/test_full_workflow.py
@pytest.mark.asyncio
async def test_full_analysis_workflow(async_test_client: AsyncClient, mock_audio_file: Path):
    """Test complete analysis pipeline."""
    # Step 1: Queue task
    response1 = await async_test_client.post(
        "/api/v1/tasks/analyze-agent",
        json={"file_path": str(mock_audio_file), "analysis_depth": "professional"}
    )
    assert response1.status_code == 202
    task_id = response1.json()["task_id"]
    
    # Step 2: Wait for completion
    for i in range(20):
        response2 = await async_test_client.get(f"/api/v1/tasks/{task_id}")
        if response2.json()["status"] == "done":
            break
        await asyncio.sleep(0.5)
    
    # Step 3: Verify results
    assert response2.status_code == 200
    result = response2.json()
    assert result["status"] == "done"
    assert "bpm" in result["result"]
    assert "key" in result["result"]
```

---

## Priority Unit Test Files (High ROI)

### 1. tests/unit/test_faiss_index.py
**Coverage target:** 100% (core search logic)

```python
class TestFAISSIndex:
    def test_build_index_creates_index(self):
        """Index building creates valid FAISS index."""
    
    def test_search_text_returns_results(self):
        """Text search returns N most similar items."""
    
    def test_search_empty_query_error(self):
        """Empty query raises ValueError."""
    
    def test_index_persistence(self):
        """Index can be saved and loaded."""
    
    def test_embedding_generation(self):
        """CLAP embeddings generated correctly."""
```

### 2. tests/unit/test_litellm_router.py
**Coverage target:** 90% (provider fallback)

```python
class TestLiteLLMRouter:
    def test_claude_primary_provider(self):
        """Claude used by default for comprehensive analysis."""
    
    def test_provider_fallback_on_error(self):
        """Falls back to next provider on error."""
    
    def test_ollama_offline_mode(self):
        """Ollama works without API keys."""
    
    def test_caching_works(self):
        """Same query cached, not re-requested."""
```

### 3. tests/unit/test_ensemble_classifier.py
**Coverage target:** 90% (ML logic)

```python
class TestEnsembleClassifier:
    def test_svm_prediction(self):
        """SVM component produces valid predictions."""
    
    def test_xgboost_prediction(self):
        """XGBoost component produces valid predictions."""
    
    def test_voting_logic(self):
        """Soft voting combines predictions correctly."""
    
    def test_confidence_scores(self):
        """Confidence scores in [0, 1] range."""
```

### 4. tests/unit/test_playlist_generator.py
**Coverage target:** 85% (business logic)

```python
class TestPlaylistGenerator:
    def test_energy_arc_ordering(self):
        """Samples ordered by energy arc correctly."""
    
    def test_camelot_wheel_compatibility(self):
        """Compatible keys selected per Camelot."""
    
    def test_duration_constraint(self):
        """Generated playlist <= requested duration."""
```

### 5. tests/unit/test_routes_ai.py
**Coverage target:** 80% (analyze endpoint)

```python
class TestAnalyzeEndpoint:
    def test_analyze_success(self):
        """POST /api/v1/ai/analyze returns analysis."""
    
    def test_analyze_file_not_found(self):
        """Returns 400 when file missing."""
    
    def test_analyze_invalid_format(self):
        """Returns 400 for unsupported format."""
    
    def test_rate_limiting(self):
        """Rate limit applied correctly."""
```

---

## Running Tests Locally Before Commit

### Pre-commit Checklist

```bash
#!/bin/bash
# Run this before committing

echo "🔍 Running quality checks..."
make quality

echo "🧪 Running unit tests..."
pytest tests/unit/ -v --tb=short

echo "📊 Checking coverage..."
pytest tests/unit/ --cov=src/samplemind --cov-fail-under=30 --cov-report=term-missing

echo "✅ All checks passed! Safe to commit."
```

### CI/CD Coverage Gate

Repository CI requires **40% test coverage** on `tests/unit/` subset to merge.

```bash
pytest tests/unit/ --cov=src/samplemind --cov-fail-under=40 --cov-report=term-missing
```

---

## Mock Patterns Reference

### Mock Redis

```python
@pytest_asyncio.fixture
async def mock_redis():
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    return mock

async def test_redis_call(mock_redis):
    await mock_redis.get("key")
    mock_redis.get.assert_called_once_with("key")
```

### Mock HTTP Request

```python
@pytest.mark.asyncio
async def test_api_endpoint(async_test_client):
    response = await async_test_client.post(
        "/api/v1/endpoint",
        json={"param": "value"}
    )
    assert response.status_code == 200
```

### Mock File I/O

```python
def test_file_operations(mock_audio_file):
    # mock_audio_file is a real Path created in temp directory
    assert mock_audio_file.exists()
    with open(mock_audio_file, 'rb') as f:
        data = f.read()
        assert len(data) > 0
```

---

## Troubleshooting

### Problem: "No module named 'samplemind'"

**Solution:** Install in dev mode:
```bash
pip install -e .
```

### Problem: "Failed to import pytest fixtures"

**Solution:** Ensure `tests/conftest.py` exists and contains:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### Problem: "Async test timeout"

**Solution:** Increase timeout in `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_scope = function
timeout = 30
```

---

## Coverage Goals by Phase

| Phase | Unit Target | Integration Target | Total Target |
|-------|-------------|--------------------|--------------|
| After Phase 1 | 30% | 10% | 20% |
| After Phase 2 | 50% | 20% | 40% |
| After Phase 3 | 70% | 40% | 60% |
| After Phase 4 | 85% | 60% | 80% |

---

*Last Updated: April 10, 2026 — Ready for implementation*
