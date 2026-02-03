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
