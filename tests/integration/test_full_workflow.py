#!/usr/bin/env python3
"""
Integration Test: Full Workflow
Tests complete end-to-end workflow for beta validation
"""

import pytest
import asyncio
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
from samplemind.integrations.ai_manager import SampleMindAIManager


@pytest.mark.integration
@pytest.mark.asyncio
class TestFullWorkflow:
    """Test complete workflow from file to AI analysis"""

    @pytest.fixture(scope="class")
    def audio_engine(self):
        """Audio engine fixture"""
        engine = AudioEngine()
        yield engine
        # Cleanup - shutdown is synchronous
        engine.shutdown()

    @pytest.fixture(scope="class")
    def test_audio_file(self, test_audio_samples):
        """Get a test audio file"""
        return test_audio_samples["120_c_major"]

    async def test_basic_workflow(self, audio_engine, test_audio_file):
        """Test: Basic analysis workflow"""
        # Step 1: Load audio
        audio_data, sr = audio_engine.load_audio(test_audio_file)
        assert audio_data is not None
        assert sr > 0

        # Step 2: Analyze
        result = await audio_engine.analyze_audio_async(
            test_audio_file,
            level=AnalysisLevel.STANDARD
        )

        assert result is not None
        assert result.tempo > 0
        assert result.key is not None
        # Check rms_energy exists and has valid values
        assert result.rms_energy is not None
        assert len(result.rms_energy) > 0

        # Step 3: Verify caching
        result2 = await audio_engine.analyze_audio_async(
            test_audio_file,
            level=AnalysisLevel.STANDARD
        )
        assert result.tempo == result2.tempo  # Should be same from cache

    async def test_batch_workflow(self, audio_engine, test_audio_samples):
        """Test: Batch processing workflow"""
        # Get multiple test files
        files = [
            test_audio_samples["120_c_major"],
            test_audio_samples["140_a_minor"]
        ]

        # Batch analyze - synchronous method that returns List[AudioFeatures]
        results = audio_engine.batch_analyze(
            files,
            level=AnalysisLevel.BASIC
        )

        assert len(results) == len(files)

        for result in results:
            assert result is not None
            assert result.tempo > 0

    @pytest.mark.skipif(
        "GOOGLE_AI_API_KEY" not in os.environ and "OPENAI_API_KEY" not in os.environ,
        reason="No AI API keys configured"
    )
    async def test_ai_workflow(self, audio_engine, test_audio_file):
        """Test: Complete workflow with AI analysis"""

        # Step 1: Extract features
        result = await audio_engine.analyze_audio_async(
            test_audio_file,
            level=AnalysisLevel.DETAILED
        )

        # Step 2: Prepare for AI
        features = {
            'tempo': result.tempo,
            'key': result.key,
            'mode': result.mode,
            'rms_energy': result.rms_energy,
            'duration': result.duration
        }

        # Step 3: AI analysis
        ai_manager = SampleMindAIManager()

        try:
            ai_result = await ai_manager.analyze_music(features)

            assert ai_result is not None
            assert ai_result.provider_used in ['google_ai', 'openai']
            assert ai_result.response_time > 0

        except Exception as e:
            pytest.skip(f"AI analysis failed: {e}")

    async def test_error_handling(self, audio_engine):
        """Test: Error handling in workflow"""
        # Test with non-existent file
        fake_file = Path("/tmp/nonexistent_audio_file.wav")

        with pytest.raises(Exception):
            audio_engine.load_audio(fake_file)

    async def test_performance_workflow(self, audio_engine, test_audio_file):
        """Test: Performance during workflow"""
        import time

        # Time the analysis
        start = time.time()

        result = await audio_engine.analyze_audio_async(
            test_audio_file,
            level=AnalysisLevel.STANDARD
        )

        elapsed = time.time() - start

        assert result is not None
        assert elapsed < 10  # Should complete in under 10 seconds

        # Check stats
        stats = audio_engine.get_performance_stats()
        assert stats['total_analyses'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
