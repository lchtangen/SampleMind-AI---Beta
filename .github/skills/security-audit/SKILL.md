---
name: security-audit
description: Guide for security auditing the SampleMind codebase. Use when checking for vulnerabilities.
---

## Security Audit Guide

### Dependency Scanning
```bash
# Python vulnerabilities
pip audit

# Node vulnerabilities
cd apps/web && npm audit
```

### Code Patterns to Check

#### Authentication
- JWT token validation in API middleware
- Supabase RLS policies
- next-auth session management
- Cookie security flags (httpOnly, secure, sameSite)

#### Input Validation
- Pydantic models on all API endpoints
- File upload size/type restrictions
- Path traversal prevention
- SQL injection (Tortoise ORM handles this)

#### Secrets Management
- `.env.example` for reference (no real secrets)
- GitHub Actions secrets for CI
- Never log sensitive data
- Environment variables for runtime config

#### API Security
- CORS configuration in `main.py`
- Rate limiting with `slowapi` (to be wired)
- Authentication on protected endpoints
- Webhook signature verification (Stripe)

#### Frontend Security
- React auto-escaping (XSS protection)
- No `dangerouslySetInnerHTML` without sanitization
- CSP headers (to be configured)
- Secure cookie handling
