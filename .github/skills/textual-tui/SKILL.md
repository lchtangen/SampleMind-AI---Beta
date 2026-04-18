---
name: textual-tui
description: Guide for building Textual TUI screens and widgets. Use when creating or modifying terminal UI components.
---

## Textual TUI Development

### Structure
- **App:** `src/samplemind/interfaces/tui/app.py`
- **Screens:** `src/samplemind/interfaces/tui/screens/` (13 screens)

### Screen Pattern
```python
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

class MyScreen(Screen):
    CSS = """
    MyScreen { layout: vertical; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Content")
        yield Footer()

    async def on_mount(self) -> None:
        # Async initialization here (NOT in compose)
        data = await self.fetch_data()
```

### Critical Rules
- **NEVER** `time.sleep()` — use `self.set_timer()` or `asyncio.sleep()`
- **NEVER** `asyncio.run()` — Textual has its own event loop
- **NEVER** blocking I/O in `compose()` — use `on_mount()`
- Use `@work` decorator for background tasks
- Use `self.query_one()` / `self.query()` for DOM queries
- Define `Message` classes for component communication
