---
name: docker-deployment
description: Docker multi-stage builds with python:3.12-slim for SampleMind
---

## Docker Deployment

### Files
- `Dockerfile` — Multi-stage build with `python:3.12-slim`
- `docker-compose.yml` — Local development
- `docker-compose.v3.yml` — Production deployment

### Port Mapping
| Service | Port |
|---------|------|
| FastAPI | 8000 |
| Next.js | 3000 |
| Ollama | 11434 |
| Redis | 6379 |
| PostgreSQL | 5432 |

### Commands
```bash
docker-compose up -d                              # Local dev
docker-compose -f docker-compose.v3.yml up -d     # Production
docker-compose -f docker-compose.v3.yml build      # Build production
```

### Best Practices
- Base: `python:3.12-slim` (not full image)
- Multi-stage: deps → build → runtime
- Run as non-root user
- Health checks for all services
- Use .dockerignore to exclude unnecessary files
- Pin versions for reproducibility
- DevContainer: `.devcontainer/devcontainer.json` (Python 3.12 + Node 22)
