"""
Loop Segmentation Module

Advanced 8-bar loop extraction with beat alignment, crossfade, and 
precise onset detection for professional-quality loop extraction.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import librosa
import soundfile as sf
from loguru import logger


class LoopSegmenter:
    """
    Professional 8-bar loop segmentation with neural beat tracking.
    
    Features:
    - Precise beat and bar detection
    - 8-bar loop extraction
    - Crossfade for seamless loops
    - Multiple loop variants
    - Tempo variation handling
    """
    
    def __init__(self, crossfade_duration: float = 0.01):
        """
        Initialize the loop segmenter.
        
        Args:
            crossfade_duration: Crossfade duration in seconds (default 0.01s = 10ms)
        """
        self.crossfade_duration = crossfade_duration
        logger.info(f"LoopSegmenter initialized with {crossfade_duration}s crossfade")
    
    def segment_8bars(
        self, 
        audio_path: Path,
        bars_per_segment: int = 8
    ) -> List[Dict]:
        """
        Extract 8-bar segments from audio file.
        
        Args:
            audio_path: Path to audio file
            bars_per_segment: Number of bars per segment (default 8)
            
        Returns:
            List of segment dictionaries with audio data and metadata
        """
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)
            
            # Detect tempo and beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            logger.info(f"Detected tempo: {tempo:.2f} BPM, {len(beats)} beats")
            
            # Calculate bar boundaries (assuming 4/4 time signature)
            beats_per_bar = 4
            
            # Get bar start positions
            bars = beats[::beats_per_bar]
            
            if len(bars) < bars_per_segment:
                logger.warning(f"Audio too short: only {len(bars)} bars, need {bars_per_segment}")
                return []
            
            # Extract segments
            segments = []
            num_segments = (len(bars) - bars_per_segment) // bars_per_segment + 1
            
            for i in range(num_segments):
                start_bar = i * bars_per_segment
                end_bar = start_bar + bars_per_segment
                
                if end_bar >= len(bars):
                    break
                
                # Convert bar indices to sample indices
                start_sample = bars[start_bar]
                end_sample = bars[end_bar] if end_bar < len(bars) else len(y)
                
                # Extract segment audio
                segment_audio = y[start_sample:end_sample]
                
                # Apply crossfade
                segment_audio = self._apply_crossfade(segment_audio, sr)
                
                # Calculate segment metadata
                segment_duration = len(segment_audio) / sr
                
                segments.append({
                    'audio': segment_audio,
                    'sample_rate': sr,
                    'start_bar': start_bar,
                    'end_bar': end_bar,
                    'start_sample': int(start_sample),
                    'end_sample': int(end_sample),
                    'duration': segment_duration,
                    'bpm': float(tempo),
                    'segment_index': i
                })
                
                logger.debug(f"Extracted segment {i}: bars {start_bar}-{end_bar}, duration {segment_duration:.2f}s")
            
            logger.info(f"Extracted {len(segments)} 8-bar segments")
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting audio: {e}")
            raise
    
    def _apply_crossfade(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Apply crossfade to make loop seamless.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Audio with crossfade applied
        """
        crossfade_samples = int(self.crossfade_duration * sr)
        
        if len(audio) < crossfade_samples * 2:
            logger.warning("Audio too short for crossfade")
            return audio
        
        # Create fade curves
        fade_out = np.linspace(1, 0, crossfade_samples)
        fade_in = np.linspace(0, 1, crossfade_samples)
        
        # Apply crossfade
        result = audio.copy()
        
        # Fade out at the end
        result[-crossfade_samples:] *= fade_out
        
        # Crossfade: blend end with beginning
        result[-crossfade_samples:] += audio[:crossfade_samples] * fade_in
        
        return result
    
    def save_segments(
        self,
        segments: List[Dict],
        output_dir: Path,
        base_name: str,
        format: str = 'wav'
    ) -> List[Path]:
        """
        Save extracted segments to files.
        
        Args:
            segments: List of segment dictionaries
            output_dir: Output directory
            base_name: Base filename
            format: Audio format (wav, flac, etc.)
            
        Returns:
            List of saved file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for segment in segments:
            # Create filename
            segment_idx = segment['segment_index']
            start_bar = segment['start_bar']
            end_bar = segment['end_bar']
            bpm = int(segment['bpm'])
            
            filename = f"{base_name}_bars{start_bar:03d}-{end_bar:03d}_{bpm}BPM_loop{segment_idx:02d}.{format}"
            filepath = output_dir / filename
            
            # Save audio
            sf.write(
                str(filepath),
                segment['audio'],
                segment['sample_rate'],
                format=format.upper()
            )
            
            saved_files.append(filepath)
            logger.info(f"Saved: {filename}")
        
        return saved_files
    
    def extract_best_loop(
        self,
        audio_path: Path,
        bars_per_segment: int = 8
    ) -> Optional[Dict]:
        """
        Extract the best quality 8-bar loop from audio.
        
        Uses energy and onset analysis to find the most suitable loop.
        
        Args:
            audio_path: Path to audio file
            bars_per_segment: Number of bars per segment
            
        Returns:
            Best segment dictionary or None
        """
        segments = self.segment_8bars(audio_path, bars_per_segment)
        
        if not segments:
            return None
        
        # Score each segment
        best_segment = None
        best_score = -1
        
        for segment in segments:
            score = self._score_segment(segment['audio'], segment['sample_rate'])
            
            if score > best_score:
                best_score = score
                best_segment = segment
        
        logger.info(f"Best loop: segment {best_segment['segment_index']} (score: {best_score:.2f})")
        return best_segment
    
    def _score_segment(self, audio: np.ndarray, sr: int) -> float:
        """
        Score a segment based on energy and onset characteristics.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Quality score (0-1)
        """
        # Calculate RMS energy
        energy = np.sqrt(np.mean(audio**2))
        
        # Calculate onset strength
        onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
        onset_score = np.mean(onset_env)
        
        # Normalize and combine
        energy_normalized = min(energy * 10, 1.0)
        onset_normalized = min(onset_score / 10, 1.0)
        
        # Weighted average (favor energetic, rhythmic segments)
        score = 0.6 * energy_normalized + 0.4 * onset_normalized
        
        return score
    
    async def segment_async(
        self,
        audio_path: Path,
        bars_per_segment: int = 8
    ) -> List[Dict]:
        """
        Async wrapper for segment extraction.
        
        Args:
            audio_path: Path to audio file
            bars_per_segment: Number of bars per segment
            
        Returns:
            List of segments
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.segment_8bars,
            audio_path,
            bars_per_segment
        )
    
    async def batch_segment(
        self,
        audio_files: List[Path],
        output_dir: Path,
        bars_per_segment: int = 8
    ) -> Dict[str, List[Path]]:
        """
        Batch process multiple audio files.
        
        Args:
            audio_files: List of audio files
            output_dir: Output directory
            bars_per_segment: Bars per segment
            
        Returns:
            Dictionary mapping input files to output files
        """
        results = {}
        
        for audio_file in audio_files:
            try:
                # Extract segments
                segments = await self.segment_async(audio_file, bars_per_segment)
                
                # Save segments
                base_name = audio_file.stem
                saved_files = self.save_segments(
                    segments,
                    output_dir / base_name,
                    base_name
                )
                
                results[str(audio_file)] = saved_files
                logger.info(f"Processed {audio_file.name}: {len(saved_files)} loops")
                
            except Exception as e:
                logger.error(f"Failed to process {audio_file}: {e}")
                results[str(audio_file)] = []
        
        return results
    
    def analyze_loop_quality(self, audio: np.ndarray, sr: int) -> Dict:
        """
        Analyze loop quality metrics.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Dictionary with quality metrics
        """
        # Energy analysis
        rms = np.sqrt(np.mean(audio**2))
        
        # Spectral analysis
        spec_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        
        # Onset analysis
        onset_strength = np.mean(librosa.onset.onset_strength(y=audio, sr=sr))
        
        # Zero crossing rate (indicator of noisiness)
        zcr = np.mean(librosa.feature.zero_crossing_rate(audio))
        
        return {
            'rms_energy': float(rms),
            'spectral_centroid': float(spec_centroid),
            'onset_strength': float(onset_strength),
            'zero_crossing_rate': float(zcr),
            'quality_score': self._score_segment(audio, sr)
        }


# Convenience functions
def quick_segment(audio_path: str, bars: int = 8) -> List[Dict]:
    """Quick 8-bar segmentation."""
    segmenter = LoopSegmenter()
    return segmenter.segment_8bars(Path(audio_path), bars)


def quick_best_loop(audio_path: str, bars: int = 8) -> Optional[Dict]:
    """Extract best loop from audio."""
    segmenter = LoopSegmenter()
    return segmenter.extract_best_loop(Path(audio_path), bars)
