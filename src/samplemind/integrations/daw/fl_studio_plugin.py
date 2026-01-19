"""
FL Studio Native Python Plugin Integration

Provides real-time integration with FL Studio 20+:
- Drag-and-drop sample analysis and loading
- Metadata display in mixer
- BPM and key sync with project
- AI-powered sample suggestions
- Real-time waveform visualization
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FLStudioMetadata:
    """FL Studio sample metadata"""

    file_path: str
    bpm: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    energy: Optional[float] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: int = 2
    bit_depth: int = 24
    timestamp: str = None
    ai_tags: List[str] = None
    analysis_level: str = "STANDARD"

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.ai_tags is None:
            self.ai_tags = []

    def to_fl_format(self) -> Dict[str, Any]:
        """Convert to FL Studio compatible format"""
        return {
            "filepath": self.file_path,
            "bpm": self.bpm,
            "key": self.key,
            "genre": self.genre,
            "mood": self.mood,
            "energy": self.energy or 0.5,
            "duration": self.duration,
            "samplerate": self.sample_rate,
            "channels": self.channels,
            "bitdepth": self.bit_depth,
            "tags": ", ".join(self.ai_tags),
            "analyzedat": self.timestamp,
        }


class FLStudioPlugin:
    """FL Studio Python Plugin Implementation"""

    NAME = "SampleMind AI"
    VERSION = "2.1.0-beta"
    AUTHOR = "SampleMind Team"
    DESCRIPTION = "AI-powered sample analysis and suggestion engine for FL Studio"

    def __init__(self):
        """Initialize FL Studio plugin"""
        self.is_active = False
        self.project_bpm = 120.0
        self.project_key = "C"
        self.loaded_samples: Dict[str, FLStudioMetadata] = {}
        self.analysis_queue: List[str] = []
        self.suggestions_cache: Dict[str, List[str]] = {}
        logger.info(f"FLStudioPlugin {self.VERSION} initialized")

    def on_init(self) -> None:
        """Called when FL Studio initializes the plugin"""
        self.is_active = True
        logger.info("FL Studio plugin activated")
        self._register_dnd_handler()
        self._sync_project_info()

    def on_destroy(self) -> None:
        """Called when FL Studio shuts down"""
        self.is_active = False
        logger.info("FL Studio plugin deactivated")

    def on_project_load(self, project_path: str) -> None:
        """Called when a project is loaded"""
        logger.info(f"Project loaded: {project_path}")
        self._sync_project_info()
        self._scan_project_samples(project_path)

    def _register_dnd_handler(self) -> None:
        """Register drag-and-drop handler for sample analysis"""
        logger.debug("Registering drag-and-drop handler")
        # FL Studio will call on_drop() when user drops files on plugin

    def on_drop(self, file_path: str) -> None:
        """Handle file drop for instant analysis"""
        logger.info(f"File dropped: {file_path}")

        try:
            # Queue for analysis
            self.analysis_queue.append(file_path)

            # Analyze immediately (async)
            metadata = self._analyze_sample(file_path)

            if metadata:
                self.loaded_samples[file_path] = metadata

                # Display metadata in FL Studio mixer
                self._display_metadata_in_mixer(file_path, metadata)

                # Get AI suggestions for this sample
                suggestions = self._get_ai_suggestions(metadata)
                self.suggestions_cache[file_path] = suggestions

                logger.info(f"Sample analyzed: {file_path}")
                logger.info(f"BPM: {metadata.bpm}, Key: {metadata.key}, Genre: {metadata.genre}")

        except Exception as e:
            logger.error(f"Error analyzing dropped file: {e}")

    def _analyze_sample(self, file_path: str) -> Optional[FLStudioMetadata]:
        """Analyze audio sample with SampleMind engine"""
        try:
            from samplemind.core.engine import AudioEngine

            engine = AudioEngine()
            result = engine.analyze_audio(file_path, analysis_level="STANDARD")

            metadata = FLStudioMetadata(
                file_path=file_path,
                bpm=result.get("bpm"),
                key=result.get("key"),
                genre=result.get("genre"),
                mood=result.get("mood"),
                energy=result.get("energy"),
                duration=result.get("duration"),
                sample_rate=result.get("sample_rate"),
                channels=result.get("channels", 2),
                analysis_level="STANDARD",
            )

            # Get AI tags if available
            try:
                from samplemind.integrations import SampleMindAIManager

                ai = SampleMindAIManager()
                ai_result = ai.analyze_music(
                    file_path, {"analysis_type": "classification"}
                )
                metadata.ai_tags = ai_result.get("tags", [])
            except Exception as e:
                logger.debug(f"Could not get AI tags: {e}")

            return metadata

        except Exception as e:
            logger.error(f"Error analyzing sample: {e}")
            return None

    def _display_metadata_in_mixer(
        self, file_path: str, metadata: FLStudioMetadata
    ) -> None:
        """Display metadata in FL Studio mixer"""
        try:
            # Convert to FL Studio format
            fl_meta = metadata.to_fl_format()

            # In real FL Studio plugin, this would update the mixer display
            logger.debug(f"Displaying metadata in mixer: {json.dumps(fl_meta, indent=2)}")

            # Store as project data for persistence
            self._save_sample_metadata(file_path, fl_meta)

        except Exception as e:
            logger.error(f"Error displaying metadata: {e}")

    def _get_ai_suggestions(self, metadata: FLStudioMetadata) -> List[str]:
        """Get AI-powered sample suggestions"""
        try:
            from samplemind.core.database import ChromaDB

            db = ChromaDB()

            # Find similar samples based on metadata
            query = f"{metadata.genre} {metadata.mood} {metadata.key}"
            similar_samples = db.search(
                query=query, collection="audio_features", limit=5
            )

            suggestions = [s.get("metadata", {}).get("filename") for s in similar_samples]

            logger.debug(f"AI suggestions for {metadata.file_path}: {suggestions}")
            return suggestions

        except Exception as e:
            logger.debug(f"Could not get AI suggestions: {e}")
            return []

    def _sync_project_info(self) -> None:
        """Sync current project BPM and key with SampleMind"""
        try:
            # In real FL Studio, would get from FLMidi.getCurrentPunchIn() etc.
            logger.debug(f"Project sync: BPM={self.project_bpm}, Key={self.project_key}")
        except Exception as e:
            logger.error(f"Error syncing project info: {e}")

    def _scan_project_samples(self, project_path: str) -> None:
        """Scan project for samples and preload metadata"""
        try:
            project_dir = Path(project_path).parent
            audio_files = list(project_dir.glob("**/*.wav")) + list(
                project_dir.glob("**/*.mp3")
            )

            logger.info(f"Scanning project for samples: {len(audio_files)} files found")

            for audio_file in audio_files[:10]:  # Limit to first 10 for performance
                if str(audio_file) not in self.loaded_samples:
                    metadata = self._analyze_sample(str(audio_file))
                    if metadata:
                        self.loaded_samples[str(audio_file)] = metadata

        except Exception as e:
            logger.error(f"Error scanning project samples: {e}")

    def _save_sample_metadata(
        self, file_path: str, metadata: Dict[str, Any]
    ) -> None:
        """Save metadata for persistence across sessions"""
        try:
            meta_dir = Path.home() / ".samplemind" / "fl_studio" / "metadata"
            meta_dir.mkdir(parents=True, exist_ok=True)

            file_hash = hash(file_path) % 10000000
            meta_file = meta_dir / f"{file_hash}.json"

            with open(meta_file, "w") as f:
                json.dump(
                    {"file_path": file_path, "metadata": metadata},
                    f,
                    indent=2,
                )

            logger.debug(f"Metadata saved: {meta_file}")

        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def get_loaded_samples(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded samples and their metadata"""
        return {
            path: asdict(metadata) for path, metadata in self.loaded_samples.items()
        }

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information for FL Studio"""
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "author": self.AUTHOR,
            "description": self.DESCRIPTION,
            "active": self.is_active,
            "samples_loaded": len(self.loaded_samples),
        }


# Global plugin instance
_plugin_instance: Optional[FLStudioPlugin] = None


def get_plugin() -> FLStudioPlugin:
    """Get or create global plugin instance"""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = FLStudioPlugin()
    return _plugin_instance


def init():
    """Initialize plugin (called by FL Studio)"""
    plugin = get_plugin()
    plugin.on_init()


def destroy():
    """Destroy plugin (called by FL Studio)"""
    plugin = get_plugin()
    plugin.on_destroy()
