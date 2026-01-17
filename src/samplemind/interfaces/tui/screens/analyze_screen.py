"""
Analyze Screen for SampleMind TUI
Single file analysis with progress tracking and AudioEngine integration
"""

import asyncio
import os
from pathlib import Path

from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, ProgressBar
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from samplemind.interfaces.tui.audio_engine_bridge import get_tui_engine
from samplemind.core.engine.audio_engine import AnalysisLevel
from samplemind.utils.file_picker import CrossPlatformFilePicker
from samplemind.interfaces.tui.widgets.dialogs import (
    ErrorDialog,
    InfoDialog,
    LoadingDialog,
    WarningDialog,
)
from samplemind.interfaces.tui.screens.results_screen import ResultsScreen


class AnalyzeScreen(Screen):
    """Screen for analyzing single audio files with AudioEngine integration"""

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

    #level_selector {
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

    #progress_area {
        width: 1fr;
        height: 3;
        border: solid $success;
        padding: 1;
        margin-bottom: 1;
        display: none;
    }

    #progress_area.active {
        display: block;
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
    progress_value: reactive[float] = reactive(0.0)

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

            yield Static(
                self._render_level_selector(),
                id="level_selector"
            )

            with Horizontal(id="button_area"):
                yield Button("📁 Browse", id="browse_btn", variant="primary")
                yield Button("🎵 Analyze", id="analyze_btn", variant="success")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

            yield Static(
                self._render_progress(),
                id="progress_area"
            )

            yield Static(
                self._render_placeholder(),
                id="results_area"
            )

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title"""
        title = Text("🎯 Analyze Single Audio File", style="bold cyan")
        return Panel(title, border_style="green", padding=(0, 1))

    def _render_level_selector(self) -> Panel:
        """Render analysis level selector"""
        levels = "📊 Analysis Level: [B]ASIC (0.5s) | [S]TANDARD (1.5s) | [D]ETAILED (2.5s) | [P]ROFESSIONAL (3.5s)"
        text = Text(levels, style="dim yellow")
        return Panel(text, border_style="yellow", padding=(0, 1))

    def _render_progress(self) -> Panel:
        """Render progress panel"""
        progress_text = Text(
            "Analyzing audio file...",
            style="bold green"
        )
        return Panel(progress_text, border_style="green", padding=(0, 1))

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
        self.tui_engine = get_tui_engine()
        self.file_picker = CrossPlatformFilePicker()
        self.analysis_level = AnalysisLevel.STANDARD

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
        """Open cross-platform file browser with comprehensive error handling"""
        try:
            selected_file = self.file_picker.choose_file(
                file_types=[
                    ("Audio files", ["*.wav", "*.mp3", "*.flac", "*.m4a", "*.ogg", "*.aiff"]),
                    ("All files", ["*.*"])
                ],
                title="Select Audio File"
            )

            if selected_file:
                # Validate the selected file
                file_path = Path(selected_file)

                if not file_path.exists():
                    self.app.push_screen(
                        ErrorDialog(
                            "File Not Found",
                            f"The selected file no longer exists:\n\n{selected_file}\n\n"
                            "The file may have been moved or deleted."
                        )
                    )
                    return

                if not file_path.is_file():
                    self.app.push_screen(
                        ErrorDialog(
                            "Not a File",
                            f"The path is a directory, not a file:\n\n{selected_file}"
                        )
                    )
                    return

                if not os.access(selected_file, os.R_OK):
                    self.app.push_screen(
                        ErrorDialog(
                            "File Not Readable",
                            f"Permission denied reading file:\n\n{selected_file}\n\n"
                            "Please check file permissions."
                        )
                    )
                    return

                # Update input field
                file_input = self.query_one("#file_input", Input)
                file_input.value = selected_file

                # Show success notification with file info
                file_size = self._format_size(os.path.getsize(selected_file))
                self.notify(
                    f"✅ Selected: {os.path.basename(selected_file)} ({file_size})",
                    severity="information"
                )

        except PermissionError:
            self.app.push_screen(
                ErrorDialog(
                    "Permission Denied",
                    "You don't have permission to access the file picker.\n\n"
                    "Please check your system permissions."
                )
            )
        except Exception as e:
            error_msg = str(e)
            if "cancelled" in error_msg.lower() or "cancel" in error_msg.lower():
                # User cancelled file picker, don't show error
                return

            self.app.push_screen(
                ErrorDialog(
                    "File Selection Error",
                    f"Error selecting file:\n\n{error_msg}"
                )
            )

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    async def action_analyze_file(self) -> None:
        """Start file analysis with AudioEngine and comprehensive error handling"""
        file_input = self.query_one("#file_input", Input)
        file_path = file_input.value.strip()

        # Validate input
        if not file_path:
            self.app.push_screen(
                ErrorDialog(
                    "No File Selected",
                    "Please enter or select an audio file path to analyze."
                )
            )
            return

        file = Path(file_path)

        # Validate file exists
        if not file.exists():
            self.app.push_screen(
                ErrorDialog(
                    "File Not Found",
                    f"The file does not exist:\n\n{file_path}"
                )
            )
            return

        # Validate file is not a directory
        if file.is_dir():
            self.app.push_screen(
                ErrorDialog(
                    "Invalid File",
                    f"The path is a directory, not a file:\n\n{file_path}\n\n"
                    "Please select an audio file."
                )
            )
            return

        # Validate file extension
        valid_extensions = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff"}
        if file.suffix.lower() not in valid_extensions:
            self.app.push_screen(
                WarningDialog(
                    "Unsupported Audio Format",
                    f"File extension: {file.suffix}\n\n"
                    "Supported formats: WAV, MP3, FLAC, M4A, OGG, AIFF\n\n"
                    "Analysis may fail for unsupported formats."
                )
            )

        # Validate file is readable
        try:
            if not os.access(file_path, os.R_OK):
                self.app.push_screen(
                    ErrorDialog(
                        "File Not Readable",
                        f"Permission denied reading file:\n\n{file_path}\n\n"
                        "Please check file permissions."
                    )
                )
                return
        except Exception as e:
            self.app.push_screen(
                ErrorDialog(
                    "File Access Error",
                    f"Error checking file permissions:\n\n{str(e)}"
                )
            )
            return

        # Show progress area and disable buttons
        self.is_analyzing = True
        progress_area = self.query_one("#progress_area", Static)
        progress_area.remove_class("-hidden")

        buttons = self.query("Button")
        for btn in buttons:
            btn.disabled = True

        try:
            # Update progress area with loading indicator
            progress_area.update(Panel(
                Text("Analyzing audio file...", style="bold green"),
                border_style="green",
                padding=(0, 1)
            ))

            # Analyze with progress callback
            features = await self.tui_engine.analyze_file(
                file_path,
                self._handle_progress,
                self.analysis_level
            )

            # Display results in new screen
            self.app.push_screen(
                ResultsScreen(features, file_path)
            )

            # Show success notification
            self.notify(
                f"✅ Analysis complete: {file.name}",
                severity="information"
            )

        except FileNotFoundError as e:
            self.app.push_screen(
                ErrorDialog(
                    "File Not Found During Analysis",
                    f"The audio file was not found:\n\n{file_path}\n\n"
                    "The file may have been moved or deleted."
                )
            )
        except ValueError as e:
            error_msg = str(e)
            if "audio" in error_msg.lower() or "format" in error_msg.lower():
                self.app.push_screen(
                    ErrorDialog(
                        "Invalid Audio File",
                        f"The file is not a valid audio file:\n\n{error_msg}\n\n"
                        "Please check the file format."
                    )
                )
            else:
                self.app.push_screen(
                    ErrorDialog(
                        "Audio Analysis Error",
                        f"Error processing audio file:\n\n{error_msg}"
                    )
                )
        except Exception as e:
            error_msg = str(e)
            self.app.push_screen(
                ErrorDialog(
                    "Unexpected Error",
                    f"An unexpected error occurred during analysis:\n\n{error_msg}\n\n"
                    "Please check the file and try again."
                )
            )
        finally:
            # Hide progress area and re-enable buttons
            self.is_analyzing = False
            progress_area.add_class("-hidden")

            for btn in buttons:
                btn.disabled = False

    def _handle_progress(self, progress: float) -> None:
        """Handle progress updates from AudioEngine"""
        self.progress_value = progress
        progress_area = self.query_one("#progress_area", Static)
        progress_text = f"Analyzing... {progress * 100:.0f}%"
        progress_area.update(Panel(
            Text(progress_text, style="bold green"),
            border_style="green",
            padding=(0, 1)
        ))

    def _display_results(self, features) -> None:
        """Display analysis results in beautiful table format"""
        # Format features for display
        formatted = self.tui_engine.format_features_for_display(features)

        # Create results table
        table = Table(title=f"✓ Analysis: {os.path.basename(features.file_path)}")
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green")

        for key, value in formatted.items():
            table.add_row(key, str(value))

        # Update results area
        results_area = self.query_one("#results_area", Static)
        results_area.update(table)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts for analysis levels with enhanced feedback"""
        if self.is_analyzing:
            return

        level_info = {
            "b": (
                AnalysisLevel.BASIC,
                "Basic Analysis (Fastest)",
                "Fast analysis optimized for quick feedback.\n"
                "Suitable for quick previews and real-time performance.\n"
                "Est. time: ~0.5 seconds per file"
            ),
            "s": (
                AnalysisLevel.STANDARD,
                "Standard Analysis (Balanced)",
                "Balanced analysis with good detail and speed.\n"
                "Recommended for most use cases and batch processing.\n"
                "Est. time: ~1.5 seconds per file"
            ),
            "d": (
                AnalysisLevel.DETAILED,
                "Detailed Analysis (Thorough)",
                "Comprehensive analysis with maximum feature extraction.\n"
                "Includes harmonic/percussive separation and advanced features.\n"
                "Est. time: ~2.5 seconds per file"
            ),
            "p": (
                AnalysisLevel.PROFESSIONAL,
                "Professional Analysis (Comprehensive)",
                "Complete professional analysis with all available features.\n"
                "Maximum detail and accuracy for production-critical analysis.\n"
                "Est. time: ~3.5 seconds per file"
            )
        }

        if event.key in level_info:
            level, title, description = level_info[event.key]
            self.analysis_level = level

            self.app.push_screen(
                InfoDialog(title, description)
            )

    def action_back(self) -> None:
        """Return to main screen"""
        self.app.pop_screen()
