"""Status Bar Widget for SampleMind TUI — Textual ^0.87 (KP 50)"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


class StatusBar(Widget):
    """Always-visible status bar with live metrics."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $panel;
        color: $foreground;
        dock: bottom;
    }
    StatusBar Horizontal {
        height: 1;
        width: 1fr;
    }
    StatusBar .status-item {
        height: 1;
        min-width: 16;
        padding: 0 1;
        border-right: solid $primary 40%;
    }
    StatusBar .status-model { color: $primary; text-style: bold; }
    StatusBar .status-api-online { color: $success; }
    StatusBar .status-api-offline { color: $error; }
    StatusBar .status-version { text-style: dim; padding: 0 1; color: $foreground 50%; }
    """

    active_model: reactive[str] = reactive("Offline")
    library_count: reactive[int] = reactive(0)
    api_status: reactive[str] = reactive("offline")
    last_action: reactive[str] = reactive("Ready")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(id="model_label", classes="status-item status-model")
            yield Label(id="library_label", classes="status-item")
            yield Label(id="action_label", classes="status-item")
            yield Label(id="api_label", classes="status-item")
            yield Label("v3.0", classes="status-version")

    def on_mount(self) -> None:
        self._refresh_all()

    def watch_active_model(self, model: str) -> None:
        try:
            self.query_one("#model_label", Label).update(f"🤖 {model}")
        except Exception:
            pass

    def watch_library_count(self, count: int) -> None:
        try:
            self.query_one("#library_label", Label).update(f"📚 {count:,} samples")
        except Exception:
            pass

    def watch_last_action(self, action: str) -> None:
        try:
            self.query_one("#action_label", Label).update(f"✔ {action}")
        except Exception:
            pass

    def watch_api_status(self, status: str) -> None:
        try:
            label = self.query_one("#api_label", Label)
            if status == "online":
                label.update("● Online")
                label.remove_class("status-api-offline")
                label.add_class("status-api-online")
            else:
                label.update("● Offline")
                label.remove_class("status-api-online")
                label.add_class("status-api-offline")
        except Exception:
            pass

    def update_status(self, message: str) -> None:
        self.last_action = message

    def _refresh_all(self) -> None:
        self.watch_active_model(self.active_model)
        self.watch_library_count(self.library_count)
        self.watch_last_action(self.last_action)
        self.watch_api_status(self.api_status)
