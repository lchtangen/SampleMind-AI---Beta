#!/bin/bash

# Start Celery Beat for SampleMind AI
# Schedules periodic tasks (cleanup, monitoring, etc.)

set -e

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Source environment variables if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "⏰ Starting Celery Beat..."
echo "📂 PYTHONPATH: $PYTHONPATH"

# Start celery beat
.venv/bin/celery -A samplemind.core.tasks.celery_app beat \
    --loglevel=info \
    --schedule=./data/celerybeat-schedule
