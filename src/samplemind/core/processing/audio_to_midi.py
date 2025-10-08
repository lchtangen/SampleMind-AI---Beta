"""
Audio-to-MIDI Converter

Convert audio files to MIDI using AI-powered pitch detection and note extraction.

Supports:
- Monophonic audio (single melody line)
- Polyphonic audio (chords and multiple notes)
- Percussion/drums to MIDI
- Real-time conversion
"""

import asyncio
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import librosa
import mido
from mido import MidiFile, MidiTrack, Message
from loguru import logger


class MIDIConversionMode(str, Enum):
    """MIDI conversion modes"""
    MONOPHONIC = "monophonic"  # Single note melody
    POLYPHONIC = "polyphonic"  # Multiple simultaneous notes/chords
    PERCUSSION = "percussion"  # Drums and percussion
    AUTO = "auto"  # Automatically detect best mode


class AudioToMIDIConverter:
    """
    Convert audio files to MIDI using AI-powered pitch detection

    Uses librosa for audio analysis and pitch detection, then converts
    detected notes to MIDI format.

    Example:
        >>> converter = AudioToMIDIConverter()
        >>> midi_file = await converter.convert_to_midi(
        ...     "melody.mp3",
        ...     mode=MIDIConversionMode.MONOPHONIC
        ... )
        >>> print(f"Saved to: {midi_file}")
    """

    def __init__(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        sample_rate: int = 22050
    ):
        """
        Initialize converter

        Args:
            output_dir: Directory to save MIDI files
            sample_rate: Sample rate for audio processing
        """
        self.output_dir = Path(output_dir) if output_dir else Path("./output/midi")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_rate = sample_rate

        # Statistics
        self.total_conversions = 0
        self.conversion_cache: Dict[str, Path] = {}

        logger.info(f"AudioToMIDIConverter initialized (sr={sample_rate})")

    async def convert_to_midi(
        self,
        audio_file: Union[str, Path],
        mode: MIDIConversionMode = MIDIConversionMode.AUTO,
        tempo: Optional[float] = None,
        min_note_duration: float = 0.1
    ) -> Path:
        """
        Convert audio file to MIDI

        Args:
            audio_file: Path to audio file
            mode: Conversion mode (mono/poly/percussion/auto)
            tempo: Tempo in BPM (auto-detected if None)
            min_note_duration: Minimum note duration in seconds

        Returns:
            Path to generated MIDI file

        Raises:
            ValueError: If file doesn't exist
            RuntimeError: If conversion fails
        """
        audio_file = Path(audio_file)
        if not audio_file.exists():
            raise ValueError(f"Audio file not found: {audio_file}")

        # Check cache
        cache_key = f"{audio_file}:{mode.value}"
        if cache_key in self.conversion_cache:
            logger.info(f"Using cached MIDI for {audio_file.name}")
            return self.conversion_cache[cache_key]

        logger.info(f"Converting {audio_file.name} to MIDI (mode: {mode})")

        try:
            # Load audio
            y, sr = librosa.load(audio_file, sr=self.sample_rate)

            # Auto-detect mode if needed
            if mode == MIDIConversionMode.AUTO:
                mode = self._detect_best_mode(y, sr)
                logger.info(f"Auto-detected mode: {mode}")

            # Detect tempo if not provided
            if tempo is None:
                tempo = self._detect_tempo(y, sr)
                logger.info(f"Detected tempo: {tempo:.1f} BPM")

            # Extract notes based on mode
            if mode == MIDIConversionMode.MONOPHONIC:
                notes = await self._extract_monophonic_notes(y, sr, min_note_duration)
            elif mode == MIDIConversionMode.POLYPHONIC:
                notes = await self._extract_polyphonic_notes(y, sr, min_note_duration)
            else:  # PERCUSSION
                notes = await self._extract_percussion_notes(y, sr)

            # Create MIDI file
            output_path = self.output_dir / f"{audio_file.stem}.mid"
            self._create_midi_file(notes, tempo, output_path)

            # Cache result
            self.conversion_cache[cache_key] = output_path
            self.total_conversions += 1

            logger.info(f"Successfully converted to MIDI: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"MIDI conversion failed: {e}")
            raise RuntimeError(f"Failed to convert {audio_file.name} to MIDI: {e}")

    def _detect_best_mode(self, y: np.ndarray, sr: int) -> MIDIConversionMode:
        """Automatically detect best conversion mode"""
        # Analyze audio characteristics
        # Check for percussive vs harmonic content
        y_harmonic, y_percussive = librosa.effects.hpss(y)

        harmonic_energy = np.sum(y_harmonic ** 2)
        percussive_energy = np.sum(y_percussive ** 2)

        if percussive_energy > harmonic_energy * 2:
            return MIDIConversionMode.PERCUSSION

        # Check for polyphonic content using spectral complexity
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        active_notes = np.sum(chroma > 0.5, axis=0)
        avg_polyphony = np.mean(active_notes)

        if avg_polyphony > 2:
            return MIDIConversionMode.POLYPHONIC
        else:
            return MIDIConversionMode.MONOPHONIC

    def _detect_tempo(self, y: np.ndarray, sr: int) -> float:
        """Detect tempo from audio"""
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return float(tempo.item() if hasattr(tempo, 'item') else tempo)

    async def _extract_monophonic_notes(
        self,
        y: np.ndarray,
        sr: int,
        min_duration: float
    ) -> List[Tuple[float, float, int, int]]:
        """
        Extract notes from monophonic audio

        Returns:
            List of (start_time, duration, pitch, velocity) tuples
        """
        # Use piptrack for pitch detection
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        # Extract pitch over time
        notes = []
        hop_length = 512
        frame_duration = hop_length / sr

        current_note = None
        note_start = 0.0

        for i in range(pitches.shape[1]):
            # Get most prominent pitch in frame
            index = magnitudes[:, i].argmax()
            pitch_hz = pitches[index, i]

            if pitch_hz > 0:  # Valid pitch detected
                midi_note = self._hz_to_midi(pitch_hz)
                velocity = int(min(127, magnitudes[index, i] * 127))

                if current_note is None:
                    # Start new note
                    current_note = midi_note
                    note_start = i * frame_duration
                elif abs(current_note - midi_note) > 1:
                    # Pitch changed - end previous note, start new one
                    duration = i * frame_duration - note_start
                    if duration >= min_duration:
                        notes.append((note_start, duration, current_note, velocity))

                    current_note = midi_note
                    note_start = i * frame_duration
            else:
                # Silence - end current note if any
                if current_note is not None:
                    duration = i * frame_duration - note_start
                    if duration >= min_duration:
                        notes.append((note_start, duration, current_note, 100))
                    current_note = None

        # End final note if still active
        if current_note is not None:
            duration = len(y) / sr - note_start
            if duration >= min_duration:
                notes.append((note_start, duration, current_note, 100))

        logger.info(f"Extracted {len(notes)} monophonic notes")
        return notes

    async def _extract_polyphonic_notes(
        self,
        y: np.ndarray,
        sr: int,
        min_duration: float
    ) -> List[Tuple[float, float, int, int]]:
        """
        Extract notes from polyphonic audio (chords)

        Returns:
            List of (start_time, duration, pitch, velocity) tuples
        """
        # Use constant-Q transform for better frequency resolution
        C = librosa.cqt(y=y, sr=sr)
        C_mag = np.abs(C)

        # Convert to chroma
        chroma = librosa.feature.chroma_cqt(C=C_mag, sr=sr)

        notes = []
        hop_length = 512
        frame_duration = hop_length / sr

        # Track active notes
        active_notes = {}  # {pitch: start_time}

        for i in range(chroma.shape[1]):
            # Find active pitches in this frame
            active_pitches = np.where(chroma[:, i] > 0.5)[0]

            current_frame_notes = set()
            for pitch_class in active_pitches:
                # Convert chroma to MIDI (C=60 as base)
                midi_note = 60 + pitch_class
                current_frame_notes.add(midi_note)

                if midi_note not in active_notes:
                    # New note started
                    active_notes[midi_note] = i * frame_duration

            # Check for notes that ended
            ended_notes = set(active_notes.keys()) - current_frame_notes
            for midi_note in ended_notes:
                start_time = active_notes[midi_note]
                duration = i * frame_duration - start_time
                if duration >= min_duration:
                    notes.append((start_time, duration, midi_note, 100))
                del active_notes[midi_note]

        # End remaining active notes
        final_time = len(y) / sr
        for midi_note, start_time in active_notes.items():
            duration = final_time - start_time
            if duration >= min_duration:
                notes.append((start_time, duration, midi_note, 100))

        logger.info(f"Extracted {len(notes)} polyphonic notes")
        return notes

    async def _extract_percussion_notes(
        self,
        y: np.ndarray,
        sr: int
    ) -> List[Tuple[float, float, int, int]]:
        """
        Extract percussion hits and map to MIDI drums

        Returns:
            List of (start_time, duration, pitch, velocity) tuples
        """
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        # Get onset strengths for velocity
        onset_strength = librosa.onset.onset_strength(y=y, sr=sr)

        notes = []
        for i, time in enumerate(onset_times):
            # Map to GM drum kit (simplified)
            # Would need spectral analysis to distinguish kick/snare/hihat
            drum_note = 36  # Bass drum 1 (C1)
            velocity = int(min(127, onset_strength[onset_frames[i]] * 127))

            notes.append((time, 0.1, drum_note, velocity))

        logger.info(f"Extracted {len(notes)} percussion hits")
        return notes

    def _hz_to_midi(self, hz: float) -> int:
        """Convert frequency in Hz to MIDI note number"""
        if hz <= 0:
            return 0
        return int(round(69 + 12 * np.log2(hz / 440.0)))

    def _create_midi_file(
        self,
        notes: List[Tuple[float, float, int, int]],
        tempo: float,
        output_path: Path
    ):
        """Create MIDI file from extracted notes"""
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Set tempo
        track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))

        # Convert notes to MIDI messages
        # Sort by start time
        notes = sorted(notes, key=lambda x: x[0])

        current_time = 0
        for start_time, duration, pitch, velocity in notes:
            # Calculate delta time in ticks
            delta_time = int((start_time - current_time) * mid.ticks_per_beat * (tempo / 60))
            delta_time = max(0, delta_time)

            # Note on
            track.append(Message('note_on', note=pitch, velocity=velocity, time=delta_time))

            # Note off
            duration_ticks = int(duration * mid.ticks_per_beat * (tempo / 60))
            track.append(Message('note_off', note=pitch, velocity=0, time=duration_ticks))

            current_time = start_time + duration

        # Save file
        mid.save(output_path)
        logger.info(f"MIDI file saved: {output_path} ({len(notes)} notes)")

    async def batch_convert(
        self,
        audio_files: List[Union[str, Path]],
        mode: MIDIConversionMode = MIDIConversionMode.AUTO,
        max_concurrent: int = 3
    ) -> Dict[Path, Path]:
        """
        Batch convert multiple audio files to MIDI

        Args:
            audio_files: List of audio files
            mode: Conversion mode
            max_concurrent: Maximum concurrent conversions

        Returns:
            Dictionary mapping input files to MIDI files
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_file(file: Union[str, Path]):
            async with semaphore:
                try:
                    midi_path = await self.convert_to_midi(file, mode)
                    return Path(file), midi_path
                except Exception as e:
                    logger.error(f"Failed to convert {file}: {e}")
                    return Path(file), None

        tasks = [process_file(f) for f in audio_files]
        results = await asyncio.gather(*tasks)

        return {audio: midi for audio, midi in results if midi is not None}

    def get_stats(self) -> dict:
        """Get converter statistics"""
        return {
            "total_conversions": self.total_conversions,
            "cached_files": len(self.conversion_cache),
            "output_directory": str(self.output_dir),
            "sample_rate": self.sample_rate,
        }


# Convenience function
async def convert_audio_to_midi(
    audio_file: Union[str, Path],
    mode: Union[MIDIConversionMode, str] = "auto",
    output_path: Optional[Union[str, Path]] = None
) -> Path:
    """
    Convenience function for quick audio-to-MIDI conversion

    Example:
        >>> midi_file = await convert_audio_to_midi("melody.mp3")
        >>> print(f"Saved to: {midi_file}")
    """
    converter = AudioToMIDIConverter()

    if isinstance(mode, str):
        mode = MIDIConversionMode(mode)

    return await converter.convert_to_midi(audio_file, mode)
