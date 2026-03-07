#!/usr/bin/env python3
"""
SampleMind AI — Whisper Transcriber
Offline speech-to-text and lyric transcription using faster-whisper.

Uses ``faster-whisper ^1.1.0`` (CTranslate2-based) for ~4× faster inference
than the original Whisper implementation with a smaller memory footprint.

Follows the lazy-load + mock-fallback pattern from neural_engine.py.

Supported models:
  tiny / base / small / medium / large-v3 / large-v3-turbo
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy globals
# ---------------------------------------------------------------------------

_WhisperModel: Any = None
_FASTER_WHISPER_AVAILABLE = False


def _ensure_faster_whisper() -> bool:
    global _WhisperModel, _FASTER_WHISPER_AVAILABLE
    if _FASTER_WHISPER_AVAILABLE:
        return True
    try:
        from faster_whisper import WhisperModel as _WM
        _WhisperModel = _WM
        _FASTER_WHISPER_AVAILABLE = True
    except ImportError:
        logger.warning(
            "faster-whisper not installed. Install with: poetry add 'faster-whisper ^1.1.0'"
        )
    return _FASTER_WHISPER_AVAILABLE


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class TranscriptionSegment:
    """A single timed transcript segment."""
    start: float
    end: float
    text: str
    confidence: float = 0.0


@dataclass
class TranscriptionResult:
    """Full transcription output from WhisperTranscriber."""

    # Full transcript
    text: str = ""
    language: str = ""
    language_probability: float = 0.0

    # Segments with timestamps
    segments: List[TranscriptionSegment] = field(default_factory=list)

    # Performance metadata
    model_name: str = ""
    processing_time: float = 0.0
    audio_duration: float = 0.0
    mock: bool = False


# ---------------------------------------------------------------------------
# Transcriber service
# ---------------------------------------------------------------------------

class WhisperTranscriber:
    """
    Offline audio-to-text transcription using faster-whisper.

    Features:
    - Lazy model loading (first call only)
    - CPU / CUDA / MPS auto-detection
    - Mock mode for tests / missing deps
    - VAD filter to skip silent regions

    Usage::

        transcriber = WhisperTranscriber(model_size="large-v3")
        result = await transcriber.transcribe("vocals.wav")
        print(result.text)
    """

    SUPPORTED_MODELS = (
        "tiny", "base", "small", "medium",
        "large-v3", "large-v3-turbo",
    )

    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "auto",
        compute_type: str = "int8",
        use_mock: bool = False,
    ) -> None:
        """
        Args:
            model_size:    faster-whisper model variant.
            device:        ``"auto"`` selects CUDA → CPU.  Pass ``"cuda"`` or ``"cpu"`` to override.
            compute_type:  Quantisation type.  ``"int8"`` is fastest on CPU.
            use_mock:      Force mock mode (returns deterministic placeholder output).
        """
        if model_size not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model_size!r}. "
                f"Choose from {self.SUPPORTED_MODELS}"
            )
        self.model_size = model_size
        self.compute_type = compute_type
        self.use_mock = use_mock
        self._model: Any = None

        # Resolve device
        if device == "auto":
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"
        else:
            self.device = device

        if use_mock:
            logger.info("WhisperTranscriber initialised in MOCK mode")
        else:
            logger.info(
                f"WhisperTranscriber configured: model={model_size}, "
                f"device={self.device}, compute_type={compute_type}"
            )

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _load_model(self) -> None:
        """Lazy-load the WhisperModel on first use."""
        if self._model is not None:
            return
        if not _ensure_faster_whisper():
            self.use_mock = True
            return
        try:
            logger.info(f"Loading faster-whisper model: {self.model_size} on {self.device}")
            self._model = _WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("faster-whisper model loaded successfully")
        except Exception as exc:
            logger.error(f"Failed to load faster-whisper model: {exc}")
            logger.warning("Falling back to mock mode")
            self.use_mock = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> TranscriptionResult:
        """
        Transcribe speech / lyrics from an audio file.

        Args:
            audio_path:  Path to the audio file (WAV, MP3, FLAC, etc.).
            language:    BCP-47 language code hint (e.g. ``"en"``).
                         ``None`` triggers automatic detection.
            beam_size:   Beam search width. Higher = more accurate, slower.
            vad_filter:  If ``True``, skip silent segments (faster on music).

        Returns:
            TranscriptionResult with full text and timed segments.
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        start_time = time.time()
        audio_path = Path(audio_path)

        if self.use_mock or not _ensure_faster_whisper():
            return self._mock_result(audio_path, start_time)

        self._load_model()
        if self.use_mock:  # may have been set during _load_model
            return self._mock_result(audio_path, start_time)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as pool:
            result = await loop.run_in_executor(
                pool,
                lambda: self._run_transcription(
                    str(audio_path), language, beam_size, vad_filter
                ),
            )
        result.processing_time = time.time() - start_time
        logger.info(
            f"Transcription complete ({result.processing_time:.2f}s, "
            f"lang={result.language}, segments={len(result.segments)})"
        )
        return result

    def transcribe_sync(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> TranscriptionResult:
        """Synchronous wrapper around :meth:`transcribe`."""
        import asyncio
        return asyncio.run(
            self.transcribe(audio_path, language, beam_size, vad_filter)
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_transcription(
        self,
        path: str,
        language: Optional[str],
        beam_size: int,
        vad_filter: bool,
    ) -> TranscriptionResult:
        """CPU-bound transcription work executed in a thread pool."""
        kwargs: Dict[str, Any] = {
            "beam_size": beam_size,
            "vad_filter": vad_filter,
        }
        if language:
            kwargs["language"] = language

        segments_iter, info = self._model.transcribe(path, **kwargs)

        full_text_parts: List[str] = []
        segments: List[TranscriptionSegment] = []
        for seg in segments_iter:
            full_text_parts.append(seg.text)
            segments.append(
                TranscriptionSegment(
                    start=seg.start,
                    end=seg.end,
                    text=seg.text.strip(),
                    confidence=getattr(seg, "avg_logprob", 0.0),
                )
            )

        return TranscriptionResult(
            text=" ".join(full_text_parts).strip(),
            language=info.language,
            language_probability=info.language_probability,
            segments=segments,
            model_name=self.model_size,
            audio_duration=info.duration,
        )

    def _mock_result(self, audio_path: Path, start_time: float) -> TranscriptionResult:
        """Return deterministic mock output for tests."""
        return TranscriptionResult(
            text="[Mock transcription — faster-whisper not available]",
            language="en",
            language_probability=1.0,
            segments=[
                TranscriptionSegment(start=0.0, end=1.0, text="Mock segment", confidence=0.9)
            ],
            model_name=f"mock-{self.model_size}",
            processing_time=time.time() - start_time,
            mock=True,
        )
