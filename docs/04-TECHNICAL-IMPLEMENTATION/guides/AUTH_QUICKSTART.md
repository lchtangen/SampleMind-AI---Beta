# Authentication Quick Start Guide

## Test Authentication System

### 1. Start the API Server

```bash
cd /home/lchta/Projects/samplemind-ai-v6
export PYTHONPATH=/home/lchta/Projects/samplemind-ai-v6/src

# Start with uvicorn
.venv/bin/uvicorn samplemind.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the startup script:
```bash
./start_api.sh
```

### 2. Test Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "producer@samplemind.ai",
    "username": "beatmaker",
    "password": "SecurePass123"
  }'
```

### 3. Test Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=producer@samplemind.ai&password=SecurePass123"
```

Save the `access_token` from response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 4. Test Protected Endpoint

```bash
# Replace <TOKEN> with your access_token
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

### 5. Test Password Change

```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePass123",
    "new_password": "NewSecure456"
  }'
```

### 6. Test Token Refresh

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<REFRESH_TOKEN>"
  }'
```

## API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

Click "Authorize" button in Swagger UI to test with Bearer token.

## Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login (get tokens) | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | No (refresh token) |
| POST | `/api/v1/auth/logout` | Logout | Yes |
| GET | `/api/v1/auth/me` | Get current user | Yes |
| PUT | `/api/v1/auth/me` | Update profile | Yes |
| POST | `/api/v1/auth/change-password` | Change password | Yes |

## Token Information

- **Access Token**: 30 minutes expiration
- **Refresh Token**: 7 days expiration
- **Algorithm**: HS256 (HMAC-SHA256)
- **Header Format**: `Authorization: Bearer <token>`

## Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

## Username Requirements

- 3-50 characters
- Alphanumeric + underscores only
- Must be unique

## Environment Configuration

Create `.env` file:
```bash
# JWT Settings
SECRET_KEY=your-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=samplemind

# Generate secure key:
# openssl rand -hex 32
```

## Protecting Your Routes

```python
from fastapi import Depends
from samplemind.core.auth import get_current_active_user

@router.post("/analyze")
async def analyze_audio(
    current_user = Depends(get_current_active_user)
):
    # Only authenticated users can access
    return {"message": f"Hello {current_user.username}"}
```

## Next Steps

✅ Task 1: FastAPI Backend - Complete
✅ Task 2: Database Layer - Complete
✅ Task 3: Authentication - Complete

Now ready for:
- Task 4: Background Tasks (Celery)
- Task 5: React Frontend
- Task 6: UI Components
