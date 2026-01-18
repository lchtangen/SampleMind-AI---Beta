"""TUI Plugins module - Plugin architecture and management"""

from samplemind.interfaces.tui.plugins.plugin_base import (
    TUIPlugin,
    PluginMetadata,
    PluginHook,
    HookHandler,
    HookSystem,
    get_hook_system,
)
from samplemind.interfaces.tui.plugins.plugin_manager import (
    PluginManager,
    get_plugin_manager,
)

__all__ = [
    "TUIPlugin",
    "PluginMetadata",
    "PluginHook",
    "HookHandler",
    "HookSystem",
    "get_hook_system",
    "PluginManager",
    "get_plugin_manager",
]
