"""
FL Studio Integration for SampleMind TUI
Generate FL Studio presets and project exports from analysis
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FLStudioPreset:
    """FL Studio preset data"""
    name: str
    tempo: float
    key: str
    mode: str
    sample_name: str
    analysis_id: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "tempo": self.tempo,
            "key": self.key,
            "mode": self.mode,
            "sample_name": self.sample_name,
            "analysis_id": self.analysis_id,
            "metadata": self.metadata,
        }


class FLStudioIntegration:
    """Integration with FL Studio for preset generation"""

    def __init__(self) -> None:
        """Initialize FL Studio integration"""
        self.presets: Dict[str, FLStudioPreset] = {}
        self.export_path: Optional[Path] = None

    def create_sampler_preset(
        self,
        sample_path: str,
        sample_name: str,
        tempo: float,
        key: str,
        mode: str,
        analysis_id: str,
        features: Optional[Dict[str, Any]] = None,
    ) -> FLStudioPreset:
        """
        Create FL Studio Sampler preset from audio analysis

        Args:
            sample_path: Path to audio sample
            sample_name: Name for the sample
            tempo: Detected tempo in BPM
            key: Detected musical key
            mode: Musical mode (major/minor)
            analysis_id: Analysis ID for reference
            features: Additional audio features

        Returns:
            FLStudioPreset object
        """
        features = features or {}

        # Create preset with analysis metadata
        preset = FLStudioPreset(
            name=f"{sample_name} ({tempo:.0f}BPM {key})",
            tempo=tempo,
            key=key,
            mode=mode,
            sample_name=sample_name,
            analysis_id=analysis_id,
            metadata={
                "sample_path": sample_path,
                "tempo": tempo,
                "key": key,
                "mode": mode,
                "spectral_centroid": features.get("spectral_centroid"),
                "rms_energy": features.get("rms_energy"),
                "zero_crossing_rate": features.get("zero_crossing_rate"),
                "created_at": self._get_timestamp(),
            },
        )

        self.presets[analysis_id] = preset
        logger.info(f"Created FL Studio sampler preset: {preset.name}")

        return preset

    def create_channel_rack_config(
        self, presets: List[FLStudioPreset]
    ) -> Dict[str, Any]:
        """
        Create FL Studio Channel Rack configuration

        Args:
            presets: List of presets to configure

        Returns:
            Channel Rack configuration dict
        """
        channels = []

        for i, preset in enumerate(presets):
            channel = {
                "channel_number": i + 1,
                "type": "Sampler",
                "name": preset.sample_name,
                "tempo": preset.tempo,
                "key": preset.key,
                "mode": preset.mode,
                "sample": preset.sample_name,
                "pitch_corrected": self._should_pitch_correct(preset.key),
                "time_corrected": True,
                "volume": 100,
                "pan": 0,
                "metadata": preset.metadata,
            }
            channels.append(channel)

        return {
            "type": "ChannelRack",
            "channels": channels,
            "total_channels": len(channels),
            "bpm": presets[0].tempo if presets else 120,
        }

    def create_playlist_arrangement(
        self,
        presets: List[FLStudioPreset],
        bpm: float = 120,
        time_signature: tuple = (4, 4),
    ) -> Dict[str, Any]:
        """
        Create FL Studio Playlist arrangement

        Args:
            presets: Presets to arrange
            bpm: Project BPM
            time_signature: Time signature tuple (numerator, denominator)

        Returns:
            Playlist arrangement dict
        """
        patterns = []

        for i, preset in enumerate(presets):
            # Create a pattern for each preset
            pattern = {
                "pattern_number": i + 1,
                "name": preset.sample_name,
                "tempo": bpm,
                "time_signature": time_signature,
                "channels": [
                    {
                        "channel": i + 1,
                        "notes": self._generate_notes_from_preset(preset),
                    }
                ],
                "length_bars": 4,
            }
            patterns.append(pattern)

        return {
            "type": "Playlist",
            "bpm": bpm,
            "time_signature": time_signature,
            "patterns": patterns,
            "arrangement": self._create_arrangement_order(patterns),
        }

    def generate_midi_export(self, preset: FLStudioPreset) -> Dict[str, Any]:
        """
        Generate MIDI data from preset (audio-to-MIDI conversion info)

        Args:
            preset: Preset to convert

        Returns:
            MIDI export data
        """
        return {
            "format": "MIDI",
            "preset_name": preset.name,
            "tempo": preset.tempo,
            "key": preset.key,
            "mode": preset.mode,
            "resolution": 480,  # MIDI PPQ
            "tracks": [
                {
                    "track_number": 1,
                    "channel": 0,
                    "name": preset.sample_name,
                    "notes": self._generate_notes_from_preset(preset),
                }
            ],
            "metadata": preset.metadata,
        }

    def export_project_template(
        self,
        presets: List[FLStudioPreset],
        project_name: str,
        bpm: float = 120,
        output_dir: Optional[str] = None,
    ) -> Path:
        """
        Export complete FL Studio project template

        Args:
            presets: Presets to include
            project_name: Project name
            bpm: Project BPM
            output_dir: Output directory

        Returns:
            Path to exported project file
        """
        output_dir = Path(output_dir) if output_dir else self.export_path or Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)

        project_data = {
            "project_name": project_name,
            "version": "2.0",
            "bpm": bpm,
            "time_signature": [4, 4],
            "master": {
                "volume": 0,
                "pan": 0,
                "limiter": True,
            },
            "channel_rack": self.create_channel_rack_config(presets),
            "playlist": self.create_playlist_arrangement(presets, bpm),
            "presets": [p.to_dict() for p in presets],
        }

        # Export as JSON (can be imported into FL Studio via script)
        output_path = output_dir / f"{project_name}.flstudio.json"

        with open(output_path, "w") as f:
            json.dump(project_data, f, indent=2)

        logger.info(f"Exported FL Studio project template: {output_path}")
        return output_path

    def get_key_transposition(self, source_key: str, target_key: str) -> int:
        """
        Calculate semitone transposition between two keys

        Args:
            source_key: Source musical key
            target_key: Target musical key

        Returns:
            Number of semitones to transpose
        """
        notes = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]

        # Find index (remove mode suffix if present)
        source = source_key.split()[0]
        target = target_key.split()[0]

        source_idx = next((i for i, n in enumerate(notes) if n in source), 0)
        target_idx = next((i for i, n in enumerate(notes) if n in target), 0)

        transposition = target_idx - source_idx
        return transposition

    def suggest_compatible_samples(
        self,
        current_preset: FLStudioPreset,
        available_presets: List[FLStudioPreset],
        max_suggestions: int = 5,
    ) -> List[FLStudioPreset]:
        """
        Suggest compatible samples for the current preset

        Args:
            current_preset: Current preset
            available_presets: Available presets to choose from
            max_suggestions: Maximum suggestions to return

        Returns:
            List of compatible presets
        """
        compatible = []

        for preset in available_presets:
            if preset.analysis_id == current_preset.analysis_id:
                continue

            # Check compatibility
            score = 0

            # Same key is best (or compatible key)
            if preset.key == current_preset.key:
                score += 100
            else:
                # Penalize different keys but allow relative keys
                score += 50

            # Similar tempo
            tempo_diff = abs(preset.tempo - current_preset.tempo)
            if tempo_diff < 5:  # Within 5 BPM
                score += 100
            elif tempo_diff < 10:
                score += 75
            else:
                score += 50

            # Same mode is good
            if preset.mode == current_preset.mode:
                score += 50

            preset_data = (preset, score)
            compatible.append(preset_data)

        # Sort by score and return top suggestions
        compatible.sort(key=lambda x: -x[1])
        return [p[0] for p in compatible[:max_suggestions]]

    @staticmethod
    def _should_pitch_correct(key: str) -> bool:
        """Determine if pitch correction should be enabled"""
        # Enable for all keys except C
        return "C" not in key or "♯" in key or "♭" in key

    @staticmethod
    def _generate_notes_from_preset(preset: FLStudioPreset) -> List[Dict]:
        """Generate MIDI note sequence from preset"""
        # Simple note generation based on key
        notes = [
            {"note": 60, "velocity": 100, "length": 480},  # C4
            {"note": 62, "velocity": 100, "length": 480},  # D4
            {"note": 64, "velocity": 100, "length": 480},  # E4
            {"note": 65, "velocity": 100, "length": 480},  # F4
        ]
        return notes

    @staticmethod
    def _create_arrangement_order(patterns: List[Dict]) -> List[int]:
        """Create arrangement order for patterns"""
        return list(range(1, len(patterns) + 1))

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global singleton instance
_fl_studio_integration: Optional[FLStudioIntegration] = None


def get_fl_studio_integration() -> FLStudioIntegration:
    """Get or create FL Studio integration singleton"""
    global _fl_studio_integration
    if _fl_studio_integration is None:
        _fl_studio_integration = FLStudioIntegration()
    return _fl_studio_integration
