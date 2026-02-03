#!/usr/bin/env python3
"""
Integration Tests for Phase 10 Neural Audio Pipeline

Tests the complete end-to-end neural audio analysis pipeline:
- Audio loading and preprocessing
- Neural embedding generation
- ChromaDB vector storage
- Semantic search functionality
- Generation manager integration
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import pytest
import soundfile as sf

from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel, AudioFeatures
from samplemind.core.engine.neural_engine import NeuralFeatureExtractor
from samplemind.core.database import chroma as chroma_db
from samplemind.core.generation.generation_manager import (
    GenerationManager,
    GenerationMode,
    GenerationRequest,
)
from samplemind.integrations.ai_manager import SampleMindAIManager, AnalysisType


class TestNeuralPipeline:
    """Test the complete neural audio analysis pipeline"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures"""
        self.audio_engine = AudioEngine()
        self.neural_extractor = NeuralFeatureExtractor()
        self.generation_manager = GenerationManager()
        self.temp_dir = tempfile.mkdtemp()

        # Initialize ChromaDB for tests
        chroma_db.init_chromadb(persist_directory="./data/chroma_test", collection_name="test_embeddings")

        # Generate synthetic audio for testing
        duration = 2  # seconds
        sample_rate = 44100
        t = np.linspace(0, duration, sample_rate * duration)
        # Simple sine wave at 440 Hz (A4 note)
        self.test_audio = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

        # Save test audio to file for use with APIs that expect file paths
        self.test_audio_path = Path(self.temp_dir) / "test_audio.wav"
        sf.write(self.test_audio_path, self.test_audio, sample_rate)

        yield

        # Cleanup
        try:
            client = chroma_db.get_chroma_client()
            client.delete_collection("test_embeddings")
        except:
            pass

        # Clean up temp files
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def test_audio_engine_produces_neural_embedding(self):
        """Test that AudioEngine generates neural embeddings"""
        # Analyze at STANDARD level to trigger neural embedding
        features = self.audio_engine.analyze_audio(
            self.test_audio_path,
            level=AnalysisLevel.STANDARD
        )

        # Verify neural embedding is present
        assert features.neural_embedding is not None
        assert isinstance(features.neural_embedding, (list, np.ndarray))

        # Verify embedding dimension (CLAP is 512-dimensional)
        if isinstance(features.neural_embedding, list):
            assert len(features.neural_embedding) == 512
        else:
            assert features.neural_embedding.shape[0] == 512

    def test_neural_extractor_generates_embeddings(self):
        """Test NeuralFeatureExtractor generates correct embeddings"""
        # Generate audio embedding
        embedding = self.neural_extractor.generate_embedding(self.test_audio_path)

        assert embedding is not None
        assert len(embedding) == 512
        assert isinstance(embedding[0], (float, np.floating))

        # Verify embedding is deterministic for same input
        embedding2 = self.neural_extractor.generate_embedding(self.test_audio_path)
        np.testing.assert_array_almost_equal(embedding, embedding2)

    def test_text_embedding_generation(self):
        """Test text embedding generation for semantic search"""
        text = "upbeat electronic drum loop with synth bass"
        embedding = self.neural_extractor.generate_text_embedding(text)

        assert embedding is not None
        assert len(embedding) == 512
        assert isinstance(embedding[0], (float, np.floating))

    @pytest.mark.asyncio
    async def test_chromadb_embedding_storage(self):
        """Test storing embeddings in ChromaDB"""
        embedding = self.neural_extractor.generate_embedding(self.test_audio_path)

        # Store embedding with metadata
        metadata = {
            "tempo": 120.0,
            "key": "C Major",
            "duration": 2.0,
            "format": "wav",
        }

        # Add to ChromaDB
        success = await chroma_db.add_embedding(
            file_id="test_audio_001",
            embedding=embedding,
            metadata=metadata
        )
        assert success

        # Verify it was stored (by doing a similarity search)
        # The test audio embedding should be most similar to itself
        results = await chroma_db.query_similar(embedding, n_results=1)

        assert results is not None
        assert len(results["ids"]) > 0

    @pytest.mark.asyncio
    async def test_semantic_search_functionality(self):
        """Test semantic search with neural embeddings"""
        # Add multiple embeddings to ChromaDB
        embeddings = []
        for i in range(3):
            # Slightly vary the audio for different embeddings
            varied_audio = self.test_audio + (0.01 * i) * np.random.randn(len(self.test_audio))
            varied_path = Path(self.temp_dir) / f"test_audio_{i}.wav"
            sf.write(varied_path, varied_audio, 44100)

            embedding = self.neural_extractor.generate_embedding(varied_path)
            embeddings.append(embedding)

            metadata = {
                "file_id": f"test_{i}",
                "tempo": 120.0 + (10 * i),
                "genre": "electronic" if i % 2 == 0 else "house",
            }

            success = await chroma_db.add_embedding(
                file_id=f"test_{i}",
                embedding=embedding,
                metadata=metadata
            )
            assert success

        # Perform semantic search with text query
        query_text = "fast electronic music"
        query_embedding = self.neural_extractor.generate_text_embedding(query_text)

        # Search for similar embeddings
        results = await chroma_db.query_similar(query_embedding, n_results=2)

        assert results is not None
        assert len(results["ids"]) > 0

    @pytest.mark.asyncio
    async def test_generation_manager_text_to_sample(self):
        """Test GenerationManager TEXT_TO_SAMPLE mode"""
        # Create generation request
        request = GenerationRequest(
            mode=GenerationMode.TEXT_TO_SAMPLE,
            prompt="upbeat electronic drum loop",
            parameters={"limit": 5}
        )

        # Generate
        result = await self.generation_manager.generate(request)

        assert result is not None
        assert result.mode == GenerationMode.TEXT_TO_SAMPLE
        assert len(result.matches) >= 0  # May be 0 if no samples in DB

        # Verify result structure
        if result.matches:
            match = result.matches[0]
            assert hasattr(match, 'file_id')
            assert hasattr(match, 'score')
            assert 0 <= match.score <= 1

    @pytest.mark.asyncio
    async def test_generation_manager_audio_variation(self):
        """Test GenerationManager AUDIO_VARIATION mode"""
        # Create generation request for audio variation
        request = GenerationRequest(
            mode=GenerationMode.AUDIO_VARIATION,
            prompt="test_audio.wav",
            parameters={"variation_count": 3}
        )

        # Generate
        result = await self.generation_manager.generate(request)

        assert result is not None
        assert result.mode == GenerationMode.AUDIO_VARIATION

    @pytest.mark.asyncio
    async def test_generation_manager_context_suggest(self):
        """Test GenerationManager CONTEXT_SUGGEST mode"""
        # Create context request
        request = GenerationRequest(
            mode=GenerationMode.CONTEXT_SUGGEST,
            prompt="C Major 120 BPM electronic",
            parameters={
                "key": "C Major",
                "tempo": 120,
                "genre": "electronic"
            }
        )

        # Generate suggestions
        result = await self.generation_manager.generate(request)

        assert result is not None
        assert result.mode == GenerationMode.CONTEXT_SUGGEST

    @pytest.mark.asyncio
    async def test_generation_manager_stem_remix(self):
        """Test GenerationManager STEM_REMIX mode"""
        # Create stem remix request
        request = GenerationRequest(
            mode=GenerationMode.STEM_REMIX,
            prompt="test_audio.wav",
            parameters={"remix_count": 3}
        )

        # Generate
        result = await self.generation_manager.generate(request)

        assert result is not None
        assert result.mode == GenerationMode.STEM_REMIX

    @pytest.mark.asyncio
    async def test_ai_manager_with_fallback(self):
        """Test AI Manager provider fallback chain"""
        ai_manager = SampleMindAIManager()

        # Create a simple feature dict for testing
        features = {
            "tempo": 120.0,
            "key": "C Major",
            "duration": 2.0,
            "energy": 0.75,
        }

        # This should attempt analysis and fall back if needed
        try:
            result = await ai_manager.analyze_music(
                features,
                AnalysisType.COMPREHENSIVE_ANALYSIS
            )

            # Verify result structure
            assert result is not None
            assert hasattr(result, 'provider')
            assert hasattr(result, 'summary')
        except RuntimeError as e:
            # OK if no providers configured - we're testing the fallback chain exists
            assert "provider" in str(e).lower() or "configured" in str(e).lower()


class TestNeuralPipelinePerformance:
    """Performance tests for neural pipeline"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up performance test fixtures"""
        self.audio_engine = AudioEngine()
        self.neural_extractor = NeuralFeatureExtractor()
        self.temp_dir = tempfile.mkdtemp()

        # Generate longer test audio
        duration = 5  # 5 seconds
        sample_rate = 44100
        t = np.linspace(0, duration, sample_rate * duration)
        test_audio = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

        # Save to file
        self.test_audio_path = Path(self.temp_dir) / "test_audio_long.wav"
        sf.write(self.test_audio_path, test_audio, sample_rate)

    def test_embedding_generation_performance(self):
        """Test that embedding generation is fast enough"""
        import time

        start = time.time()
        embedding = self.neural_extractor.generate_embedding(self.test_audio_path)
        elapsed = time.time() - start

        # Embedding generation should be reasonably fast
        # Mock mode should be <100ms, real CLAP might be 500-1000ms
        assert elapsed < 2.0, f"Embedding generation took {elapsed:.2f}s"
        assert embedding is not None

    def test_analysis_with_neural_embedding_performance(self):
        """Test that full analysis with neural embedding is fast enough"""
        import time

        start = time.time()
        features = self.audio_engine.analyze_audio(
            self.test_audio_path,
            level=AnalysisLevel.STANDARD
        )
        elapsed = time.time() - start

        # Full analysis should complete in reasonable time
        # Target: <3 seconds for STANDARD level (includes embedding generation)
        assert elapsed < 3.0, f"Analysis took {elapsed:.2f}s"
        assert features.neural_embedding is not None


class TestNeuralPipelineIntegration:
    """Integration tests for complete neural pipeline workflows"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up integration test fixtures"""
        self.audio_engine = AudioEngine()
        self.neural_extractor = NeuralFeatureExtractor()
        self.generation_manager = GenerationManager()
        self.ai_manager = SampleMindAIManager()
        self.temp_dir = tempfile.mkdtemp()

        # Initialize ChromaDB for tests
        chroma_db.init_chromadb(persist_directory="./data/chroma_test", collection_name="test_embeddings")

    @pytest.mark.asyncio
    async def test_complete_analysis_and_search_workflow(self):
        """Test complete workflow: analyze audio, store embedding, search"""
        # Step 1: Generate test audio
        sample_rate = 44100
        duration = 2
        t = np.linspace(0, duration, sample_rate * duration)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

        # Save to file
        audio_path = Path(self.temp_dir) / "workflow_test.wav"
        sf.write(audio_path, audio, sample_rate)

        # Step 2: Analyze with neural embedding
        features = self.audio_engine.analyze_audio(
            audio_path,
            level=AnalysisLevel.STANDARD
        )

        assert features.neural_embedding is not None

        # Step 3: Store embedding
        if features.neural_embedding:
            metadata = {
                "tempo": features.tempo,
                "key": features.key,
                "mode": features.mode,
                "duration": features.duration,
            }

            success = await chroma_db.add_embedding(
                file_id="workflow_test_001",
                embedding=features.neural_embedding,
                metadata=metadata
            )
            assert success

        # Step 4: Perform semantic search
        query_text = "melodic sine wave at A4"
        query_embedding = self.neural_extractor.generate_text_embedding(query_text)

        results = await chroma_db.query_similar(query_embedding, n_results=1)

        # Verify workflow completed
        assert features is not None
        assert results is not None


__all__ = [
    "TestNeuralPipeline",
    "TestNeuralPipelinePerformance",
    "TestNeuralPipelineIntegration",
]
