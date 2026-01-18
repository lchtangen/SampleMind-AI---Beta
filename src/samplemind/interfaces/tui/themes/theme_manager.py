"""
Theme Management System for SampleMind TUI
Support for 8 built-in themes with customization
"""

import logging
from typing import Dict, Optional, Any, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ThemeName(Enum):
    """Available themes"""
    DARK = "dark"
    LIGHT = "light"
    CYBERPUNK = "cyberpunk"
    SYNTHWAVE = "synthwave"
    GRUVBOX = "gruvbox"
    DRACULA = "dracula"
    NORD = "nord"
    MONOKAI = "monokai"


@dataclass
class ThemeColors:
    """Color palette for a theme"""
    primary: str
    secondary: str
    accent: str
    surface: str
    background: str
    text: str
    success: str
    warning: str
    error: str
    info: str


# Dark Theme (Default) - Professional dark mode
THEME_DARK = ThemeColors(
    primary="#00D9FF",  # Cyan
    secondary="#0066CC",  # Blue
    accent="#00FF00",  # Green
    surface="#1A1A2E",  # Dark blue-grey
    background="#16213E",  # Darker blue
    text="#FFFFFF",  # White
    success="#00FF00",  # Green
    warning="#FFD700",  # Gold
    error="#FF0000",  # Red
    info="#00D9FF",  # Cyan
)

# Light Theme - Bright and accessible
THEME_LIGHT = ThemeColors(
    primary="#0066CC",  # Blue
    secondary="#FF6B35",  # Orange
    accent="#00A86B",  # Green
    surface="#FFFFFF",  # White
    background="#F5F5F5",  # Light grey
    text="#000000",  # Black
    success="#00A86B",  # Green
    warning="#FF9500",  # Orange
    error="#FF0000",  # Red
    info="#0066CC",  # Blue
)

# Cyberpunk Theme - Neon aesthetic
THEME_CYBERPUNK = ThemeColors(
    primary="#FF10F0",  # Hot pink
    secondary="#00FFFF",  # Cyan
    accent="#39FF14",  # Neon green
    surface="#0D0221",  # Very dark purple
    background="#03001E",  # Darker purple
    text="#FFFFFF",  # White
    success="#39FF14",  # Neon green
    warning="#FFD60A",  # Yellow
    error="#FF006E",  # Hot pink
    info="#00FFFF",  # Cyan
)

# Synthwave Theme - 80s retro
THEME_SYNTHWAVE = ThemeColors(
    primary="#FF006E",  # Pink
    secondary="#8338EC",  # Purple
    accent="#FFBE0B",  # Yellow
    surface="#1A0033",  # Dark purple
    background="#0D0015",  # Darker purple
    text="#FFD60A",  # Yellow text
    success="#3A86FF",  # Blue
    warning="#FB5607",  # Orange
    error="#FF006E",  # Pink
    info="#8338EC",  # Purple
)

# Gruvbox Theme - Warm retro
THEME_GRUVBOX = ThemeColors(
    primary="#D65C0B",  # Orange
    secondary="#B8860B",  # Dark goldenrod
    accent="#A89984",  # Neutral
    surface="#282828",  # Dark grey
    background="#1D2021",  # Darker grey
    text="#EBDBB2",  # Light beige
    success="#B8BB26",  # Green
    warning="#D79921",  # Orange
    error="#FB4934",  # Red
    info="#83A598",  # Blue
)

# Dracula Theme - Popular dark theme
THEME_DRACULA = ThemeColors(
    primary="#FF79C6",  # Pink
    secondary="#8BE9FD",  # Cyan
    accent="#50FA7B",  # Green
    surface="#282A36",  # Dark grey
    background="#21222C",  # Darker grey
    text="#F8F8F2",  # Off-white
    success="#50FA7B",  # Green
    warning="#FFB86C",  # Orange
    error="#FF5555",  # Red
    info="#8BE9FD",  # Cyan
)

# Nord Theme - Arctic, north-bluish color palette
THEME_NORD = ThemeColors(
    primary="#88C0D0",  # Light blue
    secondary="#81A1C1",  # Medium blue
    accent="#A3BE8C",  # Green
    surface="#2E3440",  # Polar night 1
    background="#3B4252",  # Polar night 2
    text="#ECEFF4",  # Snow storm 3
    success="#A3BE8C",  # Green
    warning="#EBCB8B",  # Yellow
    error="#BF616A",  # Red
    info="#88C0D0",  # Light blue
)

# Monokai Theme - Classic editor theme
THEME_MONOKAI = ThemeColors(
    primary="#66D9EF",  # Blue
    secondary="#AE81FF",  # Purple
    accent="#A1EFE4",  # Teal
    surface="#272822",  # Dark grey
    background="#1E1F1C",  # Darker grey
    text="#F8F8F2",  # Off-white
    success="#A6E22E",  # Green
    warning="#E6DB74",  # Yellow
    error="#F92672",  # Pink
    info="#66D9EF",  # Blue
)

# Theme registry
THEMES: Dict[ThemeName, ThemeColors] = {
    ThemeName.DARK: THEME_DARK,
    ThemeName.LIGHT: THEME_LIGHT,
    ThemeName.CYBERPUNK: THEME_CYBERPUNK,
    ThemeName.SYNTHWAVE: THEME_SYNTHWAVE,
    ThemeName.GRUVBOX: THEME_GRUVBOX,
    ThemeName.DRACULA: THEME_DRACULA,
    ThemeName.NORD: THEME_NORD,
    ThemeName.MONOKAI: THEME_MONOKAI,
}


class ThemeManager:
    """Manages application themes and color schemes"""

    def __init__(self, default_theme: ThemeName = ThemeName.DARK):
        """Initialize theme manager with default theme"""
        self.current_theme = default_theme
        self.current_colors = THEMES[default_theme]
        logger.info(f"Theme manager initialized with {default_theme.value} theme")

    def set_theme(self, theme_name: ThemeName) -> ThemeColors:
        """
        Set current theme

        Args:
            theme_name: Theme to activate

        Returns:
            ThemeColors for the new theme
        """
        if theme_name not in THEMES:
            logger.warning(f"Unknown theme: {theme_name.value}, keeping current")
            return self.current_colors

        self.current_theme = theme_name
        self.current_colors = THEMES[theme_name]
        logger.info(f"Theme changed to: {theme_name.value}")
        return self.current_colors

    def set_theme_by_name(self, theme_name: str) -> Optional[ThemeColors]:
        """Set theme by string name"""
        try:
            theme = ThemeName(theme_name.lower())
            return self.set_theme(theme)
        except ValueError:
            logger.warning(f"Invalid theme name: {theme_name}")
            return None

    def get_theme(self) -> ThemeColors:
        """Get current theme colors"""
        return self.current_colors

    def get_theme_name(self) -> str:
        """Get current theme name"""
        return self.current_theme.value

    def get_all_themes(self) -> List[str]:
        """Get list of all available themes"""
        return [t.value for t in ThemeName]

    def get_css(self) -> str:
        """Generate CSS/TCSS for current theme"""
        colors = self.current_colors
        css = f"""
/* SampleMind TUI - {self.current_theme.value.upper()} THEME */

Screen {{
    background: {colors.background};
    color: {colors.text};
}}

Header {{
    background: {colors.primary};
    color: {colors.background};
    text-style: bold;
}}

Footer {{
    background: {colors.primary};
    color: {colors.background};
}}

Button {{
    background: {colors.secondary};
    color: {colors.text};
}}

Button:hover {{
    background: {colors.primary};
    color: {colors.background};
}}

Button.success {{
    background: {colors.success};
    color: {colors.background};
}}

Button.warning {{
    background: {colors.warning};
    color: {colors.background};
}}

Button.error {{
    background: {colors.error};
    color: {colors.text};
}}

DataTable {{
    background: {colors.surface};
    color: {colors.text};
}}

Panel {{
    border: solid {colors.accent};
}}

Input {{
    background: {colors.surface};
    color: {colors.text};
    border: solid {colors.accent};
}}

Static {{
    background: {colors.surface};
    color: {colors.text};
}}
"""
        return css

    def get_color(self, name: str) -> str:
        """Get specific color from current theme"""
        color_map = {
            "primary": self.current_colors.primary,
            "secondary": self.current_colors.secondary,
            "accent": self.current_colors.accent,
            "surface": self.current_colors.surface,
            "background": self.current_colors.background,
            "text": self.current_colors.text,
            "success": self.current_colors.success,
            "warning": self.current_colors.warning,
            "error": self.current_colors.error,
            "info": self.current_colors.info,
        }
        return color_map.get(name, self.current_colors.text)

    def print_theme_info(self) -> str:
        """Print current theme information"""
        colors = self.current_colors
        lines = [
            "╔════════════════════════════════════════╗",
            f"║  THEME: {self.current_theme.value.upper():<30} ║",
            "╠════════════════════════════════════════╣",
            f"║ Primary:    {colors.primary:<29} ║",
            f"║ Secondary:  {colors.secondary:<29} ║",
            f"║ Accent:     {colors.accent:<29} ║",
            f"║ Surface:    {colors.surface:<29} ║",
            f"║ Background: {colors.background:<29} ║",
            f"║ Text:       {colors.text:<29} ║",
            f"║ Success:    {colors.success:<29} ║",
            f"║ Warning:    {colors.warning:<29} ║",
            f"║ Error:      {colors.error:<29} ║",
            f"║ Info:       {colors.info:<29} ║",
            "╚════════════════════════════════════════╝",
        ]
        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get theme statistics"""
        return {
            "current_theme": self.current_theme.value,
            "available_themes": self.get_all_themes(),
            "total_themes": len(THEMES),
        }


# Global singleton instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager(default_theme: ThemeName = ThemeName.DARK) -> ThemeManager:
    """Get or create theme manager singleton"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(default_theme)
    return _theme_manager
