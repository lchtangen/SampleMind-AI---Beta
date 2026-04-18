"""Tests for AudioDNAComparator."""

from __future__ import annotations

import numpy as np
import pytest

from samplemind.core.similarity.audio_dna import (
    AudioDNA,
    AudioDNAComparator,
    DNA_VECTOR_DIM,
    DNAComparison,
)


class TestAudioDNAComparator:
    """Tests for AudioDNAComparator."""

    def test_init(self) -> None:
        comp = AudioDNAComparator()
        assert comp.n_mels == 128
        assert comp.n_fft == 2048

    def test_extract_dna_silence(self) -> None:
        comp = AudioDNAComparator()
        y = np.zeros(22050, dtype=np.float32)
        dna = comp.extract_dna(y, 22050)
        assert isinstance(dna, AudioDNA)
        assert len(dna.vector) == DNA_VECTOR_DIM
        assert len(dna.strands) == 8

    def test_extract_dna_noise(self) -> None:
        comp = AudioDNAComparator()
        rng = np.random.default_rng(42)
        y = rng.standard_normal(22050 * 2).astype(np.float32)
        dna = comp.extract_dna(y, 22050)
        assert len(dna.vector) == DNA_VECTOR_DIM
        # Vector should be normalized
        norm = np.linalg.norm(dna.vector)
        assert norm == pytest.approx(1.0, abs=0.01)

    def test_compare_identical(self) -> None:
        comp = AudioDNAComparator()
        rng = np.random.default_rng(42)
        y = rng.standard_normal(22050).astype(np.float32)
        dna = comp.extract_dna(y, 22050)
        comparison = comp.compare(dna, dna)
        assert isinstance(comparison, DNAComparison)
        assert comparison.overall_similarity == pytest.approx(1.0, abs=0.01)

    def test_compare_different(self) -> None:
        comp = AudioDNAComparator()
        rng = np.random.default_rng(42)
        y_a = rng.standard_normal(22050).astype(np.float32)
        y_b = np.zeros(22050, dtype=np.float32)
        dna_a = comp.extract_dna(y_a, 22050)
        dna_b = comp.extract_dna(y_b, 22050)
        comparison = comp.compare(dna_a, dna_b)
        assert comparison.overall_similarity < 0.9

    def test_strand_dimensions(self) -> None:
        comp = AudioDNAComparator()
        y = np.random.randn(22050).astype(np.float32)
        dna = comp.extract_dna(y, 22050)
        expected_dims = {
            "spectral_shape": 20,
            "temporal_envelope": 16,
            "harmonic_profile": 16,
            "rhythmic_signature": 16,
            "stereo_image": 8,
            "frequency_balance": 16,
            "dynamic_range": 16,
            "texture_density": 20,
        }
        for strand, dim in expected_dims.items():
            assert strand in dna.strands
            assert len(dna.strands[strand]) == dim, f"{strand} has wrong dim"

    def test_to_dict(self) -> None:
        comp = AudioDNAComparator()
        y = np.zeros(22050, dtype=np.float32)
        dna = comp.extract_dna(y, 22050, file_path="/test.wav")
        d = dna.to_dict()
        assert d["file_path"] == "/test.wav"
        assert d["dimension"] == DNA_VECTOR_DIM
        assert "strands" in d

    def test_comparison_to_dict(self) -> None:
        comp = AudioDNAComparator()
        y = np.zeros(22050, dtype=np.float32)
        dna = comp.extract_dna(y, 22050)
        comparison = comp.compare(dna, dna)
        d = comparison.to_dict()
        assert "overall_similarity" in d
        assert "most_similar_strand" in d
        assert "strands" in d

    def test_comparison_description(self) -> None:
        comp = AudioDNAComparator()
        y = np.zeros(22050, dtype=np.float32)
        dna = comp.extract_dna(y, 22050)
        comparison = comp.compare(dna, dna)
        assert comparison.description != ""
