"""
Tests for semantic search caching functionality.
Verifies embedding and query result caching performance improvements.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from samplemind.core.caching.semantic_cache import SemanticCache


class TestSemanticCache:
    """Test SemanticCache functionality."""

    @pytest.mark.asyncio
    async def test_embedding_cache_hit(self):
        """Test that embedding caching works."""
        with tempfile.TemporaryDirectory() as temp_cache_dir:
            cache = SemanticCache(max_embeddings=100, cache_dir=temp_cache_dir)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(b"RIFF" + b"\x00" * 100)
                temp_path = f.name

            embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100

            # First get should miss
            result = await cache.get_embedding(temp_path)
            assert result is None

            # Set embedding
            success = await cache.set_embedding(temp_path, embedding)
            assert success

            # Second get should hit
            result = await cache.get_embedding(temp_path)
            assert result == embedding
            
            Path(temp_path).unlink(missing_ok=True)
            cache.clear()

    @pytest.mark.asyncio
    async def test_query_result_caching(self):
        """Test query result caching."""
        with tempfile.TemporaryDirectory() as temp_cache_dir:
            cache = SemanticCache(max_embeddings=100, cache_dir=temp_cache_dir)
            
            query_text = "electronic drums"
            results = [
                {"id": "sample1", "distance": 0.1, "metadata": {}},
                {"id": "sample2", "distance": 0.2, "metadata": {}},
            ]

            # First query should miss
            cached = await cache.get_query_result(query_text)
            assert cached is None

            # Set query result
            success = await cache.set_query_result(
                query_text, results, n_results=2
            )
            assert success

            # Second query should hit
            cached = await cache.get_query_result(query_text, n_results=2)
            assert cached == results
            
            cache.clear()

    @pytest.mark.asyncio
    async def test_cache_statistics(self):
        """Test cache statistics tracking."""
        with tempfile.TemporaryDirectory() as temp_cache_dir:
            cache = SemanticCache(max_embeddings=100, cache_dir=temp_cache_dir)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(b"RIFF" + b"\x00" * 100)
                temp_path = f.name

            embedding = [0.1, 0.2, 0.3] * 100

            # First miss
            await cache.get_embedding(temp_path)
            
            # Set and then multiple hits
            await cache.set_embedding(temp_path, embedding)
            for _ in range(5):
                await cache.get_embedding(temp_path)

            stats = cache.get_stats()
            assert stats["embedding_hits"] == 5
            assert stats["embedding_misses"] == 1
            assert stats["cached_embeddings"] == 1
            
            Path(temp_path).unlink(missing_ok=True)
            cache.clear()
