"""
Audio DNA Comparator — Deep Structural Similarity

Computes a multi-dimensional "DNA" fingerprint of audio that captures
structural, timbral, rhythmic, and spectral characteristics in a compact
vector. Enables similarity comparison that goes beyond simple embedding
distance to understand *why* two samples are similar.

DNA Components (8 strands):
  1. Spectral Shape — mel-frequency envelope (timbral character)
  2. Temporal Envelope — amplitude contour (dynamics)
  3. Harmonic Profile — harmonic-to-noise ratio + fundamental tracking
  4. Rhythmic Signature — onset density + pattern regularity
  5. Stereo Image — mid/side energy ratio
  6. Frequency Balance — low/mid/high energy distribution
  7. Dynamic Range — crest factor + loudness consistency
  8. Texture Density — spectral flux + zero crossing profile

Each strand produces a fixed-size sub-vector. Combined, they form a
128-dimensional DNA vector suitable for cosine similarity comparison.

Usage::

    from samplemind.core.similarity.audio_dna import AudioDNAComparator

    comparator = AudioDNAComparator()
    dna_a = comparator.extract_dna(y_a, sr)
    dna_b = comparator.extract_dna(y_b, sr)
    sim = comparator.compare(dna_a, dna_b)
    print(f"Overall: {sim.overall_similarity:.2f}")
    print(f"Most similar in: {sim.most_similar_strand}")
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="audiodna")

# DNA strand dimensions (total = 128)
_STRAND_DIMS = {
    "spectral_shape": 20,
    "temporal_envelope": 16,
    "harmonic_profile": 16,
    "rhythmic_signature": 16,
    "stereo_image": 8,
    "frequency_balance": 16,
    "dynamic_range": 16,
    "texture_density": 20,
}
DNA_VECTOR_DIM = sum(_STRAND_DIMS.values())  # 128


@dataclass
class AudioDNA:
    """Multi-dimensional audio fingerprint."""

    vector: np.ndarray = field(default_factory=lambda: np.zeros(DNA_VECTOR_DIM))
    strands: dict[str, np.ndarray] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    file_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (vector as list)."""
        return {
            "vector": [round(float(x), 6) for x in self.vector],
            "strands": {
                k: [round(float(x), 6) for x in v]
                for k, v in self.strands.items()
            },
            "metadata": self.metadata,
            "file_path": self.file_path,
            "dimension": len(self.vector),
        }


@dataclass
class StrandComparison:
    """Similarity comparison for a single DNA strand."""

    strand_name: str
    similarity: float  # 0–1, cosine similarity
    distance: float  # Euclidean distance
    interpretation: str = ""


@dataclass
class DNAComparison:
    """Full DNA similarity comparison result."""

    overall_similarity: float = 0.0  # 0–1
    strand_similarities: list[StrandComparison] = field(default_factory=list)
    most_similar_strand: str = ""
    least_similar_strand: str = ""
    similarity_profile: dict[str, float] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "overall_similarity": round(self.overall_similarity, 4),
            "most_similar_strand": self.most_similar_strand,
            "least_similar_strand": self.least_similar_strand,
            "similarity_profile": {
                k: round(v, 4) for k, v in self.similarity_profile.items()
            },
            "description": self.description,
            "strands": [
                {
                    "name": sc.strand_name,
                    "similarity": round(sc.similarity, 4),
                    "interpretation": sc.interpretation,
                }
                for sc in self.strand_similarities
            ],
        }


class AudioDNAComparator:
    """
    Extracts and compares multi-dimensional audio DNA fingerprints.

    Each audio file's DNA captures 8 structural aspects in a compact
    128-dimensional vector, enabling nuanced similarity analysis.
    """

    def __init__(
        self,
        n_mels: int = 128,
        n_fft: int = 2048,
        hop_length: int = 512,
    ) -> None:
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length

    # ── Public API ────────────────────────────────────────────────────────

    def extract_dna(
        self,
        y: np.ndarray,
        sr: int,
        file_path: str = "",
    ) -> AudioDNA:
        """
        Extract audio DNA fingerprint from a signal.

        Args:
            y: Audio signal (mono or stereo, float32).
            sr: Sample rate.
            file_path: Optional file path for metadata.

        Returns:
            AudioDNA with 128-dim vector and strand breakdowns.
        """
        # Handle stereo
        if y.ndim > 1:
            y_stereo = y
            y_mono = np.mean(y, axis=0) if y.shape[0] <= 2 else np.mean(y, axis=1)
        else:
            y_stereo = None
            y_mono = y

        strands: dict[str, np.ndarray] = {}

        # Strand 1: Spectral Shape
        strands["spectral_shape"] = self._spectral_shape(y_mono, sr)

        # Strand 2: Temporal Envelope
        strands["temporal_envelope"] = self._temporal_envelope(y_mono, sr)

        # Strand 3: Harmonic Profile
        strands["harmonic_profile"] = self._harmonic_profile(y_mono, sr)

        # Strand 4: Rhythmic Signature
        strands["rhythmic_signature"] = self._rhythmic_signature(y_mono, sr)

        # Strand 5: Stereo Image
        strands["stereo_image"] = self._stereo_image(y_stereo, sr)

        # Strand 6: Frequency Balance
        strands["frequency_balance"] = self._frequency_balance(y_mono, sr)

        # Strand 7: Dynamic Range
        strands["dynamic_range"] = self._dynamic_range(y_mono, sr)

        # Strand 8: Texture Density
        strands["texture_density"] = self._texture_density(y_mono, sr)

        # Concatenate all strands into single vector
        vector = np.concatenate(list(strands.values()))

        # L2-normalize the full vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        duration = float(len(y_mono)) / sr

        return AudioDNA(
            vector=vector,
            strands=strands,
            metadata={
                "duration": round(duration, 3),
                "sample_rate": sr,
                "rms": round(float(np.sqrt(np.mean(y_mono**2))), 6),
                "peak": round(float(np.max(np.abs(y_mono))), 6),
            },
            file_path=file_path,
        )

    def compare(self, dna_a: AudioDNA, dna_b: AudioDNA) -> DNAComparison:
        """
        Compare two audio DNA fingerprints.

        Args:
            dna_a: First audio DNA.
            dna_b: Second audio DNA.

        Returns:
            DNAComparison with overall and per-strand similarities.
        """
        # Overall cosine similarity
        overall = self._cosine_similarity(dna_a.vector, dna_b.vector)

        # Per-strand comparison
        strand_comparisons: list[StrandComparison] = []
        similarity_profile: dict[str, float] = {}

        for strand_name in _STRAND_DIMS:
            a_strand = dna_a.strands.get(strand_name, np.zeros(1))
            b_strand = dna_b.strands.get(strand_name, np.zeros(1))

            sim = self._cosine_similarity(a_strand, b_strand)
            dist = float(np.linalg.norm(a_strand - b_strand))

            interpretation = self._interpret_strand_similarity(strand_name, sim)

            strand_comparisons.append(
                StrandComparison(
                    strand_name=strand_name,
                    similarity=sim,
                    distance=dist,
                    interpretation=interpretation,
                )
            )
            similarity_profile[strand_name] = sim

        # Find most/least similar strands
        strand_comparisons.sort(key=lambda x: x.similarity, reverse=True)
        most_similar = strand_comparisons[0].strand_name if strand_comparisons else ""
        least_similar = strand_comparisons[-1].strand_name if strand_comparisons else ""

        # Generate description
        desc = self._generate_description(overall, strand_comparisons)

        return DNAComparison(
            overall_similarity=overall,
            strand_similarities=strand_comparisons,
            most_similar_strand=most_similar,
            least_similar_strand=least_similar,
            similarity_profile=similarity_profile,
            description=desc,
        )

    async def extract_dna_file(
        self,
        path: Path,
        sample_rate: int = 22050,
    ) -> AudioDNA:
        """Extract DNA from an audio file asynchronously."""
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_extract, path, sample_rate
        )

    async def compare_files(
        self,
        path_a: Path,
        path_b: Path,
        sample_rate: int = 22050,
    ) -> DNAComparison:
        """Compare two audio files by extracting and comparing their DNA."""
        dna_a = await self.extract_dna_file(path_a, sample_rate)
        dna_b = await self.extract_dna_file(path_b, sample_rate)
        return self.compare(dna_a, dna_b)

    # ── Strand extractors ─────────────────────────────────────────────────

    def _spectral_shape(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Strand 1: Mel-frequency envelope capturing timbral character."""
        dim = _STRAND_DIMS["spectral_shape"]
        try:
            import librosa

            mel = librosa.feature.melspectrogram(
                y=y, sr=sr, n_mels=dim, n_fft=self.n_fft, hop_length=self.hop_length
            )
            mel_db = librosa.power_to_db(mel, ref=np.max)
            # Average across time to get spectral shape
            shape = np.mean(mel_db, axis=1)
            # Normalize to [0, 1]
            shape = (shape - shape.min()) / (shape.max() - shape.min() + 1e-9)
            return shape.astype(np.float32)
        except ImportError:
            return np.zeros(dim, dtype=np.float32)

    def _temporal_envelope(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Strand 2: Amplitude contour capturing dynamics."""
        dim = _STRAND_DIMS["temporal_envelope"]
        # Split into equal-sized frames
        frame_size = max(1, len(y) // dim)
        envelope = np.zeros(dim, dtype=np.float32)

        for i in range(dim):
            start = i * frame_size
            end = min(start + frame_size, len(y))
            if start < len(y):
                envelope[i] = np.sqrt(np.mean(y[start:end] ** 2))

        # Normalize
        env_max = np.max(envelope)
        if env_max > 0:
            envelope = envelope / env_max
        return envelope

    def _harmonic_profile(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Strand 3: Harmonic content and pitch characteristics."""
        dim = _STRAND_DIMS["harmonic_profile"]
        try:
            import librosa

            # Chroma features (12 pitch classes)
            chroma = librosa.feature.chroma_cqt(
                y=y, sr=sr, hop_length=self.hop_length
            )
            chroma_mean = np.mean(chroma, axis=1)  # 12 values

            # Harmonic-percussive separation energy ratio
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            h_energy = float(np.sum(y_harmonic**2))
            p_energy = float(np.sum(y_percussive**2))
            total = h_energy + p_energy + 1e-9
            hp_features = np.array(
                [h_energy / total, p_energy / total], dtype=np.float32
            )

            # Spectral flatness (2 values: mean and std)
            flatness = librosa.feature.spectral_flatness(y=y)
            flat_features = np.array(
                [float(np.mean(flatness)), float(np.std(flatness))], dtype=np.float32
            )

            # Combine: 12 (chroma) + 2 (h/p) + 2 (flatness) = 16
            result = np.concatenate([chroma_mean, hp_features, flat_features])
            return result[:dim].astype(np.float32)

        except ImportError:
            return np.zeros(dim, dtype=np.float32)

    def _rhythmic_signature(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Strand 4: Onset density and pattern regularity."""
        dim = _STRAND_DIMS["rhythmic_signature"]
        try:
            import librosa

            # Onset strength envelope
            onset_env = librosa.onset.onset_strength(
                y=y, sr=sr, hop_length=self.hop_length
            )

            # Tempogram (rhythmic periodicity)
            tempogram = librosa.feature.tempogram(
                onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
            )
            # Average across time, take first `dim` bins
            tempo_profile = np.mean(tempogram, axis=1)[:dim]
            if len(tempo_profile) < dim:
                tempo_profile = np.pad(
                    tempo_profile, (0, dim - len(tempo_profile))
                )

            # Normalize
            tp_max = np.max(np.abs(tempo_profile))
            if tp_max > 0:
                tempo_profile = tempo_profile / tp_max

            return tempo_profile.astype(np.float32)

        except ImportError:
            return np.zeros(dim, dtype=np.float32)

    def _stereo_image(self, y_stereo: np.ndarray | None, sr: int) -> np.ndarray:
        """Strand 5: Mid/side energy distribution."""
        dim = _STRAND_DIMS["stereo_image"]
        result = np.zeros(dim, dtype=np.float32)

        if y_stereo is None or y_stereo.ndim < 2:
            # Mono: centered image
            result[0] = 1.0  # All energy in mid
            return result

        # Ensure shape is (channels, samples)
        if y_stereo.shape[0] > y_stereo.shape[1]:
            y_stereo = y_stereo.T

        if y_stereo.shape[0] < 2:
            result[0] = 1.0
            return result

        left = y_stereo[0]
        right = y_stereo[1]

        # Mid/side decomposition
        mid = (left + right) / 2.0
        side = (left - right) / 2.0

        # Energy in frequency bands
        n_bands = dim // 2  # 4 bands for mid, 4 for side
        frame_size = max(1, len(mid) // n_bands)

        for i in range(n_bands):
            start = i * frame_size
            end = min(start + frame_size, len(mid))
            if start < len(mid):
                result[i] = np.sqrt(np.mean(mid[start:end] ** 2))
                result[n_bands + i] = np.sqrt(np.mean(side[start:end] ** 2))

        # Normalize
        r_max = np.max(result)
        if r_max > 0:
            result = result / r_max
        return result

    def _frequency_balance(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Strand 6: Low/mid/high energy distribution."""
        dim = _STRAND_DIMS["frequency_balance"]
        try:
            import librosa

            # Mel spectrogram with specific number of bands
            mel = librosa.feature.melspectrogram(
                y=y, sr=sr, n_mels=dim, n_fft=self.n_fft, hop_length=self.hop_length
            )
            # Energy per mel band averaged across time
            balance = np.mean(mel, axis=1)

            # Log-scale and normalize
            balance = np.log1p(balance)
            b_max = np.max(balance)
            if b_max > 0:
                balance = balance / b_max

            return balance.astype(np.float32)

        except ImportError:
            return np.zeros(dim, dtype=np.float32)

    def _dynamic_range(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Strand 7: Dynamic range and loudness consistency."""
        dim = _STRAND_DIMS["dynamic_range"]

        # Split into `dim` frames and compute per-frame statistics
        frame_size = max(1, len(y) // dim)
        result = np.zeros(dim, dtype=np.float32)

        for i in range(dim):
            start = i * frame_size
            end = min(start + frame_size, len(y))
            if start < len(y):
                frame = y[start:end]
                rms = np.sqrt(np.mean(frame**2))
                peak = np.max(np.abs(frame))
                # Crest factor (peak-to-RMS ratio) normalized to 0–1
                if rms > 1e-9:
                    crest = peak / rms
                    result[i] = min(1.0, crest / 20.0)  # Normalize by max 20
                else:
                    result[i] = 0.0

        return result

    def _texture_density(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Strand 8: Spectral flux and zero-crossing profile."""
        dim = _STRAND_DIMS["texture_density"]
        half = dim // 2

        # Spectral flux profile
        spec = np.abs(np.fft.rfft(
            y[: self.n_fft * (len(y) // self.n_fft)].reshape(-1, self.n_fft),
            axis=1,
        ))
        if spec.shape[0] > 1:
            flux = np.mean(np.abs(np.diff(spec, axis=0)), axis=0)
            # Resample to half-dim
            indices = np.linspace(0, len(flux) - 1, half).astype(int)
            flux_profile = flux[indices]
            f_max = np.max(flux_profile)
            if f_max > 0:
                flux_profile = flux_profile / f_max
        else:
            flux_profile = np.zeros(half)

        # Zero-crossing rate profile
        frame_size = max(1, len(y) // half)
        zcr_profile = np.zeros(half, dtype=np.float32)
        for i in range(half):
            start = i * frame_size
            end = min(start + frame_size, len(y))
            if start < len(y) - 1:
                frame = y[start:end]
                zcr = np.mean(np.abs(np.diff(np.sign(frame))) > 0)
                zcr_profile[i] = float(zcr)

        # Normalize ZCR
        z_max = np.max(zcr_profile)
        if z_max > 0:
            zcr_profile = zcr_profile / z_max

        return np.concatenate([
            flux_profile[:half].astype(np.float32),
            zcr_profile[:half],
        ])

    # ── Comparison helpers ────────────────────────────────────────────────

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @staticmethod
    def _interpret_strand_similarity(strand: str, sim: float) -> str:
        """Generate human-readable interpretation for strand similarity."""
        level = "very similar" if sim > 0.9 else (
            "similar" if sim > 0.7 else (
                "somewhat similar" if sim > 0.5 else (
                    "different" if sim > 0.3 else "very different"
                )
            )
        )
        descriptions = {
            "spectral_shape": f"Timbral character is {level}",
            "temporal_envelope": f"Dynamic contour is {level}",
            "harmonic_profile": f"Harmonic content is {level}",
            "rhythmic_signature": f"Rhythmic pattern is {level}",
            "stereo_image": f"Stereo spread is {level}",
            "frequency_balance": f"Frequency distribution is {level}",
            "dynamic_range": f"Dynamic range profile is {level}",
            "texture_density": f"Textural density is {level}",
        }
        return descriptions.get(strand, f"{strand} is {level}")

    @staticmethod
    def _generate_description(
        overall: float,
        strand_comparisons: list[StrandComparison],
    ) -> str:
        """Generate a human-readable comparison summary."""
        if overall > 0.9:
            level = "Nearly identical"
        elif overall > 0.7:
            level = "Very similar"
        elif overall > 0.5:
            level = "Moderately similar"
        elif overall > 0.3:
            level = "Somewhat different"
        else:
            level = "Quite different"

        desc = f"{level} (similarity: {overall:.2f})."

        if strand_comparisons:
            best = strand_comparisons[0]
            worst = strand_comparisons[-1]
            desc += (
                f" Most alike in {best.strand_name.replace('_', ' ')} "
                f"({best.similarity:.2f}), "
                f"most different in {worst.strand_name.replace('_', ' ')} "
                f"({worst.similarity:.2f})."
            )

        return desc

    def _load_and_extract(self, path: Path, sample_rate: int) -> AudioDNA:
        try:
            import librosa

            y, sr = librosa.load(str(path), sr=sample_rate, mono=True)
            return self.extract_dna(y, sr, file_path=str(path))
        except Exception as exc:
            logger.error("AudioDNAComparator failed for %s: %s", path, exc)
            return AudioDNA(file_path=str(path))


# ── Module exports ────────────────────────────────────────────────────────────

__all__ = [
    "AudioDNAComparator",
    "AudioDNA",
    "DNAComparison",
    "StrandComparison",
    "DNA_VECTOR_DIM",
]
