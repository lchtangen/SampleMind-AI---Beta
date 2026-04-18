"""
Celery Application Configuration — SampleMind AI
==================================================

Sets up the Celery distributed task queue used for long-running, CPU-intensive
operations that should not block the FastAPI event loop.

Broker & backend:
  Both default to **Redis** (configurable via ``CELERY_BROKER_URL`` and
  ``CELERY_RESULT_BACKEND`` env vars).

Task routing:
  Tasks are routed to dedicated queues so that I/O-heavy audio processing
  does not starve lightweight AI analysis work:

    ==================  =============================
    Queue               Purpose
    ==================  =============================
    ``default``         catch-all
    ``audio_processing``  ``process_audio_analysis``, ``batch_process_audio_files``
    ``ai_analysis``       agent pipeline tasks
    ``embeddings``        FAISS / CLAP embedding generation
    ==================  =============================

Beat schedule:
  ``cleanup-old-results`` runs every hour to garbage-collect stale task results.

Worker start command::

    celery -A samplemind.core.tasks.celery_app worker -Q default,audio_processing,ai_analysis,embeddings --loglevel=info
"""

import os

from celery import Celery
from kombu import Exchange, Queue

# ── Broker / backend URLs ─────────────────────────────────────────────────────

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# ── App instance ──────────────────────────────────────────────────────────────
# ``include`` lists task modules that Celery will auto-discover on worker start.

celery_app = Celery(
    "samplemind",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "samplemind.core.tasks.audio_tasks",
        "samplemind.core.tasks.agent_tasks",
    ],
)

# ── Core configuration ────────────────────────────────────────────────────────

celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit per task
    task_soft_time_limit=3000,  # 50 min soft limit (raises SoftTimeLimitExceeded)
    task_acks_late=True,  # ack after completion — safer with retries
    worker_prefetch_multiplier=1,  # fetch one task at a time — prevents starvation
    # Result backend settings
    result_expires=3600 * 24,  # Results expire after 24 hours
    result_extended=True,
    # Task routing
    task_default_queue="default",
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("audio_processing", Exchange("audio"), routing_key="audio.process"),
        Queue("ai_analysis", Exchange("ai"), routing_key="ai.analyze"),
        Queue("embeddings", Exchange("embeddings"), routing_key="embeddings.generate"),
    ),
    task_routes={
        "samplemind.core.tasks.audio_tasks.process_audio_analysis": {
            "queue": "audio_processing",
            "routing_key": "audio.process",
        },
        "samplemind.core.tasks.audio_tasks.batch_process_audio_files": {
            "queue": "audio_processing",
            "routing_key": "audio.process",
        },
        "samplemind.core.tasks.audio_tasks.generate_audio_embeddings": {
            "queue": "embeddings",
            "routing_key": "embeddings.generate",
        },
    },
    # Monitoring and logging
    worker_send_task_events=True,
    task_send_sent_event=True,
    # Performance settings
    broker_connection_retry_on_startup=True,
    broker_pool_limit=10,
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-old-results": {
            "task": "samplemind.core.tasks.audio_tasks.cleanup_old_results",
            "schedule": 3600.0,  # Run every hour
        },
    },
)

# ── Dev overrides ─────────────────────────────────────────────────────────────
# In development, tasks run in the normal Celery worker (not eager) by default.
# Set ``task_always_eager=True`` if you want synchronous in-process execution
# (useful for pytest without a running Redis / worker).

if os.getenv("ENVIRONMENT", "development") == "development":
    celery_app.conf.update(
        task_always_eager=False,  # Set to True for synchronous testing
        task_eager_propagates=True,
    )


if __name__ == "__main__":
    celery_app.start()
