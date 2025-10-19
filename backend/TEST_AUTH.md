# 🔐 Authentication API Testing Guide

Test the authentication endpoints for SampleMind AI backend.

---

## 🚀 Start the Server

```bash
cd backend
python main.py
```

Server will be running at: **http://localhost:8000**

---

## 📝 API Documentation

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## 🧪 Test Endpoints

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@samplemind.ai",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@samplemind.ai",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2025-10-19T20:00:00Z"
}
```

---

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@samplemind.ai",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the tokens** for subsequent requests!

---

### 3. Get Current User Info

```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@samplemind.ai",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2025-10-19T20:00:00Z"
}
```

---

### 4. Refresh Access Token

```bash
# Replace YOUR_REFRESH_TOKEN with the refresh token from login
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 5. Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "message": "Successfully logged out. Please discard your tokens."
}
```

---

## 🧪 Test in Browser (Swagger UI)

1. Open http://localhost:8000/api/docs
2. Click on any endpoint (e.g., `/api/v1/auth/register`)
3. Click **"Try it out"**
4. Fill in the request body
5. Click **"Execute"**

---

## 🔑 Token Format

### Access Token (30 minutes expiry)
```json
{
  "sub": "1",
  "email": "test@samplemind.ai",
  "exp": 1697745600,
  "type": "access"
}
```

### Refresh Token (7 days expiry)
```json
{
  "sub": "1",
  "email": "test@samplemind.ai",
  "exp": 1698350400,
  "type": "refresh"
}
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Incorrect email or password"
}
```

### 403 Forbidden
```json
{
  "detail": "User account is inactive"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

---

## 🔄 Frontend Integration Example

```typescript
// Example: Login and use token
const login = async (email: string, password: string) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Store tokens
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  return data;
};

// Example: Make authenticated request
const getProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/v1/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return response.json();
};
```

---

## 📊 Current Limitations

- **In-Memory Storage:** Users stored in memory (lost on restart)
- **No Token Blacklist:** Logout doesn't invalidate tokens server-side
- **No Database:** Replace with PostgreSQL/SQLAlchemy in production

---

## ✅ Next Steps

1. Replace in-memory storage with PostgreSQL
2. Add token blacklist with Redis
3. Add email verification
4. Add password reset flow
5. Add rate limiting
6. Add OAuth providers (Google, GitHub)

---

**Status:** ✅ Authentication system functional and ready for testing  
**Phase 7 Progress:** Task T02 complete (Auth flow)
