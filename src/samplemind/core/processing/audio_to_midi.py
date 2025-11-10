import importlib.util
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import OptionalDependencyError

logger = logging.getLogger(__name__)


@dataclass
class MidiNoteEvent:
    """Structured representation of a Basic Pitch note event."""

    start_time: float
    end_time: float
    midi_pitch: int
    amplitude: float
    pitch_bends: Optional[List[int]]


@dataclass
class AudioToMIDIResult:
    """Container for MIDI conversion output."""

    midi_path: Path
    note_events: List[MidiNoteEvent]
    metadata: Dict[str, Any]


class AudioToMIDIConverter:
    """Audio-to-MIDI conversion powered by Spotify's Basic Pitch."""

    def __init__(
        self,
        onset_threshold: float = 0.5,
        frame_threshold: float = 0.3,
        minimum_note_length: float = 0.1,
        multiple_pitch_bends: bool = False,
        midi_tempo: float = 120.0,
    ) -> None:
        self.onset_threshold = onset_threshold
        self.frame_threshold = frame_threshold
        self.minimum_note_length = minimum_note_length
        self.multiple_pitch_bends = multiple_pitch_bends
        self.midi_tempo = midi_tempo

    @staticmethod
    def _assert_dependency() -> None:
        if importlib.util.find_spec("basic_pitch") is None:
            raise OptionalDependencyError(
                "basic-pitch",
                "Basic Pitch is required for audio-to-MIDI conversion. Install it with `pip install basic-pitch`.",
            )

    def convert(
        self,
        audio_path: Path,
        output_directory: Optional[Path] = None,
        midi_filename: Optional[str] = None,
        minimum_frequency: Optional[float] = None,
        maximum_frequency: Optional[float] = None,
    ) -> AudioToMIDIResult:
        """Convert an audio file into a MIDI representation."""

        self._assert_dependency()

        from basic_pitch.inference import predict

        audio_path = Path(audio_path).expanduser().resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        output_dir = output_directory or Path(tempfile.mkdtemp(prefix="samplemind-midi-"))
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        midi_name = midi_filename or f"{audio_path.stem}.mid"
        midi_path = output_dir / midi_name

        logger.info("Running Basic Pitch on %s", audio_path)
        model_outputs, midi, note_events = predict(
            audio_path=audio_path,
            onset_threshold=self.onset_threshold,
            frame_threshold=self.frame_threshold,
            minimum_note_length=self.minimum_note_length,
            minimum_frequency=minimum_frequency,
            maximum_frequency=maximum_frequency,
            multiple_pitch_bends=self.multiple_pitch_bends,
            midi_tempo=self.midi_tempo,
        )

        midi.write(midi_path)

        parsed_notes = [
            MidiNoteEvent(
                start_time=float(event[0]),
                end_time=float(event[1]),
                midi_pitch=int(event[2]),
                amplitude=float(event[3]),
                pitch_bends=list(event[4]) if len(event) > 4 and event[4] is not None else None,
            )
            for event in note_events
        ]

        metadata: Dict[str, Any] = {
            "onset_threshold": self.onset_threshold,
            "frame_threshold": self.frame_threshold,
            "minimum_note_length": self.minimum_note_length,
            "multiple_pitch_bends": self.multiple_pitch_bends,
            "midi_tempo": self.midi_tempo,
            "minimum_frequency": minimum_frequency,
            "maximum_frequency": maximum_frequency,
            "model_outputs": {k: v.tolist() for k, v in model_outputs.items()},
        }

        return AudioToMIDIResult(
            midi_path=midi_path,
            note_events=parsed_notes,
            metadata=metadata,
        )
