---
applyTo: "**/*.py"
---

# Python Code Instructions

- Use Python 3.12+ features (type unions with `|`, `match` statements, `Self` type)
- Always add type annotations to function signatures and return types
- Use `async def` for all I/O operations (audio, AI calls, database, network)
- Run blocking I/O in `ThreadPoolExecutor` when async is not available
- Never use `time.sleep()` — use `asyncio.sleep()` in async contexts
- Never call `asyncio.run()` inside Textual event handlers
- Use lazy imports for heavy libraries: `torch`, `librosa`, `faiss`, `transformers`, `demucs`
- Format: Black (line length 88), isort, ruff
- Linting: ruff check + mypy strict mode
- Prefer `litellm_router.chat_completion()` over `SampleMindAIManager`
- Use `pathlib.Path` over `os.path` for file operations
- Use `logging` module, never `print()` for output in library code
- Docstrings: Google style with Args/Returns/Raises sections
