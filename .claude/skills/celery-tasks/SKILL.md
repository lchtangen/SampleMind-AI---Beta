---
name: celery-tasks
description: Celery background tasks with Redis broker and progress tracking
---

## Celery Tasks

### Location
- App: `src/samplemind/core/tasks/celery_app.py`
- Audio tasks: `core/tasks/audio_tasks.py`
- Agent tasks: `core/tasks/agent_tasks.py`

### Broker
Redis at `redis://localhost:6379/0`

### Task Pattern
```python
from samplemind.core.tasks.celery_app import celery_app

@celery_app.task(bind=True, name="samplemind.tasks.analyze_audio")
def analyze_audio(self, file_path: str) -> dict:
    self.update_state(state="PROGRESS", meta={"pct": 0, "step": "Loading"})

    # Process...
    self.update_state(state="PROGRESS", meta={"pct": 50, "step": "Analyzing"})

    # Complete
    return {"result": "done", "bpm": 140.0}
```

### Rules
- Always use `bind=True` for access to `self.update_state()`
- Report progress with `self.update_state(state="PROGRESS", meta={...})`
- Use explicit `name=` for task discovery across modules
- Handle failures with `self.retry()` and `max_retries`
- Use for heavy processing (>1s) — use `BackgroundTasks` for quick work
