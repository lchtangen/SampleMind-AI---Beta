"""
Status Bar Widget for SampleMind TUI
Displays session statistics and real-time status information
"""

from datetime import datetime
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel


class StatusBar(Widget):
    """Status bar displaying session stats and system information"""

    DEFAULT_CSS = """
    StatusBar {
        width: 1fr;
        height: 3;
        border: solid $accent;
        padding: 0 1;
        background: $surface;
    }
    """

    files_analyzed: reactive[int] = reactive(0)
    time_elapsed: reactive[int] = reactive(0)
    ai_provider: reactive[str] = reactive("offline")
    status_message: reactive[str] = reactive("Ready")

    def render(self) -> Panel:
        """Render the status bar with current stats"""
        # Format time as MM:SS
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        # Build status text
        status_text = Text()
        status_text.append("📊 Files: ", style="dim cyan")
        status_text.append(str(self.files_analyzed), style="bold green")
        status_text.append("  |  ⏱️  Time: ", style="dim cyan")
        status_text.append(time_str, style="bold yellow")
        status_text.append("  |  🤖 AI: ", style="dim cyan")
        status_text.append(self.ai_provider, style="bold magenta")
        status_text.append("  |  ", style="dim")
        status_text.append(self.status_message, style="bold blue")

        return Panel(
            status_text,
            border_style="green",
            padding=(0, 1)
        )

    def update_files_analyzed(self, count: int) -> None:
        """Update the files analyzed counter"""
        self.files_analyzed = count

    def update_status(self, message: str) -> None:
        """Update the status message"""
        self.status_message = message

    def update_ai_provider(self, provider: str) -> None:
        """Update the current AI provider"""
        self.ai_provider = provider

    def increment_time(self) -> None:
        """Increment elapsed time by 1 second"""
        self.time_elapsed += 1

    def reset(self) -> None:
        """Reset status bar to initial state"""
        self.files_analyzed = 0
        self.time_elapsed = 0
        self.ai_provider = "offline"
        self.status_message = "Ready"
