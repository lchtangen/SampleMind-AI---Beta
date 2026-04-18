---
name: supabase-auth
description: Supabase JWT authentication with get_current_user dependency
---

## Supabase Authentication

### Location
- Client: `src/samplemind/integrations/supabase_client.py`
- Auth middleware: used via `get_current_user` FastAPI dependency

### Auth Flows
- Email/password registration and login
- Magic link (passwordless) authentication
- JWT token validation and refresh

### FastAPI Integration
```python
from fastapi import Depends
from samplemind.integrations.supabase_client import get_current_user

@router.get("/api/v1/samples")
async def list_samples(user=Depends(get_current_user)):
    # user is the authenticated Supabase user
    samples = await TortoiseSample.filter(user_id=user.id).all()
    return samples
```

### Rules
- All protected routes must use `Depends(get_current_user)`
- Validate JWT tokens on every request
- Handle token expiration gracefully
- Never store raw passwords — Supabase handles password hashing
- Realtime sync: `integrations/realtime_sync.py` for multi-device
