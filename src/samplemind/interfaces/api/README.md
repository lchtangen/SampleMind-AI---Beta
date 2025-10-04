# 🎵 SampleMind AI - Backend API

Production-ready FastAPI backend for AI-powered music production.

## 🚀 Quick Start

### Start the Server

```bash
# From project root
cd /home/lchta/Projects/samplemind-ai-v6

# Activate virtual environment
source .venv/bin/activate

# Start the API server
python -m uvicorn src.samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📚 API Endpoints

### Health Check
```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Readiness probe (K8s)
curl http://localhost:8000/api/v1/health/ready

# Liveness probe (K8s)
curl http://localhost:8000/api/v1/health/live
```

### Audio Upload & Analysis
```bash
# Upload audio file
curl -X POST "http://localhost:8000/api/v1/audio/upload" \
  -F "file=@/path/to/audio.wav"

# Response:
# {
#   "file_id": "abc123...",
#   "filename": "audio.wav",
#   "file_size": 1234567,
#   "message": "File uploaded successfully"
# }

# Analyze audio
curl -X POST "http://localhost:8000/api/v1/audio/analyze/abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_level": "standard",
    "include_ai": true,
    "ai_provider": "google_ai"
  }'

# List uploaded files
curl "http://localhost:8000/api/v1/audio/files?page=1&page_size=50"
```

### AI Providers
```bash
# List available AI providers
curl http://localhost:8000/api/v1/ai/providers

# Response:
# [
#   {
#     "name": "google_ai",
#     "status": "available",
#     "model": "gemini-2.5-pro",
#     "features": ["comprehensive_analysis", "production_coaching", "creative_suggestions"],
#     "avg_response_time": 50.2
#   },
#   {
#     "name": "openai",
#     "status": "available",
#     "model": "gpt-4",
#     "features": ["comprehensive_analysis", "production_coaching", "creative_suggestions"],
#     "avg_response_time": 30.5
#   }
# ]
```

### Batch Processing
```bash
# Upload multiple files for batch processing
curl -X POST "http://localhost:8000/api/v1/batch/upload" \
  -F "files=@audio1.wav" \
  -F "files=@audio2.wav" \
  -F "files=@audio3.wav"

# Get batch status
curl "http://localhost:8000/api/v1/batch/status/{batch_id}"
```

### WebSocket (Real-time Updates)
```javascript
// JavaScript example
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/client-123');

ws.onopen = () => {
  console.log('Connected to SampleMind AI');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress update:', data);
};
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Application
ENVIRONMENT=development
DEBUG=true

# AI Providers
GOOGLE_AI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_AI_PROVIDER=google_ai

# Server
HOST=0.0.0.0
PORT=8000
MAX_WORKERS=4

# File Upload
MAX_UPLOAD_SIZE_MB=100

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_ENABLED=true
```

## 🏗️ Architecture

```
src/samplemind/interfaces/api/
├── __init__.py           # Package metadata
├── main.py               # FastAPI application & lifespan
├── config.py             # Configuration management
├── exceptions.py         # Custom exceptions
├── routes/               # API endpoints
│   ├── health.py         # Health checks
│   ├── audio.py          # Audio upload/analysis
│   ├── ai.py             # AI provider management
│   ├── batch.py          # Batch processing
│   └── websocket.py      # WebSocket connections
└── schemas/              # Pydantic models
    ├── common.py         # Shared schemas
    ├── audio.py          # Audio schemas
    ├── ai.py             # AI schemas
    └── batch.py          # Batch schemas
```

## 🧪 Testing

```bash
# Run API tests
pytest tests/integration/api/ -v

# Test with coverage
pytest tests/integration/api/ --cov=src.samplemind.interfaces.api
```

## 📦 Dependencies

Core dependencies managed in `pyproject.toml`:
- **fastapi** - Modern web framework
- **uvicorn** - ASGI server
- **pydantic** & **pydantic-settings** - Data validation
- **python-multipart** - File upload support

## 🔐 Security

- CORS middleware configured for frontend access
- File upload validation (type, size)
- Rate limiting (in-memory for MVP)
- Input validation via Pydantic
- Error sanitization in production mode

## 📈 Performance

- Async/await throughout for high concurrency
- Connection pooling for AI providers
- In-memory caching for audio analysis
- Efficient file handling with chunked uploads
- WebSocket for real-time updates without polling

## 🚢 Deployment

### Docker
```bash
# Build image
docker build -t samplemind-api:latest .

# Run container
docker run -p 8000:8000 --env-file .env samplemind-api:latest
```

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
```

## 📝 API Response Examples

### Successful Audio Analysis
```json
{
  "analysis_id": "def456...",
  "file_id": "abc123...",
  "duration": 180.5,
  "tempo": 128.0,
  "key": "C",
  "mode": "major",
  "time_signature": [4, 4],
  "spectral_features": {
    "centroid": [1500.2, 1520.5, ...],
    "bandwidth": [800.1, 820.3, ...]
  },
  "ai_analysis": {
    "provider": "google_ai",
    "summary": "Energetic electronic dance track with driving bassline...",
    "production_tips": ["Add sidechain compression", "Boost highs"],
    "fl_studio_recommendations": ["Fruity Limiter", "Maximus"]
  },
  "analysis_level": "standard",
  "processing_time": 5.2,
  "analyzed_at": "2025-10-03T23:50:00Z"
}
```

### Error Response
```json
{
  "error": "file_validation_error",
  "message": "Unsupported file type: audio/aac",
  "details": {
    "allowed_formats": ["audio/wav", "audio/mp3", "audio/flac"]
  }
}
```

## 🤝 Integration with CLI

The API integrates seamlessly with the existing CLI:

```python
from samplemind.interfaces.api.main import get_app_state

# Access AudioEngine
audio_engine = get_app_state("audio_engine")

# Access AI Manager
ai_manager = get_app_state("ai_manager")
```

## 📊 Monitoring

Health check endpoints suitable for:
- **Kubernetes liveness/readiness probes**
- **Load balancer health checks**
- **Monitoring systems (Prometheus, Datadog)**

## 🆘 Troubleshooting

### API won't start
```bash
# Check if port is available
lsof -i :8000

# Check environment variables
cat .env

# Check logs
tail -f logs/api.log
```

### AI providers unavailable
```bash
# Verify API keys
curl http://localhost:8000/api/v1/ai/providers

# Check .env file has correct keys
echo $GOOGLE_AI_API_KEY
```

---

**Built with ❤️ for musicians and producers**
