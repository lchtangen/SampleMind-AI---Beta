#!/bin/bash
# Quick test runner with proper PYTHONPATH

cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
source .venv/bin/activate

export PYTHONPATH=$(pwd):$PYTHONPATH

echo "Running tests with PYTHONPATH=$PYTHONPATH"
echo "Python version: $(python --version)"
echo ""

# Run tests excluding E2E (which requires playwright browser installation)
pytest tests/unit/core/ tests/integration/ \
    -v \
    --tb=short \
    --ignore=tests/e2e/ \
    -m "not slow" \
    --maxfail=5 \
    --cov=src/samplemind \
    --cov-report=term-missing \
    --cov-report=html \
    "$@"
