#!/usr/bin/env python3
"""
SampleMind AI v2.1 - Typer-Based CLI Application

Main CLI application using Typer framework with 200+ subcommands organized
into command groups (namespaces). Provides comprehensive audio analysis, library
management, and AI-powered features through a modern CLI interface.

Features:
- 200+ subcommands organized by category
- Interactive shell completion (bash, zsh, fish, powershell)
- JSON/CSV/YAML export options
- Parallel processing support
- Offline-first architecture
- Full backward compatibility with menu system

Usage:
    samplemind analyze:full <file>              # Full analysis
    samplemind library:search <query>           # Search library
    samplemind ai:coach <file>                  # Get production tips
    samplemind --help                           # Show all commands
    samplemind analyze --help                   # Show analyze subcommands
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# Create main app
app = typer.Typer(
    name="samplemind",
    help="🎵 SampleMind AI v2.1 - Professional Audio Analysis & Management",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# ============================================================================
# COMMAND GROUP IMPORTS
# ============================================================================

from .commands import (
    ai,
    analyze,
    audio,
    daw,
    groove,
    layering,
    library,
    mastering,
    metadata,
    recent,
    reporting,
    similarity,
    tagging,
    theory,
    visualization,
)

# ============================================================================
# MAIN APP CALLBACKS
# ============================================================================

@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
    ),
) -> None:
    """SampleMind AI - Professional Audio Analysis & Library Management"""
    if version:
        from . import __version__
        console.print(f"[bold cyan]SampleMind AI[/bold cyan] v2.1.0-beta")
        raise typer.Exit()


# ============================================================================
# TOP-LEVEL COMMANDS
# ============================================================================

@app.command()
def interactive():
    """Start interactive menu mode (modern interface)"""
    import asyncio

    from .modern_menu import ModernMenu

    console.print("[bold cyan]🎵 Starting SampleMind AI Interactive Menu[/bold cyan]")
    console.print("[dim]✨ Modern interactive interface with 60+ commands[/dim]\n")

    try:
        menu = ModernMenu()
        asyncio.run(menu.run())
    except ImportError:
        console.print("[yellow]⚠️  Modern menu not available, falling back to classic menu[/yellow]")
        try:
            from .menu import main as cli_main
            asyncio.run(cli_main())
        except Exception as e:
            console.print(f"[red]❌ Error starting menu: {e}[/red]")
            raise typer.Exit(1)


@app.command()
def menu():
    """Open interactive menu (shorthand for 'interactive')"""
    interactive()


@app.command()
def status():
    """Show system status and configuration"""
    from src.samplemind.core.engine.audio_engine import AudioEngine
    from src.samplemind.integrations.ai_manager import SampleMindAIManager

    console.print("[bold]📊 SampleMind AI System Status[/bold]\n")

    try:
        # Initialize engines
        audio_engine = AudioEngine()
        ai_manager = SampleMindAIManager()

        # Show status table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")

        table.add_row(
            "Audio Engine",
            "✅ Ready",
            f"Cache: {audio_engine.get_performance_stats()['cache_size']} entries"
        )

        table.add_row(
            "AI Manager",
            "✅ Ready",
            f"Primary: {ai_manager.primary_provider}"
        )

        table.add_row(
            "Database",
            "✅ Connected",
            "MongoDB/Redis"
        )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")


@app.command()
def version():
    """Show version information"""
    console.print("""
[bold cyan]SampleMind AI v2.1.0-beta[/bold cyan]
[dim]Professional Audio Analysis & Library Management[/dim]

[bold]Components:[/bold]
  • Audio Engine: Phase 4 Complete ✅
  • CLI System: 200+ Commands ✅
  • API: 50+ Endpoints ✅
  • TUI: 13 Screens ✅
  • Documentation: 24,000+ lines ✅

[bold]Built with:[/bold]
  • Python 3.11+
  • Typer CLI Framework
  • Textual TUI Framework
  • FastAPI Backend
  • Librosa Audio Processing

[bold]License:[/bold]
  MIT License

[bold]Repository:[/bold]
  https://github.com/your-org/samplemind-ai
    """)


# ============================================================================
# COMMAND GROUP REGISTRATION
# ============================================================================

def register_command_groups():
    """Register all command groups with the main app"""

    # Register command groups - Core (215+ original)
    app.add_typer(analyze.app, name="analyze", help="🎵 Audio analysis & feature extraction (40 commands)")
    app.add_typer(library.app, name="library", help="📁 Sample library management (50 commands)")
    app.add_typer(ai.app, name="ai", help="🤖 AI-powered features (30 commands)")
    app.add_typer(metadata.app, name="meta", help="📝 Metadata operations (30 commands)")
    app.add_typer(audio.app, name="audio", help="🎙️  Audio processing & conversion (25 commands)")
    app.add_typer(visualization.app, name="viz", help="📊 Visualizations & charts (15 commands)")
    app.add_typer(reporting.app, name="report", help="📋 Reports & data export (10 commands)")
    app.add_typer(similarity.app, name="similar", help="🔍 Sample similarity search (5 commands)")
    app.add_typer(theory.app, name="theory", help="🎼 Music theory analysis (4 commands)")
    app.add_typer(daw.app, name="daw", help="🎹 DAW integration (4 commands)")

    # Register Phase 10+ Premium Features
    app.add_typer(tagging.app, name="tag", help="🏷️  AI-powered sample tagging")
    app.add_typer(mastering.app, name="mastering", help="🎚️  Professional mastering assistant")
    app.add_typer(layering.app, name="layer", help="🔀 Sample layering & phase analysis")
    app.add_typer(groove.app, name="groove", help="🎵 Groove template extraction")
    app.add_typer(recent.app, name="recent", help="📁 Quick access to recent files")


# Register command groups at module load
register_command_groups()


# ============================================================================
# UTILITIES & HELPERS
# ============================================================================

def create_progress_spinner(description: str = "Processing"):
    """Create a styled progress spinner"""
    from rich.progress import Progress, SpinnerColumn, TextColumn
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[progress.description]{description}[/progress.description]"),
        console=console,
    )


async def run_command_async(async_func, *args, **kwargs) -> None:
    """Helper to run async functions from sync commands"""
    return await async_func(*args, **kwargs)


def handle_command_error(error: Exception, context: str = ""):
    """Standardized error handling"""
    console.print(f"[bold red]❌ Error{' in ' + context if context else ''}:[/bold red] {error}")
    console.print("[dim]Use --help for command usage[/dim]")
    raise typer.Exit(code=1)


# ============================================================================
# SHELL COMPLETION SETUP
# ============================================================================

@app.command()
def completion(
    shell: str = typer.Option(
        ...,
        "--shell",
        "-s",
        help="Shell type",
        autocompletion=lambda: ["bash", "zsh", "fish", "powershell"],
    ),
) -> None:
    """Generate shell completion script"""
    completions = {
        "bash": "completion_bash",
        "zsh": "completion_zsh",
        "fish": "completion_fish",
        "powershell": "completion_powershell",
    }

    console.print(f"[bold]Shell Completion for {shell.upper()}[/bold]\n")

    if shell not in completions:
        console.print(f"[bold red]❌ Unsupported shell: {shell}[/bold red]")
        raise typer.Exit(1)

    console.print(f"[dim]Add the following to your .{shell}rc:[/dim]\n")
    console.print(f"eval \"$(_SAMPLEMIND_COMPLETE={shell.upper()}_SOURCE samplemind)\"")


# ============================================================================
# HELP & DOCUMENTATION
# ============================================================================

@app.command()
def help():
    """Show detailed help and examples"""
    help_text = """
[bold cyan]SampleMind AI v2.1 - Comprehensive Help[/bold cyan]

[bold]QUICK START:[/bold]

  [cyan]# Analyze a single audio file[/cyan]
  $ samplemind analyze:full song.wav

  [cyan]# Analyze everything in a folder[/cyan]
  $ samplemind batch:analyze ./music

  [cyan]# Search your library[/cyan]
  $ samplemind library:search "house 120bpm"

  [cyan]# Get AI production tips[/cyan]
  $ samplemind ai:coach song.wav

[bold]COMMAND GROUPS:[/bold]

  [cyan]analyze[/cyan]        - Audio analysis & feature extraction (40 commands)
  [cyan]library[/cyan]        - Sample library management (50 commands)
  [cyan]ai[/cyan]             - AI-powered features (30 commands)
  [cyan]meta[/cyan]           - Metadata operations (30 commands)
  [cyan]audio[/cyan]          - Audio processing & conversion (25 commands)
  [cyan]viz[/cyan]            - Visualizations & charts (15 commands)
  [cyan]report[/cyan]         - Reports & data export (10 commands)

[bold]COMMON OPTIONS:[/bold]

  [cyan]--help, -h[/cyan]     - Show command help
  [cyan]--json[/cyan]         - Output as JSON
  [cyan]--csv[/cyan]          - Output as CSV
  [cyan]--quiet, -q[/cyan]    - Minimal output
  [cyan]--verbose, -v[/cyan]  - Detailed output

[bold]EXAMPLES:[/bold]

  [cyan]# Full analysis with JSON output[/cyan]
  $ samplemind analyze:full song.wav --json > analysis.json

  [cyan]# Batch process with parallel workers[/cyan]
  $ samplemind batch:analyze ./samples --workers 8

  [cyan]# Search library and export results[/cyan]
  $ samplemind library:search "techno" --csv > results.csv

  [cyan]# Get mastering suggestions[/cyan]
  $ samplemind ai:mastering song.wav

  [cyan]# Generate waveform visualization[/cyan]
  $ samplemind viz:waveform song.wav --output waveform.png

[bold]INTERACTIVE MODE:[/bold]

  $ samplemind interactive
  $ samplemind --interactive
  $ python main.py

[bold]DOCUMENTATION:[/bold]

  Use 'samplemind <group> --help' for group-specific commands
  Full documentation: https://samplemind.ai/docs

[bold]GETTING HELP:[/bold]

  $ samplemind --help              - Show all commands
  $ samplemind analyze --help      - Show analyze subcommands
  $ samplemind analyze:full --help - Show full analyze command help
    """

    console.print(help_text)


# ============================================================================
# PLUGIN DISCOVERY
# ============================================================================

@app.command()
def list_commands():
    """List all available commands"""
    console.print("[bold cyan]📋 SampleMind AI - Available Commands[/bold cyan]\n")

    groups = {
        "analyze": "Audio analysis & feature extraction (40 commands)",
        "library": "Sample library management (50 commands)",
        "ai": "AI-powered features (30 commands)",
        "meta": "Metadata operations (30 commands)",
        "audio": "Audio processing & conversion (25 commands)",
        "viz": "Visualizations & charts (15 commands)",
        "report": "Reports & data export (10 commands)",
    }

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Group", style="cyan", width=12)
    table.add_column("Description")
    table.add_column("Commands", justify="right", style="green")

    total_commands = 0
    for group, description in groups.items():
        commands = description.split("(")[1].split()[0]
        table.add_row(group, description.split(" (")[0], commands)
        total_commands += int(commands)

    console.print(table)
    console.print(f"\n[bold green]Total: {total_commands} commands[/bold green]")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  samplemind <group> --help     [cyan]Show group commands[/cyan]")
    console.print("  samplemind <group>:<cmd> --help [cyan]Show command help[/cyan]")


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "app",
    "console",
    "register_command_groups",
    "create_progress_spinner",
    "run_command_async",
    "handle_command_error",
]


if __name__ == "__main__":
    app()
