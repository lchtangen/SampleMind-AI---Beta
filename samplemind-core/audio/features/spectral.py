""
Spectral feature extraction for audio analysis.
"""
import numpy as np
import librosa
from typing import Dict, Tuple, Optional


def extract_spectral_features(
    y: np.ndarray,
    sr: int,
    n_fft: int = 2048,
    hop_length: int = 512,
    n_mels: int = 128,
    fmin: float = 20.0,
    fmax: Optional[float] = None
) -> Dict[str, np.ndarray]:
    """
    Extract spectral features from audio signal.
    
    Args:
        y: Audio time series
        sr: Sample rate
        n_fft: FFT window size
        hop_length: Hop length for STFT
        n_mels: Number of Mel bands
        fmin: Minimum frequency for Mel bands
        fmax: Maximum frequency for Mel bands (defaults to sr/2)
        
    Returns:
        Dictionary of spectral features
    """
    if fmax is None:
        fmax = float(sr) / 2
    
    # Compute STFT
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    
    # Mel-scaled spectrogram
    mel_spec = librosa.feature.melspectrogram(
        y=y, 
        sr=sr, 
        n_fft=n_fft, 
        hop_length=hop_length,
        n_mels=n_mels,
        fmin=fmin,
        fmax=fmax
    )
    
    # Spectral features
    spectral_centroid = librosa.feature.spectral_centroid(
        S=S, sr=sr, n_fft=n_fft, hop_length=hop_length
    )
    
    spectral_bandwidth = librosa.feature.spectral_bandwidth(
        S=S, sr=sr, n_fft=n_fft, hop_length=hop_length
    )
    
    spectral_rolloff = librosa.feature.spectral_rolloff(
        S=S, sr=sr, n_fft=n_fft, hop_length=hop_length
    )
    
    spectral_contrast = librosa.feature.spectral_contrast(
        S=S, sr=sr, n_fft=n_fft, hop_length=hop_length
    )
    
    # Zero-crossing rate
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)
    
    # RMS energy
    rms = librosa.feature.rms(S=S, frame_length=n_fft, hop_length=hop_length)
    
    return {
        'mel_spectrogram': mel_spec,
        'spectral_centroid': spectral_centroid,
        'spectral_bandwidth': spectral_bandwidth,
        'spectral_rolloff': spectral_rolloff,
        'spectral_contrast': spectral_contrast,
        'zcr': zcr,
        'rms': rms
    }
