#!/usr/bin/env python3
"""
SampleMind AI — Audio Loader (backward-compatibility shim)
==========================================================

This module is a **thin re-export layer** that keeps the original import path
working after the loader implementation was refactored into the
``samplemind.core.loading`` sub-package.

Why it exists:
  Older code and CLI commands import from ``samplemind.core.loader``.  Rather
  than update every call-site, this shim re-exports the full public API so
  both old and new import paths work:

  .. code-block:: python

      # Legacy (still works)
      from samplemind.core.loader import AdvancedAudioLoader, AudioMetadata

      # Canonical (preferred for new code)
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
