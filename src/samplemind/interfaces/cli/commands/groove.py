#!/usr/bin/env python3
"""Groove Extraction Commands"""

from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console
from rich.table import Table

from samplemind.core.processing.groove_extractor import GrooveExtractor
from . import utils

app = typer.Typer(help="🎵 Groove template extraction & application", no_args_is_help=True)
console = utils.console

@app.command("extract")
@utils.with_error_handling
@utils.async_command
async def extract_groove(
    file: Optional[Path] = typer.Argument(None, help="Audio file to extract groove from"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Groove name"),
    tempo: Optional[float] = typer.Option(None, "--tempo", "-t", help="Tempo in BPM"),
    save_path: Optional[Path] = typer.Option(None, "--save", "-s", help="Save groove to file"),
) -> None:
    """Extract groove template from drum loop"""
    try:
        if not file:
            from samplemind.utils.file_picker import select_audio_file
            file = select_audio_file(title="Select drum loop")
            if not file:
                raise typer.Exit(1)

        try:
            import librosa
            audio, sr = librosa.load(str(file), sr=None, mono=True)
        except ImportError:
            console.print("[yellow]⚠️  librosa not available[/yellow]")
            return

        console.print()
        console.print(f"[bold cyan]🎵 Groove Extraction[/bold cyan]")
        console.print(f"[cyan]File: {file.name}[/cyan]\n")

        # Extract
        extractor = GrooveExtractor()
        groove = extractor.extract(
            audio,
            sr,
            name=name or file.stem,
            tempo_bpm=tempo
        )

        # Display results
        console.print("[bold]Groove Characteristics:[/bold]")
        groove_table = Table(show_header=False, show_lines=False, padding=(0, 2))
        groove_table.add_column(width=20, style="cyan")
        groove_table.add_column()
        groove_table.add_row("Tempo:", f"{groove.tempo_bpm:.1f} BPM")
        groove_table.add_row("Type:", groove.groove_type.title())
        groove_table.add_row("Swing:", f"{groove.swing_amount:.0f}%")
        groove_table.add_row("Timing Dev:", f"±{groove.timing_deviation_ms:.1f} ms")
        console.print(groove_table)

        # Save if requested
        if save_path:
            groove.save(save_path)
            console.print(f"\n[green]✅ Groove saved to {save_path}[/green]")
        else:
            console.print(f"\n[dim]Use --save to save the groove template[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "groove:extract")
        raise typer.Exit(1)

@app.command("apply")
@utils.with_error_handling
def apply_groove(
    groove_file: Path = typer.Argument(..., help="Groove template file"),
    midi_file: Optional[Path] = typer.Option(None, "--midi", "-m", help="MIDI file to apply groove to"),
) -> None:
    """Apply groove template to MIDI"""
    console.print()
    console.print("[yellow]⏳ MIDI groove application coming soon![/yellow]")
    console.print(f"\nGroove: {groove_file.name}")
    if midi_file:
        console.print(f"MIDI: {midi_file.name}")

__all__ = ["app"]
