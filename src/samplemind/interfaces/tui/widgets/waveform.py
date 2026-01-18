"""
Waveform Visualization Widget for SampleMind TUI
Real-time waveform rendering with zoom and playback position
"""

import logging
from typing import Optional, List, Tuple
from textual.widget import Widget
from textual.reactive import reactive
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

logger = logging.getLogger(__name__)

# Unicode block characters for waveform rendering
BLOCK_CHARS = [
    " ",      # 0: empty
    "▁",      # 1: 1/8
    "▂",      # 2: 2/8
    "▃",      # 3: 3/8
    "▄",      # 4: 4/8
    "▅",      # 5: 5/8
    "▆",      # 6: 6/8
    "▇",      # 7: 7/8
    "█",      # 8: full
]

# Color ranges for amplitude
COLORS = {
    "very_low": "dim blue",
    "low": "blue",
    "medium": "cyan",
    "high": "green",
    "very_high": "yellow",
    "critical": "red",
}


class WaveformWidget(Widget):
    """Widget for displaying audio waveform visualization"""

    DEFAULT_CSS = """
    WaveformWidget {
        width: 1fr;
        height: 10;
        border: solid $accent;
        background: $surface;
    }
    """

    # Reactive properties
    zoom_level: reactive[float] = reactive(1.0)
    playback_position: reactive[float] = reactive(0.0)
    peak_db: reactive[float] = reactive(-inf)

    def __init__(
        self,
        name: Optional[str] = None,
        audio_data: Optional[List[float]] = None,
        sample_rate: int = 44100,
        height: int = 10,
    ):
        """
        Initialize waveform widget

        Args:
            name: Widget name
            audio_data: Audio samples (mono or first channel of stereo)
            sample_rate: Sample rate in Hz
            height: Height of visualization in lines
        """
        super().__init__(name=name)
        self.audio_data = audio_data or []
        self.sample_rate = sample_rate
        self.height = height
        self.width_chars = 80  # Default, updated on mount

        # Zoom and scroll
        self.zoom_level = 1.0
        self.scroll_position = 0  # Position in samples

        # Playback
        self.playback_position = 0.0  # 0.0 to 1.0 (percentage)

        # Statistics
        self.rms_values: List[float] = []
        self.peak_values: List[float] = []
        self._calculate_statistics()

    def _calculate_statistics(self) -> None:
        """Calculate RMS and peak values from audio data"""
        if not self.audio_data:
            return

        # Calculate RMS values for each pixel (simplified)
        chunk_size = max(1, len(self.audio_data) // 100)  # 100 pixels
        self.rms_values = []
        self.peak_values = []

        for i in range(0, len(self.audio_data), chunk_size):
            chunk = self.audio_data[i : i + chunk_size]
            if not chunk:
                continue

            # Calculate RMS
            rms = (sum(s * s for s in chunk) / len(chunk)) ** 0.5
            self.rms_values.append(rms)

            # Calculate peak
            peak = max(abs(s) for s in chunk)
            self.peak_values.append(peak)

        # Update peak dB
        if self.peak_values:
            self.peak_db = 20 * (max(self.peak_values) ** 0.5)

    def _normalize_value(self, value: float, max_value: float = 1.0) -> int:
        """Normalize value to 0-8 range for block character selection"""
        if max_value == 0:
            return 0
        normalized = abs(value) / max_value
        # Clamp to 0-1 and convert to 0-8
        clamped = min(1.0, normalized)
        return int(clamped * 8)

    def _get_color_for_value(self, normalized: int) -> str:
        """Get color based on normalized value (0-8)"""
        if normalized <= 1:
            return COLORS["very_low"]
        elif normalized <= 2:
            return COLORS["low"]
        elif normalized <= 4:
            return COLORS["medium"]
        elif normalized <= 6:
            return COLORS["high"]
        elif normalized <= 7:
            return COLORS["very_high"]
        else:
            return COLORS["critical"]

    def _render_waveform_line(
        self, line_num: int, max_line: int = 5
    ) -> Text:
        """Render a single line of the waveform"""
        if not self.rms_values:
            return Text("No audio data", style="dim")

        # Calculate visible samples based on zoom
        samples_per_pixel = max(1, int(100 / self.zoom_level))
        visible_samples = self.width_chars * samples_per_pixel

        # Get portion of audio to display
        start_idx = int(self.scroll_position)
        end_idx = min(
            start_idx + visible_samples, len(self.rms_values)
        )

        waveform_text = Text()

        # Render each pixel
        for i in range(start_idx, end_idx):
            if i >= len(self.rms_values):
                break

            # Get value for this pixel
            value = self.rms_values[i]

            # Calculate which "line" this belongs to (top to bottom)
            # Normalize to height (max_line = center)
            normalized = self._normalize_value(value)

            # Determine if this line should show content
            if line_num == max_line:
                # Center line (always show)
                char = BLOCK_CHARS[normalized]
            elif line_num < max_line:
                # Above center (show if value extends)
                threshold = int((max_line - line_num) * 8 / max_line)
                char = BLOCK_CHARS[normalized] if normalized >= threshold else " "
            else:
                # Below center (mirror)
                threshold = int((line_num - max_line) * 8 / max_line)
                char = BLOCK_CHARS[normalized] if normalized >= threshold else " "

            # Get color for this value
            color = self._get_color_for_value(normalized)
            waveform_text.append(char, style=color)

        return waveform_text

    def _render_playback_indicator(self) -> Text:
        """Render playback position indicator"""
        if not self.rms_values:
            return Text("")

        # Calculate position based on playback_position (0.0-1.0)
        position = int(self.playback_position * self.width_chars)
        position = min(position, self.width_chars - 1)

        # Create indicator line
        indicator = Text()
        for i in range(self.width_chars):
            if i == position:
                indicator.append("▼", style="bold yellow")
            else:
                indicator.append("─", style="dim")

        return indicator

    def render(self) -> Panel:
        """Render the waveform widget"""
        if not self.audio_data:
            content = Text(
                "No audio data loaded\n\nLoad an audio file to view waveform",
                style="dim yellow",
            )
            return Panel(
                Align.center(content),
                title="[bold]Waveform[/bold]",
                border_style="cyan",
            )

        # Create waveform display
        waveform_lines = []
        max_line = self.height // 2

        # Render waveform lines
        for line_num in range(self.height):
            line_text = self._render_waveform_line(line_num, max_line)
            waveform_lines.append(line_text)

        # Add playback indicator at the end
        playback_line = self._render_playback_indicator()
        waveform_lines.append(playback_line)

        # Combine all lines
        content = Text("\n").join(waveform_lines)

        # Title with stats
        title_text = (
            f"[bold]Waveform[/bold] | "
            f"Zoom: {self.zoom_level:.1f}x | "
            f"Peak: {self.peak_db:.1f}dB | "
            f"Playback: {self.playback_position*100:.0f}%"
        )

        return Panel(
            content,
            title=title_text,
            border_style="cyan",
            padding=(0, 1),
        )

    def update_audio(self, audio_data: List[float], sample_rate: int = 44100) -> None:
        """Update audio data for visualization"""
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self._calculate_statistics()
        self.scroll_position = 0
        self.zoom_level = 1.0
        self.playback_position = 0.0

    def set_playback_position(self, position: float) -> None:
        """Set playback position (0.0 to 1.0)"""
        self.playback_position = max(0.0, min(1.0, position))

    def zoom_in(self) -> None:
        """Zoom in on waveform"""
        self.zoom_level = min(10.0, self.zoom_level * 1.5)
        logger.debug(f"Waveform zoom: {self.zoom_level:.1f}x")

    def zoom_out(self) -> None:
        """Zoom out on waveform"""
        self.zoom_level = max(1.0, self.zoom_level / 1.5)
        logger.debug(f"Waveform zoom: {self.zoom_level:.1f}x")

    def reset_zoom(self) -> None:
        """Reset zoom to 1.0x"""
        self.zoom_level = 1.0
        self.scroll_position = 0
        logger.debug("Waveform zoom reset")

    def scroll_left(self, amount: int = 10) -> None:
        """Scroll waveform to the left"""
        self.scroll_position = max(0, self.scroll_position - amount)

    def scroll_right(self, amount: int = 10) -> None:
        """Scroll waveform to the right"""
        max_scroll = max(0, len(self.rms_values) - self.width_chars)
        self.scroll_position = min(max_scroll, self.scroll_position + amount)

    def get_stats(self) -> dict:
        """Get waveform statistics"""
        if not self.audio_data:
            return {}

        return {
            "samples": len(self.audio_data),
            "duration_sec": len(self.audio_data) / self.sample_rate,
            "peak_db": self.peak_db,
            "rms_values_count": len(self.rms_values),
            "zoom_level": self.zoom_level,
            "playback_position": self.playback_position,
        }

    def print_info(self) -> str:
        """Print waveform information"""
        stats = self.get_stats()
        lines = [
            "╔════════════════════════════════════════╗",
            "║       WAVEFORM INFORMATION            ║",
            "╠════════════════════════════════════════╣",
            f"║ Samples: {stats.get('samples', 0):>30} ║",
            f"║ Duration: {stats.get('duration_sec', 0):>28.2f}s ║",
            f"║ Peak: {stats.get('peak_db', 0):>33.1f}dB ║",
            f"║ Zoom: {stats.get('zoom_level', 1.0):>33.1f}x ║",
            f"║ Playback: {stats.get('playback_position', 0)*100:>28.0f}% ║",
            "╚════════════════════════════════════════╝",
        ]
        return "\n".join(lines)
