"""
Ableton Live Control Surface Integration

Provides real-time integration with Ableton Live 11+ via Control Surface API:
- Sample metadata display in browser
- Project-aware AI suggestions
- Real-time BPM and key sync
- Smart sample loading with metadata
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from threading import Thread
import time

logger = logging.getLogger(__name__)


@dataclass
class AbletonSampleMetadata:
    """Ableton sample metadata"""

    file_path: str
    bpm: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    energy: Optional[float] = None
    compatible_with_project: bool = False
    suggested_track_type: Optional[str] = None
    notes: str = ""


class AbletonControlSurface:
    """Ableton Live Control Surface Device"""

    NAME = "SampleMind AI Control Surface"
    VERSION = "2.1.0-beta"

    def __init__(self):
        """Initialize Ableton Control Surface"""
        self.is_connected = False
        self.current_song = None
        self.project_bpm = 120.0
        self.project_key = "C"
        self.selected_track = None
        self.sample_metadata_cache: Dict[str, AbletonSampleMetadata] = {}
        self.suggestions_list: List[str] = []
        logger.info(f"AbletonControlSurface {self.VERSION} initialized")

    def connect(self, song) -> None:
        """Connect to Ableton Live session"""
        self.current_song = song
        self.is_connected = True
        logger.info("Connected to Ableton Live")

        # Start listening for track changes
        self._setup_listeners()

        # Get current project info
        self._sync_with_project()

    def disconnect(self) -> None:
        """Disconnect from Ableton Live"""
        self.is_connected = False
        logger.info("Disconnected from Ableton Live")

    def _setup_listeners(self) -> None:
        """Setup event listeners for track/sample changes"""
        try:
            if self.current_song:
                # Listen for track selection changes
                # In real implementation: self.current_song.add_tracks_listener(self.on_track_changed)
                logger.debug("Event listeners set up")
        except Exception as e:
            logger.error(f"Error setting up listeners: {e}")

    def _sync_with_project(self) -> None:
        """Sync with current Ableton project"""
        try:
            if self.current_song:
                # Get project BPM
                self.project_bpm = getattr(self.current_song, "tempo", 120.0)

                # Get selected track
                self.selected_track = getattr(self.current_song, "view", {}).get(
                    "selected_track"
                )

                logger.info(
                    f"Project synced: BPM={self.project_bpm}, Track={self.selected_track}"
                )

        except Exception as e:
            logger.error(f"Error syncing with project: {e}")

    def on_track_selected(self, track) -> None:
        """Called when user selects a track"""
        self.selected_track = track
        logger.info(f"Track selected: {track}")

        # Get samples in track and show metadata
        self._update_track_metadata()

    def _update_track_metadata(self) -> None:
        """Update metadata for selected track"""
        try:
            if not self.selected_track:
                return

            # Get clips in track
            clips = getattr(self.selected_track, "clip_slots", [])
            logger.debug(f"Clips in track: {len(clips)}")

            # For each clip, get metadata
            for clip in clips:
                if clip and hasattr(clip, "clip"):
                    self._display_clip_metadata(clip.clip)

        except Exception as e:
            logger.error(f"Error updating track metadata: {e}")

    def _display_clip_metadata(self, clip) -> None:
        """Display metadata for a clip"""
        try:
            clip_name = getattr(clip, "name", "Unknown")
            logger.debug(f"Displaying metadata for clip: {clip_name}")

            # Get file path from clip
            file_path = self._get_clip_file_path(clip)
            if file_path:
                metadata = self._analyze_clip_file(file_path)
                self._display_in_browser(clip_name, metadata)

        except Exception as e:
            logger.error(f"Error displaying clip metadata: {e}")

    def _get_clip_file_path(self, clip) -> Optional[str]:
        """Get file path from clip"""
        try:
            # Try to get from clip properties
            if hasattr(clip, "file_path"):
                return str(clip.file_path)

            # Try to get from sample
            if hasattr(clip, "sample"):
                sample = clip.sample
                if hasattr(sample, "file_path"):
                    return str(sample.file_path)

            return None

        except Exception as e:
            logger.debug(f"Could not get clip file path: {e}")
            return None

    def _analyze_clip_file(self, file_path: str) -> Optional[AbletonSampleMetadata]:
        """Analyze audio file"""
        try:
            from samplemind.core.engine import AudioEngine

            engine = AudioEngine()
            result = engine.analyze_audio(file_path, analysis_level="STANDARD")

            metadata = AbletonSampleMetadata(
                file_path=file_path,
                bpm=result.get("bpm"),
                key=result.get("key"),
                genre=result.get("genre"),
                mood=result.get("mood"),
                energy=result.get("energy"),
                compatible_with_project=self._check_compatibility(result),
                suggested_track_type=self._suggest_track_type(result),
            )

            # Add notes about suggestions
            if metadata.compatible_with_project:
                metadata.notes += "✓ Compatible with project BPM/Key. "
            else:
                metadata.notes += "⚠ Different BPM/Key - may need warping. "

            if metadata.energy and metadata.energy > 0.7:
                metadata.notes += "High energy sample. "
            elif metadata.energy and metadata.energy < 0.3:
                metadata.notes += "Low energy/atmospheric sample. "

            self.sample_metadata_cache[file_path] = metadata
            return metadata

        except Exception as e:
            logger.error(f"Error analyzing clip: {e}")
            return None

    def _check_compatibility(self, analysis_result: Dict[str, Any]) -> bool:
        """Check if sample is compatible with project"""
        sample_bpm = analysis_result.get("bpm", self.project_bpm)

        # Allow 5% BPM deviation
        bpm_match = abs(sample_bpm - self.project_bpm) / self.project_bpm < 0.05

        # Key match
        sample_key = analysis_result.get("key", self.project_key)
        key_match = sample_key == self.project_key

        return bpm_match and key_match

    def _suggest_track_type(self, analysis_result: Dict[str, Any]) -> Optional[str]:
        """Suggest track type based on analysis"""
        genre = analysis_result.get("genre", "").lower()
        mood = analysis_result.get("mood", "").lower()

        # Map genre/mood to track type
        if "drum" in genre or "percussion" in genre:
            return "Drum Rack"
        elif "bass" in genre or "low" in mood:
            return "MIDI Track (Bass)"
        elif "synth" in genre or "melodic" in mood:
            return "MIDI Track (Synth)"
        elif "vocal" in genre or "speech" in genre:
            return "Audio Track"
        else:
            return "Audio Track"

    def _display_in_browser(
        self, clip_name: str, metadata: Optional[AbletonSampleMetadata]
    ) -> None:
        """Display metadata in browser"""
        try:
            if not metadata:
                return

            # Create display string
            display = f"""
{clip_name}
━━━━━━━━━━━━━━━━━━━━
BPM: {metadata.bpm or 'Unknown':.1f}
Key: {metadata.key or 'Unknown'}
Genre: {metadata.genre or 'Unknown'}
Mood: {metadata.mood or 'Unknown'}
Energy: {metadata.energy or 0:.0%}
━━━━━━━━━━━━━━━━━━━━
{metadata.notes}
Suggested: {metadata.suggested_track_type}
"""

            logger.debug(display)

            # In real implementation, would display in Ableton browser
            self._save_metadata_for_browser(clip_name, metadata)

        except Exception as e:
            logger.error(f"Error displaying in browser: {e}")

    def _save_metadata_for_browser(
        self, clip_name: str, metadata: AbletonSampleMetadata
    ) -> None:
        """Save metadata for browser display"""
        try:
            meta_dir = Path.home() / ".samplemind" / "ableton" / "browser"
            meta_dir.mkdir(parents=True, exist_ok=True)

            # Create metadata file
            meta_data = {
                "clip_name": clip_name,
                "file_path": metadata.file_path,
                "bpm": metadata.bpm,
                "key": metadata.key,
                "genre": metadata.genre,
                "mood": metadata.mood,
                "energy": metadata.energy,
                "compatible": metadata.compatible_with_project,
                "suggested_track": metadata.suggested_track_type,
                "notes": metadata.notes,
            }

            meta_file = meta_dir / f"{clip_name.replace(' ', '_')}.json"
            with open(meta_file, "w") as f:
                json.dump(meta_data, f, indent=2)

            logger.debug(f"Metadata saved for browser: {meta_file}")

        except Exception as e:
            logger.error(f"Error saving metadata for browser: {e}")

    def get_suggestions(self) -> List[Dict[str, Any]]:
        """Get AI-powered suggestions for current track"""
        try:
            suggestions = []

            if self.selected_track:
                # Get similar samples
                similar = self._get_similar_samples()
                suggestions.extend(similar)

            return suggestions

        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []

    def _get_similar_samples(self) -> List[Dict[str, Any]]:
        """Get similar samples from library"""
        try:
            from samplemind.core.database import ChromaDB

            db = ChromaDB()

            # Build query from current track metadata
            query_parts = []

            if self.project_key:
                query_parts.append(f"key:{self.project_key}")

            # Search for similar
            results = db.search(
                query=" ".join(query_parts) if query_parts else "music",
                collection="audio_features",
                limit=5,
            )

            suggestions = [
                {
                    "file_path": r.get("metadata", {}).get("file_path"),
                    "score": r.get("score", 0),
                    "reason": "Similar key and energy",
                }
                for r in results
            ]

            logger.debug(f"Found {len(suggestions)} similar samples")
            return suggestions

        except Exception as e:
            logger.debug(f"Could not get similar samples: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Get control surface status"""
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "connected": self.is_connected,
            "project_bpm": self.project_bpm,
            "project_key": self.project_key,
            "metadata_cached": len(self.sample_metadata_cache),
        }


# Global instance
_control_surface: Optional[AbletonControlSurface] = None


def get_control_surface() -> AbletonControlSurface:
    """Get or create global control surface"""
    global _control_surface
    if _control_surface is None:
        _control_surface = AbletonControlSurface()
    return _control_surface
