""
Rhythm feature extraction for audio analysis.
"""
import numpy as np
import librosa
from typing import Dict, Tuple, Optional


def extract_rhythm_features(
    y: np.ndarray,
    sr: int,
    hop_length: int = 512,
    start_bpm: float = 120.0,
    std_bpm: float = 1.0,
    ac_size: float = 8.0,
    max_tempo: float = 320.0,
    **kwargs
) -> Dict[str, np.ndarray]:
    """
    Extract rhythm features from audio signal.
    
    Args:
        y: Audio time series
        sr: Sample rate
        hop_length: Hop length for onset detection
        start_bpm: Initial guess for BPM
        std_bpm: Standard deviation of BPM
        ac_size: Size of the autocorrelation window in seconds
        max_tempo: Maximum tempo to consider
        
    Returns:
        Dictionary of rhythm features
    """
    # Extract onset envelope
    onset_env = librosa.onset.onset_strength(
        y=y,
        sr=sr,
        hop_length=hop_length,
        aggregate=np.median
    )
    
    # Estimate tempo
    tempo, _ = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        start_bpm=start_bpm,
        std_bpm=std_bpm,
        ac_size=ac_size,
        max_tempo=max_tempo
    )
    
    # Get beat frames and times
    _, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        start_bpm=tempo
    )
    
    beat_times = librosa.frames_to_time(
        beat_frames,
        sr=sr,
        hop_length=hop_length
    )
    
    # Dynamic tempo estimation
    dtempo = librosa.beat.tempo(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=hop_length,
        aggregate=None
    )
    
    # Onset detection
    onset_frames = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        hop_length=hop_length,
        backtrack=False
    )
    
    onset_times = librosa.frames_to_time(
        onset_frames,
        sr=sr,
        hop_length=hop_length
    )
    
    # Beat-synchronous features
    y_percussive = librosa.effects.percussive(y)
    
    return {
        'tempo': tempo,
        'beat_frames': beat_frames,
        'beat_times': beat_times,
        'dynamic_tempo': dtempo,
        'onset_env': onset_env,
        'onset_frames': onset_frames,
        'onset_times': onset_times,
        'y_percussive': y_percussive
    }
