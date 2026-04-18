---
applyTo: "**/*.yml,**/*.yaml"
excludeAgent: "code-review"
---

# CI/CD & YAML Instructions

- GitHub Actions workflows: `.github/workflows/`
  - `backend-ci.yml` — Python lint (ruff), format check, mypy, pytest
  - `frontend-ci.yml` — Next.js lint, type check, build
  - `ci-cd.yml` — Combined pipeline
- Python version: 3.12
- Package manager: uv (for CI), pip/uv (for local dev)
- Node version: 22 (for frontend CI)
- Always use `actions/checkout@v4`, `actions/setup-python@v5`, `astral-sh/setup-uv@v4`
- Docker: `docker-compose.yml` for local dev, `docker-compose.v3.yml` for production
- Dockerfile uses multi-stage build with Python 3.12-slim
