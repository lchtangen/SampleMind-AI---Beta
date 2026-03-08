"""Main Screen for SampleMind TUI v3.0 — Navigation hub"""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label

from ..widgets.menu import MainMenu, MenuSelected
from ..widgets.status_bar import StatusBar


class MainScreen(Screen):
    """Navigation hub with left menu + right quick-start panel."""

    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("a", "goto_analyze", "Analyze"),
        Binding("b", "goto_batch", "Batch"),
        Binding("l", "goto_library", "Library"),
        Binding("k", "goto_search", "Search"),
        Binding("i", "goto_ai_chat", "AI Chat"),
        Binding("v", "goto_visualizer", "Visualizer"),
        Binding("f", "goto_favorites", "Favorites"),
        Binding("t", "goto_tagging", "Tag"),
        Binding("c", "goto_chain", "Chain"),
        Binding("s", "goto_settings", "Settings"),
        Binding("/", "command_palette", "Commands"),
        Binding("?", "show_help", "Help"),
    ]

    DEFAULT_CSS = """
    MainScreen { layout: vertical; }
    #screen_body { layout: horizontal; height: 1fr; }
    #menu_panel { width: 32; padding: 1 0; border-right: solid $primary 30%; }
    #info_panel { width: 1fr; padding: 1 2; }
    #app_title { color: $primary; text-style: bold; margin-bottom: 1; height: 2; }
    #tagline { color: $foreground 60%; margin-bottom: 2; }
    .hint { height: 1; margin-bottom: 1; color: $foreground 80%; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="screen_body"):
            with Vertical(id="menu_panel"):
                yield MainMenu()
            with Vertical(id="info_panel"):
                yield Label("SampleMind AI v3.0", id="app_title")
                yield Label(
                    "Intelligent sample analysis · Offline-first · Multi-provider AI",
                    id="tagline",
                )
                yield Label(
                    "[a] Analyze  [b] Batch  [l] Library  [k] Search",
                    classes="hint",
                    markup=True,
                )
                yield Label(
                    "[i] AI Chat  [v] Visualizer  [s] Settings  [q] Quit",
                    classes="hint",
                    markup=True,
                )
                yield Label("", classes="hint")
                yield Label(
                    "[/] Command palette  [?] Keyboard reference",
                    classes="hint",
                    markup=True,
                )
        yield StatusBar(id="status_bar")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(StatusBar).update_status(
            "Ready - navigate with keyboard or menu"
        )

    @on(MenuSelected)
    def on_menu_selected(self, event: MenuSelected) -> None:
        dispatch = {
            "analyze": self.action_goto_analyze,
            "batch": self.action_goto_batch,
            "library": self.action_goto_library,
            "search": self.action_goto_search,
            "ai_chat": self.action_goto_ai_chat,
            "visualizer": self.action_goto_visualizer,
            "favorites": self.action_goto_favorites,
            "tagging": self.action_goto_tagging,
            "chain": self.action_goto_chain,
            "settings": self.action_goto_settings,
            "quit": self.action_quit_app,
        }
        handler = dispatch.get(event.action)
        if handler:
            handler()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_goto_analyze(self) -> None:
        from .analyze_screen import AnalyzeScreen

        self.app.push_screen(AnalyzeScreen())

    def action_goto_batch(self) -> None:
        from .batch_screen import BatchScreen

        self.app.push_screen(BatchScreen())

    def action_goto_library(self) -> None:
        from .library_screen import LibraryScreen

        self.app.push_screen(LibraryScreen())

    def action_goto_search(self) -> None:
        from .search_screen import SearchScreen

        self.app.push_screen(SearchScreen())

    def action_goto_ai_chat(self) -> None:
        from .ai_chat_screen import AIChatScreen

        self.app.push_screen(AIChatScreen())

    def action_goto_visualizer(self) -> None:
        from .visualizer_screen import VisualizerScreen

        self.app.push_screen(VisualizerScreen())

    def action_goto_favorites(self) -> None:
        from .favorites_screen import FavoritesScreen

        self.app.push_screen(FavoritesScreen())

    def action_goto_tagging(self) -> None:
        from .tagging_screen import TaggingScreen

        self.app.push_screen(TaggingScreen())

    def action_goto_chain(self) -> None:
        from .chain_screen import ChainScreen

        self.app.push_screen(ChainScreen())

    def action_goto_settings(self) -> None:
        from .settings_screen import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def action_show_help(self) -> None:
        from ..widgets.dialogs import InfoDialog

        help_text = (
            "A / Analyze a file\n"
            "B / Batch process folder\n"
            "L / Library browser\n"
            "K / Search samples\n"
            "I / AI Chat\n"
            "V / Visualizer\n"
            "F / Favorites\n"
            "T / Tagging\n"
            "C / Effects chain\n"
            "S / Settings\n"
            "/ / Command palette\n"
            "? / This help\n"
            "Q / Quit\n\n"
            "In any screen  Escape = Go back"
        )
        self.app.push_screen(
            InfoDialog("SampleMind AI v3.0 - Keyboard Reference", help_text)
        )
