"""
Batch Screen for SampleMind TUI
Batch file processing with progress tracking
"""

from pathlib import Path
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, DataTable
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from rich.panel import Panel
from rich.text import Text


class BatchScreen(Screen):
    """Screen for batch processing audio files"""

    DEFAULT_CSS = """
    BatchScreen {
        layout: vertical;
    }

    #batch_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #folder_input {
        width: 1fr;
        height: 3;
        margin-bottom: 1;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 1;
        margin-bottom: 1;
    }

    #files_table {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "process_batch", "Process"),
    ]

    folder_path: reactive[str] = reactive("")
    is_processing: reactive[bool] = reactive(False)

    def compose(self):
        """Compose the batch screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="batch_container"):
            yield Static(
                self._render_title(),
                id="batch_title"
            )

            yield Input(
                placeholder="Enter folder path to batch process...",
                id="folder_input"
            )

            with Horizontal(id="button_area"):
                yield Button("📁 Browse", id="browse_btn", variant="primary")
                yield Button("🚀 Process", id="process_btn", variant="success")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

            # File list table
            files_table = DataTable(id="files_table")
            files_table.add_columns("File", "Size", "Duration", "Status")
            yield files_table

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text("📁 Batch Process Audio Files", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def on_mount(self) -> None:
        """Initialize the batch screen"""
        self.title = "SampleMind - Batch Process"
        folder_input = self.query_one("#folder_input", Input)
        folder_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "browse_btn":
            self.action_browse_folder()
        elif button_id == "process_btn":
            self.action_process_batch()
        elif button_id == "back_btn":
            self.action_back()

    def action_browse_folder(self) -> None:
        """Open folder browser"""
        # Folder picker will be integrated later
        self.notify("Folder browser coming soon!")

    def action_process_batch(self) -> None:
        """Start batch processing"""
        folder_input = self.query_one("#folder_input", Input)
        folder_path = folder_input.value.strip()

        if not folder_path:
            self.notify("❌ Please enter a folder path", severity="error")
            return

        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            self.notify(f"❌ Folder not found: {folder_path}", severity="error")
            return

        # Batch processing will be implemented with AudioEngine integration
        self.notify(f"✅ Starting batch processing of {folder.name}...")

    def action_back(self) -> None:
        """Return to main screen"""
        self.app.pop_screen()
