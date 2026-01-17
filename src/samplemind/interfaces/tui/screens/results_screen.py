"""
Results Display Screen for SampleMind TUI

Comprehensive, tabbed interface for viewing audio analysis results
with export, comparison, and favorites capabilities.
"""

import os
from datetime import datetime

from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Tabs, TabPane
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive

from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from samplemind.core.engine.audio_engine import AudioFeatures


class ResultsScreen(Screen):
    """Dedicated screen for viewing comprehensive audio analysis results"""

    DEFAULT_CSS = """
    ResultsScreen {
        layout: vertical;
    }

    #results_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #tabs {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }

    #content_area {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
        padding: 1;
        overflow: auto;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 1;
    }

    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("e", "export", "Export"),
        ("c", "compare", "Compare"),
        ("f", "favorite", "Favorite"),
    ]

    current_tab: reactive[str] = reactive("overview")

    def __init__(self, features: AudioFeatures, file_path: str = ""):
        """Initialize results screen with audio features."""
        super().__init__()
        self.features = features
        self.file_path = file_path or getattr(features, "file_path", "Unknown")
        self.is_favorite = False

    def compose(self):
        """Compose the results display layout"""
        yield Header(show_clock=True)

        with Vertical(id="results_container"):
            # Title with file info
            yield Static(
                self._render_title(),
                id="results_title"
            )

            # Tab navigation
            with Tabs(id="tabs"):
                yield TabPane("📊 Overview", self._render_overview(), id="overview_tab")
                yield TabPane("📈 Spectral", self._render_spectral(), id="spectral_tab")
                yield TabPane("⏱️ Temporal", self._render_temporal(), id="temporal_tab")
                yield TabPane("🎼 MFCC", self._render_mfcc(), id="mfcc_tab")
                yield TabPane("🔬 Advanced", self._render_advanced(), id="advanced_tab")

            # Display area for tab content
            yield Static(
                self._render_content("overview"),
                id="content_area"
            )

            # Action buttons
            with Horizontal(id="button_area"):
                yield Button("⬅️  Back", id="back_btn", variant="warning")
                yield Button("💾 Export", id="export_btn", variant="primary")
                yield Button("🔍 Compare", id="compare_btn", variant="primary")
                yield Button("⭐ Favorite", id="favorite_btn", variant="success")

        yield Footer()

    def _render_title(self) -> Panel:
        """Render title with file information"""
        file_name = os.path.basename(self.file_path)
        title_text = f"🎯 Analysis Results: {file_name}"
        analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subtitle = f"Analyzed: {analysis_time}"

        content = Text(f"{title_text}\n{subtitle}", style="bold cyan")
        return Panel(content, border_style="green", padding=(0, 1))

    def _render_overview(self) -> Container:
        """Render overview tab content"""
        table = Table(title="📊 Audio Properties & Analysis Summary")
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green")

        # Audio properties
        table.add_row("File", os.path.basename(self.file_path))
        table.add_row("Duration", f"{self.features.duration:.2f}s ({self._format_time(self.features.duration)})")
        table.add_row("Sample Rate", f"{self.features.sample_rate:,} Hz")
        table.add_row("Channels", f"{self.features.channels} ({'Stereo' if self.features.channels == 2 else 'Mono'})")
        table.add_row("Bit Depth", f"{self.features.bit_depth}-bit")

        table.add_row("", "")  # Separator
        table.add_row("", "[bold yellow]Musical Analysis[/bold yellow]")

        # Musical features
        table.add_row("Tempo", f"{self.features.tempo:.1f} BPM")
        table.add_row("Key", f"{self.features.key} {self.features.mode}")
        table.add_row("Time Signature", str(self.features.time_signature))
        table.add_row("Beats Detected", str(len(self.features.beats) if self.features.beats else 0))
        table.add_row("Onset Times", str(len(self.features.onset_times) if self.features.onset_times else 0))

        return Static(table)

    def _render_spectral(self) -> Container:
        """Render spectral analysis tab"""
        table = Table(title="📈 Spectral Features")
        table.add_column("Feature", style="cyan", width=25)
        table.add_column("Value", style="green")
        table.add_column("Description", style="dim", width=40)

        table.add_row(
            "Spectral Centroid",
            f"{self.features.spectral_centroid:.0f} Hz",
            "Center of mass of the spectrum"
        )

        table.add_row(
            "Spectral Bandwidth",
            f"{self.features.spectral_bandwidth:.0f} Hz",
            "Width of the spectrum around centroid"
        )

        table.add_row(
            "Spectral Rolloff",
            f"{self.features.spectral_rolloff:.0f} Hz",
            "Frequency below which 95% of energy exists"
        )

        table.add_row(
            "Zero Crossing Rate",
            f"{self.features.zero_crossing_rate:.4f}",
            "Rate of sign changes in audio signal"
        )

        table.add_row(
            "RMS Energy",
            f"{self.features.rms_energy:.4f}",
            "Root mean square energy (loudness)"
        )

        # Chroma features summary
        if self.features.chroma_features:
            chroma_len = len(self.features.chroma_features)
            table.add_row("Chroma Features", f"{chroma_len} bands", "12-note chroma distribution")

        return Static(table)

    def _render_temporal(self) -> Container:
        """Render temporal features tab"""
        table = Table(title="⏱️ Temporal Features")
        table.add_column("Feature", style="cyan", width=25)
        table.add_column("Value", style="green")

        table.add_row("Duration", f"{self.features.duration:.2f}s")
        table.add_row("Tempo", f"{self.features.tempo:.1f} BPM")
        table.add_row("Beats", str(len(self.features.beats) if self.features.beats else 0))

        if self.features.beats and len(self.features.beats) > 0:
            beat_times = [f"{b:.2f}s" for b in self.features.beats[:10]]
            table.add_row("First 10 Beats", ", ".join(beat_times))

        table.add_row("Onset Times", str(len(self.features.onset_times) if self.features.onset_times else 0))

        if self.features.rhythm_pattern:
            table.add_row("Rhythm Pattern", str(self.features.rhythm_pattern)[:50] + "...")

        table.add_row("Time Signature", str(self.features.time_signature))
        table.add_row("Analysis Level", getattr(self.features, "analysis_level", "STANDARD"))

        return Static(table)

    def _render_mfcc(self) -> Container:
        """Render MFCC features tab"""
        if not self.features.mfccs or len(self.features.mfccs) == 0:
            return Static(Panel(
                Text("No MFCC data available", style="dim yellow"),
                border_style="yellow"
            ))

        table = Table(title="🎼 MFCC (Mel-Frequency Cepstral Coefficients)")
        table.add_column("Coefficient", style="cyan", width=20)
        table.add_column("Value", style="green")
        table.add_column("Description", style="dim", width=45)

        descriptions = [
            "Energy representation",
            "1st cepstral coefficient",
            "2nd cepstral coefficient",
            "3rd cepstral coefficient",
            "4th cepstral coefficient",
            "5th cepstral coefficient",
            "6th cepstral coefficient",
            "7th cepstral coefficient",
            "8th cepstral coefficient",
            "9th cepstral coefficient",
            "10th cepstral coefficient",
            "11th cepstral coefficient",
            "12th cepstral coefficient",
        ]

        for i, (mfcc, desc) in enumerate(zip(self.features.mfccs[:13], descriptions)):
            coeff_name = f"MFCC {i}"
            table.add_row(coeff_name, f"{float(mfcc):.6f}", desc)

        return Static(table)

    def _render_advanced(self) -> Container:
        """Render advanced features tab"""
        table = Table(title="🔬 Advanced Audio Features")
        table.add_column("Feature", style="cyan", width=30)
        table.add_column("Value", style="green")

        # Harmonic/Percussive separation
        if self.features.harmonic_content:
            table.add_row("Harmonic Content", f"{self.features.harmonic_content:.4f}")

        if self.features.percussive_content:
            table.add_row("Percussive Content", f"{self.features.percussive_content:.4f}")

        # Pitch class distribution
        if self.features.pitch_class_distribution:
            pcd = self.features.pitch_class_distribution
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            max_pitch = max(pcd) if pcd else 0

            for i, (note, value) in enumerate(zip(notes, pcd)):
                bar_length = int((value / max_pitch * 20)) if max_pitch > 0 else 0
                bar = "█" * bar_length + "░" * (20 - bar_length)
                table.add_row(f"{note}", f"{value:.4f} {bar}")

        # File metadata
        table.add_row("", "")  # Separator
        table.add_row("File Path", self.file_path[:50] + ("..." if len(self.file_path) > 50 else ""))
        table.add_row("File Size", self._format_size(os.path.getsize(self.file_path)))
        table.add_row("Last Modified", datetime.fromtimestamp(os.path.getmtime(self.file_path)).strftime("%Y-%m-%d %H:%M:%S"))

        return Static(table)

    def _render_content(self, tab_name: str) -> Panel:
        """Render content for selected tab"""
        match tab_name:
            case "overview":
                return self._render_overview()
            case "spectral":
                return self._render_spectral()
            case "temporal":
                return self._render_temporal()
            case "mfcc":
                return self._render_mfcc()
            case "advanced":
                return self._render_advanced()
            case _:
                return self._render_overview()

    def on_mount(self) -> None:
        """Initialize the results screen"""
        self.title = f"SampleMind - Results: {os.path.basename(self.file_path)}"

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "export_btn":
            self.action_export()
        elif button_id == "compare_btn":
            self.action_compare()
        elif button_id == "favorite_btn":
            self.action_favorite()

    def action_export(self) -> None:
        """Export results to file"""
        self.notify("📤 Export functionality coming in Phase 2.5 (Feature 2)", severity="information")

    def action_compare(self) -> None:
        """Open comparison screen"""
        self.notify("🔍 Comparison functionality coming in Phase 2.5 (Feature 1)", severity="information")

    def action_favorite(self) -> None:
        """Toggle favorite status"""
        self.is_favorite = not self.is_favorite
        status = "⭐ Added to favorites" if self.is_favorite else "☆ Removed from favorites"
        self.notify(status, severity="information")

    def action_back(self) -> None:
        """Return to previous screen"""
        self.app.pop_screen()

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
