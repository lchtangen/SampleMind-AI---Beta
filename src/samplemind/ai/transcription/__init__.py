"""SampleMind AI — audio transcription sub-package."""

from .whisper_transcriber import TranscriptionResult, WhisperTranscriber

__all__ = ["WhisperTranscriber", "TranscriptionResult"]
