---
name: pytest-testing
description: Guide for writing pytest tests in SampleMind. Use when creating or debugging tests.
---

## Pytest Testing Guide

### Run Tests
```bash
# All tests
pytest tests/unit/ -v --tb=short

# Specific file
pytest tests/unit/test_realtime_effects.py -v

# With coverage
pytest tests/unit/ -v --cov=src/samplemind --cov-report=term-missing

# Single test
pytest tests/unit/test_agent_memory.py::TestAgentMemory::test_store -v
```

### Test File Template
```python
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

class TestMyFeature:
    @pytest.fixture
    def setup(self):
        return {"key": "value"}

    def test_basic(self, setup):
        assert setup["key"] == "value"

    @pytest.mark.asyncio
    async def test_async_feature(self):
        result = await some_async_function()
        assert result is not None
```

### Mocking Patterns
- Mock AI providers: `patch("samplemind.integrations.litellm_router.chat_completion")`
- Mock FAISS: `MagicMock(spec=faiss.IndexFlatIP)`
- Mock heavy libs in conftest: `sys.modules` patching for torch, transformers, librosa
- Use `AsyncMock` for async function mocking

### Key Config
- `conftest.py` at repo root — global fixtures and heavy lib mocks
- `tests/fixtures/` — reusable test data
