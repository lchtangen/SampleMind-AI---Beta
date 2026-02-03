"""
Batch Screen for SampleMind TUI
Batch file processing with parallel analysis and progress tracking
"""

import asyncio
import os
from pathlib import Path
from typing import List

from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, DataTable
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from textual.binding import Binding

from rich.panel import Panel
from rich.text import Text

from samplemind.interfaces.tui.audio_engine_bridge import get_tui_engine
from samplemind.core.engine.audio_engine import AnalysisLevel
from samplemind.utils.file_picker import CrossPlatformFilePicker
from samplemind.interfaces.tui.widgets.dialogs import (
    ErrorDialog,
    InfoDialog,
    ConfirmDialog,
    WarningDialog,
)


class BatchScreen(Screen):
    """Screen for batch processing multiple audio files with parallel analysis"""

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

    #level_progress_area {
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

    #files_table {
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
        ("enter", "scan_folder", "Scan"),
        Binding("c", "cancel_processing", "Cancel", show=False),
    ]

    folder_path: reactive[str] = reactive("")
    is_processing: reactive[bool] = reactive(False)
    analysis_level: reactive[str] = reactive("STANDARD")

    def __init__(self):
        """Initialize batch screen"""
        super().__init__()
        self.audio_files: List[str] = []
        self.results = []
        self.cancel_requested = False

    def compose(self):
        """Compose the batch screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="batch_container"):
            # Title
            yield Static(
                self._render_title(),
                id="batch_title"
            )

            # Folder input
            yield Input(
                placeholder="Enter folder path to batch process (or click Browse)...",
                id="folder_input"
            )

            # Analysis level and progress display
            yield Static(
                self._render_level_progress(),
                id="level_progress_area"
            )

            # Button area with primary actions
            with Horizontal(id="button_area"):
                yield Button("📁 Browse", id="browse_btn", variant="primary")
                yield Button("🔍 Scan Folder", id="scan_btn", variant="primary")
                yield Button("🚀 Process All", id="process_btn", variant="success")
                yield Button("❌ Cancel", id="cancel_btn", variant="error")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

            # File list table with detailed columns
            files_table = DataTable(id="files_table")
            files_table.add_columns(
                "File",
                "Size",
                "Duration",
                "Tempo",
                "Key",
                "Status"
            )
            yield files_table

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text("📁 Batch Process Audio Files", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def _render_level_progress(self) -> Panel:
        """Render analysis level and progress"""
        if self.is_processing:
            progress_text = f"Processing: {len(self.results)}/{len(self.audio_files)} files"
            return Panel(
                Text(progress_text, style="bold green"),
                border_style="green",
                padding=(0, 1)
            )
        else:
            level_text = f"📊 Level: [{self.analysis_level[0].upper()}]{self.analysis_level[1:].lower()}"
            info = "Press [B]ASIC, [S]TANDARD, [D]ETAILED, or [P]ROFESSIONAL to change"
            return Panel(
                Text(f"{level_text} | {info}", style="dim yellow"),
                border_style="yellow",
                padding=(0, 1)
            )

    def on_mount(self) -> None:
        """Initialize the batch screen"""
        self.title = "SampleMind - Batch Process"
        self.tui_engine = get_tui_engine()
        self.file_picker = CrossPlatformFilePicker()
        self.analysis_level = AnalysisLevel.STANDARD.name

        folder_input = self.query_one("#folder_input", Input)
        folder_input.focus()

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "browse_btn":
            self.action_browse_folder()
        elif button_id == "scan_btn":
            self.action_scan_folder()
        elif button_id == "process_btn":
            self.action_process_batch()
        elif button_id == "cancel_btn":
            self.action_cancel_processing()
        elif button_id == "back_btn":
            self.action_back()

    def action_browse_folder(self) -> None:
        """Open cross-platform folder browser with error handling"""
        try:
            selected_folder = self.file_picker.choose_folder(
                title="Select Folder for Batch Processing"
            )

            if selected_folder:
                folder_input = self.query_one("#folder_input", Input)
                folder_input.value = selected_folder

                # Validate folder is readable
                if not os.access(selected_folder, os.R_OK):
                    self.app.push_screen(
                        ErrorDialog(
                            "Folder Not Readable",
                            f"Permission denied accessing folder:\n\n{selected_folder}\n\n"
                            "Please check folder permissions."
                        )
                    )
                    return

                folder_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(selected_folder)
                    for filename in filenames
                ) / (1024 * 1024)

                self.notify(
                    f"✅ Selected: {os.path.basename(selected_folder)} "
                    f"({folder_size:.1f} MB)",
                    severity="information"
                )
        except PermissionError:
            self.app.push_screen(
                ErrorDialog(
                    "Permission Denied",
                    "You don't have permission to access the selected folder.\n\n"
                    "Please select a different folder or check permissions."
                )
            )
        except Exception as e:
            error_msg = str(e)
            if "cancelled" in error_msg.lower() or "cancel" in error_msg.lower():
                # User cancelled folder picker, don't show error
                return

            self.app.push_screen(
                ErrorDialog(
                    "Folder Selection Error",
                    f"Error selecting folder:\n\n{error_msg}"
                )
            )

    def action_scan_folder(self) -> None:
        """Scan folder for audio files and populate table with error handling"""
        folder_input = self.query_one("#folder_input", Input)
        folder_path = folder_input.value.strip()

        # Validate input
        if not folder_path:
            self.app.push_screen(
                ErrorDialog(
                    "No Folder Selected",
                    "Please enter or select a folder path to scan for audio files."
                )
            )
            return

        folder = Path(folder_path)

        # Validate folder exists
        if not folder.exists():
            self.app.push_screen(
                ErrorDialog(
                    "Folder Not Found",
                    f"The folder does not exist:\n\n{folder_path}"
                )
            )
            return

        # Validate path is a directory
        if not folder.is_dir():
            self.app.push_screen(
                ErrorDialog(
                    "Not a Folder",
                    f"The path is a file, not a folder:\n\n{folder_path}\n\n"
                    "Please select a folder containing audio files."
                )
            )
            return

        # Validate folder is readable
        if not os.access(folder_path, os.R_OK):
            self.app.push_screen(
                ErrorDialog(
                    "Folder Not Readable",
                    f"Permission denied accessing folder:\n\n{folder_path}\n\n"
                    "Please check folder permissions."
                )
            )
            return

        try:
            # Scan for audio files
            self.audio_files = self._scan_audio_files(folder)

            if not self.audio_files:
                self.app.push_screen(
                    WarningDialog(
                        "No Audio Files Found",
                        f"No audio files found in:\n\n{folder_path}\n\n"
                        "Supported formats: WAV, MP3, FLAC, M4A, OGG, AIFF"
                    )
                )
                return

            # Populate table
            table = self.query_one("#files_table", DataTable)
            table.clear()

            total_size = 0
            for file_path in self.audio_files:
                try:
                    file_size_bytes = os.path.getsize(file_path)
                    total_size += file_size_bytes
                    file_size = self._format_size(file_size_bytes)
                except OSError:
                    file_size = "?"

                table.add_row(
                    os.path.basename(file_path),
                    file_size,
                    "—",
                    "—",
                    "—",
                    "⏳ Pending"
                )

            # Show success notification with summary
            total_size_mb = total_size / (1024 * 1024)
            self.notify(
                f"✅ Found {len(self.audio_files)} audio file(s) "
                f"({total_size_mb:.1f} MB) ready for processing",
                severity="information"
            )

        except PermissionError:
            self.app.push_screen(
                ErrorDialog(
                    "Permission Denied",
                    f"You don't have permission to scan:\n\n{folder_path}\n\n"
                    "Please check folder permissions."
                )
            )
        except Exception as e:
            self.app.push_screen(
                ErrorDialog(
                    "Folder Scan Error",
                    f"Error scanning folder:\n\n{str(e)}"
                )
            )

    async def action_process_batch(self) -> None:
        """Start batch processing with parallel analysis and comprehensive error handling"""
        # Validate files are available
        if not self.audio_files:
            self.app.push_screen(
                ErrorDialog(
                    "No Files to Process",
                    "Please scan a folder first to find audio files for batch processing."
                )
            )
            return

        # Confirm batch processing
        confirm_dialog = ConfirmDialog(
            "Start Batch Processing?",
            f"About to process {len(self.audio_files)} audio file(s) "
            f"at {self.analysis_level} analysis level.\n\n"
            f"This may take several minutes."
        )

        self.app.push_screen(confirm_dialog)

        # Wait for confirmation result
        await self.app.animator.wait_until_complete()

        if not confirm_dialog.result:
            return  # User cancelled

        self.is_processing = True
        self.cancel_requested = False
        self.results = []

        # Disable buttons except Cancel
        buttons = self.query("Button")
        for btn in buttons:
            if btn.id != "cancel_btn":
                btn.disabled = True
            else:
                btn.disabled = False

        try:
            # Process files with progress callback
            results = await self.tui_engine.analyze_batch(
                self.audio_files,
                self._handle_batch_progress,
                self._get_analysis_level()
            )

            self.results = results
            self._update_table_with_results(results)

            # Show results summary
            successful = len([r for r in results if r is not None])
            failed = len(self.audio_files) - successful

            if failed == 0:
                self.notify(
                    f"✅ Batch processing complete: "
                    f"All {successful} files analyzed successfully",
                    severity="information"
                )
            else:
                self.app.push_screen(
                    WarningDialog(
                        "Batch Processing Completed with Issues",
                        f"Successful: {successful} files\n"
                        f"Failed: {failed} files\n\n"
                        f"Check the Status column for details."
                    )
                )

        except Exception as e:
            error_msg = str(e)
            self.app.push_screen(
                ErrorDialog(
                    "Batch Processing Error",
                    f"An error occurred during batch processing:\n\n{error_msg}"
                )
            )

        finally:
            self.is_processing = False
            self.cancel_requested = False

            # Re-enable all buttons
            for btn in buttons:
                btn.disabled = False

    def _handle_batch_progress(self, current: int, total: int) -> None:
        """Handle batch progress updates"""
        if self.cancel_requested:
            return

        # Update progress display
        progress_area = self.query_one("#level_progress_area", Static)
        progress_text = f"Processing: {current}/{total} files ({current/total*100:.0f}%)"
        progress_area.update(Panel(
            Text(progress_text, style="bold green"),
            border_style="green",
            padding=(0, 1)
        ))

    def _update_table_with_results(self, results: list) -> None:
        """Update table rows with analysis results"""
        table = self.query_one("#files_table", DataTable)

        for i, features in enumerate(results):
            if features and i < len(self.audio_files):
                # Format tempo and key
                tempo = f"{features.tempo:.0f} BPM" if hasattr(features, 'tempo') else "—"
                key = f"{features.key} {features.mode}" if hasattr(features, 'key') else "—"
                duration = self._format_time(features.duration) if hasattr(features, 'duration') else "—"

                # Update row
                try:
                    table.update_cell_at(
                        (i, 2),
                        Text(duration, style="green")
                    )
                    table.update_cell_at(
                        (i, 3),
                        Text(tempo, style="cyan")
                    )
                    table.update_cell_at(
                        (i, 4),
                        Text(key, style="cyan")
                    )
                    table.update_cell_at(
                        (i, 5),
                        Text("✓ Complete", style="green")
                    )
                except Exception:
                    pass  # Row may not exist, skip

    def action_cancel_processing(self) -> None:
        """Request cancellation of batch processing"""
        if self.is_processing:
            self.cancel_requested = True
            self.notify(
                "⏸️  Cancellation requested... Processing will stop after current file.",
                severity="warning"
            )
        else:
            self.app.push_screen(
                InfoDialog(
                    "Not Processing",
                    "No batch processing is currently active.\n\n"
                    "Start batch processing by clicking 'Process All' after scanning a folder."
                )
            )

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts for analysis levels with enhanced feedback"""
        if self.is_processing:
            return

        level_info = {
            "b": (
                AnalysisLevel.BASIC.name,
                "Basic Analysis (Fastest)",
                "Fast batch analysis optimized for quick feedback.\n"
                "Perfect for quick library surveys and performance testing.\n"
                "Est. time: ~0.5 seconds per file"
            ),
            "s": (
                AnalysisLevel.STANDARD.name,
                "Standard Analysis (Balanced)",
                "Balanced batch analysis - default for most workflows.\n"
                "Recommended for comprehensive library analysis.\n"
                "Est. time: ~1.5 seconds per file"
            ),
            "d": (
                AnalysisLevel.DETAILED.name,
                "Detailed Analysis (Thorough)",
                "Comprehensive batch analysis with maximum features.\n"
                "Includes harmonic/percussive separation and rhythm analysis.\n"
                "Est. time: ~2.5 seconds per file"
            ),
            "p": (
                AnalysisLevel.PROFESSIONAL.name,
                "Professional Analysis (Comprehensive)",
                "Complete professional batch analysis.\n"
                "Maximum detail for production-critical large-scale analysis.\n"
                "Est. time: ~3.5 seconds per file"
            )
        }

        if event.key in level_info:
            level_name, title, description = level_info[event.key]
            self.analysis_level = level_name
            self._update_level_display()

            self.app.push_screen(
                InfoDialog(title, description)
            )

    def _update_level_display(self) -> None:
        """Update the level display area"""
        progress_area = self.query_one("#level_progress_area", Static)
        level_text = f"📊 Level: [{self.analysis_level[0].upper()}]{self.analysis_level[1:].lower()}"
        info = "Press [B]ASIC, [S]TANDARD, [D]ETAILED, or [P]ROFESSIONAL to change"
        progress_area.update(Panel(
            Text(f"{level_text} | {info}", style="dim yellow"),
            border_style="yellow",
            padding=(0, 1)
        ))

    @staticmethod
    def _scan_audio_files(folder: Path) -> List[str]:
        """Recursively scan folder for audio files"""
        audio_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aiff'}
        audio_files = []

        for file_path in folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                audio_files.append(str(file_path))

        # Sort by name for consistent ordering
        return sorted(audio_files)

    def _get_analysis_level(self) -> "AnalysisLevel":
        """Get current analysis level"""
        level_map = {
            'BASIC': AnalysisLevel.BASIC,
            'STANDARD': AnalysisLevel.STANDARD,
            'DETAILED': AnalysisLevel.DETAILED,
            'PROFESSIONAL': AnalysisLevel.PROFESSIONAL,
        }
        return level_map.get(self.analysis_level, AnalysisLevel.STANDARD)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def action_back(self) -> None:
        """Return to main screen with confirmation if processing"""
        if self.is_processing:
            confirm_dialog = ConfirmDialog(
                "Processing Active",
                "Batch processing is currently running.\n\n"
                "Going back will cancel the operation. Continue?"
            )

            def on_back_confirm(result: bool) -> None:
                """Handle confirmation dialog result"""
                if result:
                    self.cancel_requested = True
                    self.app.pop_screen()

            # Store the result handler
            original_pop = self.app.pop_screen

            def pop_with_handler() -> None:
                """Handle screen pop with confirmation result.
                
                Calls the confirmation callback with the dialog result
                before popping the screen.
                """
                if confirm_dialog.result:
                    on_back_confirm(True)
                original_pop()

            self.app.push_screen(confirm_dialog)
            self.app.pop_screen = pop_with_handler
        else:
            self.app.pop_screen()
