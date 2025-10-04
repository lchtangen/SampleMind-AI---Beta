#!/bin/bash
# SampleMind AI v6 - API Server Startup Script

set -e

cd "$(dirname "$0")"

echo "🚀 Starting SampleMind AI Backend Server..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. API keys may not be configured."
fi

# Set PYTHONPATH
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# Activate virtual environment and start server
source .venv/bin/activate

echo "✅ Starting server at http://0.0.0.0:8000"
echo "📖 API Docs: http://localhost:8000/api/docs"
echo "📘 ReDoc: http://localhost:8000/api/redoc"
echo ""

exec uvicorn samplemind.interfaces.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
