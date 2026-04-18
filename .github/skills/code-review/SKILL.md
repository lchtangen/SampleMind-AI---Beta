---
name: code-review
description: Guide for performing code reviews on SampleMind pull requests. Use when reviewing code changes.
---

## Code Review Checklist

### Python
- [ ] Type annotations on all new functions
- [ ] `async def` for I/O operations
- [ ] No `time.sleep()` (use `asyncio.sleep()`)
- [ ] No `asyncio.run()` inside Textual
- [ ] Lazy imports for heavy libraries
- [ ] Logging over `print()`
- [ ] Google-style docstrings
- [ ] Tests added or updated

### TypeScript
- [ ] Strict types (no `any` without justification)
- [ ] `"use client"` where needed
- [ ] `cn()` for Tailwind classes
- [ ] Design system components used
- [ ] Error boundaries for async components

### Security
- [ ] No hardcoded secrets
- [ ] Input validation on all endpoints
- [ ] Webhook signature verification
- [ ] SQL injection safe (Tortoise ORM)
- [ ] XSS safe (React auto-escaping)

### General
- [ ] Changes match the PR description
- [ ] No unrelated test modifications
- [ ] CHECKLIST.md updated if completing a task
- [ ] Consistent with existing patterns
- [ ] No breaking changes to public APIs
