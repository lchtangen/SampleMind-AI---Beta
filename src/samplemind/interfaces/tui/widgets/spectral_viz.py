"""
Spectral Analysis Visualization Widget for SampleMind TUI
Chromagram, spectrogram, and mel-spectrogram displays
"""

import logging
from typing import Optional, List, Dict, Any
from enum import Enum
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

logger = logging.getLogger(__name__)


class SpectralType(Enum):
    """Types of spectral visualization"""
    CHROMAGRAM = "chromagram"
    SPECTROGRAM = "spectrogram"
    MEL_SPECTROGRAM = "mel_spectrogram"


# Unicode density characters for spectral displays
INTENSITY_CHARS = [
    " ",      # 0: empty
    "░",      # 1: light
    "▒",      # 2: medium-light
    "▓",      # 3: medium-dark
    "█",      # 4: dark
]

# Color mapping for intensity
INTENSITY_COLORS = {
    0: "dim black",
    1: "blue",
    2: "cyan",
    3: "green",
    4: "yellow",
}


class SpectralViz(Widget):
    """Widget for displaying spectral analysis visualization"""

    DEFAULT_CSS = """
    SpectralViz {
        width: 1fr;
        height: 15;
        border: solid $accent;
        background: $surface;
    }
    """

    # Reactive properties
    viz_type: reactive[SpectralType] = reactive(SpectralType.CHROMAGRAM)
    current_frame: reactive[int] = reactive(0)

    def __init__(
        self,
        name: Optional[str] = None,
        height: int = 15,
    ):
        """
        Initialize spectral visualization widget

        Args:
            name: Widget name
            height: Height of visualization in lines
        """
        super().__init__(name=name)
        self.height = height
        self.width_chars = 80  # Default, updated on mount

        # Spectral data
        self.chromagram: Optional[List[List[float]]] = None  # 12 bins (notes) x frames
        self.spectrogram: Optional[List[List[float]]] = None  # Freq bins x frames
        self.mel_spectrogram: Optional[List[List[float]]] = None  # Mel bins x frames

        # Note names for chromagram
        self.note_names = [
            "C ", "C♯", "D ", "D♯", "E ", "F ",
            "F♯", "G ", "G♯", "A ", "A♯", "B ",
        ]

        # Statistics
        self.viz_type = SpectralType.CHROMAGRAM
        self.current_frame = 0

    def _normalize_value(self, value: float, max_value: float = 1.0) -> int:
        """Normalize value to 0-4 range for intensity character"""
        if max_value == 0:
            return 0
        normalized = min(1.0, abs(value) / max_value)
        return int(normalized * 4)

    def _get_color_for_intensity(self, intensity: int) -> str:
        """Get color based on intensity (0-4)"""
        return INTENSITY_COLORS.get(intensity, "dim black")

    def _render_chromagram(self) -> Text:
        """Render chromagram visualization (12-tone pitch class)"""
        if not self.chromagram:
            return Text("No chromagram data", style="dim")

        # Get current frame
        if self.current_frame >= len(self.chromagram[0]):
            frame_idx = len(self.chromagram[0]) - 1
        else:
            frame_idx = self.current_frame

        frame_data = [self.chromagram[bin_idx][frame_idx] for bin_idx in range(12)]

        # Find max for normalization
        max_val = max(frame_data) if frame_data else 1.0

        # Build visualization
        viz_text = Text()
        viz_text.append("Chromagram (12-tone pitch):\n", style="bold cyan")

        for note_idx, (note_name, value) in enumerate(zip(self.note_names, frame_data)):
            intensity = self._normalize_value(value, max_val)
            color = self._get_color_for_intensity(intensity)

            # Note name
            viz_text.append(note_name, style="bold")
            viz_text.append(" │ ")

            # Intensity bar
            bar_width = 30
            bar_filled = int((intensity / 4.0) * bar_width)
            bar_text = "█" * bar_filled + "░" * (bar_width - bar_filled)
            viz_text.append(bar_text, style=color)

            # Value
            viz_text.append(f" {value:.2f}\n", style="dim")

        return viz_text

    def _render_spectrogram(self) -> Text:
        """Render spectrogram visualization (frequency vs time)"""
        if not self.spectrogram:
            return Text("No spectrogram data", style="dim")

        viz_text = Text()
        viz_text.append("Spectrogram (Frequency vs Time):\n", style="bold cyan")

        # Get portion of spectrogram to display
        # Show last N frames horizontally
        display_frames = min(self.width_chars, len(self.spectrogram[0]))
        display_freqs = min(self.height - 2, len(self.spectrogram))

        # Render from top to bottom (high freq to low freq)
        for freq_idx in range(display_freqs - 1, -1, -1):
            freq_label = f"{(freq_idx * 100 // display_freqs):>3}Hz "
            viz_text.append(freq_label, style="dim")

            # Get frame range
            start_frame = max(0, len(self.spectrogram[0]) - display_frames)
            for frame_idx in range(start_frame, len(self.spectrogram[0])):
                if frame_idx < len(self.spectrogram[freq_idx]):
                    value = self.spectrogram[freq_idx][frame_idx]
                    intensity = self._normalize_value(value, 1.0)
                    char = INTENSITY_CHARS[intensity]
                    color = self._get_color_for_intensity(intensity)
                    viz_text.append(char, style=color)

            viz_text.append("\n")

        return viz_text

    def _render_mel_spectrogram(self) -> Text:
        """Render mel-spectrogram visualization (perceptual frequency)"""
        if not self.mel_spectrogram:
            return Text("No mel-spectrogram data", style="dim")

        viz_text = Text()
        viz_text.append("Mel-Spectrogram (Perceptual Frequency):\n", style="bold cyan")

        # Get portion to display
        display_frames = min(self.width_chars, len(self.mel_spectrogram[0]))
        display_mels = min(self.height - 2, len(self.mel_spectrogram))

        # Render from top to bottom (high mel to low mel)
        for mel_idx in range(display_mels - 1, -1, -1):
            mel_label = f"Mel{mel_idx:>2} "
            viz_text.append(mel_label, style="dim")

            # Get frame range
            start_frame = max(0, len(self.mel_spectrogram[0]) - display_frames)
            for frame_idx in range(start_frame, len(self.mel_spectrogram[0])):
                if frame_idx < len(self.mel_spectrogram[mel_idx]):
                    value = self.mel_spectrogram[mel_idx][frame_idx]
                    intensity = self._normalize_value(value, 1.0)
                    char = INTENSITY_CHARS[intensity]
                    color = self._get_color_for_intensity(intensity)
                    viz_text.append(char, style=color)

            viz_text.append("\n")

        return viz_text

    def _render_analysis_summary(self) -> Text:
        """Render summary of spectral analysis"""
        summary = Text()
        summary.append("Spectral Analysis Summary:\n\n", style="bold cyan")

        if self.chromagram:
            summary.append(
                f"✓ Chromagram: {len(self.chromagram[0])} frames × 12 notes\n",
                style="green"
            )

        if self.spectrogram:
            summary.append(
                f"✓ Spectrogram: {len(self.spectrogram[0])} frames × "
                f"{len(self.spectrogram)} frequencies\n",
                style="green"
            )

        if self.mel_spectrogram:
            summary.append(
                f"✓ Mel-Spectrogram: {len(self.mel_spectrogram[0])} frames × "
                f"{len(self.mel_spectrogram)} mel bins\n",
                style="green"
            )

        if not any([self.chromagram, self.spectrogram, self.mel_spectrogram]):
            summary.append("No spectral data loaded\n", style="yellow")

        summary.append(
            f"\nCurrent Frame: {self.current_frame} / "
            f"{self._get_max_frames()}\n",
            style="dim"
        )

        return summary

    def render(self) -> Panel:
        """Render the spectral visualization widget"""
        # Select visualization based on type
        if self.viz_type == SpectralType.CHROMAGRAM:
            content = self._render_chromagram()
        elif self.viz_type == SpectralType.SPECTROGRAM:
            content = self._render_spectrogram()
        elif self.viz_type == SpectralType.MEL_SPECTROGRAM:
            content = self._render_mel_spectrogram()
        else:
            content = self._render_analysis_summary()

        # Title with type info
        title_text = (
            f"[bold]Spectral Analysis[/bold] | "
            f"Type: {self.viz_type.value.replace('_', ' ').title()}"
        )

        return Panel(
            content,
            title=title_text,
            border_style="cyan",
            padding=(0, 1),
        )

    def _get_max_frames(self) -> int:
        """Get maximum number of frames across all spectral types"""
        max_frames = 0
        if self.chromagram:
            max_frames = max(max_frames, len(self.chromagram[0]))
        if self.spectrogram:
            max_frames = max(max_frames, len(self.spectrogram[0]))
        if self.mel_spectrogram:
            max_frames = max(max_frames, len(self.mel_spectrogram[0]))
        return max_frames

    def update_chromagram(self, chromagram: List[List[float]]) -> None:
        """Update chromagram data (12 bins × frames)"""
        self.chromagram = chromagram
        self.current_frame = 0
        logger.debug(f"Updated chromagram: {len(chromagram[0])} frames")

    def update_spectrogram(self, spectrogram: List[List[float]]) -> None:
        """Update spectrogram data (freq bins × frames)"""
        self.spectrogram = spectrogram
        self.current_frame = 0
        logger.debug(f"Updated spectrogram: {len(spectrogram[0])} frames")

    def update_mel_spectrogram(self, mel_spectrogram: List[List[float]]) -> None:
        """Update mel-spectrogram data (mel bins × frames)"""
        self.mel_spectrogram = mel_spectrogram
        self.current_frame = 0
        logger.debug(f"Updated mel-spectrogram: {len(mel_spectrogram[0])} frames")

    def set_visualization_type(self, viz_type: SpectralType) -> None:
        """Change visualization type"""
        self.viz_type = viz_type
        logger.debug(f"Spectral viz type: {viz_type.value}")

    def next_frame(self) -> None:
        """Move to next frame"""
        max_frames = self._get_max_frames()
        if max_frames > 0:
            self.current_frame = min(self.current_frame + 1, max_frames - 1)

    def prev_frame(self) -> None:
        """Move to previous frame"""
        self.current_frame = max(0, self.current_frame - 1)

    def jump_to_frame(self, frame_num: int) -> None:
        """Jump to specific frame"""
        max_frames = self._get_max_frames()
        self.current_frame = max(0, min(frame_num, max_frames - 1))

    def get_stats(self) -> Dict[str, Any]:
        """Get spectral analysis statistics"""
        return {
            "has_chromagram": self.chromagram is not None,
            "has_spectrogram": self.spectrogram is not None,
            "has_mel_spectrogram": self.mel_spectrogram is not None,
            "current_frame": self.current_frame,
            "max_frames": self._get_max_frames(),
            "visualization_type": self.viz_type.value,
        }

    def print_info(self) -> str:
        """Print spectral analysis information"""
        stats = self.get_stats()
        lines = [
            "╔════════════════════════════════════════╗",
            "║    SPECTRAL ANALYSIS INFORMATION      ║",
            "╠════════════════════════════════════════╣",
            f"║ Chromagram: {'✓' if stats['has_chromagram'] else '✗':>30} ║",
            f"║ Spectrogram: {'✓' if stats['has_spectrogram'] else '✗':>29} ║",
            f"║ Mel-Spec: {'✓' if stats['has_mel_spectrogram'] else '✗':>32} ║",
            f"║ Frame: {stats['current_frame']}/{stats['max_frames']:>32} ║",
            f"║ Type: {stats['visualization_type']:>34} ║",
            "╚════════════════════════════════════════╝",
        ]
        return "\n".join(lines)
