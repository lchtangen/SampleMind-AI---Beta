"""
Example Plugin for SampleMind TUI
Demonstrates basic plugin structure and hooks
"""

import logging
from typing import Dict, Any

from samplemind.interfaces.tui.plugins.plugin_base import (
    TUIPlugin,
    PluginMetadata,
    PluginHook,
)

logger = logging.getLogger(__name__)


class ExamplePlugin(TUIPlugin):
    """Example plugin demonstrating plugin architecture"""

    METADATA = PluginMetadata(
        name="Example Plugin",
        version="1.0.0",
        author="SampleMind Team",
        description="Example plugin showing basic plugin structure and hooks",
        url="https://github.com/samplemind/samplemind",
        dependencies=[],
        supported_hooks=[
            PluginHook.AFTER_ANALYSIS,
            PluginHook.ON_SETTINGS_CHANGE,
        ],
    )

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.analysis_count = 0
        self.settings_changes = 0

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        logger.info(f"Initializing {self.metadata.name}")
        self.config = config
        return True

    def shutdown(self) -> None:
        """Shutdown the plugin"""
        logger.info(f"Shutting down {self.metadata.name}")
        logger.info(f"Plugin processed {self.analysis_count} analyses")

    def get_version(self) -> str:
        """Get plugin version"""
        return self.metadata.version

    def on_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Handle hook call"""
        if hook_name == PluginHook.AFTER_ANALYSIS.value:
            return self._on_after_analysis(*args, **kwargs)
        elif hook_name == PluginHook.ON_SETTINGS_CHANGE.value:
            return self._on_settings_change(*args, **kwargs)

        return None

    def _on_after_analysis(self, *args, **kwargs) -> None:
        """Handle after analysis hook"""
        self.analysis_count += 1
        analysis_result = kwargs.get("result", {})
        logger.debug(
            f"Example plugin: Analysis #{self.analysis_count} complete. "
            f"Result: {analysis_result}"
        )

    def _on_settings_change(self, *args, **kwargs) -> None:
        """Handle settings change hook"""
        self.settings_changes += 1
        setting_name = kwargs.get("setting", "unknown")
        new_value = kwargs.get("value", None)
        logger.debug(
            f"Example plugin: Settings changed (#{self.settings_changes}). "
            f"Setting: {setting_name} = {new_value}"
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {
            "enabled": {"type": "boolean", "default": True},
            "log_level": {
                "type": "string",
                "default": "info",
                "enum": ["debug", "info", "warning", "error"],
            },
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        if "log_level" in config:
            valid_levels = ["debug", "info", "warning", "error"]
            if config["log_level"] not in valid_levels:
                return False

        return True
