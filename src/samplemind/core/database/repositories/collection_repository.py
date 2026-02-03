"""Collection repository"""

import uuid
from datetime import datetime
from typing import Any, List, Optional

from samplemind.core.database.mongo import AudioCollection, AudioFile


class CollectionRepository:
    """Repository for audio collection CRUD operations"""

    @staticmethod
    async def create(
        user_id: str,
        name: str,
        description: Optional[str] = None,
        is_public: bool = False,
        tags: List[str] = [],
        metadata: dict = {}
    ) -> AudioCollection:
        """Create new collection"""
        collection = AudioCollection(
            collection_id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            description=description,
            is_public=is_public,
            tags=tags,
            metadata=metadata,
            file_count=0,
            total_duration=0.0
        )
        await collection.insert()
        return collection

    @staticmethod
    async def get_by_id(collection_id: str) -> Optional[AudioCollection]:
        """Get collection by ID"""
        return await AudioCollection.find_one(AudioCollection.collection_id == collection_id)

    @staticmethod
    async def get_by_user(
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AudioCollection]:
        """List collections for a user"""
        return await AudioCollection.find(
            AudioCollection.user_id == user_id
        ).sort(-AudioCollection.updated_at).skip(skip).limit(limit).to_list()

    @staticmethod
    async def update(collection_id: str, **kwargs) -> Optional[AudioCollection]:
        """Update collection fields"""
        collection = await AudioCollection.find_one(AudioCollection.collection_id == collection_id)
        if collection:
            for key, value in kwargs.items():
                if hasattr(collection, key) and value is not None:
                    setattr(collection, key, value)
            collection.updated_at = datetime.utcnow()
            await collection.save()
        return collection

    @staticmethod
    async def delete(collection_id: str) -> bool:
        """Delete collection"""
        collection = await AudioCollection.find_one(AudioCollection.collection_id == collection_id)
        if collection:
            # Also remove this collection ID from all audio files
            await AudioFile.find(
                {"collection_ids": collection_id}
            ).update({"$pull": {"collection_ids": collection_id}})

            await collection.delete()
            return True
        return False

    @staticmethod
    async def get_collection_items(collection_id: str) -> List[AudioFile]:
        """Get all audio files in a collection"""
        return await AudioFile.find(
            {"collection_ids": collection_id}
        ).sort(-AudioFile.created_at).to_list()
