Run the SampleMind test suite:

```bash
pytest tests/unit/ -v --tb=short --cov=src/samplemind --cov-report=term-missing
```

Summarize results: total tests, passed, failed, coverage percentage.
If any tests fail, analyze the failures and suggest fixes.
