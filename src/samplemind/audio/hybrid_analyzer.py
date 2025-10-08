"""
Hybrid Audio Analyzer

Intelligently uses Essentia for high-performance analysis with automatic
fallback to librosa when Essentia is unavailable or fails.

Key Features:
- Automatic backend selection (Essentia preferred, librosa fallback)
- Transparent API - same interface regardless of backend
- Performance comparison logging
- Graceful error handling with fallbacks
- Compatible with existing AudioFeatures format
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from dataclasses import dataclass, field
import numpy as np
from loguru import logger

# Try to import Essentia analyzer
try:
    from .essentia_analyzer import (
        EssentiaAnalyzer,
        EssentiaFeatures,
        ESSENTIA_AVAILABLE
    )
except ImportError:
    ESSENTIA_AVAILABLE = False
    logger.warning("Essentia analyzer not available")

# Import librosa (fallback)
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.error("librosa not available - audio analysis will fail!")

# Import core AudioFeatures for compatibility
try:
    from samplemind.core.engine.audio_engine import AudioFeatures as CoreAudioFeatures
    CORE_FEATURES_AVAILABLE = True
except ImportError:
    CORE_FEATURES_AVAILABLE = False

# Import monitoring
try:
    from samplemind.monitoring.metrics import record_audio_processing
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class AnalysisBackend(Enum):
    """Available analysis backends"""
    ESSENTIA = "essentia"
    LIBROSA = "librosa"
    AUTO = "auto"


@dataclass
class HybridAnalysisResult:
    """
    Unified analysis result that works with both backends.
    Compatible with existing AudioFeatures format.
    """
    # Core features (common to both backends)
    duration: float = 0.0
    sample_rate: int = 44100
    channels: int = 1
    
    # Rhythm features
    tempo: float = 0.0
    beats: List[float] = field(default_factory=list)
    onset_times: List[float] = field(default_factory=list)
    
    # Tonal features
    key: str = "C"
    mode: str = "major"
    pitch_class_distribution: List[float] = field(default_factory=list)
    
    # Spectral features
    spectral_centroid: List[float] = field(default_factory=list)
    spectral_bandwidth: List[float] = field(default_factory=list)
    spectral_rolloff: List[float] = field(default_factory=list)
    zero_crossing_rate: List[float] = field(default_factory=list)
    
    # Timbre features
    mfccs: np.ndarray = field(default_factory=lambda: np.array([]))
    chroma_features: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Energy features
    rms_energy: List[float] = field(default_factory=list)
    
    # Performance metrics
    analysis_time: float = 0.0
    backend_used: str = "unknown"
    backend_confidence: float = 1.0
    
    # File metadata
    file_path: str = ""
    file_size: int = 0
    file_hash: str = ""
    
    def to_core_audio_features(self) -> Optional['CoreAudioFeatures']:
        """Convert to core AudioFeatures format for backward compatibility"""
        if not CORE_FEATURES_AVAILABLE:
            return None
        
        try:
            return CoreAudioFeatures(
                duration=self.duration,
                sample_rate=self.sample_rate,
                channels=self.channels,
                tempo=self.tempo,
                beats=self.beats,
                onset_times=self.onset_times,
                key=self.key,
                mode=self.mode,
                pitch_class_distribution=self.pitch_class_distribution,
                spectral_centroid=self.spectral_centroid,
                spectral_bandwidth=self.spectral_bandwidth,
                spectral_rolloff=self.spectral_rolloff,
                zero_crossing_rate=self.zero_crossing_rate,
                mfccs=self.mfccs,
                chroma_features=self.chroma_features,
                rms_energy=self.rms_energy,
                file_hash=self.file_hash,
                file_size=self.file_size,
            )
        except Exception as e:
            logger.warning(f"Failed to convert to CoreAudioFeatures: {e}")
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                result[key] = value.tolist() if value.size > 0 else []
            else:
                result[key] = value
        return result


class HybridAnalyzer:
    """
    Intelligent audio analyzer that uses Essentia when available,
    with automatic fallback to librosa.
    
    Features:
    - Automatic backend selection
    - Transparent API
    - Performance comparison
    - Graceful error handling
    - Backward compatibility
    
    Usage:
        analyzer = HybridAnalyzer(prefer_backend=AnalysisBackend.AUTO)
        result = analyzer.analyze("audio.wav")
        print(f"BPM: {result.tempo}, Backend: {result.backend_used}")
    """
    
    def __init__(
        self,
        prefer_backend: AnalysisBackend = AnalysisBackend.AUTO,
        sample_rate: int = 44100,
        enable_fallback: bool = True,
    ):
        """
        Initialize hybrid analyzer.
        
        Args:
            prefer_backend: Preferred backend (AUTO, ESSENTIA, or LIBROSA)
            sample_rate: Target sample rate
            enable_fallback: Enable automatic fallback on errors
        """
        self.prefer_backend = prefer_backend
        self.sample_rate = sample_rate
        self.enable_fallback = enable_fallback
        
        # Initialize backends
        self.essentia_analyzer = None
        self.librosa_available = LIBROSA_AVAILABLE
        
        if ESSENTIA_AVAILABLE:
            try:
                self.essentia_analyzer = EssentiaAnalyzer(sample_rate=sample_rate)
                logger.info("Essentia backend initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Essentia: {e}")
        
        # Determine active backend
        self.active_backend = self._determine_backend()
        
        # Performance tracking
        self.backend_performance = {
            'essentia': {'count': 0, 'total_time': 0.0, 'errors': 0},
            'librosa': {'count': 0, 'total_time': 0.0, 'errors': 0},
        }
        
        logger.info(
            f"HybridAnalyzer initialized: "
            f"active_backend={self.active_backend.value}, "
            f"essentia_available={ESSENTIA_AVAILABLE}, "
            f"librosa_available={LIBROSA_AVAILABLE}"
        )
    
    def _determine_backend(self) -> AnalysisBackend:
        """Determine which backend to use"""
        if self.prefer_backend == AnalysisBackend.ESSENTIA:
            if self.essentia_analyzer:
                return AnalysisBackend.ESSENTIA
            elif self.enable_fallback and self.librosa_available:
                logger.warning("Essentia preferred but not available, falling back to librosa")
                return AnalysisBackend.LIBROSA
            else:
                raise RuntimeError("Essentia not available and fallback disabled")
        
        elif self.prefer_backend == AnalysisBackend.LIBROSA:
            if self.librosa_available:
                return AnalysisBackend.LIBROSA
            else:
                raise RuntimeError("librosa not available")
        
        else:  # AUTO
            # Prefer Essentia for performance
            if self.essentia_analyzer:
                return AnalysisBackend.ESSENTIA
            elif self.librosa_available:
                return AnalysisBackend.LIBROSA
            else:
                raise RuntimeError("No audio analysis backend available")
    
    def analyze(
        self,
        file_path: Union[str, Path],
        backend: Optional[AnalysisBackend] = None,
    ) -> HybridAnalysisResult:
        """
        Analyze audio file using best available backend.
        
        Args:
            file_path: Path to audio file
            backend: Override backend selection (None = use active_backend)
            
        Returns:
            HybridAnalysisResult with comprehensive audio features
        """
        file_path = Path(file_path)
        start_time = time.time()
        
        # Determine backend to use
        use_backend = backend if backend else self.active_backend
        
        # Try primary backend
        try:
            if use_backend == AnalysisBackend.ESSENTIA:
                result = self._analyze_with_essentia(file_path)
            else:
                result = self._analyze_with_librosa(file_path)
            
            # Record success
            analysis_time = time.time() - start_time
            result.analysis_time = analysis_time
            
            self.backend_performance[result.backend_used]['count'] += 1
            self.backend_performance[result.backend_used]['total_time'] += analysis_time
            
            logger.info(
                f"Analysis complete: {file_path.name} "
                f"({analysis_time:.2f}s, backend={result.backend_used}, "
                f"BPM={result.tempo:.1f}, Key={result.key})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed with {use_backend.value}: {e}")
            self.backend_performance[use_backend.value]['errors'] += 1
            
            # Try fallback if enabled
            if self.enable_fallback:
                fallback_backend = (
                    AnalysisBackend.LIBROSA if use_backend == AnalysisBackend.ESSENTIA
                    else AnalysisBackend.ESSENTIA if self.essentia_analyzer
                    else None
                )
                
                if fallback_backend:
                    logger.warning(f"Attempting fallback to {fallback_backend.value}")
                    try:
                        return self.analyze(file_path, backend=fallback_backend)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {fallback_error}")
            
            raise
    
    def _analyze_with_essentia(self, file_path: Path) -> HybridAnalysisResult:
        """Analyze using Essentia backend"""
        if not self.essentia_analyzer:
            raise RuntimeError("Essentia not available")
        
        # Get Essentia features
        essentia_features = self.essentia_analyzer.analyze(file_path)
        
        # Convert to hybrid result
        result = HybridAnalysisResult(
            duration=essentia_features.duration,
            sample_rate=essentia_features.sample_rate,
            tempo=essentia_features.bpm,
            beats=essentia_features.beats_position,
            onset_times=essentia_features.onset_times,
            key=essentia_features.key,
            mode=essentia_features.scale,
            spectral_centroid=essentia_features.spectral_centroid,
            spectral_rolloff=essentia_features.spectral_rolloff,
            mfccs=essentia_features.mfcc,
            chroma_features=essentia_features.chroma,
            rms_energy=essentia_features.spectral_energy,
            backend_used="essentia",
            backend_confidence=essentia_features.bpm_confidence,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
        )
        
        return result
    
    def _analyze_with_librosa(self, file_path: Path) -> HybridAnalysisResult:
        """Analyze using librosa backend"""
        if not self.librosa_available:
            raise RuntimeError("librosa not available")
        
        try:
            # Load audio
            y, sr = librosa.load(str(file_path), sr=self.sample_rate, mono=True)
            
            # Initialize result
            result = HybridAnalysisResult(
                duration=len(y) / sr,
                sample_rate=sr,
                channels=1,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                backend_used="librosa",
            )
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            result.tempo = float(tempo.item() if hasattr(tempo, 'item') else tempo)
            result.beats = librosa.frames_to_time(beats, sr=sr).tolist()
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            result.onset_times = librosa.frames_to_time(onset_frames, sr=sr).tolist()
            
            # Key detection (simple Krumhansl-Schmuckler)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            result.chroma_features = chroma
            chroma_mean = np.mean(chroma, axis=1)
            key, mode = self._estimate_key_librosa(chroma_mean)
            result.key = key
            result.mode = mode
            
            # Pitch class distribution
            pitch_classes = np.sum(chroma, axis=1)
            if np.sum(pitch_classes) > 0:
                result.pitch_class_distribution = (pitch_classes / np.sum(pitch_classes)).tolist()
            
            # Spectral features
            hop_length = 512
            result.spectral_centroid = librosa.feature.spectral_centroid(
                y=y, sr=sr, hop_length=hop_length
            )[0].tolist()
            
            result.spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=y, sr=sr, hop_length=hop_length
            )[0].tolist()
            
            result.spectral_rolloff = librosa.feature.spectral_rolloff(
                y=y, sr=sr, hop_length=hop_length
            )[0].tolist()
            
            result.zero_crossing_rate = librosa.feature.zero_crossing_rate(
                y, hop_length=hop_length
            )[0].tolist()
            
            # MFCC
            result.mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
            
            # RMS energy
            result.rms_energy = librosa.feature.rms(y=y, hop_length=hop_length)[0].tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"librosa analysis failed: {e}")
            raise
    
    def _estimate_key_librosa(self, chroma_mean: np.ndarray) -> Tuple[str, str]:
        """Estimate key using Krumhansl-Schmuckler algorithm"""
        # Key profiles
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 
                                 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        best_score = -1
        best_key = 'C'
        best_mode = 'major'
        
        for i in range(12):
            # Rotate profiles
            major_rotated = np.roll(major_profile, i)
            minor_rotated = np.roll(minor_profile, i)
            
            # Calculate correlation
            major_corr = np.corrcoef(chroma_mean, major_rotated)[0, 1]
            minor_corr = np.corrcoef(chroma_mean, minor_rotated)[0, 1]
            
            if major_corr > best_score:
                best_score = major_corr
                best_key = keys[i]
                best_mode = 'major'
            
            if minor_corr > best_score:
                best_score = minor_corr
                best_key = keys[i]
                best_mode = 'minor'
        
        return best_key, best_mode
    
    def compare_backends(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Compare performance of both backends on the same file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with comparison results
        """
        if not (self.essentia_analyzer and self.librosa_available):
            raise RuntimeError("Both backends must be available for comparison")
        
        results = {}
        
        # Analyze with Essentia
        try:
            start = time.time()
            essentia_result = self._analyze_with_essentia(Path(file_path))
            essentia_time = time.time() - start
            results['essentia'] = {
                'time': essentia_time,
                'bpm': essentia_result.tempo,
                'key': f"{essentia_result.key} {essentia_result.mode}",
                'success': True,
            }
        except Exception as e:
            results['essentia'] = {
                'time': 0,
                'error': str(e),
                'success': False,
            }
        
        # Analyze with librosa
        try:
            start = time.time()
            librosa_result = self._analyze_with_librosa(Path(file_path))
            librosa_time = time.time() - start
            results['librosa'] = {
                'time': librosa_time,
                'bpm': librosa_result.tempo,
                'key': f"{librosa_result.key} {librosa_result.mode}",
                'success': True,
            }
        except Exception as e:
            results['librosa'] = {
                'time': 0,
                'error': str(e),
                'success': False,
            }
        
        # Calculate speedup
        if results['essentia']['success'] and results['librosa']['success']:
            speedup = librosa_time / essentia_time
            results['comparison'] = {
                'speedup': speedup,
                'faster_backend': 'essentia' if speedup > 1 else 'librosa',
                'bpm_match': abs(essentia_result.tempo - librosa_result.tempo) < 5,
                'key_match': essentia_result.key == librosa_result.key,
            }
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all backends"""
        stats = {}
        
        for backend_name, perf in self.backend_performance.items():
            if perf['count'] > 0:
                avg_time = perf['total_time'] / perf['count']
                error_rate = perf['errors'] / (perf['count'] + perf['errors'])
                
                stats[backend_name] = {
                    'analyses': perf['count'],
                    'total_time': perf['total_time'],
                    'avg_time': avg_time,
                    'errors': perf['errors'],
                    'error_rate': error_rate,
                }
        
        # Calculate speedup if both backends used
        if 'essentia' in stats and 'librosa' in stats:
            stats['speedup'] = stats['librosa']['avg_time'] / stats['essentia']['avg_time']
        
        return stats


# Convenience functions
def quick_analyze(file_path: Union[str, Path]) -> HybridAnalysisResult:
    """Quick analysis with automatic backend selection"""
    analyzer = HybridAnalyzer(prefer_backend=AnalysisBackend.AUTO)
    return analyzer.analyze(file_path)


def quick_bpm(file_path: Union[str, Path]) -> float:
    """Quick BPM detection"""
    result = quick_analyze(file_path)
    return result.tempo


def quick_key(file_path: Union[str, Path]) -> Tuple[str, str]:
    """Quick key detection"""
    result = quick_analyze(file_path)
    return result.key, result.mode