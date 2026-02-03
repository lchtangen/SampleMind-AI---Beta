"""
FL Studio Plugin - SampleMind AI Integration (Phase 13.2.1)

Native FL Studio plugin for real-time audio analysis and sample management:
- Real-time sample analysis
- Intelligent sample browser
- Drag-and-drop integration
- Analysis caching
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Note: This is a Python skeleton for FL Studio plugin
# FL Studio plugins require CTYPES/COM interface or Python DLL wrapper
# For production deployment, this would be wrapped with:
# - FL Studio SDK (C++ wrapper)
# - Python to COM bridge
# - Native event handlers


class FLStudioSampleMindPlugin:
    """
    FL Studio plugin for SampleMind AI audio analysis and sample management.

    Features:
    - Real-time waveform display
    - BPM detection and display
    - Key detection
    - Genre/mood classification
    - Sample browser with search
    - Drag-and-drop to mixer
    - Analysis batch processing
    """

    def __init__(self):
        """Initialize FL Studio plugin"""
        self.plugin_name = "SampleMind AI"
        self.plugin_version = "1.0.0"
        self.unique_id = 0x534D5041  # SMPA in hex

        # Plugin state
        self.is_open = False
        self.current_sample = None
        self.analysis_result = None
        self.recent_samples = []

        # UI state
        self.browser_visible = True
        self.analysis_visible = True
        self.waveform_visible = True

        # Analysis cache
        self.cache_enabled = True
        self.cache_size_mb = 100
        self.cached_analyses: Dict[str, Any] = {}

        logger.info(f"Initialized {self.plugin_name} v{self.plugin_version}")

    # ========================================================================
    # PLUGIN LIFECYCLE (called by FL Studio)
    # ========================================================================

    def on_create(self) -> None:
        """Called when plugin is created"""
        self.is_open = True
        logger.info("Plugin created")

    def on_destroy(self) -> None:
        """Called when plugin is destroyed"""
        self.is_open = False
        self.save_state()
        logger.info("Plugin destroyed")

    def on_paint(self) -> None:
        """Called when plugin window needs painting"""
        if not self.is_open:
            return

        # In production, this would draw the UI using FL Studio's graphics API
        # self._draw_ui()

    def on_idle(self) -> None:
        """Called regularly by FL Studio"""
        if not self.is_open:
            return

        # Update real-time displays
        # self._update_real_time_display()

    # ========================================================================
    # SAMPLE BROWSER
    # ========================================================================

    def load_sample(self, file_path: str) -> bool:
        """
        Load a sample for analysis.

        Args:
            file_path: Path to audio file

        Returns:
            True if successful
        """
        try:
            from samplemind.core.engine.audio_engine import AudioEngine

            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"Sample file not found: {file_path}")
                return False

            # Initialize audio engine
            engine = AudioEngine()

            # Analyze sample
            self.analysis_result = engine.analyze_full(str(file_path))

            self.current_sample = file_path
            self._add_to_recent(file_path)

            logger.info(f"Loaded sample: {file_path.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load sample: {e}")
            return False

    def search_samples(self, query: str) -> List[Dict[str, Any]]:
        """
        Search sample library for matching samples.

        Args:
            query: Search query (BPM, key, genre, etc.)

        Returns:
            List of matching samples
        """
        try:
            from samplemind.core.database.chroma import ChromaDBManager

            db = ChromaDBManager()
            results = db.semantic_search(query, top_k=20)

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_similar_samples(self, file_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find samples similar to the given file.

        Args:
            file_path: Reference audio file
            limit: Maximum results to return

        Returns:
            List of similar samples
        """
        try:
            from samplemind.core.engine.audio_engine import AudioEngine

            engine = AudioEngine()
            similar = engine.find_similar(str(file_path), limit=limit)

            return similar

        except Exception as e:
            logger.error(f"Failed to find similar samples: {e}")
            return []

    def _add_to_recent(self, file_path: Path) -> None:
        """Add sample to recent list"""
        file_path = str(file_path)
        if file_path in self.recent_samples:
            self.recent_samples.remove(file_path)
        self.recent_samples.insert(0, file_path)
        if len(self.recent_samples) > 20:
            self.recent_samples = self.recent_samples[:20]

    # ========================================================================
    # ANALYSIS DISPLAY
    # ========================================================================

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of current analysis"""
        if not self.analysis_result:
            return {}

        return {
            "tempo_bpm": self.analysis_result.get("tempo_bpm"),
            "key": self.analysis_result.get("key"),
            "genre": self.analysis_result.get("primary_genre"),
            "mood": self.analysis_result.get("mood"),
            "energy": self.analysis_result.get("energy_level"),
            "confidence": self.analysis_result.get("confidence_score"),
            "duration": self.analysis_result.get("duration_seconds"),
        }

    def get_waveform_data(self) -> Optional[List[float]]:
        """
        Get waveform data for display.

        Returns:
            Normalized waveform samples (0-1)
        """
        if not self.current_sample:
            return None

        try:
            import librosa
            import numpy as np

            audio, sr = librosa.load(str(self.current_sample), sr=22050, mono=True)

            # Downsample for display (target ~1000 samples)
            display_samples = 1000
            step = len(audio) // display_samples
            if step < 1:
                step = 1

            waveform = audio[::step]

            # Normalize to 0-1
            max_val = np.max(np.abs(waveform))
            if max_val > 0:
                waveform = (waveform + max_val) / (2 * max_val)
            else:
                waveform = np.full_like(waveform, 0.5)

            return waveform.tolist()

        except Exception as e:
            logger.error(f"Failed to get waveform: {e}")
            return None

    def get_spectrogram_data(self) -> Optional[List[List[float]]]:
        """
        Get spectrogram data for visualization.

        Returns:
            Spectrogram data (time x frequency)
        """
        if not self.current_sample:
            return None

        try:
            import librosa
            import numpy as np

            audio, sr = librosa.load(str(self.current_sample), sr=22050, mono=True)

            # Compute STFT
            D = np.abs(librosa.stft(audio))

            # Convert to dB
            S_db = librosa.power_to_db(D**2, ref=np.max)

            # Normalize to 0-1
            S_db = (S_db - S_db.min()) / (S_db.max() - S_db.min() + 1e-9)

            # Return transposed (time x frequency)
            return S_db.T.tolist()

        except Exception as e:
            logger.error(f"Failed to get spectrogram: {e}")
            return None

    # ========================================================================
    # BATCH PROCESSING
    # ========================================================================

    def analyze_batch(self, file_paths: List[str]) -> int:
        """
        Batch analyze multiple samples.

        Args:
            file_paths: List of audio file paths

        Returns:
            Number of samples successfully analyzed
        """
        try:
            from samplemind.core.engine.audio_engine import AudioEngine

            engine = AudioEngine()
            success_count = 0

            for file_path in file_paths:
                try:
                    result = engine.analyze_full(file_path)
                    if result:
                        success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")

            logger.info(f"Batch analysis complete: {success_count}/{len(file_paths)}")
            return success_count

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return 0

    # ========================================================================
    # DRAG & DROP SUPPORT
    # ========================================================================

    def on_drag_over(self, x: int, y: int) -> bool:
        """
        Called when dragging over plugin.

        Args:
            x: Mouse X coordinate
            y: Mouse Y coordinate

        Returns:
            True if drop is allowed
        """
        # Allow drops everywhere in plugin window
        return True

    def on_drop(self, x: int, y: int, file_paths: List[str]) -> bool:
        """
        Called when files are dropped on plugin.

        Args:
            x: Drop X coordinate
            y: Drop Y coordinate
            file_paths: List of dropped file paths

        Returns:
            True if drop was handled
        """
        try:
            if len(file_paths) == 1:
                # Single file: analyze it
                return self.load_sample(file_paths[0])
            else:
                # Multiple files: batch analyze
                count = self.analyze_batch(file_paths)
                return count > 0

        except Exception as e:
            logger.error(f"Drop handler failed: {e}")
            return False

    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================

    def get_state(self) -> Dict[str, Any]:
        """Get plugin state for saving"""
        return {
            "current_sample": str(self.current_sample) if self.current_sample else None,
            "recent_samples": self.recent_samples,
            "cache_enabled": self.cache_enabled,
            "browser_visible": self.browser_visible,
            "analysis_visible": self.analysis_visible,
            "waveform_visible": self.waveform_visible,
        }

    def set_state(self, state: Dict[str, Any]) -> bool:
        """Restore plugin state"""
        try:
            if "current_sample" in state and state["current_sample"]:
                self.load_sample(state["current_sample"])

            self.recent_samples = state.get("recent_samples", [])
            self.cache_enabled = state.get("cache_enabled", True)
            self.browser_visible = state.get("browser_visible", True)
            self.analysis_visible = state.get("analysis_visible", True)
            self.waveform_visible = state.get("waveform_visible", True)

            return True
        except Exception as e:
            logger.error(f"Failed to restore state: {e}")
            return False

    def save_state(self) -> None:
        """Save plugin state to file"""
        try:
            import json
            state_file = Path.home() / ".samplemind" / "fl_studio_plugin_state.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(state_file, 'w') as f:
                json.dump(self.get_state(), f, indent=2)

            logger.info("Plugin state saved")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def load_state(self) -> None:
        """Load plugin state from file"""
        try:
            import json
            state_file = Path.home() / ".samplemind" / "fl_studio_plugin_state.json"

            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)
                self.set_state(state)
                logger.info("Plugin state loaded")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")

    # ========================================================================
    # INFORMATION
    # ========================================================================

    def get_info(self) -> Dict[str, str]:
        """Get plugin information"""
        return {
            "name": self.plugin_name,
            "version": self.plugin_version,
            "unique_id": hex(self.unique_id),
            "current_sample": str(self.current_sample) if self.current_sample else "None",
            "cache_size_mb": str(self.cache_size_mb),
            "recent_samples": str(len(self.recent_samples)),
        }

    def __str__(self) -> str:
        """String representation"""
        return f"{self.plugin_name} v{self.plugin_version} (FL Studio)"


# ============================================================================
# FL Studio Plugin Entry Point
# ============================================================================

# In production, this would be loaded by FL Studio's plugin loader
# The plugin would need to be compiled with FL Studio SDK

def create_plugin():
    """Factory function for plugin creation"""
    return FLStudioSampleMindPlugin()


if __name__ == "__main__":
    # For testing purposes
    plugin = create_plugin()
    print(f"Created: {plugin}")
    print(f"Info: {plugin.get_info()}")


__all__ = [
    "FLStudioSampleMindPlugin",
    "create_plugin",
]
