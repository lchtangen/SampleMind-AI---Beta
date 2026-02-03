#!/usr/bin/env python3
"""Stem Separation Commands - AI-powered audio stem extraction"""

import asyncio
import time
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel

from samplemind.core.processing.stem_separation import (
    StemSeparationEngine,
    StemQuality,
    StemSeparationResult,
)
from . import utils

app = typer.Typer(help="🎼 AI Stem Separation - Split audio into vocals, drums, bass, other", no_args_is_help=True)
console = utils.console


@app.command("separate")
@utils.with_error_handling
def separate_stems(
    file: Optional[Path] = typer.Argument(None, help="Audio file to separate"),
    quality: str = typer.Option(
        "standard",
        "--quality", "-q",
        help="Quality preset: fast, standard, high"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for stems"
    ),
    format_type: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table, json"
    ),
) -> None:
    """
    Separate an audio file into individual stems (vocals, drums, bass, other).

    Uses state-of-the-art Demucs v4 MDX models for high-quality separation.
    """
    try:
        # File selection
        if not file:
            from samplemind.utils.file_picker import select_audio_file
            file = select_audio_file(title="Select audio file for stem separation")
            if not file:
                raise typer.Exit(1)

        file = Path(file).resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        # Quality validation
        quality_lower = quality.lower()
        if quality_lower not in ["fast", "standard", "high"]:
            console.print(f"[red]✗ Invalid quality '{quality}'. Use: fast, standard, high[/red]")
            raise typer.Exit(1)

        # Create engine
        console.print()
        console.print(f"[bold cyan]🎼 Stem Separation[/bold cyan]")
        console.print(f"[cyan]File: {file.name}[/cyan]")
        console.print(f"[cyan]Quality: {quality_lower}[/cyan]\n")

        quality_enum = StemQuality[quality_lower.upper()]
        engine = StemSeparationEngine.from_quality(
            quality=quality_enum,
            device=None,  # Auto-detect
            verbose=False
        )

        # Run separation with progress
        start_time = time.time()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Separating stems...", total=None)

            result = engine.separate(
                audio_path=file,
                output_directory=output
            )

            progress.update(task, completed=True)

        elapsed = time.time() - start_time

        # Display results
        console.print()
        console.print(f"[green]✓ Separation complete in {elapsed:.1f}s[/green]")
        console.print()

        # Create results table
        results_table = Table(title="Generated Stems", show_header=True, header_style="bold cyan")
        results_table.add_column("Stem Type", style="cyan")
        results_table.add_column("File Path", style="green")
        results_table.add_column("Size", style="yellow")

        for stem_name, stem_path in sorted(result.stems.items()):
            size_mb = stem_path.stat().st_size / (1024 * 1024)
            results_table.add_row(
                stem_name.title(),
                str(stem_path),
                f"{size_mb:.1f} MB"
            )

        console.print(results_table)

        # Output format
        if format_type == "json":
            output_data = {
                "status": "success",
                "file": str(file),
                "quality": quality_lower,
                "elapsed_seconds": elapsed,
                "output_directory": str(result.output_directory),
                "stems": {
                    name: {
                        "path": str(path),
                        "size_mb": path.stat().st_size / (1024 * 1024)
                    }
                    for name, path in result.stems.items()
                }
            }
            console.print()
            console.print(utils.format_json(output_data))

        console.print(f"\n[dim]💡 All stems saved to: {result.output_directory}[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "stems:separate")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("batch")
@utils.with_error_handling
@utils.async_command
async def batch_separate(
    folder: Optional[Path] = typer.Argument(None, help="Folder containing audio files"),
    quality: str = typer.Option(
        "standard",
        "--quality", "-q",
        help="Quality preset: fast, standard, high"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Base output directory"
    ),
    extensions: str = typer.Option(
        "wav,mp3,flac,m4a",
        "--extensions", "-e",
        help="File extensions to process (comma-separated)"
    ),
) -> None:
    """
    Batch separate multiple audio files from a folder.

    Processes all audio files in a directory, organizing stems by source file.
    """
    try:
        # Folder selection
        if not folder:
            from samplemind.utils.file_picker import select_folder
            folder = select_folder(title="Select folder with audio files")
            if not folder:
                raise typer.Exit(1)

        folder = Path(folder).resolve()
        if not folder.exists():
            console.print(f"[red]✗ Folder not found: {folder}[/red]")
            raise typer.Exit(1)

        # Find audio files
        ext_list = [ext.strip().lower() for ext in extensions.split(",")]
        audio_files = []
        for ext in ext_list:
            audio_files.extend(folder.glob(f"*.{ext}"))

        if not audio_files:
            console.print(f"[yellow]⚠ No audio files found in {folder}[/yellow]")
            raise typer.Exit(1)

        console.print()
        console.print(f"[bold cyan]🎼 Batch Stem Separation[/bold cyan]")
        console.print(f"[cyan]Folder: {folder}[/cyan]")
        console.print(f"[cyan]Files: {len(audio_files)}[/cyan]")
        console.print(f"[cyan]Quality: {quality}[/cyan]\n")

        # Create engine
        quality_lower = quality.lower()
        if quality_lower not in ["fast", "standard", "high"]:
            console.print(f"[red]✗ Invalid quality. Use: fast, standard, high[/red]")
            raise typer.Exit(1)

        quality_enum = StemQuality[quality_lower.upper()]
        engine = StemSeparationEngine.from_quality(
            quality=quality_enum,
            device=None,
            verbose=False
        )

        # Process with progress
        start_time = time.time()
        results = []
        processed_count = [0]  # Use list to allow mutation in nested function

        def progress_callback(current: int, total: int) -> None:
            """Progress callback for stem separation.
            
            Args:
                current: Current file number being processed
                total: Total number of files to process
            """
            console.print(f"[cyan]Progress: {current}/{total} files[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                "Separating stems...",
                total=len(audio_files)
            )

            results = await engine.batch_separate(
                audio_paths=audio_files,
                output_directory=output,
                max_concurrent=1,
                progress_callback=lambda c, t: progress.update(task, completed=c)
            )

        elapsed = time.time() - start_time

        # Summary
        console.print()
        console.print(f"[green]✓ Batch complete in {elapsed:.1f}s[/green]")
        console.print()

        # Results table
        summary_table = Table(title="Batch Results", show_header=True, header_style="bold cyan")
        summary_table.add_column("Input File", style="cyan")
        summary_table.add_column("Stems Generated", style="green")
        summary_table.add_column("Output Dir", style="yellow")

        for result in results:
            source_name = result.output_directory.parent.name
            summary_table.add_row(
                source_name,
                str(len(result.stems)),
                str(result.output_directory)
            )

        console.print(summary_table)
        console.print(f"\n[dim]💡 Average time per file: {elapsed / len(audio_files):.1f}s[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "stems:batch")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
@utils.with_error_handling
def list_stems(
    file: Optional[Path] = typer.Argument(None, help="Separated stem directory or list stems from previous separation"),
) -> None:
    """
    List available stem separation models and quality presets.
    """
    console.print()
    console.print("[bold cyan]🎼 Stem Separation Models & Presets[/bold cyan]\n")

    # Display available presets
    presets = StemSeparationEngine.get_available_presets()
    presets_table = Table(title="Quality Presets", show_header=True, header_style="bold cyan")
    presets_table.add_column("Preset", style="cyan")
    presets_table.add_column("Description", style="green")

    for preset_name, description in presets.items():
        presets_table.add_row(preset_name, description)

    console.print(presets_table)

    # Display model information
    console.print()
    console.print("[bold]Available Models:[/bold]")
    console.print("  [cyan]Demucs v4 Models:[/cyan]")
    console.print("    • mdx - Fast, real-time capable")
    console.print("    • mdx_extra - Balanced quality/speed (default)")
    console.print("    • mdx_q - Highest quality")
    console.print()
    console.print("  [cyan]Demucs v3 Models:[/cyan]")
    console.print("    • htdemucs - Classic model")
    console.print("    • htdemucs_ft - Fine-tuned on music")
    console.print()
    console.print("[dim]Use: samplemind stems:separate <file> --quality {fast|standard|high}[/dim]")


@app.command("extract")
@utils.with_error_handling
def extract_stem(
    stem_type: str = typer.Argument(
        ...,
        help="Stem type to extract: vocals, drums, bass, other"
    ),
    file: Optional[Path] = typer.Argument(None, help="Already-separated stem file"),
) -> None:
    """
    Extract a specific stem from an already-separated file.

    This is useful if you want to work with just one stem type (e.g., just vocals).
    """
    console.print()
    console.print(f"[bold cyan]🎼 Stem Extraction: {stem_type}[/bold cyan]\n")

    valid_stems = ["vocals", "drums", "bass", "other"]
    if stem_type.lower() not in valid_stems:
        console.print(f"[red]✗ Invalid stem type. Use: {', '.join(valid_stems)}[/red]")
        raise typer.Exit(1)

    if not file:
        from samplemind.utils.file_picker import select_audio_file
        file = select_audio_file(title=f"Select {stem_type} stem file")
        if not file:
            raise typer.Exit(1)

    console.print(f"[green]✓ Stem: {file.name}[/green]")
    console.print(f"[dim]Type: {stem_type}[/dim]")


__all__ = ["app"]
