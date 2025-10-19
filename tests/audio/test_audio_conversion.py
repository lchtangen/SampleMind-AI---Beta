"""
Unit tests for audio format conversion functionality.
"""
import os
import io
import pytest
import numpy as np
from pathlib import Path
import soundfile as sf
from samplemind.audio.processor import (
    AudioProcessor, 
    AudioFormat, 
    BitDepth, 
    ChannelMode,
    UnsupportedFormatError,
    AudioProcessingError
)

# Test directory
TEST_DIR = Path(__file__).parent.parent.parent / "test_audio_samples"
TEST_FILES = {
    'wav': TEST_DIR / "test_120bpm_c_major.wav",
    'mp3': TEST_DIR / "test_120bpm_c_major.mp3",
    'flac': TEST_DIR / "test_120bpm_c_major.flac",
    'aiff': TEST_DIR / "test_120bpm_c_major.aiff"
}

# Skip tests if test audio files are not available
pytestmark = pytest.mark.skipif(
    not all(f.exists() for f in TEST_FILES.values()),
    reason="Test audio files not found"
)

class TestAudioConversion:
    """Test cases for audio format conversion."""
    
    @pytest.fixture
    def processor(self):
        """Create a new AudioProcessor instance for each test."""
        return AudioProcessor(sample_rate=44100)
    
    @pytest.fixture(params=TEST_FILES.items(), ids=lambda x: x[0])
    def audio_file(self, request):
        """Provide each test with a different audio file format."""
        return request.param
    
    def test_convert_between_formats(self, processor, audio_file, tmp_path):
        """Test conversion between all supported formats."
        src_format, src_path = audio_file
        
        # Test conversion to all other formats
        for tgt_format in AudioFormat:
            if tgt_format.value == src_format:
                continue  # Skip same format conversion
                
            output_path = tmp_path / f"output.{tgt_format.value}"
            
            # Perform conversion
            processor.convert_audio(
                src_path,
                output_path=output_path,
                output_format=tgt_format,
                sample_rate=44100,
                bit_depth=BitDepth.INT16
            )
            
            # Verify output file exists and is not empty
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            
            # Verify the format by attempting to load it
            y, sr = sf.read(output_path)
            assert len(y) > 0
            assert sr == 44100
    
    def test_convert_to_memory(self, processor, audio_file):
        """Test conversion to in-memory bytes."
        _, src_path = audio_file
        
        # Convert to WAV in memory
        audio_bytes = processor.convert_audio(
            src_path,
            output_format=AudioFormat.WAV,
            sample_rate=44100,
            bit_depth=BitDepth.INT16
        )
        
        # Verify we got bytes
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        
        # Verify the bytes can be loaded as audio
        with io.BytesIO(audio_bytes) as f:
            y, sr = sf.read(f)
            assert len(y) > 0
            assert sr == 44100
    
    def test_sample_rate_conversion(self, processor, audio_file, tmp_path):
        """Test sample rate conversion."
        _, src_path = audio_file
        target_rates = [22050, 44100, 48000]
        
        for rate in target_rates:
            output_path = tmp_path / f"output_{rate}.wav"
            
            processor.convert_audio(
                src_path,
                output_path=output_path,
                sample_rate=rate
            )
            
            # Verify sample rate
            y, sr = sf.read(output_path)
            assert sr == rate
    
    def test_bit_depth_conversion(self, processor, audio_file, tmp_path):
        """Test bit depth conversion."
        _, src_path = audio_file
        
        for depth in BitDepth:
            output_path = tmp_path / f"output_{depth}.wav"
            
            processor.convert_audio(
                src_path,
                output_path=output_path,
                bit_depth=depth
            )
            
            # Verify file can be loaded
            y, _ = sf.read(output_path)
            assert len(y) > 0
    
    def test_channel_conversion(self, processor, audio_file, tmp_path):
        """Test channel conversion."
        _, src_path = audio_file
        
        # Test mono conversion
        mono_path = tmp_path / "mono.wav"
        processor.convert_audio(
            src_path,
            output_path=mono_path,
            channels=ChannelMode.MONO
        )
        y_mono, _ = sf.read(mono_path)
        assert y_mono.ndim == 1  # Mono should be 1D
        
        # Test stereo conversion
        stereo_path = tmp_path / "stereo.wav"
        processor.convert_audio(
            src_path,
            output_path=stereo_path,
            channels=ChannelMode.STEREO
        )
        y_stereo, _ = sf.read(stereo_path)
        assert y_stereo.ndim == 2  # Stereo should be 2D
        assert y_stereo.shape[1] == 2  # 2 channels
    
    def test_unsupported_format(self, processor, tmp_path):
        """Test handling of unsupported formats."
        # Create a test file with unsupported extension
        bad_file = tmp_path / "test.unsupported"
        bad_file.write_text("not an audio file")
        
        with pytest.raises(UnsupportedFormatError):
            processor.convert_audio(bad_file, "output.wav")
    
    def test_invalid_bit_depth(self, processor, audio_file, tmp_path):
        """Test handling of invalid bit depths."
        _, src_path = audio_file
        output_path = tmp_path / "output.wav"
        
        # Test with unsupported bit depth
        with pytest.raises(ValueError):
            processor.convert_audio(
                src_path,
                output_path=output_path,
                bit_depth=8  # Unsupported bit depth
            )
    
    def test_file_not_found(self, processor):
        """Test handling of non-existent files."
        with pytest.raises(AudioProcessingError):
            processor.convert_audio("nonexistent.wav", "output.wav")
    
    def test_file_like_object(self, processor, audio_file, tmp_path):
        """Test conversion using file-like objects."
        _, src_path = audio_file
        output_path = tmp_path / "output.wav"
        
        # Test with file-like object as input
        with open(src_path, 'rb') as f_in:
            processor.convert_audio(
                f_in,
                output_path=output_path,
                output_format=AudioFormat.WAV
            )
        
        assert output_path.exists()
        y, _ = sf.read(output_path)
        assert len(y) > 0
        
        # Test with file-like object as output
        output_path = tmp_path / "output2.wav"
        with open(output_path, 'wb') as f_out:
            processor.convert_audio(
                src_path,
                output_path=f_out,
                output_format=AudioFormat.WAV
            )
        
        assert output_path.exists()
        y, _ = sf.read(output_path)
        assert len(y) > 0
