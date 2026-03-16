# SampleMind AI — Development Automation
.PHONY: help setup dev test lint format typecheck security docs clean deploy

# Python virtual environment
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help: ## Show this help message
	@echo "SampleMind AI — Development Commands"
	@echo "====================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@echo "Setting up SampleMind AI development environment..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install poetry
	$(VENV)/bin/poetry install
	@echo "Development environment ready!"

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
	@echo "Starting SampleMind AI development server..."
	$(PYTHON) -m uvicorn src.samplemind.server.main:app --reload --host 0.0.0.0 --port 8000

upgrade-deps: ## Upgrade all dependencies to v3.0 targets
	$(VENV)/bin/poetry update
	@echo "Dependencies upgraded. Run 'make test' to verify."

install-dev: ## Install dev dependencies
	$(VENV)/bin/poetry install --with dev

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
# BETA RELEASE QUALITY TARGETS
# ============================================================================

polish: ## Run comprehensive code polish analysis
	@echo "✨ Analyzing code quality for beta release..."
	$(PYTHON) scripts/polish_codebase.py

polish-fix: ## Auto-fix code quality issues
	@echo "🔧 Auto-fixing code quality issues..."
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/
	$(PYTHON) -m ruff check --fix src/ tests/

test-cov: ## Run tests with detailed coverage report
	@echo "📊 Running tests with coverage analysis..."
	$(PYTHON) -m pytest tests/ -v \
		--cov=src \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=json
	@echo "✅ Coverage report generated in htmlcov/"

test-unit: ## Run only unit tests
	@echo "🧪 Running unit tests..."
	$(PYTHON) -m pytest tests/unit/ -v

test-integration: ## Run only integration tests
	@echo "🔗 Running integration tests..."
	$(PYTHON) -m pytest tests/integration/ -v

test-fast: ## Run fast tests only
	@echo "⚡ Running fast tests..."
	$(PYTHON) -m pytest tests/ -v -m "not slow"

typecheck: ## Run type checking with mypy
	@echo "🔍 Running type checker..."
	$(PYTHON) -m mypy src/ --show-error-codes

validate: polish test-cov typecheck security ## Full validation for beta release
	@echo "✅ Full validation complete!"

pre-commit: format lint test-fast ## Run pre-commit checks
	@echo "✅ Pre-commit checks passed!"

pre-release: validate ## Prepare for beta release
	@echo "🚀 Beta release preparation complete!"

# ============================================================================
# USB BOOT TARGETS — Optimised for Ubuntu 25.10 persistence USB drive
# ============================================================================
.PHONY: setup-usb dev-usb mount-tmpfs usb-status clean-usb

setup-usb: ## Full one-command setup for Ubuntu 25.10 USB boot
	@bash scripts/setup-usb.sh

setup-usb-full: ## USB setup including heavy ML deps (torch, transformers, demucs ~5GB)
	@bash scripts/setup-usb.sh --full

mount-tmpfs: ## Mount 2GB RAM disk for caches (run after each reboot)
	@mkdir -p /tmp/samplemind-dev/{pip,poetry,pnpm,pycache,next,dist}
	@(mountpoint -q /tmp/samplemind-dev 2>/dev/null && echo "  tmpfs already mounted") || \
	  (sudo mount -t tmpfs -o size=2G,mode=1777 tmpfs /tmp/samplemind-dev && echo "  tmpfs mounted at /tmp/samplemind-dev (2GB)")
	@echo ""
	@echo "Add these to your shell or source .env.usb-cache:"
	@echo "  export PIP_CACHE_DIR=/tmp/samplemind-dev/pip"
	@echo "  export POETRY_CACHE_DIR=/tmp/samplemind-dev/poetry"
	@echo "  export PYTHONPYCACHEPREFIX=/tmp/samplemind-dev/pycache"
	@echo "  export PNPM_STORE_DIR=/tmp/samplemind-dev/pnpm"

dev-usb: ## Start minimal services (MongoDB, Redis, ChromaDB) + API with hot-reload
	@echo "Starting USB dev stack (no Ollama/Prometheus/Grafana)..."
	docker compose -f docker-compose.yml -f docker-compose.dev-usb.yml up -d mongodb redis chromadb
	@echo "Services up. Starting API..."
	PYTHONPYCACHEPREFIX=/tmp/samplemind-dev/pycache \
	  $(PYTHON) -m uvicorn samplemind.server.main:app --reload --host 0.0.0.0 --port 8000

usb-status: ## Show USB persistence space, RAM usage, and service health
	@echo "=== Persistence .dat space ==="
	@df -h / | awk 'NR==2{print "  " $$3 " used / " $$2 " total (" $$5 " full)"}'
	@echo ""
	@echo "=== tmpfs RAM cache ==="
	@(df -h /tmp/samplemind-dev 2>/dev/null | awk 'NR==2{print "  " $$3 " used / " $$2 " total"}') || echo "  (not mounted — run: make mount-tmpfs)"
	@echo ""
	@echo "=== Docker services ==="
	@docker compose -f docker-compose.yml -f docker-compose.dev-usb.yml ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "  (Docker not running)"
	@echo ""
	@echo "=== Python venv ==="
	@du -sh .venv 2>/dev/null | awk '{print "  " $$1}' || echo "  (not installed — run: make setup-usb)"

clean-usb: ## Remove build artifacts from persistence storage (free up .dat space)
	@echo "Cleaning build artifacts from persistence storage..."
	@find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null; true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null; true
	@find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null; true
	@rm -rf .next dist build *.egg-info 2>/dev/null; true
	@echo "Done. Run 'make usb-status' to check freed space."
