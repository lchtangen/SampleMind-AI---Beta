"""
Core audio processing module for SampleMind AI.
Handles audio loading, processing, and feature extraction.
"""
import numpy as np
import librosa
import os
import io
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from queue import Queue
from threading import Lock
from typing import (
    Any, BinaryIO, Callable, Dict, Iterable, List, 
    Optional, Tuple, Union, Generator, TypeVar, Type
)
import soundfile as sf
import numpy as np
import librosa
from tqdm import tqdm
from enum import Enum, auto

# Import audio effects
from .effects import AudioEffectsProcessor, NoiseReduction, EffectType, EffectParameters


class AudioFormat(str, Enum):
    """Supported audio formats for conversion."""
    WAV = 'wav'
    MP3 = 'mp3'
    FLAC = 'flac'
    AIFF = 'aiff'
    OGG = 'ogg'


class BitDepth(int, Enum):
    """Supported bit depths for audio conversion."""
    INT16 = 16
    INT24 = 24
    FLOAT32 = 32


class ChannelMode(str, Enum):
    """Supported channel modes for audio conversion."""
    MONO = 'mono'
    STEREO = 'stereo'

@dataclass
class AudioFeatures:
    """Container for extracted audio features."""
    tempo: float
    key: str
    mode: str
    beats: np.ndarray
    chroma: np.ndarray
    mfcc: np.ndarray
    spectral_contrast: np.ndarray
    tonnetz: np.ndarray
    zcr: np.ndarray
    rmse: np.ndarray
    spectral_centroid: np.ndarray
    spectral_bandwidth: np.ndarray
    spectral_rolloff: np.ndarray
    harmonic: np.ndarray
    percussive: np.ndarray
    beat_frames: np.ndarray
    beat_times: np.ndarray
    duration: float
    sample_rate: int
    
    def to_dict(self) -> Dict:
        """Convert features to dictionary for serialization."""
        return {
            'tempo': float(self.tempo),
            'key': self.key,
            'mode': self.mode,
            'duration': float(self.duration),
            'sample_rate': self.sample_rate,
            'features': {
                'chroma': self.chroma.tolist(),
                'mfcc': self.mfcc.tolist(),
                'spectral_contrast': self.spectral_contrast.tolist(),
                'tonnetz': self.tonnetz.tolist(),
                'zcr': self.zcr.tolist(),
                'rmse': self.rmse.tolist(),
                'spectral_centroid': self.spectral_centroid.tolist(),
                'spectral_bandwidth': self.spectral_bandwidth.tolist(),
                'spectral_rolloff': self.spectral_rolloff.tolist(),
                'beat_frames': self.beat_frames.tolist(),
                'beat_times': self.beat_times.tolist()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AudioFeatures':
        """Create AudioFeatures from dictionary."""
        features = data.get('features', {})
        return cls(
            tempo=data.get('tempo', 0),
            key=data.get('key', 'C'),
            mode=data.get('mode', 'major'),
            beats=np.array([]),  # Not stored in dict
            chroma=np.array(features.get('chroma', [])),
            mfcc=np.array(features.get('mfcc', [])),
            spectral_contrast=np.array(features.get('spectral_contrast', [])),
            tonnetz=np.array(features.get('tonnetz', [])),
            zcr=np.array(features.get('zcr', [])),
            rmse=np.array(features.get('rmse', [])),
            spectral_centroid=np.array(features.get('spectral_centroid', [])),
            spectral_bandwidth=np.array(features.get('spectral_bandwidth', [])),
            spectral_rolloff=np.array(features.get('spectral_rolloff', [])),
            harmonic=np.array([]),  # Not stored in dict
            percussive=np.array([]),  # Not stored in dict
            beat_frames=np.array(features.get('beat_frames', [])),
            beat_times=np.array(features.get('beat_times', [])),
            duration=data.get('duration', 0),
            sample_rate=data.get('sample_rate', 44100)
        )

@dataclass
class BatchProgress:
    """Track progress of batch processing."""
    total: int = 0
    processed: int = 0
    failed: int = 0
    start_time: float = field(default_factory=time.time)
    lock: Lock = field(default_factory=Lock)
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def progress(self) -> float:
        return (self.processed / self.total) * 100 if self.total > 0 else 0.0
    
    @property
    def estimated_remaining_time(self) -> float:
        if self.processed == 0:
            return 0.0
        elapsed = self.elapsed_time
        return (elapsed / self.processed) * (self.total - self.processed)
    
    def increment_processed(self) -> None:
        with self.lock:
            self.processed += 1
    
    def increment_failed(self) -> None:
        with self.lock:
            self.failed += 1


class AudioProcessor:
    """
    Main audio processing class for SampleMind AI.
    
    Features:
    - Audio format conversion (WAV, MP3, FLAC, AIFF, OGG)
    - Advanced audio effects processing
    - Noise reduction and audio restoration
    - Batch processing with progress tracking
    - Multi-threaded processing
    - Comprehensive error handling
    """
    
    def __init__(
        self, 
        sample_rate: int = 44100, 
        n_fft: int = 2048, 
        hop_length: int = 512,
        max_workers: Optional[int] = None,
        progress_callback: Optional[Callable[["BatchProgress"], None]] = None,
        enable_gpu: bool = False
    ):
        """
        Initialize the audio processor.
        
        Args:
            sample_rate: Target sample rate for audio processing (Hz)
            n_fft: Number of FFT points
            hop_length: Hop length for STFT
            max_workers: Maximum number of worker threads for batch processing
            progress_callback: Callback for progress updates
            enable_gpu: Enable GPU acceleration if available
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.max_workers = max_workers or os.cpu_count() or 4
        self.progress_callback = progress_callback
        self._supported_formats = {fmt.value for fmt in AudioFormat}
        self._progress = BatchProgress()
        self._progress_lock = Lock()
        self._stop_event = False
        self._enable_gpu = enable_gpu
        
        # Initialize effects processors
        self.effects_processor = AudioEffectsProcessor(sample_rate)
        self.noise_reducer = NoiseReduction(sample_rate)
        
        # Initialize GPU if enabled
        if enable_gpu:
            self._init_gpu()
    
    def _init_gpu(self):
        """Initialize GPU acceleration if available."""
        try:
            import cupy as cp
            from cupyx.scipy.fft import rfft as curfft
            from cupyx.scipy.fft import irfft as cuirfft
            from cupyx.scipy.fft import fft as cudft
            from cupyx.scipy.fft import ifft as cuidft
            
            self._has_gpu = True
            self._cp = cp
            self._fft = cudft
            self._ifft = cuidft
            self._rfft = curfft
            self._irfft = cuirfft
            
            # Test GPU memory allocation
            _ = cp.array([1, 2, 3])
            
        except ImportError:
            self._has_gpu = False
            import numpy.fft as fft
            self._fft = fft.fft
            self._ifft = fft.ifft
            self._rfft = fft.rfft
            self._irfft = fft.irfft
    
    def _get_audio_format(self, file_path: Union[str, Path, BinaryIO]) -> str:
        """
        Get the audio format from file extension or content.
        
        Args:
            file_path: Path to audio file or file-like object
            
        Returns:
            Format string (e.g., 'wav', 'mp3')
            
        Raises:
            UnsupportedFormatError: If the format is not supported
        """
        if hasattr(file_path, 'name'):  # Handle file-like objects
            ext = os.path.splitext(file_path.name)[1].lower().lstrip('.')
        else:
            ext = Path(file_path).suffix.lower().lstrip('.')
            
        if ext == 'm4a':
            ext = 'aac'  # Handle m4a as aac for librosa
            
        if ext not in self._supported_formats:
            raise UnsupportedFormatError(f"Unsupported audio format: {ext}")
            
        return ext

    def load_audio(
        self, 
        file_path: Union[str, Path, BinaryIO], 
        offset: float = 0.0, 
        duration: Optional[float] = None,
        target_sr: Optional[int] = None,
        mono: bool = True
    ) -> Tuple[np.ndarray, int]:
        """
        Load audio file using librosa with format detection.
        
        Args:
            file_path: Path to audio file or file-like object
            offset: Start reading after this time (in seconds)
            duration: Only load up to this much audio (in seconds)
            target_sr: Target sample rate (None to use instance default)
            mono: Convert to mono if True
            
        Returns:
            Tuple of (audio_data, sample_rate)
            
        Raises:
            AudioProcessingError: If there's an error loading the audio
            UnsupportedFormatError: If the audio format is not supported
        """
        try:
            # Get format and validate
            self._get_audio_format(file_path)
            
            y, sr = librosa.load(
                file_path,
                sr=target_sr or self.sample_rate,
                offset=offset,
                duration=duration,
                mono=mono
            )
            return y, sr
        except UnsupportedFormatError:
            raise
        except Exception as e:
            raise AudioProcessingError(f"Error loading audio file: {str(e)}")
            
    def convert_audio(
        self,
        input_path: Union[str, Path, BinaryIO],
        output_path: Union[str, Path, None] = None,
        output_format: Optional[Union[str, AudioFormat]] = None,
        sample_rate: Optional[int] = None,
        bit_depth: Optional[Union[int, BitDepth]] = None,
        channels: Optional[Union[int, ChannelMode]] = None,
        **kwargs
    ) -> Union[bytes, None]:
        """
        Convert audio file to different format and/or parameters.
        
        Args:
            input_path: Input audio file path or file-like object
            output_path: Output file path (None to return bytes)
            output_format: Target format (wav, mp3, flac, aiff)
            sample_rate: Target sample rate in Hz
            bit_depth: Target bit depth (16, 24, or 32)
            channels: Target number of channels or 'mono'/'stereo'
            **kwargs: Additional arguments for soundfile.write()
            
        Returns:
            bytes if output_path is None, else None
            
        Raises:
            AudioProcessingError: If conversion fails
            UnsupportedFormatError: If format is not supported
        """
        try:
            # Load audio with target sample rate and channels
            if isinstance(channels, ChannelMode):
                mono = channels == ChannelMode.MONO
            else:
                mono = channels == 1 if channels is not None else None
                
            y, sr = self.load_audio(
                input_path,
                target_sr=sample_rate,
                mono=mono if mono is not None else True
            )
            
            # Determine output format
            if output_format is None:
                if output_path is not None:
                    output_format = Path(output_path).suffix.lstrip('.').lower()
                else:
                    output_format = 'wav'  # Default to WAV for in-memory
            
            if isinstance(output_format, AudioFormat):
                output_format = output_format.value
                
            if output_format not in self._supported_formats:
                raise UnsupportedFormatError(f"Unsupported output format: {output_format}")
            
            # Prepare output parameters
            output_kwargs = {
                'format': output_format,
                'subtype': self._get_subtype(bit_depth, output_format),
                **kwargs
            }
            
            # Handle different output types
            if output_path is None:
                # Return as bytes
                with io.BytesIO() as buffer:
                    sf.write(buffer, y.T if y.ndim > 1 else y, sr, **output_kwargs)
                    return buffer.getvalue()
            else:
                # Write to file
                sf.write(output_path, y.T if y.ndim > 1 else y, sr, **output_kwargs)
                return None
                
        except Exception as e:
            raise AudioProcessingError(f"Audio conversion failed: {str(e)}")
    
    def _get_subtype(self, bit_depth: Optional[Union[int, BitDepth]], format: str) -> str:
        """
        Get the appropriate subtype for the given bit depth and format.
        
        Args:
            bit_depth: Target bit depth
            format: Output format
            
        Returns:
            Subtype string for soundfile
        """
        if bit_depth is None:
            return 'PCM_16' if format.lower() != 'flac' else 'PCM_24'
            
        bit_depth = int(bit_depth)
        
        if format.lower() == 'wav' or format.lower() == 'aiff':
            if bit_depth == 16:
                return 'PCM_16'
            elif bit_depth == 24:
                return 'PCM_24'
            elif bit_depth == 32:
                return 'PCM_32' if format.lower() == 'wav' else 'FLOAT'
        elif format.lower() == 'flac':
            return f'PCM_{min(24, bit_depth)}'  # FLAC max is 24-bit
        elif format.lower() == 'mp3':
            return 'MP3'  # MP3 bitrate is handled separately
            
        return 'FLOAT'  # Default to float for other cases
        
    def process_batch(
        self,
        input_paths: Union[str, Path, List[Union[str, Path]]],
        output_dir: Optional[Union[str, Path]] = None,
        output_format: Optional[Union[str, AudioFormat]] = None,
        sample_rate: Optional[int] = None,
        bit_depth: Optional[Union[int, BitDepth]] = None,
        channels: Optional[Union[int, ChannelMode]] = None,
        recursive: bool = False,
        overwrite: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple audio files in batch.
        
        Args:
            input_paths: Single path, list of paths, or directory path
            output_dir: Output directory (required if input_paths is a directory)
            output_format: Target format (wav, mp3, flac, aiff)
            sample_rate: Target sample rate in Hz
            bit_depth: Target bit depth (16, 24, or 32)
            channels: Target number of channels or 'mono'/'stereo'
            recursive: Process directories recursively
            overwrite: Overwrite existing files
            **kwargs: Additional arguments for convert_audio()
            
        Returns:
            List of dictionaries with processing results
            
        Raises:
            ValueError: If input is invalid
        """
        # Reset progress
        self._progress = BatchProgress()
        self._stop_event = False
        
        # Handle different input types
        if isinstance(input_paths, (str, Path)):
            input_path = Path(input_paths)
            if input_path.is_dir():
                if output_dir is None:
                    output_dir = input_path / 'converted'
                input_paths = self._find_audio_files(input_path, recursive)
            else:
                input_paths = [input_path]
                if output_dir is None:
                    output_dir = input_path.parent
        
        # Ensure output directory exists
        output_dir = Path(output_dir) if output_dir else None
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Update progress total
        with self._progress_lock:
            self._progress.total = len(input_paths)
        
        results = []
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for input_path in input_paths:
                if self._stop_event:
                    break
                    
                input_path = Path(input_path)
                
                # Determine output path
                if output_dir:
                    rel_path = input_path.relative_to(input_paths[0].parent) if len(input_paths) > 1 else input_path.name
                    output_path = output_dir / rel_path.with_suffix(f'.{output_format or input_path.suffix.lstrip(".") or "wav"}')
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    output_path = None
                
                # Skip existing files if not overwriting
                if output_path and output_path.exists() and not overwrite:
                    with self._progress_lock:
                        self._progress.processed += 1
                    results.append({
                        'input': str(input_path),
                        'output': str(output_path) if output_path else None,
                        'status': 'skipped',
                        'error': None
                    })
                    continue
                
                # Submit task
                future = executor.submit(
                    self._process_single,
                    input_path=input_path,
                    output_path=output_path,
                    output_format=output_format,
                    sample_rate=sample_rate,
                    bit_depth=bit_depth,
                    channels=channels,
                    **kwargs
                )
                future.add_done_callback(self._handle_completion)
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'input': str(e.args[0]) if e.args else 'Unknown',
                        'output': None,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return results
    
    def stop_processing(self) -> None:
        """Stop the current batch processing."""
        self._stop_event = True
    
    def _process_single(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Process a single audio file with error handling."""
        try:
            input_path = Path(input_path)
            result = {
                'input': str(input_path),
                'output': str(output_path) if output_path else None,
                'status': 'success',
                'error': None
            }
            
            # Process the file
            if output_path is None:
                # In-memory processing
                result['data'] = self.convert_audio(
                    input_path,
                    output_path=None,
                    **kwargs
                )
            else:
                # File-based processing
                self.convert_audio(
                    input_path,
                    output_path=output_path,
                    **kwargs
                )
                
            return result
            
        except Exception as e:
            with self._progress_lock:
                self._progress.failed += 1
            return {
                'input': str(input_path),
                'output': str(output_path) if output_path else None,
                'status': 'error',
                'error': str(e)
            }
    
    def _handle_completion(self, future) -> None:
        """Handle completion of a single task."""
        with self._progress_lock:
            self._progress.processed += 1
            
        # Notify progress
        if self.progress_callback:
            try:
                self.progress_callback(self._progress)
            except Exception:
                pass  # Don't let callback errors break processing
    
    def _find_audio_files(
        self,
        directory: Union[str, Path],
        recursive: bool = False
    ) -> List[Path]:
        """Find audio files in a directory."""
        directory = Path(directory)
        patterns = [f'*.{fmt}' for fmt in self._supported_formats]
        
        if recursive:
            return [
                p for pattern in patterns
                for p in directory.rglob(pattern)
                if p.is_file()
            ]
        else:
            return [
                p for pattern in patterns
                for p in directory.glob(pattern)
                if p.is_file()
            ]
    
    # ======================
    # Audio Effects Methods
    # ======================
    
    def add_effect(self, effect_type: EffectType, params: Optional[Dict[str, Any]] = None) -> 'AudioProcessor':
        """
        Add an audio effect to the processing chain.
        
        Args:
            effect_type: Type of effect to add
            params: Effect parameters
            
        Returns:
            Self for method chaining
        """
        self.effects_processor.add_effect(effect_type, params)
        return self
    
    def clear_effects(self) -> 'AudioProcessor':
        """Clear all effects from the processing chain."""
        self.effects_processor.clear_effects()
        return self
    
    def process_effects(self, y: np.ndarray, sr: Optional[int] = None) -> np.ndarray:
        """
        Process audio with the current effects chain.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            
        Returns:
            Processed audio signal
        """
        if sr is None:
            sr = self.sample_rate
        return self.effects_processor.process(y, sr)
    
    # ======================
    # Noise Reduction Methods
    # ======================
    
    def learn_noise_profile(self, y: np.ndarray, sr: Optional[int] = None) -> 'AudioProcessor':
        """
        Learn the noise profile from a noise-only segment.
        
        Args:
            y: Noise-only audio segment
            sr: Sample rate (if None, use instance sample_rate)
            
        Returns:
            Self for method chaining
        """
        if sr is None:
            sr = self.sample_rate
        self.noise_reducer.learn_noise_profile(y, sr)
        return self
    
    def reduce_noise(self, y: np.ndarray, sr: Optional[int] = None, reduction_db: float = 10.0) -> np.ndarray:
        """
        Reduce noise in the audio signal.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            reduction_db: Amount of noise reduction in dB
            
        Returns:
            Denoised audio signal
        """
        if sr is None:
            sr = self.sample_rate
        return self.noise_reducer.reduce_noise(y, sr, reduction_db)
    
    def remove_clicks(self, y: np.ndarray, sr: Optional[int] = None, **kwargs) -> np.ndarray:
        """
        Remove clicks and pops from audio.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            **kwargs: Additional parameters for click removal
            
        Returns:
            Audio with clicks removed
        """
        if sr is None:
            sr = self.sample_rate
        return self.noise_reducer.remove_clicks(y, sr, **kwargs)
    
    def de_ess(self, y: np.ndarray, sr: Optional[int] = None, threshold: float = 0.2, ratio: float = 4.0) -> np.ndarray:
        """
        Reduce sibilance (ess sounds) in vocal recordings.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            threshold: Threshold for sibilance detection (0-1)
            ratio: Compression ratio for sibilant frequencies
            
        Returns:
            De-essed audio signal
        """
        if sr is None:
            sr = self.sample_rate
        return self.noise_reducer.de_ess(y, sr, threshold, ratio)
    
    # ======================
    # Feature Extraction
    # ======================
    
    def extract_features(self, y: np.ndarray, sr: int) -> AudioFeatures:
        """
        Extract audio features from audio data.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            AudioFeatures object containing extracted features
        """
        try:
            if len(y) == 0:
                return AudioFeatures(
                    tempo=0.0,
                    key='C',
                    mode='major',
                    beats=np.array([]),
                    chroma=np.array([]),
                    mfcc=np.array([]),
                    spectral_contrast=np.array([]),
                    tonnetz=np.array([]),
                    zcr=np.array([]),
                    rmse=np.array([]),
                    spectral_centroid=np.array([]),
                    spectral_bandwidth=np.array([]),
                    spectral_rolloff=np.array([]),
                    harmonic=np.array([]),
                    percussive=np.array([]),
                    beat_frames=np.array([]),
                    beat_times=np.array([]),
                    duration=0.0,
                    sample_rate=sr
                )
                
            # Get duration
            duration = float(len(y)) / sr
            
            # Separate harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            
            # Extract features
            tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            
            # Extract chroma features
            chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
            
            # Extract MFCCs
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            
            # Extract spectral features
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            tonnetz = librosa.feature.tonnetz(y=y_harmonic, sr=sr)
            
            # Extract zero-crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)
            
            # Extract RMSE
            rmse = librosa.feature.rms(y=y)
            
            # Extract spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Estimate key and mode
            key, mode = self._estimate_key(y, sr)
            
            return AudioFeatures(
                tempo=float(tempo),
                key=key,
                mode=mode,
                beats=beat_times,
                chroma=chroma,
                mfcc=mfcc,
                spectral_contrast=spectral_contrast,
                tonnetz=tonnetz,
                zcr=zcr[0],
                rmse=rmse[0],
                spectral_centroid=spectral_centroid,
                spectral_bandwidth=spectral_bandwidth,
                spectral_rolloff=spectral_rolloff,
                harmonic=y_harmonic,
                percussive=y_percussive,
                beat_frames=beat_frames,
                beat_times=beat_times,
                duration=duration,
                sample_rate=sr
            )
            
        except Exception as e:
            raise AudioProcessingError(f"Error extracting audio features: {str(e)}")
    
    def process_file(self, file_path: Union[str, Path]) -> AudioFeatures:
        """
        Process an audio file and extract features.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioFeatures object containing extracted features
        """
        y, sr = self.load_audio(file_path)
        return self.extract_features(y, sr)
    
    def _estimate_key(self, y: np.ndarray, sr: int) -> Tuple[str, str]:
        """
        Estimate the musical key and mode of the audio.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Tuple of (key, mode)
        """
        # Use chroma features to estimate key
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_avg = np.mean(chroma, axis=1)
        
        # Map chroma bins to note names
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_idx = np.argmax(chroma_avg)
        key = notes[key_idx]
        
        # Simple mode detection (major/minor)
        # This is a simplified approach - consider using a more sophisticated method
        mode = 'major' if chroma_avg[0] > chroma_avg[9] else 'minor'
        
        return key, mode


class AudioProcessingError(Exception):
    """Custom exception for audio processing errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            'error': self.message,
            'details': self.details
        }
    
    @classmethod
    def from_exception(cls, exc: Exception) -> 'AudioProcessingError':
        """Create from another exception."""
        return cls(str(exc), {'type': exc.__class__.__name__})


class UnsupportedFormatError(AudioProcessingError):
    """Raised when an unsupported audio format is encountered."""
    pass


def compute_audio_hash(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """
    Compute a hash of an audio file for change detection.
    
    Args:
        file_path: Path to audio file
        chunk_size: Size of chunks to read
        
    Returns:
        SHA-256 hash of the file
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()
