"""
SampleMind TUI Application
Modern Textual-based CLI for professional music production
"""

import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .screens import (
    MainScreen,
    AnalyzeScreen,
    BatchScreen,
    ResultsScreen,
    FavoritesScreen,
    SettingsScreen,
    ComparisonScreen,
    SearchScreen,
    TaggingScreen,
    PerformanceScreen,
    LibraryScreen,
)

# Import new systems
from .integrations import get_fl_studio_integration
from .history import get_history_manager
from .playback import get_audio_player
from .ai import get_ai_coach
from .monitoring import get_performance_monitor
from .library import get_library_browser
from .plugins import get_plugin_manager, get_hook_system
from .keyboard import get_shortcut_manager
from .session import get_session_manager


class SampleMindTUI(App):
    """Main SampleMind TUI Application"""

    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
        height: 1;
    }

    Footer {
        background: $primary;
        color: $text;
    }
    """

    BINDINGS = [
        ("q", "quit_app", "Quit"),
    ]

    TITLE = "🎵 SampleMind AI v6 - Professional Music Production Suite"
    SUB_TITLE = "Modern Terminal UI with Offline-First Architecture"

    def on_mount(self) -> None:
        """Initialize the application"""
        self.push_screen(MainScreen())

    def action_quit_app(self) -> None:
        """Gracefully quit the application"""
        self.exit()


async def run_tui():
    """Run the Textual TUI application"""
    app = SampleMindTUI()
    await app.run_async()


def main() -> None:
    """Entry point for TUI"""
    import asyncio

    try:
        asyncio.run(run_tui())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
