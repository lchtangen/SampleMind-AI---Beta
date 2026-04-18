---
name: ci-debugging
description: Debug GitHub Actions CI failures for backend and frontend pipelines
---

## CI/CD Debugging

### Workflow Files
- `backend-ci.yml` — Python lint (ruff), format check, mypy, pytest
- `frontend-ci.yml` — Next.js lint, type check, build
- `ci-cd.yml` — Combined pipeline

### Backend CI Steps
1. `ruff check src/` — linting
2. `ruff format --check src/` — format verification
3. `mypy src/` — type checking
4. `pytest tests/unit/ -v --tb=short` — unit tests

### Frontend CI Steps
1. `npm install --legacy-peer-deps`
2. `npm run lint` — ESLint
3. `tsc --noEmit` — type check
4. `npm run build` — production build

### Reproduce Locally
```bash
# Backend
ruff check src/ && ruff format --check src/ && mypy src/ && pytest tests/unit/ -v --tb=short

# Frontend
cd apps/web && npm install --legacy-peer-deps && npm run lint && npm run build
```

### Common Failures
- Missing type annotations → add types, run `mypy src/`
- Import ordering → run `ruff check src/ --fix`
- Peer dep conflicts → use `--legacy-peer-deps`
- CI env: Python 3.12, Node 22, uv for package management
