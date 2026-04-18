---
applyTo: "src/samplemind/interfaces/api/**/*.py"
---

# FastAPI API Instructions

- All API code lives at `src/samplemind/interfaces/api/` — NOT `src/samplemind/api/`
- App factory + lifespan: `interfaces/api/main.py` (12+ routers registered)
- Router pattern: `APIRouter(prefix="/api/v1/<domain>", tags=["<domain>"])`
- Use Pydantic v2 models for request/response schemas
- Return types must be annotated (e.g., `-> AnalysisResult`)
- Use `UploadFile` for file uploads, not raw `Request.body()`
- Background tasks: use Celery for heavy work, `BackgroundTasks` only for quick notifications
- Error handling: raise `HTTPException` with proper status codes
- Auth: JWT from Supabase via `get_current_user` dependency
- Rate limiting: `slowapi` is installed but not yet wired — wire it when adding new public endpoints
- CORS is configured in main.py lifespan
- WebSocket endpoints use `/ws/` prefix
