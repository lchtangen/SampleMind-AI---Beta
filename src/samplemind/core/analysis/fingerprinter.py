"""
Audio Fingerprinter — KP-33

Generates a perceptual audio fingerprint (SHA-256 of quantized spectral
features) and queries the similarity database for near-duplicates at
cosine similarity ≥ 0.95.

The fingerprint is NOT a cryptographic hash of raw bytes — it is based on
the perceptual energy spectrum, so transcodings and minor edits of the same
content will produce similar (often identical) fingerprints.
"""

from __future__ import annotations

import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="fingerprint")

# Similarity threshold for near-duplicate detection
_NEAR_DUPE_THRESHOLD = 0.95


@dataclass
class NearDuplicate:
    """A near-duplicate match found in the library."""

    file_id: str
    file_path: str
    similarity: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FingerprintResult:
    """Result of fingerprinting an audio file."""

    # Perceptual fingerprint hex string (SHA-256 of quantized spectrum)
    fingerprint: str = ""

    # Near-duplicate matches (cosine similarity ≥ 0.95)
    near_duplicates: list[NearDuplicate] = field(default_factory=list)

    # Whether an exact match was found (similarity == 1.0)
    is_exact_duplicate: bool = False

    # Number of near-duplicates found
    duplicate_count: int = 0

    # Metadata
    file_path: str = ""
    sample_rate: int = 22050
    duration: float = 0.0


class AudioFingerprinter:
    """
    Generates perceptual fingerprints and detects near-duplicates.

    The fingerprint is computed by:
    1. Computing the power spectrogram (mel-scaled, 128 bands)
    2. Quantizing to 8-bit integers
    3. SHA-256 hashing the result

    Near-duplicate detection queries ``SimilarityDatabase.find_similar()``
    with threshold 0.95.

    Usage::

        # Fingerprint only (no DB)
        fingerprinter = AudioFingerprinter()
        result = fingerprinter.fingerprint(y, sr)

        # Fingerprint + near-duplicate search
        from samplemind.core.similarity.similarity_db import SimilarityDatabase
        db = SimilarityDatabase()
        result = await fingerprinter.fingerprint_and_search(Path("sample.wav"), db)
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fingerprint(self, y: np.ndarray, sr: int) -> FingerprintResult:
        """
        Compute the perceptual fingerprint of an audio signal.

        Args:
            y: Audio time-series (mono, float32)
            sr: Sample rate

        Returns:
            FingerprintResult with fingerprint string (near_duplicates empty)
        """
        try:
            import librosa
        except ImportError:
            logger.warning("librosa not available — returning empty fingerprint")
            return FingerprintResult(
                sample_rate=sr, duration=float(len(y)) / max(sr, 1)
            )

        duration = float(len(y)) / sr
        result = FingerprintResult(sample_rate=sr, duration=duration)

        # --- Mel power spectrogram ----------------------------------------
        mel_spec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=self.n_mels,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
        )

        # Log-scale and quantize to uint8
        mel_log = librosa.power_to_db(mel_spec, ref=np.max)
        # Normalize to [0, 255]
        mel_min, mel_max = float(mel_log.min()), float(mel_log.max())
        if mel_max > mel_min:
            mel_norm = (mel_log - mel_min) / (mel_max - mel_min)
        else:
            mel_norm = np.zeros_like(mel_log)

        quantized = (mel_norm * 255.0).astype(np.uint8)

        # SHA-256 of quantized spectrogram bytes
        sha = hashlib.sha256(quantized.tobytes())
        result.fingerprint = sha.hexdigest()

        return result

    async def fingerprint_and_search(
        self,
        path: Path,
        similarity_db: Any | None = None,
        sample_rate: int = 22050,
    ) -> FingerprintResult:
        """
        Fingerprint a file and optionally search for near-duplicates.

        Args:
            path: Path to audio file
            similarity_db: Optional ``SimilarityDatabase`` instance for search
            sample_rate: Target sample rate

        Returns:
            FingerprintResult with near_duplicates populated if db supplied
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _EXECUTOR, self._load_and_fingerprint, path, sample_rate
        )

        if similarity_db is not None:
            result = await loop.run_in_executor(
                _EXECUTOR,
                self._search_near_duplicates,
                path,
                result,
                similarity_db,
            )

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_and_fingerprint(self, path: Path, sample_rate: int) -> FingerprintResult:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            result = self.fingerprint(y, sr)
            result.file_path = str(path)
            return result
        except Exception as exc:
            logger.error(f"AudioFingerprinter failed for {path}: {exc}")
            return FingerprintResult(
                sample_rate=sample_rate, duration=0.0, file_path=str(path)
            )

    @staticmethod
    def _search_near_duplicates(
        path: Path,
        result: FingerprintResult,
        similarity_db: Any,
    ) -> FingerprintResult:
        """
        Query SimilarityDatabase for near-duplicates (similarity ≥ 0.95).

        Args:
            path: Query file path
            result: FingerprintResult to augment
            similarity_db: SimilarityDatabase instance

        Returns:
            Updated FingerprintResult with near_duplicates populated
        """
        try:
            similar = similarity_db.find_similar(
                query_file=path,
                n_results=20,
                min_similarity=_NEAR_DUPE_THRESHOLD,
            )

            dupes: list[NearDuplicate] = []
            for s in similar:
                # Exclude the file itself (similarity == 1.0 with same path)
                if s.file_path == str(path):
                    continue
                dupes.append(
                    NearDuplicate(
                        file_id=s.file_id,
                        file_path=s.file_path,
                        similarity=round(float(s.similarity), 4),
                        metadata=s.metadata,
                    )
                )

            result.near_duplicates = dupes
            result.duplicate_count = len(dupes)
            result.is_exact_duplicate = any(d.similarity >= 0.999 for d in dupes)

        except Exception as exc:
            logger.warning(f"Near-duplicate search failed for {path}: {exc}")

        return result
