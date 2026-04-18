---
name: fastapi-routes
description: FastAPI REST API development at interfaces/api/ with Pydantic v2
---

## FastAPI Routes

### Location
All API code: `src/samplemind/interfaces/api/` — **NOT** `src/samplemind/api/`

### Router Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/samples", tags=["samples"])

class SampleResponse(BaseModel):
    id: int
    filename: str
    bpm: float | None = Field(None, description="Beats per minute")

@router.post("/upload")
async def upload_sample(
    file: UploadFile,
    user=Depends(get_current_user),
) -> SampleResponse:
    ...
```

### Rules
- Pydantic v2 models for request/response schemas
- `UploadFile` for file uploads
- JWT auth via `get_current_user` dependency (Supabase)
- Celery for heavy tasks (>1s), `BackgroundTasks` for quick work
- `HTTPException` with proper status codes
- WebSocket endpoints use `/ws/` prefix
- CORS configured in main.py lifespan
- App factory: `interfaces/api/main.py` (12+ routers)
