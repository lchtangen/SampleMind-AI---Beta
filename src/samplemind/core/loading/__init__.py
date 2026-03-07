"""
SampleMind AI — Audio Loading Sub-package

Public API surface for the loading pipeline:

  from samplemind.core.loading import AdvancedAudioLoader, AudioMetadata, LoadedAudio
"""

from .audio_loader import AdvancedAudioLoader, create_loader_from_config
from .format_detector import AudioFormatDetector
from .metadata_extractor import MetadataExtractor
from .models import AudioFormat, AudioMetadata, LoadedAudio, LoadingStrategy

__all__ = [
    # Loader
    "AdvancedAudioLoader",
    "create_loader_from_config",
    # Helper classes
    "AudioFormatDetector",
    "MetadataExtractor",
    # Models / enums
    "AudioFormat",
    "AudioMetadata",
    "LoadedAudio",
    "LoadingStrategy",
]
