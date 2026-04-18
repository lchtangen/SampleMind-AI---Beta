---
name: celery-tasks
description: Guide for creating and managing Celery background tasks. Use when implementing async task queues for heavy processing.
---

## Celery Task Development

### Configuration
- **App:** `src/samplemind/core/tasks/celery_app.py`
- **Audio tasks:** `src/samplemind/core/tasks/audio_tasks.py`
- **Agent tasks:** `src/samplemind/core/tasks/agent_tasks.py`
- **Broker:** Redis at `redis://localhost:6379/0`

### Task Pattern
```python
from samplemind.core.tasks.celery_app import celery_app

@celery_app.task(bind=True, name="samplemind.tasks.my_task")
def my_task(self, file_path: str) -> dict:
    self.update_state(state="PROGRESS", meta={"pct": 25})
    # ... processing ...
    self.update_state(state="PROGRESS", meta={"pct": 75})
    return {"result": "done"}
```

### Running Celery
```bash
# Start worker
celery -A samplemind.core.tasks.celery_app worker --loglevel=info

# Start beat (scheduled tasks)
celery -A samplemind.core.tasks.celery_app beat --loglevel=info
```

### Rules
- Always use `bind=True` for self access
- Report progress with `self.update_state()`
- Use explicit `name=` for task discovery
- Handle failures with `self.retry(max_retries=3)`
