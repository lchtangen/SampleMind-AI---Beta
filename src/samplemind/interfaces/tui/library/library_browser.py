"""
Audio Library Browser System for SampleMind TUI
Directory navigation, file browsing, duplicate detection
"""

import logging
import os
import hashlib
from typing import Optional, List, Dict, Set, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class SortOption(Enum):
    """Library sorting options"""
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    SIZE_ASC = "size_asc"
    SIZE_DESC = "size_desc"
    MODIFIED_ASC = "modified_asc"
    MODIFIED_DESC = "modified_desc"
    DURATION_ASC = "duration_asc"
    DURATION_DESC = "duration_desc"


@dataclass
class AudioFileInfo:
    """Information about an audio file"""
    path: str
    name: str
    size: int  # bytes
    modified_time: float
    duration: Optional[float] = None  # seconds
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: str = "wav"
    is_selected: bool = False
    file_hash: Optional[str] = None  # SHA-256 hash for duplicate detection

    def format_size(self) -> str:
        """Format file size nicely"""
        for unit in ["B", "KB", "MB", "GB"]:
            if self.size < 1024:
                return f"{self.size:.1f}{unit}"
            self.size /= 1024
        return f"{self.size:.1f}TB"

    def format_duration(self) -> str:
        """Format duration nicely"""
        if not self.duration:
            return "N/A"
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes}:{seconds:02d}"


@dataclass
class LibraryStats:
    """Library statistics"""
    total_files: int = 0
    total_size: int = 0  # bytes
    total_duration: float = 0.0  # seconds
    file_formats: Dict[str, int] = None  # format -> count
    duplicate_groups: int = 0
    duplicate_files: int = 0
    average_file_size: float = 0.0
    average_duration: float = 0.0

    def __post_init__(self) -> None:
        if self.file_formats is None:
            self.file_formats = defaultdict(int)

    def format_total_size(self) -> str:
        """Format total size nicely"""
        size = self.total_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def format_total_duration(self) -> str:
        """Format total duration nicely"""
        hours = int(self.total_duration // 3600)
        minutes = int((self.total_duration % 3600) // 60)
        seconds = int(self.total_duration % 60)
        return f"{hours}h {minutes}m {seconds}s"


class LibraryBrowser:
    """Audio file library browser and analyzer"""

    AUDIO_FORMATS = {".wav", ".mp3", ".flac", ".ogg", ".aac", ".m4a", ".aiff", ".wv"}
    DUPLICATE_CHECK_SIZE = 8192  # Read first 8KB for fast checking

    def __init__(self, root_path: Optional[str] = None) -> None:
        """
        Initialize library browser

        Args:
            root_path: Root directory to browse (defaults to user's music folder)
        """
        if root_path is None:
            # Use default music directory
            home = Path.home()
            root_path = str(home / "Music")

        self.root_path = Path(root_path)
        self.current_path = self.root_path
        self.files: List[AudioFileInfo] = []
        self.all_files: Dict[str, AudioFileInfo] = {}
        self.sort_option = SortOption.NAME_ASC
        self.filter_format: Optional[str] = None
        self.file_hashes: Dict[str, List[str]] = defaultdict(list)  # hash -> [paths]
        self.duplicates: List[List[AudioFileInfo]] = []

    def scan_directory(self, path: Optional[str] = None, recursive: bool = True) -> List[AudioFileInfo]:
        """
        Scan directory for audio files

        Args:
            path: Directory to scan (defaults to current path)
            recursive: Recursively scan subdirectories

        Returns:
            List of AudioFileInfo objects
        """
        if path:
            self.current_path = Path(path)
        else:
            path = str(self.current_path)

        self.files.clear()
        self.all_files.clear()

        try:
            scan_path = Path(path)
            if not scan_path.exists():
                logger.warning(f"Path does not exist: {path}")
                return []

            # Find all audio files
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"

            for file_path in scan_path.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in self.AUDIO_FORMATS:
                    info = self._create_file_info(file_path)
                    if info:
                        self.files.append(info)
                        self.all_files[str(file_path)] = info

            # Apply sort
            self._apply_sort()
            logger.info(f"Scanned {len(self.files)} audio files in {path}")

        except Exception as e:
            logger.error(f"Error scanning directory: {e}")

        return self.files

    def _create_file_info(self, file_path: Path) -> Optional[AudioFileInfo]:
        """Create AudioFileInfo from file path"""
        try:
            stat = file_path.stat()
            info = AudioFileInfo(
                path=str(file_path),
                name=file_path.name,
                size=stat.st_size,
                modified_time=stat.st_mtime,
                format=file_path.suffix.lower()[1:],  # Remove leading dot
            )
            return info
        except Exception as e:
            logger.error(f"Error creating file info for {file_path}: {e}")
            return None

    def detect_duplicates(self) -> List[List[AudioFileInfo]]:
        """
        Detect duplicate files by content hash

        Returns:
            List of duplicate groups
        """
        self.file_hashes.clear()
        self.duplicates.clear()

        for file_info in self.files:
            try:
                file_hash = self._calculate_file_hash(file_info.path)
                file_info.file_hash = file_hash
                self.file_hashes[file_hash].append(file_info.path)
            except Exception as e:
                logger.error(f"Error hashing {file_info.path}: {e}")

        # Find duplicates (files with same hash)
        for file_hash, file_paths in self.file_hashes.items():
            if len(file_paths) > 1:
                duplicate_group = [self.all_files[path] for path in file_paths]
                self.duplicates.append(duplicate_group)

        logger.info(f"Found {len(self.duplicates)} duplicate groups")
        return self.duplicates

    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of file

        Args:
            file_path: Path to file

        Returns:
            Hex hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def get_statistics(self) -> LibraryStats:
        """
        Calculate library statistics

        Returns:
            LibraryStats object
        """
        stats = LibraryStats()
        stats.total_files = len(self.files)

        format_counts: Dict[str, int] = defaultdict(int)
        total_size = 0
        total_duration = 0.0
        files_with_duration = 0

        for file_info in self.files:
            total_size += file_info.size
            format_counts[file_info.format] += 1

            if file_info.duration:
                total_duration += file_info.duration
                files_with_duration += 1

        stats.total_size = total_size
        stats.total_duration = total_duration
        stats.file_formats = dict(format_counts)
        stats.duplicate_groups = len(self.duplicates)
        stats.duplicate_files = sum(len(group) - 1 for group in self.duplicates)
        stats.average_file_size = total_size / stats.total_files if stats.total_files > 0 else 0
        stats.average_duration = total_duration / files_with_duration if files_with_duration > 0 else 0

        return stats

    def filter_by_format(self, format_str: str) -> List[AudioFileInfo]:
        """
        Filter files by format

        Args:
            format_str: Format (e.g., 'wav', 'mp3')

        Returns:
            Filtered list
        """
        self.filter_format = format_str.lower()
        filtered = [f for f in self.files if f.format == self.filter_format]
        return filtered

    def filter_by_size(self, min_size: int = 0, max_size: int = int(1e9)) -> List[AudioFileInfo]:
        """
        Filter files by size

        Args:
            min_size: Minimum size in bytes
            max_size: Maximum size in bytes

        Returns:
            Filtered list
        """
        return [f for f in self.files if min_size <= f.size <= max_size]

    def filter_by_duration(self, min_duration: float = 0, max_duration: float = float("inf")) -> List[AudioFileInfo]:
        """
        Filter files by duration

        Args:
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds

        Returns:
            Filtered list
        """
        return [
            f for f in self.files
            if f.duration and min_duration <= f.duration <= max_duration or not f.duration
        ]

    def search_files(self, query: str) -> List[AudioFileInfo]:
        """
        Search files by name

        Args:
            query: Search query (case-insensitive)

        Returns:
            Matching files
        """
        query_lower = query.lower()
        return [f for f in self.files if query_lower in f.name.lower()]

    def sort_files(self, option: SortOption) -> List[AudioFileInfo]:
        """
        Sort files

        Args:
            option: Sort option

        Returns:
            Sorted list
        """
        self.sort_option = option

        if option == SortOption.NAME_ASC:
            self.files.sort(key=lambda f: f.name.lower())
        elif option == SortOption.NAME_DESC:
            self.files.sort(key=lambda f: f.name.lower(), reverse=True)
        elif option == SortOption.SIZE_ASC:
            self.files.sort(key=lambda f: f.size)
        elif option == SortOption.SIZE_DESC:
            self.files.sort(key=lambda f: f.size, reverse=True)
        elif option == SortOption.MODIFIED_ASC:
            self.files.sort(key=lambda f: f.modified_time)
        elif option == SortOption.MODIFIED_DESC:
            self.files.sort(key=lambda f: f.modified_time, reverse=True)
        elif option == SortOption.DURATION_ASC:
            self.files.sort(key=lambda f: f.duration or 0)
        elif option == SortOption.DURATION_DESC:
            self.files.sort(key=lambda f: f.duration or 0, reverse=True)

        return self.files

    def _apply_sort(self) -> None:
        """Apply current sort option"""
        self.sort_files(self.sort_option)

    def get_directory_tree(self, path: Optional[str] = None, depth: int = 3) -> Dict[str, Any]:
        """
        Get directory tree structure

        Args:
            path: Starting path
            depth: Maximum depth to traverse

        Returns:
            Tree structure
        """
        if path is None:
            path = str(self.current_path)

        tree = {"name": Path(path).name, "path": path, "type": "dir", "children": []}

        if depth <= 0:
            return tree

        try:
            for item_path in sorted(Path(path).iterdir()):
                if item_path.is_dir() and not item_path.name.startswith("."):
                    tree["children"].append(self.get_directory_tree(str(item_path), depth - 1))
                elif item_path.is_file() and item_path.suffix.lower() in self.AUDIO_FORMATS:
                    tree["children"].append({"name": item_path.name, "path": str(item_path), "type": "file"})

        except Exception as e:
            logger.error(f"Error building tree: {e}")

        return tree

    def get_duplicate_report(self) -> str:
        """
        Get formatted duplicate report

        Returns:
            Report string
        """
        if not self.duplicates:
            return "No duplicates found"

        lines = ["=" * 50, "DUPLICATE FILES REPORT", "=" * 50]

        for i, group in enumerate(self.duplicates, 1):
            lines.append(f"\nGroup {i} ({len(group)} files):")
            for file_info in sorted(group, key=lambda f: f.size, reverse=True):
                lines.append(f"  {file_info.name}")
                lines.append(f"    Size: {file_info.format_size()}")
                lines.append(f"    Path: {file_info.path}")
                lines.append(f"    Hash: {file_info.file_hash[:16]}...")

        lines.append(f"\nTotal duplicate groups: {len(self.duplicates)}")
        lines.append(f"Total duplicate files: {sum(len(g) - 1 for g in self.duplicates)}")

        return "\n".join(lines)

    def get_library_report(self) -> str:
        """
        Get formatted library report

        Returns:
            Report string
        """
        stats = self.get_statistics()

        lines = ["=" * 50, "LIBRARY STATISTICS REPORT", "=" * 50]
        lines.append(f"Root Path: {self.root_path}")
        lines.append(f"Current Path: {self.current_path}")
        lines.append("")
        lines.append(f"Total Files: {stats.total_files}")
        lines.append(f"Total Size: {stats.format_total_size()}")
        lines.append(f"Total Duration: {stats.format_total_duration()}")
        lines.append(f"Average File Size: {stats.average_file_size / 1024 / 1024:.1f}MB")
        lines.append(f"Average Duration: {stats.average_duration / 60:.1f} minutes")
        lines.append("")
        lines.append("Format Breakdown:")
        for format_type, count in sorted(stats.file_formats.items()):
            lines.append(f"  .{format_type}: {count} files")
        lines.append("")
        lines.append(f"Duplicate Groups: {stats.duplicate_groups}")
        lines.append(f"Duplicate Files: {stats.duplicate_files}")

        return "\n".join(lines)


# Global singleton instance
_browser: Optional[LibraryBrowser] = None


def get_library_browser(root_path: Optional[str] = None) -> LibraryBrowser:
    """Get or create library browser singleton"""
    global _browser
    if _browser is None:
        _browser = LibraryBrowser(root_path)
    return _browser
