#!/usr/bin/env python3
"""
Tag Management Commands

AI-powered sample tagging with searchable library integration.

Usage:
    samplemind tag:auto <file>              # Auto-generate tags
    samplemind tag:edit <file>              # Edit tags manually
    samplemind tag:vocab                    # Show tag vocabulary
    samplemind tag:search --tags <tags>     # Search by tags
"""

from pathlib import Path
from typing import Optional, List
import asyncio

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from samplemind.core.tagging.ai_tagger import get_tagger
from samplemind.core.tagging.tag_vocabulary import get_vocabulary
from samplemind.core.history.recent_files import add_recent_file

from . import utils

# Create tagging app group
app = typer.Typer(
    help="🏷️  Sample tagging & organization",
    no_args_is_help=True,
)

console = utils.console

# ============================================================================
# AUTO-TAG COMMAND
# ============================================================================

@app.command("auto")
@utils.with_error_handling
@utils.async_command
async def auto_tag(
    file: Optional[Path] = typer.Argument(None, help="Audio file to tag"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch file picker"),
    show_sources: bool = typer.Option(False, "--sources", "-s", help="Show tag sources"),
    min_confidence: float = typer.Option(0.5, "--min-confidence", help="Minimum confidence (0.0-1.0)"),
    save: bool = typer.Option(False, "--save", help="Save tags to database"),
) -> None:
    """Auto-generate tags for an audio file using AI and feature analysis"""
    try:
        # Handle file selection
        if not file or interactive:
            from samplemind.utils.file_picker import select_audio_file
            console.print("[cyan]📁 Opening file picker...[/cyan]")
            selected_file = select_audio_file(title="Select Audio File for Tagging")
            if not selected_file:
                console.print("[yellow]❌ No file selected[/yellow]")
                raise typer.Exit(1)
            file = selected_file
            console.print(f"[green]✅ Selected: {file.name}[/green]")

        # 1. Analyze audio
        console.print()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Analyzing audio features...", total=None)
            features = await utils.analyze_file_async(file, "STANDARD")

        # 2. Generate AI analysis (optional)
        # In production, this would call the AI manager
        ai_analysis = None

        # 3. Generate tags
        tagger = get_tagger()
        tags = tagger.tag_from_features(features, ai_analysis, use_ai=True)

        # 4. Filter by confidence
        filtered_tags = [t for t in tags if t.confidence >= min_confidence]

        # 5. Display results
        console.print()
        console.print(f"[bold cyan]🏷️  Tags for {file.name}[/bold cyan]")
        console.print(f"[dim]Confidence threshold: {min_confidence:.0%}[/dim]\n")

        organized = tagger.organize_by_category(filtered_tags)

        for category, tag_list in organized.items():
            if tag_list:
                console.print(f"[bold]{category.upper()}:[/bold]")

                tag_table = Table(show_header=False, show_lines=False, padding=(0, 1))
                tag_table.add_column(style="magenta", width=20)
                tag_table.add_column(justify="right", style="green", width=12)
                if show_sources:
                    tag_table.add_column(style="dim", width=12)

                for tag in tag_list:
                    confidence_str = f"{tag.confidence:.0%}"
                    if show_sources:
                        tag_table.add_row(
                            f"  {tag.tag}",
                            confidence_str,
                            f"[{tag.source}]"
                        )
                    else:
                        tag_table.add_row(f"  {tag.tag}", confidence_str)

                console.print(tag_table)
                console.print()

        # 6. Save if requested
        if save:
            # In production, save to database/ChromaDB
            console.print("[green]✅ Tags ready to save to database[/green]")
            add_recent_file(file, "STANDARD", [t.tag for t in filtered_tags])

        # 7. Statistics
        stats = {
            "total_tags": len(filtered_tags),
            "by_category": {
                cat: len(tags) for cat, tags in organized.items() if tags
            },
        }

        console.print(f"[dim]📊 Generated {stats['total_tags']} tags[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "tag:auto")
        raise typer.Exit(1)


# ============================================================================
# VOCABULARY COMMAND
# ============================================================================

@app.command("vocab")
@utils.with_error_handling
def show_vocabulary(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Show specific category"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of tags to show"),
) -> None:
    """Show available tag vocabulary and categories"""
    vocab = get_vocabulary()
    stats = vocab.stats()

    console.print()
    console.print("[bold cyan]🏷️  Tag Vocabulary[/bold cyan]\n")

    # Show statistics
    stats_table = Table(show_header=True, header_style="bold cyan", show_lines=False)
    stats_table.add_column("Category", style="cyan")
    stats_table.add_column("Count", justify="right", style="green")

    for cat_name, count in stats.items():
        if cat_name != "total":
            stats_table.add_row(cat_name.replace("_", " ").title(), str(count))

    console.print(stats_table)

    # Show specific category if requested
    if category:
        category_lower = category.lower()

        tags = vocab.get_tags_by_category(category_lower)

        if tags:
            console.print()
            console.print(f"[bold]{category_lower.upper()} Tags ({len(tags)} total):[/bold]\n")

            # Display in columns
            sorted_tags = sorted(list(tags))[:limit]
            cols = 4
            for i in range(0, len(sorted_tags), cols):
                row = sorted_tags[i:i + cols]
                console.print("  " + "  |  ".join(f"{tag:<20}" for tag in row))

            if len(tags) > limit:
                console.print(f"\n[dim]... and {len(tags) - limit} more[/dim]")
        else:
            console.print(f"[red]❌ Unknown category: {category}[/red]")
    else:
        # Show all categories
        console.print()
        console.print("[bold]Available Categories:[/bold]")
        for cat_name in ["genres", "moods", "instruments", "energy_levels", "descriptors"]:
            actual_name = cat_name.replace("_", "-")
            console.print(f"  • [cyan]--category {actual_name}[/cyan]")

        console.print()
        console.print(f"[bold]Total Tags: {stats['total']}[/bold]")


# ============================================================================
# SEARCH COMMAND
# ============================================================================

@app.command("search")
@utils.with_error_handling
def search_by_tags(
    tags: str = typer.Option(..., "--tags", "-t", help="Tags to search (comma-separated)"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max results"),
) -> None:
    """Search library by tags (integrates with tag database)"""
    tag_list = [t.strip() for t in tags.split(",")]

    console.print()
    console.print(f"[bold cyan]🔍 Searching for samples with tags:[/bold cyan]")

    # Display search tags
    for tag in tag_list:
        console.print(f"  • {tag}")

    console.print()

    # In production, this would query ChromaDB/database
    # For now, show the tag search interface
    console.print("[yellow]⏳ Searching database... (feature coming soon)[/yellow]")
    console.print(f"[dim]Will search {len(tag_list)} tag filters in your library[/dim]")

    # Example output format (when feature is implemented)
    console.print()
    console.print("[dim]Expected results format (when enabled):[/dim]")
    example_table = Table(show_header=True, header_style="bold cyan")
    example_table.add_column("Filename")
    example_table.add_column("Match Score")
    example_table.add_column("Matching Tags")

    example_table.add_row(
        "example_kick.wav",
        "95%",
        "drums, kick, punchy, bright"
    )
    console.print(example_table)


# ============================================================================
# EDIT COMMAND
# ============================================================================

@app.command("edit")
@utils.with_error_handling
def edit_tags(
    file: Optional[Path] = typer.Argument(None, help="Audio file to edit tags for"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch file picker"),
) -> None:
    """Edit tags for a sample (interactive mode)"""
    # Handle file selection
    if not file or interactive:
        from samplemind.utils.file_picker import select_audio_file
        console.print("[cyan]📁 Opening file picker...[/cyan]")
        selected_file = select_audio_file(title="Select Audio File to Tag")
        if not selected_file:
            console.print("[yellow]❌ No file selected[/yellow]")
            raise typer.Exit(1)
        file = selected_file

    console.print()
    console.print(f"[bold cyan]✏️  Edit Tags for {file.name}[/bold cyan]\n")

    # In production, this would show an interactive prompt
    console.print("[yellow]⏳ Interactive tag editor coming soon![/yellow]")
    console.print()
    console.print("Features planned:")
    console.print("  • Auto-suggested tags with checkboxes")
    console.print("  • Manual tag addition/removal")
    console.print("  • Real-time vocabulary validation")
    console.print("  • Confidence level adjustment")


# ============================================================================
# BATCH COMMAND
# ============================================================================

@app.command("batch")
@utils.with_error_handling
async def batch_tag(
    folder: Optional[Path] = typer.Argument(None, help="Folder to batch tag"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch folder picker"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show results without saving"),
) -> None:
    """Batch tag all audio files in a folder"""
    # Handle folder selection
    if not folder or interactive:
        from samplemind.utils.file_picker import select_directory
        console.print("[cyan]📁 Opening folder picker...[/cyan]")
        selected_folder = select_directory(title="Select Folder to Batch Tag")
        if not selected_folder:
            console.print("[yellow]❌ No folder selected[/yellow]")
            raise typer.Exit(1)
        folder = selected_folder

    console.print()
    console.print(f"[bold cyan]🏷️  Batch Tagging Folder[/bold cyan]")
    console.print(f"[cyan]Folder: {folder}[/cyan]\n")

    if dry_run:
        console.print("[yellow]⚠️  DRY RUN - No changes will be made[/yellow]\n")

    # Get audio files
    audio_files = utils.get_audio_files(folder)
    console.print(f"[cyan]Found {len(audio_files)} audio files[/cyan]\n")

    # Process each file (placeholder)
    console.print("[yellow]⏳ Batch processing coming soon![/yellow]")
    console.print()
    console.print(f"Will tag all {len(audio_files)} files with AI analysis")


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = ["app"]
