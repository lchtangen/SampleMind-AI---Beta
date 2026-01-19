# 🚀 SampleMind AI - Quick Reference Guide

## One-Command Startup

```bash
# Start databases
docker-compose up -d mongodb redis chromadb

# Start API
./start_api.sh
```

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/api/docs | Interactive Swagger UI |
| MongoDB | mongodb://localhost:27017 | Database |
| Redis | redis://localhost:6379 | Cache & Sessions |
| ChromaDB | http://localhost:8002 | Vector Search |

## Quick Test

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload audio
curl -X POST http://localhost:8000/api/v1/audio/upload \
  -F "file=@test_audio_samples/test_chord_120bpm.wav"

# Analyze
curl -X POST http://localhost:8000/api/v1/audio/analyze/{file_id} \
  -H "Content-Type: application/json" \
  -d '{"analysis_level": "standard", "include_ai": true}'
```

## Project Structure

```
src/samplemind/
├── core/
│   ├── database/          # MongoDB, Redis, ChromaDB
│   └── engine/            # Audio processing
├── interfaces/
│   └── api/               # FastAPI backend
├── integrations/          # AI providers
└── utils/                 # Utilities
```

## Key Technologies

- **Backend**: FastAPI + Python 3.12
- **Databases**: MongoDB (Beanie ODM), Redis, ChromaDB
- **AI**: Google Gemini 2.5 Pro, OpenAI GPT-4
- **Audio**: librosa, soundfile
- **Deployment**: Docker Compose, K8s-ready

## Documentation

- **Tasks 1 & 2 Complete**: `TASKS_1_2_COMPLETE.md`
- **API Documentation**: `src/samplemind/interfaces/api/README.md`
- **Project Structure**: `PROJECT_STRUCTURE_CLEAN.md`
- **Quick Start**: `QUICKSTART.md`

## Next Steps

1. ✅ Task 1: FastAPI Backend - **COMPLETE**
2. ✅ Task 2: Database Layer - **COMPLETE**
3. 🚧 Task 3: Authentication - Ready to start
4. ⏳ Task 4: Background Tasks - Queued
5. ⏳ Task 5-10: Frontend, Plugins, Deploy - Queued

---

**Status: 20% Complete | 2/10 Tasks Done | Backend Ready for Frontend!**
