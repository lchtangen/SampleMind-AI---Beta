# Audio Processing Guide

## Table of Contents
- [Overview](#overview)
- [Supported Formats](#supported-formats)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Performance Tips](#performance-tips)
- [API Reference](#api-reference)

## Overview

The `AudioProcessor` class provides comprehensive audio processing capabilities including format conversion, feature extraction, and audio manipulation. This guide covers the audio format conversion features.

## Supported Formats

### Input Formats
- WAV, MP3, FLAC, AIFF, OGG
- File paths or file-like objects
- In-memory audio data

### Output Formats
- WAV, MP3, FLAC, AIFF
- In-memory bytes or file output
- Various bit depths (16-bit, 24-bit, 32-bit float)

## Basic Usage

### Initialization

```python
from samplemind.audio.processor import AudioProcessor, AudioFormat, BitDepth, ChannelMode

# Create an audio processor with default settings (44.1kHz, 2048 FFT, 512 hop)
processor = AudioProcessor()
```

### Basic Conversion

```python
# Convert between formats
processor.convert_audio(
    "input.wav",
    "output.mp3"
)

# Convert with specific parameters
processor.convert_audio(
    "input.flac",
    "output.aiff",
    sample_rate=48000,
    bit_depth=BitDepth.INT24,
    channels=ChannelMode.STEREO
)
```

### In-Memory Conversion

```python
# Convert to in-memory bytes
audio_bytes = processor.convert_audio(
    "input.wav",
    output_format=AudioFormat.MP3,
    bit_depth=BitDepth.INT16
)

# Convert from bytes to file
processor.convert_audio(
    io.BytesIO(audio_bytes),
    "output.wav"
)
```

## Advanced Features

### Batch Processing

```python
from pathlib import Path

input_dir = Path("input_samples")
output_dir = Path("converted_samples")
output_dir.mkdir(exist_ok=True)

for input_file in input_dir.glob("*.wav"):
    output_file = output_dir / f"{input_file.stem}.flac"
    processor.convert_audio(
        input_file,
        output_file,
        output_format=AudioFormat.FLAC,
        bit_depth=BitDepth.INT24
    )
```

### Custom Encoding Parameters

```python
# Custom MP3 bitrate and quality
processor.convert_audio(
    "input.wav",
    "output.mp3",
    bit_rate="320k",
    quality=0  # 0 (best) to 9 (worst)
)

# FLAC compression level
processor.convert_audio(
    "input.wav",
    "output.flac",
    compression_level=8  # 0 (fastest) to 8 (best compression)
)
```

## Error Handling

Handle common exceptions:

```python
from samplemind.audio.processor import UnsupportedFormatError, AudioProcessingError

try:
    processor.convert_audio("input.unsupported", "output.wav")
except UnsupportedFormatError as e:
    print(f"Unsupported format: {e}")
except AudioProcessingError as e:
    print(f"Processing error: {e}")
```

## Performance Tips

1. **Batch Processing**: Process multiple files in parallel
2. **Memory Usage**: Use file paths instead of in-memory for large files
3. **Sample Rate**: Lower sample rates (e.g., 44.1kHz) are faster than higher ones (e.g., 96kHz)
4. **Bit Depth**: 16-bit is faster than 24-bit or 32-bit float

## API Reference

### AudioProcessor

#### `convert_audio`
```python
def convert_audio(
    self,
    input_path: Union[str, Path, BinaryIO],
    output_path: Optional[Union[str, Path, BinaryIO]] = None,
    output_format: Optional[Union[str, AudioFormat]] = None,
    sample_rate: Optional[int] = None,
    bit_depth: Optional[Union[int, BitDepth]] = None,
    channels: Optional[Union[int, ChannelMode]] = None,
    **kwargs
) -> Union[bytes, None]:
    """Convert audio file to different format and/or parameters.
    
    Args:
        input_path: Input audio file path or file-like object
        output_path: Output file path (None to return bytes)
        output_format: Target format (wav, mp3, flac, aiff)
        sample_rate: Target sample rate in Hz
        bit_depth: Target bit depth (16, 24, or 32)
        channels: Target number of channels or 'mono'/'stereo'
        **kwargs: Additional arguments for soundfile.write()
        
    Returns:
        bytes if output_path is None, else None
        
    Raises:
        UnsupportedFormatError: If format is not supported
        AudioProcessingError: If conversion fails
    """
```

### Enums

#### `AudioFormat`
- `WAV`: WAV format
- `MP3`: MP3 format
- `FLAC`: FLAC format
- `AIFF`: AIFF format
- `OGG`: OGG/Vorbis format

#### `BitDepth`
- `INT16`: 16-bit PCM
- `INT24`: 24-bit PCM
- `FLOAT32`: 32-bit float

#### `ChannelMode`
- `MONO`: Single channel audio
- `STEREO`: Two channel (stereo) audio
