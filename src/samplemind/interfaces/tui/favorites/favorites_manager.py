"""Favorites management for TUI"""

import logging
import uuid
from typing import Optional, List, Dict, Any

from samplemind.core.database.repositories.favorite_repository import (
    FavoriteRepository,
)
from samplemind.core.database.mongo import Favorite

logger = logging.getLogger(__name__)


class FavoritesManager:
    """High-level favorites management interface for TUI screens"""

    def __init__(self, user_id: Optional[str] = None) -> None:
        """Initialize favorites manager"""
        self.user_id = user_id or "default_user"

    async def add_to_favorites(
        self, analysis_id: str, file_name: str, notes: Optional[str] = None
    ) -> Optional[str]:
        """Add analysis to favorites"""
        try:
            favorite_id = str(uuid.uuid4())
            favorite = await FavoriteRepository.create(
                favorite_id=favorite_id,
                analysis_id=analysis_id,
                file_name=file_name,
                user_id=self.user_id,
                notes=notes,
            )
            logger.info(f"⭐ Added to favorites: {file_name}")
            return favorite_id
        except Exception as e:
            logger.error(f"❌ Failed to add favorite: {e}")
            return None

    async def remove_from_favorites(self, favorite_id: str) -> bool:
        """Remove from favorites"""
        try:
            success = await FavoriteRepository.delete(favorite_id)
            if success:
                logger.info(f"⭐ Removed from favorites: {favorite_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Failed to remove favorite: {e}")
            return False

    async def is_favorite(self, analysis_id: str) -> bool:
        """Check if analysis is in favorites"""
        try:
            favorite = await FavoriteRepository.get_by_analysis_id(analysis_id)
            return favorite is not None
        except Exception as e:
            logger.error(f"❌ Failed to check favorite status: {e}")
            return False

    async def get_favorite_by_analysis_id(self, analysis_id: str) -> Optional[Favorite]:
        """Get favorite entry by analysis ID"""
        try:
            return await FavoriteRepository.get_by_analysis_id(analysis_id)
        except Exception as e:
            logger.error(f"❌ Failed to get favorite: {e}")
            return None

    async def get_all_favorites(self, limit: int = 50) -> List[Favorite]:
        """Get all favorites for user"""
        try:
            return await FavoriteRepository.get_by_user(
                self.user_id, skip=0, limit=limit
            )
        except Exception as e:
            logger.error(f"❌ Failed to get favorites: {e}")
            return []

    async def get_favorites_as_rows(
        self, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get favorites as rows for DataTable"""
        try:
            favorites = await self.get_all_favorites(limit)
            rows = []
            for idx, fav in enumerate(favorites, 1):
                rows.append({
                    "id": fav.favorite_id,
                    "index": str(idx),
                    "file_name": fav.file_name,
                    "analysis_id": fav.analysis_id[:8] + "..." if len(fav.analysis_id) > 11 else fav.analysis_id,
                    "rating": "⭐" * fav.rating if fav.rating > 0 else "Unrated",
                    "notes": fav.notes or "-",
                    "added": fav.added_at.strftime("%Y-%m-%d"),
                })
            return rows
        except Exception as e:
            logger.error(f"❌ Failed to get favorites as rows: {e}")
            return []

    async def get_recent_favorites(self, limit: int = 10) -> List[Favorite]:
        """Get recently added favorites"""
        try:
            return await FavoriteRepository.get_recent(self.user_id, limit)
        except Exception as e:
            logger.error(f"❌ Failed to get recent favorites: {e}")
            return []

    async def get_rated_favorites(self, min_rating: int = 3) -> List[Favorite]:
        """Get favorites with minimum rating"""
        try:
            return await FavoriteRepository.get_by_rating(self.user_id, min_rating)
        except Exception as e:
            logger.error(f"❌ Failed to get rated favorites: {e}")
            return []

    async def update_favorite_rating(self, favorite_id: str, rating: int) -> bool:
        """Update favorite rating (0-5 stars)"""
        try:
            if not 0 <= rating <= 5:
                logger.warning(f"Invalid rating: {rating}. Must be 0-5")
                return False

            result = await FavoriteRepository.update_rating(favorite_id, rating)
            if result:
                stars = "⭐" * rating if rating > 0 else "Unrated"
                logger.info(f"⭐ Updated rating: {favorite_id} → {stars}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to update rating: {e}")
            return False

    async def update_favorite_notes(
        self, favorite_id: str, notes: Optional[str]
    ) -> bool:
        """Update favorite notes"""
        try:
            result = await FavoriteRepository.update_notes(favorite_id, notes)
            if result:
                logger.info(f"📝 Updated notes: {favorite_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to update notes: {e}")
            return False

    async def count_favorites(self) -> int:
        """Get total count of favorites"""
        try:
            return await FavoriteRepository.count_by_user(self.user_id)
        except Exception as e:
            logger.error(f"❌ Failed to count favorites: {e}")
            return 0

    async def get_favorite_stats(self) -> Dict[str, Any]:
        """Get statistics about favorites"""
        try:
            all_favorites = await self.get_all_favorites(limit=1000)
            if not all_favorites:
                return {
                    "total": 0,
                    "rated": 0,
                    "with_notes": 0,
                    "average_rating": 0.0,
                }

            rated = sum(1 for f in all_favorites if f.rating > 0)
            with_notes = sum(1 for f in all_favorites if f.notes)
            avg_rating = sum(f.rating for f in all_favorites) / len(all_favorites)

            return {
                "total": len(all_favorites),
                "rated": rated,
                "with_notes": with_notes,
                "average_rating": round(avg_rating, 1),
            }
        except Exception as e:
            logger.error(f"❌ Failed to get favorite stats: {e}")
            return {}

    async def export_favorites(self) -> Dict[str, Any]:
        """Export all favorites as dictionary"""
        try:
            favorites = await self.get_all_favorites(limit=1000)
            stats = await self.get_favorite_stats()

            return {
                "user_id": self.user_id,
                "stats": stats,
                "favorites": [
                    {
                        "file_name": f.file_name,
                        "analysis_id": f.analysis_id,
                        "rating": f.rating,
                        "notes": f.notes,
                        "added_date": f.added_at.isoformat(),
                    }
                    for f in favorites
                ],
            }
        except Exception as e:
            logger.error(f"❌ Failed to export favorites: {e}")
            return {}

    async def toggle_favorite(
        self, analysis_id: str, file_name: str, notes: Optional[str] = None
    ) -> bool:
        """Toggle favorite status (add if not favorited, remove if favorited)"""
        try:
            existing = await self.get_favorite_by_analysis_id(analysis_id)
            if existing:
                return await self.remove_from_favorites(existing.favorite_id)
            else:
                fav_id = await self.add_to_favorites(analysis_id, file_name, notes)
                return fav_id is not None
        except Exception as e:
            logger.error(f"❌ Failed to toggle favorite: {e}")
            return False


# Global singleton instance
_favorites_manager: Optional[FavoritesManager] = None


def get_favorites_manager(user_id: Optional[str] = None) -> FavoritesManager:
    """Get or create favorites manager singleton"""
    global _favorites_manager
    if _favorites_manager is None:
        _favorites_manager = FavoritesManager(user_id)
    return _favorites_manager
