"""
Keyboard Shortcut Manager for SampleMind TUI
Customizable keyboard bindings with conflict detection
"""

import logging
import json
from typing import Optional, Dict, List, Set, Tuple
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class BindingStyle(Enum):
    """Keyboard binding styles"""
    DEFAULT = "default"
    VIM = "vim"
    EMACS = "emacs"


# Default shortcuts
DEFAULT_SHORTCUTS = {
    # Navigation
    "quit": ["q", "ctrl+q"],
    "back": ["escape", "backspace"],
    "help": ["h", "f1", "?"],
    "menu": ["m", "ctrl+m"],

    # Analysis screen
    "analyze": ["a", "ctrl+a"],
    "browse": ["ctrl+o"],
    "batch": ["b", "ctrl+b"],

    # Results
    "export": ["ctrl+e"],
    "save": ["ctrl+s"],
    "copy": ["ctrl+c"],
    "compare": ["c"],

    # Playback
    "play_pause": ["space"],
    "stop": ["ctrl+."],
    "next": ["n", "right", "j"],
    "previous": ["p", "left", "k"],
    "seek_forward": [">"],
    "seek_backward": ["<"],

    # Tagging and organization
    "favorite": ["f", "ctrl+d"],
    "tag": ["t", "ctrl+t"],
    "rating_up": ["]"],
    "rating_down": ["["],

    # View and tools
    "settings": ["s", "ctrl+,"],
    "search": ["/", "ctrl+f"],
    "filter": ["ctrl+l"],
    "sort": ["ctrl+k"],
    "refresh": ["r", "f5"],

    # Advanced
    "history": ["ctrl+h"],
    "favorites": ["ctrl+b"],
    "library": ["l", "ctrl+l"],
    "performance": ["ctrl+p"],
    "debug": ["d", "f12"],
}

# Vim-style bindings
VIM_SHORTCUTS = {
    "quit": ["q", "ctrl+c"],
    "next": ["j", "right"],
    "previous": ["k", "left"],
    "play_pause": ["space"],
    "stop": ["ctrl+s"],
    "search": ["/"],
    "filter": [":"],
    "help": ["?"],
    "back": ["escape"],
}

# Emacs-style bindings
EMACS_SHORTCUTS = {
    "quit": ["ctrl+c", "ctrl+d"],
    "next": ["ctrl+n", "down"],
    "previous": ["ctrl+p", "up"],
    "play_pause": ["space"],
    "help": ["ctrl+h"],
    "back": ["ctrl+g"],
}


class ShortcutManager:
    """Manages keyboard shortcuts"""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        """
        Initialize shortcut manager

        Args:
            config_dir: Directory for shortcut configurations
        """
        if config_dir is None:
            config_dir = str(Path.home() / ".samplemind" / "config")

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.shortcuts: Dict[str, List[str]] = DEFAULT_SHORTCUTS.copy()
        self.binding_style = BindingStyle.DEFAULT
        self.config_file = self.config_dir / "shortcuts.json"

        # Load saved shortcuts if they exist
        self._load_shortcuts()

    def set_binding_style(self, style: BindingStyle) -> None:
        """
        Set binding style (default, vim, emacs)

        Args:
            style: Binding style
        """
        self.binding_style = style

        if style == BindingStyle.VIM:
            self.shortcuts = DEFAULT_SHORTCUTS.copy()
            self.shortcuts.update(VIM_SHORTCUTS)
        elif style == BindingStyle.EMACS:
            self.shortcuts = DEFAULT_SHORTCUTS.copy()
            self.shortcuts.update(EMACS_SHORTCUTS)
        else:
            self.shortcuts = DEFAULT_SHORTCUTS.copy()

        logger.info(f"Set binding style to: {style.value}")

    def get_shortcut(self, action: str) -> Optional[List[str]]:
        """
        Get shortcuts for an action

        Args:
            action: Action name

        Returns:
            List of key combinations
        """
        return self.shortcuts.get(action)

    def get_primary_shortcut(self, action: str) -> Optional[str]:
        """
        Get primary (first) shortcut for an action

        Args:
            action: Action name

        Returns:
            First key combination
        """
        shortcuts = self.shortcuts.get(action, [])
        return shortcuts[0] if shortcuts else None

    def set_shortcut(self, action: str, keys: List[str]) -> bool:
        """
        Set shortcut for action

        Args:
            action: Action name
            keys: List of key combinations

        Returns:
            True if successful
        """
        # Check for conflicts
        conflicts = self.detect_conflicts(action, keys)
        if conflicts:
            logger.warning(f"Shortcut conflicts detected: {conflicts}")
            return False

        self.shortcuts[action] = keys
        logger.info(f"Set shortcut for {action}: {keys}")
        return True

    def add_shortcut(self, action: str, key: str) -> bool:
        """
        Add shortcut to an action

        Args:
            action: Action name
            key: Key combination

        Returns:
            True if successful
        """
        if action not in self.shortcuts:
            self.shortcuts[action] = []

        if key in self.shortcuts[action]:
            logger.warning(f"Shortcut {key} already bound to {action}")
            return False

        # Check for conflicts
        conflict = self.find_conflict(key)
        if conflict:
            logger.warning(f"Shortcut {key} conflicts with {conflict}")
            return False

        self.shortcuts[action].append(key)
        logger.info(f"Added shortcut {key} to {action}")
        return True

    def remove_shortcut(self, action: str, key: str) -> bool:
        """
        Remove shortcut from action

        Args:
            action: Action name
            key: Key combination

        Returns:
            True if successful
        """
        if action not in self.shortcuts:
            return False

        if key not in self.shortcuts[action]:
            return False

        self.shortcuts[action].remove(key)
        logger.info(f"Removed shortcut {key} from {action}")
        return True

    def detect_conflicts(self, action: str, keys: List[str]) -> List[Tuple[str, str]]:
        """
        Detect shortcut conflicts

        Args:
            action: Action name
            keys: Key combinations to check

        Returns:
            List of (conflicting_key, conflicting_action) tuples
        """
        conflicts = []

        for key in keys:
            # Check if this key is already bound to a different action
            for existing_action, existing_keys in self.shortcuts.items():
                if existing_action != action and key in existing_keys:
                    conflicts.append((key, existing_action))

        return conflicts

    def find_conflict(self, key: str) -> Optional[str]:
        """
        Find what action a key is currently bound to

        Args:
            key: Key combination

        Returns:
            Action name if bound, None otherwise
        """
        for action, keys in self.shortcuts.items():
            if key in keys:
                return action

        return None

    def get_all_shortcuts(self) -> Dict[str, List[str]]:
        """Get all shortcuts"""
        return self.shortcuts.copy()

    def get_actions(self) -> List[str]:
        """Get all available actions"""
        return list(self.shortcuts.keys())

    def reset_to_defaults(self) -> None:
        """Reset shortcuts to default"""
        self.shortcuts = DEFAULT_SHORTCUTS.copy()
        self.binding_style = BindingStyle.DEFAULT
        logger.info("Reset shortcuts to defaults")

    def save_shortcuts(self) -> bool:
        """
        Save shortcuts to file

        Returns:
            True if successful
        """
        try:
            config = {
                "binding_style": self.binding_style.value,
                "shortcuts": self.shortcuts,
            }

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Saved shortcuts to {self.config_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving shortcuts: {e}")
            return False

    def _load_shortcuts(self) -> None:
        """Load shortcuts from file"""
        if not self.config_file.exists():
            return

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)

            # Load binding style
            style_name = config.get("binding_style", "default")
            try:
                style = BindingStyle[style_name.upper()]
                self.set_binding_style(style)
            except KeyError:
                pass

            # Load shortcuts
            shortcuts = config.get("shortcuts", {})
            if shortcuts:
                self.shortcuts = shortcuts

            logger.info(f"Loaded shortcuts from {self.config_file}")

        except Exception as e:
            logger.error(f"Error loading shortcuts: {e}")

    def export_shortcuts(self, file_path: str) -> bool:
        """
        Export shortcuts to file

        Args:
            file_path: Path to export to

        Returns:
            True if successful
        """
        try:
            config = {
                "binding_style": self.binding_style.value,
                "shortcuts": self.shortcuts,
            }

            with open(file_path, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"Exported shortcuts to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting shortcuts: {e}")
            return False

    def import_shortcuts(self, file_path: str) -> bool:
        """
        Import shortcuts from file

        Args:
            file_path: Path to import from

        Returns:
            True if successful
        """
        try:
            with open(file_path, "r") as f:
                config = json.load(f)

            # Validate before applying
            shortcuts = config.get("shortcuts", {})
            if not shortcuts:
                logger.error("No shortcuts in import file")
                return False

            # Check for conflicts
            all_conflicts = []
            for action, keys in shortcuts.items():
                conflicts = self.detect_conflicts(action, keys)
                all_conflicts.extend(conflicts)

            if all_conflicts:
                logger.warning(f"Import has conflicts: {all_conflicts}")
                # Continue anyway - last binding wins

            # Apply shortcuts
            self.shortcuts = shortcuts
            logger.info(f"Imported shortcuts from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error importing shortcuts: {e}")
            return False

    def format_shortcuts(self) -> str:
        """
        Get formatted shortcuts display

        Returns:
            Formatted string
        """
        lines = ["Keyboard Shortcuts:", "=" * 50]

        # Group by category
        categories = {
            "Navigation": ["quit", "back", "help", "menu"],
            "Analysis": ["analyze", "browse", "batch"],
            "Results": ["export", "save", "copy", "compare"],
            "Playback": [
                "play_pause",
                "stop",
                "next",
                "previous",
                "seek_forward",
                "seek_backward",
            ],
            "Organization": ["favorite", "tag", "rating_up", "rating_down"],
            "Tools": ["settings", "search", "filter", "sort", "refresh"],
            "Advanced": ["history", "favorites", "library", "performance"],
        }

        for category, actions in categories.items():
            lines.append(f"\n{category}:")
            for action in actions:
                shortcuts = self.shortcuts.get(action)
                if shortcuts:
                    keys_str = ", ".join(shortcuts)
                    lines.append(f"  {action:.<30} {keys_str}")

        return "\n".join(lines)


# Global shortcut manager instance
_shortcut_manager: Optional[ShortcutManager] = None


def get_shortcut_manager(config_dir: Optional[str] = None) -> ShortcutManager:
    """Get or create shortcut manager singleton"""
    global _shortcut_manager
    if _shortcut_manager is None:
        _shortcut_manager = ShortcutManager(config_dir)
    return _shortcut_manager
