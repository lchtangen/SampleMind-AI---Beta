#!/usr/bin/env python3
"""
Audio Effects and Noise Reduction Benchmark

This script benchmarks the performance of audio effects and noise reduction
processing in the SampleMind AI audio processing pipeline.
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import soundfile as sf
from pathlib import Path
from tqdm import tqdm
from scipy import signal

# Add project root to path to import samplemind
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import the samplemind modules
import sys
sys.path.append(str(project_root / 'samplemind-core'))
from audio.effects import AudioEffectsProcessor, NoiseReduction, EffectType
from audio.processor import AudioProcessor

# Test configurations
SAMPLE_RATES = [22050, 44100, 48000]
DURATIONS = [1.0, 5.0, 10.0]  # seconds
AUDIO_TYPES = ['sine', 'speech', 'music']
EFFECTS = ['pitch_shift', 'time_stretch', 'reverb', 'delay', 'compression']
NOISE_REDUCTION_METHODS = ['spectral', 'wiener']

def generate_test_audio(duration, sample_rate, audio_type='sine', frequency=440.0):
    """Generate test audio signals."""
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    
    if audio_type == 'sine':
        # Generate a clean sine wave
        return 0.5 * np.sin(2 * np.pi * frequency * t)
    elif audio_type == 'speech':
        # Generate speech-like signal (voiced + unvoiced)
        voiced = 0.7 * np.sin(2 * np.pi * 220 * t)
        unvoiced = 0.3 * np.random.uniform(-1, 1, size=len(t))
        # Apply envelope to simulate speech
        envelope = np.ones_like(t)
        for i in range(1, len(envelope)):
            if i % (sample_rate // 5) == 0:  # Every 0.2 seconds
                envelope[i] = 0.0
            else:
                envelope[i] = 0.9 * envelope[i-1] + 0.1 * (1 if np.random.random() > 0.5 else 0)
        return envelope * (voiced + unvoiced)
    elif audio_type == 'music':
        # Generate music-like signal (chord progression)
        notes = [440.0, 554.37, 659.25, 523.25]  # A, C#, E, C
        signal = np.zeros_like(t)
        segment_length = len(t) // len(notes)
        for i, note in enumerate(notes):
            start = i * segment_length
            end = start + segment_length if i < len(notes) - 1 else len(t)
            signal[start:end] = 0.3 * np.sin(2 * np.pi * note * t[start:end])
            # Add harmonics
            signal[start:end] += 0.1 * np.sin(2 * np.pi * note * 2 * t[start:end])
            signal[start:end] += 0.05 * np.sin(2 * np.pi * note * 3 * t[start:end])
        return signal
    else:
        raise ValueError(f"Unknown audio type: {audio_type}")

def add_noise(signal, snr_db=20):
    """Add white noise to signal with specified SNR in dB."""
    signal_power = np.mean(signal ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
    return signal + noise, noise

def benchmark_effects():
    """Benchmark audio effects processing."""
    results = []
    
    for sample_rate in tqdm(SAMPLE_RATES, desc="Sample Rates"):
        for duration in tqdm(DURATIONS, desc="Durations", leave=False):
            for audio_type in tqdm(AUDIO_TYPES, desc="Audio Types", leave=False):
                # Generate test audio
                y = generate_test_audio(duration, sample_rate, audio_type)
                
                # Initialize processor
                processor = AudioEffectsProcessor(sample_rate=sample_rate)
                
                # Test each effect
                for effect in EFFECTS:
                    try:
                        # Clear previous effects
                        processor.clear_effects()
                        
                        # Add current effect with default parameters
                        if effect == 'pitch_shift':
                            processor.add_effect(EffectType.PITCH_SHIFT, {'n_steps': 2.0})
                        elif effect == 'time_stretch':
                            processor.add_effect(EffectType.TIME_STRETCH, {'rate': 1.2})
                        elif effect == 'reverb':
                            processor.add_effect(EffectType.REVERB, {'room_size': 0.7, 'wet_level': 0.3})
                        elif effect == 'delay':
                            processor.add_effect(EffectType.DELAY, {'delay_seconds': 0.3, 'feedback': 0.5})
                        elif effect == 'compression':
                            processor.add_effect(EffectType.COMPRESSOR, {'threshold': -20.0, 'ratio': 4.0})
                        
                        # Benchmark processing
                        start_time = time.perf_counter()
                        y_processed = processor.process(y, sample_rate)
                        proc_time = time.perf_counter() - start_time
                        
                        results.append({
                            'sample_rate': sample_rate,
                            'duration': duration,
                            'audio_type': audio_type,
                            'effect': effect,
                            'processing_time': proc_time,
                            'num_samples': len(y),
                            'success': True
                        })
                        
                    except Exception as e:
                        print(f"Error processing {effect} on {audio_type} at {sample_rate}Hz: {str(e)}")
                        results.append({
                            'sample_rate': sample_rate,
                            'duration': duration,
                            'audio_type': audio_type,
                            'effect': effect,
                            'processing_time': float('nan'),
                            'num_samples': len(y),
                            'success': False,
                            'error': str(e)
                        })
    
    return pd.DataFrame(results)

def benchmark_noise_reduction():
    """Benchmark noise reduction processing."""
    results = []
    
    for sample_rate in tqdm(SAMPLE_RATES, desc="Sample Rates"):
        for duration in tqdm(DURATIONS, desc="Durations", leave=False):
            for audio_type in tqdm(AUDIO_TYPES, desc="Audio Types", leave=False):
                # Generate clean and noisy signals
                y_clean = generate_test_audio(duration, sample_rate, audio_type)
                y_noisy, noise = add_noise(y_clean, snr_db=10)
                
                # Initialize noise reducer
                nr = NoiseReduction(sample_rate=sample_rate)
                
                # Learn noise profile from noise-only segment
                nr.learn_noise_profile(noise[:sample_rate])  # Use first second as noise profile
                
                # Test each noise reduction method
                for method in NOISE_REDUCTION_METHODS:
                    try:
                        # Benchmark noise reduction
                        start_time = time.perf_counter()
                        y_denoised = nr.reduce_noise(
                            y_noisy,
                            method=method,
                            reduction_db=12.0
                        )
                        proc_time = time.perf_counter() - start_time
                        
                        # Calculate SNR improvement
                        def calculate_snr(signal, noise):
                            signal_power = np.mean(signal ** 2)
                            noise_power = np.mean(noise ** 2)
                            return 10 * np.log10(signal_power / noise_power)
                        
                        original_snr = calculate_snr(y_clean, y_noisy - y_clean)
                        processed_snr = calculate_snr(y_clean, y_denoised - y_clean)
                        snr_improvement = processed_snr - original_snr
                        
                        results.append({
                            'sample_rate': sample_rate,
                            'duration': duration,
                            'audio_type': audio_type,
                            'method': method,
                            'processing_time': proc_time,
                            'snr_improvement': snr_improvement,
                            'num_samples': len(y_noisy),
                            'success': True
                        })
                        
                    except Exception as e:
                        print(f"Error with {method} NR on {audio_type} at {sample_rate}Hz: {str(e)}")
                        results.append({
                            'sample_rate': sample_rate,
                            'duration': duration,
                            'audio_type': audio_type,
                            'method': method,
                            'processing_time': float('nan'),
                            'snr_improvement': float('nan'),
                            'num_samples': len(y_noisy),
                            'success': False,
                            'error': str(e)
                        })
    
    return pd.DataFrame(results)

def analyze_effects_results(df):
    """Analyze and visualize effects benchmark results."""
    print("\n=== Audio Effects Benchmark Results ===")
    print(f"Total test cases: {len(df)}")
    print(f"Success rate: {df['success'].mean() * 100:.1f}%")
    
    # Group by effect and calculate statistics
    effect_stats = df.groupby('effect')['processing_time'].agg(['mean', 'std', 'count'])
    effect_stats['samples_per_second'] = df.groupby('effect')['num_samples'].mean() / effect_stats['mean']
    print("\nPerformance by effect:")
    print(effect_stats)
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    # Processing time by effect
    plt.subplot(2, 2, 1)
    effect_stats['mean'].plot(kind='bar', yerr=effect_stats['std'])
    plt.title('Average Processing Time by Effect')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    
    # Throughput by effect
    plt.subplot(2, 2, 2)
    effect_stats['samples_per_second'].plot(kind='bar')
    plt.title('Processing Throughput by Effect')
    plt.ylabel('Samples per second')
    plt.xticks(rotation=45, ha='right')
    
    # Processing time by sample rate
    plt.subplot(2, 2, 3)
    df_grouped = df.groupby(['effect', 'sample_rate'])['processing_time'].mean().unstack()
    df_grouped.plot(kind='bar')
    plt.title('Processing Time by Sample Rate')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Sample Rate (Hz)')
    
    plt.tight_layout()
    plt.savefig('audio_effects_benchmark.png')
    print("\nBenchmark results saved to 'audio_effects_benchmark.png'")

def analyze_nr_results(df):
    """Analyze and visualize noise reduction benchmark results."""
    print("\n=== Noise Reduction Benchmark Results ===")
    print(f"Total test cases: {len(df)}")
    print(f"Success rate: {df['success'].mean() * 100:.1f}%")
    
    # Group by method and calculate statistics
    method_stats = df.groupby('method').agg({
        'processing_time': ['mean', 'std'],
        'snr_improvement': ['mean', 'std'],
        'num_samples': 'mean'
    })
    method_stats[('performance', 'samples_per_second')] = method_stats[('num_samples', 'mean')] / method_stats[('processing_time', 'mean')]
    
    print("\nPerformance by method:")
    print(method_stats)
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    # SNR improvement by method
    plt.subplot(2, 2, 1)
    method_stats[('snr_improvement', 'mean')].plot(kind='bar', yerr=method_stats[('snr_improvement', 'std')])
    plt.title('Average SNR Improvement by Method')
    plt.ylabel('SNR Improvement (dB)')
    
    # Processing time by method
    plt.subplot(2, 2, 2)
    method_stats[('processing_time', 'mean')].plot(kind='bar', yerr=method_stats[('processing_time', 'std')])
    plt.title('Average Processing Time by Method')
    plt.ylabel('Time (seconds)')
    
    # SNR improvement by audio type
    plt.subplot(2, 2, 3)
    snr_by_type = df.groupby(['method', 'audio_type'])['snr_improvement'].mean().unstack()
    snr_by_type.plot(kind='bar')
    plt.title('SNR Improvement by Audio Type')
    plt.ylabel('SNR Improvement (dB)')
    plt.legend(title='Audio Type')
    
    plt.tight_layout()
    plt.savefig('noise_reduction_benchmark.png')
    print("\nBenchmark results saved to 'noise_reduction_benchmark.png'")

if __name__ == '__main__':
    print("Running audio effects and noise reduction benchmarks...")
    
    # Run benchmarks
    print("\n=== Benchmarking Audio Effects ===")
    effects_df = benchmark_effects()
    effects_df.to_csv('audio_effects_benchmark.csv', index=False)
    print("Raw effects benchmark results saved to 'audio_effects_benchmark.csv'")
    analyze_effects_results(effects_df)
    
    print("\n=== Benchmarking Noise Reduction ===")
    nr_df = benchmark_noise_reduction()
    nr_df.to_csv('noise_reduction_benchmark.csv', index=False)
    print("Raw noise reduction results saved to 'noise_reduction_benchmark.csv'")
    analyze_nr_results(nr_df)
    
    print("\nBenchmarking complete!")
