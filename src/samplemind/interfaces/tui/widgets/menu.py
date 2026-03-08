"""Main Menu Widget for SampleMind TUI — Textual ^0.87"""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import ListItem, ListView, Label

MENU_OPTIONS: list[tuple[str, str]] = [
    ("🎵  Analyze Audio", "analyze"),
    ("📦  Batch Process", "batch"),
    ("📚  Library Browser", "library"),
    ("🔍  Search Samples", "search"),
    ("🤖  AI Chat", "ai_chat"),
    ("📊  Visualizer", "visualizer"),
    ("⭐  Favorites", "favorites"),
    ("🏷️   Tag Samples", "tagging"),
    ("🎚️   Effects Chain", "chain"),
    ("⚙️   Settings", "settings"),
    ("❌  Quit", "quit"),
]


class MenuSelected(Message):
    """Posted when a menu option is selected."""

    def __init__(self, action: str) -> None:
        super().__init__()
        self.action = action


class MainMenuOption(Message):
    """Deprecated — use MenuSelected instead."""

    def __init__(self, option: str) -> None:
        super().__init__()
        self.option = option


class MainMenu(Widget):
    """Interactive main navigation menu using ListView."""

    DEFAULT_CSS = """
    MainMenu {
        height: auto;
    }
    MainMenu ListView {
        height: auto;
        border: none;
        padding: 0 1;
        background: transparent;
    }
    MainMenu ListItem {
        height: 1;
        padding: 0 1;
    }
    MainMenu ListItem.-highlighted {
        background: $primary 40%;
        color: $background;
    }
    """

    def compose(self) -> ComposeResult:
        items = [ListItem(Label(label), name=action) for label, action in MENU_OPTIONS]
        yield ListView(*items, id="menu_list")

    @on(ListView.Selected, "#menu_list")
    def on_menu_selected(self, event: ListView.Selected) -> None:
        if event.item.name:
            self.post_message(MenuSelected(event.item.name))
            self.post_message(MainMenuOption(event.item.name))
