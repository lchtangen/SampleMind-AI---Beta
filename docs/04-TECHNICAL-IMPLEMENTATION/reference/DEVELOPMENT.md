# Development Guide 💻

## Table of Contents
- [Development Environment](#development-environment)
- [Code Structure](#code-structure)
- [Git Workflow](#git-workflow)
- [Testing Strategy](#testing-strategy)
- [Debugging Guide](#debugging-guide)
- [Coding Standards](#coding-standards)
- [CI/CD Pipeline](#cicd-pipeline)
- [Release Process](#release-process)

---

## Development Environment

### Prerequisites

```
┌──────────────────────────────────────────┐
│       Required Software                   │
├──────────────────────────────────────────┤
│  Python: 3.11+                           │
│  Poetry: 1.5+ (dependency management)    │
│  Docker: 20.10+ & Docker Compose 2.0+    │
│  Git: 2.30+                              │
│  Node.js: 18+ (for frontend)            │
│  MongoDB: 7.0+                           │
│  Redis: 7.2+                             │
└──────────────────────────────────────────┘
```

### Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/samplemind/samplemind-ai-v6.git
cd samplemind-ai-v6

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -e ".[dev]"  # Install with dev dependencies
pre-commit install       # Install git hooks

# 4. Copy environment template
cp .env.example .env
# Edit .env with your API keys

# 5. Start databases (Docker)
docker-compose up -d mongodb redis chromadb

# 6. Verify setup
python scripts/verify_setup.py
pytest tests/ -v
```

### Development Tools

```
┌──────────────────────────────────────────────────┐
│           Development Tool Stack                  │
├──────────────────────────────────────────────────┤
│                                                   │
│  Code Quality:                                   │
│    ├─▶ Black (formatter)                        │
│    ├─▶ isort (import sorting)                   │
│    ├─▶ Ruff (linter, very fast)                 │
│    └─▶ mypy (type checker)                      │
│                                                   │
│  Testing:                                        │
│    ├─▶ pytest (test framework)                  │
│    ├─▶ pytest-cov (coverage reporting)          │
│    ├─▶ pytest-asyncio (async test support)      │
│    └─▶ pytest-mock (mocking utilities)          │
│                                                   │
│  Security:                                       │
│    ├─▶ bandit (security analyzer)               │
│    └─▶ safety (dependency vulnerability check)  │
│                                                   │
│  Documentation:                                  │
│    ├─▶ mkdocs (docs generation)                 │
│    └─▶ sphinx (API documentation)               │
│                                                   │
└──────────────────────────────────────────────────┘
```

### IDE Configuration

**VS Code** (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

**PyCharm**:
- Code style: Black
- Linter: Ruff
- Test runner: pytest
- Type checker: mypy

---

## Code Structure

### Project Organization

```
src/samplemind/
├── core/                   # Core business logic
│   ├── auth/              # Authentication & authorization
│   │   ├── jwt_handler.py      # JWT token management
│   │   ├── password.py         # Password hashing (bcrypt)
│   │   └── dependencies.py     # FastAPI dependencies
│   ├── database/          # Database clients & models
│   │   ├── mongo.py           # MongoDB (Beanie ODM)
│   │   ├── redis_client.py    # Redis caching
│   │   └── chroma.py          # ChromaDB vectors
│   ├── engine/            # Audio processing engine
│   │   └── audio_engine.py    # Core audio analysis
│   ├── tasks/             # Background task system
│   │   ├── celery_app.py      # Celery configuration
│   │   └── audio_tasks.py     # Audio processing tasks
│   └── loader.py          # Audio file loading utilities
│
├── integrations/           # External AI providers
│   ├── ai_manager.py          # Unified AI interface
│   ├── google_ai_integration.py   # Google Gemini
│   └── openai_integration.py     # OpenAI GPT-4o
│
├── interfaces/            # User-facing interfaces
│   ├── api/              # REST API (FastAPI)
│   │   ├── main.py           # API entry point
│   │   ├── config.py         # Configuration
│   │   ├── routes/           # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── audio.py
│   │   │   ├── ai.py
│   │   │   ├── tasks.py
│   │   │   ├── batch.py
│   │   │   ├── health.py
│   │   │   └── websocket.py
│   │   └── schemas/          # Pydantic schemas
│   ├── cli/              # Command-line interface
│   └── gui/              # Future GUI (tkinter/Qt)
│
└── utils/                 # Utility functions
    ├── file_picker.py        # File selection utilities
    └── modern_file_picker.py # Cross-platform file picker
```

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│            5-Layer Architecture                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  Layer 1: Interfaces (User-facing)              │
│    ├─▶ REST API (FastAPI)                      │
│    ├─▶ CLI (Typer)                             │
│    └─▶ WebSocket (Real-time)                   │
│                                                  │
│  Layer 2: Business Logic                        │
│    ├─▶ Audio Analysis                          │
│    ├─▶ AI Integration                          │
│    └─▶ User Management                         │
│                                                  │
│  Layer 3: Core Services                         │
│    ├─▶ AudioEngine (processing)                │
│    ├─▶ AI Manager (providers)                  │
│    └─▶ Task Queue (Celery)                     │
│                                                  │
│  Layer 4: Data Access                           │
│    ├─▶ MongoDB (primary)                       │
│    ├─▶ Redis (cache)                           │
│    └─▶ ChromaDB (vectors)                      │
│                                                  │
│  Layer 5: Infrastructure                        │
│    ├─▶ Docker (containers)                     │
│    ├─▶ Nginx (reverse proxy)                   │
│    └─▶ CloudFlare (CDN/WAF)                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Module Dependencies

```
interfaces/api
    │
    ├─▶ core/auth
    ├─▶ core/database
    ├─▶ core/engine
    │       │
    │       └─▶ utils/loader
    │
    └─▶ integrations/ai_manager
            │
            ├─▶ google_ai_integration
            └─▶ openai_integration
```

**Dependency Rules:**
- ✅ Lower layers can't depend on higher layers
- ✅ Interfaces can depend on core and integrations
- ✅ Core should be independent of integrations
- ❌ No circular dependencies

---

## Git Workflow

### Branching Strategy (Git Flow)

```
┌──────────────────────────────────────────────────┐
│              Git Flow Diagram                     │
├──────────────────────────────────────────────────┤
│                                                   │
│  main (production)                               │
│    └─▶ Tagged releases (v6.0.0, v6.1.0, ...)    │
│                                                   │
│  develop (integration)                           │
│    ├─▶ feature/audio-analysis                   │
│    ├─▶ feature/ai-integration                   │
│    └─▶ feature/batch-processing                 │
│                                                   │
│  hotfix/critical-bug                            │
│    └─▶ Merges to main AND develop               │
│                                                   │
└──────────────────────────────────────────────────┘
```

### Commit Message Convention

```
Format: <type>(<scope>): <subject>

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation only
  style:    Code formatting (no logic change)
  refactor: Code restructuring (no behavior change)
  perf:     Performance improvement
  test:     Add or update tests
  chore:    Build process or auxiliary tool changes

Examples:
  feat(api): add batch audio upload endpoint
  fix(auth): resolve JWT token expiration issue
  docs(readme): update installation instructions
  perf(engine): optimize audio feature extraction
```

### Branch Workflow

```bash
# 1. Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# 2. Work on feature
git add .
git commit -m "feat(scope): description"

# 3. Keep up to date with develop
git fetch origin
git rebase origin/develop

# 4. Push to remote
git push origin feature/your-feature-name

# 5. Create Pull Request on GitHub
# - Base: develop
# - Compare: feature/your-feature-name

# 6. After PR approval, feature branch is deleted
```

### Pull Request Checklist

```
┌──────────────────────────────────────────┐
│         PR Checklist                      │
├──────────────────────────────────────────┤
│ ☐ All tests passing                      │
│ ☐ Code formatted (black, isort)          │
│ ☐ No linting errors (ruff)               │
│ ☐ Type hints added (mypy clean)          │
│ ☐ Documentation updated                  │
│ ☐ New tests added for new features       │
│ ☐ Coverage maintained (>70%)             │
│ ☐ No sensitive data committed            │
│ ☐ Commit messages follow convention      │
│ ☐ PR description is clear                │
└──────────────────────────────────────────┘
```

---

## Testing Strategy

### Testing Pyramid

```
┌──────────────────────────────────────────┐
│          Testing Pyramid                  │
├──────────────────────────────────────────┤
│                                           │
│                  /\                       │
│                 /  \  E2E Tests (5%)      │
│                /____\                     │
│               /      \                    │
│              / Integ. \ (15%)            │
│             /  Tests   \                  │
│            /____________\                 │
│           /              \                │
│          /  Unit  Tests   \ (80%)        │
│         /                  \              │
│        /____________________\             │
│                                           │
│  Speed:    Fast ← ← ← Slow               │
│  Cost:     Cheap ← ← ← Expensive         │
│  Coverage: Focused ← ← ← Broad           │
│                                           │
└──────────────────────────────────────────┘
```

### Test Organization

```
tests/
├── unit/                       # Fast, isolated tests
│   ├── test_auth.py           # Auth logic tests
│   ├── test_audio_engine.py   # Audio processing tests
│   ├── core/
│   │   └── test_audio_engine.py
│   ├── integrations/
│   │   ├── test_ai_manager.py
│   │   ├── test_google_ai_integration.py
│   │   └── test_openai_integration.py
│   └── utils/
│       └── test_file_picker.py
│
├── integration/               # Component integration tests
│   ├── test_api_auth.py      # API auth flow tests
│   └── test_audio_workflow.py # End-to-end audio workflow
│
├── e2e/                       # End-to-end tests
│   └── test_user_flow.py     # Complete user workflows
│
├── performance/               # Performance benchmarks
│   └── test_audio_processing_benchmark.py
│
├── fixtures/                  # Test data
│   ├── audio/                # Sample audio files
│   └── responses/            # Mock API responses
│
└── conftest.py               # Pytest configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py

# Run specific test function
pytest tests/unit/test_auth.py::test_login_success

# Run tests matching pattern
pytest -k "auth"

# Run with verbose output
pytest -v

# Run in parallel (faster)
pytest -n auto

# Run and stop on first failure
pytest -x

# Show coverage gaps
pytest --cov=src --cov-report=term-missing
```

### Writing Tests

```python
# test_example.py
import pytest
from unittest.mock import AsyncMock, patch
from samplemind.core.auth import create_access_token, verify_token

class TestAuthentication:
    """Test authentication functionality."""
    
    @pytest.fixture
    def user_data(self):
        """Sample user data fixture."""
        return {
            "user_id": "test-uuid-123",
            "email": "test@example.com"
        }
    
    def test_create_access_token(self, user_data):
        """Test JWT access token creation."""
        token = create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"]
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
    
    def test_verify_token_valid(self, user_data):
        """Test valid token verification."""
        # Arrange
        token = create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"]
        )
        
        # Act
        user_id = verify_token(token, token_type="access")
        
        # Assert
        assert user_id == user_data["user_id"]
    
    def test_verify_token_expired(self):
        """Test expired token rejection."""
        expired_token = "expired.jwt.token"
        user_id = verify_token(expired_token)
        assert user_id is None
    
    @pytest.mark.asyncio
    async def test_async_database_operation(self):
        """Test async database operations."""
        # Mock async database call
        with patch('samplemind.core.database.mongo.User.find_one') as mock:
            mock.return_value = AsyncMock(
                user_id="test-123",
                email="test@example.com"
            )
            
            user = await User.find_one({"email": "test@example.com"})
            assert user is not None
            assert user.email == "test@example.com"
```

---

## Debugging Guide

### Debug Tools

```bash
# Python debugger (pdb)
import pdb; pdb.set_trace()  # Insert breakpoint

# IPython debugger (better interface)
import ipdb; ipdb.set_trace()

# Remote debugging (VS Code)
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

### Logging Configuration

```python
# config/logging.py
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Usage in code
logger = structlog.get_logger(__name__)
logger.info("audio_analysis_started", file_id="uuid-123", duration=180.5)
logger.error("ai_provider_error", provider="gemini", error=str(e))
```

### Common Debugging Scenarios

```python
# 1. Debug slow API endpoint
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@timing_decorator
async def analyze_audio(file_id: str):
    # ... implementation
    pass

# 2. Debug database query performance
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(mongodb_url)
db = client[database_name]

# Enable profiling
db.command("profile", 2)  # Profile all operations
db.command("profile", 0)  # Disable profiling

# View slow queries
slow_queries = db.system.profile.find({"millis": {"$gt": 100}})

# 3. Debug memory leaks
import tracemalloc

tracemalloc.start()
# ... run code
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

### Debugging Docker Services

```bash
# View logs
docker-compose logs -f api           # Follow API logs
docker-compose logs --tail=100 mongodb  # Last 100 lines

# Execute commands in container
docker-compose exec api python -c "from samplemind.core.database import health_check; print(await health_check())"

# Interactive shell
docker-compose exec api /bin/bash
docker-compose exec mongodb mongosh

# Check container resources
docker stats

# Restart specific service
docker-compose restart api
```

---

## Coding Standards

### Python Style Guide

```python
# ✅ GOOD: Follow PEP 8
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

async def analyze_audio_file(
    file_path: str,
    analysis_level: str = "basic",
    cache_results: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Analyze audio file and return results.
    
    Args:
        file_path: Path to audio file
        analysis_level: Level of analysis (basic, advanced, full)
        cache_results: Whether to cache results in Redis
        
    Returns:
        Analysis results dictionary or None if failed
        
    Raises:
        AudioProcessingError: If analysis fails
    """
    try:
        features = await extract_features(file_path)
        result = await process_analysis(features, analysis_level)
        
        if cache_results:
            await cache_set(f"analysis:{file_path}", result, ttl=3600)
            
        return result
    except Exception as e:
        logger.error("Analysis failed", exc_info=True)
        raise AudioProcessingError(f"Failed to analyze {file_path}") from e

# ❌ BAD: Poor style
def analyze(f,l="basic"):
    feat=extract(f)
    res=process(feat,l)
    return res
```

### Type Hints

```python
from typing import Optional, List, Dict, Union, TypedDict
from datetime import datetime

# Use type hints for all function parameters and returns
def process_files(
    files: List[str],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, int]]:
    ...

# TypedDict for structured dictionaries
class AudioMetadata(TypedDict):
    file_id: str
    duration: float
    sample_rate: int
    channels: int

def get_metadata(file_path: str) -> AudioMetadata:
    ...
```

### Code Organization

```python
# Module structure
# 1. Docstring
"""
Module for audio feature extraction.

This module provides functionality for extracting audio features
including tempo, key, spectral features, and rhythm analysis.
"""

# 2. Imports (grouped)
# Standard library
import os
from pathlib import Path
from typing import Optional

# Third-party
import numpy as np
import librosa
from fastapi import HTTPException

# Local imports
from samplemind.core.engine.base import BaseEngine
from samplemind.utils.logger import get_logger

# 3. Constants
DEFAULT_SAMPLE_RATE = 44100
MAX_DURATION = 600  # 10 minutes

# 4. Classes and functions
class AudioEngine:
    ...
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Ruff
        run: ruff check .
      - name: Run Black
        run: black --check .
      - name: Run mypy
        run: mypy src/
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

---

## Release Process

### Versioning (Semantic Versioning)

```
Format: MAJOR.MINOR.PATCH

Examples:
  6.0.0 → 6.0.1  (Patch: Bug fixes)
  6.0.1 → 6.1.0  (Minor: New features, backwards compatible)
  6.1.0 → 7.0.0  (Major: Breaking changes)
```

### Release Checklist

```
┌──────────────────────────────────────────┐
│         Release Checklist                 │
├──────────────────────────────────────────┤
│ ☐ All tests passing on develop           │
│ ☐ Documentation updated                  │
│ ☐ CHANGELOG.md updated                   │
│ ☐ Version bumped in pyproject.toml       │
│ ☐ Create release branch                  │
│ ☐ Final testing on release branch        │
│ ☐ Merge to main                          │
│ ☐ Tag release (git tag v6.x.x)           │
│ ☐ Build and publish to PyPI              │
│ ☐ Deploy to production                   │
│ ☐ Create GitHub release with notes       │
│ ☐ Announce release                       │
└──────────────────────────────────────────┘
```

### Release Commands

```bash
# 1. Update version
poetry version patch  # or minor, major

# 2. Update CHANGELOG.md
# - Add release date
# - List all changes since last release

# 3. Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 6.0.1"

# 4. Create tag
git tag -a v6.0.1 -m "Release version 6.0.1"

# 5. Push to remote
git push origin main --tags

# 6. Build and publish to PyPI
poetry build
poetry publish

# 7. Create GitHub release
gh release create v6.0.1 --generate-notes
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-01  
**Owner**: Engineering Team

**Status**: ✅ Ready for Development
