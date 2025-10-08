"""
Unit tests for Vector Store
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np

from samplemind.db.vector_store import VectorStore, get_vector_store


class TestVectorStore:
    """Test VectorStore functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def vector_store(self, temp_dir):
        """Create VectorStore instance"""
        return VectorStore(persist_directory=temp_dir)

    def test_initialization(self, vector_store):
        """Test VectorStore initialization"""
        assert vector_store is not None
        assert vector_store.client is not None
        assert vector_store.audio_collection is not None
        assert vector_store.sample_collection is not None

    def test_create_feature_vector(self, vector_store):
        """Test feature vector creation"""
        features = {
            'tempo': 120.0,
            'energy': 0.8,
            'loudness': -15.0,
            'spectral_features': {
                'centroid': 2000.0,
                'bandwidth': 1500.0,
                'rolloff': 5000.0,
                'flatness': 0.4,
                'brightness': 0.6
            },
            'harmonic_features': {
                'harmonic_ratio': 0.7,
                'percussive_ratio': 0.3
            },
            'rhythm_features': {
                'onset_strength': 0.6,
                'beat_strength': 0.5
            },
            'chroma': [[0.1] * 12],
            'mfcc': [[0.1] * 13]
        }

        vector = vector_store._create_feature_vector(features)

        assert isinstance(vector, list)
        assert len(vector) == 37  # 12 basic/spectral/harmonic/rhythm + 12 chroma + 13 mfcc
        assert all(isinstance(v, float) for v in vector)
        assert all(0 <= v <= 1.5 for v in vector)  # All values should be normalized-ish

    def test_add_audio_features(self, vector_store):
        """Test adding audio features"""
        features = {
            'tempo': 128.0,
            'energy': 0.7,
            'spectral_features': {'centroid': 2500.0}
        }

        doc_id = vector_store.add_audio_features(
            file_path="/test/audio.wav",
            features=features,
            metadata={'genre': 'electronic'}
        )

        assert doc_id is not None
        assert isinstance(doc_id, str)
        assert doc_id.startswith('audio_')

    def test_search_similar(self, vector_store):
        """Test similarity search"""
        # Add some test data
        features1 = {
            'tempo': 120.0,
            'energy': 0.8,
            'spectral_features': {'centroid': 2000.0}
        }
        features2 = {
            'tempo': 122.0,
            'energy': 0.75,
            'spectral_features': {'centroid': 2100.0}
        }

        vector_store.add_audio_features("/test/audio1.wav", features1)
        vector_store.add_audio_features("/test/audio2.wav", features2)

        # Search for similar
        results = vector_store.search_similar(features1, n_results=2)

        assert isinstance(results, list)
        assert len(results) <= 2
        if results:
            assert 'file_path' in results[0]
            assert 'similarity' in results[0]
            assert 'distance' in results[0]

    def test_search_by_file(self, vector_store):
        """Test search by file path"""
        features = {
            'tempo': 130.0,
            'energy': 0.9,
            'spectral_features': {'centroid': 3000.0}
        }

        file_path = "/test/reference.wav"
        vector_store.add_audio_features(file_path, features)

        # Add another file
        vector_store.add_audio_features(
            "/test/other.wav",
            {'tempo': 132.0, 'energy': 0.85}
        )

        # Search by file
        results = vector_store.search_by_file(file_path, n_results=5)

        assert isinstance(results, list)
        # Should not include the reference file itself
        assert not any(r['file_path'] == file_path for r in results)

    def test_get_collection_stats(self, vector_store):
        """Test getting collection statistics"""
        stats = vector_store.get_collection_stats()

        assert isinstance(stats, dict)
        assert 'audio_count' in stats
        assert 'sample_count' in stats
        assert 'persist_directory' in stats
        assert isinstance(stats['audio_count'], int)

    def test_delete_audio(self, vector_store):
        """Test deleting audio from vector store"""
        features = {'tempo': 140.0, 'energy': 0.6}
        file_path = "/test/delete_me.wav"

        vector_store.add_audio_features(file_path, features)

        # Delete
        success = vector_store.delete_audio(file_path)
        assert success is True

    def test_feature_vector_normalization(self, vector_store):
        """Test that feature vectors are properly normalized"""
        features = {
            'tempo': 200.0,  # High tempo
            'energy': 1.0,    # Max energy
            'loudness': 0.0,  # Max loudness
            'spectral_features': {
                'centroid': 10000.0,  # High frequency
                'bandwidth': 8000.0,
                'rolloff': 9000.0,
                'flatness': 1.0,
                'brightness': 1.0
            }
        }

        vector = vector_store._create_feature_vector(features)

        # Check normalization
        assert vector[0] == pytest.approx(1.0, abs=0.01)  # tempo normalized to 200/200
        assert vector[1] == pytest.approx(1.0, abs=0.01)  # energy at max

    def test_handle_missing_features(self, vector_store):
        """Test handling of missing features"""
        # Minimal features
        features = {'tempo': 120.0}

        vector = vector_store._create_feature_vector(features)

        # Should still create a valid vector with defaults
        assert len(vector) == 37
        assert all(isinstance(v, float) for v in vector)

    def test_clear_collection(self, vector_store):
        """Test clearing a collection"""
        # Add some data
        features = {'tempo': 120.0, 'energy': 0.5}
        vector_store.add_audio_features("/test/audio.wav", features)

        # Clear collection
        success = vector_store.clear_collection("audio_features")
        assert success is True

        # Verify cleared
        stats = vector_store.get_collection_stats()
        assert stats['audio_count'] == 0


class TestVectorStoreSingleton:
    """Test VectorStore singleton pattern"""

    def test_get_vector_store_singleton(self):
        """Test that get_vector_store returns singleton"""
        store1 = get_vector_store()
        store2 = get_vector_store()

        assert store1 is store2


class TestFeatureVectorDimensions:
    """Test feature vector dimensions"""

    @pytest.fixture
    def vector_store(self):
        temp_dir = tempfile.mkdtemp()
        store = VectorStore(persist_directory=temp_dir)
        yield store
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_complete_features_vector_size(self, vector_store):
        """Test vector size with complete features"""
        features = {
            'tempo': 120.0,
            'energy': 0.8,
            'loudness': -15.0,
            'spectral_features': {
                'centroid': 2000.0,
                'bandwidth': 1500.0,
                'rolloff': 5000.0,
                'flatness': 0.4,
                'brightness': 0.6
            },
            'harmonic_features': {
                'harmonic_ratio': 0.7,
                'percussive_ratio': 0.3
            },
            'rhythm_features': {
                'onset_strength': 0.6,
                'beat_strength': 0.5
            },
            'chroma': np.random.rand(12, 100).tolist(),
            'mfcc': np.random.rand(20, 100).tolist()
        }

        vector = vector_store._create_feature_vector(features)
        assert len(vector) == 37

    def test_minimal_features_vector_size(self, vector_store):
        """Test vector size with minimal features"""
        features = {'tempo': 120.0}

        vector = vector_store._create_feature_vector(features)
        assert len(vector) == 37  # Should pad with zeros

    def test_vector_all_floats(self, vector_store):
        """Test that all vector values are floats"""
        features = {
            'tempo': 120,  # int
            'energy': 0.8,  # float
            'spectral_features': {'centroid': 2000}
        }

        vector = vector_store._create_feature_vector(features)
        assert all(isinstance(v, float) for v in vector)
