# SampleMind AI - Project Structure

## Directory Organization

### Root Structure
```
samplemind-ai-v6/
├── src/samplemind/          # Main Python package
├── backend/                 # FastAPI backend application
├── apps/web/                # Next.js web application
├── frontend/web/            # Alternative frontend location
├── samplemind-core/         # Core audio processing modules
├── packages/audio-engine/   # Audio engine package
├── tests/                   # Comprehensive test suite
├── scripts/                 # Setup and automation scripts
├── docs/                    # Documentation
├── deployment/              # Docker and Kubernetes configs
├── benchmarks/              # Performance benchmarking
└── monitoring/              # Grafana and Prometheus configs
```

## Core Components

### 1. Python Backend (`src/samplemind/`)
```
src/samplemind/
├── core/
│   ├── engine/              # Audio processing engine
│   ├── database/            # Database operations (MongoDB, Redis, ChromaDB)
│   └── auth/                # Authentication and RBAC
├── integrations/            # AI provider integrations
│   ├── google_ai_integration.py
│   ├── openai_integration.py
│   └── anthropic_integration.py
├── interfaces/              # User interfaces
│   ├── cli/                 # Command-line interface
│   └── api/                 # REST API endpoints
└── utils/                   # Utilities (file picker, etc.)
```

### 2. FastAPI Backend (`backend/`)
```
backend/
├── app/
│   ├── api/                 # API routes and endpoints
│   ├── core/                # Core configuration and settings
│   ├── middleware/          # Request/response middleware
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   └── main.py              # FastAPI application entry
├── tests/                   # Backend-specific tests
└── alembic/                 # Database migrations
```

### 3. Frontend Applications
```
apps/web/                    # Primary Next.js app
├── app/                     # Next.js 14 app directory
├── components/              # React components
├── contexts/                # React contexts
├── hooks/                   # Custom React hooks
└── public/                  # Static assets

frontend/web/                # Alternative frontend
├── app/                     # App routes
├── components/              # UI components
└── store/                   # State management
```

### 4. Core Audio Processing (`samplemind-core/`)
```
samplemind-core/
├── audio/
│   ├── engine/              # Audio engine implementation
│   ├── features/            # Feature extraction
│   │   └── spectral.py      # Spectral analysis
│   ├── effects.py           # Audio effects
│   └── processor.py         # Audio processing
└── tests/                   # Core module tests
```

### 5. Test Suite (`tests/`)
```
tests/
├── unit/                    # Unit tests
│   ├── core/                # Core module tests
│   ├── integrations/        # Integration tests
│   └── utils/               # Utility tests
├── integration/             # Integration tests
│   ├── test_audio_workflow.py
│   ├── test_batch_processing.py
│   └── test_distributed_processing.py
├── audio/                   # Audio-specific tests
├── e2e/                     # End-to-end tests
├── load/                    # Load testing (Locust)
└── fixtures/                # Test audio files
```

## Architectural Patterns

### Monorepo Structure
- Uses **pnpm workspaces** for JavaScript/TypeScript packages
- Uses **Poetry** for Python dependency management
- **Turbo** for build orchestration across packages

### Layered Architecture
1. **Presentation Layer**: CLI, Web UI, REST API
2. **Business Logic Layer**: AI integrations, audio processing services
3. **Data Layer**: MongoDB (primary), Redis (cache), ChromaDB (vectors)
4. **Infrastructure Layer**: Docker, Kubernetes, monitoring

### Microservices Components
- **API Server**: FastAPI async web service
- **Worker Service**: Celery background tasks
- **Database Services**: MongoDB, Redis, ChromaDB
- **Monitoring**: Prometheus + Grafana

### Key Design Patterns
- **Repository Pattern**: Database abstraction in `models/` and `repositories/`
- **Service Layer**: Business logic separation in `services/`
- **Factory Pattern**: AI provider selection and instantiation
- **Strategy Pattern**: Multiple AI providers with fallback chain
- **Async/Await**: Throughout for non-blocking I/O operations
- **Dependency Injection**: FastAPI dependencies for services

## Configuration Management
- **Environment Variables**: `.env` files for configuration
- **Settings Classes**: Pydantic Settings for type-safe config
- **Multi-Environment**: Development, production, testing configs
- **Secrets Management**: API keys via environment variables

## Data Flow
1. **Audio Input** → File picker or API upload
2. **Feature Extraction** → Audio engine processes file
3. **AI Analysis** → Features sent to AI providers
4. **Storage** → Results cached in Redis, stored in MongoDB
5. **Vector Indexing** → Embeddings stored in ChromaDB
6. **Response** → Results returned via CLI/API/Web UI

## Deployment Architecture
- **Docker Compose**: Local development and testing
- **Kubernetes**: Production deployment with scaling
- **Nginx**: Reverse proxy and load balancing
- **CI/CD**: GitHub Actions for automated testing and deployment
