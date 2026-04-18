---
name: textual-tui
description: Textual TUI framework patterns — no sleep, no asyncio.run, use on_mount
---

## Textual TUI

### Location
- App: `src/samplemind/interfaces/tui/app.py`
- Screens: `src/samplemind/interfaces/tui/screens/` (13 screens)

### Critical Rules
- **Never** `time.sleep()` — use `self.set_timer()` or `asyncio.sleep()`
- **Never** `asyncio.run()` — Textual has its own event loop
- **Never** blocking I/O in `compose()` — use `on_mount()` for async init

### Patterns
```python
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button
from textual.worker import work

class AnalysisScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Loading...", id="status")
        yield Button("Analyze", id="analyze-btn")

    async def on_mount(self) -> None:
        # Async init goes here, NOT in compose()
        await self.load_data()

    @work(thread=True)
    def heavy_computation(self) -> None:
        # Background work with @work decorator
        ...
```

### Component Communication
- Define custom `Message` classes
- Use `self.query_one()` and `self.query()` for DOM queries
- Textual CSS for styling, not inline styles
