#!/usr/bin/env python3
"""
SampleMind AI CLI Branding Module

Professional ASCII art branding, startup messages, and visual theming
for the SampleMind AI command-line interface.

Features:
- ASCII art logo with theme support
- Startup banner with version and tips
- Status messages with emoji and colors
- Motivational taglines
- System status display
"""

import random
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table

console = Console()

# ============================================================================
# ASCII ART LOGOS
# ============================================================================

ASCII_LOGO_MAIN = r"""
   ____                        __     __  __ _           __   ___    ____
  / __/__ ___ _  ___  ___ ___ /  |   /  |/  (_)__  ___  / /  / _ |  /  _/
 _\ \/ _ `/  ' \/ _ \/ -_)_ // / /  / /|_/ / / _ \/ _ \/ _ \/ __ | _/ /
/___/\_,_/_/_/_/ .__/\__/__//_/_/  /_/  /_/_/_//_/\__,_/_//_/_/ |_/___/
              /_/
"""

ASCII_LOGO_COMPACT = r"""
  ███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗███╗   ███╗██╗███╗   ██╗██████╗
  ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝████╗ ████║██║████╗  ██║██╔══██╗
  ███████╗███████║██╔████╔██║██████╔╝██║     █████╗  ██╔████╔██║██║██╔██╗ ██║██║  ██║
  ╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║
  ███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
"""

ASCII_LOGO_MINIMAL = r"""
  ╔═══════════════════════════════════════════════════════════╗
  ║                    🎵 SAMPLEMIND AI 🎵                   ║
  ║         Professional Audio Intelligence Platform         ║
  ╚═══════════════════════════════════════════════════════════╝
"""

# ============================================================================
# STARTUP TIPS & TAGLINES
# ============================================================================

STARTUP_TIPS = [
    "💡 Use [cyan]--interactive[/cyan] flag for GUI file selection",
    "💡 Try [cyan]samplemind recent[/cyan] to access recently analyzed files",
    "💡 Use [cyan]--help[/cyan] flag for detailed command information",
    "💡 Run [cyan]samplemind tag:auto[/cyan] to auto-generate tags for samples",
    "💡 Check [cyan]samplemind mastering:analyze[/cyan] for loudness analysis",
    "💡 Use [cyan]--json[/cyan] flag to export results in JSON format",
    "💡 Try [cyan]samplemind layer:analyze[/cyan] for phase-aligned layering",
    "💡 Extract grooves with [cyan]samplemind groove:extract[/cyan]",
    "💡 Enable notifications for batch operations: [cyan]--notify[/cyan]",
    "💡 Access command history with arrow keys (↑/↓)",
    "💡 Use [cyan]samplemind similar:find[/cyan] to find related samples",
    "💡 Create favorites with [cyan]samplemind fav:add[/cyan]",
    "💡 Save sessions: [cyan]samplemind session:save[/cyan]",
    "💡 Check health: [cyan]samplemind health:check[/cyan]",
]

TAGLINES = [
    "Professional Audio Intelligence",
    "AI-Powered Music Production",
    "Intelligent Sample Discovery",
    "Creative Audio Analysis",
    "Next-Generation Production Tool",
    "Your AI Audio Assistant",
    "Powered by Neural Audio Processing",
    "Smart Sample Library Management",
]

# ============================================================================
# STATUS INDICATORS & MESSAGES
# ============================================================================

WELCOME_MESSAGE = """
[bold cyan]Welcome to SampleMind AI[/bold cyan]
[dim]Professional AI-powered music production platform[/dim]

[bold]Quick Start:[/bold]
  [cyan]samplemind analyze:full[/cyan] <file>       Analyze audio file
  [cyan]samplemind interactive[/cyan]              Interactive menu
  [cyan]samplemind --help[/cyan]                   Show all commands

[bold]Documentation:[/bold]
  Use [cyan]--help[/cyan] flag for detailed command information
  Full docs: https://samplemind.ai/docs
"""

# ============================================================================
# BANNER GENERATION
# ============================================================================

def get_version() -> str:
    """Get current version from package"""
    try:
        from samplemind import __version__
        return __version__
    except:
        return "v2.2.0-beta"


def print_startup_banner(
    show_tips: bool = True,
    show_welcome: bool = False,
    compact: bool = False
) -> None:
    """
    Print professional startup banner

    Args:
        show_tips: Display startup tip
        show_welcome: Show welcome message
        compact: Use compact ASCII art
    """
    # Clear screen effect
    console.print()

    # ASCII Logo
    if compact:
        logo = ASCII_LOGO_MINIMAL
    else:
        logo = ASCII_LOGO_MAIN

    # Color the logo
    logo_text = Text(logo, style="bold cyan")
    console.print(logo_text)

    # Version and tagline
    version = get_version()
    tagline = random.choice(TAGLINES)

    version_text = f"[bold cyan]SampleMind AI {version}[/bold cyan] [dim]|[/dim] {tagline}"
    console.print(Align.center(version_text))

    # Separator
    console.print(Align.center("[dim]" + "═" * 70 + "[/dim]"))
    console.print()

    # Random tip
    if show_tips:
        tip = random.choice(STARTUP_TIPS)
        console.print(Align.center(f"[yellow]{tip}[/yellow]"))
        console.print()

    # Welcome message
    if show_welcome:
        console.print(WELCOME_MESSAGE)
        console.print()


def print_success_banner(message: str, icon: str = "✅") -> None:
    """Print success message with banner styling"""
    console.print()
    success_text = f"{icon} [bold green]{message}[/bold green]"
    console.print(Align.center(success_text))
    console.print()


def print_warning_banner(message: str, icon: str = "⚠️") -> None:
    """Print warning message with banner styling"""
    console.print()
    warning_text = f"{icon} [bold yellow]{message}[/bold yellow]"
    console.print(Align.center(warning_text))
    console.print()


def print_error_banner(message: str, icon: str = "❌") -> None:
    """Print error message with banner styling"""
    console.print()
    error_text = f"{icon} [bold red]{message}[/bold red]"
    console.print(Align.center(error_text))
    console.print()


# ============================================================================
# SYSTEM STATUS DISPLAY
# ============================================================================

def print_system_status(
    audio_engine_ready: bool = True,
    ai_manager_ready: bool = True,
    database_ready: bool = True,
    cache_size: int = 0,
    primary_provider: str = "Google Gemini"
) -> None:
    """
    Print system status table

    Args:
        audio_engine_ready: Audio engine status
        ai_manager_ready: AI manager status
        database_ready: Database status
        cache_size: Number of cached items
        primary_provider: Primary AI provider
    """
    console.print()
    console.print("[bold]📊 System Status:[/bold]")

    status_table = Table(show_header=True, header_style="bold cyan", show_lines=False)
    status_table.add_column("Component", style="cyan", width=20)
    status_table.add_column("Status", width=12)
    status_table.add_column("Details")

    # Audio Engine
    ae_status = "✅ Ready" if audio_engine_ready else "❌ Error"
    status_table.add_row("Audio Engine", ae_status, f"Cache: {cache_size} items")

    # AI Manager
    ai_status = "✅ Ready" if ai_manager_ready else "❌ Error"
    status_table.add_row("AI Manager", ai_status, f"Provider: {primary_provider}")

    # Database
    db_status = "✅ Connected" if database_ready else "❌ Offline"
    status_table.add_row("Database", db_status, "MongoDB/ChromaDB")

    console.print(status_table)
    console.print()


# ============================================================================
# THEMED PANELS
# ============================================================================

def create_info_panel(
    title: str,
    content: str,
    icon: str = "ℹ️"
) -> Panel:
    """Create an info panel with content"""
    panel_content = f"{icon} [bold cyan]{content}[/bold cyan]"
    return Panel(
        panel_content,
        title=title,
        border_style="cyan",
        expand=False
    )


def create_success_panel(
    title: str,
    content: str,
    icon: str = "✅"
) -> Panel:
    """Create a success panel"""
    panel_content = f"{icon} [bold green]{content}[/bold green]"
    return Panel(
        panel_content,
        title=title,
        border_style="green",
        expand=False
    )


def create_warning_panel(
    title: str,
    content: str,
    icon: str = "⚠️"
) -> Panel:
    """Create a warning panel"""
    panel_content = f"{icon} [bold yellow]{content}[/bold yellow]"
    return Panel(
        panel_content,
        title=title,
        border_style="yellow",
        expand=False
    )


def create_error_panel(
    title: str,
    content: str,
    icon: str = "❌"
) -> Panel:
    """Create an error panel"""
    panel_content = f"{icon} [bold red]{content}[/bold red]"
    return Panel(
        panel_content,
        title=title,
        border_style="red",
        expand=False
    )


# ============================================================================
# FEATURE SHOWCASE
# ============================================================================

def print_feature_highlights() -> None:
    """Print available premium features"""
    console.print()
    console.print("[bold cyan]✨ Premium Features Available:[/bold cyan]")
    console.print()

    features_table = Table(show_header=False, show_lines=False)
    features_table.add_column(width=3)  # Icon
    features_table.add_column()  # Feature name
    features_table.add_column(width=50)  # Description

    features = [
        ("🎵", "[cyan]AI Sample Tagging[/cyan]", "Auto-generate descriptive tags for samples"),
        ("🎚️", "[cyan]Mastering Assistant[/cyan]", "LUFS analysis with platform-specific targets"),
        ("🔀", "[cyan]Intelligent Layering[/cyan]", "Phase-aligned sample stacking analysis"),
        ("🎶", "[cyan]Groove Extraction[/cyan]", "Capture and apply groove feel from samples"),
        ("📁", "[cyan]Interactive File Picker[/cyan]", "Native GUI file selection (all platforms)"),
        ("📊", "[cyan]Recent Files[/cyan]", "Quick access to recently analyzed files"),
        ("⭐", "[cyan]Favorites System[/cyan]", "Organize samples into collections"),
        ("💾", "[cyan]Session Management[/cyan]", "Save and resume analysis sessions"),
    ]

    for icon, name, desc in features:
        features_table.add_row(icon, name, desc)

    console.print(features_table)
    console.print()


# ============================================================================
# COMMAND SUGGESTIONS
# ============================================================================

def print_command_suggestions(
    last_command: Optional[str] = None,
    context: Optional[str] = None
) -> None:
    """
    Print contextual command suggestions

    Args:
        last_command: Last command executed
        context: Current context (file analyzed, search performed, etc.)
    """
    console.print()
    console.print("[bold cyan]💡 Smart Suggestions:[/bold cyan]")

    suggestions = []

    if context and "analyzed" in context.lower():
        suggestions.append(("[cyan]samplemind similar:find[/cyan]", "Find similar samples"))
        suggestions.append(("[cyan]samplemind report:json[/cyan]", "Export as JSON"))
        suggestions.append(("[cyan]samplemind ai:coach[/cyan]", "Get production tips"))

    if context and "tag" in context.lower():
        suggestions.append(("[cyan]samplemind library:search --tags[/cyan]", "Search by tags"))
        suggestions.append(("[cyan]samplemind fav:add[/cyan]", "Add to favorites"))

    if not suggestions:
        suggestions = [
            ("[cyan]samplemind analyze:full[/cyan]", "Analyze audio file"),
            ("[cyan]samplemind library:search[/cyan]", "Search sample library"),
            ("[cyan]samplemind recent[/cyan]", "Access recent files"),
        ]

    for cmd, desc in suggestions[:3]:  # Show top 3
        console.print(f"  • {cmd:<40} {desc}")

    console.print()


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "print_startup_banner",
    "print_success_banner",
    "print_warning_banner",
    "print_error_banner",
    "print_system_status",
    "create_info_panel",
    "create_success_panel",
    "create_warning_panel",
    "create_error_panel",
    "print_feature_highlights",
    "print_command_suggestions",
    "get_version",
]


if __name__ == "__main__":
    # Demo the branding module
    print_startup_banner(show_tips=True, show_welcome=True)
    print_system_status()
    print_feature_highlights()
    print_command_suggestions(context="file_analyzed")
    print_success_banner("All features initialized successfully!")
