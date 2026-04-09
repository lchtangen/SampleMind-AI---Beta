"""
SampleMind AI — Audio Metadata Extractor

Extracts comprehensive tag and technical metadata from audio files
using mutagen, supporting ID3 (MP3), Vorbis (OGG/FLAC), iTunes (M4A),
and generic containers.
"""

import logging
from pathlib import Path
from typing import Any

import mutagen

from .models import AudioFormat

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract comprehensive metadata from audio files"""

    @staticmethod
    def extract_metadata(file_path: Path, audio_format: AudioFormat) -> dict[str, Any]:
        """Extract all available tag and technical metadata."""
        metadata: dict[str, Any] = {}

        try:
            audio_file = mutagen.File(str(file_path))

            if audio_file is not None:
                # Common tags — checked in ID3 / Vorbis / iTunes order
                metadata["title"] = MetadataExtractor._get_tag(
                    audio_file, ["TIT2", "TITLE", "\xa9nam"]
                )
                metadata["artist"] = MetadataExtractor._get_tag(
                    audio_file, ["TPE1", "ARTIST", "\xa9ART"]
                )
                metadata["album"] = MetadataExtractor._get_tag(
                    audio_file, ["TALB", "ALBUM", "\xa9alb"]
                )
                metadata["genre"] = MetadataExtractor._get_tag(
                    audio_file, ["TCON", "GENRE", "\xa9gen"]
                )
                metadata["year"] = MetadataExtractor._get_year(audio_file)
                metadata["track_number"] = MetadataExtractor._get_track_number(
                    audio_file
                )

                # Technical properties from mutagen's info block
                if hasattr(audio_file, "info"):
                    info = audio_file.info
                    metadata["duration"] = getattr(info, "length", 0.0)
                    metadata["bitrate"] = getattr(info, "bitrate", None)
                    metadata["sample_rate"] = getattr(info, "sample_rate", None)
                    metadata["channels"] = getattr(info, "channels", None)

                    if hasattr(info, "bits_per_sample"):
                        metadata["bit_depth"] = info.bits_per_sample
                    elif hasattr(info, "bits"):
                        metadata["bit_depth"] = info.bits

        except Exception as e:
            logger.warning("⚠️ Metadata extraction failed for %s: %s", file_path, e)

        return metadata

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_tag(audio_file: Any, tag_names: list[str]) -> str | None:
        """Return the first matching tag value, coerced to str."""
        for tag_name in tag_names:
            if tag_name in audio_file:
                value = audio_file[tag_name]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return None

    @staticmethod
    def _get_year(audio_file: Any) -> int | None:
        """Extract year from TDRC / TYER / DATE / ©day tags."""
        year_tags = ["TDRC", "TYER", "DATE", "\xa9day"]
        for tag in year_tags:
            if tag in audio_file:
                value = audio_file[tag]
                if isinstance(value, list) and value:
                    value = value[0]
                try:
                    return int(str(value)[:4])
                except (ValueError, TypeError):
                    continue
        return None

    @staticmethod
    def _get_track_number(audio_file: Any) -> int | None:
        """Extract track number, handling 'N/Total' format."""
        track_tags = ["TRCK", "TRACKNUMBER", "trkn"]
        for tag in track_tags:
            if tag in audio_file:
                value = audio_file[tag]
                if isinstance(value, list) and value:
                    value = value[0]
                try:
                    return int(str(value).split("/")[0])
                except (ValueError, TypeError):
                    continue
        return None
