"""
SampleMind AI — Audio Format Detector

Detects audio file formats via:
  1. File extension
  2. MIME type
  3. Magic bytes (file signature)
"""

import mimetypes
from pathlib import Path
from typing import Any, Dict, Optional

from .models import AudioFormat


class AudioFormatDetector:
    """Intelligent audio format detection"""

    @staticmethod
    def detect_format(file_path: Path) -> Optional[AudioFormat]:
        """Detect audio format from file"""
        if not file_path.exists():
            return None

        # 1 — Extension
        ext = file_path.suffix.lower()
        for fmt in AudioFormat:
            if fmt.value["ext"] == ext:
                return fmt

        # 2 — MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            for fmt in AudioFormat:
                if fmt.value["mime"] == mime_type:
                    return fmt

        # 3 — Magic bytes
        try:
            with open(file_path, "rb") as f:
                header = f.read(12)

            if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
                return AudioFormat.WAV
            if header[:4] == b"fLaC":
                return AudioFormat.FLAC
            if header[:3] == b"ID3" or header[:2] == b"\xff\xfb":
                return AudioFormat.MP3
            if header[:4] == b"OggS":
                return AudioFormat.OGG
        except Exception:
            pass

        return None

    @staticmethod
    def is_supported_format(file_path: Path) -> bool:
        """Check if file format is supported"""
        return AudioFormatDetector.detect_format(file_path) is not None

    @staticmethod
    def get_format_info(fmt: AudioFormat) -> Dict[str, Any]:
        """Get detailed format information"""
        return fmt.value
