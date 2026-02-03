"""
VST3 Plugin Integration (Cross-Platform)

Provides VST3 plugin for universal DAW support:
- Windows, macOS, Linux support
- Sample analysis and metadata display
- Real-time AI suggestions
- Embedded web UI for configuration

VST3 requires C++ wrapper (JUCE or similar).
This module provides the Python logic layer.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from threading import Thread
import asyncio

logger = logging.getLogger(__name__)


class VST3ParameterID(Enum):
    """VST3 Parameter IDs"""

    ANALYSIS_MODE = 0  # 0=Quick, 1=Standard, 2=Detailed
    AUTO_SUGGESTIONS = 1
    WEB_UI_ENABLED = 2
    METADATA_DISPLAY = 3
    AI_PROVIDER = 4  # 0=Gemini, 1=Ollama, 2=OpenAI
    VERBOSE_LOGGING = 5


@dataclass
class VST3ProcessContext:
    """VST3 process context"""

    sample_rate: int = 44100
    block_size: int = 512
    tempo: float = 120.0
    time_signature_numerator: int = 4
    time_signature_denominator: int = 4
    is_playing: bool = False
    project_name: str = "Untitled"


@dataclass
class VST3SampleData:
    """VST3 sample data for display"""

    file_path: str
    duration: float
    bpm: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    energy: float = 0.5
    ai_tags: List[str] = None
    quality_score: float = 0.0

    def __post_init__(self) -> None:
        if self.ai_tags is None:
            self.ai_tags = []


class VST3Plugin:
    """VST3 Plugin Logic Layer (Cross-Platform)"""

    # Plugin metadata
    NAME = "SampleMind AI"
    VERSION = "2.1.0-beta"
    UID = "SampleMind VST3 2.1.0-beta"
    VENDOR = "SampleMind"
    VENDOR_URL = "https://samplemind.ai"
    VENDOR_EMAIL = "support@samplemind.ai"

    # VST3 compatibility
    PLUGIN_TYPE = "Analyzer"
    CATEGORIES = "Mastering Tool|Analyzer"  # VST3 category flags
    SUPPORTS_MONO = True
    SUPPORTS_STEREO = True
    SUPPORTS_SURROUND = False

    # Parameters
    PARAM_COUNT = 6
    PARAM_NAMES = {
        VST3ParameterID.ANALYSIS_MODE.value: "Analysis Mode",
        VST3ParameterID.AUTO_SUGGESTIONS.value: "Auto Suggestions",
        VST3ParameterID.WEB_UI_ENABLED.value: "Web UI Enabled",
        VST3ParameterID.METADATA_DISPLAY.value: "Metadata Display",
        VST3ParameterID.AI_PROVIDER.value: "AI Provider",
        VST3ParameterID.VERBOSE_LOGGING.value: "Verbose Logging",
    }

    def __init__(self) -> None:
        """Initialize VST3 plugin"""
        self.is_active = False
        self.process_context = VST3ProcessContext()
        self.parameters = {
            VST3ParameterID.ANALYSIS_MODE.value: 1,  # Standard
            VST3ParameterID.AUTO_SUGGESTIONS.value: 1.0,  # Enabled
            VST3ParameterID.WEB_UI_ENABLED.value: 1.0,  # Enabled
            VST3ParameterID.METADATA_DISPLAY.value: 1.0,  # Enabled
            VST3ParameterID.AI_PROVIDER.value: 0,  # Gemini
            VST3ParameterID.VERBOSE_LOGGING.value: 0.0,  # Disabled
        }
        self.loaded_samples: Dict[str, VST3SampleData] = {}
        self.suggestions_queue: List[str] = []
        self.analysis_thread: Optional[Thread] = None
        self.web_server_running = False
        self.web_server_port = 8765

        logger.info(f"VST3Plugin {self.VERSION} initialized")

    def vst_init(self) -> None:
        """Called when plugin initializes"""
        self.is_active = True
        logger.info("VST3 plugin initialized")

        # Start web UI if enabled
        if self.parameters[VST3ParameterID.WEB_UI_ENABLED.value] > 0.5:
            self._start_web_ui()

    def vst_process(self, context: VST3ProcessContext) -> None:
        """Called for each audio block (no-op for analyzer)"""
        self.process_context = context

    def vst_shutdown(self) -> None:
        """Called when plugin shuts down"""
        self.is_active = False

        if self.web_server_running:
            self._stop_web_ui()

        logger.info("VST3 plugin shutdown")

    def set_parameter(self, param_id: int, value: float) -> None:
        """Set VST3 parameter"""
        try:
            self.parameters[param_id] = value

            # Handle specific parameters
            if param_id == VST3ParameterID.WEB_UI_ENABLED.value:
                if value > 0.5:
                    self._start_web_ui()
                else:
                    self._stop_web_ui()

            elif param_id == VST3ParameterID.ANALYSIS_MODE.value:
                logger.debug(f"Analysis mode changed: {int(value)}")

            logger.debug(f"Parameter {param_id} set to {value}")

        except Exception as e:
            logger.error(f"Error setting parameter: {e}")

    def get_parameter(self, param_id: int) -> float:
        """Get VST3 parameter value"""
        return self.parameters.get(param_id, 0.0)

    def on_file_drop(self, file_path: str) -> None:
        """Handle file drop"""
        try:
            logger.info(f"File dropped: {file_path}")

            # Queue for analysis
            self.suggestions_queue.append(file_path)

            # Start analysis if not running
            if self.analysis_thread is None or not self.analysis_thread.is_alive():
                self.analysis_thread = Thread(target=self._analyze_queue)
                self.analysis_thread.daemon = True
                self.analysis_thread.start()

        except Exception as e:
            logger.error(f"Error handling file drop: {e}")

    def _analyze_queue(self) -> None:
        """Analyze queued samples"""
        try:
            while self.suggestions_queue:
                file_path = self.suggestions_queue.pop(0)
                self._analyze_sample(file_path)

        except Exception as e:
            logger.error(f"Error analyzing queue: {e}")

    def _analyze_sample(self, file_path: str) -> None:
        """Analyze audio sample"""
        try:
            from samplemind.core.engine import AudioEngine

            engine = AudioEngine()

            # Get analysis mode
            analysis_mode_val = int(self.parameters[VST3ParameterID.ANALYSIS_MODE.value])
            analysis_modes = ["QUICK", "STANDARD", "DETAILED"]
            analysis_mode = analysis_modes[min(analysis_mode_val, 2)]

            # Analyze
            result = engine.analyze_audio(file_path, analysis_level=analysis_mode)

            # Create sample data
            sample_data = VST3SampleData(
                file_path=file_path,
                duration=result.get("duration", 0),
                bpm=result.get("bpm"),
                key=result.get("key"),
                genre=result.get("genre"),
                mood=result.get("mood"),
                energy=result.get("energy", 0.5),
                quality_score=result.get("quality_score", 0.0),
            )

            # Get AI tags if auto-suggestions enabled
            if self.parameters[VST3ParameterID.AUTO_SUGGESTIONS.value] > 0.5:
                try:
                    from samplemind.integrations import SampleMindAIManager

                    ai = SampleMindAIManager()
                    ai_result = ai.analyze_music(
                        file_path, {"analysis_type": "classification"}
                    )
                    sample_data.ai_tags = ai_result.get("tags", [])
                except Exception as e:
                    logger.debug(f"Could not get AI tags: {e}")

            self.loaded_samples[file_path] = sample_data

            logger.info(
                f"Sample analyzed: {Path(file_path).name} - BPM: {sample_data.bpm}, Key: {sample_data.key}"
            )

            # Display metadata
            self._display_metadata(file_path, sample_data)

        except Exception as e:
            logger.error(f"Error analyzing sample: {e}")

    def _display_metadata(self, file_path: str, sample_data: VST3SampleData) -> None:
        """Display sample metadata"""
        try:
            if self.parameters[VST3ParameterID.METADATA_DISPLAY.value] > 0.5:
                # Create metadata display
                display = {
                    "file": Path(file_path).name,
                    "bpm": sample_data.bpm,
                    "key": sample_data.key,
                    "genre": sample_data.genre,
                    "mood": sample_data.mood,
                    "energy": f"{sample_data.energy:.0%}",
                    "quality": f"{sample_data.quality_score:.0f}%",
                    "tags": ", ".join(sample_data.ai_tags),
                    "project_tempo": f"{self.process_context.tempo:.1f} BPM",
                }

                logger.info(f"Metadata: {json.dumps(display, indent=2)}")

        except Exception as e:
            logger.error(f"Error displaying metadata: {e}")

    def _start_web_ui(self) -> None:
        """Start embedded web UI"""
        try:
            if self.web_server_running:
                return

            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading

            class WebUIHandler(BaseHTTPRequestHandler):
                """Simple web UI handler"""

                def do_GET(self) -> None:
                    """Handle GET requests"""
                    if self.path == "/":
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(self._get_html().encode())

                    elif self.path == "/api/samples":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()

                        samples_list = [
                            {
                                "file": Path(fp).name,
                                "data": asdict(data),
                            }
                            for fp, data in self.server.plugin.loaded_samples.items()
                        ]
                        self.wfile.write(json.dumps(samples_list).encode())

                    elif self.path == "/api/status":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()

                        status = {
                            "name": VST3Plugin.NAME,
                            "version": VST3Plugin.VERSION,
                            "active": self.server.plugin.is_active,
                            "samples": len(self.server.plugin.loaded_samples),
                            "tempo": self.server.plugin.process_context.tempo,
                        }
                        self.wfile.write(json.dumps(status).encode())

                def log_message(self, format: str, *args: Any) -> None:
                    """Suppress HTTP server logging"""
                    pass  # Suppress logging

                def _get_html(self) -> str:
                    return """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>SampleMind AI VST3</title>
                        <style>
                            body { font-family: Arial; margin: 20px; background: #1e1e1e; color: #fff; }
                            .header { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
                            .sample { background: #2d2d2d; padding: 10px; margin: 10px 0; border-radius: 5px; }
                            .param { margin: 10px 0; }
                            label { display: inline-block; width: 150px; }
                        </style>
                    </head>
                    <body>
                        <div class="header">🎵 SampleMind AI VST3 2.1.0-beta</div>
                        <div id="status"></div>
                        <div id="samples"></div>
                        <script>
                            async function updateStatus() {
                                const status = await fetch('/api/status').then(r => r.json());
                                document.getElementById('status').innerHTML =
                                    `<p>Active: ${status.active} | Samples: ${status.samples} | Tempo: ${status.tempo} BPM</p>`;
                            }

                            async function updateSamples() {
                                const samples = await fetch('/api/samples').then(r => r.json());
                                let html = '<div class="header" style="font-size:18px;">Loaded Samples</div>';
                                for (const s of samples) {
                                    html += `<div class="sample">
                                        <strong>${s.file}</strong><br>
                                        BPM: ${s.data.bpm} | Key: ${s.data.key} | Genre: ${s.data.genre}
                                    </div>`;
                                }
                                document.getElementById('samples').innerHTML = html;
                            }

                            updateStatus();
                            updateSamples();
                            setInterval(updateStatus, 1000);
                            setInterval(updateSamples, 2000);
                        </script>
                    </body>
                    </html>
                    """

            # Create and start server
            server = HTTPServer(("127.0.0.1", self.web_server_port), WebUIHandler)
            server.plugin = self

            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            self.web_server_running = True
            logger.info(f"Web UI started on http://127.0.0.1:{self.web_server_port}")

        except Exception as e:
            logger.error(f"Error starting web UI: {e}")

    def _stop_web_ui(self) -> None:
        """Stop embedded web UI"""
        self.web_server_running = False
        logger.info("Web UI stopped")

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "vendor": self.VENDOR,
            "type": self.PLUGIN_TYPE,
            "categories": self.CATEGORIES,
            "is_active": self.is_active,
            "samples_loaded": len(self.loaded_samples),
            "web_ui_enabled": self.web_server_running,
            "parameters": {
                self.PARAM_NAMES[k]: v for k, v in self.parameters.items()
            },
        }


# Global instance
_vst3_plugin: Optional[VST3Plugin] = None


def get_vst3_plugin() -> VST3Plugin:
    """Get or create global VST3 plugin instance"""
    global _vst3_plugin
    if _vst3_plugin is None:
        _vst3_plugin = VST3Plugin()
    return _vst3_plugin
