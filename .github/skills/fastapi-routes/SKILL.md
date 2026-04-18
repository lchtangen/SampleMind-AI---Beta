---
name: fastapi-routes
description: Guide for creating and modifying FastAPI REST API endpoints. Use when building new API routes or modifying existing ones.
---

## FastAPI Route Development

When creating or modifying API routes:

1. **Routes live at** `src/samplemind/interfaces/api/routes/` — NOT `src/samplemind/api/`
2. **Register in main.py** — `src/samplemind/interfaces/api/main.py` (12+ routers)
3. **Use Pydantic v2** for request/response models

### New Route Pattern
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/new-domain", tags=["new-domain"])

class MyRequest(BaseModel):
    param: str

class MyResponse(BaseModel):
    result: str

@router.post("/action", response_model=MyResponse)
async def my_action(req: MyRequest) -> MyResponse:
    # Implementation
    return MyResponse(result="done")
```

### Registration in main.py
```python
from samplemind.interfaces.api.routes.new_module import router as new_router
app.include_router(new_router)
```

### Existing Routes
- ai.py, search.py, analytics.py, marketplace.py, billing.py
- audio.py, auth.py, tasks.py, websocket.py, processing.py
