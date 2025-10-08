# SampleMind AI v6 - Development Automation
.PHONY: help setup dev test lint format typecheck security docs clean deploy

# Python virtual environment
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help: ## Show this help message
	@echo "SampleMind AI v6 - Development Commands"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@echo "🚀 Setting up SampleMind AI development environment..."
	python3.11 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "✅ Development environment ready!"

setup-dev: setup install-models setup-db ## Complete development setup

install-models: ## Download and install AI models
	@echo "🤖 Installing AI models..."
	ollama pull phi3:mini
	ollama pull qwen2.5:7b-instruct
	ollama pull gemma2:2b
	@echo "✅ AI models installed!"

setup-db: ## Setup development databases
	@echo "🗄️ Setting up databases..."
	docker-compose up -d mongodb redis chromadb
	@echo "✅ Databases ready!"

dev: ## Start development server
	@echo "🚀 Starting SampleMind AI development server..."
	$(PYTHON) -m uvicorn src.interfaces.api.fastapi_app:app --reload --host 0.0.0.0 --port 8000

dev-full: ## Start full development stack
	docker-compose up -d
	@echo "🌟 Full development stack running at http://localhost:8000"

test: ## Run all tests
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Run linting
	@echo "🔍 Running linters..."
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy src/

format: ## Format code
	@echo "🎨 Formatting code..."
	$(PYTHON) -m black .
	$(PYTHON) -m isort .

security: ## Run security checks
	@echo "🛡️ Running security scans..."
	$(PYTHON) -m bandit -r src/
	$(PYTHON) -m safety check

quality: lint security ## Run all quality checks

build: ## Build Docker image
	docker build -t samplemind-ai:latest .

clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf dist/ build/ *.egg-info/

doctor: ## Check system health
	$(PYTHON) -m src.core.utils.doctor

# ============================================================================
# Performance Testing (NEW in v7)
# ============================================================================

benchmark: ## Run API performance benchmark
	@echo "🚀 Running performance benchmarks..."
	locust -f scripts/performance/benchmark.py --host=http://localhost:8000 \
		--users 100 --spawn-rate 10 --run-time 5m --headless

benchmark-quick: ## Quick benchmark (10 users, 2 min)
	@echo "⚡ Running quick benchmark..."
	locust -f scripts/performance/benchmark.py --host=http://localhost:8000 \
		--users 10 --spawn-rate 2 --run-time 2m --headless

benchmark-stress: ## Stress test (500 users, 15 min)
	@echo "💪 Running stress test..."
	locust -f scripts/performance/benchmark.py --host=http://localhost:8000 \
		--users 500 --spawn-rate 50 --run-time 15m --headless

benchmark-ui: ## Run benchmark with web UI
	@echo "🌐 Starting Locust Web UI at http://localhost:8089"
	locust -f scripts/performance/benchmark.py --host=http://localhost:8000

profile: ## Profile memory usage with memray
	@echo "🔍 Profiling memory usage..."
	memray run -o memray-output.bin scripts/performance/profile_memory.py
	@echo "📊 Generating flamegraph..."
	memray flamegraph memray-output.bin -o memray-flamegraph.html
	@echo "✅ View results: memray-flamegraph.html"

profile-cpu: ## Profile CPU usage with py-spy
	@echo "⚡ Profiling CPU usage (sampling for 60s)..."
	py-spy record -o profile-cpu.svg --duration 60 -- python main.py
	@echo "✅ View results: profile-cpu.svg"

perf-test: benchmark profile ## Run all performance tests
	@echo "✅ All performance tests complete!"

# Database performance
setup-db-indexes: ## Create MongoDB performance indexes
	@echo "📊 Creating MongoDB indexes..."
	mongosh --file config/mongodb-indexes.js
	@echo "✅ Database indexes created!"

test-parallel: ## Run tests in parallel (faster)
	@echo "🧪 Running tests in parallel..."
	$(PYTHON) -m pytest tests/ -n auto -v --dist loadfile
