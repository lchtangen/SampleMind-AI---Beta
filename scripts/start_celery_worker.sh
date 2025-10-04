#!/bin/bash

# Start Celery Worker for SampleMind AI
# Processes background tasks for audio analysis

set -e

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Source environment variables if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "🚀 Starting Celery Worker..."
echo "📂 PYTHONPATH: $PYTHONPATH"
echo "🔧 Redis URL: ${REDIS_URL:-redis://localhost:6379/0}"

# Start celery worker with multiple queues
.venv/bin/celery -A samplemind.core.tasks.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --queues=default,audio_processing,ai_analysis,embeddings \
    --hostname=worker@%h

# Alternative: Start worker for specific queue only
# .venv/bin/celery -A samplemind.core.tasks.celery_app worker \
#     --loglevel=info \
#     --queues=audio_processing \
#     --hostname=audio_worker@%h
