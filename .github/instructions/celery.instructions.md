---
applyTo: "src/samplemind/core/tasks/**/*.py"
---

# Celery Task Instructions

- Celery app: `core/tasks/celery_app.py`
- Audio tasks: `core/tasks/audio_tasks.py`
- Agent tasks: `core/tasks/agent_tasks.py` (wraps LangGraph)
- Broker: Redis at `redis://localhost:6379/0`
- Task pattern:
  ```python
  @celery_app.task(bind=True, name="samplemind.tasks.my_task")
  def my_task(self, file_path: str) -> dict:
      self.update_state(state="PROGRESS", meta={"pct": 50})
      return {"result": "done"}
  ```
- Always use `bind=True` for access to `self.update_state()`
- Report progress with `self.update_state(state="PROGRESS", meta={...})`
- Use explicit `name=` for task discovery across modules
- Handle task failures with `self.retry()` and `max_retries`
