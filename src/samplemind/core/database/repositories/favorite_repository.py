"""Favorites repository"""

from samplemind.core.database.mongo import Favorite


class FavoriteRepository:
    """Repository for favorite CRUD operations"""

    @staticmethod
    async def create(
        favorite_id: str,
        analysis_id: str,
        file_name: str,
        user_id: str | None = None,
        notes: str | None = None,
        rating: int = 0,
    ) -> Favorite:
        """Create new favorite"""
        favorite = Favorite(
            favorite_id=favorite_id,
            user_id=user_id,
            analysis_id=analysis_id,
            file_name=file_name,
            notes=notes,
            rating=rating,
        )
        await favorite.insert()
        return favorite

    @staticmethod
    async def get_by_id(favorite_id: str) -> Favorite | None:
        """Get favorite by ID"""
        return await Favorite.find_one(Favorite.favorite_id == favorite_id)

    @staticmethod
    async def get_by_analysis_id(analysis_id: str) -> Favorite | None:
        """Get favorite by analysis ID"""
        return await Favorite.find_one(Favorite.analysis_id == analysis_id)

    @staticmethod
    async def get_by_user(
        user_id: str, skip: int = 0, limit: int = 50
    ) -> list[Favorite]:
        """Get all favorites for a user"""
        return (
            await Favorite.find(Favorite.user_id == user_id)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def delete(favorite_id: str) -> bool:
        """Delete favorite"""
        favorite = await Favorite.find_one(Favorite.favorite_id == favorite_id)
        if favorite:
            await favorite.delete()
            return True
        return False

    @staticmethod
    async def update_rating(favorite_id: str, rating: int) -> Favorite | None:
        """Update rating (0-5)"""
        if not 0 <= rating <= 5:
            raise ValueError("Rating must be between 0 and 5")

        favorite = await Favorite.find_one(Favorite.favorite_id == favorite_id)
        if favorite:
            favorite.rating = rating
            await favorite.save()
            return favorite
        return None

    @staticmethod
    async def update_notes(favorite_id: str, notes: str | None) -> Favorite | None:
        """Update notes"""
        favorite = await Favorite.find_one(Favorite.favorite_id == favorite_id)
        if favorite:
            favorite.notes = notes
            await favorite.save()
            return favorite
        return None

    @staticmethod
    async def get_by_rating(user_id: str, min_rating: int = 0) -> list[Favorite]:
        """Get favorites with minimum rating"""
        return (
            await Favorite.find(
                Favorite.user_id == user_id, Favorite.rating >= min_rating
            )
            .sort(-Favorite.rating)
            .to_list()
        )

    @staticmethod
    async def get_recent(user_id: str, limit: int = 10) -> list[Favorite]:
        """Get recently added favorites"""
        return (
            await Favorite.find(Favorite.user_id == user_id)
            .sort(-Favorite.added_at)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        """Count favorites for user"""
        return await Favorite.find(Favorite.user_id == user_id).count()
