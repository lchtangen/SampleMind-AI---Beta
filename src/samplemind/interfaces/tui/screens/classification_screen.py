"""AI Classification Screen for SampleMind TUI.

Provides bulk AI classification and auto-tagging capabilities with
real-time progress tracking and results visualization.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from rich.panel import Panel
from rich.text import Text
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from samplemind.ai.classification.auto_tagger import AutoTagger
from samplemind.core.engine.audio_engine import AnalysisLevel
from samplemind.interfaces.tui.audio_engine_bridge import get_tui_engine
from samplemind.interfaces.tui.widgets.dialogs import (
    ConfirmDialog,
    ErrorDialog,
    InfoDialog,
    WarningDialog,
)
from samplemind.utils.file_picker import CrossPlatformFilePicker


class ClassificationScreen(Screen):
    """Screen for AI-powered sample classification and auto-tagging."""

    DEFAULT_CSS = """
    ClassificationScreen {
        layout: vertical;
    }

    #classification_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #folder_input {
        width: 1fr;
        height: 3;
        margin-bottom: 1;
    }

    #status_area {
        width: 1fr;
        height: 2;
        border: solid $success;
        padding: 0 1;
        margin-bottom: 1;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 0;
        margin-bottom: 1;
    }

    #results_table {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
    }

    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "classify", "Classify"),
        Binding("c", "cancel_processing", "Cancel", show=False),
    ]

    folder_path: reactive[str] = reactive("")
    is_processing: reactive[bool] = reactive(False)
    files_processed: reactive[int] = reactive(0)
    total_files: reactive[int] = reactive(0)
    confidence_threshold: reactive[float] = reactive(0.60)

    def __init__(self) -> None:
        """Initialize classification screen."""
        super().__init__()
        self.audio_files: List[str] = []
        self.classification_results: Dict[str, Dict] = {}
        self.cancel_requested = False

    def compose(self):
        """Compose the classification screen layout."""
        yield Header(show_clock=True)

        with Vertical(id="classification_container"):
            # Title
            yield Static(self._render_title(), id="classification_title")

            # Folder input
            yield Input(
                placeholder="Enter folder path to classify (or click Browse)...",
                id="folder_input",
            )

            # Status and progress display
            yield Static(
                self._render_status(),
                id="status_area",
            )

            # Button area
            with Horizontal(id="button_area"):
                yield Button("📁 Browse", id="browse_btn", variant="primary")
                yield Button("🔍 Scan Folder", id="scan_btn", variant="primary")
                yield Button("🤖 Classify All", id="classify_btn", variant="success")
                yield Button("❌ Cancel", id="cancel_btn", variant="error")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

            # Results table
            results_table = DataTable(id="results_table")
            results_table.add_columns(
                "File",
                "Instrument",
                "Genre",
                "Mood",
                "Quality",
                "Tempo",
                "Tags",
            )
            yield results_table

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title."""
        title = Text("🤖 AI Sample Classification & Auto-Tagging", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def _render_status(self) -> Panel:
        """Render status and progress."""
        if self.is_processing:
            progress = (
                f"{self.files_processed}/{self.total_files}"
                if self.total_files > 0
                else "0/0"
            )
            status_text = f"Classifying: {progress} files"
            return Panel(
                Text(status_text, style="bold green"),
                border_style="green",
                padding=(0, 1),
            )
        else:
            threshold_text = f"Confidence: {self.confidence_threshold:.0%}"
            files_text = f"Files: {len(self.audio_files)}"
            return Panel(
                Text(f"Ready | {threshold_text} | {files_text}", style="dim yellow"),
                border_style="yellow",
                padding=(0, 1),
            )

    def on_mount(self) -> None:
        """Initialize the classification screen."""
        self.title = "SampleMind - AI Classification"
        self.tui_engine = get_tui_engine()
        self.file_picker = CrossPlatformFilePicker()
        self.auto_tagger = AutoTagger(confidence_threshold=self.confidence_threshold)

        folder_input = self.query_one("#folder_input", Input)
        folder_input.focus()

    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "browse_btn":
            self.action_browse_folder()
        elif button_id == "scan_btn":
            self.action_scan_folder()
        elif button_id == "classify_btn":
            self.action_classify()
        elif button_id == "cancel_btn":
            self.action_cancel_processing()
        elif button_id == "back_btn":
            self.action_back()

    def action_browse_folder(self) -> None:
        """Open cross-platform folder browser."""
        try:
            selected_folder = self.file_picker.choose_folder(
                title="Select Folder for Classification"
            )

            if selected_folder:
                folder_input = self.query_one("#folder_input", Input)
                folder_input.value = selected_folder
                self.notify(
                    f"✅ Selected: {Path(selected_folder).name}",
                    severity="information",
                )

        except Exception as e:
            error_msg = str(e)
            if "cancelled" in error_msg.lower() or "cancel" in error_msg.lower():
                return

            self.app.push_screen(
                ErrorDialog(
                    "Folder Selection Error",
                    f"Error selecting folder:\n\n{error_msg}",
                )
            )

    def action_scan_folder(self) -> None:
        """Scan folder for audio files."""
        folder_input = self.query_one("#folder_input", Input)
        folder_path = folder_input.value.strip()

        if not folder_path:
            self.app.push_screen(
                ErrorDialog(
                    "Empty Folder Path",
                    "Please enter a folder path or use the Browse button.",
                )
            )
            return

        folder = Path(folder_path).expanduser()

        if not folder.exists():
            self.app.push_screen(
                ErrorDialog(
                    "Folder Not Found",
                    f"Folder does not exist:\n\n{folder}",
                )
            )
            return

        if not folder.is_dir():
            self.app.push_screen(
                ErrorDialog(
                    "Not a Directory",
                    f"Path is not a directory:\n\n{folder}",
                )
            )
            return

        # Find audio files
        audio_extensions = {".wav", ".mp3", ".flac", ".m4a", ".aiff", ".ogg"}
        self.audio_files = [
            str(f)
            for f in folder.rglob("*")
            if f.is_file() and f.suffix.lower() in audio_extensions
        ]

        if not self.audio_files:
            self.app.push_screen(
                WarningDialog(
                    "No Audio Files Found",
                    f"No audio files found in:\n\n{folder}",
                )
            )
            return

        # Populate table
        self._populate_results_table()
        self.notify(
            f"✅ Found {len(self.audio_files)} audio files",
            severity="information",
        )

    def _populate_results_table(self) -> None:
        """Populate results table with scanned files."""
        table = self.query_one("#results_table", DataTable)
        table.clear()

        for audio_file in self.audio_files:
            file_path = Path(audio_file)
            table.add_row(
                file_path.name,
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                key=audio_file,
            )

    def action_classify(self) -> None:
        """Start classification process."""
        if not self.audio_files:
            self.app.push_screen(
                ErrorDialog(
                    "No Files",
                    "Please scan a folder first to find audio files.",
                )
            )
            return

        self.app.push_screen(
            ConfirmDialog(
                "Confirm Classification",
                f"Classify {len(self.audio_files)} files?\n\n"
                f"This may take several minutes depending on file count.",
                confirm_callback=self._do_classification,
            )
        )

    def _do_classification(self) -> None:
        """Execute classification on all files."""
        self.cancel_requested = False
        asyncio.create_task(self._classify_files_async())

    async def _classify_files_async(self) -> None:
        """Asynchronously classify all files."""
        self.is_processing = True
        self.total_files = len(self.audio_files)
        self.files_processed = 0

        try:
            for i, audio_file in enumerate(self.audio_files):
                if self.cancel_requested:
                    self.notify("❌ Classification cancelled", severity="warning")
                    break

                try:
                    file_path = Path(audio_file)

                    # Extract features using tui_engine
                    features = await self.tui_engine.analyze_file(
                        file_path,
                        progress_callback=None,
                    )

                    # Classify and generate tags
                    tags = self.auto_tagger.auto_tag_sample(features, file_path)

                    # Store classification result
                    classification = self.auto_tagger.classifier.classify_audio(
                        features
                    )

                    self.classification_results[audio_file] = {
                        "classification": classification,
                        "tags": tags,
                    }

                    # Update table
                    self._update_result_row(
                        audio_file,
                        classification,
                        tags,
                    )

                except Exception as e:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.error(f"Error classifying {audio_file}: {e}")
                    self.classification_results[audio_file] = {
                        "error": str(e),
                    }

                self.files_processed = i + 1

        except Exception as e:
            self.app.push_screen(
                ErrorDialog(
                    "Classification Error",
                    f"Error during classification:\n\n{str(e)}",
                )
            )

        finally:
            self.is_processing = False
            if not self.cancel_requested:
                self.notify(
                    f"✅ Classification complete: {self.files_processed} files",
                    severity="information",
                )

    def _update_result_row(self, audio_file: str, classification, tags: List[str]) -> None:
        """Update a result row in the table."""
        table = self.query_one("#results_table", DataTable)

        try:
            table.update_cell(
                row_key=audio_file,
                column_key="Instrument",
                value=classification.instrument[:12],
            )
            table.update_cell(
                row_key=audio_file,
                column_key="Genre",
                value=classification.genre[:12],
            )
            table.update_cell(
                row_key=audio_file,
                column_key="Mood",
                value=classification.mood[:12],
            )
            table.update_cell(
                row_key=audio_file,
                column_key="Quality",
                value=f"{classification.quality_score:.0%}",
            )
            table.update_cell(
                row_key=audio_file,
                column_key="Tempo",
                value=classification.tempo_category[:4],
            )
            table.update_cell(
                row_key=audio_file,
                column_key="Tags",
                value=", ".join(tags[:3]),
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error updating table row: {e}")

    def action_cancel_processing(self) -> None:
        """Cancel ongoing classification process."""
        if self.is_processing:
            self.cancel_requested = True
            self.notify("Cancelling classification...", severity="warning")

    def action_back(self) -> None:
        """Go back to previous screen."""
        if self.is_processing:
            self.app.push_screen(
                WarningDialog(
                    "Classification In Progress",
                    "Classification is still running. Cancel first?",
                )
            )
        else:
            self.app.pop_screen()
