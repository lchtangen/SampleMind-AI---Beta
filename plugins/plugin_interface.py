"""
Base Plugin Interface & Architecture (Phase 13.2)

Foundation for all SampleMind DAW plugins:
- Parameter management
- Audio processing interface
- Preset system
- Plugin lifecycle
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class ParameterType(str, Enum):
    """Parameter data types"""
    FLOAT = "float"           # Float parameter (0-1)
    INT = "int"               # Integer parameter
    BOOL = "bool"             # Boolean parameter
    STRING = "string"         # String parameter
    CHOICE = "choice"         # Enumerated choice
    FILE = "file"             # File path


@dataclass
class Parameter:
    """Plugin parameter definition"""
    name: str                          # Parameter name
    param_type: ParameterType          # Parameter type
    default_value: Any                 # Default value
    min_value: Optional[float] = None  # Minimum (for numeric)
    max_value: Optional[float] = None  # Maximum (for numeric)
    choices: List[str] = field(default_factory=list)  # Choices (for choice type)
    label: str = ""                    # Display label
    description: str = ""              # Parameter description
    automation_enabled: bool = True    # Allow automation
    current_value: Any = None          # Current value

    def __post_init__(self):
        if self.current_value is None:
            self.current_value = self.default_value

    def set_value(self, value: Any) -> bool:
        """Set parameter value with bounds checking"""
        try:
            if self.param_type == ParameterType.FLOAT:
                value = float(value)
                if self.min_value is not None:
                    value = max(value, self.min_value)
                if self.max_value is not None:
                    value = min(value, self.max_value)
            elif self.param_type == ParameterType.INT:
                value = int(value)
                if self.min_value is not None:
                    value = max(value, int(self.min_value))
                if self.max_value is not None:
                    value = min(value, int(self.max_value))
            elif self.param_type == ParameterType.CHOICE:
                if value not in self.choices:
                    return False

            self.current_value = value
            return True
        except (ValueError, TypeError):
            return False

    def get_normalized_value(self) -> float:
        """Get parameter as normalized 0-1 value"""
        if self.param_type in (ParameterType.FLOAT, ParameterType.INT):
            if self.min_value is None or self.max_value is None:
                return 0.5
            range_val = self.max_value - self.min_value
            return (self.current_value - self.min_value) / range_val
        return 0.0


@dataclass
class Preset:
    """Plugin preset"""
    name: str
    description: str = ""
    author: str = "Unknown"
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_date: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "parameters": self.parameters,
            "created_date": self.created_date,
            "tags": self.tags
        }


class AudioBuffer:
    """Audio buffer wrapper"""

    def __init__(self, num_samples: int, num_channels: int, sample_rate: int):
        """Initialize audio buffer"""
        import numpy as np
        self.data = np.zeros((num_channels, num_samples), dtype=np.float32)
        self.num_samples = num_samples
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self.is_silent = True

    def get_channel(self, channel: int) -> 'np.ndarray':
        """Get audio data for a channel"""
        return self.data[channel]

    def set_silent(self) -> None:
        """Mark buffer as silent"""
        self.is_silent = True
        self.data.fill(0.0)

    def apply_gain(self, gain_db: float) -> None:
        """Apply gain to entire buffer"""
        import numpy as np
        gain_linear = 10 ** (gain_db / 20.0)
        self.data *= gain_linear


class SampleMindPlugin(ABC):
    """
    Base plugin interface for all SampleMind plugins.

    All DAW plugins (FL Studio, Ableton, VST, AU) inherit from this class.
    """

    def __init__(
        self,
        plugin_name: str,
        plugin_version: str = "1.0.0",
        unique_id: int = 0,
    ):
        """Initialize plugin"""
        self.plugin_name = plugin_name
        self.plugin_version = plugin_version
        self.unique_id = unique_id

        # Plugin state
        self.is_initialized = False
        self.is_playing = False
        self.sample_rate = 44100
        self.block_size = 512

        # Parameters
        self.parameters: Dict[str, Parameter] = {}
        self.presets: Dict[str, Preset] = {}
        self.current_preset: Optional[Preset] = None

        # Callbacks
        self.param_changed_callbacks: List[Callable[[str, Any], None]] = []
        self.preset_changed_callbacks: List[Callable[[str], None]] = []

        logger.info(f"Initialized plugin: {plugin_name} v{plugin_version}")

    # ========================================================================
    # PLUGIN LIFECYCLE
    # ========================================================================

    def initialize(self, sample_rate: int, block_size: int) -> bool:
        """
        Initialize plugin with DAW settings.

        Args:
            sample_rate: Sample rate in Hz
            block_size: Audio block size in samples

        Returns:
            True if successful
        """
        try:
            self.sample_rate = sample_rate
            self.block_size = block_size
            self.is_initialized = True
            logger.info(f"Plugin initialized: {sample_rate}Hz, {block_size} samples")
            return True
        except Exception as e:
            logger.error(f"Plugin initialization failed: {e}")
            return False

    def shutdown(self) -> None:
        """Shutdown plugin and cleanup resources"""
        self.is_initialized = False
        logger.info("Plugin shutdown")

    def reset(self) -> None:
        """Reset plugin state"""
        for param in self.parameters.values():
            param.current_value = param.default_value

    # ========================================================================
    # PARAMETER MANAGEMENT
    # ========================================================================

    def add_parameter(
        self,
        param_id: str,
        parameter: Parameter,
    ) -> None:
        """Register a parameter"""
        self.parameters[param_id] = parameter
        logger.debug(f"Added parameter: {param_id}")

    def set_parameter(self, param_id: str, value: Any) -> bool:
        """Set parameter value"""
        if param_id not in self.parameters:
            logger.warning(f"Parameter not found: {param_id}")
            return False

        param = self.parameters[param_id]
        if param.set_value(value):
            # Trigger callbacks
            for callback in self.param_changed_callbacks:
                callback(param_id, param.current_value)
            return True
        return False

    def get_parameter(self, param_id: str) -> Optional[Any]:
        """Get parameter value"""
        if param_id in self.parameters:
            return self.parameters[param_id].current_value
        return None

    def get_parameter_normalized(self, param_id: str) -> float:
        """Get parameter as normalized 0-1 value"""
        if param_id in self.parameters:
            return self.parameters[param_id].get_normalized_value()
        return 0.0

    def on_parameter_changed(self, callback: Callable[[str, Any], None]) -> None:
        """Register parameter changed callback"""
        self.param_changed_callbacks.append(callback)

    # ========================================================================
    # PRESET MANAGEMENT
    # ========================================================================

    def add_preset(self, preset: Preset) -> None:
        """Register a preset"""
        self.presets[preset.name] = preset
        logger.info(f"Added preset: {preset.name}")

    def load_preset(self, preset_name: str) -> bool:
        """Load a preset"""
        if preset_name not in self.presets:
            logger.warning(f"Preset not found: {preset_name}")
            return False

        preset = self.presets[preset_name]
        for param_id, value in preset.parameters.items():
            self.set_parameter(param_id, value)

        self.current_preset = preset

        # Trigger callbacks
        for callback in self.preset_changed_callbacks:
            callback(preset_name)

        logger.info(f"Loaded preset: {preset_name}")
        return True

    def save_preset(self, preset_name: str, description: str = "") -> bool:
        """Save current state as preset"""
        params_dict = {
            param_id: param.current_value
            for param_id, param in self.parameters.items()
        }

        preset = Preset(
            name=preset_name,
            description=description,
            parameters=params_dict
        )

        self.add_preset(preset)
        return True

    def on_preset_changed(self, callback: Callable[[str], None]) -> None:
        """Register preset changed callback"""
        self.preset_changed_callbacks.append(callback)

    # ========================================================================
    # AUDIO PROCESSING
    # ========================================================================

    @abstractmethod
    def process_audio(self, input_buffer: AudioBuffer, output_buffer: AudioBuffer) -> None:
        """
        Process audio samples.

        Args:
            input_buffer: Input audio
            output_buffer: Output audio
        """
        pass

    def process_block(
        self,
        input_data: List[List[float]],
        output_data: List[List[float]],
    ) -> None:
        """
        Process audio block (called by DAW).

        Args:
            input_data: Input samples [[ch0_samples...], [ch1_samples...]]
            output_data: Output samples
        """
        if not self.is_initialized:
            return

        # Create buffers
        num_channels = len(input_data)
        num_samples = len(input_data[0]) if input_data else 0

        input_buffer = AudioBuffer(num_samples, num_channels, self.sample_rate)
        import numpy as np
        for ch in range(num_channels):
            input_buffer.data[ch] = np.array(input_data[ch], dtype=np.float32)

        output_buffer = AudioBuffer(num_samples, num_channels, self.sample_rate)

        # Process
        self.process_audio(input_buffer, output_buffer)

        # Copy to output
        for ch in range(num_channels):
            output_data[ch][:] = output_buffer.data[ch].tolist()

    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================

    def get_state(self) -> Dict[str, Any]:
        """Get plugin state for saving"""
        return {
            "parameters": {
                param_id: param.current_value
                for param_id, param in self.parameters.items()
            },
            "current_preset": self.current_preset.name if self.current_preset else None
        }

    def set_state(self, state: Dict[str, Any]) -> bool:
        """Restore plugin state"""
        try:
            if "parameters" in state:
                for param_id, value in state["parameters"].items():
                    self.set_parameter(param_id, value)

            if "current_preset" in state and state["current_preset"]:
                self.load_preset(state["current_preset"])

            return True
        except Exception as e:
            logger.error(f"Failed to restore state: {e}")
            return False

    # ========================================================================
    # INFORMATION
    # ========================================================================

    def get_info(self) -> Dict[str, str]:
        """Get plugin information"""
        return {
            "name": self.plugin_name,
            "version": self.plugin_version,
            "unique_id": str(self.unique_id),
            "sample_rate": str(self.sample_rate),
            "block_size": str(self.block_size),
            "parameters": str(len(self.parameters)),
            "presets": str(len(self.presets)),
        }

    def __str__(self) -> str:
        """String representation"""
        return f"{self.plugin_name} v{self.plugin_version}"


__all__ = [
    "SampleMindPlugin",
    "Parameter",
    "ParameterType",
    "Preset",
    "AudioBuffer",
]
