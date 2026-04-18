---
name: docker-deployment
description: Guide for Docker containerization and deployment. Use when building or modifying Docker configurations.
---

## Docker Deployment

### Files
- `Dockerfile` — Multi-stage Python 3.12-slim build
- `docker-compose.yml` — Local development
- `docker-compose.v3.yml` — Production deployment
- `.devcontainer/devcontainer.json` — VS Code DevContainer

### Local Development
```bash
docker-compose up -d        # Start all services
docker-compose logs -f app  # View logs
docker-compose down         # Stop all
```

### Production
```bash
docker-compose -f docker-compose.v3.yml up -d
```

### Services
- **app** — FastAPI backend (port 8000)
- **redis** — Session cache + Celery broker (port 6379)
- **postgres** — Production database (port 5432)
- **celery-worker** — Background task processing
- **celery-beat** — Scheduled tasks

### DevContainer
- Python 3.12 + Node 22
- Ports: 8000, 8080, 11434
- Extensions: ms-python.python, charliermarsh.ruff
