"""
DAW Integration Module

Provides native integration with popular Digital Audio Workstations:
- FL Studio (Python plugin)
- Ableton Live (Control Surface)
- Logic Pro (Audio Unit plugin)
- VST3 (Cross-platform plugin)

Each integration provides:
- Real-time metadata sync
- Sample metadata display
- AI-powered suggestions
- BPM/Key sync with project

Phase 10 Additions:
- DAWBridge abstract interface for consistent APIs
- CLI commands for DAW interaction
"""

from .base import DAWBridge, DAWType, DAWProject, DAWChannel
from .fl_studio_plugin import FLStudioPlugin
from .ableton_integration import AbletonControlSurface
from .logic_pro_integration import LogicProAUPlugin
from .vst3_plugin import VST3Plugin

__all__ = [
    # Base classes
    "DAWBridge",
    "DAWType",
    "DAWProject",
    "DAWChannel",
    # DAW implementations
    "FLStudioPlugin",
    "AbletonControlSurface",
    "LogicProAUPlugin",
    "VST3Plugin",
]
