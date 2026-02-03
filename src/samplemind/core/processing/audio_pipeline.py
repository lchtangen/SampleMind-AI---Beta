"""
Audio Processing Pipeline for SampleMind AI

This module provides a comprehensive audio preprocessing pipeline that handles:
- Audio file loading and format conversion
- Sample rate conversion
- Channel management (stereo/mono)
- Normalization and gain control
- Noise reduction and filtering
- Audio segmentation and framing
"""

import os
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path
from typing import Union, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

from ..engine.audio_engine import AudioProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    """Supported audio formats for input/output"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AIFF = "aiff"
    OGG = "ogg"
    M4A = "m4a"

@dataclass
class AudioMetadata:
    """Metadata for audio files"""
    sample_rate: int
    channels: int
    duration: float
    format: str
    bit_depth: Optional[int] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None

class AudioPipeline:
    """
    Audio preprocessing pipeline for SampleMind AI.
    
    This class provides a chainable interface for applying various audio processing
    operations in a pipeline fashion.
    """
    
    def __init__(self, target_sr: int = 44100, mono: bool = True) -> None:
        """
        Initialize the audio pipeline.
        
        Args:
            target_sr: Target sample rate in Hz
            mono: Whether to convert to mono
        """
        self.target_sr = target_sr
        self.mono = mono
        self.y = None
        self.sr = None
        self.metadata = None
        self.history = []
    
    def load(self, input_path: Union[str, Path]) -> 'AudioPipeline':
        """
        Load an audio file from disk.
        
        Args:
            input_path: Path to the input audio file
            
        Returns:
            Self for method chaining
        """
        try:
            # Load audio file
            self.y, self.sr = librosa.load(
                str(input_path),
                sr=None,  # Keep original sample rate
                mono=False  # Load all channels
            )
            
            # Get file info
            with sf.SoundFile(str(input_path)) as f:
                self.metadata = AudioMetadata(
                    sample_rate=f.samplerate,
                    channels=f.channels,
                    duration=len(f) / f.samplerate,
                    format=f.format,
                    bit_depth=f.subtype
                )
            
            self.history.append(f"Loaded audio from {input_path}")
            return self
            
        except Exception as e:
            logger.error(f"Error loading audio file {input_path}: {str(e)}")
            raise
    
    def resample(self, target_sr: Optional[int] = None) -> 'AudioPipeline':
        """
        Resample audio to target sample rate.
        
        Args:
            target_sr: Target sample rate (uses instance target_sr if None)
            
        Returns:
            Self for method chaining
        """
        if self.y is None:
            raise ValueError("No audio loaded. Call load() first.")
            
        target_sr = target_sr or self.target_sr
        
        if self.sr != target_sr:
            # Resample each channel separately if multi-channel
            if len(self.y.shape) > 1:
                y_resampled = []
                for channel in self.y:
                    y_resampled.append(librosa.resample(channel, orig_sr=self.sr, target_sr=target_sr))
                self.y = np.array(y_resampled)
            else:
                self.y = librosa.resample(self.y, orig_sr=self.sr, target_sr=target_sr)
            
            self.history.append(f"Resampled from {self.sr}Hz to {target_sr}Hz")
            self.sr = target_sr
            
        return self
    
    def to_mono(self) -> 'AudioPipeline':
        """
        Convert audio to mono if it's not already.
        
        Returns:
            Self for method chaining
        """
        if self.y is None:
            raise ValueError("No audio loaded. Call load() first.")
            
        if len(self.y.shape) > 1 and self.y.shape[0] > 1 and self.mono:
            self.y = librosa.to_mono(self.y)
            self.history.append("Converted to mono")
            
        return self
    
    def normalize(self, target_db: float = -16.0, max_peak: float = 0.0) -> 'AudioPipeline':
        """
        Normalize audio to target LUFS level and apply peak limiting.
        
        Args:
            target_db: Target loudness in LUFS
            max_peak: Maximum peak level in dBFS (0.0 = no peak limiting)
            
        Returns:
            Self for method chaining
        """
        if self.y is None:
            raise ValueError("No audio loaded. Call load() first.")
            
        # Apply normalization
        self.y = AudioProcessor.normalize_audio(self.y, target_db)
        
        # Apply peak limiting if requested
        if max_peak < 0:
            max_amplitude = 10 ** (max_peak / 20.0)
            self.y = np.clip(self.y, -max_amplitude, max_amplitude)
            
        self.history.append(f"Normalized to {target_db} LUFS" + 
                          (f" with peak limiting at {max_peak}dBFS" if max_peak < 0 else ""))
        
        return self
    
    def filter(self, low_cut: float = 20.0, high_cut: float = 20000.0) -> 'AudioPipeline':
        """
        Apply high-pass and low-pass filtering.
        
        Args:
            low_cut: High-pass filter cutoff frequency in Hz
            high_cut: Low-pass filter cutoff frequency in Hz
            
        Returns:
            Self for method chaining
        """
        if self.y is None:
            raise ValueError("No audio loaded. Call load() first.")
            
        # Apply high-pass filter
        if low_cut > 0 and low_cut < self.sr / 2:
            self.y = AudioProcessor.apply_high_pass_filter(self.y, self.sr, low_cut)
            self.history.append(f"Applied high-pass filter at {low_cut}Hz")
            
        # Apply low-pass filter (placeholder - would use a proper low-pass filter)
        if high_cut < self.sr / 2 and high_cut > 0:
            nyquist = 0.5 * self.sr
            normalized_cutoff = high_cut / nyquist
            b, a = signal.butter(4, normalized_cutoff, btype='low')
            
            if len(self.y.shape) > 1:
                self.y = np.array([signal.filtfilt(b, a, channel) for channel in self.y])
            else:
                self.y = signal.filtfilt(b, a, self.y)
                
            self.history.append(f"Applied low-pass filter at {high_cut}Hz")
            
        return self
    
    def trim_silence(self, top_db: float = 30.0, frame_length: int = 2048, hop_length: int = 512) -> 'AudioPipeline':
        """
        Trim leading and trailing silence from audio.
        
        Args:
            top_db: The threshold (in decibels) below reference to consider as silence
            frame_length: The number of samples per analysis frame
            hop_length: The number of samples between analysis frames
            
        Returns:
            Self for method chaining
        """
        if self.y is None:
            raise ValueError("No audio loaded. Call load() first.")
            
        if len(self.y.shape) > 1:  # Multi-channel
            trimmed = []
            for channel in self.y:
                trimmed_channel, _ = librosa.effects.trim(
                    channel,
                    top_db=top_db,
                    frame_length=frame_length,
                    hop_length=hop_length
                )
                trimmed.append(trimmed_channel)
            self.y = np.array(trimmed)
        else:  # Mono
            self.y, _ = librosa.effects.trim(
                self.y,
                top_db=top_db,
                frame_length=frame_length,
                hop_length=hop_length
            )
            
        self.history.append(f"Trimmed silence (threshold: {top_db}dB)")
        return self
    
    def process(self, input_path: Union[str, Path], **kwargs) -> 'AudioPipeline':
        """
        Process audio with default pipeline steps.
        
        Args:
            input_path: Path to input audio file
            **kwargs: Override default processing parameters
            
        Returns:
            Self for method chaining
        """
        # Default processing steps
        steps = {
            'load': True,
            'resample': True,
            'to_mono': self.mono,
            'normalize': True,
            'filter': True,
            'trim_silence': True,
            'target_sr': self.target_sr,
            'normalize_db': -16.0,
            'max_peak': -1.0,
            'low_cut': 20.0,
            'high_cut': 20000.0,
            'trim_db': 30.0
        }
        
        # Update with any provided kwargs
        steps.update(kwargs)
        
        # Execute processing pipeline
        if steps['load']:
            self.load(input_path)
        
        if steps['resample'] and steps.get('target_sr') != self.sr:
            self.resample(steps.get('target_sr'))
            
        if steps['to_mono']:
            self.to_mono()
            
        if steps['normalize']:
            self.normalize(
                target_db=steps.get('normalize_db', -16.0),
                max_peak=steps.get('max_peak', -1.0)
            )
            
        if steps['filter']:
            self.filter(
                low_cut=steps.get('low_cut', 20.0),
                high_cut=steps.get('high_cut', 20000.0)
            )
            
        if steps['trim_silence']:
            self.trim_silence(top_db=steps.get('trim_db', 30.0))
            
        return self
    
    def save(self, output_path: Union[str, Path], format: Optional[AudioFormat] = None) -> None:
        """
        Save processed audio to disk.
        
        Args:
            output_path: Path to save the output file
            format: Output format (inferred from extension if None)
        """
        if self.y is None:
            raise ValueError("No audio to save. Process audio first.")
            
        output_path = Path(output_path)
        
        # Determine format from extension if not specified
        if format is None:
            ext = output_path.suffix[1:].lower()
            try:
                format = AudioFormat(ext)
            except ValueError:
                format = AudioFormat.WAV
                output_path = output_path.with_suffix(f".{AudioFormat.WAV.value}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        sf.write(
            str(output_path),
            self.y.T if len(self.y.shape) > 1 else self.y,
            self.sr,
            format=str(format.value).upper(),
            subtype='PCM_16'  # 16-bit depth
        )
        
        self.history.append(f"Saved audio to {output_path}")
    
    def get_processing_history(self) -> list:
        """
        Get the processing history for this pipeline.
        
        Returns:
            List of processing steps
        """
        return self.history.copy()
    
    def get_audio_data(self) -> Tuple[np.ndarray, int]:
        """
        Get the processed audio data and sample rate.
        
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        if self.y is None:
            raise ValueError("No audio data available. Process audio first.")
            
        return self.y, self.sr
