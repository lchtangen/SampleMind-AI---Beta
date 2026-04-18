Start the SampleMind development environment:

For the backend:
```bash
source .venv/bin/activate && uvicorn samplemind.interfaces.api.main:create_app --factory --reload --host 0.0.0.0 --port 8000
```

For the frontend:
```bash
cd apps/web && npm run dev
```

For Docker:
```bash
docker-compose up -d
```

Show which services are running. Use $ARGUMENTS to specify which service (backend, frontend, all, docker).
