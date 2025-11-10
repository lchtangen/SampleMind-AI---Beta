# SampleMind AI - Technology Stack

## Programming Languages
- **Python**: 3.11+ (primary backend language)
- **TypeScript**: 5.0+ (frontend and type safety)
- **JavaScript**: Node.js 18+ (build tools and scripts)

## Backend Technologies

### Core Framework
- **FastAPI**: 0.104.1+ - High-performance async web framework
- **Uvicorn**: 0.24.0+ - ASGI server with standard extras
- **Pydantic**: 2.5.0+ - Data validation and settings management
- **Starlette**: 0.27.0+ - ASGI framework foundation

### Audio Processing
- **librosa**: 0.10.1+ - Audio analysis and feature extraction
- **soundfile**: 0.12.1+ - Audio file I/O
- **scipy**: 1.11.4+ - Signal processing algorithms
- **numpy**: 1.25.2+ - Numerical computations
- **resampy**: 0.4.2+ - Audio resampling
- **audioread**: 3.0.1+ - Audio file reading
- **spleeter**: 2.4.0+ - Source separation
- **basic-pitch**: 0.2.5+ - Pitch detection
- **mido**: 1.3.0+ - MIDI file I/O

### AI/ML Stack
- **Google Generative AI**: 0.3.0+ - Gemini 2.5 Pro integration
- **OpenAI**: 1.3.0+ - GPT-4o integration
- **Anthropic**: 0.7.0+ - Claude 3.5 Sonnet integration
- **Ollama**: 0.1.7+ - Local AI models (Phi3, Qwen2.5)
- **PyTorch**: 2.1.0+ - Deep learning framework
- **Transformers**: 4.35.0+ - Hugging Face models
- **sentence-transformers**: 2.2.2+ - Embedding generation

### Databases
- **MongoDB**: Primary database with Motor 3.3.1+ (async driver)
- **Redis**: 5.0.1+ - Caching and pub/sub
- **ChromaDB**: 0.4.17+ - Vector database for similarity search
- **Prisma**: 5.7.0+ - Database ORM (TypeScript)

### Authentication & Security
- **python-jose**: 3.3.0+ with cryptography - JWT handling
- **passlib**: 1.7.4+ with bcrypt - Password hashing

### CLI & TUI
- **Typer**: 0.9.0+ - CLI framework
- **Click**: 8.1.7+ - Command-line interface creation
- **Rich**: 13.7.0+ - Rich text and formatting
- **Questionary**: 2.0.1+ - Interactive prompts
- **Textual**: 0.44.0+ - Modern TUI framework
- **textual-plotext**: 0.2.0+ - TUI plotting

### Utilities
- **python-dotenv**: 1.0.0+ - Environment variable management
- **loguru**: 0.7.2+ - Logging
- **structlog**: 23.2.0+ - Structured logging
- **httpx**: 0.25.2+ - Async HTTP client
- **aiofiles**: 23.2.1+ - Async file operations
- **websockets**: 12.0+ - WebSocket support
- **Jinja2**: 3.1.2+ - Template engine
- **python-multipart**: 0.0.6+ - Multipart form data

## Frontend Technologies

### Core Framework
- **Next.js**: 14.1.0+ - React framework with App Router
- **React**: 18+ - UI library
- **TypeScript**: 5.0+ - Type safety

### UI & Styling
- **Tailwind CSS**: 3+ - Utility-first CSS framework
- **PostCSS**: Latest - CSS processing
- **clsx**: 2.1.1+ - Conditional class names
- **tailwind-merge**: 3.3.1+ - Tailwind class merging
- **lucide-react**: 0.546.0+ - Icon library
- **next-themes**: 0.4.6+ - Theme management

### State & Data
- **Zod**: 3.22.0+ - Schema validation
- **@prisma/client**: 5.7.0+ - Database client

## Development Tools

### Testing
- **pytest**: 7.4.3+ - Test framework
- **pytest-asyncio**: 0.21.1+ - Async test support
- **pytest-cov**: 4.1.0+ - Coverage reporting
- **pytest-mock**: 3.12.0+ - Mocking utilities
- **pytest-xdist**: 3.4.0+ - Parallel test execution
- **Locust**: Load testing framework

### Code Quality
- **ruff**: 0.1.6+ - Fast Python linter
- **black**: 23.11.0+ - Code formatter (line-length: 88)
- **isort**: 5.12.0+ - Import sorting (black profile)
- **mypy**: 1.7.1+ - Static type checker
- **bandit**: 1.7.5+ - Security linter
- **safety**: 2.3.5+ - Dependency security checker
- **ESLint**: 8.0+ - JavaScript/TypeScript linting
- **Prettier**: 3.0+ - Code formatting

### Build & Deployment
- **Poetry**: Python dependency management and packaging
- **pnpm**: 8.0.0+ - Fast, disk-efficient package manager
- **Turbo**: 1.10.0+ - Monorepo build system
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Kubernetes**: Production orchestration
- **Alembic**: Database migrations

### Version Control & CI/CD
- **Git**: Version control
- **GitHub Actions**: CI/CD pipelines
- **pre-commit**: 3.5.0+ - Git hooks
- **commitizen**: 3.12.0+ - Conventional commits
- **husky**: 8.0+ - Git hooks (JavaScript)
- **lint-staged**: 15.0+ - Staged file linting

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Flower**: Celery monitoring UI

## Development Commands

### Python/Backend
```bash
# Environment setup
poetry install                    # Install dependencies
poetry shell                      # Activate virtual environment
python -m venv .venv             # Create venv manually
source .venv/bin/activate        # Activate venv (Unix)

# Development
python main.py                   # Start CLI
uvicorn backend.app.main:app --reload  # Start API server
make dev                         # Start development server
make test                        # Run tests
make test-cov                    # Run tests with coverage

# Code quality
make format                      # Format code (black + isort)
make lint                        # Lint code (ruff)
make quality                     # Run all quality checks
black src/                       # Format with black
ruff check src/                  # Lint with ruff
mypy src/                        # Type check

# Database
alembic upgrade head             # Run migrations
alembic revision --autogenerate  # Create migration
```

### Frontend/JavaScript
```bash
# Package management
pnpm install                     # Install dependencies
pnpm add <package>               # Add dependency
pnpm run dev                     # Start dev server
pnpm run build                   # Build for production
pnpm run start                   # Start production server

# Monorepo commands
turbo run dev --parallel         # Run dev in all workspaces
turbo run build                  # Build all packages
turbo run test                   # Test all packages
turbo run lint                   # Lint all packages

# Specific workspace commands
pnpm web:dev                     # Start web app dev server
pnpm api:dev                     # Start API dev server
pnpm audio:build                 # Build audio engine

# Database
pnpm db:generate                 # Generate Prisma client
pnpm db:migrate                  # Run Prisma migrations
pnpm db:studio                   # Open Prisma Studio
```

### Docker & Services
```bash
# Docker Compose
docker-compose up -d             # Start all services
docker-compose down              # Stop all services
docker-compose logs -f           # Follow logs
docker-compose ps                # List running services

# Database services
make setup-db                    # Start databases
make install-models              # Install AI models
```

### Testing
```bash
# Python tests
pytest                           # Run all tests
pytest tests/unit/               # Run unit tests
pytest tests/integration/        # Run integration tests
pytest --cov=src                 # Run with coverage
pytest -v -s                     # Verbose output
pytest -n auto                   # Parallel execution

# Load testing
locust -f tests/load/locustfile.py  # Start load tests
```

### Utilities
```bash
# Setup
make setup                       # Complete environment setup
./scripts/setup/quick_start.sh   # Quick start (Unix)
.\scripts\setup\windows_setup.ps1 # Quick start (Windows)

# Cleanup
make clean                       # Clean cache and build files
pnpm clean                       # Clean node_modules
```

## Configuration Files
- **pyproject.toml**: Python project configuration and dependencies
- **package.json**: JavaScript project configuration
- **pnpm-workspace.yaml**: Monorepo workspace configuration
- **turbo.json**: Turbo build configuration
- **tsconfig.json**: TypeScript configuration
- **pytest.ini**: Pytest configuration
- **.env**: Environment variables
- **alembic.ini**: Database migration configuration
- **docker-compose.yml**: Docker services configuration

## Build System
- **Poetry**: Python dependency resolution and packaging
- **pnpm workspaces**: JavaScript monorepo management
- **Turbo**: Incremental builds with caching
- **Make**: Task automation and shortcuts
