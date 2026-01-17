"""
AI Coach Sidebar Widget for SampleMind TUI
Displays real-time coaching tips and suggestions
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container, Vertical, Horizontal
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

from samplemind.interfaces.tui.ai import (
    AICoach,
    GenreType,
    ProductionTipCategory,
    get_ai_coach,
)

logger = logging.getLogger(__name__)


class AICoachWidget(Static):
    """Real-time AI coaching sidebar widget"""

    def __init__(
        self,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        collapsed: bool = False,
    ):
        super().__init__(id=id, classes=classes)
        self.coach = get_ai_coach()
        self.collapsed = collapsed
        self.current_context: Dict[str, Any] = {
            "analyzed_count": 0,
            "current_genre": GenreType.UNKNOWN,
            "user_level": "beginner",
        }
        self.last_tip_update = datetime.now()
        self.current_tips: List[str] = []
        self.current_pairings: List[Dict[str, Any]] = []

    def render(self) -> str:
        """Render the AI coach widget"""
        if self.collapsed:
            return "💭 AI Coach (collapsed)"

        lines = ["╔════════════════════════════════════╗", "║          🧠 AI COACH                ║", "╠════════════════════════════════════╣"]

        # Current context info
        context_line = f"║ Genre: {self.current_context['current_genre'].value:<27} ║"
        lines.append(context_line)

        # Divider
        lines.append("╠════════════════════════════════════╣")

        # Tips section
        tips = self.current_tips
        if not tips:
            tips = self._generate_tips()
            self.current_tips = tips

        if tips:
            lines.append("║  💡 PRODUCTION TIPS:                ║")
            for tip in tips[:2]:  # Show top 2 tips
                wrapped = self._wrap_text(tip, 34)
                for line in wrapped:
                    lines.append(f"║  {line:<34} ║")
        else:
            lines.append("║  No tips available right now        ║")

        # Divider
        lines.append("╠════════════════════════════════════╣")

        # Pairings section
        if self.current_pairings:
            lines.append("║  🎵 SAMPLE PAIRINGS:                ║")
            for pairing in self.current_pairings[:2]:
                wrapped = self._wrap_text(pairing, 34)
                for line in wrapped:
                    lines.append(f"║  {line:<34} ║")
        else:
            lines.append("║  Analyze samples to get pairing     ║")
            lines.append("║  suggestions                        ║")

        # Footer
        lines.append("╠════════════════════════════════════╣")
        lines.append("║  [P] Tips | [K] Genre | [T] Toggle ║")
        lines.append("╚════════════════════════════════════╝")

        return "\n".join(lines)

    def update_context(self, context: Dict[str, Any]) -> None:
        """
        Update coaching context

        Args:
            context: Context dictionary with analyzed_count, current_genre, user_level
        """
        self.current_context.update(context)
        self.current_tips = self._generate_tips()
        self.refresh()

    def update_pairings(self, pairings: List[Dict[str, Any]]) -> None:
        """
        Update sample pairing suggestions

        Args:
            pairings: List of pairing dictionaries
        """
        self.current_pairings = [
            self.coach.format_pairing_suggestion(pairing) if hasattr(pairing, "sample_name") else str(pairing)
            for pairing in pairings
        ]
        self.refresh()

    def toggle_collapse(self) -> None:
        """Toggle between collapsed and expanded state"""
        self.collapsed = not self.collapsed
        self.refresh()

    def _generate_tips(self) -> List[str]:
        """Generate fresh tips for current context"""
        genre = self.current_context.get("current_genre", GenreType.UNKNOWN)
        difficulty = 2 if self.current_context.get("user_level") == "beginner" else 3

        # Get production tips
        tips_objs = self.coach.get_production_tips(
            genre=genre,
            difficulty_level=difficulty,
            limit=2,
        )
        tips = [f"• {tip.title}: {tip.description}" for tip in tips_objs]

        # Add context tips
        context_tips = self.coach.get_context_tips(self.current_context, limit=1)
        tips.extend(context_tips)

        return tips

    def _wrap_text(self, text: str, width: int = 34) -> List[str]:
        """
        Wrap text to specified width

        Args:
            text: Text to wrap
            width: Maximum line width

        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines if lines else [text[:width]]


class AICoachPanel(Static):
    """Collapsible AI Coach panel for main screens"""

    DEFAULT_CSS = """
    AICoachPanel {
        width: 38;
        height: 100%;
        border: solid $primary;
        background: $surface;
    }

    AICoachPanel > Static {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self):
        super().__init__()
        self.coach_widget = AICoachWidget()

    def compose(self):
        """Compose the panel"""
        yield self.coach_widget

    def update_context(self, context: Dict[str, Any]) -> None:
        """Update context"""
        self.coach_widget.update_context(context)

    def update_pairings(self, pairings: List[Dict[str, Any]]) -> None:
        """Update pairings"""
        self.coach_widget.update_pairings(pairings)
