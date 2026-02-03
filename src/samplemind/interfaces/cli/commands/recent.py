#!/usr/bin/env python3
"""
Recent Files Command Group

Provides quick access to recently analyzed audio files.

Usage:
    samplemind recent                   # List recent files
    samplemind recent:search <query>    # Search recent files
    samplemind recent:clear             # Clear history
    samplemind recent:export            # Export as JSON
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from samplemind.core.history.recent_files import (
    get_recent_files,
    get_recent_file_by_index,
    search_recent_files,
    export_recent_files,
    get_recent_files_stats,
    get_manager,
)

from . import utils

# Create recent app group
app = typer.Typer(
    help="📁 Quick access to recent files",
    no_args_is_help=True,
)

console = Console()


# ============================================================================
# MAIN RECENT FILES LIST COMMAND
# ============================================================================

@app.command()
@utils.with_error_handling
def list_recent(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of files to show"),
    show_stats: bool = typer.Option(False, "--stats", "-s", help="Show statistics"),
):
    """List recently analyzed audio files"""
    files = get_recent_files()

    if not files:
        console.print("[yellow]📭 No recent files. Try analyzing something first![/yellow]")
        return

    # Show recent files table
    console.print()
    console.print("[bold]📁 Recent Files[/bold]")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=3, style="dim")
    table.add_column("Filename", width=30, style="cyan")
    table.add_column("Time", width=12, style="dim")
    table.add_column("Size", width=10, justify="right", style="dim")
    table.add_column("Level", width=10, style="green")

    for i, file in enumerate(files[:limit], 1):
        size_str = f"{file.size_mb:.1f} MB"
        table.add_row(
            str(i),
            file.name,
            file.time_ago,
            size_str,
            file.analysis_level,
        )

    console.print(table)

    # Usage hints
    console.print()
    console.print("[bold cyan]💡 Usage Hints:[/bold cyan]")
    console.print("  [dim]samplemind analyze:full @1[/dim]      Re-analyze most recent file")
    console.print("  [dim]samplemind recent:search <query>[/dim]  Search by filename or tags")
    console.print("  [dim]samplemind recent:export[/dim]         Export as JSON")

    # Show stats if requested
    if show_stats:
        console.print()
        console.print("[bold cyan]📊 Statistics[/bold cyan]")
        stats = get_recent_files_stats()

        stats_table = Table(show_header=False, show_lines=False)
        stats_table.add_column(width=25, style="cyan")
        stats_table.add_column(justify="right", style="green")

        stats_table.add_row("Total Files:", str(stats["total_files"]))
        stats_table.add_row("Total Size:", f"{stats['total_size_mb']:.2f} MB")
        stats_table.add_row("Total Duration:", f"{stats['total_duration_hours']:.1f} hours")

        console.print(stats_table)

        if stats["by_analysis_level"]:
            console.print()
            console.print("[dim]By Analysis Level:[/dim]")
            for level, count in stats["by_analysis_level"].items():
                console.print(f"  {level:<15} {count:>3} files")


# ============================================================================
# SEARCH COMMAND
# ============================================================================

@app.command("search")
@utils.with_error_handling
def search_command(
    query: str = typer.Argument(..., help="Search query (filename, path, or tags)"),
):
    """Search recent files by name, path, or tags"""
    results = search_recent_files(query)

    if not results:
        console.print(f"[yellow]🔍 No recent files matching '{query}'[/yellow]")
        return

    console.print()
    console.print(f"[bold]🔍 Search Results for '{query}'[/bold]")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=3)
    table.add_column("Filename", style="cyan")
    table.add_column("Time", style="dim")
    table.add_column("Tags", style="magenta")

    for i, file in enumerate(results, 1):
        tags_str = ", ".join(file.tags) if file.tags else "-"
        table.add_row(
            str(i),
            file.name,
            file.time_ago,
            tags_str,
        )

    console.print(table)


# ============================================================================
# EXPORT COMMAND
# ============================================================================

@app.command("export")
@utils.with_error_handling
def export_command(
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (default: recent_files.json in current directory)"
    ),
):
    """Export recent files as JSON"""
    output_path = output or Path("recent_files.json")

    json_data = export_recent_files(output_path)

    console.print(f"[green]✅ Exported {len(get_recent_files())} recent files[/green]")
    console.print(f"[cyan]📄 Saved to: {output_path.absolute()}[/cyan]")


# ============================================================================
# CLEAR COMMAND
# ============================================================================

@app.command("clear")
@utils.with_error_handling
def clear_command(
    confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation"
    ),
):
    """Clear all recent file history"""
    if not confirm:
        console.print("[yellow]⚠️  This will clear all recent file history[/yellow]")
        response = typer.confirm("Are you sure?", default=False)
        if not response:
            console.print("[yellow]Cancelled[/yellow]")
            return

    get_manager().clear()
    console.print("[green]✅ Recent file history cleared[/green]")


# ============================================================================
# VIEW COMMAND - Show details for a specific file
# ============================================================================

@app.command("view")
@utils.with_error_handling
def view_command(
    index: int = typer.Argument(1, help="File index (1 = most recent)"),
):
    """View details for a specific recent file"""
    file = get_recent_file_by_index(index)

    if not file:
        files = get_recent_files()
        console.print(f"[red]❌ Index {index} out of range (max: {len(files)})[/red]")
        return

    console.print()
    console.print(f"[bold cyan]📄 {file.name}[/bold cyan]")

    info_table = Table(show_header=False, show_lines=False)
    info_table.add_column(width=20, style="cyan")
    info_table.add_column()

    info_table.add_row("Path:", file.path)
    info_table.add_row("Size:", f"{file.size_mb:.2f} MB")
    info_table.add_row("Duration:", f"{file.duration_seconds:.1f} seconds")
    info_table.add_row("Analysis Level:", file.analysis_level)
    info_table.add_row("Analyzed:", file.time_ago)

    if file.tags:
        info_table.add_row("Tags:", ", ".join(file.tags))

    console.print(info_table)

    # Quick actions
    console.print()
    console.print("[bold cyan]💡 Quick Actions:[/bold cyan]")
    console.print(f"  [dim]samplemind analyze:full @{index}[/dim]           Re-analyze")
    console.print(f"  [dim]samplemind tag:auto @{index}[/dim]              Auto-tag")
    console.print(f"  [dim]samplemind fav:add @{index}[/dim]               Add to favorites")


# ============================================================================
# STATS COMMAND
# ============================================================================

@app.command("stats")
@utils.with_error_handling
def stats_command():
    """Show statistics about recent files"""
    stats = get_recent_files_stats()

    console.print()
    console.print("[bold cyan]📊 Recent Files Statistics[/bold cyan]")

    stats_table = Table(show_header=False, show_lines=False, padding=(0, 2))
    stats_table.add_column(width=25, style="cyan", no_wrap=True)
    stats_table.add_column(justify="right", style="green")

    stats_table.add_row("Total Files:", str(stats["total_files"]))
    stats_table.add_row("Total Size:", f"{stats['total_size_mb']:.2f} MB")
    stats_table.add_row("Total Duration:", f"{stats['total_duration_hours']:.1f} hours")
    if stats["total_files"] > 0:
        avg_size = stats["total_size_mb"] / stats["total_files"]
        stats_table.add_row("Average File Size:", f"{avg_size:.2f} MB")

    console.print(stats_table)

    # By analysis level
    if stats["by_analysis_level"]:
        console.print()
        console.print("[bold]By Analysis Level:[/bold]")
        level_table = Table(show_header=True, header_style="bold cyan", show_lines=False)
        level_table.add_column("Level", style="cyan")
        level_table.add_column("Count", justify="right", style="green")

        for level, count in sorted(stats["by_analysis_level"].items()):
            level_table.add_row(level, str(count))

        console.print(level_table)

    # Top tags
    if stats["top_tags"]:
        console.print()
        console.print("[bold]Top Tags:[/bold]")
        tag_table = Table(show_header=True, header_style="bold cyan", show_lines=False)
        tag_table.add_column("Tag", style="magenta")
        tag_table.add_column("Count", justify="right", style="green")

        for tag, count in stats["top_tags"][:10]:
            tag_table.add_row(tag, str(count))

        console.print(tag_table)


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = ["app"]
