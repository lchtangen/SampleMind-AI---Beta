"""User settings repository"""

from typing import Optional, Dict, Any
from samplemind.core.database.mongo import UserSettings


class SettingsRepository:
    """Repository for user settings CRUD operations"""

    # Default settings template
    DEFAULT_SETTINGS = {
        "default_analysis_level": "STANDARD",
        "auto_save_results": False,
        "cache_enabled": True,
        "export_format": "JSON",
        "theme": "dark",
        "show_advanced_stats": False,
        "max_cache_size": 100,
        "batch_parallel_workers": 4,
        "show_waveform": True,
        "waveform_height": 10,
        "auto_preview": False,
    }

    @staticmethod
    async def get_or_create(user_id: Optional[str] = None) -> UserSettings:
        """Get or create default settings for user"""
        existing = await UserSettings.find_one(UserSettings.user_id == user_id)
        if existing:
            return existing

        settings = UserSettings(
            settings_id=f"settings_{user_id or 'default'}",
            user_id=user_id,
            **SettingsRepository.DEFAULT_SETTINGS,
        )
        await settings.insert()
        return settings

    @staticmethod
    async def get(user_id: Optional[str] = None) -> Optional[UserSettings]:
        """Get user settings"""
        return await UserSettings.find_one(UserSettings.user_id == user_id)

    @staticmethod
    async def update(user_id: Optional[str], **kwargs) -> UserSettings:
        """Update user settings"""
        settings = await SettingsRepository.get_or_create(user_id)

        # Update only provided fields
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        await settings.save()
        return settings

    @staticmethod
    async def update_analysis_level(
        user_id: Optional[str], level: str
    ) -> UserSettings:
        """Update default analysis level"""
        return await SettingsRepository.update(user_id, default_analysis_level=level)

    @staticmethod
    async def update_theme(user_id: Optional[str], theme: str) -> UserSettings:
        """Update theme preference"""
        return await SettingsRepository.update(user_id, theme=theme)

    @staticmethod
    async def update_export_format(
        user_id: Optional[str], format_type: str
    ) -> UserSettings:
        """Update default export format"""
        return await SettingsRepository.update(user_id, export_format=format_type)

    @staticmethod
    async def toggle_cache(user_id: Optional[str]) -> UserSettings:
        """Toggle cache enabled/disabled"""
        settings = await SettingsRepository.get_or_create(user_id)
        return await SettingsRepository.update(
            user_id, cache_enabled=not settings.cache_enabled
        )

    @staticmethod
    async def toggle_auto_save(user_id: Optional[str]) -> UserSettings:
        """Toggle auto-save results"""
        settings = await SettingsRepository.get_or_create(user_id)
        return await SettingsRepository.update(
            user_id, auto_save_results=not settings.auto_save_results
        )

    @staticmethod
    async def set_cache_size(user_id: Optional[str], size: int) -> UserSettings:
        """Set max cache size"""
        if size < 10 or size > 1000:
            raise ValueError("Cache size must be between 10 and 1000")
        return await SettingsRepository.update(user_id, max_cache_size=size)

    @staticmethod
    async def set_parallel_workers(user_id: Optional[str], workers: int) -> UserSettings:
        """Set batch parallel workers"""
        if workers < 1 or workers > 32:
            raise ValueError("Parallel workers must be between 1 and 32")
        return await SettingsRepository.update(user_id, batch_parallel_workers=workers)

    @staticmethod
    async def reset_to_defaults(user_id: Optional[str]) -> UserSettings:
        """Reset all settings to defaults"""
        settings = await SettingsRepository.get_or_create(user_id)
        for key, value in SettingsRepository.DEFAULT_SETTINGS.items():
            setattr(settings, key, value)
        await settings.save()
        return settings

    @staticmethod
    async def export_settings(user_id: Optional[str]) -> Dict[str, Any]:
        """Export settings as dictionary"""
        settings = await SettingsRepository.get_or_create(user_id)
        return {
            "default_analysis_level": settings.default_analysis_level,
            "auto_save_results": settings.auto_save_results,
            "cache_enabled": settings.cache_enabled,
            "export_format": settings.export_format,
            "export_path": settings.export_path,
            "theme": settings.theme,
            "show_advanced_stats": settings.show_advanced_stats,
            "max_cache_size": settings.max_cache_size,
            "batch_parallel_workers": settings.batch_parallel_workers,
            "show_waveform": settings.show_waveform,
            "waveform_height": settings.waveform_height,
            "auto_preview": settings.auto_preview,
        }

    @staticmethod
    async def delete(user_id: Optional[str]) -> bool:
        """Delete user settings"""
        settings = await UserSettings.find_one(UserSettings.user_id == user_id)
        if settings:
            await settings.delete()
            return True
        return False
