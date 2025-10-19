""
Timbre feature extraction for audio analysis.
"""
import numpy as np
import librosa
from typing import Dict, Tuple, Optional


def extract_timbre_features(
    y: np.ndarray,
    sr: int,
    n_fft: int = 2048,
    hop_length: int = 512,
    n_mfcc: int = 20,
    n_mels: int = 128,
    **kwargs
) -> Dict[str, np.ndarray]:
    """
    Extract timbre features from audio signal.
    
    Args:
        y: Audio time series
        sr: Sample rate
        n_fft: FFT window size
        hop_length: Hop length for STFT
        n_mfcc: Number of MFCC coefficients
        n_mels: Number of Mel bands
        
    Returns:
        Dictionary of timbre features
    """
    # Compute MFCCs
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels
    )
    
    # MFCC deltas (first and second order)
    mfcc_delta = librosa.feature.delta(mfcc)
    mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
    
    # Mel-scaled spectrogram
    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels
    )
    
    # Spectral contrast
    spectral_contrast = librosa.feature.spectral_contrast(
        y=y,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    # Spectral flatness
    spectral_flatness = librosa.feature.spectral_flatness(
        y=y,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    # Spectral rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(
        y=y,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    # Zero-crossing rate
    zcr = librosa.feature.zero_crossing_rate(
        y,
        frame_length=n_fft,
        hop_length=hop_length
    )
    
    # Root-mean-square (RMS) energy
    rms = librosa.feature.rms(
        y=y,
        frame_length=n_fft,
        hop_length=hop_length
    )
    
    # Spectral centroid and bandwidth
    spectral_centroid = librosa.feature.spectral_centroid(
        y=y,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    spectral_bandwidth = librosa.feature.spectral_bandwidth(
        y=y,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length
    )
    
    return {
        'mfcc': mfcc,
        'mfcc_delta': mfcc_delta,
        'mfcc_delta2': mfcc_delta2,
        'mel_spectrogram': S,
        'spectral_contrast': spectral_contrast,
        'spectral_flatness': spectral_flatness,
        'spectral_rolloff': spectral_rolloff,
        'zcr': zcr,
        'rms': rms,
        'spectral_centroid': spectral_centroid,
        'spectral_bandwidth': spectral_bandwidth
    }
