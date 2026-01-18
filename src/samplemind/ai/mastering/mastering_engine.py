"""AI-powered mastering engine."""

import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from .processing_chain import MasteringChain
from .reference_analyzer import MasteringProfile, ReferenceAnalyzer

logger = logging.getLogger(__name__)


class MasteringEngine:
    """AI-powered mastering engine with reference matching."""

    def __init__(self, sample_rate: int = 44100):
        """Initialize mastering engine.

        Args:
            sample_rate: Target sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.reference_analyzer = ReferenceAnalyzer()

    def auto_master(
        self,
        audio_path: Path,
        target_lufs: float = -14.0,
        genre: Optional[str] = None,
        reference_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Automatically master audio file.

        Args:
            audio_path: Path to audio file to master
            target_lufs: Target loudness in LUFS
            genre: Optional genre hint for preset selection
            reference_path: Optional reference track to match
            output_path: Optional output path (default: original_mastered.wav)

        Returns:
            Path to mastered audio file
        """
        try:
            import librosa
            import soundfile as sf
        except ImportError:
            logger.error("librosa or soundfile not available")
            raise

        # Load audio
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=False)
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            raise

        # Determine mastering profile
        if reference_path:
            logger.info(f"Using reference track: {reference_path}")
            profile = self.reference_analyzer.analyze_reference(reference_path)
        elif genre and genre in GENRE_PRESETS:
            logger.info(f"Using {genre} preset")
            profile = GENRE_PRESETS[genre]
        else:
            logger.info(f"Using default profile with target LUFS: {target_lufs}")
            profile = self._create_default_profile(target_lufs)

        # Build processing chain from profile
        chain = self._build_chain_from_profile(profile)

        # Process audio
        try:
            mastered = chain.process(y)
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise

        # Normalize to target LUFS
        mastered = self._normalize_loudness(mastered, profile.target_lufs)

        # Determine output path
        if output_path is None:
            output_path = audio_path.parent / f"{audio_path.stem}_mastered{audio_path.suffix}"

        # Save output
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save file
            sf.write(output_path, mastered.T if mastered.ndim > 1 else mastered, self.sample_rate)
            logger.info(f"Mastered audio saved to: {output_path}")

        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            raise

        return output_path

    def _create_default_profile(self, target_lufs: float) -> MasteringProfile:
        """Create default mastering profile."""
        return MasteringProfile(
            target_lufs=target_lufs,
            dynamic_range=10.0,
            spectral_balance=np.zeros(31),
            stereo_width=0.8,
            compression_ratio=3.0,
            peak_limit=-0.1,
            low_end_boost=0.0,
            high_end_boost=0.0,
            metadata={"profile_type": "default"},
        )

    def _build_chain_from_profile(self, profile: MasteringProfile) -> MasteringChain:
        """Build processing chain from mastering profile."""
        chain = MasteringChain(self.sample_rate)

        # EQ based on spectral balance
        low_boost = profile.low_end_boost
        high_boost = profile.high_end_boost

        chain.add_eq(
            low_shelf_db=low_boost,
            mid_db=0.0,
            high_shelf_db=high_boost,
        )

        # Compression for dynamics control
        chain.add_compressor(
            threshold=-20.0,
            ratio=profile.compression_ratio,
            attack=0.005,
            release=0.100,
            makeup_gain=6.0,
        )

        # Stereo width enhancement
        if profile.stereo_width > 0:
            chain.add_stereo_width(width=profile.stereo_width)

        # Limiter for peak protection
        chain.add_limiter(
            threshold=profile.peak_limit,
            release=0.05,
        )

        return chain

    def _normalize_loudness(self, audio: np.ndarray, target_lufs: float) -> np.ndarray:
        """Normalize audio to target LUFS loudness."""
        # Measure current loudness
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio

        rms = np.sqrt(np.mean(audio_mono**2))
        current_lufs = 20 * np.log10(rms + 1e-10) - 23.0

        # Calculate gain adjustment
        lufs_diff = target_lufs - current_lufs
        gain = 10 ** (lufs_diff / 20)

        logger.debug(
            f"Current LUFS: {current_lufs:.1f}, Target: {target_lufs:.1f}, "
            f"Adjustment: {lufs_diff:.1f}dB ({gain:.2f}x gain)"
        )

        # Apply gain
        audio = audio * gain

        # Prevent clipping
        peak = np.max(np.abs(audio))
        if peak > 0.99:
            headroom_reduction = peak / 0.99
            logger.warning(
                f"Peak would exceed 0dB by {20*np.log10(headroom_reduction):.1f}dB, "
                f"reducing gain to prevent clipping"
            )
            audio = audio / headroom_reduction

        return audio


# Genre-specific mastering presets
GENRE_PRESETS: Dict[str, MasteringProfile] = {
    "techno": MasteringProfile(
        target_lufs=-11.0,  # Loud for club playback
        dynamic_range=8.0,  # Moderately compressed
        spectral_balance=np.zeros(31),
        stereo_width=0.9,  # Wide stereo
        compression_ratio=4.0,
        peak_limit=-0.1,
        low_end_boost=2.0,  # Boost bass
        high_end_boost=1.0,  # Slight high boost
        metadata={"genre": "techno", "style": "club"},
    ),
    "house": MasteringProfile(
        target_lufs=-11.0,
        dynamic_range=9.0,
        spectral_balance=np.zeros(31),
        stereo_width=0.85,
        compression_ratio=3.5,
        peak_limit=-0.1,
        low_end_boost=1.5,
        high_end_boost=0.5,
        metadata={"genre": "house", "style": "dance"},
    ),
    "hiphop": MasteringProfile(
        target_lufs=-9.0,  # Very loud (typical for hip-hop)
        dynamic_range=7.0,  # Heavy compression
        spectral_balance=np.zeros(31),
        stereo_width=0.7,  # Narrower stereo for bass
        compression_ratio=5.0,
        peak_limit=-0.1,
        low_end_boost=3.0,  # Heavy bass boost
        high_end_boost=-0.5,  # Slight high cut
        metadata={"genre": "hiphop", "style": "rap"},
    ),
    "ambient": MasteringProfile(
        target_lufs=-16.0,  # Quieter, more dynamic
        dynamic_range=14.0,  # Light compression
        spectral_balance=np.zeros(31),
        stereo_width=1.0,  # Maximum width
        compression_ratio=2.0,
        peak_limit=-0.3,
        low_end_boost=0.0,
        high_end_boost=0.5,
        metadata={"genre": "ambient", "style": "atmospheric"},
    ),
    "rock": MasteringProfile(
        target_lufs=-10.0,
        dynamic_range=10.0,
        spectral_balance=np.zeros(31),
        stereo_width=0.8,
        compression_ratio=3.0,
        peak_limit=-0.1,
        low_end_boost=1.0,
        high_end_boost=2.0,  # Bright sound
        metadata={"genre": "rock", "style": "alternative"},
    ),
    "pop": MasteringProfile(
        target_lufs=-11.0,  # Loud like modern pop
        dynamic_range=8.5,
        spectral_balance=np.zeros(31),
        stereo_width=0.75,
        compression_ratio=4.0,
        peak_limit=-0.1,
        low_end_boost=1.5,
        high_end_boost=1.0,
        metadata={"genre": "pop", "style": "mainstream"},
    ),
    "edm": MasteringProfile(
        target_lufs=-11.0,
        dynamic_range=7.5,
        spectral_balance=np.zeros(31),
        stereo_width=0.9,
        compression_ratio=4.0,
        peak_limit=-0.1,
        low_end_boost=2.5,
        high_end_boost=1.5,
        metadata={"genre": "edm", "style": "electronic"},
    ),
}
