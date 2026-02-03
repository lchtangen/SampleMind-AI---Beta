"""
MIDI Generation from Audio (Phase 13.3)

Extract musical information from audio and convert to MIDI:
- Melody extraction (monophonic melody)
- Chord detection and progression
- Drum pattern quantization
- Bassline extraction
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import librosa
import mido
import numpy as np
from mido import Message, MidiFile, MidiTrack

logger = logging.getLogger(__name__)


class MIDIExtractionType(str, Enum):
    """Types of MIDI extraction"""
    MELODY = "melody"           # Monophonic melody extraction
    HARMONY = "harmony"         # Chord detection
    RHYTHM = "rhythm"           # Drum/beat pattern
    BASS_LINE = "bass_line"     # Bass line extraction


class ChordType(str, Enum):
    """Common chord types"""
    MAJOR = "major"
    MINOR = "minor"
    MAJOR_7 = "maj7"
    MINOR_7 = "min7"
    DOMINANT_7 = "dom7"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    SUSPENDED = "sus"


@dataclass
class MidiNote:
    """Representation of a single MIDI note"""
    start_time: float       # Seconds
    duration: float         # Seconds
    pitch: int              # MIDI note number (0-127)
    velocity: int = 64      # Velocity (0-127)
    confidence: float = 1.0 # Confidence (0-1)

    def to_mido_events(self, tick_rate: float) -> tuple[Message, Message]:
        """Convert to mido note on/off messages"""
        start_ticks = int(self.start_time * tick_rate)
        duration_ticks = int(self.duration * tick_rate)

        note_on = Message('note_on', note=self.pitch, velocity=self.velocity, time=start_ticks)
        note_off = Message('note_off', note=self.pitch, velocity=0, time=duration_ticks)

        return note_on, note_off


@dataclass
class Chord:
    """Representation of a chord"""
    start_time: float           # Seconds
    duration: float             # Seconds
    root: int                   # Root note MIDI number
    chord_type: ChordType       # Chord type
    notes: list[int]            # MIDI notes in chord
    confidence: float = 1.0     # Confidence (0-1)

    def get_name(self) -> str:
        """Get chord name (e.g., 'C Major')"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        root_name = note_names[self.root % 12]
        return f"{root_name} {self.chord_type.value.title()}"


@dataclass
class MIDIExtractionResult:
    """Result of MIDI extraction"""
    extraction_type: MIDIExtractionType
    notes: list[MidiNote]           # For melody
    chords: list[Chord]             # For harmony
    tempo_bpm: float | None      # Detected tempo
    time_signature: tuple[int, int] | None  # (numerator, denominator)
    confidence: float               # Overall confidence (0-1)
    midi_file: MidiFile | None = None  # Generated MIDI file


class MIDIGenerator:
    """
    Generate MIDI from audio files using various extraction methods.

    Example:
        generator = MIDIGenerator(sample_rate=22050)
        result = generator.extract_melody("song.wav")
        result.midi_file.save("melody.mid")
    """

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize MIDI generator.

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        logger.info(f"MIDI Generator initialized (SR: {sample_rate}Hz)")

    def load_audio(self, file_path: Path) -> tuple[np.ndarray, int]:
        """Load audio file"""
        audio, sr = librosa.load(str(file_path), sr=self.sample_rate, mono=True)
        logger.info(f"Loaded audio: {audio.shape}, SR: {sr}")
        return audio, sr

    # ========================================================================
    # MELODY EXTRACTION
    # ========================================================================

    def extract_melody(
        self,
        audio: np.ndarray,
        min_duration: float = 0.1,
        confidence_threshold: float = 0.5,
    ) -> MIDIExtractionResult:
        """
        Extract monophonic melody from audio.

        Uses harmonic-percussive source separation + pitch tracking.

        Args:
            audio: Input audio array
            min_duration: Minimum note duration in seconds
            confidence_threshold: Minimum confidence for notes (0-1)

        Returns:
            MIDIExtractionResult with melody notes
        """
        # Separate harmonic component (melody)
        harmonic = librosa.effects.hpss(audio)[0]

        # Extract pitch using constant-Q transform
        cqt = librosa.cqt(harmonic, sr=self.sample_rate)
        cqt_magnitude = np.abs(cqt)

        # Get pitch contour
        pitches, confidences = librosa.piptrack(
            y=audio,
            sr=self.sample_rate,
            threshold=0.1,
            fmin=50,
            fmax=2000
        )

        # Convert pitch contour to MIDI notes
        notes = self._pitch_contour_to_notes(
            pitches,
            confidences,
            self.sample_rate,
            min_duration,
            confidence_threshold
        )

        # Estimate tempo
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=self.sample_rate)
        tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=self.sample_rate)[0]

        # Create MIDI file
        midi_file = self._create_midi_file(notes, tempo_bpm=tempo)

        logger.info(f"Extracted melody: {len(notes)} notes, tempo: {tempo:.1f} BPM")

        return MIDIExtractionResult(
            extraction_type=MIDIExtractionType.MELODY,
            notes=notes,
            chords=[],
            tempo_bpm=tempo,
            time_signature=(4, 4),
            confidence=np.mean([n.confidence for n in notes]) if notes else 0.0,
            midi_file=midi_file
        )

    def _pitch_contour_to_notes(
        self,
        pitches: np.ndarray,
        confidences: np.ndarray,
        sr: int,
        min_duration: float,
        confidence_threshold: float,
    ) -> list[MidiNote]:
        """Convert pitch contour to discrete notes"""
        notes = []
        hop_length = 512
        frame_length = hop_length * 4

        # Smooth confidence values
        confidences_smooth = librosa.util.normalize(confidences[0])

        current_pitch = None
        current_start = 0
        frame_time = 0

        for frame_idx in range(len(pitches[0])):
            frame_time = librosa.frames_to_time(frame_idx, sr=sr, hop_length=hop_length)
            pitch = pitches[0, frame_idx]
            confidence = confidences_smooth[frame_idx]

            if confidence > confidence_threshold and pitch > 0:
                midi_pitch = librosa.hz_to_midi(pitch)

                if current_pitch is None:
                    current_pitch = midi_pitch
                    current_start = frame_time
                elif abs(midi_pitch - current_pitch) < 1:
                    # Same note, continue
                    continue
                else:
                    # Note changed
                    if frame_time - current_start >= min_duration:
                        notes.append(MidiNote(
                            start_time=current_start,
                            duration=frame_time - current_start,
                            pitch=int(round(current_pitch)),
                            velocity=int(64 + confidence * 32),
                            confidence=confidence
                        ))
                    current_pitch = midi_pitch
                    current_start = frame_time
            else:
                # Silence or low confidence
                if current_pitch is not None and frame_time - current_start >= min_duration:
                    notes.append(MidiNote(
                        start_time=current_start,
                        duration=frame_time - current_start,
                        pitch=int(round(current_pitch)),
                        velocity=int(64 + confidence * 32),
                        confidence=confidence
                    ))
                current_pitch = None

        return notes

    # ========================================================================
    # CHORD DETECTION
    # ========================================================================

    def extract_chords(
        self,
        audio: np.ndarray,
        fmin: float = 50,
        fmax: float = 2000,
        resolution: int = 2,
    ) -> MIDIExtractionResult:
        """
        Detect chord progressions in audio.

        Args:
            audio: Input audio array
            fmin: Minimum frequency in Hz
            fmax: Maximum frequency in Hz
            resolution: Resolution in semitones per cent

        Returns:
            MIDIExtractionResult with detected chords
        """
        # Extract chroma features (pitch class distribution)
        chroma = librosa.feature.chroma_cqt(
            y=audio,
            sr=self.sample_rate,
            fmin=fmin,
            fmax=fmax
        )

        # Smooth chroma over time
        chroma_smooth = librosa.util.normalize(chroma, axis=0)

        # Detect chords from chroma
        chords = self._detect_chords_from_chroma(chroma_smooth, self.sample_rate)

        # Estimate tempo
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=self.sample_rate)[0]

        logger.info(f"Detected {len(chords)} chords, tempo: {tempo:.1f} BPM")

        return MIDIExtractionResult(
            extraction_type=MIDIExtractionType.HARMONY,
            notes=[],
            chords=chords,
            tempo_bpm=tempo,
            time_signature=(4, 4),
            confidence=np.mean([c.confidence for c in chords]) if chords else 0.0,
            midi_file=None
        )

    def _detect_chords_from_chroma(
        self,
        chroma: np.ndarray,
        sr: int,
    ) -> list[Chord]:
        """Detect chords from chroma features"""
        chords = []
        hop_length = 512
        frame_duration = hop_length / sr

        # Common chord templates (semitone offsets from root)
        chord_templates = {
            ChordType.MAJOR: [0, 4, 7],
            ChordType.MINOR: [0, 3, 7],
            ChordType.MAJOR_7: [0, 4, 7, 11],
            ChordType.MINOR_7: [0, 3, 7, 10],
            ChordType.DOMINANT_7: [0, 4, 7, 10],
            ChordType.DIMINISHED: [0, 3, 6],
        }

        # Find chord changes every ~0.5 seconds
        chord_frames = []
        for frame_idx in range(0, chroma.shape[1], int(0.5 * sr / hop_length)):
            if frame_idx >= chroma.shape[1]:
                break

            # Get chroma slice
            chroma_slice = chroma[:, frame_idx]

            # Try all roots
            best_chord = None
            best_score = -1

            for root in range(12):
                for chord_type, template in chord_templates.items():
                    score = 0
                    for offset in template:
                        pitch_class = (root + offset) % 12
                        score += chroma_slice[pitch_class]

                    if score > best_score:
                        best_score = score
                        best_chord = (root, chord_type, score)

            if best_chord:
                root, chord_type, score = best_chord
                frame_time = librosa.frames_to_time(frame_idx, sr=sr, hop_length=hop_length)
                confidence = float(best_score / 3.0)  # Normalize confidence

                chord = Chord(
                    start_time=frame_time,
                    duration=0.5,
                    root=root + 60,  # MIDI note C4 = 60
                    chord_type=chord_type,
                    notes=[root + 60 + offset for offset in chord_templates[chord_type]],
                    confidence=min(1.0, confidence)
                )
                chord_frames.append(chord)

        # Merge consecutive same chords
        merged_chords = []
        for chord in chord_frames:
            if merged_chords and merged_chords[-1].chord_type == chord.chord_type and \
               abs(merged_chords[-1].root - chord.root) < 1:
                # Same chord, extend duration
                merged_chords[-1].duration += 0.5
            else:
                merged_chords.append(chord)

        return merged_chords

    # ========================================================================
    # DRUM PATTERN EXTRACTION
    # ========================================================================

    def extract_drums(
        self,
        audio: np.ndarray,
        quantize_grid: int = 16,
    ) -> MIDIExtractionResult:
        """
        Extract drum pattern from audio.

        Args:
            audio: Input audio array
            quantize_grid: Quantization grid (16 = 16th notes)

        Returns:
            MIDIExtractionResult with drum pattern
        """
        # Separate percussion component
        percussive = librosa.effects.hpss(audio)[1]

        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            y=percussive,
            sr=self.sample_rate,
            units='frames'
        )

        # Convert to time
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)

        # Estimate tempo
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=self.sample_rate)[0]

        # Quantize onsets to grid
        quantized_notes = self._quantize_onsets(onset_times, tempo, quantize_grid)

        logger.info(f"Extracted drum pattern: {len(quantized_notes)} notes, tempo: {tempo:.1f} BPM")

        return MIDIExtractionResult(
            extraction_type=MIDIExtractionType.RHYTHM,
            notes=quantized_notes,
            chords=[],
            tempo_bpm=tempo,
            time_signature=(4, 4),
            confidence=0.8,  # Drums are usually well-detected
            midi_file=None
        )

    def _quantize_onsets(
        self,
        onset_times: np.ndarray,
        tempo: float,
        grid: int,
    ) -> list[MidiNote]:
        """Quantize onset times to a grid"""
        beat_duration = 60.0 / tempo  # Duration of one beat
        grid_duration = beat_duration / (grid / 4)  # Duration of one grid point

        quantized_notes = []
        current_grid_idx = 0
        note_pitch = 36  # Kick drum

        for onset_time in onset_times:
            grid_idx = round(onset_time / grid_duration)

            # Only add if on grid
            if grid_idx >= current_grid_idx:
                quantized_time = grid_idx * grid_duration

                note = MidiNote(
                    start_time=quantized_time,
                    duration=0.1,  # Short drum hit
                    pitch=note_pitch,
                    velocity=100,
                    confidence=0.8
                )
                quantized_notes.append(note)
                current_grid_idx = grid_idx + 1

        return quantized_notes

    # ========================================================================
    # MIDI FILE CREATION
    # ========================================================================

    def _create_midi_file(
        self,
        notes: list[MidiNote],
        tempo_bpm: float = 120.0,
        time_signature: tuple[int, int] = (4, 4),
    ) -> MidiFile:
        """Create a MIDI file from notes"""
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Set tempo
        tempo_us = int(60_000_000 / tempo_bpm)
        track.append(Message('program_change', program=0, time=0))
        track.append(mido.MetaMessage('set_tempo', tempo=tempo_us, time=0))

        # Add time signature
        track.append(mido.MetaMessage('time_signature', numerator=time_signature[0],
                                      denominator=time_signature[1], time=0))

        # Convert notes to MIDI messages
        tick_rate = mid.ticks_per_beat * (tempo_bpm / 60.0)

        last_time = 0
        for note in sorted(notes, key=lambda n: n.start_time):
            # Calculate time delta
            current_time = int(note.start_time * tick_rate)
            time_delta = current_time - last_time

            # Add note on
            note_on = Message('note_on', note=note.pitch, velocity=note.velocity, time=time_delta)
            track.append(note_on)

            # Add note off
            duration_ticks = int(note.duration * tick_rate)
            note_off = Message('note_off', note=note.pitch, velocity=0, time=duration_ticks)
            track.append(note_off)

            last_time = current_time + duration_ticks

        return mid

    def save_midi(self, midi_file: MidiFile, output_path: Path) -> None:
        """Save MIDI file to disk"""
        midi_file.save(str(output_path))
        logger.info(f"Saved MIDI to {output_path}")

    # ========================================================================
    # HIGH-LEVEL EXTRACTION
    # ========================================================================

    def extract(
        self,
        file_path: Path,
        extraction_type: MIDIExtractionType = MIDIExtractionType.MELODY,
        **kwargs
    ) -> MIDIExtractionResult:
        """
        Extract MIDI from audio file.

        Args:
            file_path: Path to audio file
            extraction_type: Type of extraction (melody, harmony, rhythm)
            **kwargs: Additional arguments for extraction method

        Returns:
            MIDIExtractionResult with extracted MIDI data
        """
        audio, sr = self.load_audio(file_path)

        if extraction_type == MIDIExtractionType.MELODY:
            return self.extract_melody(audio, **kwargs)
        elif extraction_type == MIDIExtractionType.HARMONY:
            return self.extract_chords(audio, **kwargs)
        elif extraction_type == MIDIExtractionType.RHYTHM:
            return self.extract_drums(audio, **kwargs)
        else:
            raise ValueError(f"Unknown extraction type: {extraction_type}")


__all__ = [
    "MIDIGenerator",
    "MIDIExtractionType",
    "ChordType",
    "MidiNote",
    "Chord",
    "MIDIExtractionResult",
]
