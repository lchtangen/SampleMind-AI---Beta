#!/bin/bash
# =============================================================================
# Celery Entrypoint Script
# Flexible entrypoint for worker, beat, and flower services
# =============================================================================

set -e

# Function to wait for services
wait_for_services() {
    echo "Waiting for Redis..."
    while ! curl -f "${REDIS_URL:-redis://redis:6379}" &>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 2
    done
    echo "Redis is up!"

    echo "Waiting for MongoDB..."
    # MongoDB check would require mongosh, simplified for now
    sleep 5
    echo "MongoDB should be up!"
}

# Wait for services to be ready
wait_for_services

# Determine which Celery service to run
case "$1" in
    worker)
        echo "Starting Celery Worker..."
        exec celery -A src.samplemind.core.tasks.celery_app worker \
            --loglevel="${CELERY_LOG_LEVEL:-info}" \
            --concurrency="${CELERY_WORKER_CONCURRENCY:-4}" \
            --max-tasks-per-child="${CELERY_WORKER_MAX_TASKS_PER_CHILD:-1000}" \
            --time-limit="${CELERY_TASK_TIME_LIMIT:-3600}" \
            --soft-time-limit="${CELERY_TASK_SOFT_TIME_LIMIT:-3300}"
        ;;
    
    beat)
        echo "Starting Celery Beat (Scheduler)..."
        # Remove old beat schedule if exists
        rm -f /app/celerybeat-schedule.db
        exec celery -A src.samplemind.core.tasks.celery_app beat \
            --loglevel="${CELERY_LOG_LEVEL:-info}" \
            --schedule="/app/celerybeat-schedule/celerybeat-schedule.db"
        ;;
    
    flower)
        echo "Starting Flower (Monitoring)..."
        exec celery -A src.samplemind.core.tasks.celery_app flower \
            --port="${FLOWER_PORT:-5555}" \
            --loglevel="${CELERY_LOG_LEVEL:-info}" \
            --basic_auth="${FLOWER_BASIC_AUTH:-admin:admin}" \
            --url_prefix="${FLOWER_URL_PREFIX:-}"
        ;;
    
    *)
        echo "Unknown command: $1"
        echo "Available commands: worker, beat, flower"
        exit 1
        ;;
esac