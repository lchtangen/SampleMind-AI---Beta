# 🔌 API LEARNING GUIDE FOR SAMPLEMIND AI

## Complete Guide to Understanding and Using the FastAPI Backend

### Table of Contents
1. [API Basics](#api-basics)
2. [Understanding FastAPI](#understanding-fastapi)
3. [Core API Endpoints](#core-api-endpoints)
4. [Testing API Endpoints](#testing-api-endpoints)
5. [Common API Patterns](#common-api-patterns)
6. [Debugging API Issues](#debugging-api-issues)
7. [Integration with CLI](#integration-with-cli)

---

## 🎯 API Basics

### What is an API?

**API = Application Programming Interface**

An API is a contract between your frontend (CLI/Web UI) and backend (FastAPI). It defines:
- What requests can be made (endpoints)
- What parameters are needed
- What responses you'll get back
- Error handling

### REST API Principles

SampleMind uses **REST (Representational State Transfer)**, which means:

| Method | Purpose | Example |
|--------|---------|---------|
| **GET** | Retrieve data | `GET /api/v1/library` - Get sample list |
| **POST** | Create data | `POST /api/v1/audio/analyze` - Analyze audio |
| **PUT** | Update data | `PUT /api/v1/samples/123` - Update sample |
| **DELETE** | Remove data | `DELETE /api/v1/samples/123` - Delete sample |

### API Base URL

In development with Docker:
```
http://localhost:8000
```

In production:
```
https://api.samplemind.ai
```

---

## 🚀 Understanding FastAPI

### What is FastAPI?

FastAPI is a modern Python web framework that:
- ✓ Automatically validates request data
- ✓ Generates interactive documentation
- ✓ Handles async operations efficiently
- ✓ Provides type safety with Python type hints
- ✓ Auto-generates OpenAPI (Swagger) documentation

### Key FastAPI Features

```python
# src/samplemind/interfaces/api/routes/audio.py example:

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/audio", tags=["Audio"])

# Define request/response model
class AnalysisRequest(BaseModel):
    """Request to analyze audio file"""
    file: str
    level: str = "STANDARD"

class AnalysisResponse(BaseModel):
    """Response with analysis results"""
    id: str
    tempo: float
    key: str
    genre: str
    confidence: float

# Define endpoint
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    level: str = "STANDARD"
):
    """
    Analyze audio file and return features

    - **file**: Audio file (MP3, WAV, FLAC)
    - **level**: Analysis level (BASIC, STANDARD, DETAILED, PROFESSIONAL)

    Returns analysis with:
    - tempo (BPM)
    - key (musical key)
    - genre (detected genre)
    - confidence (0-1 score)
    """
    # Process file
    result = await process_audio(file, level)
    return result
```

### How to Read FastAPI Code

1. **@router.post()** = HTTP POST method at /api/v1/audio/analyze
2. **file: UploadFile** = Required file parameter
3. **level: str = "STANDARD"** = Optional string parameter with default
4. **response_model=AnalysisResponse** = Response will be AnalysisResponse shape
5. **async def** = Function runs asynchronously (non-blocking)

---

## 🔗 Core API Endpoints

### 1. Audio Analysis Endpoints

#### Analyze Audio File
```bash
POST /api/v1/audio/analyze
```

**Request:**
```json
{
  "file": "<binary audio data>",
  "level": "STANDARD"
}
```

**Response:**
```json
{
  "id": "uuid",
  "tempo": 120.5,
  "key": "C Major",
  "genre": "Electronic",
  "energy": 0.8,
  "confidence": 0.92,
  "features": {
    "chroma": [...],
    "mfcc": [...],
    "spectral_centroid": 2500.5
  }
}
```

**Learning Task:**
1. Open Thunder Client in VSCode (Ctrl+Shift+D)
2. Create new request:
   - Method: POST
   - URL: `http://localhost:8000/api/v1/audio/analyze`
   - Body: Select "File" tab, upload an MP3
3. Click Send and observe response

#### Batch Analysis
```bash
POST /api/v1/audio/batch-analyze
```

**Request:**
```json
{
  "files": ["file1.mp3", "file2.wav"],
  "level": "STANDARD"
}
```

**Response:**
```json
{
  "results": [
    { "id": "1", "tempo": 120, ... },
    { "id": "2", "tempo": 130, ... }
  ],
  "duration_ms": 5000
}
```

### 2. Library Management Endpoints

#### Get Sample Library
```bash
GET /api/v1/library?limit=20&offset=0
```

**Response:**
```json
{
  "samples": [
    {
      "id": "uuid",
      "name": "Kick Drum",
      "path": "/data/samples/kick.wav",
      "features": {...},
      "tags": ["drum", "kick", "percussion"]
    }
  ],
  "total": 150,
  "has_more": true
}
```

#### Search Library
```bash
GET /api/v1/library/search?q=techno&limit=10
```

**Response:**
```json
{
  "results": [
    { "id": "1", "name": "Techno Drum", "similarity": 0.95 },
    { "id": "2", "name": "Techno Bass", "similarity": 0.87 }
  ]
}
```

#### Add Sample to Library
```bash
POST /api/v1/library/upload
```

**Request:**
```json
{
  "file": "<binary>",
  "name": "My Sample",
  "tags": ["drum", "kick"]
}
```

### 3. AI Assistant Endpoints

#### Get AI Suggestions
```bash
POST /api/v1/ai/suggest
```

**Request:**
```json
{
  "analysis": { "tempo": 120, "key": "C Major", "genre": "House" },
  "context": "production_tips",
  "model": "gemini"
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "type": "drum_selection",
      "suggestion": "Use 4-on-the-floor kick pattern",
      "reasoning": "Matches House genre at 120 BPM",
      "confidence": 0.92
    }
  ],
  "source": "gemini-3-flash"
}
```

### 4. Workspace Endpoints

#### Create Workspace
```bash
POST /api/v1/workspaces
```

**Request:**
```json
{
  "name": "My Project",
  "description": "House track",
  "bpm": 120,
  "key": "C Major"
}
```

**Response:**
```json
{
  "id": "workspace-uuid",
  "name": "My Project",
  "created_at": "2026-01-19T10:00:00Z",
  "samples": []
}
```

---

## ✅ Testing API Endpoints

### Method 1: Thunder Client (VSCode)

**Best for:** Quick testing, learning, debugging

**Steps:**
1. Open Thunder Client (Extension icon on left sidebar)
2. Click "+ New Request"
3. Enter URL: `http://localhost:8000/api/v1/health`
4. Click "Send"
5. See response in right panel

**Pro Tips:**
- Save requests in collections for reuse
- Use variables for localhost:8000
- Test before/after code changes
- Export collection for team sharing

### Method 2: REST Client Extension

**Best for:** Complex workflows, environment variables

**File: requests.http**
```http
### Health Check
GET http://localhost:8000/health

### Analyze Audio
POST http://localhost:8000/api/v1/audio/analyze
Content-Type: multipart/form-data; boundary=----FormBoundary7MA4YWxkTrZu0gW

------FormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="sample.wav"

< ./data/samples/sample.wav
------FormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="level"

STANDARD
------FormBoundary7MA4YWxkTrZu0gW--

### Get Library
GET http://localhost:8000/api/v1/library?limit=10

### Store in variable
@baseUrl = http://localhost:8000
@token = your-auth-token

### Use variable
GET {{baseUrl}}/api/v1/health
Authorization: Bearer {{token}}
```

**Run:**
```bash
# Install REST Client extension
# Right-click on .http file
# Select "Send Request"
```

### Method 3: Python Requests Library

**Best for:** Automation, CI/CD, integration tests

```python
import requests

# 1. Test API Health
response = requests.get("http://localhost:8000/health")
print(response.json())  # {'status': 'ok'}

# 2. Analyze Audio
with open("sample.wav", "rb") as f:
    files = {"file": f}
    data = {"level": "STANDARD"}
    response = requests.post(
        "http://localhost:8000/api/v1/audio/analyze",
        files=files,
        data=data
    )
print(response.json())

# 3. Get Library
params = {"limit": 10, "offset": 0}
response = requests.get(
    "http://localhost:8000/api/v1/library",
    params=params
)
print(response.json())

# 4. Error Handling
try:
    response = requests.post(
        "http://localhost:8000/api/v1/audio/analyze",
        files={"file": open("missing.wav", "rb")}
    )
    response.raise_for_status()  # Raise error if status != 200
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
```

### Method 4: FastAPI Documentation

**Best for:** Discovering endpoints, exploring API structure

**Access:**
```
http://localhost:8000/docs       # Swagger UI (interactive)
http://localhost:8000/redoc      # ReDoc (cleaner documentation)
```

**Interactive Features:**
1. Click endpoint to expand
2. See request/response models
3. Try it out button to test
4. Copy curl command
5. View schema definitions

---

## 🔄 Common API Patterns

### Pattern 1: Error Handling

```python
# API Response with error
{
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "Audio file not found or invalid",
    "details": {
      "file": "sample.wav",
      "reason": "File size > 100MB"
    }
  }
}
```

**In Python:**
```python
try:
    response = requests.post(
        "http://localhost:8000/api/v1/audio/analyze",
        files={"file": open("huge_file.wav", "rb")}
    )

    if response.status_code == 400:
        error = response.json()["error"]
        print(f"Error: {error['message']}")
    elif response.status_code == 500:
        print("Server error, try again later")
    else:
        result = response.json()
        print(f"Success: {result}")

except requests.exceptions.Timeout:
    print("Request timed out (> 30 seconds)")
```

### Pattern 2: Pagination

```python
# Get first page
response = requests.get(
    "http://localhost:8000/api/v1/library",
    params={"limit": 20, "offset": 0}
)
data = response.json()

# data = {
#   "samples": [...20 items...],
#   "total": 500,
#   "has_more": true
# }

# Get next page
if data["has_more"]:
    response = requests.get(
        "http://localhost:8000/api/v1/library",
        params={"limit": 20, "offset": 20}
    )
```

### Pattern 3: Async Operations

```python
# Some operations are async (take time)

# Start analysis
response = requests.post(
    "http://localhost:8000/api/v1/audio/analyze",
    files={"file": f},
    data={"async": True}  # Don't wait for result
)

job_id = response.json()["job_id"]

# Poll for result
import time
while True:
    response = requests.get(
        f"http://localhost:8000/api/v1/jobs/{job_id}"
    )
    job = response.json()

    if job["status"] == "completed":
        print(f"Result: {job['result']}")
        break
    elif job["status"] == "failed":
        print(f"Error: {job['error']}")
        break
    else:
        print(f"Status: {job['status']} - {job['progress']}%")
        time.sleep(1)
```

---

## 🐛 Debugging API Issues

### Issue 1: Connection Refused

```
Error: Connection refused at http://localhost:8000
```

**Solution:**
```bash
# Check if Docker is running
docker ps

# Check if API container is running
docker logs samplemind-api

# Start services if stopped
docker compose up -d

# Test connection
curl http://localhost:8000/health
```

### Issue 2: Request Timeout

```
Error: Read timeout after 30 seconds
```

**Solution:**
```python
# Increase timeout
response = requests.post(
    url,
    files=files,
    timeout=120  # 2 minutes
)

# Check API logs
# docker logs samplemind-api -f
```

### Issue 3: Bad Request (400)

```json
{
  "detail": [
    {
      "loc": ["body", "level"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

**Solution:**
```python
# Check valid values
valid_levels = ["BASIC", "STANDARD", "DETAILED", "PROFESSIONAL"]

response = requests.post(
    url,
    files=files,
    data={"level": "STANDARD"}  # Use valid value
)
```

### Issue 4: Unauthorized (401)

```json
{
  "detail": "Not authenticated"
}
```

**Solution:**
```python
# Add authentication token
headers = {"Authorization": f"Bearer {your_token}"}

response = requests.post(
    url,
    files=files,
    headers=headers
)
```

### Debugging Tools

```bash
# View real-time API logs
docker logs samplemind-api -f

# Test endpoint with curl
curl -X POST http://localhost:8000/api/v1/audio/analyze \
  -F "file=@sample.wav" \
  -F "level=STANDARD"

# Check API is accessible
curl http://localhost:8000/health

# Monitor network requests
# In Thunder Client: Click "Network" tab
```

---

## 🔗 Integration with CLI

### How CLI Calls API

```python
# src/samplemind/interfaces/cli/commands/analyze.py

import httpx

async def analyze_command(file_path: str, level: str = "STANDARD"):
    """CLI command that calls API"""

    # 1. Read file
    with open(file_path, "rb") as f:
        files = {"file": f}

        # 2. Send to API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/audio/analyze",
                files=files,
                data={"level": level}
            )

        # 3. Handle response
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Tempo: {result['tempo']} BPM")
            print(f"✓ Key: {result['key']}")
            print(f"✓ Genre: {result['genre']}")
        else:
            error = response.json()
            print(f"✗ Error: {error['message']}")
```

### Testing CLI → API Integration

```bash
# 1. Start Docker services
docker compose up -d

# 2. Run CLI command
python main.py analyze sample.wav

# 3. Watch real-time API logs
docker logs samplemind-api -f

# 4. Check if request reaches API
# You should see POST request in logs
```

---

## 📚 Learning Resources

### Next Steps

1. **Explore Endpoints**
   - Open http://localhost:8000/docs
   - Try each endpoint with example data
   - Note response structure

2. **Write Tests**
   - Create requests.http file with all endpoints
   - Save in version control
   - Use for regression testing

3. **Debug Issues**
   - Watch API logs while testing
   - Use Thunder Client breakpoints
   - Check data types match schema

4. **Understand Flow**
   - CLI → API → Database → Response
   - Each layer can be tested independently

5. **Build Features**
   - Start with simple GET endpoint
   - Progress to POST with file upload
   - Add error handling
   - Add pagination

---

## 🎯 Practice Exercises

### Exercise 1: Test All Audio Endpoints
- [ ] Test /api/v1/audio/analyze with MP3
- [ ] Test with WAV
- [ ] Test with FLAC
- [ ] Test with invalid file
- [ ] Observe different error messages

### Exercise 2: Create API Testing Script
- [ ] Write Python script using requests
- [ ] Test 5 different endpoints
- [ ] Add error handling
- [ ] Display formatted results
- [ ] Save as reusable script

### Exercise 3: Monitor API Performance
- [ ] Record response times
- [ ] Compare different file sizes
- [ ] Identify bottlenecks
- [ ] Note in development journal

### Exercise 4: Integrate CLI with API
- [ ] Make CLI call API endpoint
- [ ] Display results in CLI format
- [ ] Add CLI flag for API endpoint URL
- [ ] Test local vs Docker API

---

## 💡 Key Takeaways

✓ **API = Contract between frontend and backend**
✓ **REST uses GET, POST, PUT, DELETE**
✓ **FastAPI auto-generates documentation**
✓ **Test endpoints before coding against them**
✓ **Use Thunder Client for quick testing**
✓ **Check logs when debugging**
✓ **CLI calls API over HTTP**
✓ **Error messages help debugging**
✓ **Pagination handles large data**
✓ **Async operations improve performance**

---

Keep learning! Every endpoint you understand gets you closer to mastering the full-stack! 🚀
