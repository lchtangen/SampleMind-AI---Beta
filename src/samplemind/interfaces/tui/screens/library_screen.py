"""
Audio Library Browser Screen for SampleMind TUI
Directory navigation, file browsing, duplicate detection
"""

import logging
from typing import Optional, List

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DataTable, Input, Static, Button
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive

from samplemind.interfaces.tui.library import get_library_browser, SortOption

logger = logging.getLogger(__name__)


class LibraryStatsWidget(Static):
    """Widget displaying library statistics"""

    def __init__(self) -> None:
        super().__init__()
        self.browser = get_library_browser()

    def render(self) -> str:
        """Render library statistics"""
        stats = self.browser.get_statistics()

        lines = [
            "╔═════════════════════════════════════════════════════════╗",
            "║           📚 AUDIO LIBRARY STATISTICS                  ║",
            "╠═════════════════════════════════════════════════════════╣",
            f"║ Total Files:        {stats.total_files:<48} ║",
            f"║ Total Size:         {stats.format_total_size():<48} ║",
            f"║ Total Duration:     {stats.format_total_duration():<48} ║",
            f"║ Average File Size:  {stats.average_file_size / 1024 / 1024:>6.1f} MB                                  ║",
            f"║ Average Duration:   {stats.average_duration / 60:>6.1f} minutes                              ║",
            "╠═════════════════════════════════════════════════════════╣",
            "║ Format Distribution:                                    ║",
        ]

        for format_type, count in sorted(stats.file_formats.items()):
            lines.append(f"║   .{format_type:<7} {count:>4} files " + " " * 35 + "║")

        lines.extend([
            "╠═════════════════════════════════════════════════════════╣",
            "║ Duplicate Detection:                                    ║",
            f"║   Groups:           {stats.duplicate_groups:<48} ║",
            f"║   Duplicate Files:  {stats.duplicate_files:<48} ║",
            "╠═════════════════════════════════════════════════════════╣",
            "║ [D] Detect Duplicates | [E] Export | [R] Refresh       ║",
            "╚═════════════════════════════════════════════════════════╝",
        ])

        return "\n".join(lines)


class LibraryFileTableWidget(Static):
    """Widget displaying files in table format"""

    def __init__(self) -> None:
        super().__init__()
        self.browser = get_library_browser()
        self.table = DataTable(id="library-table")

    def compose(self) -> ComposeResult:
        """Compose the widget"""
        yield self.table

    def on_mount(self) -> None:
        """Set up table"""
        self.table.add_columns("Name", "Size", "Format", "Modified", "Duration")

        # Add sample files
        for file_info in self.browser.files[:50]:
            self.table.add_row(
                file_info.name,
                file_info.format_size(),
                file_info.format,
                "N/A",
                file_info.format_duration(),
            )


class LibraryScreen(Screen):
    """Audio library browser screen"""

    BINDINGS = [
        ("s", "sort_by_name", "Sort"),
        ("f", "filter_files", "Filter"),
        ("d", "detect_duplicates", "Duplicates"),
        ("r", "refresh", "Refresh"),
        ("e", "export_report", "Export"),
        ("q", "back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.browser = get_library_browser()
        self.search_query = ""

    def compose(self) -> ComposeResult:
        """Compose the screen"""
        yield Header(show_clock=True)

        with Container(id="library-main"):
            with Vertical():
                # Search bar
                yield Input(
                    placeholder="Search audio files... (name, format, size)",
                    id="library-search",
                )

                # Statistics widget
                yield LibraryStatsWidget(id="library-stats")

                # File list
                yield LibraryFileTableWidget(id="library-table-widget")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize screen"""
        # Scan default directory
        self.browser.scan_directory()

        # Update stats
        stats_widget = self.query_one("#library-stats", LibraryStatsWidget)
        stats_widget.update(stats_widget.render())

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input change"""
        self.search_query = event.value
        self._update_file_list()

    def _update_file_list(self) -> None:
        """Update file list based on search/filter"""
        table_widget = self.query_one("#library-table-widget", LibraryFileTableWidget)
        table = table_widget.table

        # Clear existing rows
        table.clear()

        # Search if query provided
        if self.search_query:
            files = self.browser.search_files(self.search_query)
        else:
            files = self.browser.files

        # Add rows
        for file_info in files[:100]:  # Limit to 100 for performance
            table.add_row(
                file_info.name,
                file_info.format_size(),
                file_info.format,
                "N/A",
                file_info.format_duration(),
            )

    def action_sort_by_name(self) -> None:
        """Sort by name"""
        current = self.browser.sort_option
        if current == SortOption.NAME_ASC:
            self.browser.sort_files(SortOption.NAME_DESC)
        else:
            self.browser.sort_files(SortOption.NAME_ASC)
        self._update_file_list()

    def action_filter_files(self) -> None:
        """Filter files"""
        logger.info("Filter action - implement filter dialog")

    def action_detect_duplicates(self) -> None:
        """Detect and display duplicates"""
        duplicates = self.browser.detect_duplicates()
        report = self.browser.get_duplicate_report()
        logger.info(f"Duplicate detection complete:\n{report}")

    def action_refresh(self) -> None:
        """Refresh library scan"""
        self.browser.scan_directory()
        self._update_file_list()

        # Update stats
        stats_widget = self.query_one("#library-stats", LibraryStatsWidget)
        stats_widget.update(stats_widget.render())

    def action_export_report(self) -> None:
        """Export library report"""
        library_report = self.browser.get_library_report()
        duplicate_report = self.browser.get_duplicate_report()

        full_report = f"{library_report}\n\n{duplicate_report}"
        logger.info(f"Library Report:\n{full_report}")

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()
