#!/usr/bin/env python3
"""
SampleMind AI — Audio Loader (backward-compatibility shim)

This module re-exports the full public API from :mod:`samplemind.core.loading`
so that existing import paths continue to work unchanged:

    from samplemind.core.loader import AdvancedAudioLoader, AudioMetadata

New code should import from the canonical sub-package instead:

    from samplemind.core.loading import AdvancedAudioLoader, AudioMetadata
"""

# Re-export everything for backward compatibility
from samplemind.core.loading import (  # noqa: F401
    AdvancedAudioLoader,
    AudioFormat,
    AudioFormatDetector,
    AudioMetadata,
    LoadedAudio,
    LoadingStrategy,
    MetadataExtractor,
    create_loader_from_config,
)

__all__ = [
    "AdvancedAudioLoader",
    "AudioFormat",
    "AudioFormatDetector",
    "AudioMetadata",
    "LoadedAudio",
    "LoadingStrategy",
    "MetadataExtractor",
    "create_loader_from_config",
]
