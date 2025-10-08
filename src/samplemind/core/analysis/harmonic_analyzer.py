"""
Harmonic Analysis

Advanced chord detection, key/scale analysis, and harmonic progression extraction
using Essentia's music theory algorithms.

Features:
- Real-time chord detection
- Chord progression extraction
- Key and scale detection
- Harmonic complexity analysis
- Chord quality classification (major, minor, diminished, augmented, etc.)
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from loguru import logger
from dataclasses import dataclass, field
import librosa

# Essentia for harmonic analysis
import essentia
import essentia.standard as es


@dataclass
class Chord:
    """A single chord with timing"""
    name: str
    start_time: float
    end_time: float
    confidence: float
    root: str
    quality: str  # major, minor, diminished, augmented, etc.
    
    def __repr__(self):
        return f"{self.name} [{self.start_time:.2f}s-{self.end_time:.2f}s]"
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclass
class ChordProgression:
    """A sequence of chords"""
    chords: List[Chord]
    key: str
    scale: str  # major, minor, etc.
    
    def __repr__(self):
        chord_names = ' -> '.join([c.name for c in self.chords[:5]])
        return f"Progression in {self.key} {self.scale}: {chord_names}..."
    
    @property
    def total_duration(self) -> float:
        if not self.chords:
            return 0.0
        return self.chords[-1].end_time - self.chords[0].start_time
    
    def get_chord_names(self) -> List[str]:
        """Get list of chord names"""
        return [c.name for c in self.chords]
    
    def get_unique_chords(self) -> List[str]:
        """Get unique chords in progression"""
        return list(dict.fromkeys(self.get_chord_names()))


@dataclass
class HarmonicAnalysis:
    """Complete harmonic analysis result"""
    audio_file: Path
    key: str
    scale: str
    key_confidence: float
    chords: List[Chord] = field(default_factory=list)
    progressions: List[ChordProgression] = field(default_factory=list)
    harmonic_complexity: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'audio_file': str(self.audio_file),
            'key': self.key,
            'scale': self.scale,
            'key_confidence': self.key_confidence,
            'num_chords': len(self.chords),
            'unique_chords': len(set(c.name for c in self.chords)),
            'harmonic_complexity': self.harmonic_complexity,
            'chords': [
                {
                    'name': c.name,
                    'start': c.start_time,
                    'end': c.end_time,
                    'confidence': c.confidence
                }
                for c in self.chords
            ]
        }


class HarmonicAnalyzer:
    """
    Advanced harmonic analysis using music theory
    
    Features:
    - Chord detection (major, minor, 7th, diminished, etc.)
    - Key and scale detection
    - Chord progression extraction
    - Harmonic complexity scoring
    - Roman numeral analysis
    """
    
    # Chord qualities
    CHORD_QUALITIES = {
        'M': 'major',
        'm': 'minor',
        '7': 'dominant 7th',
        'M7': 'major 7th',
        'm7': 'minor 7th',
        'dim': 'diminished',
        'aug': 'augmented',
        'sus2': 'suspended 2nd',
        'sus4': 'suspended 4th'
    }
    
    # Musical keys
    KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self, hop_size: int = 2048):
        """
        Initialize harmonic analyzer
        
        Args:
            hop_size: Frame hop size for chord detection
        """
        self.hop_size = hop_size
        logger.info("HarmonicAnalyzer initialized")
    
    def analyze(
        self,
        audio_path: Path,
        detect_progressions: bool = True
    ) -> HarmonicAnalysis:
        """
        Perform complete harmonic analysis
        
        Args:
            audio_path: Path to audio file
            detect_progressions: Whether to extract chord progressions
        
        Returns:
            HarmonicAnalysis object
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Analyzing harmonics: {audio_path.name}")
        
        try:
            # Load audio
            loader = es.MonoLoader(filename=str(audio_path))
            audio = loader()
            
            # Detect key and scale
            key, scale, key_confidence = self.detect_key(audio)
            
            # Detect chords
            chords = self.detect_chords(audio)
            
            # Create result
            result = HarmonicAnalysis(
                audio_file=audio_path,
                key=key,
                scale=scale,
                key_confidence=key_confidence,
                chords=chords
            )
            
            # Extract progressions
            if detect_progressions and chords:
                result.progressions = self.extract_progressions(chords, key, scale)
            
            # Calculate harmonic complexity
            result.harmonic_complexity = self.calculate_complexity(chords)
            
            logger.info(f"Analysis complete: {key} {scale}, {len(chords)} chords detected")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing harmonics: {e}")
            raise
    
    def detect_key(
        self,
        audio: np.ndarray
    ) -> Tuple[str, str, float]:
        """
        Detect musical key and scale
        
        Args:
            audio: Audio signal
        
        Returns:
            Tuple of (key, scale, confidence)
        """
        try:
            # Use Key extractor from Essentia
            key_extractor = es.KeyExtractor()
            key, scale, strength = key_extractor(audio)
            
            # Normalize key name
            key = key.replace('b', 'b')  # Flat symbol
            
            logger.info(f"Detected key: {key} {scale} (confidence: {strength:.2f})")
            return key, scale, strength
            
        except Exception as e:
            logger.warning(f"Key detection failed: {e}, using fallback")
            return self._fallback_key_detection(audio)
    
    def _fallback_key_detection(
        self,
        audio: np.ndarray
    ) -> Tuple[str, str, float]:
        """Fallback key detection using librosa"""
        try:
            # Use chromagram for key detection
            chroma = librosa.feature.chroma_cqt(y=audio, sr=44100)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Find dominant pitch class
            dominant_pitch = np.argmax(chroma_mean)
            key = self.KEYS[dominant_pitch]
            
            # Detect scale (major vs minor) based on chroma profile
            major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
            minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
            
            # Rotate profiles to match detected key
            major_profile = np.roll(major_profile, dominant_pitch)
            minor_profile = np.roll(minor_profile, dominant_pitch)
            
            # Calculate correlation
            major_corr = np.corrcoef(chroma_mean, major_profile)[0, 1]
            minor_corr = np.corrcoef(chroma_mean, minor_profile)[0, 1]
            
            if major_corr > minor_corr:
                scale = 'major'
                confidence = major_corr
            else:
                scale = 'minor'
                confidence = minor_corr
            
            return key, scale, float(confidence)
            
        except Exception as e:
            logger.error(f"Fallback key detection failed: {e}")
            return 'C', 'major', 0.5
    
    def detect_chords(
        self,
        audio: np.ndarray,
        sample_rate: int = 44100
    ) -> List[Chord]:
        """
        Detect chords in audio
        
        Args:
            audio: Audio signal
            sample_rate: Sample rate
        
        Returns:
            List of Chord objects
        """
        try:
            # Use ChordsDetection algorithm from Essentia
            chords_detection = es.ChordsDetection(
                hopSize=self.hop_size,
                windowSize=self.hop_size * 2
            )
            
            chords, strengths = chords_detection(audio)
            
            # Convert to Chord objects with timing
            chord_list = []
            hop_duration = self.hop_size / sample_rate
            
            # Group consecutive same chords
            current_chord = None
            start_time = 0.0
            
            for i, (chord_name, strength) in enumerate(zip(chords, strengths)):
                time = i * hop_duration
                
                if chord_name != current_chord:
                    # Save previous chord
                    if current_chord is not None:
                        chord_obj = self._create_chord_object(
                            current_chord,
                            start_time,
                            time,
                            strength
                        )
                        if chord_obj:
                            chord_list.append(chord_obj)
                    
                    # Start new chord
                    current_chord = chord_name
                    start_time = time
            
            # Add final chord
            if current_chord is not None:
                final_time = len(chords) * hop_duration
                chord_obj = self._create_chord_object(
                    current_chord,
                    start_time,
                    final_time,
                    strengths[-1] if len(strengths) > 0 else 1.0
                )
                if chord_obj:
                    chord_list.append(chord_obj)
            
            logger.info(f"Detected {len(chord_list)} chords")
            return chord_list
            
        except Exception as e:
            logger.warning(f"Chord detection failed: {e}, using fallback")
            return self._fallback_chord_detection(audio, sample_rate)
    
    def _create_chord_object(
        self,
        chord_name: str,
        start_time: float,
        end_time: float,
        confidence: float
    ) -> Optional[Chord]:
        """Create Chord object from name and timing"""
        # Skip silent/no-chord segments
        if chord_name in ['N', 'X', '']:
            return None
        
        # Parse chord name
        root, quality = self._parse_chord_name(chord_name)
        
        return Chord(
            name=chord_name,
            start_time=start_time,
            end_time=end_time,
            confidence=float(confidence),
            root=root,
            quality=quality
        )
    
    def _parse_chord_name(self, chord_name: str) -> Tuple[str, str]:
        """Parse chord name into root and quality"""
        # Simple parsing - can be enhanced
        if len(chord_name) == 0:
            return 'C', 'major'
        
        root = chord_name[0]
        if len(chord_name) > 1 and chord_name[1] in ['#', 'b']:
            root += chord_name[1]
            quality_str = chord_name[2:] if len(chord_name) > 2 else ''
        else:
            quality_str = chord_name[1:] if len(chord_name) > 1 else ''
        
        # Determine quality
        if quality_str in self.CHORD_QUALITIES:
            quality = self.CHORD_QUALITIES[quality_str]
        elif 'm' in quality_str.lower():
            quality = 'minor'
        else:
            quality = 'major'
        
        return root, quality
    
    def _fallback_chord_detection(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> List[Chord]:
        """Fallback chord detection using chromagram"""
        # Simplified chord detection based on chroma
        chroma = librosa.feature.chroma_cqt(y=audio, sr=sample_rate, hop_length=self.hop_size)
        
        # Detect chord changes
        chords = []
        hop_duration = self.hop_size / sample_rate
        
        for i in range(0, chroma.shape[1], 10):  # Process every 10 frames
            if i + 10 > chroma.shape[1]:
                break
            
            # Get average chroma for this segment
            segment_chroma = np.mean(chroma[:, i:i+10], axis=1)
            
            # Find dominant pitch classes
            top_pitches = np.argsort(segment_chroma)[-3:][::-1]
            
            # Simple chord naming (just use root for now)
            root = self.KEYS[top_pitches[0]]
            
            # Determine major/minor based on third
            third_interval = (top_pitches[1] - top_pitches[0]) % 12
            if third_interval == 3:
                quality = 'minor'
                chord_name = f"{root}m"
            else:
                quality = 'major'
                chord_name = root
            
            start_time = i * hop_duration
            end_time = (i + 10) * hop_duration
            
            chords.append(Chord(
                name=chord_name,
                start_time=start_time,
                end_time=end_time,
                confidence=0.7,
                root=root,
                quality=quality
            ))
        
        return chords
    
    def extract_progressions(
        self,
        chords: List[Chord],
        key: str,
        scale: str,
        min_length: int = 4
    ) -> List[ChordProgression]:
        """
        Extract chord progressions from chord sequence
        
        Args:
            chords: List of chords
            key: Musical key
            scale: Scale (major/minor)
            min_length: Minimum progression length
        
        Returns:
            List of ChordProgression objects
        """
        progressions = []
        
        # Simple approach: group every N chords as a progression
        for i in range(0, len(chords) - min_length + 1, min_length):
            progression_chords = chords[i:i+min_length]
            
            progression = ChordProgression(
                chords=progression_chords,
                key=key,
                scale=scale
            )
            progressions.append(progression)
        
        logger.info(f"Extracted {len(progressions)} chord progressions")
        return progressions
    
    def calculate_complexity(self, chords: List[Chord]) -> float:
        """
        Calculate harmonic complexity score (0-1)
        
        Based on:
        - Number of unique chords
        - Chord change frequency
        - Chord quality variety
        """
        if not chords:
            return 0.0
        
        # Unique chords
        unique_chords = len(set(c.name for c in chords))
        uniqueness_score = min(unique_chords / 12.0, 1.0)  # Normalize to 12 possible roots
        
        # Chord change frequency
        total_duration = chords[-1].end_time - chords[0].start_time
        changes_per_second = len(chords) / total_duration if total_duration > 0 else 0
        change_score = min(changes_per_second / 2.0, 1.0)  # Normalize to 2 changes/sec max
        
        # Quality variety
        unique_qualities = len(set(c.quality for c in chords))
        quality_score = min(unique_qualities / 5.0, 1.0)  # Normalize to 5 quality types
        
        # Weighted average
        complexity = (
            uniqueness_score * 0.4 +
            change_score * 0.3 +
            quality_score * 0.3
        )
        
        return float(complexity)


# Convenience functions

def quick_analyze_harmonics(audio_path: Path) -> HarmonicAnalysis:
    """Quick harmonic analysis"""
    analyzer = HarmonicAnalyzer()
    return analyzer.analyze(audio_path)


def quick_detect_key(audio_path: Path) -> Tuple[str, str]:
    """Quick key detection, returns (key, scale)"""
    analyzer = HarmonicAnalyzer()
    loader = es.MonoLoader(filename=str(audio_path))
    audio = loader()
    key, scale, _ = analyzer.detect_key(audio)
    return key, scale


def quick_detect_chords(audio_path: Path) -> List[str]:
    """Quick chord detection, returns list of chord names"""
    result = quick_analyze_harmonics(audio_path)
    return [c.name for c in result.chords]
