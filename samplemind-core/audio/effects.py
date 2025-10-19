"""
Advanced audio effects and processing for SampleMind AI.
Includes time-stretching, pitch-shifting, and various audio effects.
"""
import numpy as np
import librosa
import soundfile as sf
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, Union, List, Dict, Any

class EffectType(Enum):
    """Types of audio effects."""
    TIME_STRETCH = auto()
    PITCH_SHIFT = auto()
    REVERB = auto()
    DELAY = auto()
    CHORUS = auto()
    FLANGER = auto()
    PHASER = auto()
    COMPRESSOR = auto()
    NOISE_GATE = auto()
    EQUALIZER = auto()
    LIMITER = auto()
    EXCITER = auto()
    BIT_CRUSHER = auto()
    VINYL = auto()
    TAPE_SATURATION = auto()

@dataclass
class EffectParameters:
    """Parameters for audio effects."""
    effect_type: EffectType
    params: Dict[str, Any]
    enabled: bool = True

class AudioEffectsProcessor:
    """Advanced audio effects processing with optimized performance."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize the audio effects processor.
        
        Args:
            sample_rate: Sample rate in Hz (default: 44100)
        """
        self.sample_rate = sample_rate
        self.effects_chain: List[EffectParameters] = []
        self._reverb_buffers = {}
        self._last_reverb_t = 0
        
    def add_effect(self, effect_type: EffectType, params: Optional[Dict[str, Any]] = None) -> 'AudioEffectsProcessor':
        """
        Add an effect to the processing chain.
        
        Args:
            effect_type: Type of effect to add
            params: Effect parameters
            
        Returns:
            Self for method chaining
        """
        if params is None:
            params = {}
        self.effects_chain.append(EffectParameters(effect_type, params))
        return self
    
    def clear_effects(self) -> 'AudioEffectsProcessor':
        """Clear all effects from the processing chain."""
        self.effects_chain.clear()
        return self
    
    def process(self, y: np.ndarray, sr: Optional[int] = None) -> np.ndarray:
        """
        Process audio with the current effects chain.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            
        Returns:
            Processed audio signal
        """
        if sr is None:
            sr = self.sample_rate
            
        if len(y) == 0:
            return y
            
        processed = y.copy()
        
        # Process effects in the chain
        for effect in self.effects_chain:
            if not effect.enabled or len(processed) == 0:
                continue
                
            try:
                if effect.effect_type == EffectType.TIME_STRETCH:
                    rate = effect.params.get('rate', 1.0)
                    processed = self.time_stretch(processed, sr, rate)
                    
                elif effect.effect_type == EffectType.PITCH_SHIFT:
                    n_steps = effect.params.get('n_steps', 0)
                    bins_per_octave = effect.params.get('bins_per_octave', 12)
                    processed = self.pitch_shift(processed, sr, n_steps, bins_per_octave)
                    
                elif effect.effect_type == EffectType.REVERB:
                    room_size = effect.params.get('room_size', 0.5)
                    damping = effect.params.get('damping', 0.5)
                    wet_level = effect.params.get('wet_level', 0.33)
                    dry_level = effect.params.get('dry_level', 0.4)
                    width = effect.params.get('width', 1.0)
                    
                    processed = self.apply_reverb(
                        processed, sr, 
                        room_size=room_size,
                        damping=damping,
                        wet_level=wet_level,
                        dry_level=dry_level,
                        width=width
                    )
                    
                elif effect.effect_type == EffectType.DELAY:
                    delay_seconds = effect.params.get('delay_seconds', 0.5)
                    feedback = effect.params.get('feedback', 0.5)
                    mix = effect.params.get('mix', 0.3)
                    
                    processed = self.apply_delay(
                        processed, sr,
                        delay_seconds=delay_seconds,
                        feedback=feedback,
                        mix=mix
                    )
                    
                elif effect.effect_type == EffectType.COMPRESSOR:
                    threshold = effect.params.get('threshold', -20.0)
                    ratio = effect.params.get('ratio', 4.0)
                    attack = effect.params.get('attack', 0.01)
                    release = effect.params.get('release', 0.1)
                    
                    processed = self.apply_compression(
                        processed, sr,
                        threshold=threshold,
                        ratio=ratio,
                        attack=attack,
                        release=release
                    )
                    
            except Exception as e:
                import traceback
                print(f"Error applying effect {effect.effect_type}: {str(e)}\n{traceback.format_exc()}")
                continue
                
        return processed
    
    @staticmethod
    def time_stretch(y: np.ndarray, sr: int, rate: float) -> np.ndarray:
        """
        Time-stretch audio by a fixed rate with high quality.
        
        Args:
            y: Input audio signal
            sr: Sample rate
            rate: Stretch factor (e.g., 1.5 for 50% slower, 0.5 for 2x faster)
            
        Returns:
            Time-stretched audio
        """
        if rate == 1.0 or len(y) == 0:
            return y
            
        try:
            # Use phase vocoder for high-quality time stretching
            n_fft = 2048
            hop_length = n_fft // 4
            win_length = n_fft // 2
            
            # Handle multi-channel audio
            if y.ndim > 1:
                return np.column_stack([
                    AudioEffectsProcessor.time_stretch(channel, sr, rate)
                    for channel in y.T
                ])
            
            # Compute STFT
            D = librosa.stft(
                y.astype(np.float32), 
                n_fft=n_fft, 
                hop_length=hop_length, 
                win_length=win_length,
                window='hann'
            )
            
            # Time-stretch using phase vocoder
            D_stretch = librosa.phase_vocoder(
                D, 
                rate=rate, 
                hop_length=hop_length
            )
            
            # Reconstruct audio
            y_stretch = librosa.istft(
                D_stretch, 
                hop_length=hop_length, 
                win_length=win_length,
                window='hann',
                length=min(int(len(y) / rate), len(y) * 4)  # Prevent excessive length
            )
            
            return y_stretch.astype(y.dtype)
            
        except Exception as e:
            print(f"Error in time_stretch: {str(e)}")
            return y
    
    @staticmethod
    def pitch_shift(y: np.ndarray, sr: int, n_steps: float, bins_per_octave: int = 12) -> np.ndarray:
        """
        Pitch shift audio by a specified number of semitones with high quality.
        
        Args:
            y: Input audio signal
            sr: Sample rate
            n_steps: Number of semitones to shift (positive = higher pitch, negative = lower pitch)
            bins_per_octave: Number of steps per octave (default: 12 for equal temperament)
            
        Returns:
            Pitch-shifted audio
        """
        if n_steps == 0 or len(y) == 0:
            return y
            
        try:
            # Handle multi-channel audio
            if y.ndim > 1:
                return np.column_stack([
                    AudioEffectsProcessor.pitch_shift(channel, sr, n_steps, bins_per_octave)
                    for channel in y.T
                ])
            
            # Use phase-vocoder based pitch shifting with optimized parameters
            n_fft = 2048
            hop_length = n_fft // 4
            
            # Apply pitch shift
            y_shifted = librosa.effects.pitch_shift(
                y.astype(np.float32),
                sr=sr,
                n_steps=n_steps,
                bins_per_octave=bins_per_octave,
                n_fft=n_fft,
                hop_length=hop_length
            )
            
            # Ensure output length matches input length
            if len(y_shifted) > len(y):
                y_shifted = y_shifted[:len(y)]
            elif len(y_shifted) < len(y):
                y_shifted = np.pad(y_shifted, (0, len(y) - len(y_shifted)), 'constant')
                
            return y_shifted.astype(y.dtype)
            
        except Exception as e:
            print(f"Error in pitch_shift: {str(e)}")
            return y
    
    # Add more effect methods here...


    # ===================================
    # Advanced Audio Effects
    # ===================================
    
    def apply_reverb(self, y: np.ndarray, sr: int, room_size: float = 0.5, 
                    damping: float = 0.5, wet_level: float = 0.33, 
                    dry_level: float = 0.4, width: float = 1.0) -> np.ndarray:
        """
        Apply reverb effect to audio.
        
        Args:
            y: Input audio signal
            sr: Sample rate
            room_size: Room size (0-1)
            damping: High-frequency damping (0-1)
            wet_level: Wet signal level (0-1)
            dry_level: Dry signal level (0-1)
            width: Stereo width (0-1)
            
        Returns:
            Audio with reverb applied
        """
        try:
            # Simple reverb implementation using feedback delay network (FDN)
            # This is a simplified version - consider using a more advanced reverb algorithm
            
            # Normalize input
            if np.max(np.abs(y)) > 0:
                y = y / np.max(np.abs(y)) * 0.8  # Avoid clipping
            
            # Create impulse response for the reverb
            length = int(sr * (0.1 + room_size * 2.9))  # 0.1s to 3s reverb time
            impulse = np.zeros(length)
            impulse[0] = 1.0
            
            # Create decay envelope
            t = np.linspace(0, 1, len(impulse))
            decay = np.exp(-t * (1.0 - damping * 0.9) * 10.0)
            
            # Create random allpass filters for diffusion
            def allpass_filter(x, delay, gain):
                result = np.zeros_like(x)
                buffer = np.zeros(delay + 1)
                
                for i in range(len(x)):
                    buffer[0] = x[i] - gain * buffer[-1]
                    result[i] = gain * buffer[0] + buffer[-1]
                    buffer[1:] = buffer[:-1]
                    buffer[0] = 0
                    
                return result
            
            # Apply multiple allpass filters for diffusion
            for _ in range(4):
                delay = int(np.random.uniform(50, 200))
                gain = np.random.uniform(0.4, 0.7)
                impulse = allpass_filter(impulse, delay, gain)
            
            # Apply decay
            impulse *= decay
            
            # Convolve with input signal
            wet = np.convolve(y, impulse, mode='same')
            
            # Mix wet and dry signals
            result = wet * wet_level + y * dry_level
            
            # Normalize to prevent clipping
            if np.max(np.abs(result)) > 0:
                result = result / np.max(np.abs(result)) * 0.99
                
            return result.astype(y.dtype)
            
        except Exception as e:
            print(f"Error in apply_reverb: {str(e)}")
            return y
    
    def apply_delay(self, y: np.ndarray, sr: int, delay_seconds: float = 0.5, 
                   feedback: float = 0.5, mix: float = 0.3) -> np.ndarray:
        """
        Apply delay/echo effect to audio.
        
        Args:
            y: Input audio signal
            sr: Sample rate
            delay_seconds: Delay time in seconds
            feedback: Feedback amount (0-1)
            mix: Wet/dry mix (0-1)
            
        Returns:
            Audio with delay effect
        """
        try:
            if len(y) == 0:
                return y
                
            delay_samples = int(delay_seconds * sr)
            result = np.zeros_like(y)
            delay_line = np.zeros(delay_samples)
            
            for i in range(len(y)):
                # Read from delay line
                delayed = delay_line[0] if len(delay_line) > 0 else 0
                
                # Mix input with delayed signal
                result[i] = y[i] * (1 - mix) + delayed * mix
                
                # Update delay line with feedback
                if len(delay_line) > 0:
                    delay_line = np.roll(delay_line, -1)
                    delay_line[-1] = y[i] + delayed * feedback
            
            return result
            
        except Exception as e:
            print(f"Error in apply_delay: {str(e)}")
            return y
    
    def apply_compression(self, y: np.ndarray, sr: int, threshold: float = -20.0, 
                         ratio: float = 4.0, attack: float = 0.01, 
                         release: float = 0.1) -> np.ndarray:
        """
        Apply dynamic range compression to audio.
        
        Args:
            y: Input audio signal
            sr: Sample rate
            threshold: Threshold in dB (default: -20 dB)
            ratio: Compression ratio (e.g., 4:1)
            attack: Attack time in seconds
            release: Release time in seconds
            
        Returns:
            Compressed audio
        """
        try:
            if len(y) == 0:
                return y
                
            # Convert to dB
            threshold_linear = 10 ** (threshold / 20.0)
            
            # Initialize envelope and gain
            envelope = 0.0
            gain = 1.0
            
            # Calculate attack and release coefficients
            attack_coeff = np.exp(-1.0 / (attack * sr))
            release_coeff = np.exp(-1.0 / (release * sr))
            
            result = np.zeros_like(y)
            
            for i in range(len(y)):
                # Calculate envelope (peak detection)
                env_in = np.abs(y[i])
                
                if env_in > envelope:
                    envelope = attack_coeff * envelope + (1 - attack_coeff) * env_in
                else:
                    envelope = release_coeff * envelope + (1 - release_coeff) * env_in
                
                # Calculate gain reduction
                if envelope > threshold_linear:
                    # Convert to dB, apply ratio, and convert back to linear
                    env_db = 20 * np.log10(max(1e-6, envelope))
                    gain_db = (env_db - threshold) / ratio + threshold
                    gain = 10 ** ((gain_db - env_db) / 20.0)
                else:
                    gain = 1.0
                
                # Apply gain
                result[i] = y[i] * gain
                
            return result
            
        except Exception as e:
            print(f"Error in apply_compression: {str(e)}")
            return y


class NoiseReduction:
    """Advanced noise reduction and audio restoration with improved algorithms."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize the noise reduction processor.
        
        Args:
            sample_rate: Sample rate in Hz (default: 44100)
        """
        self.sample_rate = sample_rate
        self.noise_profile = None
        self.noise_floor = 1e-6  # Minimum noise floor to avoid division by zero
        self._noise_fft = None
        self._noise_phase = None
        self._noise_psd = None
        self._n_fft = 2048
        self._hop_length = self._n_fft // 4
        self._win_length = self._n_fft // 2
        self._window = 'hann'
        self._smoothing_beta = 0.98  # Smoothing factor for noise estimation
        
        # AI model placeholders (would be loaded from a trained model in production)
        self._denoiser_model = None
        self._is_ai_initialized = False
        
    def _init_ai_denoiser(self):
        """Initialize the AI denoiser model (placeholder implementation)."""
        if self._is_ai_initialized:
            return
            
        try:
            # In a real implementation, this would load a pre-trained model
            # For example: self._denoiser_model = load_denoiser_model()
            self._is_ai_initialized = True
            
        except Exception as e:
            print(f"Warning: Could not initialize AI denoiser: {str(e)}")
            self._is_ai_initialized = False
    
    def learn_noise_profile(self, y: np.ndarray, sr: Optional[int] = None) -> 'NoiseReduction':
        """
        Learn the noise profile from a noise-only segment using spectral analysis.
        
        Args:
            y: Noise-only audio segment
            sr: Sample rate (if None, use instance sample_rate)
            
        Returns:
            self for method chaining
        """
        if sr is None:
            sr = self.sample_rate
            
        if len(y) == 0:
            return self
            
        try:
            # Convert to mono if needed
            if y.ndim > 1:
                y = np.mean(y, axis=1) if y.shape[0] > 1 else np.mean(y, axis=0)
            
            # Compute STFT of noise
            D = librosa.stft(
                y.astype(np.float32),
                n_fft=self._n_fft,
                hop_length=self._hop_length,
                win_length=self._win_length,
                window=self._window
            )
            
            # Store magnitude and phase
            self._noise_fft = np.abs(D)
            self._noise_phase = np.angle(D)
            
            # Compute power spectral density (PSD) of noise
            self._noise_psd = (np.abs(D) ** 2) / (self._n_fft / 2)
            
            # Store basic statistics
            self.noise_profile = {
                'mean': np.mean(np.abs(y)),
                'std': np.std(y),
                'max_amp': np.max(np.abs(y)),
                'sample_rate': sr,
                'psd_mean': np.mean(self._noise_psd),
                'psd_std': np.std(self._noise_psd)
            }
            
            # Initialize AI denoiser if available
            self._init_ai_denoiser()
            
        except Exception as e:
            print(f"Error learning noise profile: {str(e)}")
            
        return self
    
    def reduce_noise(self, y: np.ndarray, sr: Optional[int] = None, 
                     reduction_db: float = 12.0, method: str = 'spectral',
                     use_ai: bool = False) -> np.ndarray:
        """
        Reduce noise in the audio signal using the specified method.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            reduction_db: Amount of noise reduction in dB (default: 12.0)
            method: Noise reduction method ('spectral', 'wiener', 'ai')
            use_ai: Whether to use AI-based denoising (if available)
            
        Returns:
            Denoised audio signal
        """
        if sr is None:
            sr = self.sample_rate
            
        if len(y) == 0:
            return y
            
        # Convert to mono if needed
        is_stereo = y.ndim > 1 and y.shape[0] > 1
        if is_stereo:
            y_mono = np.mean(y, axis=0)
        else:
            y_mono = y.copy()
            
        # Apply noise reduction
        try:
            if use_ai and self._is_ai_initialized:
                # Use AI-based denoising if available
                y_denoised = self._denoise_with_ai(y_mono, sr)
            else:
                # Use traditional methods
                if method == 'spectral':
                    y_denoised = self._reduce_noise_spectral(y_mono, sr, reduction_db)
                elif method == 'wiener':
                    y_denoised = self._reduce_noise_wiener(y_mono, sr, reduction_db)
                else:
                    raise ValueError(f"Unknown noise reduction method: {method}")
            
            # Process stereo channels separately if input was stereo
            if is_stereo:
                left = self._reduce_noise_spectral(y[0], sr, reduction_db)
                right = self._reduce_noise_spectral(y[1], sr, reduction_db)
                y_denoised = np.vstack((left, right))
                
            return y_denoised
            
        except Exception as e:
            print(f"Error in noise reduction: {str(e)}")
            return y
    
    def _reduce_noise_spectral(self, y: np.ndarray, sr: int, reduction_db: float) -> np.ndarray:
        """Spectral subtraction noise reduction."""
        if self._noise_psd is None:
            raise ValueError("No noise profile available. Call learn_noise_profile() first.")
            
        # Compute STFT of signal
        D = librosa.stft(
            y.astype(np.float32),
            n_fft=self._n_fft,
            hop_length=self._hop_length,
            win_length=self._win_length,
            window=self._window
        )
        
        # Get magnitude and phase
        mag = np.abs(D)
        phase = np.angle(D)
        
        # Estimate noise PSD if not already available
        if self._noise_psd is None:
            self._noise_psd = np.mean(np.abs(D) ** 2, axis=1, keepdims=True)
        
        # Compute signal PSD
        signal_psd = np.maximum(np.abs(D) ** 2 - self._noise_psd, 0)
        
        # Compute Wiener filter
        wiener = signal_psd / (signal_psd + self._noise_psd + 1e-10)
        
        # Apply gain based on reduction amount
        reduction_factor = 10 ** (-reduction_db / 20.0)
        gain = np.minimum(wiener * reduction_factor, 1.0)
        
        # Apply gain to magnitude
        mag_denoised = mag * gain
        
        # Reconstruct signal
        D_denoised = mag_denoised * np.exp(1j * phase)
        y_denoised = librosa.istft(
            D_denoised,
            hop_length=self._hop_length,
            win_length=self._win_length,
            window=self._window,
            length=len(y)
        )
        
        return y_denoised
    
    def _reduce_noise_wiener(self, y: np.ndarray, sr: int, reduction_db: float) -> np.ndarray:
        """Wiener filter noise reduction."""
        if self._noise_psd is None:
            raise ValueError("No noise profile available. Call learn_noise_profile() first.")
            
        # Compute STFT of signal
        D = librosa.stft(
            y.astype(np.float32),
            n_fft=self._n_fft,
            hop_length=self._hop_length,
            win_length=self._win_length,
            window=self._window
        )
        
        # Get magnitude and phase
        mag = np.abs(D)
        phase = np.angle(D)
        
        # Compute signal PSD
        signal_psd = np.maximum(np.abs(D) ** 2 - self._noise_psd, 0)
        
        # Wiener filter
        wiener = signal_psd / (signal_psd + self._noise_psd + 1e-10)
        
        # Apply gain based on reduction amount
        reduction_factor = 10 ** (-reduction_db / 20.0)
        gain = np.minimum(wiener * reduction_factor, 1.0)
        
        # Apply gain to magnitude
        mag_denoised = mag * gain
        
        # Reconstruct signal
        D_denoised = mag_denoised * np.exp(1j * phase)
        y_denoised = librosa.istft(
            D_denoised,
            hop_length=self._hop_length,
            win_length=self._win_length,
            window=self._window,
            length=len(y)
        )
        
        return y_denoised
    
    def _denoise_with_ai(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Apply AI-based denoising (placeholder implementation)."""
        # In a real implementation, this would use a pre-trained neural network
        # For now, we'll use spectral subtraction as a fallback
        print("AI denoising not fully implemented, using spectral subtraction")
        return self._reduce_noise_spectral(y, sr, reduction_db=12.0)
    
    def remove_clicks(self, y: np.ndarray, sr: Optional[int] = None, 
                      threshold: float = 0.1, method: str = 'median') -> np.ndarray:
        """
        Remove clicks, pops, and other transient artifacts from audio.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            threshold: Detection sensitivity (0-1)
            method: Interpolation method ('median', 'linear', 'spline')
            
        Returns:
            Audio with clicks removed
        """
        if sr is None:
            sr = self.sample_rate
            
        if len(y) < 5:  # Need at least 5 samples for processing
            return y
            
        try:
            # Convert to mono if needed
            is_stereo = y.ndim > 1 and y.shape[0] > 1
            if is_stereo:
                return np.column_stack([
                    self.remove_clicks(channel, sr, threshold, method)
                    for channel in y
                ])
            
            y_clean = y.copy().astype(np.float64)
            
            # 1. Detect transients using spectral flux
            D = librosa.stft(y, n_fft=512, hop_length=64, win_length=128)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            
            # Compute spectral flux (difference between consecutive frames)
            flux = np.sum(np.diff(S_db, axis=1) ** 2, axis=0)
            flux = np.pad(flux, (0, 1), 'edge')  # Pad to match input length
            
            # Find peaks in spectral flux
            peaks, _ = find_peaks(flux, height=np.percentile(flux, 95) * threshold)
            
            if len(peaks) == 0:
                return y_clean
                
            # Convert peaks to sample indices
            frame_indices = librosa.frames_to_samples(peaks, hop_length=64, n_fft=512)
            
            # 2. Remove clicks using the specified method
            if method == 'median':
                # Median filtering around detected clicks
                for idx in frame_indices:
                    start = max(0, idx - 2)
                    end = min(len(y_clean), idx + 3)
                    y_clean[idx] = np.median(y_clean[start:end])
                    
            elif method == 'linear':
                # Linear interpolation between surrounding samples
                for idx in frame_indices:
                    if 0 < idx < len(y_clean) - 1:
                        y_clean[idx] = (y_clean[idx-1] + y_clean[idx+1]) / 2
                        
            elif method == 'spline':
                # Spline interpolation for smoother results
                from scipy import interpolate
                
                # Create mask of good samples (not in click regions)
                mask = np.ones(len(y_clean), dtype=bool)
                for idx in frame_indices:
                    start = max(0, idx - 2)
                    end = min(len(y_clean), idx + 3)
                    mask[start:end] = False
                
                # Only keep non-click samples
                x = np.arange(len(y_clean))[mask]
                y_good = y_clean[mask]
                
                # Create spline interpolator
                if len(x) > 3:  # Need at least 4 points for cubic spline
                    spline = interpolate.CubicSpline(x, y_good)
                    y_clean = spline(np.arange(len(y_clean)))
            
            return y_clean.astype(y.dtype)
            
        except Exception as e:
            print(f"Error in remove_clicks: {str(e)}")
            return y
    
    def de_ess(self, y: np.ndarray, sr: Optional[int] = None, threshold: float = 0.2, ratio: float = 4.0) -> np.ndarray:
        """
        Reduce sibilance (ess sounds) in vocal recordings.
        
        Args:
            y: Input audio signal
            sr: Sample rate (if None, use instance sample_rate)
            threshold: Threshold for sibilance detection (0-1)
            ratio: Compression ratio for sibilant frequencies
            
        Returns:
            De-essed audio signal
        """
        if sr is None:
            sr = self.sample_rate
            
        # This is a simplified implementation
        # A real de-esser would use a more sophisticated approach
        D = librosa.stft(y)
        magnitude, phase = np.abs(D), np.angle(D)
        
        # Find sibilant frequencies (typically 4-10kHz)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        sibilant_band = (freqs >= 4000) & (freqs <= 10000)
        
        # Apply compression to sibilant frequencies
        sibilant_energy = np.mean(magnitude[sibilant_band, :], axis=0)
        gain = np.ones_like(sibilant_energy)
        mask = sibilant_energy > threshold
        gain[mask] = 1.0 / ratio
        
        # Apply gain to sibilant frequencies
        magnitude[sibilant_band, :] *= gain
        
        # Reconstruct audio
        return librosa.istft(magnitude * np.exp(1j * phase))
