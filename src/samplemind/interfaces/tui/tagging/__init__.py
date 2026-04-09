"""TUI Tagging module - Comprehensive tagging system with categories"""

from samplemind.interfaces.tui.tagging.tagging_system import (
    TAG_CATEGORIES,
    Tag,
    TagCategory,
    TaggingProfile,
    TaggingSystem,
    get_tagging_system,
)

__all__ = [
    "TaggingSystem",
    "Tag",
    "TaggingProfile",
    "TagCategory",
    "TAG_CATEGORIES",
    "get_tagging_system",
]
