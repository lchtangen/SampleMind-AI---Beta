"""
Multi-Stem Audio Separation

Uses Demucs for high-quality multi-stem separation into:
- Vocals, Bass, Drums, Other (4-stem)
- Vocals, Bass, Kick, Snare, Hi-hat, Guitar, Keys, Other (8-stem experimental)

Supports multiple models and quality presets.
"""

from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple
import numpy as np
from loguru import logger
from dataclasses import dataclass

# Optional imports for stem separation
try:
    import torch
    import torchaudio
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    from demucs.audio import AudioFile
    STEM_SEPARATION_AVAILABLE = True
except ImportError:
    STEM_SEPARATION_AVAILABLE = False
    logger.warning("Stem separation dependencies not available (torch, torchaudio, demucs)")


@dataclass
class StemResult:
    """Result of stem separation"""
    stem_name: str
    audio: np.ndarray
    sample_rate: int
    duration: float
    
    def save(self, output_path: Path) -> None:
        """Save stem to WAV file"""
        if not STEM_SEPARATION_AVAILABLE:
            raise ImportError("Stem separation dependencies not available")

        torchaudio.save(
            str(output_path),
            torch.from_numpy(self.audio),
            self.sample_rate
        )


class MultiStemSeparator:
    """
    Multi-stem audio separator using Demucs
    
    Features:
    - 4-stem separation (vocals, bass, drums, other)
    - 8-stem experimental (vocals, bass, kick, snare, hi-hat, guitar, keys, other)
    - Multiple model presets (fast, balanced, quality)
    - GPU acceleration support
    - Batch processing
    """
    
    # Demucs model presets
    MODELS = {
        'fast': 'htdemucs_ft',      # Fast, good quality
        'balanced': 'htdemucs',      # Balanced speed/quality
        'quality': 'htdemucs_6s',    # Best quality, slowest
        'experimental_8stem': 'htdemucs_8s'  # 8 stems (experimental)
    }
    
    # Standard 4-stem names
    STANDARD_STEMS = ['drums', 'bass', 'other', 'vocals']
    
    # 6-stem names (htdemucs_6s)
    SIX_STEMS = ['drums', 'bass', 'other', 'vocals', 'guitar', 'piano']
    
    # Experimental 8-stem (custom fine-tune needed)
    EIGHT_STEMS = ['kick', 'snare', 'hi_hat', 'bass', 'vocals', 'guitar', 'keys', 'other']
    
    def __init__(
        self,
        model_preset: Literal['fast', 'balanced', 'quality', 'experimental_8stem'] = 'balanced',
        device: Optional[str] = None
    ):
        """
        Initialize stem separator

        Args:
            model_preset: Model quality preset
            device: Compute device ('cpu', 'cuda', 'mps'). Auto-detect if None.
        """
        if not STEM_SEPARATION_AVAILABLE:
            raise ImportError(
                "Stem separation dependencies not available. "
                "Install with: pip install torch torchaudio demucs"
            )

        self.model_preset = model_preset

        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        
        self.device = device
        logger.info(f"MultiStemSeparator initialized with model '{model_preset}' on {device}")
        
        # Load model lazily
        self._model = None
    
    @property
    def model(self):
        """Lazy load Demucs model"""
        if self._model is None:
            model_name = self.MODELS[self.model_preset]
            logger.info(f"Loading Demucs model: {model_name}")
            self._model = get_model(model_name)
            self._model.to(self.device)
            self._model.eval()
            logger.info(f"Model loaded successfully")
        return self._model
    
    def separate(
        self,
        audio_path: Path,
        output_dir: Optional[Path] = None,
        save_stems: bool = True
    ) -> Dict[str, StemResult]:
        """
        Separate audio into stems
        
        Args:
            audio_path: Path to audio file
            output_dir: Directory to save stems (if save_stems=True)
            save_stems: Whether to save stems to disk
        
        Returns:
            Dictionary mapping stem names to StemResult objects
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Separating audio: {audio_path.name}")
        
        # Load audio
        wav = AudioFile(str(audio_path)).read(
            streams=0,
            samplerate=self.model.samplerate,
            channels=self.model.audio_channels
        )
        
        # Convert to torch tensor
        wav_tensor = torch.from_numpy(wav).to(self.device)
        
        # Add batch dimension
        if wav_tensor.dim() == 2:
            wav_tensor = wav_tensor.unsqueeze(0)
        
        # Apply model
        with torch.no_grad():
            sources = apply_model(
                self.model,
                wav_tensor,
                device=self.device,
                shifts=1,  # Number of random shifts for better quality
                split=True,  # Split audio in chunks to save memory
                overlap=0.25
            )
        
        # Get stem names
        stem_names = self._get_stem_names()
        
        # Create results
        results = {}
        
        for idx, stem_name in enumerate(stem_names):
            # Get stem audio (remove batch dimension, convert to numpy)
            stem_audio = sources[0, idx].cpu().numpy()
            
            # Get sample rate
            sample_rate = self.model.samplerate
            
            # Calculate duration
            duration = stem_audio.shape[1] / sample_rate
            
            # Create result
            result = StemResult(
                stem_name=stem_name,
                audio=stem_audio,
                sample_rate=sample_rate,
                duration=duration
            )
            
            results[stem_name] = result
            
            # Save if requested
            if save_stems and output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{audio_path.stem}_{stem_name}.wav"
                result.save(output_path)
                logger.info(f"Saved stem: {output_path.name}")
        
        logger.info(f"Separation complete: {len(results)} stems")
        return results
    
    def separate_batch(
        self,
        audio_paths: List[Path],
        output_dir: Path,
        save_stems: bool = True
    ) -> Dict[Path, Dict[str, StemResult]]:
        """
        Separate multiple audio files
        
        Args:
            audio_paths: List of audio file paths
            output_dir: Directory to save all stems
            save_stems: Whether to save stems to disk
        
        Returns:
            Dictionary mapping file paths to stem results
        """
        all_results = {}
        
        for audio_path in audio_paths:
            logger.info(f"Processing {audio_path.name} ({audio_paths.index(audio_path) + 1}/{len(audio_paths)})")
            
            # Create subdirectory for this file
            file_output_dir = output_dir / audio_path.stem if save_stems else None
            
            try:
                results = self.separate(
                    audio_path,
                    output_dir=file_output_dir,
                    save_stems=save_stems
                )
                all_results[audio_path] = results
            except Exception as e:
                logger.error(f"Error processing {audio_path.name}: {e}")
                continue
        
        logger.info(f"Batch separation complete: {len(all_results)}/{len(audio_paths)} files")
        return all_results
    
    def analyze_stem_quality(
        self,
        stem_result: StemResult
    ) -> Dict[str, float]:
        """
        Analyze stem separation quality
        
        Returns metrics:
        - rms_db: RMS level in dB
        - peak_db: Peak level in dB
        - dynamic_range: Dynamic range
        - silence_ratio: Ratio of silent samples
        """
        audio = stem_result.audio
        
        # RMS level
        rms = np.sqrt(np.mean(audio ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        
        # Peak level
        peak = np.max(np.abs(audio))
        peak_db = 20 * np.log10(peak + 1e-10)
        
        # Dynamic range
        dynamic_range = peak_db - rms_db
        
        # Silence detection (threshold at -60dB)
        silence_threshold = 10 ** (-60 / 20)
        silence_samples = np.sum(np.abs(audio) < silence_threshold)
        silence_ratio = silence_samples / audio.size
        
        return {
            'rms_db': float(rms_db),
            'peak_db': float(peak_db),
            'dynamic_range': float(dynamic_range),
            'silence_ratio': float(silence_ratio)
        }
    
    def mix_stems(
        self,
        stems: Dict[str, StemResult],
        output_path: Path,
        stem_volumes: Optional[Dict[str, float]] = None
    ) -> None:
        """
        Mix selected stems back together
        
        Args:
            stems: Dictionary of stem results
            output_path: Path to save mixed audio
            stem_volumes: Optional volume multipliers for each stem (0.0-1.0)
        """
        if not stems:
            raise ValueError("No stems provided for mixing")
        
        # Get reference stem for shape and sample rate
        ref_stem = next(iter(stems.values()))
        sample_rate = ref_stem.sample_rate
        
        # Initialize mix
        mix = np.zeros_like(ref_stem.audio)
        
        # Add each stem
        for stem_name, stem_result in stems.items():
            volume = stem_volumes.get(stem_name, 1.0) if stem_volumes else 1.0
            mix += stem_result.audio * volume
        
        # Normalize to prevent clipping
        peak = np.max(np.abs(mix))
        if peak > 0.95:
            mix = mix * (0.95 / peak)
            logger.warning(f"Mix normalized to prevent clipping (peak: {peak:.2f})")
        
        # Save
        torchaudio.save(
            str(output_path),
            torch.from_numpy(mix),
            sample_rate
        )
        logger.info(f"Mixed stems saved: {output_path}")
    
    def _get_stem_names(self) -> List[str]:
        """Get stem names for current model"""
        if self.model_preset == 'quality':
            return self.SIX_STEMS
        elif self.model_preset == 'experimental_8stem':
            return self.EIGHT_STEMS
        else:
            return self.STANDARD_STEMS


# Convenience functions

def quick_separate(
    audio_path: Path,
    model_preset: Literal['fast', 'balanced', 'quality'] = 'balanced',
    output_dir: Optional[Path] = None
) -> Dict[str, StemResult]:
    """Quick stem separation with default settings"""
    separator = MultiStemSeparator(model_preset=model_preset)
    return separator.separate(audio_path, output_dir=output_dir, save_stems=output_dir is not None)


def quick_separate_4stem(audio_path: Path, output_dir: Optional[Path] = None) -> Dict[str, StemResult]:
    """Quick 4-stem separation (vocals, bass, drums, other)"""
    return quick_separate(audio_path, model_preset='balanced', output_dir=output_dir)


def quick_separate_6stem(audio_path: Path, output_dir: Optional[Path] = None) -> Dict[str, StemResult]:
    """Quick 6-stem separation (adds guitar, piano)"""
    return quick_separate(audio_path, model_preset='quality', output_dir=output_dir)
