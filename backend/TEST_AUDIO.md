# 🎵 Audio API Testing Guide

Test the audio upload and analysis endpoints for SampleMind AI backend.

---

## 🚀 Prerequisites

1. **Start the server:**
```bash
cd backend
python main.py
```

2. **Get authentication token:**
```bash
# Register and login (see TEST_AUTH.md)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@samplemind.ai","password":"Test123456"}'
```

**Save the `access_token` from the response!**

---

## 🎵 Test Audio Endpoints

### 1. Upload Audio File

```bash
# Replace YOUR_TOKEN with your access token
curl -X POST "http://localhost:8000/api/v1/audio/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@path/to/your/audio.mp3"
```

**Expected Response:**
```json
{
  "id": 1,
  "filename": "audio.mp3",
  "file_size": 3456789,
  "format": "mp3",
  "duration": null,
  "sample_rate": null,
  "channels": null,
  "uploaded_at": "2025-10-19T20:30:00Z",
  "status": "uploaded"
}
```

**Save the `id` for next steps!**

---

### 2. Analyze Audio

```bash
# Replace YOUR_TOKEN and AUDIO_ID
curl -X POST "http://localhost:8000/api/v1/audio/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_id": 1,
    "analysis_type": "full",
    "extract_features": true,
    "ai_analysis": true
  }'
```

**Expected Response:**
```json
{
  "audio_id": 1,
  "status": "completed",
  "features": {
    "tempo": 128.5,
    "key": "C major",
    "time_signature": "4/4",
    "duration": 180.0,
    "loudness": -12.5,
    "energy": 0.75,
    "danceability": 0.68,
    "valence": 0.72,
    "spectral_centroid": 1500.5,
    "zero_crossing_rate": 0.08
  },
  "ai_analysis": {
    "genre": ["Electronic", "House"],
    "mood": ["Energetic", "Uplifting"],
    "instruments": ["Synthesizer", "Drums", "Bass"],
    "tags": ["Dance", "Club", "EDM"],
    "similarity_score": 0.85,
    "description": "An energetic electronic track with a driving beat and uplifting melodies."
  },
  "processing_time": 0.234,
  "analyzed_at": "2025-10-19T20:31:00Z"
}
```

---

### 3. List Audio Files

```bash
curl -X GET "http://localhost:8000/api/v1/audio?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "items": [
    {
      "id": 1,
      "filename": "audio.mp3",
      "duration": null,
      "format": "mp3",
      "uploaded_at": "2025-10-19T20:30:00Z",
      "has_analysis": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

### 4. Get Audio Details

```bash
# Replace AUDIO_ID
curl -X GET "http://localhost:8000/api/v1/audio/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "filename": "audio.mp3",
  "file_size": 3456789,
  "format": "mp3",
  "duration": null,
  "sample_rate": null,
  "channels": null,
  "uploaded_at": "2025-10-19T20:30:00Z",
  "status": "uploaded",
  "features": {
    "tempo": 128.5,
    "key": "C major",
    ...
  },
  "ai_analysis": {
    "genre": ["Electronic", "House"],
    ...
  },
  "metadata": null
}
```

---

### 5. Delete Audio

```bash
# Replace AUDIO_ID
curl -X DELETE "http://localhost:8000/api/v1/audio/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:** HTTP 204 No Content

---

## 🧪 Test in Browser (Swagger UI)

1. Open http://localhost:8000/api/docs
2. Click **"Authorize"** button (top right)
3. Enter your access token: `Bearer YOUR_TOKEN`
4. Test any endpoint by clicking → "Try it out" → Execute

---

## 📊 Available Endpoints

### Upload
- `POST /api/v1/audio/upload` — Upload audio file

### Analysis
- `POST /api/v1/audio/analyze` — Analyze uploaded audio

### List & Detail
- `GET /api/v1/audio` — List all audio files (paginated)
- `GET /api/v1/audio/{id}` — Get audio details with analysis

### Management
- `DELETE /api/v1/audio/{id}` — Delete audio file

---

## 🎯 Supported Audio Formats

- **MP3** — MPEG Audio Layer III
- **WAV** — Waveform Audio File Format
- **FLAC** — Free Lossless Audio Codec
- **AIFF** — Audio Interchange File Format
- **OGG** — Ogg Vorbis

---

## 📏 Upload Limits

- **Max File Size:** 100MB (configurable in `config.py`)
- **File Format:** Must be one of supported formats
- **Authentication:** Required for all endpoints

---

## 🎨 Analysis Features

### Audio Features Extracted
- **Tempo:** BPM (beats per minute)
- **Key:** Musical key (e.g., "C major")
- **Time Signature:** e.g., "4/4"
- **Duration:** Length in seconds
- **Loudness:** Amplitude in dB
- **Energy:** Overall energy level (0-1)
- **Danceability:** Suitability for dancing (0-1)
- **Valence:** Musical positiveness (0-1)
- **Spectral Centroid:** Brightness measure
- **Zero Crossing Rate:** Signal roughness

### AI Analysis Results
- **Genre Detection:** Predicted genres
- **Mood Detection:** Emotional characteristics
- **Instrument Detection:** Instruments used
- **Tags:** Descriptive keywords
- **Similarity Score:** Quality/confidence score
- **Description:** AI-generated summary

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "Unsupported file format. Allowed: mp3, wav, flac, aiff, ogg"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid access token"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this audio"
}
```

### 404 Not Found
```json
{
  "detail": "Audio file not found"
}
```

### 413 Request Entity Too Large
```json
{
  "detail": "File too large. Maximum size: 100MB"
}
```

---

## 🔄 Frontend Integration Example

```typescript
// Upload audio file
const uploadAudio = async (file: File, token: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/v1/audio/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return response.json();
};

// Analyze audio
const analyzeAudio = async (audioId: number, token: string) => {
  const response = await fetch('http://localhost:8000/api/v1/audio/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      audio_id: audioId,
      analysis_type: 'full',
      extract_features: true,
      ai_analysis: true
    })
  });
  
  return response.json();
};

// Get audio list
const getAudioList = async (token: string, page = 1) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/audio?page=${page}&page_size=20`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return response.json();
};
```

---

## 📝 Current Limitations (Development Mode)

- **In-Memory Storage:** Audio files lost on restart
- **No File Persistence:** Files not saved to disk
- **Simulated Analysis:** Using mock data instead of real audio engine
- **No Celery:** Analysis runs synchronously (blocking)
- **No Cloud Storage:** Files stored in memory

---

## ✅ Production TODO

1. Integrate real audio engine (`/src/samplemind/core/audio/`)
2. Add file storage (S3, MinIO, or local filesystem)
3. Implement Celery tasks for async processing
4. Add WebSocket for real-time progress updates
5. Add database storage (PostgreSQL)
6. Implement actual feature extraction (librosa)
7. Integrate AI models for genre/mood detection
8. Add audio preview/streaming endpoint
9. Implement search and filtering
10. Add batch upload and analysis

---

## 🎯 Next Steps

1. Test all endpoints with real audio files
2. Verify authentication works correctly
3. Check file size and format validation
4. Review analysis results structure
5. Plan integration with Python audio engine

---

**Status:** ✅ Audio endpoints functional and ready for testing  
**Phase 7 Progress:** 40% (4/10 tasks complete)  
**Next:** Database integration, Celery tasks, real audio engine integration

---

Built with ❤️ for music producers and audio engineers
