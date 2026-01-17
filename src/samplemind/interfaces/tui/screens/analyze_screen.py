"""
Analyze Screen for SampleMind TUI
Single file analysis with progress tracking
"""

from pathlib import Path
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text


class AnalyzeScreen(Screen):
    """Screen for analyzing single audio files"""

    DEFAULT_CSS = """
    AnalyzeScreen {
        layout: vertical;
    }

    #analyze_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #file_input {
        width: 1fr;
        height: 3;
        margin-bottom: 1;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 1;
    }

    #results_area {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
        padding: 1;
        overflow: auto;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "analyze_file", "Analyze"),
    ]

    file_path: reactive[str] = reactive("")
    is_analyzing: reactive[bool] = reactive(False)

    def compose(self):
        """Compose the analyze screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="analyze_container"):
            yield Static(
                self._render_title(),
                id="analyze_title"
            )

            yield Input(
                placeholder="Enter audio file path (WAV, MP3, FLAC, M4A, OGG)...",
                id="file_input"
            )

            with Horizontal(id="button_area"):
                yield Button("📁 Browse", id="browse_btn", variant="primary")
                yield Button("🎵 Analyze", id="analyze_btn", variant="success")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

            yield Static(
                self._render_placeholder(),
                id="results_area"
            )

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text("🎯 Analyze Single Audio File", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def _render_placeholder(self) -> Panel:
        """Render placeholder for results"""
        text = Text(
            "📊 Analysis results will appear here\n\n"
            "Supported formats: WAV, MP3, FLAC, M4A, OGG, AIFF\n"
            "Features extracted: tempo, key, spectral analysis, MFCC, and more",
            style="dim"
        )
        return Panel(text, border_style="blue", padding=(1, 2))

    def on_mount(self) -> None:
        """Initialize the analyze screen"""
        self.title = "SampleMind - Analyze"
        file_input = self.query_one("#file_input", Input)
        file_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "browse_btn":
            self.action_browse_file()
        elif button_id == "analyze_btn":
            self.action_analyze_file()
        elif button_id == "back_btn":
            self.action_back()

    def action_browse_file(self) -> None:
        """Open file browser"""
        # File picker will be integrated later
        self.notify("File browser coming soon!")

    def action_analyze_file(self) -> None:
        """Start file analysis"""
        file_input = self.query_one("#file_input", Input)
        file_path = file_input.value.strip()

        if not file_path:
            self.notify("❌ Please enter a file path", severity="error")
            return

        file = Path(file_path)
        if not file.exists():
            self.notify(f"❌ File not found: {file_path}", severity="error")
            return

        # Analysis will be implemented with AudioEngine integration
        self.notify(f"✅ Starting analysis of {file.name}...")

    def action_back(self) -> None:
        """Return to main screen"""
        self.app.pop_screen()
