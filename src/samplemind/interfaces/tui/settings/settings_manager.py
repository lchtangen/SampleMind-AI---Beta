"""Settings management for TUI"""

import logging
from typing import Optional, Dict, Any, List

from samplemind.core.database.repositories.settings_repository import (
    SettingsRepository,
)

logger = logging.getLogger(__name__)


class SettingsManager:
    """High-level settings management interface for TUI screens"""

    # Available analysis levels
    ANALYSIS_LEVELS = ["BASIC", "STANDARD", "DETAILED", "PROFESSIONAL"]

    # Available themes
    THEMES = ["dark", "light", "cyberpunk", "synthwave", "gruvbox", "dracula", "nord", "monokai"]

    # Available export formats
    EXPORT_FORMATS = ["JSON", "CSV", "YAML", "Markdown"]

    def __init__(self, user_id: Optional[str] = None):
        """Initialize settings manager"""
        self.user_id = user_id or "default_user"

    async def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        try:
            return await SettingsRepository.export_settings(self.user_id)
        except Exception as e:
            logger.error(f"❌ Failed to get settings: {e}")
            return {}

    async def get_setting(self, key: str) -> Any:
        """Get specific setting value"""
        try:
            settings = await SettingsRepository.get_or_create(self.user_id)
            if hasattr(settings, key):
                return getattr(settings, key)
            logger.warning(f"Unknown setting: {key}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get setting {key}: {e}")
            return None

    async def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting"""
        try:
            await SettingsRepository.update(self.user_id, **{key: value})
            logger.info(f"✅ Updated setting: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set setting {key}: {e}")
            return False

    # ============================================================================
    # ANALYSIS LEVEL
    # ============================================================================

    async def get_default_analysis_level(self) -> str:
        """Get default analysis level"""
        try:
            return await self.get_setting("default_analysis_level")
        except Exception as e:
            logger.error(f"❌ Failed to get analysis level: {e}")
            return "STANDARD"

    async def set_default_analysis_level(self, level: str) -> bool:
        """Set default analysis level"""
        if level not in self.ANALYSIS_LEVELS:
            logger.warning(f"Invalid analysis level: {level}")
            return False
        try:
            await SettingsRepository.update_analysis_level(self.user_id, level)
            logger.info(f"✅ Analysis level set to: {level}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set analysis level: {e}")
            return False

    # ============================================================================
    # THEME
    # ============================================================================

    async def get_theme(self) -> str:
        """Get current theme"""
        try:
            return await self.get_setting("theme")
        except Exception as e:
            logger.error(f"❌ Failed to get theme: {e}")
            return "dark"

    async def set_theme(self, theme: str) -> bool:
        """Set theme"""
        if theme not in self.THEMES:
            logger.warning(f"Invalid theme: {theme}")
            return False
        try:
            await SettingsRepository.update_theme(self.user_id, theme)
            logger.info(f"✅ Theme set to: {theme}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set theme: {e}")
            return False

    # ============================================================================
    # EXPORT FORMAT
    # ============================================================================

    async def get_export_format(self) -> str:
        """Get default export format"""
        try:
            return await self.get_setting("export_format")
        except Exception as e:
            logger.error(f"❌ Failed to get export format: {e}")
            return "JSON"

    async def set_export_format(self, format_type: str) -> bool:
        """Set export format"""
        if format_type not in self.EXPORT_FORMATS:
            logger.warning(f"Invalid export format: {format_type}")
            return False
        try:
            await SettingsRepository.update_export_format(self.user_id, format_type)
            logger.info(f"✅ Export format set to: {format_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set export format: {e}")
            return False

    # ============================================================================
    # CACHE SETTINGS
    # ============================================================================

    async def is_cache_enabled(self) -> bool:
        """Check if caching is enabled"""
        try:
            return await self.get_setting("cache_enabled")
        except Exception as e:
            logger.error(f"❌ Failed to check cache status: {e}")
            return True

    async def toggle_cache(self) -> bool:
        """Toggle cache enabled/disabled"""
        try:
            await SettingsRepository.toggle_cache(self.user_id)
            logger.info("✅ Cache toggled")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to toggle cache: {e}")
            return False

    async def get_cache_size(self) -> int:
        """Get max cache size"""
        try:
            return await self.get_setting("max_cache_size")
        except Exception as e:
            logger.error(f"❌ Failed to get cache size: {e}")
            return 100

    async def set_cache_size(self, size: int) -> bool:
        """Set max cache size"""
        try:
            await SettingsRepository.set_cache_size(self.user_id, size)
            logger.info(f"✅ Cache size set to: {size}")
            return True
        except ValueError as e:
            logger.warning(f"Invalid cache size: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to set cache size: {e}")
            return False

    # ============================================================================
    # BATCH PROCESSING
    # ============================================================================

    async def get_parallel_workers(self) -> int:
        """Get number of parallel workers"""
        try:
            return await self.get_setting("batch_parallel_workers")
        except Exception as e:
            logger.error(f"❌ Failed to get parallel workers: {e}")
            return 4

    async def set_parallel_workers(self, workers: int) -> bool:
        """Set number of parallel workers"""
        try:
            await SettingsRepository.set_parallel_workers(self.user_id, workers)
            logger.info(f"✅ Parallel workers set to: {workers}")
            return True
        except ValueError as e:
            logger.warning(f"Invalid worker count: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to set parallel workers: {e}")
            return False

    async def is_auto_save_enabled(self) -> bool:
        """Check if auto-save results is enabled"""
        try:
            return await self.get_setting("auto_save_results")
        except Exception as e:
            logger.error(f"❌ Failed to check auto-save status: {e}")
            return False

    async def toggle_auto_save(self) -> bool:
        """Toggle auto-save results"""
        try:
            await SettingsRepository.toggle_auto_save(self.user_id)
            logger.info("✅ Auto-save toggled")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to toggle auto-save: {e}")
            return False

    # ============================================================================
    # DISPLAY SETTINGS
    # ============================================================================

    async def show_advanced_stats(self) -> bool:
        """Check if advanced stats should be shown"""
        try:
            return await self.get_setting("show_advanced_stats")
        except Exception as e:
            logger.error(f"❌ Failed to check advanced stats setting: {e}")
            return False

    async def toggle_advanced_stats(self) -> bool:
        """Toggle advanced stats display"""
        try:
            current = await self.show_advanced_stats()
            await self.set_setting("show_advanced_stats", not current)
            logger.info("✅ Advanced stats display toggled")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to toggle advanced stats: {e}")
            return False

    async def show_waveform(self) -> bool:
        """Check if waveform should be shown"""
        try:
            return await self.get_setting("show_waveform")
        except Exception as e:
            logger.error(f"❌ Failed to check waveform setting: {e}")
            return True

    async def toggle_waveform(self) -> bool:
        """Toggle waveform display"""
        try:
            current = await self.show_waveform()
            await self.set_setting("show_waveform", not current)
            logger.info("✅ Waveform display toggled")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to toggle waveform: {e}")
            return False

    # ============================================================================
    # RESET
    # ============================================================================

    async def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            await SettingsRepository.reset_to_defaults(self.user_id)
            logger.info("✅ Settings reset to defaults")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to reset settings: {e}")
            return False

    # ============================================================================
    # VALIDATION
    # ============================================================================

    def get_available_analysis_levels(self) -> List[str]:
        """Get list of available analysis levels"""
        return self.ANALYSIS_LEVELS.copy()

    def get_available_themes(self) -> List[str]:
        """Get list of available themes"""
        return self.THEMES.copy()

    def get_available_export_formats(self) -> List[str]:
        """Get list of available export formats"""
        return self.EXPORT_FORMATS.copy()

    # ============================================================================
    # SETTINGS GROUPS
    # ============================================================================

    async def get_analysis_settings(self) -> Dict[str, Any]:
        """Get analysis-related settings"""
        return {
            "default_analysis_level": await self.get_default_analysis_level(),
            "cache_enabled": await self.is_cache_enabled(),
            "max_cache_size": await self.get_cache_size(),
        }

    async def get_display_settings(self) -> Dict[str, Any]:
        """Get display-related settings"""
        return {
            "theme": await self.get_theme(),
            "show_advanced_stats": await self.show_advanced_stats(),
            "show_waveform": await self.show_waveform(),
        }

    async def get_export_settings(self) -> Dict[str, Any]:
        """Get export-related settings"""
        return {
            "export_format": await self.get_export_format(),
        }

    async def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance-related settings"""
        return {
            "batch_parallel_workers": await self.get_parallel_workers(),
            "cache_enabled": await self.is_cache_enabled(),
            "max_cache_size": await self.get_cache_size(),
        }


# Global singleton instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager(user_id: Optional[str] = None) -> SettingsManager:
    """Get or create settings manager singleton"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager(user_id)
    return _settings_manager
