# SampleMind AI API Documentation

**Version**: v6.0.0
**Status**: Production Ready
**Last Updated**: February 3, 2026

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Overview](#api-overview)
3. [Authentication](#authentication)
4. [Core Endpoints](#core-endpoints)
5. [Request/Response Examples](#requestresponse-examples)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [WebSocket API](#websocket-api)
9. [Integration Patterns](#integration-patterns)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Accessing API Documentation

The SampleMind AI API provides both interactive and comprehensive documentation:

**Interactive Documentation:**
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

**OpenAPI Specification:**
- **JSON Schema**: http://localhost:8000/api/openapi.json

### Running the API Server

```bash
# Start the development API server
make dev

# Or manually with uvicorn
uvicorn samplemind.interfaces.api.main:app --host 0.0.0.0 --port 8000 --reload

# With Docker
docker-compose up api
```

The API will be available at `http://localhost:8000`

### First Request

```bash
# Health check (requires no authentication)
curl http://localhost:8000/api/v1/health

# Response:
# {
#   "status": "healthy",
#   "version": "6.0.0",
#   "environment": "development",
#   "components": {
#     "audio_engine": "healthy",
#     "ai_providers": "3 available"
#   }
# }
```

---

## API Overview

### Base URL

```
http://localhost:8000/api/v1
```

### API Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Audio Upload & Processing** | ✅ Stable | Upload audio files, extract features, apply effects |
| **Semantic Search** | ✅ Stable | Search by natural language description |
| **AI Analysis** | ✅ Stable | Multi-provider AI analysis (Gemini, OpenAI, Local) |
| **Batch Processing** | ✅ Stable | Process multiple files asynchronously |
| **Collections** | ✅ Stable | Organize samples into collections |
| **Authentication** | ✅ Stable | JWT-based API authentication |
| **WebSocket** | ✅ Stable | Real-time streaming and notifications |
| **Cloud Sync** | ✅ Beta | Sync data to cloud storage (S3, local, mock) |
| **Session Management** | ✅ Stable | Save and restore analysis sessions |

### Supported Audio Formats

| Format | MIME Type | Notes |
|--------|-----------|-------|
| WAV | `audio/wav` | Recommended, lossless |
| MP3 | `audio/mpeg` | Widely compatible |
| FLAC | `audio/flac` | Lossless compression |
| AIFF | `audio/aiff` | Uncompressed |
| OGG | `audio/ogg` | Compressed, open format |
| M4A | `audio/mp4` | Apple format |

**Max File Size**: 100 MB
**Max Concurrent Uploads**: 10

---

## Authentication

### Methods

SampleMind AI API supports two authentication methods:

#### 1. API Key Authentication (Simple)

```bash
# Include API key in Authorization header
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/health
```

#### 2. JWT Token Authentication (Production)

```bash
# Step 1: Get authentication token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIs...",
#   "token_type": "bearer",
#   "expires_in": 3600
# }

# Step 2: Use token in Authorization header
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  http://localhost:8000/api/v1/health
```

### Configuration

Edit `.env` or config file:

```env
# Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys
API_KEY=your-api-key-here

# AI Providers
GOOGLE_AI_API_KEY=your-google-key
OPENAI_API_KEY=your-openai-key
```

### Protected Endpoints

Most endpoints require authentication. Exceptions:

- `GET /health` - Public health check
- `GET /health/ready` - Public readiness check
- `GET /health/live` - Public liveness check
- `POST /auth/register` - Public registration (if enabled)

---

## Core Endpoints

### Health & Status

#### GET `/health` - Health Check

Check API and component status.

**Request:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "6.0.0",
  "environment": "development",
  "components": {
    "audio_engine": "healthy",
    "ai_providers": "3 available"
  }
}
```

**Status Codes:**
- `200 OK` - API is healthy
- `503 Service Unavailable` - Critical components unavailable

---

### Audio Operations

#### POST `/audio/upload` - Upload Audio File

Upload an audio file for processing.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/audio/upload \
  -F "file=@song.wav" \
  -H "Authorization: Bearer <token>"
```

**Request Parameters:**
- `file` (FormData, required) - Audio file to upload
- `filename` (optional) - Override filename

**Response:**
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "song.wav",
  "file_size": 5242880,
  "message": "File uploaded successfully"
}
```

**Status Codes:**
- `201 Created` - File uploaded successfully
- `400 Bad Request` - Invalid file format or too large
- `413 Request Entity Too Large` - File exceeds 100 MB limit

---

#### POST `/audio/analyze/{file_id}` - Analyze Audio

Extract and analyze audio features from an uploaded file.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/audio/analyze/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_level": "standard",
    "include_ai": true
  }'
```

**Request Parameters:**
- `file_id` (path, required) - ID of uploaded file
- `analysis_level` (query, optional) - `basic`, `standard`, `detailed`, `professional` (default: `standard`)
- `include_ai` (query, optional) - Include AI analysis (default: `false`)

**Response:**
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "duration": 245.5,
  "tempo": 120.0,
  "key": "C",
  "mode": "major",
  "time_signature": [4, 4],
  "spectral_features": {
    "centroid_mean": 2150.5,
    "rolloff_mean": 8950.3
  },
  "ai_analysis": {
    "genre": "electronic",
    "mood": ["energetic", "uplifting"],
    "bpm_confidence": 0.95
  },
  "analysis_level": "standard",
  "processing_time": 2.34,
  "analyzed_at": "2026-02-03T12:30:45Z"
}
```

**Analysis Levels:**

| Level | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| `basic` | <100ms | 70% | Quick preview |
| `standard` | <500ms | 85% | General use (recommended) |
| `detailed` | 1-3s | 95% | Professional analysis |
| `professional` | 3-10s | 98% | Mastering/reference |

**Status Codes:**
- `200 OK` - Analysis completed
- `202 Accepted` - Analysis started (if async)
- `404 Not Found` - File not found
- `503 Service Unavailable` - Analysis engine unavailable

---

#### POST `/audio/process/{file_id}` - Process Audio

Apply audio processing effects to an uploaded file.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/audio/process/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "steps": {
      "normalize": true,
      "target_loudness": -14,
      "trim_silence": true
    },
    "background": false,
    "return_path": true
  }'
```

**Request Parameters:**
- `file_id` (path, required) - ID of uploaded file
- `steps` (body, required) - Processing operations to apply
- `background` (optional) - Run in background (default: `false`)
- `return_path` (optional) - Return output file path (default: `true`)

**Available Processing Steps:**

```json
{
  "normalize": true,           // Normalize loudness to -3dB
  "target_loudness": -14,      // Target LUFS (Spotify: -14)
  "trim_silence": true,        // Remove leading/trailing silence
  "convert_mono": false,       // Convert to mono
  "sample_rate": 44100,        // Resample (optional)
  "remove_dc": true,           // Remove DC offset
  "apply_fade": true,          // Apply fade in/out
  "fade_duration": 0.5         // Fade duration in seconds
}
```

**Response:**
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Audio processing completed successfully",
  "output_path": "/path/to/processed/file.wav",
  "processing_time": 5.67,
  "processing_steps": [
    "normalize",
    "trim_silence"
  ]
}
```

**Status Codes:**
- `200 OK` - Processing completed
- `202 Accepted` - Processing started (if async)
- `400 Bad Request` - Invalid processing steps
- `404 Not Found` - File not found

---

#### GET `/audio/list` - List Audio Files

Get a paginated list of uploaded audio files.

**Request:**
```bash
curl "http://localhost:8000/api/v1/audio/list?page=1&page_size=20&file_type=wav" \
  -H "Authorization: Bearer <token>"
```

**Request Parameters:**
- `page` (query, optional) - Page number (default: `1`)
- `page_size` (query, optional) - Items per page (default: `50`, max: `100`)
- `file_type` (query, optional) - Filter by type (`wav`, `mp3`, etc.)

**Response:**
```json
[
  {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "song.wav",
    "file_size": 5242880,
    "upload_time": "2026-02-03T12:00:00Z",
    "mime_type": "audio/wav",
    "duration": 245.5
  }
]
```

---

### Semantic Search

#### POST `/ai/search/semantic` - Semantic Search

Search audio library using natural language description.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/search/semantic \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "upbeat electronic drum loop with jazz influence",
    "limit": 10
  }'
```

**Request Parameters:**
- `query` (required) - Natural language search description
- `limit` (optional) - Max results (default: `10`, max: `100`)

**Response:**
```json
{
  "results": [
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440001",
      "score": 0.92,
      "filename": "jazz_electronic_loop.wav",
      "metadata": {
        "tempo": 120,
        "key": "C",
        "genre": "electronic"
      }
    },
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440002",
      "score": 0.87,
      "filename": "upbeat_drums.wav",
      "metadata": {
        "tempo": 128,
        "key": "D",
        "genre": "house"
      }
    }
  ],
  "total_found": 2
}
```

**Search Tips:**
- Be descriptive: "warm, analog synth pad" vs. "synth"
- Include tempo: "120 BPM upbeat electronic"
- Mention mood: "dark, moody, cinematic"
- Specify instruments: "acoustic piano, strings, drums"

**Status Codes:**
- `200 OK` - Search completed
- `503 Service Unavailable` - Neural engine unavailable

---

### Collections

#### POST `/collections` - Create Collection

Create a new collection to organize samples.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/collections \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronic Drums",
    "description": "High-quality electronic drum samples"
  }'
```

**Response:**
```json
{
  "id": "electronic_drums",
  "name": "Electronic Drums",
  "type": "custom",
  "description": "High-quality electronic drum samples",
  "created_at": "2026-02-03T12:00:00Z",
  "sample_count": 0
}
```

#### POST `/collections/{collection_id}/samples` - Add Sample

Add a sample to a collection.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/collections/electronic_drums/samples \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "metadata": {
      "tempo": 120,
      "key": "C"
    }
  }'
```

#### GET `/collections` - List Collections

**Request:**
```bash
curl http://localhost:8000/api/v1/collections \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
[
  {
    "id": "electronic_drums",
    "name": "Electronic Drums",
    "type": "custom",
    "created_at": "2026-02-03T12:00:00Z",
    "sample_count": 42
  },
  {
    "id": "favorites",
    "name": "Favorites",
    "type": "favorites",
    "created_at": "2026-02-01T10:00:00Z",
    "sample_count": 15
  }
]
```

---

### Batch Processing

#### POST `/batch/analyze` - Analyze Multiple Files

Analyze multiple files in a batch operation with progress tracking.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/batch/analyze \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "550e8400-e29b-41d4-a716-446655440001",
      "550e8400-e29b-41d4-a716-446655440002"
    ],
    "analysis_level": "standard",
    "include_ai": false
  }'
```

**Response:**
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "processing",
  "total_files": 3,
  "processed": 1,
  "failed": 0,
  "percent_complete": 33.3,
  "eta_seconds": 45
}
```

#### GET `/batch/{batch_id}` - Get Batch Status

Poll batch status or use WebSocket for real-time updates.

**Request:**
```bash
curl http://localhost:8000/api/v1/batch/550e8400-e29b-41d4-a716-446655440003 \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440003",
  "status": "completed",
  "total_files": 3,
  "processed": 3,
  "failed": 0,
  "percent_complete": 100,
  "results": [
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "success",
      "analysis_id": "analysis-001",
      "processing_time": 2.34
    }
  ]
}
```

---

## Request/Response Examples

### Complete Workflow Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key"
HEADERS = {"X-API-Key": API_KEY}

# 1. Upload an audio file
print("1. Uploading audio file...")
with open("sample.wav", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/audio/upload",
        files=files,
        headers=HEADERS
    )

upload_response = response.json()
file_id = upload_response["file_id"]
print(f"   File uploaded: {file_id}")

# 2. Analyze the audio
print("2. Analyzing audio...")
analyze_response = requests.post(
    f"{BASE_URL}/audio/analyze/{file_id}",
    params={"analysis_level": "standard", "include_ai": True},
    headers=HEADERS
).json()

print(f"   Tempo: {analyze_response['tempo']} BPM")
print(f"   Key: {analyze_response['key']} {analyze_response['mode']}")
print(f"   Processing time: {analyze_response['processing_time']}s")

# 3. Semantic search for similar samples
print("3. Searching for similar samples...")
search_response = requests.post(
    f"{BASE_URL}/ai/search/semantic",
    json={
        "query": "upbeat electronic drum loop",
        "limit": 5
    },
    headers=HEADERS
).json()

print(f"   Found {search_response['total_found']} similar samples")
for result in search_response["results"]:
    print(f"   - {result['filename']} (score: {result['score']:.2f})")

# 4. Create a collection and add the file
print("4. Creating collection...")
collection_response = requests.post(
    f"{BASE_URL}/collections",
    json={"name": "My Samples", "description": "My favorite samples"},
    headers=HEADERS
).json()

collection_id = collection_response["id"]
print(f"   Collection created: {collection_id}")

# 5. Add file to collection
print("5. Adding file to collection...")
requests.post(
    f"{BASE_URL}/collections/{collection_id}/samples",
    json={"file_id": file_id},
    headers=HEADERS
)
print(f"   File added to collection")

print("\n✅ Workflow complete!")
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "invalid_file_format",
  "message": "Unsupported audio format: application/json",
  "details": {
    "allowed_formats": ["audio/wav", "audio/mpeg", "audio/flac", "audio/ogg"]
  }
}
```

### Common Error Codes

| Code | Error | Cause | Solution |
|------|-------|-------|----------|
| `400` | `invalid_file_format` | Wrong audio format | Use WAV, MP3, FLAC, OGG |
| `413` | `file_too_large` | File > 100 MB | Upload smaller file |
| `404` | `file_not_found` | File ID doesn't exist | Check file ID |
| `401` | `unauthorized` | Missing/invalid auth | Add valid API key/token |
| `403` | `forbidden` | Insufficient permissions | Use correct credentials |
| `500` | `internal_server_error` | Server error | Try again, check logs |
| `503` | `service_unavailable` | Component offline | Check health endpoint |

### Error Recovery

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def analyze_with_retry(file_id, headers):
    response = requests.post(
        f"http://localhost:8000/api/v1/audio/analyze/{file_id}",
        headers=headers
    )
    response.raise_for_status()  # Raise exception if status >= 400
    return response.json()

# Call with automatic retry
try:
    result = analyze_with_retry(file_id, headers)
    print(f"Analysis succeeded: {result['analysis_id']}")
except requests.exceptions.RequestException as e:
    print(f"Analysis failed after retries: {e}")
```

---

## Rate Limiting

### Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/audio/upload` | 100 | per hour |
| `/audio/analyze` | 500 | per hour |
| `/ai/search/semantic` | 200 | per hour |
| `/batch/analyze` | 50 | per hour |
| `/health` | 10,000 | per hour |

### Headers

Rate limit info is included in response headers:

```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 489
X-RateLimit-Reset: 1643898000
```

### Handling Rate Limits

```python
import requests
import time

def call_with_rate_limit(url, headers):
    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 429:  # Too Many Requests
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait_seconds = reset_time - int(time.time())
            print(f"Rate limited. Waiting {wait_seconds} seconds...")
            time.sleep(max(1, wait_seconds))
            continue

        response.raise_for_status()
        return response.json()

result = call_with_rate_limit("http://localhost:8000/api/v1/health", headers)
```

---

## WebSocket API

### Real-Time Batch Processing Updates

```javascript
// Connect to WebSocket for batch processing updates
const ws = new WebSocket("ws://localhost:8000/api/v1/ws");

ws.onopen = () => {
  // Subscribe to batch updates
  ws.send(JSON.stringify({
    type: "subscribe",
    channel: "batch:550e8400-e29b-41d4-a716-446655440003"
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case "batch_progress":
      console.log(`Progress: ${message.percent_complete}%`);
      console.log(`Files: ${message.processed}/${message.total_files}`);
      break;

    case "batch_completed":
      console.log(`Batch complete! Results:`, message.results);
      ws.close();
      break;

    case "error":
      console.error(`Error: ${message.message}`);
      break;
  }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};
```

---

## Integration Patterns

### Pattern 1: Upload → Analyze → Search

```python
# 1. Upload
upload = requests.post(f"{BASE_URL}/audio/upload", files={"file": open("song.wav", "rb")}, headers=headers).json()
file_id = upload["file_id"]

# 2. Analyze with AI
analysis = requests.post(
    f"{BASE_URL}/audio/analyze/{file_id}",
    params={"include_ai": True},
    headers=headers
).json()

# 3. Search for similar samples
search = requests.post(
    f"{BASE_URL}/ai/search/semantic",
    json={"query": f"{analysis['ai_analysis']['mood']} samples"},
    headers=headers
).json()
```

### Pattern 2: Batch Processing with WebSocket

```python
# Start batch
batch = requests.post(
    f"{BASE_URL}/batch/analyze",
    json={"file_ids": file_ids},
    headers=headers
).json()

batch_id = batch["batch_id"]

# Wait for completion via WebSocket
async def wait_for_batch(batch_id):
    async with websockets.connect(f"ws://localhost:8000/api/v1/ws") as ws:
        await ws.send(json.dumps({
            "type": "subscribe",
            "channel": f"batch:{batch_id}"
        }))

        while True:
            message = json.loads(await ws.recv())
            if message["type"] == "batch_completed":
                return message["results"]
```

### Pattern 3: Collection Management

```python
# Create collection
collection = requests.post(
    f"{BASE_URL}/collections",
    json={"name": "Electronic Drums"},
    headers=headers
).json()

# Add samples from search
search_results = requests.post(
    f"{BASE_URL}/ai/search/semantic",
    json={"query": "electronic drum loop", "limit": 10},
    headers=headers
).json()

for result in search_results["results"]:
    requests.post(
        f"{BASE_URL}/collections/{collection['id']}/samples",
        json={"file_id": result["file_id"]},
        headers=headers
    )
```

---

## Troubleshooting

### Issue: "Neural engine not available"

**Cause**: NeuralFeatureExtractor not initialized
**Solution**:
```bash
# Check health status
curl http://localhost:8000/api/v1/health

# Make sure audio engine has neural extractor
# In config, ensure ENABLE_NEURAL_ENGINE=true
```

### Issue: "File not found" after upload

**Cause**: File ID incorrect or file was cleaned up
**Solution**:
```bash
# Verify file was uploaded
curl http://localhost:8000/api/v1/audio/list -H "Authorization: Bearer <token>"

# Use file_id from upload response exactly as returned
```

### Issue: Semantic search returns empty results

**Cause**: No embeddings in database yet, or query doesn't match samples
**Solution**:
```bash
# Upload and analyze files first
# Try more general search queries
# "upbeat electronic" instead of "heavy bass synth wobble"
```

### Issue: Rate limiting errors (429)

**Cause**: API quota exceeded
**Solution**:
```bash
# Check remaining requests
curl -i http://localhost:8000/api/v1/health | grep X-RateLimit

# Implement exponential backoff in client
# Or request higher limits
```

### Issue: JWT token expired

**Cause**: Token exceeded expiration time
**Solution**:
```bash
# Get new token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -d '{"username": "user", "password": "password"}'

# Use new token in Authorization header
```

### Issue: 503 Service Unavailable

**Cause**: Critical components not initialized
**Solution**:
```bash
# Check logs
docker logs api

# Verify dependencies
# - AudioEngine initialized
# - AI Manager available
# - ChromaDB started

# Restart service
docker-compose restart api
```

---

## API Roadmap

### Phase 12 (Next)
- [ ] Real-time WebSocket streaming for batch processing
- [ ] Advanced filtering in semantic search
- [ ] Collection import/export
- [ ] Session management API

### Phase 13 (Future)
- [ ] Webhook support for batch completion
- [ ] GraphQL API option
- [ ] Streaming audio upload for large files
- [ ] Collaborative features with user management

---

## Support & Resources

**Documentation:**
- [CLI Reference](CLI_REFERENCE.md)
- [Architecture Guide](PROJECT_STRUCTURE.md)
- [Getting Started](../README.md)

**Interactive Docs:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

**Community:**
- GitHub Issues: Report bugs and request features
- Discord: Real-time support (link to be added)
- Email: support@samplemind.ai

**Quick Links:**
- [Health Check](http://localhost:8000/api/v1/health)
- [OpenAPI Spec](http://localhost:8000/api/openapi.json)
- [API Docs](http://localhost:8000/api/docs)

---

**Generated**: Phase 11.3b - API Documentation
**Status**: ✅ Complete
**Last Updated**: February 3, 2026
