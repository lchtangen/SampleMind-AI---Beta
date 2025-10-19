""
Integration tests for distributed audio processing.
"""
import os
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np
import pytest

from samplemind.core.engine.distributed_processor import DistributedAudioProcessor


@pytest.fixture(scope="module")
def test_audio_files():
    """Create temporary directory with test audio files."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="test_audio_")
    
    # Generate some test audio files
    sample_rate = 44100
    duration = 5.0  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Create different types of audio signals
    test_signals = {
        'sine_440.wav': np.sin(2 * np.pi * 440 * t),
        'noise.wav': np.random.normal(0, 0.1, len(t)),
        'silence.wav': np.zeros_like(t),
    }
    
    # Save test files
    import soundfile as sf
    
    for filename, signal in test_signals.items():
        filepath = Path(temp_dir) / filename
        sf.write(filepath, signal, sample_rate)
    
    yield temp_dir, list(test_signals.keys())
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_distributed_processor_init():
    """Test initialization of DistributedAudioProcessor."""
    with DistributedAudioProcessor(n_workers=2, memory_limit='1GB') as processor:
        assert processor.n_workers == 2
        assert processor.use_cache is True


def test_process_audio_files(test_audio_files):
    """Test processing of multiple audio files."""
    temp_dir, filenames = test_audio_files
    file_paths = [str(Path(temp_dir) / f) for f in filenames]
    
    with DistributedAudioProcessor(n_workers=2) as processor:
        results = processor.process_audio_files(
            file_paths=file_paths,
            feature_type='rhythm',
            level='basic'
        )
        
        # Check that all files were processed
        assert len(results) == len(file_paths)
        
        # Check that each result has the expected structure
        for file_path, features in results.items():
            assert isinstance(file_path, str)
            assert 'tempo' in features
            assert 'beat_times' in features
            assert 'onset_times' in features


def test_feature_extraction_levels(test_audio_files):
    """Test different feature extraction levels."""
    temp_dir, filenames = test_audio_files
    file_path = str(Path(temp_dir) / filenames[0])  # Just test with one file
    
    with DistributedAudioProcessor(n_workers=1) as processor:
        # Test basic level
        basic = processor.process_audio_files(
            file_paths=[file_path],
            feature_type='all',
            level='basic'
        )
        assert 'mfcc' not in basic[file_path]  # MFCCs not included in basic
        
        # Test standard level
        standard = processor.process_audio_files(
            file_paths=[file_path],
            feature_type='all',
            level='standard'
        )
        assert 'mfcc' in standard[file_path]  # MFCCs included in standard
        
        # Test advanced level
        advanced = processor.process_audio_files(
            file_paths=[file_path],
            feature_type='all',
            level='advanced'
        )
        assert 'chroma_cqt' in advanced[file_path]  # Chroma features in advanced


def test_error_handling():
    """Test error handling for invalid inputs."""
    with DistributedAudioProcessor(n_workers=1) as processor:
        # Test with non-existent file
        results = processor.process_audio_files(
            file_paths=['/path/to/nonexistent/file.wav'],
            feature_type='rhythm'
        )
        assert '_error' in results['/path/to/nonexistent/file.wav']
        
        # Test with invalid feature type
        with pytest.raises(ValueError):
            processor.process_audio_files(
                file_paths=['test.wav'],
                feature_type='invalid_feature'
            )


def test_parallel_performance(test_audio_files, benchmark):
    """Test performance with different numbers of workers."""
    temp_dir, filenames = test_audio_files
    file_paths = [str(Path(temp_dir) / f) for f in filenames * 5]  # Repeat to get more files
    
    def run_with_workers(n_workers):
        with DistributedAudioProcessor(n_workers=n_workers) as processor:
            return processor.process_audio_files(
                file_paths=file_paths,
                feature_type='rhythm',
                level='basic'
            )
    
    # Time with 1 worker (sequential)
    start = time.time()
    results_1 = run_with_workers(1)
    time_1 = time.time() - start
    
    # Time with multiple workers (parallel)
    start = time.time()
    results_2 = run_with_workers(2)
    time_2 = time.time() - start
    
    # Verify results are the same
    assert len(results_1) == len(results_2)
    
    # Verify parallel processing is faster (with some tolerance)
    # Note: This might not always be true due to system load, but should be in most cases
    assert time_2 < time_1 * 0.8  # At least 20% faster with 2 workers


def test_batch_processing(test_audio_files):
    """Test processing files in batches."""
    temp_dir, filenames = test_audio_files
    file_paths = [str(Path(temp_dir) / f) for f in filenames * 3]  # 9 files total
    
    with DistributedAudioProcessor(n_workers=2) as processor:
        # Process with batch size of 2
        results = processor.process_audio_files(
            file_paths=file_paths,
            feature_type='spectral',
            level='basic',
            batch_size=2
        )
        
        assert len(results) == len(file_paths)
        
        # Check that batch processing didn't affect results
        for file_path in file_paths:
            assert 'spectral_centroid' in results[file_path]
