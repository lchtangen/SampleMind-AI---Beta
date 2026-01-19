# Celery Quick Start Guide

## Starting the System

### 1. Start Redis (if not running)
```bash
# Using Docker Compose
docker-compose up -d redis

# Or check if running
redis-cli ping
```

### 2. Start Components

#### Option A: All in separate terminals
```bash
# Terminal 1: API Server
./start_api.sh

# Terminal 2: Celery Worker
./start_celery_worker.sh

# Terminal 3: Celery Beat (optional - for periodic tasks)
./start_celery_beat.sh

# Terminal 4: Flower UI (optional - for monitoring)
./start_flower.sh
# Then open http://localhost:5555
```

#### Option B: Using process manager
```bash
# Using tmux
tmux new-session -d -s samplemind './start_api.sh'
tmux split-window -h './start_celery_worker.sh'
tmux split-window -v './start_flower.sh'
tmux attach -t samplemind
```

## Testing Tasks

### 1. Register and Login
```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@samplemind.ai",
    "username": "testuser",
    "password": "TestPass123"
  }'

# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@samplemind.ai&password=TestPass123" \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Submit Analysis Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "test-audio-001",
    "file_path": "/path/to/test.wav",
    "analysis_options": {"ai_provider": "google_ai"}
  }' | jq

# Save task_id from response
TASK_ID="your-task-id-here"
```

### 3. Check Task Status
```bash
# Check status (repeat until SUCCESS)
curl -X GET "http://localhost:8000/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

# Watch status (auto-refresh)
watch -n 2 "curl -s -X GET 'http://localhost:8000/api/v1/tasks/$TASK_ID' \
  -H 'Authorization: Bearer $TOKEN' | jq '.status, .progress, .progress_message'"
```

### 4. Monitor Workers
```bash
# Via API
curl -X GET http://localhost:8000/api/v1/tasks/workers/status \
  -H "Authorization: Bearer $TOKEN" | jq

# Via Flower UI
open http://localhost:5555

# Via Celery CLI
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect active
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect stats
```

### 5. Check Queue Stats
```bash
curl -X GET http://localhost:8000/api/v1/tasks/queues/stats \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Common Commands

### Celery Worker
```bash
# Start worker
./start_celery_worker.sh

# Start with specific queue
.venv/bin/celery -A samplemind.core.tasks.celery_app worker \
  --queues=audio_processing

# Start with more concurrency
.venv/bin/celery -A samplemind.core.tasks.celery_app worker \
  --concurrency=8

# Enable debug logging
.venv/bin/celery -A samplemind.core.tasks.celery_app worker \
  --loglevel=debug
```

### Celery Inspect
```bash
# List active tasks
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect active

# List registered tasks
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect registered

# Worker stats
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect stats

# Check scheduled tasks
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect scheduled
```

### Celery Control
```bash
# Shutdown workers
.venv/bin/celery -A samplemind.core.tasks.celery_app control shutdown

# Enable/disable event monitoring
.venv/bin/celery -A samplemind.core.tasks.celery_app control enable_events
.venv/bin/celery -A samplemind.core.tasks.celery_app control disable_events

# Set worker concurrency
.venv/bin/celery -A samplemind.core.tasks.celery_app control pool_grow 2
.venv/bin/celery -A samplemind.core.tasks.celery_app control pool_shrink 1
```

### Flower Monitoring
```bash
# Start Flower
./start_flower.sh

# Custom port
.venv/bin/celery -A samplemind.core.tasks.celery_app flower --port=8080

# With basic auth
.venv/bin/celery -A samplemind.core.tasks.celery_app flower \
  --basic_auth=admin:password
```

## Troubleshooting

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Check Redis info
redis-cli info server

# Test connection with Python
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

### Worker Not Picking Up Tasks
```bash
# Check worker is running
ps aux | grep celery

# Check worker logs
# (look at terminal output)

# Verify task routing
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect registered

# Check queue has messages
redis-cli LLEN celery  # default queue
redis-cli LLEN audio_processing
```

### Task Stuck in PENDING
```bash
# Check worker is consuming from correct queue
.venv/bin/celery -A samplemind.core.tasks.celery_app inspect active_queues

# Verify task was sent to correct queue
# (check API logs)

# Restart worker
# Ctrl+C in worker terminal, then ./start_celery_worker.sh
```

### Clear All Tasks
```bash
# Purge all pending tasks (careful!)
.venv/bin/celery -A samplemind.core.tasks.celery_app purge

# Clear specific queue
redis-cli DEL audio_processing

# Clear result backend
redis-cli FLUSHDB  # WARNING: Clears entire Redis database
```

## Task States

- **PENDING**: Task waiting for execution
- **STARTED**: Task has started  
- **PROGRESS**: Task is running (custom state)
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed
- **RETRY**: Task is being retried
- **REVOKED**: Task was cancelled

## Environment Variables

Add to `.env`:
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Task Settings
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3000
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CELERY_WORKER_MAX_TASKS_PER_CHILD=100

# Monitoring
FLOWER_PORT=5555
FLOWER_PERSISTENT=True
```

## Production Deployment

### Using Supervisor
```ini
[program:samplemind-celery-worker]
command=/path/to/.venv/bin/celery -A samplemind.core.tasks.celery_app worker --loglevel=info
directory=/path/to/samplemind-ai-v6
user=samplemind
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stdout_logfile=/var/log/samplemind/celery-worker.log
stderr_logfile=/var/log/samplemind/celery-worker-error.log
```

### Using systemd
```ini
[Unit]
Description=Celery Worker for SampleMind AI
After=network.target redis.service

[Service]
Type=forking
User=samplemind
Group=samplemind
WorkingDirectory=/path/to/samplemind-ai-v6
Environment="PYTHONPATH=/path/to/samplemind-ai-v6/src"
ExecStart=/path/to/.venv/bin/celery -A samplemind.core.tasks.celery_app worker \
  --detach --loglevel=info --logfile=/var/log/samplemind/celery.log
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Compose
```yaml
celery-worker:
  build: .
  command: celery -A samplemind.core.tasks.celery_app worker --loglevel=info
  depends_on:
    - redis
    - mongodb
  environment:
    - REDIS_URL=redis://redis:6379/0
    - MONGODB_URL=mongodb://mongodb:27017
  volumes:
    - ./data:/app/data
  restart: unless-stopped
```

## Next Steps

- ✅ Celery workers running
- ✅ Tasks submitting and processing
- ✅ Monitoring via Flower
- → Move to frontend development (Task 5)

## Resources

- Celery Documentation: https://docs.celeryq.dev/
- Flower Documentation: https://flower.readthedocs.io/
- Redis Documentation: https://redis.io/docs/
- FastAPI + Celery: https://fastapi.tiangolo.com/tutorial/background-tasks/
