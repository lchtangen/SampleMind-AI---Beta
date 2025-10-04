"""Audio file repository"""

from typing import Optional, List
from datetime import datetime
from samplemind.core.database.mongo import AudioFile


class AudioRepository:
    """Repository for audio file CRUD operations"""
    
    @staticmethod
    async def create(
        file_id: str,
        filename: str,
        file_path: str,
        file_size: int,
        duration: float,
        sample_rate: int,
        channels: int,
        format: str,
        user_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None
    ) -> AudioFile:
        """Create new audio file record"""
        audio_file = AudioFile(
            file_id=file_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            duration=duration,
            sample_rate=sample_rate,
            channels=channels,
            format=format,
            user_id=user_id,
            tags=tags or [],
            metadata=metadata or {}
        )
        await audio_file.insert()
        return audio_file
    
    @staticmethod
    async def get_by_id(file_id: str) -> Optional[AudioFile]:
        """Get audio file by ID"""
        return await AudioFile.find_one(AudioFile.file_id == file_id)
    
    @staticmethod
    async def get_by_user(user_id: str, skip: int = 0, limit: int = 50) -> List[AudioFile]:
        """Get all audio files for a user"""
        return await AudioFile.find(AudioFile.user_id == user_id).skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def list_all(skip: int = 0, limit: int = 50) -> List[AudioFile]:
        """List all audio files with pagination"""
        return await AudioFile.find_all().skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def update(file_id: str, **kwargs) -> Optional[AudioFile]:
        """Update audio file"""
        audio_file = await AudioFile.find_one(AudioFile.file_id == file_id)
        if audio_file:
            for key, value in kwargs.items():
                setattr(audio_file, key, value)
            await audio_file.save()
        return audio_file
    
    @staticmethod
    async def delete(file_id: str) -> bool:
        """Delete audio file"""
        audio_file = await AudioFile.find_one(AudioFile.file_id == file_id)
        if audio_file:
            await audio_file.delete()
            return True
        return False
    
    @staticmethod
    async def count() -> int:
        """Count total audio files"""
        return await AudioFile.count()
    
    @staticmethod
    async def search_by_tags(tags: List[str], skip: int = 0, limit: int = 50) -> List[AudioFile]:
        """Search audio files by tags"""
        return await AudioFile.find(AudioFile.tags.in_(tags)).skip(skip).limit(limit).to_list()
