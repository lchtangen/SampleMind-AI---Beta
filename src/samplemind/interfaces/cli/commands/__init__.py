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
- similarity (5 commands) - Sample similarity search [Phase 10]
- theory (4 commands) - Music theory analysis [Phase 10]
- daw (4 commands) - DAW integration [Phase 10]

Total: 215+ commands - COMPLETE ✅
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
from . import similarity  # Phase 10: Sample Similarity Engine
from . import theory      # Phase 10: Music Theory Analysis
from . import daw         # Phase 10: DAW Integration
from . import tagging     # Phase 10: AI-powered Sample Tagging
from . import mastering   # Phase 10: Professional Mastering Assistant
from . import layering    # Phase 10: Sample Layering & Phase Analysis
from . import groove      # Phase 10: Groove Template Extraction
from . import recent      # Phase 10: Quick Access to Recent Files
from . import stems       # Phase 13: AI Stem Separation
from . import midi        # Phase 13: MIDI Extraction
from . import pack        # Phase 13: Sample Pack Creator
from . import effects     # Phase 13: Audio Effects & Presets

__all__ = [
    "analyze",          # 40 commands ✅
    "library",          # 50 commands ✅
    "ai",               # 30 commands ✅
    "metadata",         # 30 commands ✅
    "audio",            # 25 commands ✅
    "visualization",    # 15 commands ✅
    "reporting",        # 10 commands ✅
    "similarity",       # 5 commands ✅ (Phase 10)
    "theory",           # 4 commands ✅ (Phase 10)
    "daw",              # 4 commands ✅ (Phase 10)
    "tagging",          # AI-powered sample tagging ✅ (Phase 10)
    "mastering",        # Professional mastering ✅ (Phase 10)
    "layering",         # Sample layering ✅ (Phase 10)
    "groove",           # Groove extraction ✅ (Phase 10)
    "recent",           # Recent files ✅ (Phase 10)
    "stems",            # AI Stem Separation ✅ (Phase 13)
    "midi",             # MIDI Extraction ✅ (Phase 13)
    "pack",             # Sample Pack Creator ✅ (Phase 13)
    "effects",          # Audio Effects & Presets ✅ (Phase 13)
]
