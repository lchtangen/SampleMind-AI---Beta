"""
BPM and Key Detection Module

Accurate tempo (BPM) and musical key detection using combination of 
librosa and madmom with confidence scoring and automatic file labeling.
"""

import asyncio
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import librosa
from loguru import logger

# Try to import madmom - it's optional
try:
    import madmom
    MADMOM_AVAILABLE = True
except ImportError:
    MADMOM_AVAILABLE = False
    logger.warning("madmom not available - BPM detection will use librosa only")


class BPMKeyDetector:
    """
    Advanced BPM and Key detection using multiple algorithms for accuracy.
    
    Features:
    - Multiple algorithm combination (librosa + madmom)
    - Confidence scoring
    - Automatic file labeling
    - Support for various audio formats
    """
    
    def __init__(self):
        """Initialize the BPM/Key detector."""
        if MADMOM_AVAILABLE:
            try:
                self.beat_tracker = madmom.features.beats.RNNBeatProcessor()
                self.tempo_estimator = madmom.features.tempo.TempoEstimationProcessor(fps=100)
                logger.info("BPMKeyDetector initialized with madmom support")
            except Exception as e:
                logger.warning(f"Failed to initialize madmom: {e}, falling back to librosa only")
                self.beat_tracker = None
                self.tempo_estimator = None
        else:
            self.beat_tracker = None
            self.tempo_estimator = None
            logger.info("BPMKeyDetector initialized (librosa only - madmom not available)")
    
    def detect_bpm(self, audio_path: Path) -> Dict[str, float]:
        """
        Detect BPM using multiple algorithms and average with confidence weighting.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with 'bpm' and 'confidence' keys
        """
        try:
            # Load audio with librosa
            y, sr = librosa.load(str(audio_path), sr=None)
            
            # Method 1: librosa beat tracking
            tempo_librosa, beats_librosa = librosa.beat.beat_track(y=y, sr=sr)
            
            # Method 2: madmom tempo estimation (if available)
            if MADMOM_AVAILABLE and self.tempo_estimator is not None:
                try:
                    act = madmom.features.beats.RNNBeatProcessor()(str(audio_path))
                    tempo_madmom_array = self.tempo_estimator(act)
                    # Get the tempo with highest confidence
                    if len(tempo_madmom_array) > 0:
                        tempo_madmom = float(tempo_madmom_array[0][0])
                    else:
                        tempo_madmom = float(tempo_librosa)
                except Exception as e:
                    logger.warning(f"Madmom tempo estimation failed: {e}, using librosa only")
                    tempo_madmom = float(tempo_librosa)
            else:
                # Madmom not available, use librosa result
                tempo_madmom = float(tempo_librosa)
            
            # Combine results with weighted average
            # If results are similar, use average; if different, prefer more reliable method
            if abs(tempo_librosa - tempo_madmom) < 5:
                # Close agreement - high confidence
                bpm = (float(tempo_librosa) + tempo_madmom) / 2
                confidence = 0.95
            elif abs(tempo_librosa - tempo_madmom) < 10:
                # Moderate agreement
                bpm = (float(tempo_librosa) + tempo_madmom) / 2
                confidence = 0.85
            else:
                # Large disagreement - lower confidence, prefer librosa
                bpm = float(tempo_librosa)
                confidence = 0.70
            
            # Round to 2 decimal places
            bpm = round(bpm, 2)
            
            logger.info(f"BPM detected: {bpm} (confidence: {confidence})")
            
            return {
                'bpm': bpm,
                'confidence': confidence,
                'librosa_bpm': float(tempo_librosa),
                'madmom_bpm': tempo_madmom
            }
            
        except Exception as e:
            logger.error(f"Error detecting BPM: {e}")
            raise
    
    def detect_key(self, audio_path: Path) -> str:
        """
        Detect musical key using chroma features and Krumhansl-Schmuckler algorithm.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Musical key as string (e.g., 'C major', 'A minor')
        """
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)
            
            # Extract chroma features using Constant-Q Transform
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # Average over time to get overall chromagram
            chroma_mean = np.mean(chroma, axis=1)
            
            # Estimate key using Krumhansl-Schmuckler algorithm
            key = self._estimate_key_ks(chroma_mean)
            
            logger.info(f"Key detected: {key}")
            
            return key
            
        except Exception as e:
            logger.error(f"Error detecting key: {e}")
            raise
    
    def _estimate_key_ks(self, chroma: np.ndarray) -> str:
        """
        Estimate musical key using Krumhansl-Schmuckler algorithm.
        
        Args:
            chroma: 12-element chroma vector
            
        Returns:
            Key as string
        """
        # Krumhansl-Schmuckler key profiles
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 
                                 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                                 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Normalize profiles
        major_profile = major_profile / np.linalg.norm(major_profile)
        minor_profile = minor_profile / np.linalg.norm(minor_profile)
        
        # Normalize chroma
        chroma = chroma / np.linalg.norm(chroma)
        
        # Calculate correlation for each key
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        best_score = -1
        best_key = 'C major'
        
        for i in range(12):
            # Rotate chroma to match key
            rotated_chroma = np.roll(chroma, -i)
            
            # Try major
            major_score = np.corrcoef(rotated_chroma, major_profile)[0, 1]
            if major_score > best_score:
                best_score = major_score
                best_key = f"{keys[i]} major"
            
            # Try minor
            minor_score = np.corrcoef(rotated_chroma, minor_profile)[0, 1]
            if minor_score > best_score:
                best_score = minor_score
                best_key = f"{keys[i]} minor"
        
        return best_key
    
    def label_file(self, audio_path: Path) -> str:
        """
        Generate labeled filename with BPM and key.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            New filename with BPM and key labels
        """
        try:
            bpm_data = self.detect_bpm(audio_path)
            key = self.detect_key(audio_path)
            
            # Get original filename without extension
            name = audio_path.stem
            extension = audio_path.suffix
            
            # Clean key for filename (remove spaces, make safe)
            key_safe = key.replace(' ', '_')
            
            # Create new filename
            bpm_rounded = int(round(bpm_data['bpm']))
            new_name = f"{name}_{bpm_rounded}BPM_{key_safe}{extension}"
            
            logger.info(f"Generated label: {new_name}")
            
            return new_name
            
        except Exception as e:
            logger.error(f"Error labeling file: {e}")
            raise
    
    async def analyze_async(self, audio_path: Path) -> Dict:
        """
        Async wrapper for BPM and key detection.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with bpm_data and key
        """
        loop = asyncio.get_event_loop()
        
        # Run in executor to avoid blocking
        bpm_data = await loop.run_in_executor(None, self.detect_bpm, audio_path)
        key = await loop.run_in_executor(None, self.detect_key, audio_path)
        
        return {
            'bpm_data': bpm_data,
            'key': key,
            'file': str(audio_path)
        }
    
    async def batch_analyze(self, audio_files: list[Path]) -> Dict[str, Dict]:
        """
        Batch analyze multiple audio files.
        
        Args:
            audio_files: List of paths to audio files
            
        Returns:
            Dictionary mapping filenames to analysis results
        """
        results = {}
        
        for audio_file in audio_files:
            try:
                result = await self.analyze_async(audio_file)
                results[str(audio_file)] = result
                logger.info(f"Analyzed: {audio_file.name}")
            except Exception as e:
                logger.error(f"Failed to analyze {audio_file}: {e}")
                results[str(audio_file)] = {'error': str(e)}
        
        return results


# Convenience functions for quick usage
def quick_bpm(audio_path: str) -> float:
    """Quick BPM detection."""
    detector = BPMKeyDetector()
    result = detector.detect_bpm(Path(audio_path))
    return result['bpm']


def quick_key(audio_path: str) -> str:
    """Quick key detection."""
    detector = BPMKeyDetector()
    return detector.detect_key(Path(audio_path))


def quick_label(audio_path: str) -> str:
    """Quick file labeling."""
    detector = BPMKeyDetector()
    return detector.label_file(Path(audio_path))
