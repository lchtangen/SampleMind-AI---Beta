---
applyTo: "tests/**/*.py"
---

# Testing Instructions

- Framework: pytest with fixtures in `tests/fixtures/`
- Run: `pytest tests/unit/ -v --tb=short`
- Coverage: `pytest tests/unit/ -v --cov=src/samplemind --cov-report=term-missing`
- Always mock AI providers (anthropic, openai, google-genai, ollama) — never make real API calls
- Always mock FAISS index operations — use `MagicMock` for `faiss.IndexFlatIP`
- Always mock heavy libraries in conftest: `torch`, `transformers`, `librosa`, `demucs`
- Use `@pytest.fixture` for reusable test setup
- Use `pytest.mark.asyncio` for async test functions
- Test files: `tests/unit/test_<module_name>.py`
- Assert specific values, not just `is not None`
- Test edge cases: empty inputs, invalid types, boundary values
- Do not remove or modify existing tests unless they test removed functionality
