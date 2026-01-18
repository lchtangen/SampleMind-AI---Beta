"""
History & Undo/Redo System for SampleMind TUI
Track operations and support undo/redo functionality
"""

import logging
from typing import List, Optional, Any, Callable, Dict
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations that can be undone"""
    ANALYSIS = "analysis"
    TAG_ADD = "tag_add"
    TAG_REMOVE = "tag_remove"
    FAVORITE_ADD = "favorite_add"
    FAVORITE_REMOVE = "favorite_remove"
    RATING_CHANGE = "rating_change"
    NOTES_CHANGE = "notes_change"
    EXPORT = "export"
    SETTINGS_CHANGE = "settings_change"
    COMPARISON = "comparison"
    SEARCH = "search"


@dataclass
class HistoryEntry:
    """Single history entry for undo/redo"""
    operation_type: OperationType
    timestamp: str
    description: str
    data: Dict[str, Any]
    undo_action: Optional[Callable] = None
    redo_action: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for export)"""
        return {
            "operation_type": self.operation_type.value,
            "timestamp": self.timestamp,
            "description": self.description,
            "data": self.data,
        }


class HistoryManager:
    """Manages operation history for undo/redo"""

    def __init__(self, max_history: int = 100):
        """
        Initialize history manager

        Args:
            max_history: Maximum history entries to keep
        """
        self.max_history = max_history
        self.history: List[HistoryEntry] = []
        self.current_index = -1
        self.stats = {
            "total_operations": 0,
            "undo_count": 0,
            "redo_count": 0,
        }

    def add_entry(
        self,
        operation_type: OperationType,
        description: str,
        data: Dict[str, Any],
        undo_action: Optional[Callable] = None,
        redo_action: Optional[Callable] = None,
    ) -> None:
        """
        Add operation to history

        Args:
            operation_type: Type of operation
            description: Human-readable description
            data: Operation data/context
            undo_action: Function to undo this operation
            redo_action: Function to redo this operation
        """
        # Remove any entries after current index (redo stack)
        self.history = self.history[: self.current_index + 1]

        # Create entry
        entry = HistoryEntry(
            operation_type=operation_type,
            timestamp=datetime.now().isoformat(),
            description=description,
            data=data,
            undo_action=undo_action,
            redo_action=redo_action,
        )

        self.history.append(entry)
        self.current_index = len(self.history) - 1

        # Trim history if too large
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]
            self.current_index = len(self.history) - 1

        self.stats["total_operations"] += 1
        logger.debug(f"Added history entry: {description}")

    def undo(self) -> bool:
        """
        Undo last operation

        Returns:
            True if undo was successful
        """
        if self.current_index <= 0:
            logger.warning("No operations to undo")
            return False

        entry = self.history[self.current_index]

        try:
            if entry.undo_action:
                entry.undo_action()

            self.current_index -= 1
            self.stats["undo_count"] += 1
            logger.info(f"Undid: {entry.description}")
            return True

        except Exception as e:
            logger.error(f"Failed to undo operation: {e}")
            return False

    def redo(self) -> bool:
        """
        Redo last undone operation

        Returns:
            True if redo was successful
        """
        if self.current_index >= len(self.history) - 1:
            logger.warning("No operations to redo")
            return False

        entry = self.history[self.current_index + 1]

        try:
            if entry.redo_action:
                entry.redo_action()

            self.current_index += 1
            self.stats["redo_count"] += 1
            logger.info(f"Redid: {entry.description}")
            return True

        except Exception as e:
            logger.error(f"Failed to redo operation: {e}")
            return False

    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.current_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.current_index < len(self.history) - 1

    def get_undo_description(self) -> Optional[str]:
        """Get description of next undo operation"""
        if self.current_index >= 0:
            return self.history[self.current_index].description
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of next redo operation"""
        if self.current_index < len(self.history) - 1:
            return self.history[self.current_index + 1].description
        return None

    def get_history(self, limit: int = 50) -> List[HistoryEntry]:
        """Get recent history entries"""
        start_idx = max(0, len(self.history) - limit)
        return self.history[start_idx:]

    def get_history_by_type(
        self, operation_type: OperationType, limit: int = 20
    ) -> List[HistoryEntry]:
        """Get history entries of specific type"""
        entries = [
            e for e in self.history if e.operation_type == operation_type
        ]
        return entries[-limit:] if limit else entries

    def get_current_state(self) -> Optional[HistoryEntry]:
        """Get current state in history"""
        if self.current_index >= 0:
            return self.history[self.current_index]
        return None

    def export_history(self) -> List[Dict[str, Any]]:
        """Export history as list of dictionaries"""
        return [entry.to_dict() for entry in self.history]

    def import_history(self, data: List[Dict[str, Any]]) -> None:
        """Import history from exported data"""
        self.history = []
        for item in data:
            try:
                entry = HistoryEntry(
                    operation_type=OperationType[item["operation_type"].upper()],
                    timestamp=item["timestamp"],
                    description=item["description"],
                    data=item["data"],
                )
                self.history.append(entry)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to import history entry: {e}")

        self.current_index = len(self.history) - 1

    def clear_history(self) -> None:
        """Clear all history"""
        self.history = []
        self.current_index = -1
        logger.info("History cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics"""
        return {
            "total_entries": len(self.history),
            "current_index": self.current_index,
            "can_undo": self.can_undo(),
            "can_redo": self.can_redo(),
            "total_operations": self.stats["total_operations"],
            "undo_count": self.stats["undo_count"],
            "redo_count": self.stats["redo_count"],
            "operation_types": self._count_operation_types(),
        }

    def _count_operation_types(self) -> Dict[str, int]:
        """Count operations by type"""
        counts = {}
        for entry in self.history:
            op_type = entry.operation_type.value
            counts[op_type] = counts.get(op_type, 0) + 1
        return counts

    def print_info(self) -> str:
        """Print history information"""
        stats = self.get_statistics()
        lines = [
            "╔════════════════════════════════════════╗",
            "║         HISTORY INFORMATION           ║",
            "╠════════════════════════════════════════╣",
            f"║ Total Entries: {stats['total_entries']:>28} ║",
            f"║ Current Index: {stats['current_index']:>28} ║",
            f"║ Can Undo: {'Yes' if stats['can_undo'] else 'No':>31} ║",
            f"║ Can Redo: {'Yes' if stats['can_redo'] else 'No':>31} ║",
            f"║ Total Operations: {stats['total_operations']:>24} ║",
            f"║ Undo Count: {stats['undo_count']:>30} ║",
            f"║ Redo Count: {stats['redo_count']:>30} ║",
            "╚════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


# Global singleton instance
_history_manager: Optional[HistoryManager] = None


def get_history_manager() -> HistoryManager:
    """Get or create history manager singleton"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager
