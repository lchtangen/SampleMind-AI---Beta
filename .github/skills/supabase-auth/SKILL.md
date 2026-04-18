---
name: supabase-auth
description: Guide for Supabase authentication integration. Use when implementing auth flows, JWT validation, or user management.
---

## Supabase Auth Integration

### Files
- **Client:** `src/samplemind/integrations/supabase_client.py`
- **Realtime:** `src/samplemind/integrations/realtime_sync.py`
- **API Auth:** `src/samplemind/interfaces/api/routes/auth.py`

### Auth Methods
- Email/password signup and login
- Magic link authentication
- JWT token validation

### Backend Pattern
```python
from samplemind.integrations.supabase_client import get_supabase_client

client = get_supabase_client()

# Verify JWT token
user = client.auth.get_user(token)

# Create user
response = client.auth.sign_up({"email": email, "password": password})
```

### Frontend (Next.js)
- next-auth v5 beta with Supabase provider
- Session management via cookies
- Protected routes via middleware

### Realtime Sync
- Multi-device library synchronization
- Uses Supabase Realtime channels
- Handles presence and broadcast events

### Security
- JWT tokens expire and must be refreshed
- Row Level Security (RLS) policies on Supabase tables
- Never expose service_role key to client
