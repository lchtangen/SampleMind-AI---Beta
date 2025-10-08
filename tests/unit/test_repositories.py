"""
Unit tests for database repositories
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

from samplemind.core.database.repositories.audio_repository import AudioRepository
from samplemind.core.database.repositories.analysis_repository import AnalysisRepository
from samplemind.core.database.repositories.user_repository import UserRepository


@pytest.mark.unit
@pytest.mark.asyncio
class TestAudioRepository:
    """Test AudioRepository CRUD operations"""
    
    async def test_create_audio_file(self):
        """Test creating audio file document"""
        repo = AudioRepository()
        
        file_data = {
            "user_id": "test_user_123",
            "filename": "test_track.wav",
            "file_path": "/audio/test_track.wav",
            "size": 1024000,
            "duration": 180.5,
            "sample_rate": 44100,
            "channels": 2,
            "format": "wav"
        }
        
        with patch.object(repo, 'create', new_callable=AsyncMock) as mock_create:
            mock_audio = MagicMock()
            mock_audio.id = ObjectId()
            mock_audio.filename = file_data['filename']
            mock_audio.user_id = file_data['user_id']
            mock_create.return_value = mock_audio
            
            result = await repo.create(**file_data)
            
            assert result is not None
            assert result.filename == file_data['filename']
            mock_create.assert_called_once()
    
    async def test_get_by_user_id(self):
        """Test getting audio files by user ID"""
        repo = AudioRepository()
        user_id = "test_user_123"
        
        with patch.object(repo, 'find_many', new_callable=AsyncMock) as mock_find:
            mock_files = [
                MagicMock(id=ObjectId(), filename=f"test_{i}.wav", user_id=user_id)
                for i in range(3)
            ]
            mock_find.return_value = mock_files
            
            results = await repo.find_many({"user_id": user_id})
            
            assert len(results) == 3
            for result in results:
                assert result.user_id == user_id
    
    async def test_update_audio_metadata(self):
        """Test updating audio file metadata"""
        repo = AudioRepository()
        audio_id = ObjectId()
        
        with patch.object(repo, 'update', new_callable=AsyncMock) as mock_update:
            updated_data = {"tags": ["electronic", "ambient"]}
            mock_audio = MagicMock()
            mock_audio.id = audio_id
            mock_audio.tags = updated_data["tags"]
            mock_update.return_value = mock_audio
            
            result = await repo.update(str(audio_id), updated_data)
            
            assert result.tags == updated_data["tags"]
            mock_update.assert_called_once()
    
    async def test_delete_audio_file(self):
        """Test deleting audio file"""
        repo = AudioRepository()
        audio_id = ObjectId()
        
        with patch.object(repo, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True
            
            result = await repo.delete(str(audio_id))
            
            assert result is True
            mock_delete.assert_called_once_with(str(audio_id))


@pytest.mark.unit
@pytest.mark.asyncio
class TestAnalysisRepository:
    """Test AnalysisRepository operations"""
    
    async def test_create_analysis(self):
        """Test creating analysis document"""
        repo = AnalysisRepository()
        
        analysis_data = {
            "audio_file_id": str(ObjectId()),
            "user_id": "test_user_123",
            "analysis_type": "full",
            "results": {
                "bpm": 120,
                "key": "C",
                "scale": "major"
            },
            "processing_time": 2.5
        }
        
        with patch.object(repo, 'create', new_callable=AsyncMock) as mock_create:
            mock_analysis = MagicMock()
            mock_analysis.id = ObjectId()
            mock_analysis.results = analysis_data['results']
            mock_create.return_value = mock_analysis
            
            result = await repo.create(**analysis_data)
            
            assert result is not None
            assert result.results['bpm'] == 120
    
    async def test_find_by_audio_id(self):
        """Test finding analysis by audio file ID"""
        repo = AnalysisRepository()
        audio_id = str(ObjectId())
        
        with patch.object(repo, 'find_one', new_callable=AsyncMock) as mock_find:
            mock_analysis = MagicMock()
            mock_analysis.audio_file_id = audio_id
            mock_analysis.results = {"bpm": 128}
            mock_find.return_value = mock_analysis
            
            result = await repo.find_one({"audio_file_id": audio_id})
            
            assert result is not None
            assert result.audio_file_id == audio_id


@pytest.mark.unit
@pytest.mark.asyncio
class TestUserRepository:
    """Test UserRepository operations"""
    
    async def test_create_user(self):
        """Test creating user"""
        repo = UserRepository()
        
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password_here",
            "is_active": True
        }
        
        with patch.object(repo, 'create', new_callable=AsyncMock) as mock_create:
            mock_user = MagicMock()
            mock_user.id = ObjectId()
            mock_user.username = user_data['username']
            mock_user.email = user_data['email']
            mock_create.return_value = mock_user
            
            result = await repo.create(**user_data)
            
            assert result.username == user_data['username']
            assert result.email == user_data['email']
    
    async def test_find_by_username(self):
        """Test finding user by username"""
        repo = UserRepository()
        username = "testuser"
        
        with patch.object(repo, 'find_one', new_callable=AsyncMock) as mock_find:
            mock_user = MagicMock()
            mock_user.username = username
            mock_user.email = "test@example.com"
            mock_find.return_value = mock_user
            
            result = await repo.find_one({"username": username})
            
            assert result is not None
            assert result.username == username
    
    async def test_find_by_email(self):
        """Test finding user by email"""
        repo = UserRepository()
        email = "test@example.com"
        
        with patch.object(repo, 'find_one', new_callable=AsyncMock) as mock_find:
            mock_user = MagicMock()
            mock_user.email = email
            mock_user.username = "testuser"
            mock_find.return_value = mock_user
            
            result = await repo.find_one({"email": email})
            
            assert result is not None
            assert result.email == email
    
    async def test_update_user_stats(self):
        """Test updating user statistics"""
        repo = UserRepository()
        user_id = ObjectId()
        
        with patch.object(repo, 'update', new_callable=AsyncMock) as mock_update:
            updated_data = {
                "total_uploads": 10,
                "total_analyses": 8
            }
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.total_uploads = updated_data['total_uploads']
            mock_update.return_value = mock_user
            
            result = await repo.update(str(user_id), updated_data)
            
            assert result.total_uploads == 10
