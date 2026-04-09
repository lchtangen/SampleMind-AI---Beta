# SampleMind AI — Development Automation
.PHONY: help setup setup-dev install install-dev sync dev test lint format typecheck \
        security quality clean build setup-db install-models upgrade \
        test-unit test-integration test-cov test-fast polish polish-fix \
        plugins plugins-ableton plugins-fl-studio

UV = uv
PYTHON = uv run python
PYTEST = uv run pytest
RUFF = uv run ruff
BLACK = uv run black
MYPY = uv run mypy

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Environment ──────────────────────────────────────────────────────────────

setup: ## Create venv and install all dependencies (including dev)
	$(UV) sync
	@echo "✅ Environment ready. Use 'uv run <cmd>' or activate .venv."

setup-dev: setup install-models setup-db ## Full dev setup (deps + models + databases)

sync: ## Sync dependencies from lockfile (fast, no resolution)
	$(UV) sync

install: ## Install production dependencies only
	$(UV) sync --no-dev

install-dev: ## Install dev dependencies
	$(UV) sync

upgrade: ## Upgrade all dependencies and regenerate lockfile
	$(UV) lock --upgrade
	$(UV) sync
	@echo "✅ Dependencies upgraded. Run 'make test' to verify."

install-models: ## Download Ollama AI models
	@echo "🤖 Installing AI models..."
	ollama pull phi3:mini
	ollama pull qwen2.5:7b-instruct
	ollama pull gemma2:2b
	@echo "✅ AI models installed!"

setup-db: ## Start development databases via Docker
	docker-compose up -d mongodb redis chromadb
	@echo "✅ Databases ready!"

# ── Development ───────────────────────────────────────────────────────────────

dev: ## Start FastAPI development server
	$(UV) run uvicorn samplemind.server.main:app --reload --host 0.0.0.0 --port 8000

dev-full: ## Start full stack (databases + API server)
	docker-compose up -d
	$(UV) run uvicorn samplemind.server.main:app --reload --host 0.0.0.0 --port 8000

cli: ## Run the CLI
	$(UV) run python main.py

tui: ## Run the TUI
	$(UV) run python -m samplemind.interfaces.tui.main

# ── Testing ───────────────────────────────────────────────────────────────────

test: ## Run all tests
	$(PYTEST) tests/ -v

test-unit: ## Run unit tests only
	$(PYTEST) tests/unit/ -v

test-integration: ## Run integration tests only
	$(PYTEST) tests/integration/ -v

test-fast: ## Run fast tests (skip slow)
	$(PYTEST) tests/ -v -m "not slow"

test-cov: ## Run tests with HTML coverage report (parallel)
	$(PYTEST) tests/ -n auto --dist=loadfile --cov=src/samplemind --cov-report=html --cov-report=term-missing
	@echo "✅ Coverage report: htmlcov/index.html"

test-parallel: ## Run unit tests in parallel with pytest-xdist (fastest)
	$(PYTEST) tests/unit/ -n auto --dist=loadfile --no-cov -q

test-smoke: ## Smoke test: unit tests, fail-fast, no coverage
	$(PYTEST) tests/unit/ -x --no-cov -q --timeout=30

test-watch: ## Auto-rerun unit tests on file changes (dev inner loop)
	$(UV) run ptw tests/unit/ src/ -- -x --tb=short --no-cov -q

# ── Code Quality ──────────────────────────────────────────────────────────────

lint: ## Run ruff + mypy
	$(RUFF) check .
	$(MYPY) src/

format: ## Format code with ruff
	$(RUFF) format .
	$(RUFF) check --fix .

security: ## Run bandit security scan
	$(UV) run bandit -r src/ -ll

quality: lint security ## Run all quality checks

polish: ## Analyse code quality
	$(PYTHON) scripts/polish_codebase.py

polish-fix: ## Auto-fix code quality issues
	$(RUFF) format src/ tests/
	$(RUFF) check --fix src/ tests/

typecheck: ## Run mypy type checking
	$(MYPY) src/

# ── DAW Plugins ───────────────────────────────────────────────────────────────

plugins: plugins-ableton plugins-fl-studio ## Build all DAW plugins

plugins-ableton: ## Start Ableton Live backend API server (Max for Live companion)
	@echo "🎛️  Starting Ableton Live backend on :8002..."
	$(UV) run uvicorn plugins.ableton.python_backend:app --host 0.0.0.0 --port 8002 --reload

plugins-fl-studio: ## Build FL Studio C++ wrapper (requires CMake + compiler)
	@echo "🎛️  Building FL Studio C++ plugin wrapper..."
	@if [ -d "plugins/fl_studio/cpp" ]; then \
		mkdir -p plugins/fl_studio/cpp/build && \
		cmake -B plugins/fl_studio/cpp/build -S plugins/fl_studio/cpp \
		      -DCMAKE_BUILD_TYPE=Release && \
		cmake --build plugins/fl_studio/cpp/build --config Release; \
		echo "✅ FL Studio plugin built: plugins/fl_studio/cpp/build/"; \
	else \
		echo "⚠️  plugins/fl_studio/cpp/ not found — skipping C++ build"; \
	fi

# ── Build & Deploy ────────────────────────────────────────────────────────────

build: ## Build Docker image
	docker build -t samplemind-ai:latest .

build-pkg: ## Build Python package
	$(UV) build

clean: ## Remove cache and build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf dist/ build/ htmlcov/ .coverage
