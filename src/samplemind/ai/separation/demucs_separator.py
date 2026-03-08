#!/usr/bin/env python3
"""
SampleMind AI — Demucs Stem Separator
6-stem source separation using the htdemucs_6s model.

Uses ``demucs ^4.0.0`` to separate audio into:
  drums / bass / vocals / piano / guitar / other

CPU-only by default; GPU accelerated when torch.cuda is available.
Heavy work is dispatched to a ThreadPoolExecutor so callers stay non-blocking.

Follows the lazy-load + mock-fallback pattern from neural_engine.py.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy globals
# ---------------------------------------------------------------------------

_demucs_api: Any = None
_DEMUCS_AVAILABLE = False

STEM_NAMES = ("drums", "bass", "vocals", "piano", "guitar", "other")
DEFAULT_MODEL = "htdemucs_6s"


def _ensure_demucs() -> bool:
    global _demucs_api, _DEMUCS_AVAILABLE
    if _DEMUCS_AVAILABLE:
        return True
    try:
        import demucs.api as _api

        _demucs_api = _api
        _DEMUCS_AVAILABLE = True
    except ImportError:
        logger.warning("demucs not installed. Install with: poetry add 'demucs ^4.0.0'")
    return _DEMUCS_AVAILABLE


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class StemTrack:
    """A single separated stem."""

    name: str  # e.g. "drums"
    output_path: Optional[Path]  # None for in-memory only
    sample_rate: int = 44100


@dataclass
class SeparationResult:
    """Full output from StemSeparator."""

    stems: List[StemTrack] = field(default_factory=list)
    model_name: str = DEFAULT_MODEL
    source_path: str = ""
    output_dir: Optional[Path] = None
    processing_time: float = 0.0
    mock: bool = False

    @property
    def stem_names(self) -> List[str]:
        return [s.name for s in self.stems]

    def to_description(self) -> str:
        """Human-readable stem summary for use in AI prompts."""
        return (
            f"Separated with {self.model_name}: "
            + ", ".join(self.stem_names)
            + f" (source: {Path(self.source_path).name})"
        )


# ---------------------------------------------------------------------------
# Separator service
# ---------------------------------------------------------------------------


class StemSeparator:
    """
    Demucs-powered 6-stem source separator.

    Features:
    - Lazy model loading (first call only)
    - CPU / CUDA auto-detection
    - Async-safe via ThreadPoolExecutor
    - Configurable output directory
    - Mock mode for tests / missing deps

    Usage::

        separator = StemSeparator()
        result = await separator.separate("full_track.wav", output_dir="stems/")
        print(result.to_description())
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "auto",
        use_mock: bool = False,
        jobs: int = 1,
    ) -> None:
        """
        Args:
            model_name:  Demucs model identifier (default: ``htdemucs_6s``).
            device:      ``"auto"``, ``"cuda"``, or ``"cpu"``.
            use_mock:    Force mock mode (no actual separation performed).
            jobs:        Number of parallel jobs for multi-track batches.
        """
        self.model_name = model_name
        self.jobs = jobs
        self.use_mock = use_mock
        self._separator: Any = None

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
            logger.info("StemSeparator initialised in MOCK mode")
        else:
            logger.info(
                f"StemSeparator configured: model={model_name}, device={self.device}"
            )

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _load_model(self) -> None:
        """Lazy-load the Demucs separator on first use."""
        if self._separator is not None:
            return
        if not _ensure_demucs():
            self.use_mock = True
            return
        try:
            logger.info(f"Loading Demucs model: {self.model_name} on {self.device}")
            self._separator = _demucs_api.Separator(
                model=self.model_name,
                device=self.device,
                jobs=self.jobs,
            )
            logger.info("Demucs model loaded successfully")
        except Exception as exc:
            logger.error(f"Failed to load Demucs model: {exc}")
            logger.warning("Falling back to mock mode")
            self.use_mock = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def separate(
        self,
        audio_path: str | Path,
        output_dir: Optional[str | Path] = None,
    ) -> SeparationResult:
        """
        Separate a full audio track into stems.

        Args:
            audio_path:  Path to the input audio file.
            output_dir:  Directory to write stem files.  If ``None``, stems are
                         processed in-memory only (no files written).

        Returns:
            SeparationResult with paths to each stem file (or mock stems).
        """
        import asyncio

        start_time = time.time()
        audio_path = Path(audio_path)
        out_dir = Path(output_dir) if output_dir else None

        if self.use_mock or not _ensure_demucs():
            return self._mock_result(audio_path, out_dir, start_time)

        self._load_model()
        if self.use_mock:
            return self._mock_result(audio_path, out_dir, start_time)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as pool:
            stems = await loop.run_in_executor(
                pool,
                lambda: self._run_separation(audio_path, out_dir),
            )

        result = SeparationResult(
            stems=stems,
            model_name=self.model_name,
            source_path=str(audio_path),
            output_dir=out_dir,
            processing_time=time.time() - start_time,
        )
        logger.info(
            f"Separation complete ({result.processing_time:.1f}s): "
            f"{result.stem_names}"
        )
        return result

    def separate_sync(
        self,
        audio_path: str | Path,
        output_dir: Optional[str | Path] = None,
    ) -> SeparationResult:
        """Synchronous wrapper around :meth:`separate`."""
        import asyncio

        return asyncio.run(self.separate(audio_path, output_dir))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_separation(
        self, audio_path: Path, out_dir: Optional[Path]
    ) -> List[StemTrack]:
        """CPU-bound separation work executed in thread pool."""
        origin, separated = self._separator.separate_audio_file(str(audio_path))

        stems: List[StemTrack] = []
        for stem_name, waveform in separated.items():
            stem_path: Optional[Path] = None
            if out_dir is not None:
                out_dir.mkdir(parents=True, exist_ok=True)
                stem_path = out_dir / f"{audio_path.stem}_{stem_name}.wav"
                _demucs_api.save_audio(
                    waveform,
                    str(stem_path),
                    samplerate=self._separator.samplerate,
                )
            stems.append(
                StemTrack(
                    name=stem_name,
                    output_path=stem_path,
                    sample_rate=self._separator.samplerate,
                )
            )
        return stems

    def _mock_result(
        self,
        audio_path: Path,
        out_dir: Optional[Path],
        start_time: float,
    ) -> SeparationResult:
        stems = [StemTrack(name=n, output_path=None) for n in STEM_NAMES]
        return SeparationResult(
            stems=stems,
            model_name=f"mock-{self.model_name}",
            source_path=str(audio_path),
            output_dir=out_dir,
            processing_time=time.time() - start_time,
            mock=True,
        )
