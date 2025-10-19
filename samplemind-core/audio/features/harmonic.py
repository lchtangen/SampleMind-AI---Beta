""
Harmonic feature extraction for audio analysis.
"""
import numpy as np
import librosa
from typing import Dict, Tuple, Optional


def extract_harmonic_features(
    y: np.ndarray,
    sr: int,
    n_fft: int = 2048,
    hop_length: int = 512,
    n_chroma: int = 12,
    n_octaves: int = 7,
    **kwargs
) -> Dict[str, np.ndarray]:
    """
    Extract harmonic features from audio signal.
    
    Args:
        y: Audio time series
        sr: Sample rate
        n_fft: FFT window size
        hop_length: Hop length for STFT
        n_chroma: Number of chroma bins
        n_octaves: Number of octaves for CQT
        
    Returns:
        Dictionary of harmonic features
    """
    # Separate harmonic and percussive components
    y_harmonic, _ = librosa.effects.hpss(y)
    
    # Chroma features
    chroma_cqt = librosa.feature.chroma_cqt(
        y=y_harmonic,
        sr=sr,
        n_chroma=n_chroma,
        n_octaves=n_octaves,
        hop_length=hop_length
    )
    
    # Chroma energy normalized statistics (CENS)
    chroma_cens = librosa.feature.chroma_cens(
        y=y_harmonic,
        sr=sr,
        n_chroma=n_chroma,
        n_octaves=n_octaves,
        hop_length=hop_length
    )
    
    # Harmonic network features
    tonnetz = librosa.feature.tonnetz(
        y=y_harmonic,
        sr=sr,
        chroma=chroma_cqt
    )
    
    # Tuning estimation
    tuning = librosa.estimate_tuning(y=y_harmonic, sr=sr)
    
    # Key and mode estimation (simplified)
    chroma_mean = np.mean(chroma_cqt, axis=1)
    key_idx = np.argmax(chroma_mean)
    mode = 'major' if chroma_mean[0] > chroma_mean[9] else 'minor'
    
    # Map to note names
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = notes[key_idx]
    
    return {
        'chroma_cqt': chroma_cqt,
        'chroma_cens': chroma_cens,
        'tonnetz': tonnetz,
        'tuning': tuning,
        'key': key,
        'mode': mode,
        'chroma_mean': chroma_mean
    }
