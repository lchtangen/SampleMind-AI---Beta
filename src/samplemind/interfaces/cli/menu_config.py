#!/usr/bin/env python3
"""
SampleMind AI - Menu Configuration and State Management

Manages menu state, user preferences, and persistent configuration.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from samplemind.interfaces.cli.modern_menu import MenuTheme


@dataclass
class MenuPreferences:
    """User menu preferences"""
    theme: MenuTheme = MenuTheme.DARK
    enable_animations: bool = True
    enable_shortcuts_help: bool = True
    default_analysis_type: str = "standard"
    default_export_format: str = "json"
    remember_last_menu: bool = True
    last_menu_path: str = "main"
    verbose_mode: bool = False
    use_legacy_menu: bool = False  # Option to use old numbered menu
    custom_shortcuts: Dict[str, str] = field(default_factory=dict)
    preferred_ai_provider: str = "gemini"
    auto_refresh_library: bool = True
    show_help_tips: bool = True


class MenuConfigManager:
    """Manages menu configuration and state persistence"""

    CONFIG_DIR = Path.home() / ".samplemind" / "config"
    PREFERENCES_FILE = CONFIG_DIR / "menu_preferences.json"

    def __init__(self) -> None:
        """Initialize configuration manager"""
        self.config_dir = self.CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> MenuPreferences:
        """Load preferences from file or create defaults"""
        if self.PREFERENCES_FILE.exists():
            try:
                with open(self.PREFERENCES_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert theme string back to enum
                    if 'theme' in data:
                        data['theme'] = MenuTheme(data['theme'])
                    return MenuPreferences(**data)
            except (json.JSONDecodeError, ValueError, TypeError):
                # Fall back to defaults if file is corrupted
                return MenuPreferences()
        return MenuPreferences()

    def save_preferences(self) -> bool:
        """Save preferences to file"""
        try:
            # Convert enum to string for JSON serialization
            prefs_dict = asdict(self.preferences)
            if isinstance(prefs_dict['theme'], MenuTheme):
                prefs_dict['theme'] = prefs_dict['theme'].value

            with open(self.PREFERENCES_FILE, 'w') as f:
                json.dump(prefs_dict, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save preferences: {e}")
            return False

    def set_theme(self, theme: MenuTheme) -> None:
        """Set the current theme"""
        self.preferences.theme = theme
        self.save_preferences()

    def set_ai_provider(self, provider: str) -> None:
        """Set the preferred AI provider"""
        self.preferences.preferred_ai_provider = provider
        self.save_preferences()

    def set_analysis_type(self, analysis_type: str) -> None:
        """Set the default analysis type"""
        self.preferences.default_analysis_type = analysis_type
        self.save_preferences()

    def set_export_format(self, export_format: str) -> None:
        """Set the default export format"""
        self.preferences.default_export_format = export_format
        self.save_preferences()

    def register_custom_shortcut(self, action: str, keys: str) -> None:
        """Register a custom keyboard shortcut"""
        self.preferences.custom_shortcuts[action] = keys
        self.save_preferences()

    def get_custom_shortcut(self, action: str) -> Optional[str]:
        """Get a custom keyboard shortcut"""
        return self.preferences.custom_shortcuts.get(action)

    def set_last_menu(self, menu_name: str) -> None:
        """Remember the last menu accessed"""
        if self.preferences.remember_last_menu:
            self.preferences.last_menu_path = menu_name
            self.save_preferences()

    def get_last_menu(self) -> str:
        """Get the last menu accessed"""
        if self.preferences.remember_last_menu:
            return self.preferences.last_menu_path
        return "main"

    def reset_to_defaults(self) -> None:
        """Reset all preferences to defaults"""
        self.preferences = MenuPreferences()
        self.save_preferences()

    def export_preferences(self, file_path: Path) -> bool:
        """Export preferences to a file"""
        try:
            prefs_dict = asdict(self.preferences)
            if isinstance(prefs_dict['theme'], MenuTheme):
                prefs_dict['theme'] = prefs_dict['theme'].value

            with open(file_path, 'w') as f:
                json.dump(prefs_dict, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to export preferences: {e}")
            return False

    def import_preferences(self, file_path: Path) -> bool:
        """Import preferences from a file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'theme' in data:
                    data['theme'] = MenuTheme(data['theme'])
                self.preferences = MenuPreferences(**data)
            self.save_preferences()
            return True
        except Exception as e:
            print(f"Failed to import preferences: {e}")
            return False


class MenuStateManager:
    """Manages current menu state during runtime"""

    def __init__(self) -> None:
        """Initialize state manager"""
        self.menu_stack: list = []
        self.current_menu = "main"
        self.search_query = ""
        self.filtered_items = []
        self.selected_index = 0

    def push_menu(self, menu_name: str) -> None:
        """Push menu onto stack for breadcrumb navigation"""
        self.menu_stack.append(self.current_menu)
        self.current_menu = menu_name
        self.selected_index = 0

    def pop_menu(self) -> Optional[str]:
        """Pop menu from stack"""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            self.selected_index = 0
            return self.current_menu
        return None

    def get_breadcrumb(self) -> str:
        """Get breadcrumb navigation string"""
        breadcrumb_path = ["SampleMind"] + self.menu_stack + [self.current_menu]
        return " > ".join(breadcrumb_path)

    def set_search_query(self, query: str) -> None:
        """Set search query for menu filtering"""
        self.search_query = query.lower()
        self.selected_index = 0

    def clear_search(self) -> None:
        """Clear search query"""
        self.search_query = ""
        self.filtered_items = []
        self.selected_index = 0

    def filter_items(self, items: list, query: str) -> list:
        """Filter menu items based on search query"""
        if not query:
            return items

        filtered = []
        for item in items:
            if (query in item.label.lower() or
                query in item.description.lower() or
                (item.help_text and query in item.help_text.lower())):
                filtered.append(item)

        return filtered

    def move_selection_up(self, items_count: int) -> None:
        """Move selection up (with wraparound)"""
        self.selected_index = (self.selected_index - 1) % items_count

    def move_selection_down(self, items_count: int) -> None:
        """Move selection down (with wraparound)"""
        self.selected_index = (self.selected_index + 1) % items_count

    def get_selected_index(self) -> int:
        """Get current selection index"""
        return self.selected_index

    def reset(self) -> None:
        """Reset state to initial values"""
        self.menu_stack = []
        self.current_menu = "main"
        self.search_query = ""
        self.filtered_items = []
        self.selected_index = 0


# Global instances
config_manager = MenuConfigManager()
state_manager = MenuStateManager()
