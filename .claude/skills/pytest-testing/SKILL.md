---
name: pytest-testing
description: pytest testing with mocked AI, FAISS, and heavy library dependencies
---

## Testing with pytest

### Commands
```bash
pytest tests/unit/ -v --tb=short                    # Run tests
pytest tests/unit/ -v --cov=src/samplemind           # With coverage
```

### Mock Requirements
Always mock — never make real calls:
- AI: anthropic, openai, google-genai, ollama, litellm
- FAISS: `MagicMock` for `faiss.IndexFlatIP`
- Heavy libs: torch, transformers, librosa, demucs, soundfile
- External: Supabase, Stripe, Redis, R2/S3

### Pattern
```python
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.fixture
def mock_litellm():
    with patch("samplemind.integrations.litellm_router.chat_completion") as m:
        m.return_value = AsyncMock(return_value={"choices": [...]})
        yield m

@pytest.mark.asyncio
async def test_analysis(mock_litellm):
    result = await analyze(...)
    assert result.bpm == 140.0  # Assert specific values
```

### Rules
- Test files: `tests/unit/test_<module>.py`
- Fixtures in `tests/fixtures/` and `conftest.py`
- `@pytest.mark.asyncio` for async tests
- Assert specific values, not just `is not None`
- Test edge cases: empty inputs, invalid types, boundaries
- Do not remove existing tests
- Coverage target: 30% → 50%
