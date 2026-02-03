"""
Session Management System for SampleMind TUI
Save and restore session state, manage projects
"""

import logging
import json
from typing import Optional, Dict, List, Any
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AnalyzedFile:
    """Information about an analyzed file in session"""
    path: str
    name: str
    analysis_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    rating: int = 0
    favorite: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionSnapshot:
    """Complete session state snapshot"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Session"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""

    # Session content
    analyzed_files: List[AnalyzedFile] = field(default_factory=list)
    favorite_files: List[str] = field(default_factory=list)  # File paths
    pinned_files: List[str] = field(default_factory=list)
    notes: str = ""

    # UI state
    current_screen: str = "main"
    search_query: str = ""
    active_filters: Dict[str, Any] = field(default_factory=dict)

    # Settings snapshot
    settings: Dict[str, Any] = field(default_factory=dict)
    theme: str = "dark"

    # Metadata
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Manages session saving and restoration"""

    def __init__(self, session_dir: Optional[str] = None) -> None:
        """
        Initialize session manager

        Args:
            session_dir: Directory for session files
        """
        if session_dir is None:
            session_dir = str(Path.home() / ".samplemind" / "sessions")

        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[SessionSnapshot] = None
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes

    def create_session(self, name: str, description: str = "") -> SessionSnapshot:
        """
        Create a new session

        Args:
            name: Session name
            description: Session description

        Returns:
            New session snapshot
        """
        session = SessionSnapshot(name=name, description=description)
        self.current_session = session
        logger.info(f"Created new session: {name}")
        return session

    def save_session(self, session: Optional[SessionSnapshot] = None) -> bool:
        """
        Save session to file

        Args:
            session: Session to save (uses current if None)

        Returns:
            True if successful
        """
        if session is None:
            session = self.current_session

        if session is None:
            logger.warning("No session to save")
            return False

        try:
            # Update modification time
            session.modified_at = datetime.now().isoformat()

            # Create session file
            session_file = self.session_dir / f"{session.session_id}.json"

            # Convert to JSON-serializable dict
            session_data = {
                "session_id": session.session_id,
                "name": session.name,
                "created_at": session.created_at,
                "modified_at": session.modified_at,
                "description": session.description,
                "analyzed_files": [asdict(f) for f in session.analyzed_files],
                "favorite_files": session.favorite_files,
                "pinned_files": session.pinned_files,
                "notes": session.notes,
                "current_screen": session.current_screen,
                "search_query": session.search_query,
                "active_filters": session.active_filters,
                "settings": session.settings,
                "theme": session.theme,
                "version": session.version,
                "metadata": session.metadata,
            }

            with open(session_file, "w") as f:
                json.dump(session_data, f, indent=2)

            logger.info(f"Saved session: {session.name} to {session_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    def load_session(self, session_id: str) -> Optional[SessionSnapshot]:
        """
        Load session from file

        Args:
            session_id: Session ID

        Returns:
            SessionSnapshot or None
        """
        try:
            session_file = self.session_dir / f"{session_id}.json"

            if not session_file.exists():
                logger.warning(f"Session file not found: {session_file}")
                return None

            with open(session_file, "r") as f:
                session_data = json.load(f)

            # Reconstruct session
            session = SessionSnapshot(
                session_id=session_data["session_id"],
                name=session_data["name"],
                created_at=session_data["created_at"],
                modified_at=session_data["modified_at"],
                description=session_data.get("description", ""),
                analyzed_files=[
                    AnalyzedFile(**f) for f in session_data.get("analyzed_files", [])
                ],
                favorite_files=session_data.get("favorite_files", []),
                pinned_files=session_data.get("pinned_files", []),
                notes=session_data.get("notes", ""),
                current_screen=session_data.get("current_screen", "main"),
                search_query=session_data.get("search_query", ""),
                active_filters=session_data.get("active_filters", {}),
                settings=session_data.get("settings", {}),
                theme=session_data.get("theme", "dark"),
                version=session_data.get("version", "1.0"),
                metadata=session_data.get("metadata", {}),
            )

            self.current_session = session
            logger.info(f"Loaded session: {session.name}")
            return session

        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return None

    def get_all_sessions(self) -> List[SessionSnapshot]:
        """
        Get all available sessions

        Returns:
            List of session snapshots
        """
        sessions = []

        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file, "r") as f:
                    session_data = json.load(f)

                session = SessionSnapshot(
                    session_id=session_data["session_id"],
                    name=session_data["name"],
                    created_at=session_data["created_at"],
                    modified_at=session_data["modified_at"],
                    description=session_data.get("description", ""),
                )

                sessions.append(session)

            except Exception as e:
                logger.error(f"Error reading session file {session_file}: {e}")

        # Sort by modified time, newest first
        sessions.sort(key=lambda s: s.modified_at, reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        try:
            session_file = self.session_dir / f"{session_id}.json"

            if not session_file.exists():
                logger.warning(f"Session not found: {session_id}")
                return False

            session_file.unlink()
            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

    def add_analyzed_file(
        self, path: str, analysis_id: str, tags: Optional[List[str]] = None
    ) -> None:
        """
        Add analyzed file to current session

        Args:
            path: File path
            analysis_id: Analysis ID
            tags: Optional tags
        """
        if self.current_session is None:
            logger.warning("No session active")
            return

        file_info = AnalyzedFile(
            path=path, name=Path(path).name, analysis_id=analysis_id, tags=tags or []
        )

        self.current_session.analyzed_files.append(file_info)
        logger.debug(f"Added file to session: {path}")

    def add_favorite_file(self, path: str) -> None:
        """
        Add file to favorites in session

        Args:
            path: File path
        """
        if self.current_session is None:
            return

        if path not in self.current_session.favorite_files:
            self.current_session.favorite_files.append(path)

    def remove_favorite_file(self, path: str) -> None:
        """
        Remove file from favorites

        Args:
            path: File path
        """
        if self.current_session is None:
            return

        if path in self.current_session.favorite_files:
            self.current_session.favorite_files.remove(path)

    def set_session_note(self, note: str) -> None:
        """
        Set session note

        Args:
            note: Note text
        """
        if self.current_session is None:
            return

        self.current_session.notes = note

    def get_session_statistics(
        self, session: Optional[SessionSnapshot] = None
    ) -> Dict[str, Any]:
        """
        Get session statistics

        Args:
            session: Session (uses current if None)

        Returns:
            Statistics dictionary
        """
        if session is None:
            session = self.current_session

        if session is None:
            return {}

        return {
            "total_files": len(session.analyzed_files),
            "total_favorites": len(session.favorite_files),
            "total_pinned": len(session.pinned_files),
            "file_formats": self._count_formats(session.analyzed_files),
            "total_tags": len(set(tag for f in session.analyzed_files for tag in f.tags)),
            "session_duration": self._calculate_duration(
                session.created_at, session.modified_at
            ),
        }

    def export_session(self, session: Optional[SessionSnapshot] = None, file_path: Optional[str] = None) -> bool:
        """
        Export session to file

        Args:
            session: Session to export (uses current if None)
            file_path: Export path (uses default if None)

        Returns:
            True if successful
        """
        if session is None:
            session = self.current_session

        if session is None:
            return False

        if file_path is None:
            file_path = str(
                self.session_dir / f"{session.name}_{session.session_id[:8]}.smai"
            )

        return self.save_session(session)

    @staticmethod
    def _count_formats(files: List[AnalyzedFile]) -> Dict[str, int]:
        """Count file formats"""
        formats: Dict[str, int] = {}
        for file in files:
            ext = Path(file.path).suffix.lower()
            formats[ext] = formats.get(ext, 0) + 1
        return formats

    @staticmethod
    def _calculate_duration(start: str, end: str) -> str:
        """Calculate duration between timestamps"""
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            duration = end_dt - start_dt
            return str(duration)
        except Exception:
            return "N/A"


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(session_dir: Optional[str] = None) -> SessionManager:
    """Get or create session manager singleton"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(session_dir)
    return _session_manager
