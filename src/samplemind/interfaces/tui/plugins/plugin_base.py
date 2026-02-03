"""
Plugin Architecture Foundation for SampleMind TUI
Base classes and interfaces for plugin development
"""

import logging
from typing import Optional, Dict, Any, Callable, List, Set
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class PluginHook(Enum):
    """Available plugin hooks"""
    # Analysis hooks
    BEFORE_ANALYSIS = "before_analysis"
    AFTER_ANALYSIS = "after_analysis"
    ON_ANALYSIS_ERROR = "on_analysis_error"

    # Tagging hooks
    BEFORE_TAG = "before_tag"
    AFTER_TAG = "after_tag"

    # Export hooks
    BEFORE_EXPORT = "before_export"
    AFTER_EXPORT = "after_export"

    # UI hooks
    ON_APP_STARTUP = "on_app_startup"
    ON_APP_SHUTDOWN = "on_app_shutdown"
    ON_SCREEN_CHANGE = "on_screen_change"

    # Settings hooks
    ON_SETTINGS_CHANGE = "on_settings_change"

    # Custom user hooks
    CUSTOM = "custom"


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    author: str
    description: str
    url: Optional[str] = None
    dependencies: List[str] = None
    supported_hooks: List[PluginHook] = None

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []
        if self.supported_hooks is None:
            self.supported_hooks = []


class TUIPlugin(ABC):
    """Base class for TUI plugins"""

    def __init__(self, metadata: PluginMetadata) -> None:
        """
        Initialize plugin

        Args:
            metadata: Plugin metadata
        """
        self.metadata = metadata
        self.enabled = False
        self.config: Dict[str, Any] = {}

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin

        Args:
            config: Plugin configuration

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin"""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version"""
        pass

    @abstractmethod
    def on_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """
        Handle hook call

        Args:
            hook_name: Name of hook
            *args: Hook arguments
            **kwargs: Hook keyword arguments

        Returns:
            Hook return value (optional)
        """
        pass

    def validate_dependencies(self) -> bool:
        """Validate plugin dependencies are available"""
        return True

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {}

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        return True


class HookHandler:
    """Single hook handler"""

    def __init__(
        self,
        hook_name: str,
        callback: Callable,
        priority: int = 0,
        is_async: bool = False,
    ):
        """
        Initialize hook handler

        Args:
            hook_name: Name of hook
            callback: Callback function
            priority: Handler priority (higher = earlier execution)
            is_async: Whether handler is async
        """
        self.hook_name = hook_name
        self.callback = callback
        self.priority = priority
        self.is_async = is_async
        self.enabled = True

    def __call__(self, *args, **kwargs) -> None:
        """Call the handler"""
        if self.enabled:
            return self.callback(*args, **kwargs)
        return None


class HookSystem:
    """Plugin hook system"""

    def __init__(self) -> None:
        """Initialize hook system"""
        self.hooks: Dict[str, List[HookHandler]] = {}
        self.hook_history: List[Dict[str, Any]] = []

    def register_hook(
        self,
        hook_name: str,
        callback: Callable,
        priority: int = 0,
        is_async: bool = False,
    ) -> HookHandler:
        """
        Register a hook handler

        Args:
            hook_name: Name of hook
            callback: Callback function
            priority: Handler priority
            is_async: Whether async

        Returns:
            HookHandler instance
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []

        handler = HookHandler(hook_name, callback, priority, is_async)
        self.hooks[hook_name].append(handler)

        # Sort by priority
        self.hooks[hook_name].sort(key=lambda h: h.priority, reverse=True)

        logger.debug(f"Registered hook handler for {hook_name}")
        return handler

    def unregister_hook(self, hook_name: str, callback: Callable) -> bool:
        """
        Unregister a hook handler

        Args:
            hook_name: Name of hook
            callback: Callback function

        Returns:
            True if found and removed
        """
        if hook_name in self.hooks:
            original_len = len(self.hooks[hook_name])
            self.hooks[hook_name] = [
                h for h in self.hooks[hook_name] if h.callback != callback
            ]
            if len(self.hooks[hook_name]) < original_len:
                logger.debug(f"Unregistered hook handler for {hook_name}")
                return True

        return False

    def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Call all handlers for a hook

        Args:
            hook_name: Name of hook
            *args: Hook arguments
            **kwargs: Hook keyword arguments

        Returns:
            List of return values from handlers
        """
        if hook_name not in self.hooks:
            return []

        results = []
        for handler in self.hooks[hook_name]:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error calling hook {hook_name}: {e}")

        # Record in history
        self.hook_history.append(
            {
                "hook": hook_name,
                "handlers": len(self.hooks.get(hook_name, [])),
                "results": len(results),
            }
        )

        return results

    def get_hook_handlers(self, hook_name: str) -> List[HookHandler]:
        """Get all handlers for a hook"""
        return self.hooks.get(hook_name, [])

    def get_available_hooks(self) -> List[str]:
        """Get list of available hooks"""
        return list(self.hooks.keys())

    def clear_hooks(self, hook_name: Optional[str] = None) -> None:
        """
        Clear hook handlers

        Args:
            hook_name: Specific hook to clear (all if None)
        """
        if hook_name:
            self.hooks[hook_name] = []
        else:
            self.hooks.clear()


# Global hook system instance
_hook_system: Optional[HookSystem] = None


def get_hook_system() -> HookSystem:
    """Get or create global hook system"""
    global _hook_system
    if _hook_system is None:
        _hook_system = HookSystem()
    return _hook_system
