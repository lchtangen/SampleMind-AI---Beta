---
name: code-review
description: Code review checklists for Python and TypeScript changes
---

## Code Review

### Python Checklist
- [ ] Type annotations on all function signatures and return types
- [ ] `async def` for I/O operations
- [ ] Lazy imports for torch, librosa, faiss, transformers, demucs
- [ ] `litellm_router.chat_completion()` for AI calls (not direct SDKs)
- [ ] No `time.sleep()`, no `asyncio.run()` in Textual
- [ ] Google-style docstrings
- [ ] `pathlib.Path` over `os.path`
- [ ] Error handling with proper exceptions
- [ ] No hardcoded secrets or credentials

### TypeScript Checklist
- [ ] Strict types — no `any` unless justified
- [ ] `"use client"` for interactive components
- [ ] `cn()` for Tailwind class merging
- [ ] Design system imports from `@/design-system`
- [ ] `apiFetch<T>()` for backend calls
- [ ] Proper error handling and loading states

### General Rules
- Do not modify unrelated tests
- Run `ruff check src/ && mypy src/` before committing
- Run `pytest tests/unit/ -v --tb=short` before committing
- Check for security issues in every review
