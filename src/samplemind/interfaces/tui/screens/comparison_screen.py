"""
Audio Comparison Screen for SampleMind TUI
Side-by-side comparison of multiple audio analyses
"""

import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, DataTable
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Console

from samplemind.core.engine.audio_engine import AudioFeatures
from samplemind.interfaces.tui.widgets.dialogs import ErrorDialog, InfoDialog


@dataclass
class ComparisonResult:
    """Result of comparing two analyses"""
    property_name: str
    value_1: Any
    value_2: Any
    difference: Optional[float] = None
    percentage_diff: Optional[float] = None
    match: bool = False
    similar: bool = False  # Within 5% for numeric values


class ComparisonEngine:
    """Engine for comparing audio analyses"""

    def __init__(self):
        """Initialize comparison engine"""
        self.comparisons: List[ComparisonResult] = []

    def calculate_similarity(
        self, features1: AudioFeatures, features2: AudioFeatures
    ) -> float:
        """
        Calculate similarity score between two analyses (0-100%)

        Args:
            features1: First audio features
            features2: Second audio features

        Returns:
            Similarity percentage (0-100)
        """
        if not features1 or not features2:
            return 0.0

        # Properties to compare
        properties = [
            "tempo",
            "key",
            "mode",
            "time_signature",
            "spectral_centroid",
            "spectral_bandwidth",
            "zero_crossing_rate",
            "rms_energy",
        ]

        matches = 0
        compared = 0

        for prop in properties:
            val1 = getattr(features1, prop, None)
            val2 = getattr(features2, prop, None)

            if val1 is None or val2 is None:
                continue

            compared += 1

            if isinstance(val1, str):
                # Exact match for strings
                if val1 == val2:
                    matches += 1
            elif isinstance(val1, (int, float)):
                # Within 5% for numeric values
                if val1 == 0 and val2 == 0:
                    matches += 1
                elif val1 != 0:
                    percent_diff = abs((val2 - val1) / val1) * 100
                    if percent_diff <= 5:
                        matches += 1

        if compared == 0:
            return 0.0

        return (matches / compared) * 100

    def compare_features(
        self, features1: AudioFeatures, features2: AudioFeatures
    ) -> List[ComparisonResult]:
        """
        Compare two feature sets and return detailed comparison

        Args:
            features1: First audio features
            features2: Second audio features

        Returns:
            List of comparison results
        """
        self.comparisons = []

        # Basic properties
        basic_props = [
            ("Tempo (BPM)", "tempo"),
            ("Key", "key"),
            ("Mode", "mode"),
            ("Duration (s)", "duration"),
            ("Sample Rate (Hz)", "sample_rate"),
            ("Channels", "channels"),
            ("Bit Depth", "bit_depth"),
        ]

        # Spectral properties
        spectral_props = [
            ("Spectral Centroid (Hz)", "spectral_centroid"),
            ("Spectral Bandwidth (Hz)", "spectral_bandwidth"),
            ("Spectral Rolloff (Hz)", "spectral_rolloff"),
            ("Zero Crossing Rate", "zero_crossing_rate"),
            ("RMS Energy", "rms_energy"),
        ]

        # Process basic properties
        for display_name, prop in basic_props:
            val1 = getattr(features1, prop, None)
            val2 = getattr(features2, prop, None)

            if val1 is not None and val2 is not None:
                result = self._create_comparison(display_name, val1, val2)
                self.comparisons.append(result)

        # Process spectral properties
        for display_name, prop in spectral_props:
            val1 = getattr(features1, prop, None)
            val2 = getattr(features2, prop, None)

            if val1 is not None and val2 is not None:
                result = self._create_comparison(display_name, val1, val2)
                self.comparisons.append(result)

        return self.comparisons

    def _create_comparison(
        self, name: str, val1: Any, val2: Any
    ) -> ComparisonResult:
        """Create a comparison result for two values"""
        match = val1 == val2
        similar = False
        difference = None
        percentage_diff = None

        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            difference = val2 - val1
            if val1 != 0:
                percentage_diff = (difference / val1) * 100
                similar = abs(percentage_diff) <= 5

        return ComparisonResult(
            property_name=name,
            value_1=val1,
            value_2=val2,
            difference=difference,
            percentage_diff=percentage_diff,
            match=match,
            similar=similar,
        )

    def get_comparison_summary(self) -> Dict[str, Any]:
        """Get summary statistics of comparison"""
        if not self.comparisons:
            return {}

        numeric_comps = [
            c for c in self.comparisons if c.difference is not None
        ]
        string_comps = [c for c in self.comparisons if c.difference is None]

        matches = sum(1 for c in self.comparisons if c.match)
        similar = sum(1 for c in numeric_comps if c.similar)

        avg_percent_diff = 0.0
        if numeric_comps:
            avg_percent_diff = sum(
                abs(c.percentage_diff) for c in numeric_comps if c.percentage_diff
            ) / len(numeric_comps)

        return {
            "total_properties": len(self.comparisons),
            "exact_matches": matches,
            "similar_values": similar,
            "string_properties": len(string_comps),
            "numeric_properties": len(numeric_comps),
            "average_percent_difference": round(avg_percent_diff, 2),
        }


class ComparisonScreen(Screen):
    """Screen for comparing multiple audio analyses"""

    DEFAULT_CSS = """
    ComparisonScreen {
        layout: vertical;
    }

    #comparison_container {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
    }

    #comparison_table {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
        margin-bottom: 1;
    }

    #stats_area {
        width: 1fr;
        height: auto;
        border: solid $success;
        padding: 1;
        margin-bottom: 1;
    }

    #button_area {
        width: 1fr;
        height: auto;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("e", "export_comparison", "Export"),
        ("r", "refresh", "Refresh"),
    ]

    is_loading: reactive[bool] = reactive(False)

    def __init__(
        self,
        features_list: List[tuple],  # List of (name, AudioFeatures) tuples
    ):
        """
        Initialize comparison screen

        Args:
            features_list: List of (file_name, AudioFeatures) tuples to compare
        """
        super().__init__()
        self.features_list = features_list
        self.comparison_engine = ComparisonEngine()
        self.comparison_results: List[ComparisonResult] = []

    def compose(self):
        """Compose the comparison screen layout"""
        yield Header(show_clock=True)

        with Vertical(id="comparison_container"):
            yield Static(self._render_title(), id="comparison_title")

            yield Static("Loading comparison...", id="stats_area")

            # Comparison table
            table = DataTable(id="comparison_table")
            table.add_columns("Property", "File 1", "File 2", "Difference", "Status")
            yield table

            # Button area
            with Horizontal(id="button_area"):
                yield Button("📤 Export", id="export_btn", variant="success")
                yield Button("🔄 Refresh", id="refresh_btn", variant="primary")
                yield Button("⬅️  Back", id="back_btn", variant="warning")

        yield Footer()

    def _render_title(self) -> Panel:
        """Render screen title with file names"""
        file_names = [name for name, _ in self.features_list]
        title = f"🔍 Comparison: {' vs '.join(file_names)}"
        subtitle = f"Comparing {len(self.features_list)} audio files"

        content = Text(f"{title}\n{subtitle}", style="bold cyan")
        return Panel(content, border_style="green", padding=(0, 1))

    def on_mount(self) -> None:
        """Initialize the comparison screen"""
        self.title = "SampleMind - Audio Comparison"
        asyncio.create_task(self._load_comparison())

    async def _load_comparison(self) -> None:
        """Load and display comparison"""
        try:
            self.is_loading = True

            if len(self.features_list) < 2:
                self.app.push_screen(
                    ErrorDialog("Error", "At least 2 files are required for comparison")
                )
                return

            # Compare all against the first one
            features1_name, features1 = self.features_list[0]
            features2_name, features2 = self.features_list[1]

            # Calculate comparison
            self.comparison_results = self.comparison_engine.compare_features(
                features1, features2
            )

            # Get summary
            summary = self.comparison_engine.get_comparison_summary()

            # Update stats
            stats_text = (
                f"Similarity: {self.comparison_engine.calculate_similarity(features1, features2):.1f}% | "
                f"Exact Matches: {summary.get('exact_matches', 0)} | "
                f"Similar: {summary.get('similar_values', 0)} | "
                f"Avg Diff: {summary.get('average_percent_difference', 0):.1f}%"
            )
            stats_area = self.query_one("#stats_area")
            stats_area.update(Panel(stats_text, border_style="blue", padding=(0, 1)))

            # Populate table
            table = self.query_one("#comparison_table", DataTable)

            for result in self.comparison_results:
                status = "✓" if result.match else ("~" if result.similar else "✗")
                status_style = (
                    "green" if result.match else "yellow" if result.similar else "red"
                )

                # Format values
                val1_str = self._format_value(result.value_1)
                val2_str = self._format_value(result.value_2)
                diff_str = self._format_difference(
                    result.difference, result.percentage_diff
                )

                table.add_row(
                    result.property_name,
                    val1_str,
                    val2_str,
                    diff_str,
                    Text(status, style=f"bold {status_style}"),
                )

            self.notify(
                f"✅ Compared {len(self.comparison_results)} properties",
                severity="information",
            )

        except Exception as e:
            self.app.push_screen(
                ErrorDialog("Error", f"Failed to load comparison: {e}")
            )
        finally:
            self.is_loading = False

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for display"""
        if isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, list):
            return f"[{len(value)} items]"
        else:
            return str(value)

    @staticmethod
    def _format_difference(
        difference: Optional[float], percentage: Optional[float]
    ) -> str:
        """Format difference for display"""
        if difference is None:
            return "-"
        if percentage is None:
            return f"{difference:+.2f}"
        return f"{difference:+.2f} ({percentage:+.1f}%)"

    def on_button_pressed(self, event) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "back_btn":
            self.action_back()
        elif button_id == "export_btn":
            asyncio.create_task(self._export_comparison())
        elif button_id == "refresh_btn":
            asyncio.create_task(self._load_comparison())

    async def _export_comparison(self) -> None:
        """Export comparison to file"""
        try:
            self.notify("📤 Export functionality coming soon!", severity="information")
        except Exception as e:
            self.app.push_screen(ErrorDialog("Error", f"Failed to export: {e}"))

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()

    def action_export_comparison(self) -> None:
        """Keyboard shortcut to export"""
        asyncio.create_task(self._export_comparison())

    def action_refresh(self) -> None:
        """Keyboard shortcut to refresh"""
        asyncio.create_task(self._load_comparison())
