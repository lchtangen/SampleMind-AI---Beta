"""TUI Database integration - High-level interface for TUI screens"""

import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from samplemind.core.database.mongo import Analysis, Favorite, UserSettings
from samplemind.core.database.repositories.analysis_repository import (
    AnalysisRepository,
)
from samplemind.core.database.repositories.favorite_repository import (
    FavoriteRepository,
)
from samplemind.core.database.repositories.settings_repository import (
    SettingsRepository,
)

logger = logging.getLogger(__name__)


class TUIDatabase:
    """High-level database interface for TUI screens"""

    def __init__(self, user_id: Optional[str] = None) -> None:
        """Initialize TUI database with optional user ID"""
        self.user_id = user_id or "default_user"
        self._settings: Optional[UserSettings] = None

    async def initialize(self) -> None:
        """Initialize database connection and settings"""
        try:
            # Load or create user settings
            self._settings = await SettingsRepository.get_or_create(self.user_id)
            logger.info(f"✅ TUI Database initialized for user: {self.user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize TUI Database: {e}")
            raise

    # ============================================================================
    # ANALYSIS OPERATIONS
    # ============================================================================

    async def save_analysis_result(
        self,
        file_path: str,
        features: Dict[str, Any],
        analysis_level: str = "STANDARD",
        processing_time: float = 0.0,
        ai_summary: Optional[str] = None,
        production_tips: Optional[List[str]] = None,
        spectral_features: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save analysis result to database and return analysis_id"""
        try:
            analysis_id = str(uuid.uuid4())
            file_id = f"{file_path}_{analysis_level}"

            # Extract features (assuming AudioFeatures object or dict)
            tempo = features.get("tempo", 0.0) if isinstance(features, dict) else features.tempo
            key = features.get("key", "Unknown") if isinstance(features, dict) else features.key
            mode = features.get("mode", "Unknown") if isinstance(features, dict) else features.mode
            time_signature = (
                features.get("time_signature", [4, 4])
                if isinstance(features, dict)
                else features.time_signature
            )
            duration = (
                features.get("duration", 0.0)
                if isinstance(features, dict)
                else features.duration
            )

            analysis = await AnalysisRepository.create(
                analysis_id=analysis_id,
                file_id=file_id,
                tempo=tempo,
                key=key,
                mode=mode,
                time_signature=time_signature,
                duration=duration,
                analysis_level=analysis_level,
                processing_time=processing_time,
                user_id=self.user_id,
                ai_summary=ai_summary,
                production_tips=production_tips or [],
                spectral_features=spectral_features,
            )

            logger.info(
                f"✅ Saved analysis result: {file_path} (ID: {analysis_id})"
            )
            return analysis_id

        except Exception as e:
            logger.error(f"❌ Failed to save analysis result: {e}")
            raise

    async def get_analysis_result(self, analysis_id: str) -> Optional[Analysis]:
        """Retrieve analysis result by ID"""
        try:
            return await AnalysisRepository.get_by_id(analysis_id)
        except Exception as e:
            logger.error(f"❌ Failed to retrieve analysis: {e}")
            return None

    async def get_recent_analyses(self, limit: int = 10) -> List[Analysis]:
        """Get recently analyzed files"""
        try:
            # Get recent analyses by user (would need to extend repo)
            return await AnalysisRepository.get_by_user(
                self.user_id, skip=0, limit=limit
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve recent analyses: {e}")
            return []

    # ============================================================================
    # FAVORITE OPERATIONS
    # ============================================================================

    async def add_favorite(
        self, analysis_id: str, file_name: str, notes: Optional[str] = None
    ) -> str:
        """Add analysis to favorites and return favorite_id"""
        try:
            favorite_id = str(uuid.uuid4())
            favorite = await FavoriteRepository.create(
                favorite_id=favorite_id,
                analysis_id=analysis_id,
                file_name=file_name,
                user_id=self.user_id,
                notes=notes,
            )
            logger.info(f"⭐ Added favorite: {file_name} (ID: {favorite_id})")
            return favorite_id
        except Exception as e:
            logger.error(f"❌ Failed to add favorite: {e}")
            raise

    async def remove_favorite(self, favorite_id: str) -> bool:
        """Remove favorite"""
        try:
            success = await FavoriteRepository.delete(favorite_id)
            if success:
                logger.info(f"⭐ Removed favorite: {favorite_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to remove favorite: {e}")
            return False

    async def get_favorite_by_analysis_id(self, analysis_id: str) -> Optional[Favorite]:
        """Check if analysis is favorited"""
        try:
            return await FavoriteRepository.get_by_analysis_id(analysis_id)
        except Exception as e:
            logger.error(f"❌ Failed to check favorite status: {e}")
            return None

    async def get_all_favorites(self, limit: int = 50) -> List[Favorite]:
        """Get all favorites for user"""
        try:
            return await FavoriteRepository.get_by_user(
                self.user_id, skip=0, limit=limit
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve favorites: {e}")
            return []

    async def get_rated_favorites(self, min_rating: int = 3) -> List[Favorite]:
        """Get favorites with minimum rating"""
        try:
            return await FavoriteRepository.get_by_rating(self.user_id, min_rating)
        except Exception as e:
            logger.error(f"❌ Failed to retrieve rated favorites: {e}")
            return []

    async def get_recent_favorites(self, limit: int = 10) -> List[Favorite]:
        """Get recently added favorites"""
        try:
            return await FavoriteRepository.get_recent(self.user_id, limit)
        except Exception as e:
            logger.error(f"❌ Failed to retrieve recent favorites: {e}")
            return []

    async def update_favorite_rating(self, favorite_id: str, rating: int) -> bool:
        """Update favorite rating (0-5)"""
        try:
            result = await FavoriteRepository.update_rating(favorite_id, rating)
            if result:
                logger.info(f"⭐ Updated favorite rating: {favorite_id} → {rating}")
            return result is not None
        except Exception as e:
            logger.error(f"❌ Failed to update rating: {e}")
            return False

    async def count_favorites(self) -> int:
        """Get count of favorites for user"""
        try:
            return await FavoriteRepository.count_by_user(self.user_id)
        except Exception as e:
            logger.error(f"❌ Failed to count favorites: {e}")
            return 0

    # ============================================================================
    # SETTINGS OPERATIONS
    # ============================================================================

    async def get_settings(self) -> UserSettings:
        """Get user settings"""
        try:
            if self._settings is None:
                self._settings = await SettingsRepository.get_or_create(self.user_id)
            return self._settings
        except Exception as e:
            logger.error(f"❌ Failed to retrieve settings: {e}")
            raise

    async def update_setting(self, key: str, value: Any) -> bool:
        """Update a specific setting"""
        try:
            settings = await SettingsRepository.update(self.user_id, **{key: value})
            self._settings = settings
            logger.info(f"✅ Updated setting: {key} → {value}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update setting: {e}")
            return False

    async def update_analysis_level(self, level: str) -> bool:
        """Update default analysis level"""
        try:
            self._settings = await SettingsRepository.update_analysis_level(
                self.user_id, level
            )
            logger.info(f"✅ Updated analysis level: {level}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update analysis level: {e}")
            return False

    async def update_theme(self, theme: str) -> bool:
        """Update theme preference"""
        try:
            self._settings = await SettingsRepository.update_theme(
                self.user_id, theme
            )
            logger.info(f"✅ Updated theme: {theme}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update theme: {e}")
            return False

    async def update_export_format(self, format_type: str) -> bool:
        """Update default export format"""
        try:
            self._settings = await SettingsRepository.update_export_format(
                self.user_id, format_type
            )
            logger.info(f"✅ Updated export format: {format_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update export format: {e}")
            return False

    async def export_settings(self) -> Dict[str, Any]:
        """Export all settings as dictionary"""
        try:
            return await SettingsRepository.export_settings(self.user_id)
        except Exception as e:
            logger.error(f"❌ Failed to export settings: {e}")
            return {}

    async def reset_settings_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self._settings = await SettingsRepository.reset_to_defaults(
                self.user_id
            )
            logger.info("✅ Reset settings to defaults")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to reset settings: {e}")
            return False

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    async def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of session data (analyses, favorites, etc.)"""
        try:
            recent_analyses = await self.get_recent_analyses(limit=5)
            favorites = await self.get_all_favorites(limit=5)
            favorites_count = await self.count_favorites()
            settings = await self.get_settings()

            return {
                "user_id": self.user_id,
                "recent_analyses": len(recent_analyses),
                "favorites_count": favorites_count,
                "analysis_level": settings.default_analysis_level,
                "theme": settings.theme,
                "cache_enabled": settings.cache_enabled,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get session summary: {e}")
            return {}

    async def search_by_tags(self, tags: List[str]) -> List[Analysis]:
        """Search analyses by tags (future enhancement)"""
        # This would be implemented when Analysis model includes tags
        # For now, return empty list as placeholder
        logger.info(f"🔍 Searching by tags: {tags}")
        return []

    async def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about user's analyses"""
        try:
            analyses = await self.get_recent_analyses(limit=1000)

            if not analyses:
                return {
                    "total_analyses": 0,
                    "average_tempo": 0.0,
                    "common_keys": [],
                    "average_duration": 0.0,
                }

            tempos = [a.tempo for a in analyses]
            keys = [a.key for a in analyses]
            durations = [a.duration for a in analyses]

            avg_tempo = sum(tempos) / len(tempos) if tempos else 0
            avg_duration = sum(durations) / len(durations) if durations else 0

            # Find most common keys
            key_counts = {}
            for key in keys:
                key_counts[key] = key_counts.get(key, 0) + 1
            common_keys = sorted(
                key_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]

            return {
                "total_analyses": len(analyses),
                "average_tempo": round(avg_tempo, 1),
                "common_keys": [k[0] for k in common_keys],
                "average_duration": round(avg_duration, 2),
            }
        except Exception as e:
            logger.error(f"❌ Failed to get analysis stats: {e}")
            return {}


# Global singleton instance
_tui_database: Optional[TUIDatabase] = None


def get_tui_database(user_id: Optional[str] = None) -> TUIDatabase:
    """Get or create TUI database singleton"""
    global _tui_database
    if _tui_database is None:
        _tui_database = TUIDatabase(user_id)
    return _tui_database


async def initialize_tui_database(user_id: Optional[str] = None) -> TUIDatabase:
    """Initialize TUI database singleton"""
    global _tui_database
    _tui_database = TUIDatabase(user_id)
    await _tui_database.initialize()
    return _tui_database
