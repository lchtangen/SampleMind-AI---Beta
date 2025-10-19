#!/usr/bin/env python3
"""
Audio Feature Extraction Benchmark

This script benchmarks the performance of various audio feature extraction methods
in the SampleMind AI audio processing pipeline.
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from pathlib import Path

# Add parent directory to path to import samplemind
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.samplemind.core.engine.audio_engine import AdvancedFeatureExtractor

# Test configurations
SAMPLE_RATES = [22050, 44100, 48000]
DURATIONS = [1.0, 5.0, 10.0, 30.0]  # seconds
AUDIO_TYPES = ['sine', 'noise', 'impulse', 'silence']


def generate_test_audio(duration, sample_rate, audio_type='sine', frequency=440.0):
    """Generate test audio signals."""
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    
    if audio_type == 'sine':
        return 0.5 * np.sin(2 * np.pi * frequency * t)
    elif audio_type == 'noise':
        return np.random.uniform(-0.5, 0.5, size=len(t))
    elif audio_type == 'impulse':
        signal = np.zeros_like(t)
        signal[0] = 1.0
        return signal
    elif audio_type == 'silence':
        return np.zeros_like(t)
    else:
        raise ValueError(f"Unknown audio type: {audio_type}")


def run_benchmark():
    """Run the benchmark for different configurations."""
    results = []
    
    for sample_rate in tqdm(SAMPLE_RATES, desc="Sample Rates"):
        for duration in tqdm(DURATIONS, desc="Durations", leave=False):
            for audio_type in tqdm(AUDIO_TYPES, desc="Audio Types", leave=False):
                # Generate test audio
                y = generate_test_audio(duration, sample_rate, audio_type)
                
                # Initialize extractor
                extractor = AdvancedFeatureExtractor(sample_rate=sample_rate)
                
                # Benchmark tempo detection
                start = time.perf_counter()
                tempo_features = extractor.extract_rhythmic_features(y)
                tempo_time = time.perf_counter() - start
                
                # Benchmark spectral features
                start = time.perf_counter()
                spectral_features = extractor.extract_spectral_features(y)
                spectral_time = time.perf_counter() - start
                
                # Benchmark MFCC features
                start = time.perf_counter()
                mfcc_features = extractor.extract_mfcc_features(y)
                mfcc_time = time.perf_counter() - start
                
                # Benchmark harmonic/percussive separation
                start = time.perf_counter()
                try:
                    y_h, y_p = extractor.extract_harmonic_percussive(y)
                    hpss_time = time.perf_counter() - start
                    hpss_success = True
                except Exception as e:
                    hpss_time = float('nan')
                    hpss_success = False
                
                results.append({
                    'sample_rate': sample_rate,
                    'duration': duration,
                    'audio_type': audio_type,
                    'tempo_time': tempo_time,
                    'spectral_time': spectral_time,
                    'mfcc_time': mfcc_time,
                    'hpss_time': hpss_time,
                    'hpss_success': hpss_success,
                    'tempo': tempo_features.get('tempo', 0),
                    'num_samples': len(y)
                })
    
    return pd.DataFrame(results)


def analyze_results(df):
    """Analyze and visualize benchmark results."""
    # Basic statistics
    print("\n=== Benchmark Results ===")
    print(f"Total test cases: {len(df)}")
    print(f"Average processing times (ms):")
    print(df[['tempo_time', 'spectral_time', 'mfcc_time', 'hpss_time']].mean() * 1000)
    
    # Group by audio type
    print("\nAverage processing time by audio type (ms):")
    print(df.groupby('audio_type')[['tempo_time', 'spectral_time', 'mfcc_time', 'hpss_time']].mean() * 1000)
    
    # Group by sample rate
    print("\nAverage processing time by sample rate (ms):")
    print(df.groupby('sample_rate')[['tempo_time', 'spectral_time', 'mfcc_time', 'hpss_time']].mean() * 1000)
    
    # Group by duration
    print("\nAverage processing time by duration (ms):")
    print(df.groupby('duration')[['tempo_time', 'spectral_time', 'mfcc_time', 'hpss_time']].mean() * 1000)
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    # Plot processing time vs duration for different features
    plt.subplot(2, 2, 1)
    for feature in ['tempo_time', 'spectral_time', 'mfcc_time', 'hpss_time']:
        df_grouped = df.groupby('duration')[feature].mean()
        plt.plot(df_grouped.index, df_grouped * 1000, 'o-', label=feature.replace('_time', ''))
    plt.xlabel('Duration (s)')
    plt.ylabel('Processing Time (ms)')
    plt.title('Processing Time vs Duration')
    plt.legend()
    plt.grid(True)
    
    # Plot processing time vs sample rate
    plt.subplot(2, 2, 2)
    for feature in ['tempo_time', 'spectral_time', 'mfcc_time', 'hpss_time']:
        df_grouped = df.groupby('sample_rate')[feature].mean()
        plt.plot(df_grouped.index, df_grouped * 1000, 'o-', label=feature.replace('_time', ''))
    plt.xlabel('Sample Rate (Hz)')
    plt.ylabel('Processing Time (ms)')
    plt.title('Processing Time vs Sample Rate')
    plt.legend()
    plt.grid(True)
    
    # Plot success rate of HPSS by audio type
    plt.subplot(2, 2, 3)
    success_rates = df.groupby('audio_type')['hpss_success'].mean() * 100
    success_rates.plot(kind='bar')
    plt.title('HPSS Success Rate by Audio Type')
    plt.ylabel('Success Rate (%)')
    plt.ylim(0, 110)
    
    plt.tight_layout()
    plt.savefig('audio_benchmark_results.png')
    print("\nBenchmark results saved to 'audio_benchmark_results.png'")


if __name__ == '__main__':
    print("Running audio feature extraction benchmark...")
    results_df = run_benchmark()
    
    # Save results to CSV
    results_df.to_csv('audio_benchmark_results.csv', index=False)
    print("Raw results saved to 'audio_benchmark_results.csv'")
    
    # Analyze and visualize results
    analyze_results(results_df)
