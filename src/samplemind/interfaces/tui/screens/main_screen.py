"""
Main Screen for SampleMind TUI
Entry point with menu and navigation
"""

from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header

from ..widgets import MainMenu, StatusBar
from .chain_screen import ChainScreen
from .favorites_screen import FavoritesScreen
from .search_screen import SearchScreen
from .settings_screen import SettingsScreen


class MainScreen(Screen):
    """Main application screen with menu and status bar"""

    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
    }

    #main_container {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
    }

    #menu_area {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #status_area {
        width: 1fr;
        height: auto;
        padding: 1 0;
    }
    """

    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("a", "analyze", "Analyze"),
        ("b", "batch", "Batch"),
        ("f", "favorites", "Favorites"),
        ("s", "settings", "Settings"),
        ("h", "help", "Help"),
        ("k", "search", "Search (Keywords/Semantic)"),
        ("c", "chain", "Chain Recommender"),
    ]

    def compose(self):
        """Compose the main screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="main_container"):
            with Vertical(id="menu_area"):
                yield MainMenu()

            yield StatusBar(id="status_bar")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the main screen"""
        self.title = "SampleMind AI v6 - Professional Music Production Suite"
        status_bar = self.query_one(StatusBar)
        status_bar.update_status("Ready • Use arrow keys to navigate")

    def action_quit_app(self) -> None:
        """Exit the application"""
        self.app.exit()

    def action_analyze(self) -> None:
        """Navigate to analyze screen"""
        # This will be handled by the app when screen is implemented
        self.notify("Analyze feature coming soon!")

    def action_batch(self) -> None:
        """Navigate to batch processing screen"""
        # This will be handled by the app when screen is implemented
        self.notify("Batch processing coming soon!")

    def action_search(self) -> None:
        """Navigate to search screen"""
        self.app.push_screen(SearchScreen())

    def action_chain(self) -> None:
        """Navigate to chain recommender"""
        self.app.push_screen(ChainScreen())

    def action_favorites(self) -> None:
        """Navigate to favorites screen"""
        self.app.push_screen(FavoritesScreen())

    def action_settings(self) -> None:
        """Navigate to settings screen"""
        self.app.push_screen(SettingsScreen())

    def action_help(self) -> None:
        """Show help information"""
        self.notify(
            "🎵 SampleMind AI v6 Help\n\n"
            "Main Controls:\n"
            "  Q - Quit application\n"
            "  A - Analyze single file\n"
            "  B - Batch process folder\n"
            "  K - Search (Semantic/Keyword)\n"
            "  C - Chain Recommender\n"
            "  F - View favorites\n"
            "  S - Settings\n"
            "  H - Show this help\n\n"
            "Menu Navigation:\n"
            "  ↑/↓ - Move up/down\n"
            "  ENTER - Select option\n"
            "  MOUSE - Click to select\n"
        )
