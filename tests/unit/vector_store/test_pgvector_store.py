"""
Unit tests for PgVectorStore
"""
import os
import pytest
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock

vector_module = pytest.importorskip(
    "samplemind.core.vector_store.pgvector_store",
    reason="PgVectorStore module is no longer part of the active codebase"
)
PgVectorStore = vector_module.PgVectorStore
AudioFeatureRecord = vector_module.AudioFeatureRecord

# Test data
TEST_RECORD = AudioFeatureRecord(
    id="test_123",
    audio_path="/test/path/audio.wav",
    file_hash="abc123",
    sample_rate=44100,
    duration=180.5,
    features={"bpm": 120, "key": "C#m"},
    embedding=np.random.rand(1536).astype(np.float32),
    metadata={"artist": "Test Artist", "genre": "Test Genre"}
)

# Skip tests if we're not in CI and don't have a test database
SKIP_DB_TESTS = not os.getenv('CI') and not os.getenv('TEST_WITH_DB')

@pytest.fixture
def mock_db():
    """Fixture for testing without a real database."""
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur
        
        store = PgVectorStore("postgresql://test:test@localhost:5432/test")
        store.connect = MagicMock(return_value=mock_conn)
        
        yield store, mock_conn, mock_cur

@pytest.fixture(scope="module")
def test_db():
    """Fixture for testing with a real database."""
    if SKIP_DB_TESTS:
        pytest.skip("Skipping database tests. Set TEST_WITH_DB=1 to enable.")
    
    # Use test database
    store = PgVectorStore("postgresql://samplemind:samplemind123@localhost:5432/samplemind_test")
    
    # Clean up before tests
    with store.connect() as conn, conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS audio_features")
        conn.commit()
    
    # Recreate tables
    store._create_tables()
    
    yield store
    
    # Clean up after tests
    with store.connect() as conn, conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS audio_features")
        conn.commit()
    
    store.close()

class TestPgVectorStoreUnit:
    """Unit tests for PgVectorStore with mocks."""
    
    def test_initialization(self, mock_db):
        """Test store initialization."""
        store, mock_conn, mock_cur = mock_db
        assert store is not None
        mock_cur.execute.assert_called()
    
    def test_add_audio_features(self, mock_db):
        """Test adding audio features."""
        store, mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = (TEST_RECORD.id,)
        
        result = store.add_audio_features(TEST_RECORD)
        
        assert result == TEST_RECORD.id
        assert mock_cur.execute.call_count >= 1
        assert mock_conn.commit.called
    
    def test_get_audio_features(self, mock_db):
        """Test retrieving audio features."""
        store, mock_conn, mock_cur = mock_db
        mock_cur.fetchone.return_value = (
            TEST_RECORD.id,
            TEST_RECORD.audio_path,
            TEST_RECORD.file_hash,
            TEST_RECORD.sample_rate,
            TEST_RECORD.duration,
            TEST_RECORD.features,
            TEST_RECORD.embedding.tolist(),
            TEST_RECORD.metadata,
            datetime.now(),
            datetime.now()
        )
        
        result = store.get_audio_features(TEST_RECORD.id)
        
        assert result is not None
        assert result.id == TEST_RECORD.id
        assert result.audio_path == TEST_RECORD.audio_path
        assert np.array_equal(result.embedding, TEST_RECORD.embedding)
    
    def test_find_similar(self, mock_db):
        """Test finding similar audio features."""
        store, mock_conn, mock_cur = mock_db
        mock_cur.fetchall.return_value = [
            ("test_123", "/test/path/audio.wav", "abc123", 44100, 180.5, 
             {"bpm": 120, "key": "C#m"}, 0.1)
        ]
        
        query_embedding = np.random.rand(1536).astype(np.float32)
        results = store.find_similar(query_embedding, limit=5)
        
        assert len(results) == 1
        assert results[0]['id'] == "test_123"
        assert results[0]['distance'] == 0.1

@pytest.mark.skipif(SKIP_DB_TESTS, reason="Database tests disabled")
class TestPgVectorStoreIntegration:
    """Integration tests for PgVectorStore with a real database."""
    
    def test_crud_operations(self, test_db):
        """Test create, read, update, delete operations."""
        # Create
        test_id = test_db.add_audio_features(TEST_RECORD)
        assert test_id == TEST_RECORD.id
        
        # Read
        retrieved = test_db.get_audio_features(test_id)
        assert retrieved is not None
        assert retrieved.id == TEST_RECORD.id
        assert retrieved.audio_path == TEST_RECORD.audio_path
        assert np.allclose(retrieved.embedding, TEST_RECORD.embedding, atol=1e-6)
        
        # Update
        updated_record = AudioFeatureRecord(
            id=TEST_RECORD.id,
            audio_path="/updated/path/audio.wav",
            file_hash=TEST_RECORD.file_hash,
            sample_rate=TEST_RECORD.sample_rate,
            duration=TEST_RECORD.duration,
            features={"bpm": 125, "key": "D"},
            embedding=TEST_RECORD.embedding,
            metadata={"artist": "Updated Artist"}
        )
        
        update_id = test_db.add_audio_features(updated_record)
        assert update_id == test_id
        
        updated = test_db.get_audio_features(test_id)
        assert updated.audio_path == "/updated/path/audio.wav"
        assert updated.features["bpm"] == 125
        
        # Delete
        deleted = test_db.delete_audio_features(test_id)
        assert deleted is True
        
        # Verify deletion
        should_be_none = test_db.get_audio_features(test_id)
        assert should_be_none is None
    
    def test_similarity_search(self, test_db):
        """Test vector similarity search."""
        # Add test records
        base_embedding = np.random.rand(1536).astype(np.float32)
        similar_embedding = base_embedding + np.random.normal(0, 0.1, 1536).astype(np.float32)
        different_embedding = np.random.rand(1536).astype(np.float32)
        
        # Add records
        test_db.add_audio_features(AudioFeatureRecord(
            id="similar_1",
            audio_path="/test/similar1.wav",
            file_hash="sim1",
            sample_rate=44100,
            duration=180.0,
            features={},
            embedding=similar_embedding
        ))
        
        test_db.add_audio_features(AudioFeatureRecord(
            id="different_1",
            audio_path="/test/different1.wav",
            file_hash="diff1",
            sample_rate=44100,
            duration=200.0,
            features={},
            embedding=different_embedding
        ))
        
        # Search for similar
        results = test_db.find_similar(base_embedding, limit=2)
        
        # Should find the similar record first
        assert len(results) > 0
        assert results[0]['id'] == "similar_1"
        
        # The similar record should have a smaller distance
        similar_dist = next(r['distance'] for r in results if r['id'] == 'similar_1')
        different_dist = next((r['distance'] for r in results if r['id'] == 'different_1'), float('inf'))
        
        assert similar_dist < different_dist
    
    def test_count_audio_features(self, test_db):
        """Test counting audio features."""
        # Initial count should be 0
        assert test_db.count_audio_features() == 0
        
        # Add some records
        for i in range(3):
            test_db.add_audio_features(AudioFeatureRecord(
                id=f"test_{i}",
                audio_path=f"/test/audio_{i}.wav",
                file_hash=f"hash_{i}",
                sample_rate=44100,
                duration=180.0,
                features={"test": i},
                embedding=np.random.rand(1536).astype(np.float32)
            ))
        
        # Should count all records
        assert test_db.count_audio_features() == 3
