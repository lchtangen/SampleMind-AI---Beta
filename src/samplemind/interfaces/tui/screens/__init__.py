"""TUI Screens - Individual application screens for Textual ^0.87"""

from .ai_chat_screen import AIChatScreen
from .analyze_screen import AnalyzeScreen
from .batch_screen import BatchScreen
from .chain_screen import ChainScreen
from .classification_screen import ClassificationScreen
from .comparison_screen import ComparisonScreen
from .favorites_screen import FavoritesScreen
from .library_screen import LibraryScreen
from .main_screen import MainScreen
from .performance_screen import PerformanceScreen
from .results_screen import ResultsScreen
from .search_screen import SearchScreen
from .settings_screen import SettingsScreen
from .tagging_screen import TaggingScreen
from .visualizer_screen import VisualizerScreen

__all__ = [
    "MainScreen",
    "AnalyzeScreen",
    "BatchScreen",
    "ResultsScreen",
    "FavoritesScreen",
    "SettingsScreen",
    "ComparisonScreen",
    "SearchScreen",
    "TaggingScreen",
    "PerformanceScreen",
    "LibraryScreen",
    "ChainScreen",
    "ClassificationScreen",
    "AIChatScreen",
    "VisualizerScreen",
]
