"""Pytest fixtures and utilities for comprehensive test coverage.

This module provides reusable fixtures, mocks, and helpers for writing
tests that follow best practices and maintain consistency across the suite.

Usage:
    >>> import pytest
    >>> from tests.fixtures.common import mock_audio_file, mock_redis
    >>>
    >>> def test_analyze(mock_audio_file, mock_redis):
    ...     result = analyze_audio(mock_audio_file)
    ...     assert result.bpm > 0
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

logger = logging.getLogger(__name__)


# ============================================================================
# Audio Fixtures
# ============================================================================


@pytest.fixture
def audio_samples_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test audio files."""
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    return audio_dir


@pytest.fixture
def mock_audio_file(audio_samples_dir: Path) -> Path:
    """Create a mock WAV audio file for testing."""
    import wave

    import numpy as np

    # Create a simple 440Hz sine wave (A4 note)
    sample_rate = 44100
    duration = 2  # 2 seconds
    frequency = 440

    samples = (
        32767
        * np.sin(2 * np.pi * frequency * np.arange(sample_rate * duration) / sample_rate)
    ).astype(np.int16)

    wav_file = audio_samples_dir / "test_sample.wav"
    with wave.open(str(wav_file), "wb") as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())

    return wav_file


@pytest.fixture
def mock_audio_files(audio_samples_dir: Path) -> list[Path]:
    """Create multiple mock audio files with different properties."""
    files = []
    for i, (bpm, freq) in enumerate([(120, 440), (140, 880), (100, 220)]):
        import wave

        import numpy as np

        sample_rate = 44100
        duration = 1
        samples = (
            32767
            * np.sin(2 * np.pi * freq * np.arange(sample_rate * duration) / sample_rate)
        ).astype(np.int16)

        wav_file = audio_samples_dir / f"sample_{i}_bpm_{bpm}.wav"
        with wave.open(str(wav_file), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(samples.tobytes())

        files.append(wav_file)

    return files


# ============================================================================
# Redis Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def mock_redis() -> AsyncMock:
    """Mock Redis client for testing."""
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.rpush = AsyncMock(return_value=1)
    mock.lpop = AsyncMock(return_value=None)
    mock.hset = AsyncMock(return_value=1)
    mock.hget = AsyncMock(return_value=None)
    return mock


@pytest_asyncio.fixture
async def mock_redis_with_patching(mock_redis: AsyncMock) -> AsyncGenerator[AsyncMock, None]:
    """Patch get_redis to return mock throughout test."""
    with patch("samplemind.integrations.redis_client.get_redis", return_value=mock_redis):
        yield mock_redis


# ============================================================================
# MongoDB/Tortoise ORM Fixtures
# ============================================================================


@pytest.fixture
def mock_mongodb_connection() -> MagicMock:
    """Mock MongoDB connection for testing."""
    mock = MagicMock()
    return mock


@pytest_asyncio.fixture
async def mock_sample_model() -> MagicMock:
    """Mock TortoiseSample model."""
    mock = AsyncMock()
    mock.create = AsyncMock(
        return_value={
            "id": 1,
            "filename": "test.wav",
            "bpm": 128.0,
            "key": "A minor",
            "duration": 120.0,
        }
    )
    mock.get = AsyncMock(return_value={"id": 1, "filename": "test.wav"})
    mock.filter = MagicMock(
        return_value=AsyncMock(all=AsyncMock(return_value=[{"id": 1, "filename": "test.wav"}]))
    )
    return mock


# ============================================================================
# AI Provider Fixtures
# ============================================================================


@pytest.fixture
def mock_anthropic_client() -> MagicMock:
    """Mock Anthropic/Claude client."""
    mock = MagicMock()
    mock.messages.create = MagicMock(
        return_value=MagicMock(
            content=[MagicMock(text='{"bpm": 128, "key": "A minor", "confidence": 0.95}')]
        )
    )
    return mock


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Mock OpenAI/GPT client."""
    mock = MagicMock()
    mock.chat.completions.create = MagicMock(
        return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"genres": ["trap", "dark"]}'))]
        )
    )
    return mock


@pytest.fixture
def mock_gemini_client() -> MagicMock:
    """Mock Google Gemini client."""
    mock = MagicMock()
    return mock


# ============================================================================
# HTTP Client Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_client():
    """Create a test HTTP client for FastAPI app."""
    from fastapi.testclient import TestClient

    from samplemind.interfaces.api.main import app

    return TestClient(app)


@pytest_asyncio.fixture
async def async_test_client():
    """Create an async test HTTP client."""
    from httpx import AsyncClient

    from samplemind.interfaces.api.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# Event Loop Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Logging Fixtures
# ============================================================================


@pytest.fixture
def caplog_with_level(caplog):
    """Fixture for capturing logs at specific level."""
    caplog.set_level(logging.DEBUG)
    return caplog


# ============================================================================
# Helper Functions
# ============================================================================


def create_mock_analysis_result(
    bpm: float = 128.0,
    key: str = "A minor",
    confidence: float = 0.95,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Helper to create a mock analysis result."""
    if tags is None:
        tags = ["trap", "bass-heavy"]

    return {
        "file_path": "/path/to/sample.wav",
        "duration": 180.5,
        "bpm": bpm,
        "key": key,
        "confidence": confidence,
        "tags": tags,
        "metadata": {
            "energy": 0.8,
            "mood": "dark",
            "instruments": ["drums", "bass"],
        },
    }


def create_mock_search_result(
    index_id: int = 1,
    score: float = 0.95,
) -> dict[str, Any]:
    """Helper to create a mock FAISS search result."""
    return {
        "index_id": index_id,
        "path": f"/path/to/sample_{index_id}.wav",
        "filename": f"sample_{index_id}.wav",
        "score": score,
        "metadata": {
            "bpm": 128,
            "key": "A minor",
            "energy": 0.8,
            "genre_labels": ["trap"],
            "mood_labels": ["dark"],
        },
    }


@pytest.fixture
def sample_analysis_result() -> dict[str, Any]:
    """Fixed sample analysis result for tests."""
    return create_mock_analysis_result()


@pytest.fixture
def multiple_search_results() -> list[dict[str, Any]]:
    """Generate multiple mock search results."""
    return [create_mock_search_result(i, 1.0 - i * 0.05) for i in range(1, 6)]
