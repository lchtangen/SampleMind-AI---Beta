Perform a security review of the SampleMind codebase:

1. Check for hardcoded secrets in src/, apps/web/, and config files
2. Review API routes for authentication/authorization gaps
3. Check for SQL injection risks in Tortoise ORM usage
4. Verify JWT validation in Supabase auth middleware
5. Check for XSS risks in Next.js frontend
6. Review file upload endpoints for path traversal
7. Check dependency versions for known vulnerabilities

Focus on: src/samplemind/interfaces/api/, apps/web/src/, .env*, docker-compose*.yml

Report findings with severity levels: CRITICAL, HIGH, MEDIUM, LOW.
