"""
Audio Embedding Engine for Sample Similarity Search

Generates fixed-size embeddings from audio features for use in vector similarity search.
The embeddings capture:
- Timbral characteristics (MFCCs, spectral features)
- Harmonic content (chroma features)
- Rhythmic properties (tempo, onset patterns)
- Dynamic range and energy
"""

import logging
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import numpy as np

logger = logging.getLogger(__name__)

# Embedding dimension: 128 features total
EMBEDDING_DIM = 128


@dataclass
class AudioEmbedding:
    """Container for an audio file's embedding and metadata"""
    file_id: str                    # Unique identifier (usually file hash)
    file_path: Path                 # Original file path
    embedding: np.ndarray           # Fixed-size embedding vector
    metadata: Dict[str, Any] = field(default_factory=dict)  # Extracted features for filtering

    def to_list(self) -> List[float]:
        """Convert embedding to list for ChromaDB"""
        return self.embedding.tolist()


class AudioEmbeddingEngine:
    """
    Generates embeddings from audio files for similarity search.

    The embedding is a 128-dimensional vector combining:
    - MFCCs (20 coefficients, mean + std = 40 dims)
    - Chroma features (12 features, mean + std = 24 dims)
    - Spectral features (centroid, bandwidth, rolloff, contrast - 16 dims)
    - Rhythm features (tempo, onset strength, beat variance - 8 dims)
    - Energy features (RMS, dynamic range, zero-crossing - 8 dims)
    - Harmonic-percussive ratio (4 dims)
    - Additional statistics (28 dims padding to 128)
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        n_mfcc: int = 20,
        n_chroma: int = 12,
    ):
        """
        Initialize the embedding engine.

        Args:
            sample_rate: Target sample rate for analysis
            n_mfcc: Number of MFCC coefficients
            n_chroma: Number of chroma features
        """
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.n_chroma = n_chroma

    def generate_embedding(
        self,
        file_path: Path,
        include_metadata: bool = True,
    ) -> AudioEmbedding:
        """
        Generate embedding for a single audio file.

        Args:
            file_path: Path to audio file
            include_metadata: Include feature metadata for filtering

        Returns:
            AudioEmbedding containing the embedding vector and metadata
        """
        import librosa

        file_path = Path(file_path).expanduser().resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Generate file ID from content hash
        file_id = self._compute_file_hash(file_path)

        logger.info(f"Generating embedding for: {file_path.name}")

        # Load audio
        y, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)

        # Extract features
        embedding_parts = []
        metadata = {}

        # 1. MFCC features (20 coefficients * 2 stats = 40 dims)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        embedding_parts.extend([mfcc_mean, mfcc_std])

        # 2. Chroma features (12 * 2 = 24 dims)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        chroma_std = np.std(chroma, axis=1)
        embedding_parts.extend([chroma_mean, chroma_std])

        if include_metadata:
            # Estimate key from chroma
            key_idx = int(np.argmax(chroma_mean))
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            metadata['estimated_key'] = key_names[key_idx]

        # 3. Spectral features (4 features * 4 stats = 16 dims)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

        spectral_features = np.array([
            np.mean(spectral_centroid), np.std(spectral_centroid),
            np.mean(spectral_bandwidth), np.std(spectral_bandwidth),
            np.mean(spectral_rolloff), np.std(spectral_rolloff),
            np.mean(spectral_contrast), np.std(spectral_contrast),
            np.max(spectral_centroid), np.min(spectral_centroid),
            np.max(spectral_bandwidth), np.min(spectral_bandwidth),
            np.max(spectral_rolloff), np.min(spectral_rolloff),
            np.median(spectral_centroid), np.median(spectral_bandwidth),
        ])
        embedding_parts.append(spectral_features)

        if include_metadata:
            metadata['spectral_centroid_mean'] = float(np.mean(spectral_centroid))
            metadata['brightness'] = 'bright' if np.mean(spectral_centroid) > 3000 else 'dark'

        # 4. Rhythm features (8 dims)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        rhythm_features = np.array([
            float(tempo) / 200.0,  # Normalized tempo
            np.mean(onset_env),
            np.std(onset_env),
            np.max(onset_env),
            len(beats) / (len(y) / sr) if len(y) > 0 else 0,  # Beat density
            np.var(np.diff(beats)) if len(beats) > 1 else 0,  # Beat variance
            np.median(onset_env),
            float(np.percentile(onset_env, 90)),
        ])
        embedding_parts.append(rhythm_features)

        if include_metadata:
            metadata['tempo'] = float(tempo)

        # 5. Energy features (8 dims)
        rms = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        energy_features = np.array([
            np.mean(rms),
            np.std(rms),
            np.max(rms),
            np.min(rms),
            np.mean(zcr),
            np.std(zcr),
            np.max(rms) - np.min(rms),  # Dynamic range
            np.percentile(rms, 90) - np.percentile(rms, 10),  # Robust dynamic range
        ])
        embedding_parts.append(energy_features)

        if include_metadata:
            metadata['energy'] = 'high' if np.mean(rms) > 0.1 else 'low'
            metadata['dynamic_range'] = float(np.max(rms) - np.min(rms))

        # 6. Harmonic-Percussive features (4 dims)
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        hp_ratio = np.mean(np.abs(y_harmonic)) / (np.mean(np.abs(y_percussive)) + 1e-8)

        hp_features = np.array([
            np.mean(np.abs(y_harmonic)),
            np.mean(np.abs(y_percussive)),
            hp_ratio,
            1.0 / (hp_ratio + 1e-8),  # Inverse ratio
        ])
        embedding_parts.append(hp_features)

        if include_metadata:
            metadata['character'] = 'harmonic' if hp_ratio > 1.0 else 'percussive'

        # Concatenate all parts
        embedding = np.concatenate(embedding_parts)

        # Pad or truncate to fixed dimension
        if len(embedding) < EMBEDDING_DIM:
            # Pad with additional statistics
            padding_needed = EMBEDDING_DIM - len(embedding)
            # Add more statistics from the signal
            additional_stats = np.array([
                np.mean(y), np.std(y), np.max(y), np.min(y),
                float(len(y) / sr),  # Duration
                np.percentile(np.abs(y), 95),
                np.percentile(np.abs(y), 5),
                np.median(np.abs(y)),
            ])
            padding = np.zeros(padding_needed)
            padding[:min(len(additional_stats), padding_needed)] = additional_stats[:padding_needed]
            embedding = np.concatenate([embedding, padding])
        else:
            embedding = embedding[:EMBEDDING_DIM]

        # Normalize to unit vector
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        if include_metadata:
            metadata['duration'] = float(len(y) / sr)
            metadata['file_name'] = file_path.name
            metadata['file_path'] = str(file_path)

        return AudioEmbedding(
            file_id=file_id,
            file_path=file_path,
            embedding=embedding.astype(np.float32),
            metadata=metadata,
        )

    def generate_embeddings_batch(
        self,
        file_paths: List[Path],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[AudioEmbedding]:
        """
        Generate embeddings for multiple audio files.

        Args:
            file_paths: List of audio file paths
            progress_callback: Optional callback(current, total, filename)

        Returns:
            List of AudioEmbedding objects
        """
        embeddings = []
        total = len(file_paths)

        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(i + 1, total, file_path.name)

            try:
                embedding = self.generate_embedding(file_path)
                embeddings.append(embedding)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for {file_path}: {e}")
                continue

        return embeddings

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        # Embeddings are already normalized, so dot product = cosine similarity
        similarity = np.dot(embedding1, embedding2)
        # Clamp to [0, 1] range
        return float(max(0.0, min(1.0, (similarity + 1) / 2)))

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """Compute SHA-256 hash of file for unique identification"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]  # Use first 16 chars for brevity
