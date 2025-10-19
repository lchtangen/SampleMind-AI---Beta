# 📡 SampleMind AI - Complete API Reference

**Base URL:** `http://localhost:8000`  
**Production:** `https://api.samplemind.ai`  
**Version:** v1  
**Authentication:** JWT Bearer Token

---

## Quick Links

- **Swagger UI:** [/api/docs](http://localhost:8000/api/docs)
- **ReDoc:** [/api/redoc](http://localhost:8000/api/redoc)
- **Health:** [/health](http://localhost:8000/health)
- **Status:** [/api/v1/status](http://localhost:8000/api/v1/status)

---

## Authentication Endpoints

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePass123",
  "full_name": "John Doe"
}
```

**Response 201:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-10-19T20:00:00Z"
}
```

---

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePass123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Usage:**
```http
Authorization: Bearer <access_token>
```

---

### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "message": "Successfully logged out"
}
```

---

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-10-19T20:00:00Z"
}
```

---

## Audio Endpoints

### Upload Audio
```http
POST /api/v1/audio/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <audio-file.mp3>
```

**Response 201:**
```json
{
  "id": 1,
  "filename": "audio-file.mp3",
  "format": "mp3",
  "size": 5242880,
  "duration": 245,
  "status": "uploaded",
  "uploaded_at": "2025-10-19T20:00:00Z",
  "user_id": 1
}
```

**Supported Formats:** MP3, WAV, FLAC, AIFF, OGG  
**Max Size:** 100MB

---

### Analyze Audio
```http
POST /api/v1/audio/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "audio_id": 1,
  "analysis_type": "full",
  "extract_features": true,
  "ai_analysis": true
}
```

**Response 200:**
```json
{
  "audio_id": 1,
  "status": "completed",
  "features": {
    "tempo": 128.5,
    "key": "C major",
    "time_signature": "4/4",
    "duration": 245,
    "loudness": -12.5,
    "energy": 0.75,
    "danceability": 0.82,
    "valence": 0.68
  },
  "ai_analysis": {
    "genre": ["Electronic", "House"],
    "mood": ["Energetic", "Uplifting"],
    "instruments": ["Synthesizer", "Drums", "Bass"],
    "tags": ["Summer", "Festival", "Club"]
  },
  "analyzed_at": "2025-10-19T20:01:00Z"
}
```

---

### List Audio
```http
GET /api/v1/audio?page=1&page_size=20
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `status` (string): Filter by status (uploaded, processing, completed, failed)

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "filename": "track1.mp3",
      "status": "completed",
      "uploaded_at": "2025-10-19T20:00:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

### Get Audio Details
```http
GET /api/v1/audio/{id}
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "id": 1,
  "filename": "track1.mp3",
  "format": "mp3",
  "size": 5242880,
  "duration": 245,
  "status": "completed",
  "features": { ... },
  "ai_analysis": { ... },
  "uploaded_at": "2025-10-19T20:00:00Z",
  "analyzed_at": "2025-10-19T20:01:00Z"
}
```

---

### Delete Audio
```http
DELETE /api/v1/audio/{id}
Authorization: Bearer <token>
```

**Response 204:** No Content

---

## WebSocket

### Connect
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/1?token=<access_token>');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message:', data);
};
```

### Message Types

**Connection:**
```json
{
  "type": "connection",
  "data": {
    "status": "connected",
    "user_id": 1,
    "message": "WebSocket connection established"
  },
  "timestamp": "2025-10-19T20:00:00Z"
}
```

**Upload Progress:**
```json
{
  "type": "upload_progress",
  "data": {
    "audio_id": 1,
    "progress": 65.5,
    "status": "Uploading..."
  },
  "timestamp": "2025-10-19T20:00:00Z"
}
```

**Analysis Status:**
```json
{
  "type": "analysis_status",
  "data": {
    "audio_id": 1,
    "status": "completed",
    "progress": 100,
    "results": { ... }
  },
  "timestamp": "2025-10-19T20:00:00Z"
}
```

**Notification:**
```json
{
  "type": "notification",
  "data": {
    "title": "Analysis Complete",
    "message": "Your audio has been analyzed",
    "level": "success"
  },
  "timestamp": "2025-10-19T20:00:00Z"
}
```

---

## System Endpoints

### API Info
```http
GET /
```

**Response 200:**
```json
{
  "name": "SampleMind AI API",
  "version": "0.1.0-beta",
  "status": "operational",
  "docs": "/api/docs",
  "features": [...]
}
```

---

### Health Check
```http
GET /health
```

**Response 200:**
```json
{
  "status": "healthy",
  "service": "samplemind-api",
  "checks": {
    "api": "ok",
    "database": "not_configured",
    "redis": "not_configured"
  }
}
```

---

### Endpoint Status
```http
GET /api/v1/status
```

**Response 200:**
```json
{
  "api_version": "v1",
  "status": "active",
  "endpoints": {
    "auth": "active",
    "audio": "active",
    "analysis": "active",
    "search": "pending"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

- **Per Minute:** 60 requests
- **Per Hour:** 1000 requests
- **Headers:**
  - `X-RateLimit-Limit`: Total allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

---

## cURL Examples

### Register & Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123","full_name":"Test User"}'

# Login (save token)
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}' \
  | jq -r '.access_token')

echo $TOKEN
```

### Upload & Analyze
```bash
# Upload
curl -X POST http://localhost:8000/api/v1/audio/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@audio.mp3"

# Analyze (use audio_id from upload response)
curl -X POST http://localhost:8000/api/v1/audio/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"audio_id":1,"analysis_type":"full"}'

# Get results
curl -X GET http://localhost:8000/api/v1/audio/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## TypeScript Client Example

```typescript
import { AuthAPI, AudioAPI } from '@/lib/api-client';

// Login
const { access_token } = await AuthAPI.login(email, password);

// Upload with progress
const audio = await AudioAPI.upload(file, (progress) => {
  console.log(`Upload: ${progress}%`);
});

// Analyze
const analysis = await AudioAPI.analyze(audio.id);

// List all
const { items, total } = await AudioAPI.list(1, 20);

// Get details
const details = await AudioAPI.get(audio.id);

// Delete
await AudioAPI.delete(audio.id);
```

---

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Docs
```bash
open http://localhost:8000/api/docs
```

### Complete Flow
```bash
# See: backend/TEST_AUTH.md
# See: backend/TEST_AUDIO.md
# See: backend/TEST_WEBSOCKET.md
```

---

**API Status:** ✅ Fully Functional  
**Endpoints:** 14 (13 REST + 1 WebSocket)  
**Documentation:** Complete  
**Testing:** All endpoints validated
