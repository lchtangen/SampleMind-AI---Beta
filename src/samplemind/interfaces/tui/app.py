"""
SampleMind AI TUI - Terminal User Interface

Modern, interactive terminal interface with:
- Sample browser with keyboard navigation
- Real-time analysis display
- Waveform visualization
- Progress tracking
- Keyboard shortcuts
"""

import asyncio
from pathlib import Path
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, DataTable, Button, Input,
    DirectoryTree, Label, ProgressBar, Placeholder
)
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import Screen
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Import SampleMind components
from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
from samplemind.core.processing.stem_separation import StemSeparationEngine, StemType
from samplemind.core.processing.audio_to_midi import AudioToMIDIConverter, MIDIConversionMode


class WaveformWidget(Static):
    """Display ASCII waveform visualization"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.waveform_data = None

    def set_waveform(self, audio_data):
        """Set waveform data and render"""
        self.waveform_data = audio_data
        self.update_waveform()

    def update_waveform(self):
        """Render ASCII waveform"""
        if self.waveform_data is None:
            self.update("No waveform data")
            return

        # Simple ASCII waveform (simplified version)
        width = 60
        height = 10

        # Sample the audio data
        import numpy as np
        if len(self.waveform_data) > width:
            indices = np.linspace(0, len(self.waveform_data)-1, width, dtype=int)
            samples = self.waveform_data[indices]
        else:
            samples = self.waveform_data

        # Normalize to height
        samples = np.interp(samples, (samples.min(), samples.max()), (0, height-1))

        # Build ASCII waveform
        lines = []
        for i in range(height):
            line = ""
            for sample in samples:
                if int(sample) == height - i - 1:
                    line += "█"
                else:
                    line += " "
            lines.append(line)

        waveform_text = "\n".join(lines)
        self.update(waveform_text)


class AnalysisPanel(Static):
    """Display analysis results"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analysis_result = None

    def set_analysis(self, result):
        """Set and display analysis results"""
        self.analysis_result = result
        self.update_analysis()

    def update_analysis(self):
        """Render analysis results"""
        if self.analysis_result is None:
            self.update("No analysis data")
            return

        # Create rich table
        table = Table(title="📊 Analysis Results", show_header=True)
        table.add_column("Feature", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Tempo", f"{self.analysis_result.tempo:.1f} BPM")
        table.add_row("Key", str(self.analysis_result.key))
        table.add_row("Energy", f"{self.analysis_result.energy:.2f}")

        if hasattr(self.analysis_result, 'mood') and self.analysis_result.mood:
            table.add_row("Mood", self.analysis_result.mood)

        self.update(table)


class SampleBrowserScreen(Screen):
    """Main screen for browsing and analyzing samples"""

    BINDINGS = [
        Binding("a", "analyze", "Analyze", key_display="A"),
        Binding("s", "stems", "Stems", key_display="S"),
        Binding("m", "midi", "MIDI", key_display="M"),
        Binding("q", "quit", "Quit", key_display="Q"),
    ]

    def __init__(self):
        super().__init__()
        self.audio_engine = AudioEngine()
        self.stem_engine = StemSeparationEngine()
        self.midi_converter = AudioToMIDIConverter()
        self.current_file: Optional[Path] = None

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()

        with Horizontal():
            # Left panel - File browser
            with Vertical(id="file-panel"):
                yield Label("📁 Sample Library")
                yield DataTable(id="file-table")

            # Right panel - Analysis and visualization
            with Vertical(id="info-panel"):
                yield Label("📊 Analysis")
                yield AnalysisPanel(id="analysis")
                yield Label("〰️ Waveform")
                yield WaveformWidget(id="waveform")
                yield Label("ℹ️ Info")
                yield Static(id="file-info")

        with Container(id="status-bar"):
            yield Static(id="status-text")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the screen"""
        # Setup file table
        table = self.query_one("#file-table", DataTable)
        table.add_columns("Filename", "Type", "Size")
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Load sample files
        await self.load_samples()

        # Update status
        status = self.query_one("#status-text", Static)
        status.update("Ready | Use arrow keys to navigate, 'A' to analyze")

    async def load_samples(self):
        """Load audio files from current directory"""
        table = self.query_one("#file-table", DataTable)

        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aiff', '.ogg']
        current_dir = Path.cwd()

        # Find audio files
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(current_dir.glob(f"*{ext}"))

        # Add to table
        for file in sorted(audio_files):
            size = file.stat().st_size
            size_mb = size / (1024 * 1024)
            table.add_row(
                file.name,
                file.suffix[1:].upper(),
                f"{size_mb:.2f} MB"
            )

    async def action_analyze(self) -> None:
        """Analyze selected file"""
        table = self.query_one("#file-table", DataTable)

        if table.row_count == 0:
            return

        # Get selected file
        row_index = table.cursor_row
        if row_index < 0:
            return

        filename = table.get_cell_at((row_index, 0))
        file_path = Path.cwd() / filename

        # Update status
        status = self.query_one("#status-text", Static)
        status.update(f"Analyzing {filename}...")

        try:
            # Analyze audio
            result = await self.audio_engine.analyze_audio_async(
                file_path,
                level=AnalysisLevel.DETAILED
            )

            # Update analysis panel
            analysis_panel = self.query_one("#analysis", AnalysisPanel)
            analysis_panel.set_analysis(result)

            # Load and display waveform
            audio_data, sr = self.audio_engine.load_audio(file_path)
            waveform = self.query_one("#waveform", WaveformWidget)
            waveform.set_waveform(audio_data[:sr*5])  # First 5 seconds

            # Update file info
            file_info = self.query_one("#file-info", Static)
            info_text = f"File: {filename}\n"
            info_text += f"Duration: {len(audio_data)/sr:.1f}s\n"
            info_text += f"Sample Rate: {sr} Hz"
            file_info.update(info_text)

            status.update(f"✅ Analyzed: {filename}")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    async def action_stems(self) -> None:
        """Separate stems from selected file"""
        table = self.query_one("#file-table", DataTable)

        if table.row_count == 0:
            return

        row_index = table.cursor_row
        if row_index < 0:
            return

        filename = table.get_cell_at((row_index, 0))
        file_path = Path.cwd() / filename

        status = self.query_one("#status-text", Static)
        status.update(f"Separating stems: {filename}...")

        try:
            result = await self.stem_engine.separate_stems(
                file_path,
                stems=[StemType.VOCALS, StemType.INSTRUMENTAL]
            )

            status.update(f"✅ Stems separated: {len(result)} stems")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    async def action_midi(self) -> None:
        """Convert selected file to MIDI"""
        table = self.query_one("#file-table", DataTable)

        if table.row_count == 0:
            return

        row_index = table.cursor_row
        if row_index < 0:
            return

        filename = table.get_cell_at((row_index, 0))
        file_path = Path.cwd() / filename

        status = self.query_one("#status-text", Static)
        status.update(f"Converting to MIDI: {filename}...")

        try:
            midi_path = await self.midi_converter.convert_to_midi(
                file_path,
                mode=MIDIConversionMode.AUTO
            )

            status.update(f"✅ MIDI created: {midi_path.name}")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    async def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()


class SampleMindTUI(App):
    """
    SampleMind AI Terminal User Interface

    Modern, interactive terminal interface for music production.
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #file-panel {
        width: 50%;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    #info-panel {
        width: 50%;
        height: 100%;
        border: solid $secondary;
        padding: 1;
    }

    #file-table {
        height: 100%;
    }

    #analysis {
        height: 12;
        border: solid $accent;
        padding: 1;
        margin: 1;
    }

    #waveform {
        height: 12;
        border: solid $warning;
        padding: 1;
        margin: 1;
    }

    #file-info {
        height: 8;
        border: solid $success;
        padding: 1;
        margin: 1;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
    }

    #status-text {
        text-style: bold;
        color: $text;
    }
    """

    TITLE = "🎵 SampleMind AI - Terminal UI"
    SUB_TITLE = "Professional Music Production Suite"

    def on_mount(self) -> None:
        """Called when app starts"""
        self.push_screen(SampleBrowserScreen())

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def main():
    """Run the TUI application"""
    app = SampleMindTUI()
    app.run()


if __name__ == "__main__":
    main()
