"""
Integration tests for batch audio processing functionality.
"""
import os
import pytest
import tempfile
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from samplemind.audio.processor import AudioProcessor, AudioFormat, BitDepth, ChannelMode

# Test directory
TEST_DIR = Path(__file__).parent.parent.parent / "test_audio_samples"
TEST_FILES = [
    TEST_DIR / "test_120bpm_c_major.wav",
    TEST_DIR / "test_140bpm_a_minor.wav"
]

# Skip tests if test audio files are not available
pytestmark = pytest.mark.skipif(
    not all(f.exists() for f in TEST_FILES),
    reason="Test audio files not found"
)

class TestBatchProcessing:
    """Test cases for batch audio processing."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def processor(self):
        """Create a new AudioProcessor instance for each test."""
        return AudioProcessor(sample_rate=44100, max_workers=2)
    
    def test_batch_conversion(self, processor, temp_dir):
        """Test batch conversion of multiple audio files."""
        # Prepare test files
        input_files = TEST_FILES
        output_dir = temp_dir / "converted"
        
        # Process batch
        results = processor.process_batch(
            input_paths=input_files,
            output_dir=output_dir,
            output_format=AudioFormat.MP3,
            sample_rate=44100,
            bit_depth=BitDepth.INT16,
            channels=ChannelMode.STEREO
        )
        
        # Verify results
        assert len(results) == len(input_files)
        for result in results:
            assert result['status'] == 'success'
            assert Path(result['output']).exists()
            assert Path(result['output']).stat().st_size > 0
    
    def test_batch_with_progress_callback(self, processor, temp_dir):
        """Test batch processing with progress callback."""
        progress_updates = []
        
        def progress_callback(progress):
            progress_updates.append({
                'processed': progress.processed,
                'total': progress.total,
                'progress': progress.progress
            })
        
        # Set up processor with progress callback
        processor.progress_callback = progress_callback
        
        # Process batch
        results = processor.process_batch(
            input_paths=TEST_FILES,
            output_dir=temp_dir / "with_progress",
            output_format=AudioFormat.WAV
        )
        
        # Verify progress updates
        assert len(progress_updates) > 0
        assert progress_updates[-1]['processed'] == len(TEST_FILES)
        assert progress_updates[-1]['total'] == len(TEST_FILES)
        assert abs(progress_updates[-1]['progress'] - 100.0) < 0.1
    
    def test_batch_with_invalid_files(self, processor, temp_dir):
        """Test batch processing with invalid input files."""
        # Prepare test files (one valid, one non-existent)
        input_files = [
            TEST_FILES[0],  # valid
            temp_dir / "nonexistent.wav"  # invalid
        ]
        
        # Process batch
        results = processor.process_batch(
            input_paths=input_files,
            output_dir=temp_dir / "with_errors"
        )
        
        # Verify results
        assert len(results) == 2
        assert results[0]['status'] == 'success'
        assert results[1]['status'] == 'error'
        assert "No such file or directory" in results[1]['error']
    
    def test_stop_processing(self, processor, temp_dir):
        """Test stopping batch processing."""
        # Create a large number of test files
        num_files = 10
        test_dir = temp_dir / "many_files"
        test_dir.mkdir()
        
        for i in range(num_files):
            # Create empty files with different extensions
            (test_dir / f"test_{i}.wav").touch()
        
        # Process in a separate thread to allow stopping
        def process():
            return processor.process_batch(
                input_paths=test_dir,
                output_dir=temp_dir / "stopped"
            )
        
        with ThreadPoolExecutor() as executor:
            future = executor.submit(process)
            
            # Let it start processing
            import time
            time.sleep(0.5)
            
            # Stop processing
            processor.stop_processing()
            
            # Get results
            results = future.result()
        
        # Verify some files were processed but not all
        processed = sum(1 for r in results if r['status'] in ('success', 'error'))
        assert 0 < processed < num_files
    
    def test_recursive_processing(self, processor, temp_dir):
        """Test recursive directory processing."""
        # Create a nested directory structure
        nested_dir = temp_dir / "nested" / "audio" / "files"
        nested_dir.mkdir(parents=True)
        
        # Create test files in nested directories
        for i, ext in enumerate(['wav', 'mp3']):
            (nested_dir / f"test_{i}.{ext}").touch()
        
        # Process recursively
        results = processor.process_batch(
            input_paths=temp_dir / "nested",
            output_dir=temp_dir / "recursive_out",
            recursive=True
        )
        
        # Verify all files were found and processed
        assert len(results) == 2  # Only .wav and .mp3 files should be processed
        assert all(r['status'] == 'success' for r in results)
