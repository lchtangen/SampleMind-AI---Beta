#!/bin/bash

# Start Flower - Celery Monitoring UI
# Web-based monitoring and administration for Celery

set -e

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Source environment variables if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "🌸 Starting Flower (Celery Monitoring)..."
echo "📂 PYTHONPATH: $PYTHONPATH"
echo "🌐 Web UI will be available at: http://localhost:5555"

# Start Flower
.venv/bin/celery -A samplemind.core.tasks.celery_app flower \
    --port=5555 \
    --max_tasks=10000 \
    --persistent=True \
    --db=./data/flower.db

# Open browser (optional)
# xdg-open http://localhost:5555 2>/dev/null || open http://localhost:5555 2>/dev/null || true
