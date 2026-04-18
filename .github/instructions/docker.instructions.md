---
applyTo: "Dockerfile,docker-compose*.yml,.devcontainer/**"
---

# Docker & DevContainer Instructions

- Dockerfile: Multi-stage build with `python:3.12-slim`
- docker-compose.yml: Local development (app + Redis + Postgres)
- docker-compose.v3.yml: Production deployment
- DevContainer: `.devcontainer/devcontainer.json` — Python 3.12 + Node 22
- Forward ports: 8000 (FastAPI), 8080 (alternate), 11434 (Ollama)
- Install: `pip install -e '.[dev]'` in post-create command
- Include extensions: ms-python.python, charliermarsh.ruff, ms-python.mypy-type-checker
