"""
Plugin Manager for SampleMind TUI
Handles plugin discovery, loading, and lifecycle management
"""

import logging
import sys
import importlib.util
from typing import Optional, Dict, List, Any
from pathlib import Path

from .plugin_base import TUIPlugin, PluginMetadata, get_hook_system

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugin discovery and lifecycle"""

    def __init__(self, plugin_dir: Optional[str] = None):
        """
        Initialize plugin manager

        Args:
            plugin_dir: Directory to scan for plugins
        """
        if plugin_dir is None:
            # Use default plugins directory
            plugin_dir = str(Path(__file__).parent / "plugins")

        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, TUIPlugin] = {}
        self.loaded_modules: Dict[str, Any] = {}
        self.hook_system = get_hook_system()

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins

        Returns:
            List of plugin names
        """
        discovered = []

        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory does not exist: {self.plugin_dir}")
            return []

        for plugin_path in self.plugin_dir.glob("**/*.py"):
            if plugin_path.name.startswith("_"):
                continue

            plugin_name = plugin_path.stem
            discovered.append(plugin_name)
            logger.debug(f"Discovered plugin: {plugin_name}")

        return discovered

    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Load a plugin

        Args:
            plugin_name: Name of plugin to load
            config: Plugin configuration

        Returns:
            True if loaded successfully
        """
        if plugin_name in self.plugins:
            logger.warning(f"Plugin already loaded: {plugin_name}")
            return False

        try:
            # Find plugin file
            plugin_path = self._find_plugin_file(plugin_name)
            if not plugin_path:
                logger.error(f"Plugin not found: {plugin_name}")
                return False

            # Load module
            module = self._load_module_from_file(plugin_name, plugin_path)
            if not module:
                return False

            self.loaded_modules[plugin_name] = module

            # Find plugin class (should be TUIPlugin subclass)
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                logger.error(f"No TUIPlugin class found in {plugin_name}")
                return False

            # Create plugin instance
            metadata = getattr(plugin_class, "METADATA", None)
            if not metadata:
                logger.error(f"Plugin {plugin_name} missing METADATA")
                return False

            plugin = plugin_class(metadata)

            # Validate dependencies
            if not plugin.validate_dependencies():
                logger.error(f"Plugin {plugin_name} dependencies not satisfied")
                return False

            # Validate config
            if config and not plugin.validate_config(config):
                logger.error(f"Invalid configuration for plugin {plugin_name}")
                return False

            # Initialize plugin
            if not plugin.initialize(config or {}):
                logger.error(f"Failed to initialize plugin {plugin_name}")
                return False

            plugin.enabled = True
            self.plugins[plugin_name] = plugin

            logger.info(f"Loaded plugin: {plugin_name} v{plugin.get_version()}")
            return True

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            True if unloaded successfully
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False

        try:
            plugin = self.plugins[plugin_name]
            plugin.shutdown()
            del self.plugins[plugin_name]

            logger.info(f"Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False

    def reload_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Reload a plugin

        Args:
            plugin_name: Name of plugin
            config: New configuration

        Returns:
            True if reloaded successfully
        """
        self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name, config)

    def get_plugin(self, plugin_name: str) -> Optional[TUIPlugin]:
        """Get loaded plugin by name"""
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, TUIPlugin]:
        """Get all loaded plugins"""
        return self.plugins.copy()

    def get_enabled_plugins(self) -> Dict[str, TUIPlugin]:
        """Get enabled plugins"""
        return {name: p for name, p in self.plugins.items() if p.enabled}

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name not in self.plugins:
            return False

        self.plugins[plugin_name].enabled = True
        return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name not in self.plugins:
            return False

        self.plugins[plugin_name].enabled = False
        return True

    def call_plugin_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Call plugin hook

        Args:
            hook_name: Name of hook
            *args: Hook arguments
            **kwargs: Hook keyword arguments

        Returns:
            List of plugin responses
        """
        responses = []
        for plugin_name, plugin in self.get_enabled_plugins().items():
            try:
                result = plugin.on_hook(hook_name, *args, **kwargs)
                if result is not None:
                    responses.append(result)
            except Exception as e:
                logger.error(f"Error calling hook in plugin {plugin_name}: {e}")

        return responses

    def register_plugin_hook(self, plugin_name: str, hook_name: str) -> None:
        """
        Register a plugin to listen to a hook

        Args:
            plugin_name: Name of plugin
            hook_name: Name of hook
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return

        plugin = self.plugins[plugin_name]

        def plugin_hook_callback(*args, **kwargs):
            return plugin.on_hook(hook_name, *args, **kwargs)

        self.hook_system.register_hook(hook_name, plugin_hook_callback)

    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all plugins"""
        status = {}
        for name, plugin in self.plugins.items():
            status[name] = {
                "name": plugin.metadata.name,
                "version": plugin.get_version(),
                "author": plugin.metadata.author,
                "enabled": plugin.enabled,
                "description": plugin.metadata.description,
            }

        return status

    def _find_plugin_file(self, plugin_name: str) -> Optional[Path]:
        """Find plugin file"""
        # Try .py file
        py_file = self.plugin_dir / f"{plugin_name}.py"
        if py_file.exists():
            return py_file

        # Try package
        pkg_dir = self.plugin_dir / plugin_name / "__init__.py"
        if pkg_dir.exists():
            return pkg_dir

        return None

    def _load_module_from_file(self, module_name: str, file_path: Path) -> Optional[Any]:
        """Load Python module from file"""
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                logger.error(f"Could not create spec for {module_name}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            return module

        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            return None

    def _find_plugin_class(self, module: Any) -> Optional[type]:
        """Find TUIPlugin subclass in module"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, TUIPlugin) and attr != TUIPlugin:
                return attr

        return None


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager(plugin_dir: Optional[str] = None) -> PluginManager:
    """Get or create plugin manager singleton"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugin_dir)
    return _plugin_manager
