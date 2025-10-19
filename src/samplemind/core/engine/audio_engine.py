#!/usr/bin/env python3
"""
SampleMind AI v6 - Core Audio Engine
The heart of the AI music production platform

This module provides comprehensive audio analysis capabilities including:
- Real-time audio processing and analysis
- Feature extraction (tempo, pitch, rhythm, spectral features)
- Audio similarity comparison
- Music information retrieval
- Format conversion and normalization
- Real-time visualization and monitoring

Designed specifically for professional music production and FL Studio integration.
"""

import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.spatial.distance import cosine
import logging
from concurrent.futures import ThreadPoolExecutor
import time
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AIFF = "aiff"
    M4A = "m4a"
    OGG = "ogg"


class AnalysisLevel(Enum):
    """Audio analysis complexity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    PROFESSIONAL = "professional"


@dataclass
class AudioFeatures:
    """Comprehensive audio feature representation"""
    # Basic properties
    duration: float
    sample_rate: int
    channels: int
    bit_depth: Optional[int] = None
    
    # Temporal features
    tempo: float = 0.0
    time_signature: Tuple[int, int] = (4, 4)
    beats: List[float] = field(default_factory=list)
    onset_times: List[float] = field(default_factory=list)
    
    # Tonal features
    key: str = "C"
    mode: str = "major"
    pitch_class_distribution: List[float] = field(default_factory=list)
    chroma_features: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Spectral features
    spectral_centroid: List[float] = field(default_factory=list)
    spectral_bandwidth: List[float] = field(default_factory=list)
    spectral_rolloff: List[float] = field(default_factory=list)
    zero_crossing_rate: List[float] = field(default_factory=list)
    
    # MFCC features
    mfccs: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Advanced features
    harmonic_content: np.ndarray = field(default_factory=lambda: np.array([]))
    percussive_content: np.ndarray = field(default_factory=lambda: np.array([]))
    rms_energy: List[float] = field(default_factory=list)
    
    # Rhythm and groove
    rhythm_pattern: List[float] = field(default_factory=list)
    groove_template: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Metadata
    analysis_timestamp: float = field(default_factory=time.time)
    file_hash: str = ""
    file_size: int = 0
    analysis_level: AnalysisLevel = AnalysisLevel.STANDARD

    def calculate_similarity(self, other: 'AudioFeatures') -> float:
        """
        Calculate similarity score between two AudioFeatures objects
        Returns a score between 0.0 (completely different) and 1.0 (identical)
        """
        from scipy.spatial.distance import cosine

        similarities = []

        # Tempo similarity (normalized difference)
        if self.tempo > 0 and other.tempo > 0:
            tempo_sim = 1.0 - min(abs(self.tempo - other.tempo) / max(self.tempo, other.tempo), 1.0)
            similarities.append(tempo_sim * 0.2)  # 20% weight

        # Key/mode similarity
        if self.key == other.key:
            similarities.append(0.15)  # 15% weight
        if self.mode == other.mode:
            similarities.append(0.1)  # 10% weight

        # Pitch class distribution similarity
        if len(self.pitch_class_distribution) == len(other.pitch_class_distribution) == 12:
            pcd_sim = 1.0 - cosine(self.pitch_class_distribution, other.pitch_class_distribution)
            similarities.append(pcd_sim * 0.25)  # 25% weight

        # Spectral features similarity
        if self.spectral_centroid and other.spectral_centroid:
            spec_sim = 1.0 - min(abs(np.mean(self.spectral_centroid) - np.mean(other.spectral_centroid)) /
                                 max(np.mean(self.spectral_centroid), np.mean(other.spectral_centroid)), 1.0)
            similarities.append(spec_sim * 0.15)  # 15% weight

        # Duration similarity
        if self.duration > 0 and other.duration > 0:
            dur_sim = 1.0 - min(abs(self.duration - other.duration) / max(self.duration, other.duration), 1.0)
            similarities.append(dur_sim * 0.15)  # 15% weight

        return sum(similarities) if similarities else 0.0

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of audio file"""
        import hashlib

        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert features to dictionary for JSON serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                result[key] = value.tolist() if value.size > 0 else []
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFeatures':
        """Create AudioFeatures from dictionary"""
        # Convert lists back to numpy arrays where needed
        numpy_fields = ['chroma_features', 'mfccs', 'harmonic_content', 'percussive_content', 'groove_template']
        for field in numpy_fields:
            if field in data and isinstance(data[field], list):
                data[field] = np.array(data[field])
        
        if 'analysis_level' in data and isinstance(data['analysis_level'], str):
            data['analysis_level'] = AnalysisLevel(data['analysis_level'])
            
        return cls(**data)


class AudioProcessor:
    """Advanced audio processing utilities"""
    
    @staticmethod
    def normalize_audio(y: np.ndarray, target_lufs: float = -23.0) -> np.ndarray:
        """Normalize audio to target LUFS level"""
        # Simple peak normalization (can be enhanced with pyloudnorm for LUFS)
        peak = np.max(np.abs(y))
        if peak > 0:
            return y / peak * 0.95  # Leave some headroom
        return y
    
    @staticmethod
    def apply_high_pass_filter(y: np.ndarray, sr: int, cutoff: float = 80.0) -> np.ndarray:
        """Apply high-pass filter to remove low-frequency noise"""
        nyquist = sr // 2
        normalized_cutoff = cutoff / nyquist
        b, a = signal.butter(4, normalized_cutoff, btype='high')
        return signal.filtfilt(b, a, y)
    
    @staticmethod
    def extract_harmonic_percussive(y: np.ndarray, margin: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Separate harmonic and percussive components of an audio signal.
        
        Args:
            y: Audio time series. Must be a 1D numpy array of floats.
            margin: Margin for harmonic/percussive separation (1.0-10.0, higher values make separation more aggressive)
            
        Returns:
            Tuple of (y_harmonic, y_percussive)
            
        Raises:
            ValueError: If input is not a 1D numpy array or has invalid values
            RuntimeError: If separation fails
        """
        # Input validation
        if not isinstance(y, np.ndarray) or y.ndim != 1:
            raise ValueError("Input must be a 1D numpy array")
            
        if len(y) < 512:  # Minimum length for STFT
            raise ValueError(f"Input signal too short for HPSS. Got {len(y)} samples, need at least 512.")
            
        if not np.isfinite(y).all():
            raise ValueError("Input contains NaN or infinite values")
            
        if margin < 1.0 or margin > 10.0:
            raise ValueError(f"Margin must be between 1.0 and 10.0, got {margin}")
            
        try:
            # Normalize input to prevent numerical issues
            y_norm = y / (np.max(np.abs(y)) + 1e-8)
            
            # Compute short-time Fourier transform with appropriate window size
            n_fft = min(2048, len(y_norm) // 4)  # Adjust FFT size based on input length
            hop_length = n_fft // 4
            
            D = librosa.stft(
                y_norm,
                n_fft=n_fft,
                hop_length=hop_length,
                window='hann',
                center=True,
                pad_mode='reflect'
            )
            
            # Separate harmonic and percussive components
            D_harmonic, D_percussive = librosa.decompose.hpss(
                D,
                margin=margin,
                kernel_size=31,  # Larger kernel for better separation
                power=2.0       # Power of the margin distance
            )
            
            # Invert back to time domain
            y_harmonic = librosa.istft(
                D_harmonic,
                hop_length=hop_length,
                length=len(y_norm),
                window='hann'
            )
            
            y_percussive = librosa.istft(
                D_percussive,
                hop_length=hop_length,
                length=len(y_norm),
                window='hann'
            )
            
            # Ensure output has same scale as input
            scale = np.max(np.abs(y)) / (np.max(np.abs([y_harmonic, y_percussive])) + 1e-8)
            y_harmonic = y_harmonic * scale
            y_percussive = y_percussive * scale
            
            # Ensure perfect reconstruction (y ≈ y_harmonic + y_percussive)
            y_combined = y_harmonic + y_percussive
            if not np.allclose(y_norm, y_combined, atol=1e-4):
                # If reconstruction isn't perfect, adjust to match input
                y_harmonic = y_harmonic * (y_norm / (y_combined + 1e-8))
                y_percussive = y_percussive * (y_norm / (y_combined + 1e-8))
            
            return y_harmonic, y_percussive
            
        except Exception as e:
            raise RuntimeError(f"HPSS separation failed: {str(e)}")


class AdvancedFeatureExtractor:
    """
    Advanced feature extraction for professional music analysis.
    
    This class provides high-level methods for extracting various audio features
    with automatic caching and performance optimizations.
    """
    
    def __init__(self, sample_rate: int = 44100, use_cache: bool = True):
        """
        Initialize the feature extractor.
        
        Args:
            sample_rate: Target sample rate for audio processing
            use_cache: Whether to use the feature cache
        """
        self.sample_rate = sample_rate
        self.hop_length = 512
        self.n_fft = 2048
        self.use_cache = use_cache
        self._cache = cache if use_cache else None
        
    def extract_tonal_features(self, y: np.ndarray) -> Dict[str, Any]:
        """
        Extract comprehensive tonal features including key and pitch information.
        
        Args:
            y: Audio time series
            
        Returns:
            Dictionary containing tonal features
        """
        # Compute chroma features for key detection
        chroma = librosa.feature.chroma_stft(y=y, sr=self.sample_rate, hop_length=self.hop_length)
        chroma_mean = np.mean(chroma, axis=1)
        
        # Get key and mode
        key, mode = self._estimate_key_mode(chroma_mean)
        
        # Compute harmonic and percussive components
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        # Get harmonic ratio
        harmonic_ratio = np.mean(y_harmonic**2) / (np.mean(y_harmonic**2) + np.mean(y_percussive**2) + 1e-6)
        
        return {
            'chroma': chroma,
            'chroma_mean': chroma_mean,
            'key': key,
            'mode': mode,
            'harmonic_ratio': harmonic_ratio,
            'pitch_class_distribution': chroma_mean.tolist()
        }
        
    def extract_rhythmic_features(self, y: np.ndarray) -> Dict[str, Any]:
        """
        Extract rhythm and tempo information from audio.
        
        Args:
            y: Audio time series
            
        Returns:
            Dictionary containing rhythmic features
        """
        # Check cache first if enabled
        cache_key = self._get_cache_key('rhythm', y)
        if self.use_cache and self._cache:
            cached = self._cache.get(y, cache_key)
            if cached is not None:
                return cached
        
        start_time = time.time()
        
        try:
            # Compute onset envelope
            onset_env = librosa.onset.onset_strength(y=y, sr=self.sample_rate, hop_length=self.hop_length)
            
            # Estimate tempo
            tempo, beat_frames = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Ensure tempo is a scalar value
            if isinstance(tempo, (np.ndarray, list)):
                tempo = tempo[0] if len(tempo) > 0 else 120.0  # Default to 120 BPM if no tempo detected
            
            # Get beat times
            beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate, hop_length=self.hop_length)
            
            # Get onset times
            onset_frames = librosa.onset.onset_detect(
                y=y, 
                sr=self.sample_rate,
                hop_length=self.hop_length,
                backtrack=True
            )
            onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate, hop_length=self.hop_length)
            
            # Compute rhythm pattern
            rhythm_pattern = self._analyze_rhythm_pattern(beat_times, onset_times)
            
            result = {
                'tempo': float(tempo),
                'beat_times': beat_times.tolist(),
                'onset_times': onset_times.tolist(),
                'onset_env': onset_env.tolist(),
                'rhythm_pattern': rhythm_pattern,
                '_cached': False
            }
            
            # Cache the result
            if self.use_cache and self._cache:
                self._cache.set(y, cache_key, result)
                result['_cached'] = True
                
            processing_time = time.time() - start_time
            logger.debug(f"Extracted rhythmic features in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting rhythmic features: {e}")
            raise
        
    def extract_spectral_features(self, y: np.ndarray) -> Dict[str, Any]:
        """
        Extract spectral characteristics from audio.
        
        Args:
            y: Audio time series
            
        Returns:
            Dictionary containing spectral features
        """
        # Check cache first if enabled
        cache_key = self._get_cache_key('spectral', y)
        if self.use_cache and self._cache:
            cached = self._cache.get(y, cache_key)
            if cached is not None:
                return cached
        
        start_time = time.time()
        
        try:
            # Compute spectral features in parallel where possible
            with np.errstate(divide='ignore', invalid='ignore'):
                # Use stft as a basis for multiple features
                D = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))
                
                # Compute features in parallel
                spectral_centroid = librosa.feature.spectral_centroid(
                    S=D, 
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )
                
                spectral_bandwidth = librosa.feature.spectral_bandwidth(
                    S=D, 
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )
                
                spectral_rolloff = librosa.feature.spectral_rolloff(
                    S=D, 
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )
                
                # These features don't use the STFT
                zero_crossing_rate = librosa.feature.zero_crossing_rate(
                    y, 
                    hop_length=self.hop_length
                )
                
                rms_energy = librosa.feature.rms(
                    y=y, 
                    hop_length=self.hop_length
                )
            
            result = {
                'spectral_centroid': spectral_centroid[0].tolist(),
                'spectral_bandwidth': spectral_bandwidth[0].tolist(),
                'spectral_rolloff': spectral_rolloff[0].tolist(),
                'zero_crossing_rate': zero_crossing_rate[0].tolist(),
                'rms_energy': rms_energy[0].tolist(),
                '_cached': False
            }
            
            # Cache the result
            if self.use_cache and self._cache:
                self._cache.set(y, cache_key, result)
                result['_cached'] = True
            
            processing_time = time.time() - start_time
            logger.debug(f"Extracted spectral features in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting spectral features: {e}")
            raise
        
    def extract_mfcc_features(self, y: np.ndarray, n_mfcc: int = 20) -> Dict[str, Any]:
        """
        Extract Mel-frequency cepstral coefficients (MFCCs) from audio.
        
        Args:
            y: Audio time series
            n_mfcc: Number of MFCCs to return
            
        Returns:
            Dictionary containing MFCC features
        """
        # Check cache first if enabled
        cache_key = self._get_cache_key(f'mfcc_{n_mfcc}', y)
        if self.use_cache and self._cache:
            cached = self._cache.get(y, cache_key)
            if cached is not None:
                return cached
        
        start_time = time.time()
        
        try:
            # Use a larger FFT window for better frequency resolution
            n_fft = min(4096, len(y) // 4)  # Adjust based on signal length
            
            # Extract MFCCs with optimized parameters
            mfcc = librosa.feature.mfcc(
                y=y,
                sr=self.sample_rate,
                n_mfcc=n_mfcc,
                n_fft=n_fft,
                hop_length=self.hop_length,
                n_mels=128,  # Increased mel bands for better resolution
                fmin=20,     # Lower frequency bound (Hz)
                fmax=8000,   # Upper frequency bound (Hz)
                htk=True     # Use HTK formula for mel scaling (matches some other tools)
            )
            
            # Compute delta and delta-delta features
            mfcc_delta = librosa.feature.delta(mfcc)
            mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
            
            result = {
                'mfcc': mfcc.tolist(),
                'mfcc_delta': mfcc_delta.tolist(),
                'mfcc_delta2': mfcc_delta2.tolist(),
                '_cached': False
            }
            
            # Cache the result
            if self.use_cache and self._cache:
                self._cache.set(y, cache_key, result)
                result['_cached'] = True
            
            processing_time = time.time() - start_time
            logger.debug(f"Extracted {n_mfcc} MFCCs in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting MFCC features: {e}")
            raise
            'mfcc_std': mfcc_std.tolist()
        }
        
    def _get_cache_key(self, feature_type: str, y: np.ndarray) -> Dict[str, Any]:
        """
        Generate cache key for the given feature type and audio data.
        
        Args:
            feature_type: Type of feature being extracted
            y: Audio time series
            
        Returns:
            Dictionary of parameters for caching
        """
        import hashlib
        return {
            'feature_type': feature_type,
            'sample_rate': self.sample_rate,
            'hop_length': self.hop_length,
            'n_fft': self.n_fft,
            'audio_length': len(y),
            'audio_hash': hashlib.sha256(y.tobytes()).hexdigest()[:16]  # First 16 chars of hash
        }
        
    def _estimate_key_mode(self, chroma_mean: np.ndarray) -> Tuple[str, str]:
        """
        Estimate musical key and mode from chroma features.
        
        Args:
            chroma_mean: Mean chroma features (12-dimensional vector)
            
        Returns:
            Tuple of (key, mode) where key is a note name (A-G) and mode is 'major' or 'minor'
        """
        # Chroma features for major and minor keys (Krumhansl-Kessler profiles)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Normalize profiles
        major_profile = major_profile / np.linalg.norm(major_profile)
        minor_profile = minor_profile / np.linalg.norm(minor_profile)
        
        # Compute correlation with all 24 possible keys
        correlations = {}
        for i in range(12):
            # Major key
            shifted = np.roll(chroma_mean, i)
            major_corr = np.corrcoef(shifted, major_profile)[0, 1]
            correlations[(i, 'major')] = major_corr
            
            # Minor key
            minor_corr = np.corrcoef(shifted, minor_profile)[0, 1]
            correlations[(i, 'minor')] = minor_corr
        
        # Find the best matching key and mode
        (shift, mode), _ = max(correlations.items(), key=lambda x: x[1])
        
        # Map shift to note name
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = notes[shift]
        
        return key, mode
        
    def _analyze_rhythm_pattern(self, beat_times: np.ndarray, onset_times: np.ndarray) -> List[float]:
        """
        Analyze rhythm pattern complexity based on beat and onset times.
        
        Args:
            beat_times: Array of beat times in seconds
            onset_times: Array of onset times in seconds
            
        Returns:
            List of rhythm pattern features
        """
        # Initialize pattern array (16 steps)
        pattern = np.zeros(16, dtype=np.float32)
        
        if len(beat_times) < 2:
            return [0.0] * 4  # Default pattern for too few beats
            
        # Calculate average beat duration
        beat_duration = np.mean(np.diff(beat_times)) if len(beat_times) > 1 else 0.5
        
        for onset in onset_times:
            # Find the closest beat
            beat_distances = np.abs(beat_times - onset)
            closest_beat_idx = np.argmin(beat_distances)
            
            if closest_beat_idx < len(beat_times):
                # Map to 16-step grid (4 beats * 4 subdivisions)
                beat_position = closest_beat_idx % 4  # Position within current measure
                relative_position = (onset - beat_times[closest_beat_idx]) / beat_duration
                grid_position = int(beat_position * 4 + relative_position * 4)
                grid_position = max(0, min(15, grid_position))
                pattern[grid_position] += 1
        
        # Normalize pattern to sum to 1.0
        if np.sum(pattern) > 0:
            pattern = pattern / np.sum(pattern)
        
        # Return first 4 features: downbeat, backbeat, offbeat, and syncopation
        return [
            np.mean(pattern[::4]),  # Downbeats
            np.mean(pattern[2::4]),  # Backbeats
            np.mean(pattern[1::2]),  # All offbeats
            np.mean(np.abs(np.diff(pattern)))  # Syncopation
        ]


class AudioEngine:
    """
    Main SampleMind AI Audio Engine
    
    Provides comprehensive audio analysis capabilities for professional music production.
    Designed to integrate seamlessly with FL Studio and other DAWs.
    """
    
    def __init__(self, max_workers: int = 4, cache_size: int = 1000):
        self.max_workers = max_workers
        self.cache_size = cache_size
        self.feature_cache = {}
        self.processor = AudioProcessor()
        self.feature_extractor = AdvancedFeatureExtractor()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance monitoring
        self.analysis_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(f"🎵 SampleMind Audio Engine initialized with {max_workers} workers")
    
    def load_audio(self, file_path: Union[str, Path], target_sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """
        Load audio file with automatic format detection and conversion
        
        Args:
            file_path: Path to audio file
            target_sr: Target sample rate (None for original)
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            # Load audio using soundfile for better format support
            y, sr = sf.read(str(file_path), always_2d=False)
            
            # Convert to mono if stereo
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
            
            # Resample if target sample rate specified
            if target_sr and sr != target_sr:
                y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
                sr = target_sr
            
            # Normalize audio
            y = self.processor.normalize_audio(y)
            
            # Apply high-pass filter to remove low-frequency noise
            y = self.processor.apply_high_pass_filter(y, sr)
            
            logger.info(f"✅ Loaded audio: {file_path.name} ({len(y)/sr:.2f}s, {sr}Hz)")
            return y, sr
            
        except Exception as e:
            logger.error(f"❌ Failed to load audio {file_path}: {e}")
            raise
    
    def analyze_audio(
        self, 
        file_path: Union[str, Path], 
        level: AnalysisLevel = AnalysisLevel.STANDARD,
        use_cache: bool = True
    ) -> AudioFeatures:
        """
        Comprehensive audio analysis
        
        Args:
            file_path: Path to audio file
            level: Analysis complexity level
            use_cache: Whether to use feature cache
            
        Returns:
            AudioFeatures object with comprehensive analysis
        """
        file_path = Path(file_path)
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(file_path, level)
        
        # Check cache
        if use_cache and cache_key in self.feature_cache:
            self.cache_hits += 1
            logger.info(f"📦 Cache hit for {file_path.name}")
            return self.feature_cache[cache_key]
        
        self.cache_misses += 1
        
        try:
            # Load audio
            y, sr = self.load_audio(file_path)
            
            # Initialize features
            features = AudioFeatures(
                duration=len(y) / sr,
                sample_rate=sr,
                channels=1,  # We convert to mono
                file_hash=self._compute_file_hash(file_path),
                file_size=file_path.stat().st_size,
                analysis_level=level
            )
            
            # Basic analysis (always performed)
            tonal_features = self.feature_extractor.extract_tonal_features(y)
            rhythmic_features = self.feature_extractor.extract_rhythmic_features(y)
            spectral_features = self.feature_extractor.extract_spectral_features(y)
            
            # Update features
            features.chroma_features = tonal_features['chroma_features']
            features.key = tonal_features['key']
            features.mode = tonal_features['mode']
            features.pitch_class_distribution = tonal_features['pitch_class_distribution']
            
            features.tempo = rhythmic_features['tempo']
            features.beats = rhythmic_features['beats']
            features.onset_times = rhythmic_features['onset_times']
            features.rhythm_pattern = rhythmic_features['rhythm_pattern']
            
            features.spectral_centroid = spectral_features['spectral_centroid']
            features.spectral_bandwidth = spectral_features['spectral_bandwidth']
            features.spectral_rolloff = spectral_features['spectral_rolloff']
            features.zero_crossing_rate = spectral_features['zero_crossing_rate']
            features.mfccs = spectral_features['mfccs']
            features.rms_energy = spectral_features['rms_energy']
            
            # Advanced analysis for higher levels
            if level in [AnalysisLevel.DETAILED, AnalysisLevel.PROFESSIONAL]:
                harmonic, percussive = self.processor.extract_harmonic_percussive(y)
                features.harmonic_content = harmonic
                features.percussive_content = percussive
            
            # Professional analysis
            if level == AnalysisLevel.PROFESSIONAL:
                # Additional advanced features can be added here
                pass
            
            # Cache results
            if use_cache:
                self._cache_features(cache_key, features)
            
            analysis_time = time.time() - start_time
            self.analysis_times.append(analysis_time)
            
            logger.info(f"🎯 Analysis complete: {file_path.name} ({analysis_time:.2f}s, {level.value})")
            return features
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {file_path}: {e}")
            raise
    
    async def analyze_audio_async(
        self, 
        file_path: Union[str, Path], 
        level: AnalysisLevel = AnalysisLevel.STANDARD
    ) -> AudioFeatures:
        """Asynchronous audio analysis"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.analyze_audio, 
            file_path, 
            level, 
            True
        )
    
    def batch_analyze(
        self, 
        file_paths: List[Union[str, Path]], 
        level: AnalysisLevel = AnalysisLevel.STANDARD,
        parallel: bool = True
    ) -> List[AudioFeatures]:
        """
        Batch analyze multiple audio files
        
        Args:
            file_paths: List of audio file paths
            level: Analysis complexity level
            parallel: Whether to process in parallel
            
        Returns:
            List of AudioFeatures objects
        """
        logger.info(f"🔄 Starting batch analysis of {len(file_paths)} files")
        
        if parallel:
            # Parallel processing
            futures = []
            for file_path in file_paths:
                future = self.executor.submit(self.analyze_audio, file_path, level)
                futures.append(future)
            
            results = []
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"📈 Progress: {i+1}/{len(file_paths)}")
                except Exception as e:
                    logger.error(f"❌ Failed to analyze {file_paths[i]}: {e}")
                    # Create empty features for failed analysis
                    empty_features = AudioFeatures(duration=0, sample_rate=44100, channels=0)
                    results.append(empty_features)
            
            return results
        else:
            # Sequential processing
            results = []
            for i, file_path in enumerate(file_paths):
                try:
                    features = self.analyze_audio(file_path, level)
                    results.append(features)
                    logger.info(f"📈 Progress: {i+1}/{len(file_paths)}")
                except Exception as e:
                    logger.error(f"❌ Failed to analyze {file_path}: {e}")
                    empty_features = AudioFeatures(duration=0, sample_rate=44100, channels=0)
                    results.append(empty_features)
            
            return results
    
    def compare_audio_similarity(
        self, 
        features1: AudioFeatures, 
        features2: AudioFeatures,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Compare similarity between two audio files based on their features
        
        Args:
            features1: First audio features
            features2: Second audio features
            weights: Custom weights for different feature types
            
        Returns:
            Similarity score (0.0 - 1.0, higher is more similar)
        """
        if weights is None:
            weights = {
                'tempo': 0.2,
                'key': 0.15,
                'chroma': 0.25,
                'mfcc': 0.25,
                'spectral': 0.15
            }
        
        similarities = []
        
        # Tempo similarity
        tempo_diff = abs(features1.tempo - features2.tempo)
        tempo_sim = max(0, 1 - tempo_diff / 50.0)  # Normalize by reasonable tempo range
        similarities.append(('tempo', tempo_sim))
        
        # Key similarity (simple approach)
        key_sim = 1.0 if features1.key == features2.key else 0.5
        similarities.append(('key', key_sim))
        
        # Chroma similarity
        if features1.chroma_features.size > 0 and features2.chroma_features.size > 0:
            chroma1_mean = np.mean(features1.chroma_features, axis=1)
            chroma2_mean = np.mean(features2.chroma_features, axis=1)
            chroma_sim = 1 - cosine(chroma1_mean, chroma2_mean)
            similarities.append(('chroma', max(0, chroma_sim)))
        
        # MFCC similarity
        if features1.mfccs.size > 0 and features2.mfccs.size > 0:
            mfcc1_mean = np.mean(features1.mfccs, axis=1)
            mfcc2_mean = np.mean(features2.mfccs, axis=1)
            mfcc_sim = 1 - cosine(mfcc1_mean, mfcc2_mean)
            similarities.append(('mfcc', max(0, mfcc_sim)))
        
        # Spectral similarity
        if (len(features1.spectral_centroid) > 0 and len(features2.spectral_centroid) > 0):
            spec1 = np.mean(features1.spectral_centroid)
            spec2 = np.mean(features2.spectral_centroid)
            spec_diff = abs(spec1 - spec2)
            spec_sim = max(0, 1 - spec_diff / 5000.0)  # Normalize by frequency range
            similarities.append(('spectral', spec_sim))
        
        # Weighted average
        total_weight = 0
        weighted_sum = 0
        
        for feature_type, sim_value in similarities:
            if feature_type in weights:
                weight = weights[feature_type]
                weighted_sum += sim_value * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_analysis_time = np.mean(self.analysis_times) if self.analysis_times else 0
        cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        return {
            'total_analyses': len(self.analysis_times),
            'avg_analysis_time': avg_analysis_time,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.feature_cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses
        }
    
    def export_features(self, features: AudioFeatures, output_path: Union[str, Path]) -> None:
        """Export features to JSON file"""
        output_path = Path(output_path)
        
        with open(output_path, 'w') as f:
            json.dump(features.to_dict(), f, indent=2)
        
        logger.info(f"💾 Features exported to {output_path}")
    
    def import_features(self, input_path: Union[str, Path]) -> AudioFeatures:
        """Import features from JSON file"""
        input_path = Path(input_path)
        
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        features = AudioFeatures.from_dict(data)
        logger.info(f"📁 Features imported from {input_path}")
        return features
    
    def _generate_cache_key(self, file_path: Path, level: AnalysisLevel) -> str:
        """Generate cache key for file"""
        file_stat = file_path.stat()
        key_data = f"{file_path}_{file_stat.st_mtime}_{file_stat.st_size}_{level.value}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _cache_features(self, cache_key: str, features: AudioFeatures) -> None:
        """Cache features with size management"""
        if len(self.feature_cache) >= self.cache_size:
            # Remove oldest entries (simple FIFO for now)
            oldest_key = next(iter(self.feature_cache))
            del self.feature_cache[oldest_key]
        
        self.feature_cache[cache_key] = features
    
    def clear_cache(self) -> None:
        """Clear feature cache"""
        self.feature_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("🧹 Feature cache cleared")
    
    def shutdown(self) -> None:
        """Shutdown the audio engine and cleanup resources"""
        self.executor.shutdown(wait=True)
        logger.info("🔴 Audio Engine shutdown complete")


# FL Studio Plugin Integration Utilities
class FLStudioIntegration:
    """FL Studio specific integration utilities"""
    
    @staticmethod
    def generate_fl_preset(features: AudioFeatures) -> Dict[str, Any]:
        """Generate FL Studio preset based on audio features"""
        preset = {
            'name': f"SampleMind_{features.key}_{int(features.tempo)}BPM",
            'tempo': features.tempo,
            'key': features.key,
            'mode': features.mode,
            'suggested_effects': FLStudioIntegration._suggest_effects(features),
            'mixer_settings': FLStudioIntegration._suggest_mixer_settings(features)
        }
        return preset
    
    @staticmethod
    def _suggest_effects(features: AudioFeatures) -> List[str]:
        """Suggest FL Studio effects based on audio characteristics"""
        effects = []
        
        # Analyze spectral characteristics
        if len(features.spectral_centroid) > 0:
            avg_centroid = np.mean(features.spectral_centroid)
            if avg_centroid > 3000:
                effects.append("Fruity Filter (High Cut)")
            elif avg_centroid < 1000:
                effects.append("Fruity Filter (Low Cut)")
        
        # Analyze dynamics
        if len(features.rms_energy) > 0:
            rms_std = np.std(features.rms_energy)
            if rms_std > 0.1:
                effects.append("Fruity Compressor")
        
        # Tempo-based suggestions
        if features.tempo > 140:
            effects.append("Fruity Reeverb 2 (Short)")
        elif features.tempo < 80:
            effects.append("Fruity Reeverb 2 (Long)")
        
        return effects
    
    @staticmethod
    def _suggest_mixer_settings(features: AudioFeatures) -> Dict[str, Any]:
        """Suggest mixer settings based on audio analysis"""
        settings = {
            'eq': {
                'low_cut': 80 if features.key in ['C', 'D', 'E'] else 60,
                'low_boost': 2 if 'bass' in features.key.lower() else 0,
                'mid_boost': 1 if features.mode == 'major' else -1,
                'high_boost': 3 if np.mean(features.spectral_centroid) > 4000 else 1
            },
            'compression': {
                'ratio': 3.0 if np.std(features.rms_energy) > 0.15 else 2.0,
                'attack': 'fast' if features.tempo > 120 else 'medium',
                'release': 'auto'
            }
        }
        return settings


# Example usage and testing
if __name__ == "__main__":
    # Initialize audio engine
    engine = AudioEngine(max_workers=4)
    
    # Example analysis workflow
    try:
        # This would be used with actual audio files
        logger.info("🎵 SampleMind Audio Engine - Ready for Analysis!")
        logger.info("📋 Supported formats: WAV, MP3, FLAC, AIFF, M4A, OGG")
        logger.info("🔧 Analysis levels: BASIC, STANDARD, DETAILED, PROFESSIONAL")
        logger.info("🎯 FL Studio integration ready!")
        
        # Performance stats
        stats = engine.get_performance_stats()
        logger.info(f"📊 Engine Stats: {stats}")
        
    except Exception as e:
        logger.error(f"❌ Engine initialization failed: {e}")
    finally:
        engine.shutdown()