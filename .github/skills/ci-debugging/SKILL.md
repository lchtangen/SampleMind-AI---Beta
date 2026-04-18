---
name: ci-debugging
description: Guide for debugging failing GitHub Actions workflows. Use when asked to debug CI/CD failures.
allowed-tools: shell
---

## CI/CD Failure Debugging

To debug failing GitHub Actions workflows:

1. **Check workflow runs** — Use `list_workflow_runs` to see recent runs and status
2. **Get failure summaries** — Use `summarize_job_log_failures` for AI-powered failure analysis
3. **Get detailed logs** — Use `get_job_logs` or `get_workflow_run_logs` for full output
4. **Reproduce locally** — Try to reproduce the failure in your environment
5. **Fix and verify** — Make the fix and ensure it passes before committing

### Common Failure Patterns

#### Python CI (`backend-ci.yml`)
```bash
# Lint failures
ruff check src/
ruff format --check src/

# Type check failures
mypy src/

# Test failures
pytest tests/unit/ -v --tb=short
```

#### Frontend CI (`frontend-ci.yml`)
```bash
cd apps/web
npm install --legacy-peer-deps
npm run lint
npm run build
```

### Quick Fixes
- **Import order:** `ruff check --fix src/`
- **Formatting:** `ruff format src/`
- **Missing types:** Add type annotations
- **Peer dep errors:** Use `--legacy-peer-deps` flag
