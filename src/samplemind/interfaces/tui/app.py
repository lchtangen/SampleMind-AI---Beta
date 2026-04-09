"""
SampleMind TUI Application — v3.0
Terminal UI built with Textual ^0.87 for professional music production
"""

from __future__ import annotations

import sys
from pathlib import Path

from textual.app import App
from textual.binding import Binding
from textual.theme import Theme

# ── SampleMind Design Palette ────────────────────────────────────────────────
_TEAL = "#00F5FF"
_PURPLE_DARK = "#1A0A2E"
_PURPLE_MID = "#241040"
_LIME = "#A8FF3E"
_HOT_PINK = "#FF007F"

# ── Six custom themes ────────────────────────────────────────────────────────
_THEMES: list[Theme] = [
    Theme(
        name="samplemind-dark",
        dark=True,
        primary=_TEAL,
        secondary="#0066CC",
        accent=_LIME,
        background=_PURPLE_DARK,
        surface=_PURPLE_MID,
        panel="#2D0A4E",
        boost="#3A1060",
        warning="#FFD700",
        error=_HOT_PINK,
        success=_LIME,
    ),
    Theme(
        name="samplemind-light",
        dark=False,
        primary="#0088AA",
        secondary="#005580",
        accent="#007755",
        background="#F5F5F5",
        surface="#FFFFFF",
        panel="#E8EEF2",
        boost="#D0D8E0",
        warning="#FF9500",
        error="#CC002B",
        success="#007755",
    ),
    Theme(
        name="midnight-pro",
        dark=True,
        primary="#FFD700",
        secondary="#FFA500",
        accent="#FFB800",
        background="#000000",
        surface="#111111",
        panel="#1A1A1A",
        boost="#242424",
        warning="#FF8C00",
        error="#FF4040",
        success="#00FF88",
    ),
    Theme(
        name="neon-synthwave",
        dark=True,
        primary=_HOT_PINK,
        secondary="#8338EC",
        accent=_LIME,
        background="#0D0015",
        surface="#1A0033",
        panel="#240044",
        boost="#300055",
        warning="#FFD60A",
        error="#FF006E",
        success=_LIME,
    ),
    Theme(
        name="forest-green",
        dark=True,
        primary=_LIME,
        secondary="#4CAF50",
        accent="#FFC107",
        background="#0A1F0A",
        surface="#112211",
        panel="#1A331A",
        boost="#234423",
        warning="#FFC107",
        error="#FF5252",
        success=_LIME,
    ),
    Theme(
        name="high-contrast",
        dark=True,
        primary="#FFFFFF",
        secondary="#FFFF00",
        accent="#00FFFF",
        background="#000000",
        surface="#0A0A0A",
        panel="#111111",
        boost="#222222",
        warning="#FFFF00",
        error="#FF0000",
        success="#00FF00",
    ),
]

# Expose theme names for settings screen
THEME_NAMES: list[str] = [t.name for t in _THEMES]


class SampleMindTUI(App[None]):
    """SampleMind AI TUI — Professional music production assistant."""

    TITLE = "🎵 SampleMind AI v3.0"
    SUB_TITLE = "Intelligent Sample Analysis • Offline-First • Multi-Provider AI"

    CSS_PATH = [Path(__file__).parent / "themes" / "base.tcss"]

    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("/", "command_palette", "Commands"),
        Binding("ctrl+p", "command_palette", "Commands", show=False),
    ]

    def on_mount(self) -> None:
        """Bootstrap: register all themes then push main screen."""
        for theme in _THEMES:
            self.register_theme(theme)
        self.theme = "samplemind-dark"

        from .screens import MainScreen

        self.push_screen(MainScreen())

    def action_quit_app(self) -> None:
        """Gracefully exit."""
        self.exit()

    @property
    def commands(self):  # type: ignore[override]
        """Lazily import commands provider to avoid circular imports."""
        try:
            from .commands import SampleMindCommands

            return {SampleMindCommands}
        except ImportError:
            return set()


async def run_tui() -> None:
    """Run the Textual TUI application asynchronously."""
    app = SampleMindTUI()
    await app.run_async()


def main() -> None:
    """Entry point for TUI."""
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
