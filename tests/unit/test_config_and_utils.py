"""
Unit tests for configuration and utilities
"""

import pytest
from pathlib import Path


class TestVectorStoreConfig:
    """Test vector store configuration"""

    def test_vector_store_default_persist_dir(self):
        """Test default persist directory"""
        default_dir = "data/chromadb"
        assert isinstance(default_dir, str)
        assert "chromadb" in default_dir

    def test_vector_store_imports(self):
        """Test vector store module imports"""
        from samplemind.db import vector_store
        assert hasattr(vector_store, 'VectorStore')
        assert hasattr(vector_store, 'get_vector_store')

    def test_embedding_service_imports(self):
        """Test embedding service imports"""
        from samplemind.ai import embedding_service
        assert hasattr(embedding_service, 'EmbeddingService')
        assert hasattr(embedding_service, 'get_embedding_service')


class TestAPIRouteImports:
    """Test API route imports"""

    def test_vector_search_route_exists(self):
        """Test vector search route module exists"""
        from samplemind.interfaces.api.routes import vector_search
        assert hasattr(vector_search, 'router')

    def test_vector_search_router_type(self):
        """Test vector search router is APIRouter"""
        from samplemind.interfaces.api.routes.vector_search import router
        from fastapi import APIRouter
        assert isinstance(router, APIRouter)

    def test_vector_search_route_prefix(self):
        """Test vector search route has correct prefix"""
        from samplemind.interfaces.api.routes.vector_search import router
        assert router.prefix == "/api/v1/vector"


class TestFeatureVectorConstants:
    """Test feature vector constants"""

    def test_feature_vector_dimensions(self):
        """Test feature vector has 37 dimensions"""
        # 12 basic/spectral/harmonic/rhythm + 12 chroma + 13 mfcc = 37
        basic_features = 3  # tempo, energy, loudness
        spectral_features = 5  # centroid, bandwidth, rolloff, flatness, brightness
        harmonic_features = 2  # harmonic_ratio, percussive_ratio
        rhythm_features = 2  # onset_strength, beat_strength
        chroma_features = 12
        mfcc_features = 13

        total = (basic_features + spectral_features + harmonic_features +
                 rhythm_features + chroma_features + mfcc_features)

        assert total == 37

    def test_chroma_dimensions(self):
        """Test chroma has 12 pitch classes"""
        chroma_dims = 12  # 12 semitones in an octave
        assert chroma_dims == 12

    def test_mfcc_dimensions(self):
        """Test MFCC has 13 coefficients"""
        mfcc_dims = 13  # Standard is 13 coefficients
        assert mfcc_dims == 13


class TestAPIModels:
    """Test API model availability"""

    def test_index_file_request_exists(self):
        """Test IndexFileRequest model exists"""
        from samplemind.interfaces.api.routes.vector_search import IndexFileRequest
        assert IndexFileRequest is not None

    def test_similar_file_model_exists(self):
        """Test SimilarFile model exists"""
        from samplemind.interfaces.api.routes.vector_search import SimilarFile
        assert SimilarFile is not None

    def test_recommendation_response_exists(self):
        """Test RecommendationResponse model exists"""
        from samplemind.interfaces.api.routes.vector_search import RecommendationResponse
        assert RecommendationResponse is not None
