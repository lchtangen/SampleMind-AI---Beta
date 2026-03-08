"""Keyboard Shortcut Hint Widgets for SampleMind TUI"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Horizontal


class KeyboardShortcut(Widget):
    """Renders a single shortcut hint: [KEY] Description."""

    DEFAULT_CSS = """
    KeyboardShortcut {
        height: 1;
        width: auto;
    }
    """

    def __init__(self, key: str, description: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._key = key
        self._description = description

    def compose(self) -> ComposeResult:
        color = self._key_color()
        yield Label(
            f"[[bold {color}]{self._key}[/]] [dim]{self._description}[/]",
            markup=True,
        )

    def _key_color(self) -> str:
        if self._key.lower() in ("q", "escape", "ctrl+c"):
            return "red"
        if self._key in ("/", "?"):
            return "cyan"
        if self._key.lower().startswith("ctrl"):
            return "yellow"
        return "green"


class KeyboardShortcutBar(Widget):
    """Horizontal row of keyboard shortcut hints."""

    DEFAULT_CSS = """
    KeyboardShortcutBar {
        height: 1;
        background: $panel;
        padding: 0 1;
    }
    KeyboardShortcutBar Horizontal { height: 1; }
    KeyboardShortcutBar KeyboardShortcut { margin-right: 2; }
    """

    def __init__(self, shortcuts: list[tuple[str, str]], **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._shortcuts = shortcuts

    def compose(self) -> ComposeResult:
        with Horizontal():
            for key, desc in self._shortcuts:
                yield KeyboardShortcut(key, desc)
