"""
Session Management System for SampleMind AI

Allows users to:
- Save analysis sessions (state + results)
- Resume previous sessions
- Save session notes and metadata
- Export session reports
- Manage session history
- Track session analytics
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status states"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AnalysisResult:
    """Represents a single audio analysis result"""

    def __init__(
        self,
        file_id: str,
        filename: str,
        filepath: str,
        features: Optional[Dict] = None,
        analysis_level: str = "standard",
        duration: float = 0.0,
        timestamp: Optional[str] = None
    ):
        self.file_id = file_id
        self.filename = filename
        self.filepath = filepath
        self.features = features or {}
        self.analysis_level = analysis_level
        self.duration = duration
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "file_id": self.file_id,
            "filename": self.filename,
            "filepath": self.filepath,
            "features": self.features,
            "analysis_level": self.analysis_level,
            "duration": self.duration,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AnalysisResult":
        """Create from dictionary"""
        return cls(
            file_id=data["file_id"],
            filename=data["filename"],
            filepath=data["filepath"],
            features=data.get("features", {}),
            analysis_level=data.get("analysis_level", "standard"),
            duration=data.get("duration", 0.0),
            timestamp=data.get("timestamp")
        )


class Session:
    """Represents an analysis session"""

    def __init__(
        self,
        session_id: Optional[str] = None,
        name: str = "Untitled Session",
        description: str = "",
        created_at: Optional[str] = None
    ):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now().isoformat()
        self.modified_at = datetime.now().isoformat()
        self.status = SessionStatus.ACTIVE
        self.results: Dict[str, AnalysisResult] = {}
        self.notes: List[str] = []
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def add_result(self, result: AnalysisResult) -> bool:
        """Add analysis result to session"""
        if result.file_id in self.results:
            logger.debug(f"Result for {result.filename} already in session")
            return False

        self.results[result.file_id] = result
        self._update_modified()
        logger.debug(f"Added {result.filename} to session {self.name}")
        return True

    def remove_result(self, file_id: str) -> bool:
        """Remove analysis result from session"""
        if file_id not in self.results:
            return False

        del self.results[file_id]
        self._update_modified()
        return True

    def get_result(self, file_id: str) -> Optional[AnalysisResult]:
        """Get analysis result by ID"""
        return self.results.get(file_id)

    def list_results(self) -> List[AnalysisResult]:
        """Get all results in session"""
        return list(self.results.values())

    def add_note(self, note: str) -> None:
        """Add a note to the session"""
        self.notes.append(f"[{datetime.now().isoformat()}] {note}")
        self._update_modified()

    def get_notes(self) -> List[str]:
        """Get all session notes"""
        return self.notes.copy()

    def add_tag(self, tag: str) -> None:
        """Add tag to session"""
        if tag not in self.tags:
            self.tags.append(tag)
            self._update_modified()

    def remove_tag(self, tag: str) -> None:
        """Remove tag from session"""
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_modified()

    def set_status(self, status: SessionStatus) -> None:
        """Set session status"""
        self.status = status
        self._update_modified()

    def _update_modified(self) -> None:
        """Update modification timestamp"""
        self.modified_at = datetime.now().isoformat()

    def get_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        if not self.results:
            return {
                "total_files": 0,
                "total_duration": 0.0,
                "average_duration": 0.0
            }

        durations = [r.duration for r in self.results.values()]
        total_duration = sum(durations)

        return {
            "total_files": len(self.results),
            "total_duration": total_duration,
            "average_duration": total_duration / len(self.results) if self.results else 0.0,
            "min_duration": min(durations) if durations else 0.0,
            "max_duration": max(durations) if durations else 0.0,
            "results_by_level": self._count_by_level()
        }

    def _count_by_level(self) -> Dict[str, int]:
        """Count results by analysis level"""
        counts = {}
        for result in self.results.values():
            level = result.analysis_level
            counts[level] = counts.get(level, 0) + 1
        return counts

    def to_dict(self) -> Dict:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "status": self.status.value,
            "results": [r.to_dict() for r in self.results.values()],
            "notes": self.notes,
            "tags": self.tags,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        """Create session from dictionary"""
        session = cls(
            session_id=data.get("session_id"),
            name=data.get("name", "Untitled"),
            description=data.get("description", ""),
            created_at=data.get("created_at")
        )

        session.modified_at = data.get("modified_at", datetime.now().isoformat())
        session.status = SessionStatus(data.get("status", "active"))
        session.notes = data.get("notes", [])
        session.tags = data.get("tags", [])
        session.metadata = data.get("metadata", {})

        # Add results
        for result_data in data.get("results", []):
            result = AnalysisResult.from_dict(result_data)
            session.add_result(result)

        return session


class SessionManager:
    """
    Manages user sessions.

    Provides:
    - Session creation and management
    - Session persistence
    - Session history
    - Session export/import
    - Session search
    """

    def __init__(self, storage_dir: str = ".samplemind/sessions"):
        """
        Initialize session manager.

        Args:
            storage_dir: Directory for storing sessions
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Session] = {}
        self.current_session: Optional[Session] = None
        self._load_sessions()

        logger.info(f"Session manager initialized at {self.storage_dir.absolute()}")

    def create_session(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict] = None
    ) -> Session:
        """
        Create a new session.

        Args:
            name: Session name
            description: Session description
            metadata: Additional metadata

        Returns:
            Created session
        """
        session = Session(name=name, description=description)
        session.metadata = metadata or {}

        self.sessions[session.session_id] = session
        self._save_session(session)

        logger.info(f"Created session: {name} ({session.session_id})")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def list_sessions(
        self,
        status: Optional[SessionStatus] = None,
        limit: int = 20
    ) -> List[Session]:
        """
        List sessions.

        Args:
            status: Filter by status (None = all)
            limit: Maximum number to return

        Returns:
            List of sessions
        """
        sessions = list(self.sessions.values())

        if status:
            sessions = [s for s in sessions if s.status == status]

        # Sort by modification time (newest first)
        sessions.sort(key=lambda s: s.modified_at, reverse=True)

        return sessions[:limit]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: ID of session to delete

        Returns:
            True if deleted
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False

        session_name = self.sessions[session_id].name
        del self.sessions[session_id]
        self._delete_session_file(session_id)

        if self.current_session and self.current_session.session_id == session_id:
            self.current_session = None

        logger.info(f"Deleted session: {session_name}")
        return True

    def activate_session(self, session_id: str) -> bool:
        """
        Activate a session (make it current).

        Args:
            session_id: ID of session to activate

        Returns:
            True if activated
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False

        session.set_status(SessionStatus.ACTIVE)
        self.current_session = session
        self._save_session(session)

        logger.info(f"Activated session: {session.name}")
        return True

    def pause_session(self, session_id: str) -> bool:
        """Pause a session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.set_status(SessionStatus.PAUSED)
        self._save_session(session)

        if self.current_session and self.current_session.session_id == session_id:
            self.current_session = None

        return True

    def archive_session(self, session_id: str) -> bool:
        """Archive a session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.set_status(SessionStatus.ARCHIVED)
        self._save_session(session)
        return True

    def search_sessions(
        self,
        query: str,
        search_results: bool = True,
        search_notes: bool = True
    ) -> List[Session]:
        """
        Search sessions by name, description, notes, or results.

        Args:
            query: Search query
            search_results: Search in file results
            search_notes: Search in session notes

        Returns:
            List of matching sessions
        """
        query_lower = query.lower()
        results = []

        for session in self.sessions.values():
            # Search name and description
            if query_lower in session.name.lower() or query_lower in session.description.lower():
                results.append(session)
                continue

            # Search notes
            if search_notes:
                for note in session.notes:
                    if query_lower in note.lower():
                        results.append(session)
                        break

            # Search results
            if search_results:
                for analysis_result in session.results.values():
                    if query_lower in analysis_result.filename.lower():
                        results.append(session)
                        break

        return results

    def export_session(self, session_id: str, export_path: str) -> bool:
        """
        Export session to JSON file.

        Args:
            session_id: ID of session to export
            export_path: Path to export to

        Returns:
            True if exported
        """
        session = self.get_session(session_id)
        if not session:
            return False

        try:
            with open(export_path, "w") as f:
                json.dump(session.to_dict(), f, indent=2)

            logger.info(f"Exported session {session.name} to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            return False

    def import_session(self, import_path: str) -> Optional[Session]:
        """
        Import session from JSON file.

        Args:
            import_path: Path to import from

        Returns:
            Imported session or None
        """
        try:
            with open(import_path, "r") as f:
                data = json.load(f)

            session = Session.from_dict(data)
            self.sessions[session.session_id] = session
            self._save_session(session)

            logger.info(f"Imported session: {session.name}")
            return session
        except Exception as e:
            logger.error(f"Failed to import session: {e}")
            return None

    def _save_session(self, session: Session) -> None:
        """Save session to disk"""
        file_path = self.storage_dir / f"{session.session_id}.json"

        try:
            with open(file_path, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
            logger.debug(f"Saved session {session.name}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def _load_sessions(self) -> None:
        """Load all sessions from disk"""
        for json_file in self.storage_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)

                session = Session.from_dict(data)
                self.sessions[session.session_id] = session

                logger.debug(f"Loaded session: {session.name}")
            except Exception as e:
                logger.warning(f"Failed to load session from {json_file}: {e}")

    def _delete_session_file(self, session_id: str) -> None:
        """Delete session file from disk"""
        file_path = self.storage_dir / f"{session_id}.json"

        try:
            file_path.unlink(missing_ok=True)
            logger.debug(f"Deleted session file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete session file: {e}")


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def init_sessions(storage_dir: str = ".samplemind/sessions") -> SessionManager:
    """Initialize global session manager"""
    global _session_manager
    _session_manager = SessionManager(storage_dir)
    return _session_manager


def get_sessions() -> SessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
