---
applyTo: "src/samplemind/interfaces/tui/**/*.py"
---

# Textual TUI Instructions

- Framework: Textual ^0.87.0
- App entry: `interfaces/tui/app.py`
- Screens: 13 screens in `interfaces/tui/screens/`
- Never use `time.sleep()` in event handlers — use `self.set_timer()` or `asyncio.sleep()`
- Never call `asyncio.run()` inside Textual — Textual has its own event loop
- Never do blocking I/O in `compose()` — use `on_mount()` for async initialization
- Use `self.query_one()` and `self.query()` for DOM queries
- CSS: Use Textual CSS, not inline styles
- Messages: Define custom `Message` classes for component communication
- Workers: Use `@work` decorator or `self.run_worker()` for background tasks
