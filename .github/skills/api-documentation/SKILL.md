---
name: api-documentation
description: Guide for documenting API endpoints and generating API reference docs. Use when writing API documentation.
---

## API Documentation

### FastAPI Auto-Docs
FastAPI automatically generates OpenAPI docs:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Endpoint Documentation Pattern
```python
@router.post(
    "/analyze",
    response_model=AnalysisResult,
    summary="Analyze audio file",
    description="Perform audio analysis at the specified level.",
    responses={
        200: {"description": "Analysis completed successfully"},
        400: {"description": "Invalid file format"},
        404: {"description": "File not found"},
    }
)
async def analyze_audio(
    file: UploadFile = File(..., description="Audio file to analyze"),
    level: str = Query("STANDARD", description="Analysis level")
) -> AnalysisResult:
    """Analyze an audio file and return BPM, key, and features."""
    ...
```

### API Route Summary
| Prefix | Module | Description |
|--------|--------|-------------|
| `/api/v1/ai` | ai.py | AI analysis + FAISS |
| `/api/v1/search` | search.py | Search |
| `/api/v1/analytics` | analytics.py | Charts data |
| `/api/v1/marketplace` | marketplace.py | Pack store |
| `/api/v1/audio` | audio.py | Upload/process |
| `/api/v1/tasks` | tasks.py | Celery + agent history |
| `/api/v1/processing` | processing.py | Audio effects |
| `/ws/` | websocket.py | Real-time |
