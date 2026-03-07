#!/usr/bin/env python3
"""
SampleMind AI — MIDI Converter
Audio-to-MIDI transcription via Spotify's basic-pitch library.

Uses ``basic-pitch ^0.4.0`` to detect pitched notes in audio and export them
as standard MIDI files, with optional per-note confidence filtering.

Follows the lazy-load + mock-fallback pattern from neural_engine.py.
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy globals
# ---------------------------------------------------------------------------

_predict: Any = None
_note_creation: Any = None
_BASIC_PITCH_AVAILABLE = False


def _ensure_basic_pitch() -> bool:
    global _predict, _note_creation, _BASIC_PITCH_AVAILABLE
    if _BASIC_PITCH_AVAILABLE:
        return True
    try:
        from basic_pitch import inference as _inf
        from basic_pitch import note_creation as _nc
        _predict = _inf.predict
        _note_creation = _nc
        _BASIC_PITCH_AVAILABLE = True
    except ImportError:
        logger.warning(
            "basic-pitch not installed. Install with: poetry add 'basic-pitch ^0.4.0'"
        )
    return _BASIC_PITCH_AVAILABLE


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class DetectedNote:
    """A single detected pitched note."""
    pitch_midi: int          # MIDI note number (0–127)
    start_time: float        # seconds
    end_time: float          # seconds
    confidence: float        # model raw confidence (0–1)
    amplitude: float = 0.0   # normalised amplitude


@dataclass
class MidiConversionResult:
    """Output from MidiConverter."""

    notes: List[DetectedNote] = field(default_factory=list)
    midi_path: Optional[Path] = None
    source_path: str = ""
    model_output_path: Optional[Path] = None
    processing_time: float = 0.0
    mock: bool = False

    @property
    def note_count(self) -> int:
        return len(self.notes)

    @property
    def pitch_range(self) -> Tuple[int, int]:
        if not self.notes:
            return (0, 0)
        pitches = [n.pitch_midi for n in self.notes]
        return (min(pitches), max(pitches))

    def to_summary(self) -> str:
        return (
            f"{self.note_count} notes detected, "
            f"pitch range {self.pitch_range[0]}–{self.pitch_range[1]} MIDI, "
            f"source: {Path(self.source_path).name}"
        )


# ---------------------------------------------------------------------------
# Converter service
# ---------------------------------------------------------------------------

class MidiConverter:
    """
    Basic-pitch-powered audio-to-MIDI transcription service.

    Features:
    - Lazy model loading (first call only)
    - Configurable confidence threshold
    - Optional MIDI file export
    - Async-safe via ThreadPoolExecutor
    - Mock mode for tests / missing deps

    Usage::

        converter = MidiConverter()
        result = await converter.convert("melody.wav", output_dir="midi/")
        print(result.to_summary())
    """

    def __init__(
        self,
        minimum_note_length: float = 0.058,
        minimum_frequency: Optional[float] = None,
        maximum_frequency: Optional[float] = None,
        onset_threshold: float = 0.5,
        frame_threshold: float = 0.3,
        melodia_trick: bool = True,
        use_mock: bool = False,
    ) -> None:
        """
        Args:
            minimum_note_length:  Minimum duration (seconds) for a note to be kept.
            minimum_frequency:    Lowest pitch to detect (Hz).  ``None`` = no limit.
            maximum_frequency:    Highest pitch to detect (Hz).  ``None`` = no limit.
            onset_threshold:      Sensitivity for note onset detection (0–1).
            frame_threshold:      Per-frame activation threshold (0–1).
            melodia_trick:        Apply melodia trick to reduce spurious notes.
            use_mock:             Force mock mode.
        """
        self.minimum_note_length = minimum_note_length
        self.minimum_frequency = minimum_frequency
        self.maximum_frequency = maximum_frequency
        self.onset_threshold = onset_threshold
        self.frame_threshold = frame_threshold
        self.melodia_trick = melodia_trick
        self.use_mock = use_mock

        if use_mock:
            logger.info("MidiConverter initialised in MOCK mode")
        else:
            logger.info(
                f"MidiConverter configured: onset_threshold={onset_threshold}, "
                f"frame_threshold={frame_threshold}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def convert(
        self,
        audio_path: str | Path,
        output_dir: Optional[str | Path] = None,
        midi_filename: Optional[str] = None,
    ) -> MidiConversionResult:
        """
        Transcribe pitched audio into MIDI notes.

        Args:
            audio_path:     Path to the audio file (WAV, MP3, FLAC, etc.).
            output_dir:     Directory to write the MIDI file.  If ``None``, the
                            MIDI data is returned in-memory only.
            midi_filename:  Override filename for the MIDI output.

        Returns:
            MidiConversionResult with detected notes and optional MIDI path.
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        start_time = time.time()
        audio_path = Path(audio_path)

        if self.use_mock or not _ensure_basic_pitch():
            return self._mock_result(audio_path, start_time)

        loop = asyncio.get_event_loop()
        out_dir = Path(output_dir) if output_dir else None

        with ThreadPoolExecutor(max_workers=1) as pool:
            result = await loop.run_in_executor(
                pool,
                lambda: self._run_conversion(audio_path, out_dir, midi_filename),
            )
        result.processing_time = time.time() - start_time
        logger.info(
            f"MIDI conversion complete ({result.processing_time:.2f}s): "
            f"{result.to_summary()}"
        )
        return result

    def convert_sync(
        self,
        audio_path: str | Path,
        output_dir: Optional[str | Path] = None,
    ) -> MidiConversionResult:
        """Synchronous wrapper around :meth:`convert`."""
        import asyncio
        return asyncio.run(self.convert(audio_path, output_dir))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_conversion(
        self,
        audio_path: Path,
        out_dir: Optional[Path],
        midi_filename: Optional[str],
    ) -> MidiConversionResult:
        """CPU-bound basic-pitch inference — runs in thread pool."""
        model_output, midi_data, note_events = _predict(
            str(audio_path),
            onset_threshold=self.onset_threshold,
            frame_threshold=self.frame_threshold,
            minimum_note_length=self.minimum_note_length,
            minimum_frequency=self.minimum_frequency,
            maximum_frequency=self.maximum_frequency,
            melodia_trick=self.melodia_trick,
        )

        # Convert note events to DetectedNote objects
        notes: List[DetectedNote] = []
        for event in note_events:
            # basic-pitch note events: (start_time, end_time, pitch_midi, amplitude, confidence)
            if isinstance(event, (list, tuple)) and len(event) >= 3:
                notes.append(
                    DetectedNote(
                        pitch_midi=int(event[2]),
                        start_time=float(event[0]),
                        end_time=float(event[1]),
                        confidence=float(event[4]) if len(event) > 4 else 0.9,
                        amplitude=float(event[3]) if len(event) > 3 else 0.5,
                    )
                )

        midi_path: Optional[Path] = None
        if out_dir is not None and midi_data is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
            fname = midi_filename or f"{audio_path.stem}.mid"
            midi_path = out_dir / fname
            with open(midi_path, "wb") as f:
                midi_data.write(f)

        return MidiConversionResult(
            notes=notes,
            midi_path=midi_path,
            source_path=str(audio_path),
        )

    def _mock_result(self, audio_path: Path, start_time: float) -> MidiConversionResult:
        """Return deterministic mock output for tests."""
        mock_notes = [
            DetectedNote(pitch_midi=60, start_time=0.0, end_time=0.5, confidence=0.9),
            DetectedNote(pitch_midi=64, start_time=0.5, end_time=1.0, confidence=0.85),
            DetectedNote(pitch_midi=67, start_time=1.0, end_time=1.5, confidence=0.88),
        ]
        return MidiConversionResult(
            notes=mock_notes,
            source_path=str(audio_path),
            processing_time=time.time() - start_time,
            mock=True,
        )
