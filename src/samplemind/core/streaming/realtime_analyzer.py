"""
Real-time Audio Analyzer

Performs live audio analysis on streaming data with minimal latency.

Features:
- Real-time tempo detection
- Live pitch tracking
- Onset detection
- Energy analysis
- Spectral features
"""

import asyncio
import numpy as np
import librosa
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass
from loguru import logger


@dataclass
class RealtimeAnalysisResult:
    """Real-time analysis results"""
    timestamp: float
    tempo: Optional[float] = None
    pitch: Optional[float] = None
    energy: float = 0.0
    spectral_centroid: Optional[float] = None
    spectral_rolloff: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    rms: float = 0.0
    onset_detected: bool = False


class RealtimeAudioAnalyzer:
    """
    Analyze audio in real-time with low latency

    Processes audio chunks as they arrive and provides
    immediate analysis results.

    Example:
        >>> analyzer = RealtimeAudioAnalyzer(sample_rate=44100)
        >>> result = await analyzer.analyze_chunk(audio_chunk)
        >>> print(f"Tempo: {result.tempo}, Energy: {result.energy}")
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        hop_length: int = 512,
        enable_tempo: bool = True,
        enable_pitch: bool = True,
        enable_onset: bool = True
    ):
        """
        Initialize real-time analyzer

        Args:
            sample_rate: Audio sample rate
            hop_length: Hop length for analysis
            enable_tempo: Enable tempo detection
            enable_pitch: Enable pitch tracking
            enable_onset: Enable onset detection
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.enable_tempo = enable_tempo
        self.enable_pitch = enable_pitch
        self.enable_onset = enable_onset

        # Analysis state
        self.tempo_history: List[float] = []
        self.pitch_history: List[float] = []
        self.onset_strength_history: List[float] = []

        # History buffer for tempo tracking
        self.history_size = sample_rate * 2  # 2 seconds
        self.audio_history = np.array([], dtype=np.float32)

        # Callbacks
        self.callbacks: List[Callable] = []

        # Statistics
        self.total_chunks = 0
        self.analysis_times: List[float] = []

        logger.info(f"RealtimeAudioAnalyzer initialized (sr={sample_rate})")

    async def analyze_chunk(
        self,
        audio_chunk: np.ndarray,
        timestamp: float
    ) -> RealtimeAnalysisResult:
        """
        Analyze single audio chunk in real-time

        Args:
            audio_chunk: Audio data chunk
            timestamp: Chunk timestamp

        Returns:
            Analysis results
        """
        import time
        start_time = time.time()

        # Update history
        self.audio_history = np.concatenate([self.audio_history, audio_chunk])
        if len(self.audio_history) > self.history_size:
            self.audio_history = self.audio_history[-self.history_size:]

        result = RealtimeAnalysisResult(timestamp=timestamp)

        # Basic features (always computed)
        result.energy = float(np.mean(audio_chunk ** 2))
        result.rms = float(np.sqrt(result.energy))

        # Zero crossing rate
        zero_crossings = np.where(np.diff(np.sign(audio_chunk)))[0]
        result.zero_crossing_rate = len(zero_crossings) / len(audio_chunk)

        # Spectral features (if chunk is long enough)
        if len(audio_chunk) >= self.hop_length * 2:
            try:
                # Spectral centroid
                spectral_centroids = librosa.feature.spectral_centroid(
                    y=audio_chunk,
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )[0]
                result.spectral_centroid = float(np.mean(spectral_centroids))

                # Spectral rolloff
                spectral_rolloff = librosa.feature.spectral_rolloff(
                    y=audio_chunk,
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )[0]
                result.spectral_rolloff = float(np.mean(spectral_rolloff))

            except Exception as e:
                logger.debug(f"Spectral analysis error: {e}")

        # Pitch detection
        if self.enable_pitch and len(audio_chunk) >= self.hop_length:
            try:
                pitches, magnitudes = librosa.piptrack(
                    y=audio_chunk,
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )

                # Get most prominent pitch
                max_mag_idx = np.argmax(magnitudes, axis=0)
                pitch_values = [
                    pitches[max_mag_idx[i], i]
                    for i in range(pitches.shape[1])
                ]
                pitch_values = [p for p in pitch_values if p > 0]

                if pitch_values:
                    result.pitch = float(np.median(pitch_values))
                    self.pitch_history.append(result.pitch)
                    if len(self.pitch_history) > 100:
                        self.pitch_history.pop(0)

            except Exception as e:
                logger.debug(f"Pitch detection error: {e}")

        # Onset detection
        if self.enable_onset:
            try:
                onset_env = librosa.onset.onset_strength(
                    y=audio_chunk,
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )

                # Simple onset detection (threshold-based)
                mean_onset = np.mean(onset_env)
                std_onset = np.std(onset_env)
                threshold = mean_onset + 2 * std_onset

                if np.max(onset_env) > threshold:
                    result.onset_detected = True

                self.onset_strength_history.append(float(mean_onset))
                if len(self.onset_strength_history) > 100:
                    self.onset_strength_history.pop(0)

            except Exception as e:
                logger.debug(f"Onset detection error: {e}")

        # Tempo detection (requires sufficient history)
        if self.enable_tempo and len(self.audio_history) >= self.sample_rate:
            try:
                tempo, _ = librosa.beat.beat_track(
                    y=self.audio_history,
                    sr=self.sample_rate,
                    hop_length=self.hop_length
                )
                result.tempo = float(tempo.item() if hasattr(tempo, 'item') else tempo)

                self.tempo_history.append(result.tempo)
                if len(self.tempo_history) > 10:
                    self.tempo_history.pop(0)

            except Exception as e:
                logger.debug(f"Tempo detection error: {e}")

        # Update statistics
        self.total_chunks += 1
        analysis_time = time.time() - start_time
        self.analysis_times.append(analysis_time)
        if len(self.analysis_times) > 100:
            self.analysis_times.pop(0)

        # Invoke callbacks
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Callback error: {e}")

        return result

    def register_callback(self, callback: Callable):
        """Register callback for analysis results"""
        self.callbacks.append(callback)
        logger.info("Registered analysis callback")

    def get_stats(self) -> dict:
        """Get analyzer statistics"""
        return {
            "total_chunks": self.total_chunks,
            "avg_analysis_time": np.mean(self.analysis_times) if self.analysis_times else 0,
            "max_analysis_time": np.max(self.analysis_times) if self.analysis_times else 0,
            "current_tempo": self.tempo_history[-1] if self.tempo_history else None,
            "avg_tempo": np.mean(self.tempo_history) if self.tempo_history else None,
            "current_pitch": self.pitch_history[-1] if self.pitch_history else None,
            "avg_pitch": np.mean(self.pitch_history) if self.pitch_history else None,
            "history_size": len(self.audio_history),
        }

    def reset(self):
        """Reset analyzer state"""
        self.audio_history = np.array([], dtype=np.float32)
        self.tempo_history.clear()
        self.pitch_history.clear()
        self.onset_strength_history.clear()
        logger.info("Analyzer reset")
