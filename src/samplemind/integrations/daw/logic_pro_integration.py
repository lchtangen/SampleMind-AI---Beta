"""
Logic Pro Audio Unit (AU) Plugin Integration

Provides real-time integration with Logic Pro via AU plugin format:
- Smart browser organization
- Sample metadata display in library
- Project-aware suggestions
- Real-time BPM/Key sync

Note: AU plugin wrapper requires Xcode and C++/ObjC bridge.
This module provides the Python logic layer.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LogicProBrowserCategory(Enum):
    """Logic Pro browser categories"""

    DRUMS = "Drums"
    BASS = "Bass"
    SYNTH = "Synth"
    STRINGS = "Strings"
    BRASS = "Brass"
    WOODWINDS = "Woodwinds"
    VOCAL = "Vocal"
    EFFECTS = "Effects"
    LOOPS = "Loops"
    AMBIENT = "Ambient"
    ORCHESTRAL = "Orchestral"
    WORLD = "World"
    ELECTRONIC = "Electronic"


@dataclass
class LogicProSampleInfo:
    """Logic Pro sample information"""

    file_path: str
    category: LogicProBrowserCategory
    subcategory: str
    bpm: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    color_tag: str = "None"  # Logic Pro color coding
    compatibility_rating: float = 0.0  # 0-100%
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class LogicProAUPlugin:
    """Logic Pro Audio Unit Plugin Logic Layer"""

    NAME = "SampleMind AI"
    VERSION = "2.1.0-beta"
    BUNDLE_ID = "com.samplemind.logic-pro-au"
    MANUFACTURER_ID = "SMnd"

    # AU Plugin parameters
    PARAM_ANALYSIS_MODE = 0  # 0=Quick, 1=Standard, 2=Detailed
    PARAM_AUTO_TAG = 1
    PARAM_BROWSER_SYNC = 2
    PARAM_BPM_SYNC = 3

    def __init__(self):
        """Initialize Logic Pro AU plugin"""
        self.is_loaded = False
        self.sample_library: Dict[str, LogicProSampleInfo] = {}
        self.current_project_bpm = 120.0
        self.current_project_key = "C"
        self.browser_categories: Dict[str, List[str]] = {}
        self.parameters = {
            self.PARAM_ANALYSIS_MODE: 1,  # Standard
            self.PARAM_AUTO_TAG: 1.0,  # Enabled
            self.PARAM_BROWSER_SYNC: 1.0,  # Enabled
            self.PARAM_BPM_SYNC: 1.0,  # Enabled
        }

        logger.info(f"LogicProAUPlugin {self.VERSION} initialized")

    def au_init(self) -> None:
        """Called when AU plugin loads"""
        self.is_loaded = True
        logger.info("Logic Pro AU plugin loaded")

        # Initialize browser structure
        self._initialize_browser()

        # Scan system audio library
        self._scan_audio_library()

    def au_destroy(self) -> None:
        """Called when AU plugin unloads"""
        self.is_loaded = False
        logger.info("Logic Pro AU plugin unloaded")

    def au_render(self, num_frames: int) -> None:
        """Called for audio rendering (no-op for browser plugin)"""
        pass

    def _initialize_browser(self) -> None:
        """Initialize browser category structure"""
        try:
            for category in LogicProBrowserCategory:
                self.browser_categories[category.value] = []

            logger.debug("Browser categories initialized")

        except Exception as e:
            logger.error(f"Error initializing browser: {e}")

    def _scan_audio_library(self) -> None:
        """Scan system audio library for samples"""
        try:
            # Scan standard Logic Pro library locations
            library_paths = [
                Path.home() / "Music" / "Logic Pro Library",
                Path("/Library/Audio/Apple Loops"),
                Path("/Library/Application Support/Logic Pro"),
            ]

            for lib_path in library_paths:
                if lib_path.exists():
                    self._scan_directory(lib_path)

            logger.info(
                f"Audio library scanned: {len(self.sample_library)} samples found"
            )

        except Exception as e:
            logger.error(f"Error scanning audio library: {e}")

    def _scan_directory(self, directory: Path) -> None:
        """Scan directory for audio files"""
        try:
            audio_extensions = {".wav", ".mp3", ".m4a", ".aiff", ".caf"}

            for audio_file in directory.rglob("*"):
                if audio_file.suffix.lower() in audio_extensions:
                    self._add_sample_to_library(audio_file)

        except Exception as e:
            logger.debug(f"Error scanning directory {directory}: {e}")

    def _add_sample_to_library(self, file_path: Path) -> None:
        """Add sample to Logic Pro library"""
        try:
            # Analyze sample
            info = self._analyze_sample(file_path)

            if info:
                self.sample_library[str(file_path)] = info

                # Add to browser category
                if info.category.value not in self.browser_categories:
                    self.browser_categories[info.category.value] = []

                self.browser_categories[info.category.value].append(str(file_path))

                logger.debug(f"Sample added to library: {file_path.name}")

        except Exception as e:
            logger.debug(f"Error adding sample: {e}")

    def _analyze_sample(self, file_path: Path) -> Optional[LogicProSampleInfo]:
        """Analyze audio sample"""
        try:
            from samplemind.core.engine import AudioEngine

            engine = AudioEngine()
            result = engine.analyze_audio(str(file_path), analysis_level="QUICK")

            # Determine category from genre/mood
            category = self._determine_category(result)
            subcategory = result.get("mood", "Other")

            # Calculate compatibility with current project
            compatibility = self._calculate_compatibility(result)

            # Determine color tag
            color_tag = self._determine_color_tag(compatibility)

            info = LogicProSampleInfo(
                file_path=str(file_path),
                category=category,
                subcategory=subcategory,
                bpm=result.get("bpm"),
                key=result.get("key"),
                genre=result.get("genre"),
                mood=result.get("mood"),
                color_tag=color_tag,
                compatibility_rating=compatibility,
                tags=result.get("tags", []),
            )

            return info

        except Exception as e:
            logger.debug(f"Error analyzing sample: {e}")
            return None

    def _determine_category(self, analysis: Dict[str, Any]) -> LogicProBrowserCategory:
        """Determine browser category from analysis"""
        genre = analysis.get("genre", "").lower()
        mood = analysis.get("mood", "").lower()

        # Map genre to category
        if "drum" in genre or "percussion" in genre:
            return LogicProBrowserCategory.DRUMS
        elif "bass" in genre:
            return LogicProBrowserCategory.BASS
        elif "synth" in genre or "electronic" in genre:
            return LogicProBrowserCategory.SYNTH
        elif "string" in genre or "violin" in genre:
            return LogicProBrowserCategory.STRINGS
        elif "brass" in genre or "trumpet" in genre:
            return LogicProBrowserCategory.BRASS
        elif "vocal" in genre or "voice" in genre:
            return LogicProBrowserCategory.VOCAL
        elif "ambient" in mood or "pad" in genre:
            return LogicProBrowserCategory.AMBIENT
        elif "loop" in genre:
            return LogicProBrowserCategory.LOOPS
        else:
            return LogicProBrowserCategory.ELECTRONIC

    def _calculate_compatibility(self, analysis: Dict[str, Any]) -> float:
        """Calculate compatibility with current project (0-100%)"""
        compatibility = 50.0  # Base score

        # BPM compatibility (±5% = 100 points)
        sample_bpm = analysis.get("bpm", self.current_project_bpm)
        bpm_diff = abs(sample_bpm - self.current_project_bpm) / self.current_project_bpm

        if bpm_diff < 0.05:
            compatibility += 25
        elif bpm_diff < 0.1:
            compatibility += 15
        elif bpm_diff < 0.2:
            compatibility += 5

        # Key compatibility (exact = 25 points)
        sample_key = analysis.get("key", self.current_project_key)
        if sample_key == self.current_project_key:
            compatibility += 25

        return min(100.0, compatibility)

    def _determine_color_tag(self, compatibility: float) -> str:
        """Determine Logic Pro color tag based on compatibility"""
        if compatibility >= 90:
            return "Green"  # Perfect match
        elif compatibility >= 75:
            return "Blue"  # Good match
        elif compatibility >= 60:
            return "Yellow"  # Acceptable
        elif compatibility >= 40:
            return "Orange"  # Needs adjustment
        else:
            return "Red"  # Poor match

    def get_browser_contents(self, category: str) -> List[Dict[str, Any]]:
        """Get browser contents for category"""
        try:
            if category not in self.browser_categories:
                return []

            samples = []
            for file_path in self.browser_categories[category]:
                if file_path in self.sample_library:
                    info = self.sample_library[file_path]
                    samples.append(
                        {
                            "name": Path(file_path).stem,
                            "file_path": file_path,
                            "bpm": info.bpm,
                            "key": info.key,
                            "color": info.color_tag,
                            "compatibility": f"{info.compatibility_rating:.0f}%",
                            "mood": info.mood,
                        }
                    )

            return sorted(samples, key=lambda x: x["compatibility"], reverse=True)

        except Exception as e:
            logger.error(f"Error getting browser contents: {e}")
            return []

    def set_parameter(self, param_id: int, value: float) -> None:
        """Set AU plugin parameter"""
        try:
            self.parameters[param_id] = value

            # Handle specific parameters
            if param_id == self.PARAM_BROWSER_SYNC and value > 0.5:
                self._sync_browser_with_library()

            elif param_id == self.PARAM_BPM_SYNC and value > 0.5:
                self._sync_bpm_with_project()

            logger.debug(f"Parameter set: {param_id} = {value}")

        except Exception as e:
            logger.error(f"Error setting parameter: {e}")

    def get_parameter(self, param_id: int) -> float:
        """Get AU plugin parameter value"""
        return self.parameters.get(param_id, 0.0)

    def _sync_browser_with_library(self) -> None:
        """Sync browser with current library"""
        try:
            self._initialize_browser()
            self._scan_audio_library()
            logger.info("Browser synced with library")

        except Exception as e:
            logger.error(f"Error syncing browser: {e}")

    def _sync_bpm_with_project(self) -> None:
        """Sync BPM with Logic Pro project"""
        try:
            # In real AU plugin, would get from AUHost
            logger.debug(
                f"BPM synced: project={self.current_project_bpm}, samples={len(self.sample_library)}"
            )

        except Exception as e:
            logger.error(f"Error syncing BPM: {e}")

    def set_project_tempo(self, bpm: float) -> None:
        """Set current project tempo"""
        self.current_project_bpm = bpm
        logger.debug(f"Project tempo set: {bpm}")

    def set_project_key(self, key: str) -> None:
        """Set current project key"""
        self.current_project_key = key
        logger.debug(f"Project key set: {key}")

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "bundle_id": self.BUNDLE_ID,
            "manufacturer": self.MANUFACTURER_ID,
            "is_loaded": self.is_loaded,
            "samples_in_library": len(self.sample_library),
            "categories": len(self.browser_categories),
        }


# Global instance
_au_plugin: Optional[LogicProAUPlugin] = None


def get_au_plugin() -> LogicProAUPlugin:
    """Get or create global AU plugin instance"""
    global _au_plugin
    if _au_plugin is None:
        _au_plugin = LogicProAUPlugin()
    return _au_plugin
