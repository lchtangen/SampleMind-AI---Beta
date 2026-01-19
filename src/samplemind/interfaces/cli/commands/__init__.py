"""
SampleMind AI - CLI Commands Package

Organized command groups for the Typer-based CLI system:
- analyze (40 commands) - Audio analysis & feature extraction
- library (50 commands) - Sample library management
- ai (30 commands) - AI-powered features
- metadata (30 commands) - Metadata operations
- audio (25 commands) - Audio processing & conversion
- visualization (15 commands) - Visualizations & charts
- reporting (10 commands) - Reports & data export

Total: 200+ commands - COMPLETE ✅
"""

__version__ = "2.1.0-beta"

# Import all command groups
from . import analyze
from . import library
from . import ai
from . import metadata
from . import audio
from . import visualization
from . import reporting

__all__ = [
    "analyze",          # 40 commands ✅
    "library",          # 50 commands ✅
    "ai",               # 30 commands ✅
    "metadata",         # 30 commands ✅
    "audio",            # 25 commands ✅
    "visualization",    # 15 commands ✅
    "reporting",        # 10 commands ✅
]
