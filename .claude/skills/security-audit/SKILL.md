---
name: security-audit
description: Security auditing for secrets, auth, injection, XSS, uploads, and dependencies
---

## Security Audit

### Checklist
1. **Secrets:** Scan for hardcoded API keys, tokens, passwords
2. **Auth:** Verify JWT validation, `get_current_user` on all protected routes
3. **Injection:** Check Tortoise ORM for raw SQL, subprocess for command injection
4. **XSS:** Review Next.js for `dangerouslySetInnerHTML`, unescaped input
5. **Uploads:** Path traversal in `UploadFile` handlers, file type/size validation
6. **CORS:** Verify FastAPI CORS configuration
7. **Dependencies:** Check pyproject.toml and package.json for CVEs

### Focus Areas
- `src/samplemind/interfaces/api/` — API routes
- `apps/web/src/` — Frontend components
- `.env*` — Environment files
- `docker-compose*.yml` — Container configs

### Severity Levels
- **CRITICAL:** Secrets exposed, auth bypass
- **HIGH:** Injection, path traversal
- **MEDIUM:** Missing headers, weak validation
- **LOW:** Best practice improvements
