# 🏗️ SampleMind AI - System Architecture

**Version:** 1.0 Beta | **Last Updated:** 2025-10-04  
**Difficulty:** 🟡 Intermediate | **Time to Read:** 15 minutes

```
┌─────────────────────────────────────────────────────────────┐
│  🎵 Complete System Architecture & Design Documentation     │
│  From high-level overview to implementation details 📐       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📑 Table of Contents

| Section | What's Inside | For Who |
|---------|---------------|---------|
| [🎯 Overview](#-system-overview) | 30,000-foot view | Everyone |
| [🏛️ Architecture](#-high-level-architecture) | System layers | Architects |
| [🔄 Data Flow](#-data-flow) | How data moves | Developers |
| [🧩 Components](#-core-components) | Building blocks | Developers |
| [💾 Database](#-database-architecture) | Data storage | DBAs |
| [🔐 Security](#-security-architecture) | Auth & protection | Security |
| [🚀 Deployment](#-deployment-architecture) | Infrastructure | DevOps |
| [⚡ Performance](#-performance-optimization) | Speed & scale | SREs |
| [🔌 Integrations](#-external-integrations) | Third-party APIs | Integrators |

---

## 🎯 System Overview

### What is SampleMind AI?

SampleMind AI is a **hybrid AI-powered music production platform** that combines:
- 🎹 Advanced audio analysis (tempo, key, mood, genre)
- 🤖 AI-powered insights (Google Gemini + OpenAI GPT-4)
- 📁 Intelligent sample organization (similarity search)
- ⚡ Real-time processing (local + cloud AI)

### Visual System Map

```
┌─────────────────────────────────────────────────────────────┐
│                    SAMPLEMIND AI SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  👤 USERS                                                    │
│    │                                                         │
│    ├──▶ 🌐 Web App (React/Next.js) ──────┐                 │
│    │                                       │                 │
│    └──▶ 📱 CLI Interface ─────────────────┼──┐              │
│                                            │  │              │
│                                            ▼  ▼              │
│  🔧 API LAYER                                                │
│    ┌────────────────────────────────────────────┐           │
│    │  FastAPI REST API (Port 8000)             │           │
│    │  • Authentication (JWT)                    │           │
│    │  • Audio Upload/Download                   │           │
│    │  • Analysis Endpoints                      │           │
│    │  • WebSocket (Real-time updates)           │           │
│    └────────────────────────────────────────────┘           │
│                     │                                        │
│                     ▼                                        │
│  🧠 BUSINESS LOGIC                                           │
│    ┌─────────────┐  ┌─────────────┐  ┌──────────────┐      │
│    │ AudioEngine │  │ AI Manager  │  │ Task Queue   │      │
│    │ (librosa)   │  │ (Gemini+GPT)│  │ (Celery)     │      │
│    └─────────────┘  └─────────────┘  └──────────────┘      │
│                     │                                        │
│                     ▼                                        │
│  💾 DATA LAYER                                               │
│    ┌──────────┐  ┌────────┐  ┌──────────┐                  │
│    │ MongoDB  │  │ Redis  │  │ ChromaDB │                  │
│    │ (Docs)   │  │ (Cache)│  │ (Vectors)│                  │
│    └──────────┘  └────────┘  └──────────┘                  │
│                                                              │
│  🌍 EXTERNAL SERVICES                                        │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────┐        │
│    │ Google Gemini│  │ OpenAI GPT-4 │  │ Ollama   │        │
│    │ (Cloud AI)   │  │ (Cloud AI)   │  │ (Local)  │        │
│    └──────────────┘  └──────────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏛️ High-Level Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LAYER ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LAYER 1: PRESENTATION (Frontend)                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  • Next.js 14 Web Application                      │     │
│  │  • CLI Interface (Rich)                            │     │
│  │  • Real-time WebSocket connections                 │     │
│  └────────────────────────────────────────────────────┘     │
│                        ▼ HTTP/WS                             │
│  LAYER 2: API GATEWAY (Backend)                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  • FastAPI Application                             │     │
│  │  • JWT Authentication                              │     │
│  │  • Request validation (Pydantic)                   │     │
│  │  • Rate limiting                                   │     │
│  │  • CORS handling                                   │     │
│  └────────────────────────────────────────────────────┘     │
│                        ▼                                     │
│  LAYER 3: BUSINESS LOGIC                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │  • Audio Processing Engine (librosa)               │     │
│  │  • AI Analysis Manager                             │     │
│  │  • Background Task Processor (Celery)              │     │
│  │  • File Management                                 │     │
│  └────────────────────────────────────────────────────┘     │
│                        ▼                                     │
│  LAYER 4: DATA ACCESS                                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │  • Repository Pattern (MongoDB/Beanie)             │     │
│  │  • Cache Layer (Redis)                             │     │
│  │  • Vector Storage (ChromaDB)                       │     │
│  └────────────────────────────────────────────────────┘     │
│                        ▼                                     │
│  LAYER 5: EXTERNAL SERVICES                                 │
│  ┌────────────────────────────────────────────────────┐     │
│  │  • Google Gemini API                               │     │
│  │  • OpenAI API                                      │     │
│  │  • Ollama (Local LLM)                              │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Microservices Breakdown

```
┌──────────────────────────────────────────────────────┐
│              MICROSERVICES ARCHITECTURE              │
├──────────────────────────────────────────────────────┤
│                                                       │
│  [API Gateway]          [Celery Worker 1]            │
│    Port: 8000            Task: Audio Analysis        │
│    ↓                     ↓                            │
│  [Auth Service]         [Celery Worker 2]            │
│    JWT tokens            Task: AI Processing         │
│    ↓                     ↓                            │
│  [Audio Service]        [Celery Beat]                │
│    Upload/Process        Periodic Tasks              │
│    ↓                     ↓                            │
│  [AI Service]           [Flower Monitor]             │
│    Gemini/GPT-4          Port: 5555                  │
│                                                       │
│  All connected via:                                  │
│    • MongoDB (shared database)                       │
│    • Redis (message broker + cache)                 │
│    • ChromaDB (vector storage)                       │
└──────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Audio Analysis Workflow

```
┌─────────────────────────────────────────────────────────────┐
│          COMPLETE AUDIO ANALYSIS WORKFLOW                    │
└─────────────────────────────────────────────────────────────┘

Step 1: UPLOAD
  User uploads audio file (MP3/WAV/FLAC)
    │
    ├─▶ Frontend validates file (size, format)
    │
    ├─▶ POST /api/v1/audio/upload
    │
    ├─▶ Backend receives file
    │     • Save to disk (./storage/uploads/)
    │     • Generate SHA-256 hash
    │     • Create MongoDB document
    │     • Return file_id
    │
    └─▶ Client receives response
          { "file_id": "abc123", "status": "uploaded" }

Step 2: ANALYZE (Async)
  POST /api/v1/analysis/analyze/{file_id}
    │
    ├─▶ Create Celery task
    │     • Task ID generated
    │     • Added to audio_processing queue
    │     • Return task_id immediately
    │
    └─▶ Client receives
          { "task_id": "xyz789", "status": "pending" }

Step 3: BACKGROUND PROCESSING
  Celery Worker picks up task
    │
    ├─▶ Load audio file
    │     • Read from disk
    │     • Validate format
    │
    ├─▶ Extract features (AudioEngine)
    │     ┌───────────────────────────────┐
    │     │ • Tempo (BPM)         [20%]   │
    │     │ • Key & Scale         [40%]   │
    │     │ • Spectral features   [60%]   │
    │     │ • MFCC coefficients   [80%]   │
    │     │ • Chroma vectors      [100%]  │
    │     └───────────────────────────────┘
    │
    ├─▶ AI Analysis (if enabled)
    │     • Call Google Gemini API
    │     • Get genre/mood predictions
    │     • Timeout: 30 seconds
    │
    ├─▶ Generate embeddings
    │     • Create 128-dim vector
    │     • Store in ChromaDB
    │
    ├─▶ Save results
    │     • Update MongoDB document
    │     • Cache in Redis (1 hour TTL)
    │
    └─▶ Broadcast via WebSocket
          • Status: "completed"
          • Results available

Step 4: RETRIEVE RESULTS
  GET /api/v1/analysis/{file_id}
    │
    ├─▶ Check Redis cache first (fast path)
    │     • Hit? Return immediately
    │     • Miss? Query MongoDB
    │
    └─▶ Return complete analysis
          {
            "tempo": 128.0,
            "key": "C",
            "scale": "major",
            "mood": "energetic",
            "genre": "electronic",
            "features": {...},
            "ai_insights": {...}
          }
```

### Real-Time Updates (WebSocket)

```
┌─────────────────────────────────────────────────────┐
│         WEBSOCKET REAL-TIME COMMUNICATION            │
└─────────────────────────────────────────────────────┘

Client connects:
  WS /api/v1/ws/{client_id}
    │
    ├─▶ Handshake & authentication
    │
    └─▶ Connection established

Backend sends updates:
  
  Event: task_started
    {
      "event": "task_started",
      "task_id": "xyz789",
      "file_id": "abc123",
      "timestamp": "2025-10-04T12:00:00Z"
    }

  Event: task_progress
    {
      "event": "task_progress",
      "task_id": "xyz789",
      "progress": 45,
      "stage": "Extracting spectral features"
    }

  Event: task_completed
    {
      "event": "task_completed",
      "task_id": "xyz789",
      "file_id": "abc123",
      "results_url": "/api/v1/analysis/abc123"
    }

Client receives real-time updates
    │
    └─▶ Update UI dynamically
          • Progress bar
          • Status messages
          • Auto-refresh when done
```

---

## 🧩 Core Components

### 1. AudioEngine

```
┌─────────────────────────────────────────────────────┐
│              AUDIO ENGINE ARCHITECTURE               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  AudioEngine (samplemind/core/engine/)              │
│    │                                                 │
│    ├─▶ FileLoader                                   │
│    │     • Load audio files                         │
│    │     • Format detection                         │
│    │     • Resampling (if needed)                   │
│    │                                                 │
│    ├─▶ FeatureExtractor                             │
│    │     ├─ TempoAnalyzer                           │
│    │     │   • BPM detection                        │
│    │     │   • Beat tracking                        │
│    │     │                                           │
│    │     ├─ KeyAnalyzer                             │
│    │     │   • Key detection (C, D, E, etc.)        │
│    │     │   • Mode (major/minor)                   │
│    │     │                                           │
│    │     ├─ SpectralAnalyzer                        │
│    │     │   • Spectral centroid                    │
│    │     │   • Spectral rolloff                     │
│    │     │   • Spectral contrast                    │
│    │     │                                           │
│    │     └─ ChromaAnalyzer                          │
│    │         • Chroma features                      │
│    │         • Harmonic analysis                    │
│    │                                                 │
│    ├─▶ Cache Manager                                │
│    │     • LRU cache (1000 items)                   │
│    │     • File hash-based keys                     │
│    │     • Automatic expiration                     │
│    │                                                 │
│    └─▶ Worker Pool                                  │
│          • ThreadPoolExecutor                       │
│          • Parallel processing                      │
│          • CPU-bound optimization                   │
│                                                      │
│  Performance:                                        │
│    • 1-3 seconds per file (avg)                     │
│    • 4 parallel workers                             │
│    • Caching reduces repeat analysis by 90%         │
└─────────────────────────────────────────────────────┘
```

### 2. AI Manager

```
┌─────────────────────────────────────────────────────┐
│              AI MANAGER ARCHITECTURE                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  SampleMindAIManager                                │
│    │                                                 │
│    ├─▶ Provider Registry                            │
│    │     ├─ GoogleAIProvider (Gemini 2.5 Pro)       │
│    │     │   • Creative analysis                    │
│    │     │   • Genre classification                 │
│    │     │   • Mood detection                       │
│    │     │   • ~2-5 seconds response                │
│    │     │                                           │
│    │     ├─ OpenAIProvider (GPT-4o)                 │
│    │     │   • Production coaching                  │
│    │     │   • Mix suggestions                      │
│    │     │   • ~2-5 seconds response                │
│    │     │                                           │
│    │     └─ OllamaProvider (Local)                  │
│    │         • Fast analysis (<100ms)               │
│    │         • Privacy-focused                      │
│    │         • No API costs                         │
│    │                                                 │
│    ├─▶ Fallback Chain                               │
│    │     • Primary: Gemini                          │
│    │     • Secondary: OpenAI                        │
│    │     • Tertiary: Ollama                         │
│    │     • Automatic failover                       │
│    │                                                 │
│    ├─▶ Rate Limiter                                 │
│    │     • Token bucket algorithm                   │
│    │     • Per-provider limits                      │
│    │     • Backoff strategy                         │
│    │                                                 │
│    └─▶ Response Parser                              │
│          • JSON extraction                          │
│          • Validation                               │
│          • Error handling                           │
│                                                      │
│  Cost Optimization:                                  │
│    • Use Ollama for quick checks                    │
│    • Use Gemini for detailed analysis               │
│    • Cache AI responses (Redis)                     │
└─────────────────────────────────────────────────────┘
```

### 3. Background Task System (Celery)

```
┌─────────────────────────────────────────────────────┐
│              CELERY TASK ARCHITECTURE                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Celery Application                                 │
│    │                                                 │
│    ├─▶ Broker: Redis                                │
│    │     • Message queue                            │
│    │     • Task distribution                        │
│    │                                                 │
│    ├─▶ Backend: Redis                               │
│    │     • Result storage                           │
│    │     • Status tracking                          │
│    │                                                 │
│    ├─▶ Task Queues                                  │
│    │     ├─ default (low priority)                  │
│    │     ├─ audio_processing (medium)               │
│    │     ├─ ai_analysis (high)                      │
│    │     └─ embeddings (low)                        │
│    │                                                 │
│    ├─▶ Workers                                      │
│    │     • Concurrency: 4 per worker                │
│    │     • Autoscaling: 2-10 workers                │
│    │     • Graceful shutdown                        │
│    │                                                 │
│    ├─▶ Beat Scheduler (Periodic Tasks)              │
│    │     • Cleanup old files (daily)                │
│    │     • Cache maintenance (hourly)               │
│    │     • Health checks (every 5 min)              │
│    │                                                 │
│    └─▶ Flower Monitor                               │
│          • Web UI on port 5555                      │
│          • Real-time task tracking                  │
│          • Worker management                        │
│                                                      │
│  Tasks:                                              │
│    1. process_audio_analysis                        │
│    2. generate_embeddings                           │
│    3. batch_process_files                           │
│    4. cleanup_old_results                           │
└─────────────────────────────────────────────────────┘
```

---

## 💾 Database Architecture

### MongoDB Schema

```
┌─────────────────────────────────────────────────────┐
│              MONGODB COLLECTIONS                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Collection: users                                  │
│  ┌──────────────────────────────────────────┐      │
│  │ _id: ObjectId                             │      │
│  │ username: string (indexed, unique)        │      │
│  │ email: string (indexed, unique)           │      │
│  │ hashed_password: string                   │      │
│  │ is_active: boolean                        │      │
│  │ is_verified: boolean                      │      │
│  │ created_at: datetime                      │      │
│  │ updated_at: datetime                      │      │
│  │ stats: {                                  │      │
│  │   total_uploads: int                      │      │
│  │   total_analyses: int                     │      │
│  │ }                                         │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  Collection: audio_files                            │
│  ┌──────────────────────────────────────────┐      │
│  │ _id: ObjectId                             │      │
│  │ user_id: ObjectId (ref: users)            │      │
│  │ filename: string                          │      │
│  │ file_path: string                         │      │
│  │ file_hash: string (indexed, unique)       │      │
│  │ file_size: int                            │      │
│  │ format: string (mp3, wav, flac)           │      │
│  │ duration: float                           │      │
│  │ sample_rate: int                          │      │
│  │ tags: array[string] (indexed)             │      │
│  │ uploaded_at: datetime                     │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  Collection: analyses                               │
│  ┌──────────────────────────────────────────┐      │
│  │ _id: ObjectId                             │      │
│  │ file_id: ObjectId (ref: audio_files)      │      │
│  │ status: string (pending/processing/done)  │      │
│  │ features: {                               │      │
│  │   tempo: float                            │      │
│  │   key: string                             │      │
│  │   scale: string                           │      │
│  │   spectral_centroid: array[float]         │      │
│  │   mfcc: array[array[float]]               │      │
│  │   chroma: array[array[float]]             │      │
│  │ }                                         │      │
│  │ ai_insights: {                            │      │
│  │   provider: string                        │      │
│  │   genre: string                           │      │
│  │   mood: string                            │      │
│  │   suggestions: string                     │      │
│  │ }                                         │      │
│  │ created_at: datetime                      │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  Collection: batch_jobs                             │
│  ┌──────────────────────────────────────────┐      │
│  │ _id: ObjectId                             │      │
│  │ user_id: ObjectId                         │      │
│  │ file_ids: array[ObjectId]                 │      │
│  │ status: string                            │      │
│  │ progress: float (0-100)                   │      │
│  │ started_at: datetime                      │      │
│  │ completed_at: datetime                    │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  Indexes:                                           │
│    • users: username, email                        │
│    • audio_files: file_hash, user_id, tags         │
│    • analyses: file_id, status                     │
│    • batch_jobs: user_id, status                   │
└─────────────────────────────────────────────────────┘
```

### Redis Key Patterns

```
┌─────────────────────────────────────────────────────┐
│              REDIS KEY PATTERNS                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Cache Keys:                                        │
│    cache:analysis:{file_hash}       TTL: 1 hour    │
│    cache:audio_features:{file_id}   TTL: 24 hours  │
│    cache:ai_response:{file_id}      TTL: 1 week    │
│                                                      │
│  Session Keys:                                      │
│    session:{session_id}             TTL: 7 days    │
│    access_token:{user_id}           TTL: 30 min    │
│    refresh_token:{token_id}         TTL: 7 days    │
│                                                      │
│  Rate Limiting:                                     │
│    ratelimit:{user_id}:{endpoint}   TTL: 1 minute  │
│    ratelimit:ip:{ip_address}        TTL: 1 hour    │
│                                                      │
│  Task Status:                                       │
│    celery-task-meta-{task_id}      TTL: 24 hours  │
│                                                      │
│  Temporary Data:                                    │
│    temp:upload:{upload_id}          TTL: 1 hour    │
│    temp:processing:{file_id}        TTL: 30 min    │
└─────────────────────────────────────────────────────┘
```

### ChromaDB Collections

```
┌─────────────────────────────────────────────────────┐
│              CHROMADB STRUCTURE                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Collection: audio_embeddings                       │
│    │                                                 │
│    ├─▶ Vectors: 128-dimensional                     │
│    │     • Normalized (L2 norm = 1)                 │
│    │     • Generated from MFCC features             │
│    │                                                 │
│    ├─▶ Metadata                                     │
│    │     • file_id: ObjectId                        │
│    │     • tempo: float                             │
│    │     • key: string                              │
│    │     • genre: string                            │
│    │     • tags: array[string]                      │
│    │                                                 │
│    └─▶ Similarity Search                            │
│          • Query: vector (128-dim)                  │
│          • Method: Cosine similarity                │
│          • Results: Top K matches                   │
│          • Speed: <50ms for 10,000 vectors          │
│                                                      │
│  Usage:                                              │
│    1. Find similar samples                          │
│    2. Genre clustering                              │
│    3. Mood-based recommendations                    │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

### Authentication Flow

```
┌─────────────────────────────────────────────────────┐
│           JWT AUTHENTICATION FLOW                    │
└─────────────────────────────────────────────────────┘

Step 1: USER REGISTRATION
  POST /api/v1/auth/register
    │
    ├─▶ Validate input (email, username, password)
    │
    ├─▶ Check uniqueness (email & username)
    │
    ├─▶ Hash password (bcrypt, 12 rounds)
    │
    ├─▶ Create user in MongoDB
    │
    └─▶ Return success (no auto-login)

Step 2: USER LOGIN
  POST /api/v1/auth/login
    │
    ├─▶ Find user by username/email
    │
    ├─▶ Verify password (bcrypt)
    │
    ├─▶ Generate tokens:
    │     ┌─────────────────────────────────┐
    │     │ Access Token (JWT)              │
    │     │   • Expires: 30 minutes         │
    │     │   • Payload: user_id, username  │
    │     │   • Signed: HS256               │
    │     └─────────────────────────────────┘
    │     ┌─────────────────────────────────┐
    │     │ Refresh Token (JWT)             │
    │     │   • Expires: 7 days             │
    │     │   • Payload: user_id, token_id  │
    │     │   • Signed: HS256               │
    │     └─────────────────────────────────┘
    │
    └─▶ Return both tokens

Step 3: AUTHENTICATED REQUEST
  GET /api/v1/audio (with Authorization header)
    │
    ├─▶ Extract token from header
    │     "Authorization: Bearer {access_token}"
    │
    ├─▶ Verify token signature
    │
    ├─▶ Check expiration
    │
    ├─▶ Extract user_id from payload
    │
    └─▶ Process request with user context

Step 4: TOKEN REFRESH
  POST /api/v1/auth/refresh (with refresh token)
    │
    ├─▶ Verify refresh token
    │
    ├─▶ Check if token is blacklisted
    │
    ├─▶ Generate new access token
    │
    └─▶ Return new access token
```

### Security Layers

```
┌─────────────────────────────────────────────────────┐
│              SECURITY LAYERS                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Layer 1: NETWORK                                   │
│    • HTTPS/TLS 1.3 only                            │
│    • SSL certificates (Let's Encrypt)              │
│    • Firewall rules (UFW/iptables)                 │
│                                                      │
│  Layer 2: API GATEWAY                               │
│    • CORS whitelist                                │
│    • Rate limiting (Redis)                         │
│    • Request size limits (50MB)                    │
│    • IP blocking                                   │
│                                                      │
│  Layer 3: AUTHENTICATION                            │
│    • JWT tokens (HS256)                            │
│    • Password hashing (bcrypt, 12 rounds)          │
│    • Token expiration                              │
│    • Refresh token rotation                        │
│                                                      │
│  Layer 4: AUTHORIZATION                             │
│    • Role-based access control (RBAC)              │
│    • Resource ownership validation                 │
│    • Endpoint-level permissions                    │
│                                                      │
│  Layer 5: DATA                                      │
│    • Encryption at rest (MongoDB)                  │
│    • Encrypted backups                             │
│    • Secure file storage                           │
│    • API key encryption                            │
│                                                      │
│  Layer 6: MONITORING                                │
│    • Failed login tracking                         │
│    • Suspicious activity detection                 │
│    • Security audit logs                           │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Architecture

### Docker Compose (Development)

```
┌─────────────────────────────────────────────────────┐
│         DOCKER COMPOSE ARCHITECTURE                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Network: samplemind-network (bridge)               │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Container: samplemind-api                │      │
│  │    Port: 8000                             │      │
│  │    Image: samplemind/api:latest           │      │
│  │    Depends: mongodb, redis, chromadb      │      │
│  │    Volumes:                               │      │
│  │      - ./src:/app/src (hot-reload)        │      │
│  │      - ./data:/data (persistent)          │      │
│  └──────────────────────────────────────────┘      │
│                    ▼                                 │
│  ┌──────────────────────────────────────────┐      │
│  │  Container: mongodb                       │      │
│  │    Port: 27017                            │      │
│  │    Image: mongo:7.0                       │      │
│  │    Volume: mongodb_data                   │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Container: redis                         │      │
│  │    Port: 6379                             │      │
│  │    Image: redis:7.2-alpine                │      │
│  │    Volume: redis_data                     │      │
│  │    Memory: 1GB limit                      │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Container: chromadb                      │      │
│  │    Port: 8002                             │      │
│  │    Image: chromadb/chroma:latest          │      │
│  │    Volume: chromadb_data                  │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Container: celery-worker                 │      │
│  │    Image: samplemind/api:latest           │      │
│  │    Command: celery worker                 │      │
│  │    Concurrency: 4                         │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Container: flower                        │      │
│  │    Port: 5555                             │      │
│  │    Image: samplemind/api:latest           │      │
│  │    Command: celery flower                 │      │
│  └──────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

### Kubernetes (Production)

```
┌─────────────────────────────────────────────────────┐
│         KUBERNETES DEPLOYMENT                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Namespace: samplemind-prod                         │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Deployment: api                          │      │
│  │    Replicas: 3 (auto-scaling 2-10)       │      │
│  │    Resources:                             │      │
│  │      CPU: 500m - 2000m                    │      │
│  │      Memory: 512Mi - 2Gi                  │      │
│  │    Probes:                                │      │
│  │      Liveness: /health                    │      │
│  │      Readiness: /api/v1/health/ready      │      │
│  └──────────────────────────────────────────┘      │
│          ▼                                           │
│  ┌──────────────────────────────────────────┐      │
│  │  Service: api-service (ClusterIP)         │      │
│  │    Port: 8000                             │      │
│  │    Selector: app=api                      │      │
│  └──────────────────────────────────────────┘      │
│          ▼                                           │
│  ┌──────────────────────────────────────────┐      │
│  │  Ingress: samplemind-ingress              │      │
│  │    Host: api.samplemind.ai                │      │
│  │    TLS: cert-manager                      │      │
│  │    Rules:                                 │      │
│  │      /api → api-service:8000              │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  StatefulSet: mongodb                     │      │
│  │    Replicas: 3 (replica set)              │      │
│  │    Storage: 50Gi PVC per pod              │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  StatefulSet: redis                       │      │
│  │    Replicas: 3 (sentinel)                 │      │
│  │    Storage: 10Gi PVC per pod              │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │  Deployment: celery-worker                │      │
│  │    Replicas: 5 (auto-scaling 2-20)       │      │
│  │    Queue: audio_processing                │      │
│  └──────────────────────────────────────────┘      │
│                                                      │
│  ConfigMaps:                                        │
│    • app-config (environment variables)            │
│    • nginx-config (proxy settings)                 │
│                                                      │
│  Secrets:                                           │
│    • jwt-secret                                    │
│    • api-keys                                      │
│    • db-credentials                                │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Performance Optimization

### Caching Strategy

```
┌─────────────────────────────────────────────────────┐
│           MULTI-LEVEL CACHING                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Level 1: BROWSER CACHE (Client-side)              │
│    • Static assets: 1 year                         │
│    • API responses: 5 minutes                      │
│    • Service Worker: Offline support               │
│                                                      │
│  Level 2: CDN CACHE (Edge)                         │
│    • Static files: CloudFlare                      │
│    • Images: Optimized & cached                    │
│    • API responses: Geo-distributed                │
│                                                      │
│  Level 3: APPLICATION CACHE (Redis)                │
│    ┌─────────────────────────────────────┐         │
│    │ Analysis results: 1 hour TTL        │         │
│    │ Audio features: 24 hours TTL        │         │
│    │ AI responses: 1 week TTL            │         │
│    │ User sessions: 7 days TTL           │         │
│    └─────────────────────────────────────┘         │
│                                                      │
│  Level 4: IN-MEMORY CACHE (Python LRU)             │
│    • AudioEngine: 1000 items                       │
│    • File metadata: 500 items                      │
│    • Hot path data: Unlimited                      │
│                                                      │
│  Cache Invalidation:                                │
│    • Time-based (TTL)                              │
│    • Event-based (file update)                     │
│    • Manual (admin action)                         │
└─────────────────────────────────────────────────────┘
```

### Performance Benchmarks

```
┌─────────────────────────────────────────────────────┐
│           PERFORMANCE TARGETS                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  API Response Times:                                │
│    ├─ GET /health              < 10ms    ████████  │
│    ├─ POST /auth/login         < 200ms   ████████  │
│    ├─ POST /audio/upload       varies    ████████  │
│    ├─ GET /audio               < 100ms   ████████  │
│    └─ GET /analysis/{id}       < 50ms    ████████  │
│                                                      │
│  Processing Times:                                  │
│    ├─ Audio analysis (basic)   1-2s      ████████  │
│    ├─ Audio analysis (detailed) 2-3s     ████████  │
│    ├─ AI analysis (Gemini)     2-5s      ████████  │
│    ├─ Embedding generation     500ms     ████████  │
│    └─ Similarity search        < 50ms    ████████  │
│                                                      │
│  Throughput:                                        │
│    ├─ API requests             1000/sec            │
│    ├─ Concurrent users         500                 │
│    ├─ File uploads             50/sec              │
│    └─ Analysis tasks           20/sec              │
│                                                      │
│  Resource Usage:                                    │
│    ├─ CPU (per pod)            0.5-2 cores         │
│    ├─ Memory (per pod)         512MB-2GB           │
│    ├─ Storage (total)          100GB+              │
│    └─ Network                  100Mbps+            │
└─────────────────────────────────────────────────────┘
```

---

## 🔌 External Integrations

### AI Providers

```
┌─────────────────────────────────────────────────────┐
│           EXTERNAL AI SERVICES                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Google Gemini API                                  │
│    ├─ Model: gemini-2.5-pro                         │
│    ├─ Endpoint: generativelanguage.googleapis.com  │
│    ├─ Rate Limit: 60 requests/minute               │
│    ├─ Cost: $0.00125 per 1K chars                  │
│    └─ Use Case: Creative music analysis            │
│                                                      │
│  OpenAI API                                         │
│    ├─ Model: gpt-4o                                 │
│    ├─ Endpoint: api.openai.com/v1                  │
│    ├─ Rate Limit: 500 requests/minute              │
│    ├─ Cost: $0.01 per 1K tokens                    │
│    └─ Use Case: Production coaching                │
│                                                      │
│  Ollama (Self-Hosted)                               │
│    ├─ Models: phi3, gemma2, qwen2.5                 │
│    ├─ Endpoint: localhost:11434                     │
│    ├─ Rate Limit: Unlimited                        │
│    ├─ Cost: $0 (local compute)                     │
│    └─ Use Case: Fast, private analysis             │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Technology Stack Summary

```
┌─────────────────────────────────────────────────────┐
│           COMPLETE TECH STACK                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Backend:                                           │
│    • Python 3.12                                   │
│    • FastAPI 0.105+                                │
│    • Uvicorn (ASGI server)                         │
│    • Celery 5.3+ (task queue)                      │
│    • Pydantic (validation)                         │
│                                                      │
│  Audio Processing:                                  │
│    • librosa (analysis)                            │
│    • soundfile (I/O)                               │
│    • scipy (signal processing)                     │
│    • numpy (math)                                  │
│                                                      │
│  Databases:                                         │
│    • MongoDB 7.0 (Beanie ODM)                      │
│    • Redis 7.2 (cache + broker)                    │
│    • ChromaDB 0.4 (vectors)                        │
│                                                      │
│  AI/ML:                                             │
│    • Google Gemini 2.5 Pro                         │
│    • OpenAI GPT-4o                                 │
│    • Ollama (local LLMs)                           │
│    • sentence-transformers                         │
│                                                      │
│  Frontend:                                          │
│    • Next.js 14 (React 18)                         │
│    • TypeScript 5                                  │
│    • Tailwind CSS 3                                │
│    • Zustand (state)                               │
│    • Axios (HTTP)                                  │
│    • WaveSurfer.js (audio viz)                     │
│                                                      │
│  DevOps:                                            │
│    • Docker & Docker Compose                       │
│    • Kubernetes (K8s)                              │
│    • Nginx (reverse proxy)                         │
│    • GitHub Actions (CI/CD)                        │
│                                                      │
│  Testing:                                           │
│    • pytest (unit + integration)                   │
│    • Playwright (E2E)                              │
│    • Locust (load testing)                         │
│                                                      │
│  Monitoring:                                        │
│    • Flower (Celery)                               │
│    • Prometheus (metrics)                          │
│    • Grafana (dashboards)                          │
└─────────────────────────────────────────────────────┘
```

---

## 📚 Related Documentation

| Document | Purpose | For Who |
|----------|---------|---------|
| [API_REFERENCE.md](./API_REFERENCE.md) | Complete API docs | Developers |
| [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) | Schema details | DBAs |
| [SECURITY.md](./SECURITY.md) | Security guide | Security team |
| [PERFORMANCE.md](./PERFORMANCE.md) | Optimization | SREs |
| [DEVELOPMENT.md](./DEVELOPMENT.md) | Dev setup | Developers |

---

## 🎯 Key Architectural Decisions

### 1. Why FastAPI?
- **Performance**: Async/await → high concurrency
- **Validation**: Pydantic → type safety
- **Documentation**: Auto-generated OpenAPI docs
- **Modern**: Python 3.12+ features

### 2. Why MongoDB?
- **Flexibility**: Schema-less for evolving data
- **Performance**: Fast reads/writes
- **Scalability**: Easy horizontal scaling
- **Integration**: Great with Python (Beanie ODM)

### 3. Why Celery?
- **Async Tasks**: Long-running audio processing
- **Scalability**: Easy to add workers
- **Reliability**: Task retry & failure handling
- **Monitoring**: Flower UI

### 4. Why Hybrid AI?
- **Speed**: Ollama for quick checks (<100ms)
- **Quality**: Gemini/GPT-4 for deep analysis
- **Cost**: Balance API costs with local compute
- **Reliability**: Fallback chain for uptime

### 5. Why ChromaDB?
- **Vector Search**: Fast similarity matching
- **Simple**: Easy to integrate & deploy
- **Scalable**: Handles millions of vectors
- **Open Source**: No vendor lock-in

---

**Last Updated:** 2025-10-04 | **Version:** 1.0 Beta

**Questions?** Check the [full documentation index](./DOCUMENTATION_INDEX.md)

*Built with ❤️ and lots of architectural thinking*
