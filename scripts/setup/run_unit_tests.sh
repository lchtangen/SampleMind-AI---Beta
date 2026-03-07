#!/bin/bash
# Run unit tests only (no database required)

cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
source .venv/bin/activate

export PYTHONPATH=$(pwd):$PYTHONPATH

echo "==================================="
echo "Running Unit Tests Only"
echo "==================================="
echo ""

pytest tests/unit/ -v --tb=short --cov=src/samplemind/core "$@"
