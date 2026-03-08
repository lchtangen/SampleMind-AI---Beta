"""TUI Widget exports for SampleMind v3.0"""

from .ai_coach_widget import AICoachWidget
from .dialogs import (
    ConfirmDialog,
    ErrorDialog,
    InfoDialog,
    LoadingDialog,
    ProgressDialog,
    WarningDialog,
)
from .menu import MainMenu, MainMenuOption, MenuSelected
from .spectral_viz import SpectralType, SpectralViz
from .status_bar import StatusBar
from .waveform import WaveformWidget
from .sample_card import SampleCard
from .bpm_wheel import BPMWheel
from .progress_ring import ProgressRing
from .keyboard_shortcut import KeyboardShortcut, KeyboardShortcutBar

__all__ = [
    "AICoachWidget",
    "BPMWheel",
    "ConfirmDialog",
    "ErrorDialog",
    "InfoDialog",
    "KeyboardShortcut",
    "KeyboardShortcutBar",
    "LoadingDialog",
    "MainMenu",
    "MainMenuOption",
    "MenuSelected",
    "ProgressDialog",
    "ProgressRing",
    "SampleCard",
    "SpectralType",
    "SpectralViz",
    "StatusBar",
    "WarningDialog",
    "WaveformWidget",
]
