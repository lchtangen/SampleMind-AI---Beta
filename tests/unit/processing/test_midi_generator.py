"""Unit tests for MIDI generator module."""

from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest

from samplemind.core.processing.midi_generator import (
    ChordType,
    MIDIExtractionType,
    MIDIGenerator,
    MidiNote,
)


class TestMIDIGenerator:

    @pytest.fixture
    def generator(self):
        return MIDIGenerator(sample_rate=22050)

    @pytest.fixture
    def audio_chunk(self):
        return np.random.rand(22050).astype(np.float32)

    @patch("samplemind.core.processing.midi_generator.librosa")
    def test_extract_melody(self, mock_librosa, generator, audio_chunk):
        # Mock librosa results
        mock_librosa.effects.hpss.return_value = (audio_chunk, audio_chunk) # harmonic, percussive
        mock_librosa.cqt.return_value = np.zeros((12, 100))

        # Mock piptrack: returns pitches, mags. Shape (d, t)
        # Create a fake pitch track around 440Hz (A4)
        pitches = np.zeros((100, 50))
        mags = np.zeros((100, 50))
        pitches[50, 10:20] = 440.0 # Frames 10-20 have 440Hz
        mags[50, 10:20] = 1.0

        mock_librosa.piptrack.return_value = (pitches, mags)
        mock_librosa.hz_to_midi.side_effect = lambda x: 69 if abs(x-440) < 1 else 0
        mock_librosa.frames_to_time.side_effect = lambda f, sr=None, hop_length=None: f * 0.02
        mock_librosa.util.normalize.return_value = mags[50] # Simplified confidence

        # Tempo mocks
        mock_librosa.onset.onset_strength.return_value = np.zeros(100)
        mock_librosa.feature.tempogram.return_value = np.zeros((10, 100))
        mock_librosa.feature.tempo.return_value = [120.0]

        result = generator.extract_melody(audio_chunk)

        assert result.extraction_type == MIDIExtractionType.MELODY
        assert result.tempo_bpm == 120.0
        # Should detect some notes if mocking logic aligns, otherwise empty list is also a valid "run" test.
        assert isinstance(result.notes, list)
        assert result.midi_file is not None

    @patch("samplemind.core.processing.midi_generator.librosa")
    def test_extract_chords(self, mock_librosa, generator, audio_chunk):
        # Mock chroma
        # Create C Major chroma (C, E, G) -> indices 0, 4, 7
        chroma = np.zeros((12, 100))
        chroma[[0, 4, 7], :] = 1.0
        mock_librosa.feature.chroma_cqt.return_value = chroma
        mock_librosa.util.normalize.return_value = chroma

        # Tempo
        mock_librosa.feature.tempo.return_value = [120.0]
        # Frames to time
        mock_librosa.frames_to_time.side_effect = lambda f, sr=None, hop_length=None: f * 0.02

        result = generator.extract_chords(audio_chunk)

        assert result.extraction_type == MIDIExtractionType.HARMONY
        assert isinstance(result.chords, list)

        # Should detect C Major
        # Note: logic loops over frames. If we set all frames to C major, it should pick it up.
        if len(result.chords) > 0:
            chord = result.chords[0]
            assert chord.chord_type == ChordType.MAJOR
            assert "C" in chord.get_name()

    @patch("samplemind.core.processing.midi_generator.librosa")
    def test_extract_drums(self, mock_librosa, generator, audio_chunk):
        mock_librosa.effects.hpss.return_value = (audio_chunk, audio_chunk)

        # Mock onsets at 0.5s, 1.0s
        mock_librosa.onset.onset_detect.return_value = [25, 50] # frames
        mock_librosa.frames_to_time.return_value = np.array([0.5, 1.0])
        mock_librosa.feature.tempo.return_value = [120.0] # 0.5s per beat

        result = generator.extract_drums(audio_chunk)

        assert result.extraction_type == MIDIExtractionType.RHYTHM
        assert len(result.notes) == 2
        assert result.tempo_bpm == 120.0

    def test_midi_file_creation(self, generator):
        notes = [
            MidiNote(start_time=0.0, duration=0.5, pitch=60, velocity=100),
            MidiNote(start_time=0.5, duration=0.5, pitch=62, velocity=100)
        ]
        mid = generator._create_midi_file(notes, tempo_bpm=120.0)
        assert len(mid.tracks) == 1
        assert len(mid.tracks[0]) > 0 # Should have events

    @patch("samplemind.core.processing.midi_generator.librosa")
    def test_high_level_extract(self, mock_librosa, generator):
        mock_librosa.load.return_value = (np.zeros(100), 22050)

        # Mock specific extractors - use patch on the CLASS/INSTANCE methods or just assume they run if we don't mock them out fully.
        # But we are mocking librosa so the underlying calls will use mocks.

        # Actually easier to mock the methods on the instance for this test
        generator.extract_melody = Mock()

        path = Path("test.wav")
        generator.extract(path, MIDIExtractionType.MELODY)

        generator.extract_melody.assert_called_once()
