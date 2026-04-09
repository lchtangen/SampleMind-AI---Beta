"""
SampleMind AI — Audio Data Models

Core enums and dataclasses used throughout the audio loading pipeline:
- AudioFormat: Supported audio file formats with format metadata
- LoadingStrategy: Loading quality/speed trade-off modes
- AudioMetadata: Comprehensive file + audio + musical metadata
- LoadedAudio: Container for raw audio array + associated metadata
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np


class AudioFormat(Enum):
    """Supported audio formats with detailed information"""

    WAV = {
        "ext": ".wav",
        "mime": "audio/wav",
        "compressed": False,
        "quality": "lossless",
    }
    FLAC = {
        "ext": ".flac",
        "mime": "audio/flac",
        "compressed": True,
        "quality": "lossless",
    }
    AIFF = {
        "ext": ".aiff",
        "mime": "audio/aiff",
        "compressed": False,
        "quality": "lossless",
    }
    MP3 = {"ext": ".mp3", "mime": "audio/mpeg", "compressed": True, "quality": "lossy"}
    AAC = {"ext": ".aac", "mime": "audio/aac", "compressed": True, "quality": "lossy"}
    M4A = {"ext": ".m4a", "mime": "audio/mp4", "compressed": True, "quality": "lossy"}
    OGG = {"ext": ".ogg", "mime": "audio/ogg", "compressed": True, "quality": "lossy"}
    WMA = {
        "ext": ".wma",
        "mime": "audio/x-ms-wma",
        "compressed": True,
        "quality": "lossy",
    }


class LoadingStrategy(Enum):
    """Audio loading strategies for different use cases"""

    FAST = "fast"  # Quick loading, lower quality for previews
    BALANCED = "balanced"  # Good balance of speed and quality
    QUALITY = "quality"  # High quality loading for analysis
    STREAMING = "streaming"  # Chunk-based loading for large files


@dataclass
class AudioMetadata:
    """Comprehensive audio file metadata"""

    # File information
    file_path: Path
    file_size: int
    file_hash: str
    format: AudioFormat
    creation_time: float
    modification_time: float

    # Audio properties
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int | None = None
    bitrate: int | None = None

    # Musical metadata
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    year: int | None = None
    track_number: int | None = None
    bpm: float | None = None
    key: str | None = None

    # Technical metadata
    codec: str | None = None
    encoder: str | None = None
    encoding_settings: dict[str, Any] = field(default_factory=dict)

    # Processing metadata
    load_time: float = 0.0
    strategy_used: LoadingStrategy = LoadingStrategy.BALANCED
    normalization_applied: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AudioMetadata":
        """Create metadata from dictionary"""
        data = dict(data)
        if "file_path" in data:
            data["file_path"] = Path(data["file_path"])
        if "format" in data:
            data["format"] = AudioFormat(data["format"])
        if "strategy_used" in data:
            data["strategy_used"] = LoadingStrategy(data["strategy_used"])
        return cls(**data)


@dataclass
class LoadedAudio:
    """Container for loaded audio data and metadata"""

    audio_data: np.ndarray
    metadata: AudioMetadata
    chunks: list[np.ndarray] | None = None  # For streaming
    is_stereo: bool = False
    peak_amplitude: float = 0.0
    rms_level: float = 0.0

    def get_duration_samples(self) -> int:
        """Get duration in samples"""
        return len(self.audio_data)

    def get_duration_seconds(self) -> float:
        """Get duration in seconds"""
        return len(self.audio_data) / self.metadata.sample_rate

    def to_mono(self) -> np.ndarray:
        """Convert to mono if stereo"""
        if self.is_stereo and len(self.audio_data.shape) > 1:
            return np.mean(self.audio_data, axis=1)
        return self.audio_data

    def normalize(self, target_level: float = 0.95) -> np.ndarray:
        """Normalize audio to target level"""
        peak = np.max(np.abs(self.audio_data))
        if peak > 0:
            normalized = self.audio_data * (target_level / peak)
            self.metadata.normalization_applied = True
            return normalized
        return self.audio_data
