Run the full SampleMind quality gate:

1. Python lint: `ruff check src/`
2. Python format check: `ruff format --check src/`
3. Type check: `mypy src/`
4. Unit tests: `pytest tests/unit/ -v --tb=short`

Report results for each step. If any step fails, stop and show the errors.
