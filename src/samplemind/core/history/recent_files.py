#!/usr/bin/env python3
"""
Recent Files Tracking System

Maintains a history of recently analyzed audio files for quick access.
Enables users to use shortcuts like @1, @2, etc. to reference recent files.

Features:
- Persistent history storage in ~/.samplemind/recent_files.json
- Automatic timestamp tracking
- File size and duration caching
- Quick @N access shortcuts
- File existence validation
- Configurable history limit (default: 50 files)
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class RecentFile:
    """Represents a recently analyzed file"""
    path: str  # Full path to the file
    name: str  # Filename only
    timestamp: str  # ISO format timestamp
    size_bytes: int = 0
    duration_seconds: float = 0.0
    analysis_level: str = "STANDARD"  # BASIC, STANDARD, DETAILED, PROFESSIONAL
    tags: List[str] = field(default_factory=list)  # Auto-assigned tags

    @property
    def path_obj(self) -> Path:
        """Get Path object"""
        return Path(self.path)

    @property
    def time_ago(self) -> str:
        """Get human-readable time since analysis"""
        try:
            dt = datetime.fromisoformat(self.timestamp)
            now = datetime.now()
            delta = now - dt

            if delta.seconds < 60:
                return "just now"
            elif delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"{minutes}m ago"
            elif delta.seconds < 86400:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
            else:
                days = delta.days
                return f"{days}d ago"
        except Exception:
            return "unknown"

    @property
    def size_mb(self) -> float:
        """Get file size in MB"""
        return self.size_bytes / (1024 * 1024)

    def is_valid(self) -> bool:
        """Check if file still exists"""
        return self.path_obj.exists()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RecentFile":
        """Create from dictionary"""
        return cls(**data)


# ============================================================================
# RECENT FILES MANAGER
# ============================================================================

class RecentFilesManager:
    """Manages recent file history"""

    def __init__(self, max_history: int = 50):
        """
        Initialize Recent Files Manager

        Args:
            max_history: Maximum number of files to keep (default: 50)
        """
        self.max_history = max_history
        self.config_dir = Path.home() / ".samplemind"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.config_dir / "recent_files.json"
        self._files: List[RecentFile] = []
        self._load()

    def _load(self) -> None:
        """Load recent files from disk"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self._files = [RecentFile.from_dict(item) for item in data]
                    logger.debug(f"Loaded {len(self._files)} recent files")
            except Exception as e:
                logger.error(f"Failed to load recent files: {e}")
                self._files = []
        else:
            self._files = []

    def _save(self) -> None:
        """Save recent files to disk"""
        try:
            with open(self.history_file, "w") as f:
                data = [f.to_dict() for f in self._files]
                json.dump(data, f, indent=2)
                logger.debug(f"Saved {len(self._files)} recent files")
        except Exception as e:
            logger.error(f"Failed to save recent files: {e}")

    def add(
        self,
        file_path: Path,
        analysis_level: str = "STANDARD",
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Add a file to recent history

        Args:
            file_path: Path to the audio file
            analysis_level: Level of analysis performed
            tags: Optional tags for the file
        """
        file_path = Path(file_path).expanduser().resolve()

        # Check if file already exists in history
        existing_index = None
        for i, f in enumerate(self._files):
            if Path(f.path).resolve() == file_path:
                existing_index = i
                break

        # Create new recent file entry
        recent_file = RecentFile(
            path=str(file_path),
            name=file_path.name,
            timestamp=datetime.now().isoformat(),
            size_bytes=file_path.stat().st_size if file_path.exists() else 0,
            analysis_level=analysis_level,
            tags=tags or [],
        )

        # Remove if already exists (we'll re-add at top)
        if existing_index is not None:
            self._files.pop(existing_index)

        # Add to beginning (most recent first)
        self._files.insert(0, recent_file)

        # Trim to max history
        self._files = self._files[:self.max_history]

        # Save to disk
        self._save()

    def get_all(self) -> List[RecentFile]:
        """Get all recent files (in order of recency)"""
        # Filter out files that no longer exist
        valid_files = [f for f in self._files if f.is_valid()]

        # Remove invalid files from list
        if len(valid_files) < len(self._files):
            self._files = valid_files
            self._save()

        return valid_files

    def get_by_index(self, index: int) -> Optional[RecentFile]:
        """
        Get recent file by index (1-based)

        Args:
            index: 1-based index (1 = most recent)

        Returns:
            RecentFile or None if index out of range
        """
        files = self.get_all()
        if 1 <= index <= len(files):
            return files[index - 1]
        return None

    def get_most_recent(self) -> Optional[RecentFile]:
        """Get the most recently analyzed file"""
        files = self.get_all()
        return files[0] if files else None

    def clear(self) -> None:
        """Clear all recent file history"""
        self._files = []
        self._save()

    def remove(self, file_path: Path) -> bool:
        """
        Remove a file from history

        Args:
            file_path: Path to the file to remove

        Returns:
            True if removed, False if not found
        """
        file_path = Path(file_path).expanduser().resolve()

        for i, f in enumerate(self._files):
            if Path(f.path).resolve() == file_path:
                self._files.pop(i)
                self._save()
                return True

        return False

    def search(self, query: str) -> List[RecentFile]:
        """
        Search recent files by name, path, or tags

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching RecentFile objects
        """
        query_lower = query.lower()
        results = []

        for f in self.get_all():
            if (
                query_lower in f.name.lower()
                or query_lower in f.path.lower()
                or any(query_lower in tag.lower() for tag in f.tags)
            ):
                results.append(f)

        return results

    def export(self, output_path: Optional[Path] = None) -> str:
        """
        Export recent files as JSON

        Args:
            output_path: Optional path to save JSON file

        Returns:
            JSON string of recent files
        """
        data = [f.to_dict() for f in self.get_all()]
        json_str = json.dumps(data, indent=2)

        if output_path:
            output_path.write_text(json_str)

        return json_str

    def stats(self) -> Dict[str, any]:
        """Get statistics about recent files"""
        files = self.get_all()

        total_size = sum(f.size_bytes for f in files)
        total_duration = sum(f.duration_seconds for f in files)

        # Group by analysis level
        by_level = {}
        for f in files:
            level = f.analysis_level
            by_level[level] = by_level.get(level, 0) + 1

        # Collect all tags
        all_tags = {}
        for f in files:
            for tag in f.tags:
                all_tags[tag] = all_tags.get(tag, 0) + 1

        return {
            "total_files": len(files),
            "total_size_mb": total_size / (1024 * 1024),
            "total_duration_hours": total_duration / 3600,
            "by_analysis_level": by_level,
            "top_tags": sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10],
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_manager: Optional[RecentFilesManager] = None


def get_manager() -> RecentFilesManager:
    """Get global recent files manager instance"""
    global _manager
    if _manager is None:
        _manager = RecentFilesManager()
    return _manager


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def add_recent_file(
    file_path: Path,
    analysis_level: str = "STANDARD",
    tags: Optional[List[str]] = None,
) -> None:
    """Add a file to recent history"""
    manager = get_manager()
    manager.add(file_path, analysis_level, tags)


def get_recent_files() -> List[RecentFile]:
    """Get all recent files"""
    manager = get_manager()
    return manager.get_all()


def get_recent_file_by_index(index: int) -> Optional[RecentFile]:
    """Get recent file by index (1-based)"""
    manager = get_manager()
    return manager.get_by_index(index)


def get_most_recent_file() -> Optional[RecentFile]:
    """Get most recently analyzed file"""
    manager = get_manager()
    return manager.get_most_recent()


def search_recent_files(query: str) -> List[RecentFile]:
    """Search recent files"""
    manager = get_manager()
    return manager.search(query)


def export_recent_files(output_path: Optional[Path] = None) -> str:
    """Export recent files as JSON"""
    manager = get_manager()
    return manager.export(output_path)


def get_recent_files_stats() -> Dict[str, any]:
    """Get statistics about recent files"""
    manager = get_manager()
    return manager.stats()


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "RecentFile",
    "RecentFilesManager",
    "get_manager",
    "add_recent_file",
    "get_recent_files",
    "get_recent_file_by_index",
    "get_most_recent_file",
    "search_recent_files",
    "export_recent_files",
    "get_recent_files_stats",
]


if __name__ == "__main__":
    # Demo usage
    manager = RecentFilesManager()

    # Add some test files (if they exist)
    test_files = [
        Path.home() / "Music" / "test.wav",
        Path.home() / "Music" / "drums.mp3",
    ]

    for f in test_files:
        if f.exists():
            manager.add(f, "STANDARD", ["test"])

    # Show recent files
    print("\n📁 Recent Files:")
    for i, f in enumerate(manager.get_all(), 1):
        print(f"  [{i}] {f.name:<40} ({f.time_ago})")

    # Show stats
    stats = manager.stats()
    print(f"\n📊 Statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size_mb']:.2f} MB")
