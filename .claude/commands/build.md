Build the SampleMind project for production:

Backend:
```bash
ruff check src/ && mypy src/ && pytest tests/unit/ -v --tb=short
```

Frontend:
```bash
cd apps/web && npm install --legacy-peer-deps && npm run build
```

Docker:
```bash
docker-compose -f docker-compose.v3.yml build
```

Use $ARGUMENTS to specify target (backend, frontend, docker, all). Report status.
