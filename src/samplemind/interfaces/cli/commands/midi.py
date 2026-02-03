#!/usr/bin/env python3
"""MIDI Extraction Commands - Extract musical information as MIDI"""

import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from samplemind.core.processing.midi_generator import (
    MIDIGenerator,
    MIDIExtractionType,
)
from . import utils

app = typer.Typer(help="🎼 MIDI Extraction - Extract melody, chords, and drums as MIDI", no_args_is_help=True)
console = utils.console


@app.command("extract")
@utils.with_error_handling
def extract_midi(
    file: Optional[Path] = typer.Argument(None, help="Audio file to extract MIDI from"),
    extraction_type: str = typer.Option(
        "melody",
        "--type", "-t",
        help="Extraction type: melody, harmony, rhythm"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output MIDI file path"
    ),
    format_type: str = typer.Option(
        "table",
        "--format", "-f",
        help="Output format: table, json"
    ),
) -> None:
    """
    Extract MIDI from audio file.

    Supported types:
    - melody: Extract monophonic melody line
    - harmony: Detect chord progressions
    - rhythm: Extract drum pattern
    """
    try:
        # File selection
        if not file:
            from samplemind.utils.file_picker import select_audio_file
            file = select_audio_file(title="Select audio file for MIDI extraction")
            if not file:
                raise typer.Exit(1)

        file = Path(file).resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        # Type validation
        extraction_lower = extraction_type.lower()
        valid_types = ["melody", "harmony", "rhythm"]
        if extraction_lower not in valid_types:
            console.print(f"[red]✗ Invalid type '{extraction_type}'. Use: {', '.join(valid_types)}[/red]")
            raise typer.Exit(1)

        # Display header
        console.print()
        console.print(f"[bold cyan]🎼 MIDI Extraction[/bold cyan]")
        console.print(f"[cyan]File: {file.name}[/cyan]")
        console.print(f"[cyan]Type: {extraction_lower}[/cyan]\n")

        # Extract MIDI
        start_time = time.time()

        type_enum = MIDIExtractionType[extraction_lower.upper()]
        generator = MIDIGenerator(sample_rate=22050)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Extracting {extraction_lower}...", total=None)
            result = generator.extract(file, extraction_type=type_enum)
            progress.update(task, completed=True)

        elapsed = time.time() - start_time

        # Display results
        console.print()
        console.print(f"[green]✓ Extraction complete in {elapsed:.1f}s[/green]")
        console.print()

        # Type-specific display
        if extraction_lower == "melody":
            _display_melody_results(result)
        elif extraction_lower == "harmony":
            _display_chord_results(result)
        elif extraction_lower == "rhythm":
            _display_rhythm_results(result)

        # Save MIDI if requested
        if output:
            output_path = Path(output)
            if result.midi_file:
                generator.save_midi(result.midi_file, output_path)
                console.print(f"[green]✓ MIDI saved to {output_path}[/green]")
        else:
            console.print(f"[dim]Use --output to save as MIDI file[/dim]")

        # JSON output
        if format_type == "json":
            _output_json_result(result, elapsed, extraction_lower)

    except utils.CLIError as e:
        utils.handle_error(e, "midi:extract")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("melody")
@utils.with_error_handling
def extract_melody_shortcut(
    file: Optional[Path] = typer.Argument(None, help="Audio file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output MIDI file"),
) -> None:
    """Extract melody from audio (shortcut for --type melody)"""
    extract_midi(file, extraction_type="melody", output=output)


@app.command("chords")
@utils.with_error_handling
def extract_chords_shortcut(
    file: Optional[Path] = typer.Argument(None, help="Audio file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output MIDI file"),
) -> None:
    """Extract chords from audio (shortcut for --type harmony)"""
    extract_midi(file, extraction_type="harmony", output=output)


@app.command("drums")
@utils.with_error_handling
def extract_drums_shortcut(
    file: Optional[Path] = typer.Argument(None, help="Audio file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output MIDI file"),
) -> None:
    """Extract drum pattern from audio (shortcut for --type rhythm)"""
    extract_midi(file, extraction_type="rhythm", output=output)


@app.command("batch")
@utils.with_error_handling
def batch_extract_midi(
    folder: Optional[Path] = typer.Argument(None, help="Folder with audio files"),
    extraction_type: str = typer.Option(
        "melody",
        "--type", "-t",
        help="Extraction type: melody, harmony, rhythm"
    ),
    output_folder: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output folder for MIDI files"
    ),
) -> None:
    """
    Batch extract MIDI from multiple audio files.
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
        audio_files = list(folder.glob("*.wav")) + list(folder.glob("*.mp3")) + \
                      list(folder.glob("*.flac")) + list(folder.glob("*.m4a"))

        if not audio_files:
            console.print(f"[yellow]⚠ No audio files found in {folder}[/yellow]")
            raise typer.Exit(1)

        console.print()
        console.print(f"[bold cyan]🎼 Batch MIDI Extraction[/bold cyan]")
        console.print(f"[cyan]Folder: {folder}[/cyan]")
        console.print(f"[cyan]Files: {len(audio_files)}[/cyan]")
        console.print(f"[cyan]Type: {extraction_type}[/cyan]\n")

        # Set output folder
        if output_folder:
            output_folder = Path(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)
        else:
            output_folder = folder / f"midi_{extraction_type}"
            output_folder.mkdir(exist_ok=True)

        # Process files
        start_time = time.time()
        extraction_lower = extraction_type.lower()
        type_enum = MIDIExtractionType[extraction_lower.upper()]
        generator = MIDIGenerator(sample_rate=22050)

        success_count = 0
        from rich.progress import Progress as RichProgress, BarColumn

        with RichProgress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            console=console
        ) as progress:
            task = progress.add_task("Extracting MIDI...", total=len(audio_files))

            for audio_file in audio_files:
                try:
                    result = generator.extract(audio_file, extraction_type=type_enum)

                    if result.midi_file:
                        midi_filename = f"{audio_file.stem}_{extraction_lower}.mid"
                        midi_path = output_folder / midi_filename
                        generator.save_midi(result.midi_file, midi_path)
                        success_count += 1

                except Exception as e:
                    console.print(f"[yellow]⚠ Failed to process {audio_file.name}: {e}[/yellow]")

                progress.update(task, advance=1)

        elapsed = time.time() - start_time

        # Summary
        console.print()
        console.print(f"[green]✓ Batch complete in {elapsed:.1f}s[/green]")
        console.print(f"[green]Successfully extracted: {success_count}/{len(audio_files)}[/green]")
        console.print(f"[dim]MIDI files saved to: {output_folder}[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "midi:batch")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


# ============================================================================
# Display Helpers
# ============================================================================

def _display_melody_results(result) -> None:
    """Display melody extraction results"""
    if not result.notes:
        console.print("[yellow]⚠ No notes detected[/yellow]")
        return

    table = Table(title="Extracted Melody", show_header=True, header_style="bold cyan")
    table.add_column("Note", style="cyan")
    table.add_column("Time (s)", style="yellow")
    table.add_column("Duration (s)", style="yellow")
    table.add_column("MIDI #", style="green")
    table.add_column("Confidence", style="green")

    # Show first 20 notes
    for note in result.notes[:20]:
        note_name = _get_note_name(note.pitch)
        table.add_row(
            note_name,
            f"{note.start_time:.2f}",
            f"{note.duration:.2f}",
            str(note.pitch),
            f"{note.confidence:.2f}"
        )

    console.print(table)

    if result.tempo_bpm:
        console.print(f"\n[cyan]Tempo: {result.tempo_bpm:.1f} BPM[/cyan]")
    console.print(f"[cyan]Total Notes: {len(result.notes)}[/cyan]")
    console.print(f"[cyan]Confidence: {result.confidence:.2f}[/cyan]")


def _display_chord_results(result) -> None:
    """Display chord detection results"""
    if not result.chords:
        console.print("[yellow]⚠ No chords detected[/yellow]")
        return

    table = Table(title="Detected Chords", show_header=True, header_style="bold cyan")
    table.add_column("Chord", style="cyan")
    table.add_column("Time (s)", style="yellow")
    table.add_column("Duration (s)", style="yellow")
    table.add_column("Confidence", style="green")

    # Show chords
    for chord in result.chords:
        table.add_row(
            chord.get_name(),
            f"{chord.start_time:.2f}",
            f"{chord.duration:.2f}",
            f"{chord.confidence:.2f}"
        )

    console.print(table)

    if result.tempo_bpm:
        console.print(f"\n[cyan]Tempo: {result.tempo_bpm:.1f} BPM[/cyan]")
    console.print(f"[cyan]Total Chords: {len(result.chords)}[/cyan]")
    console.print(f"[cyan]Confidence: {result.confidence:.2f}[/cyan]")


def _display_rhythm_results(result) -> None:
    """Display drum pattern extraction results"""
    if not result.notes:
        console.print("[yellow]⚠ No rhythm detected[/yellow]")
        return

    table = Table(title="Drum Pattern", show_header=True, header_style="bold cyan")
    table.add_column("Hit Type", style="cyan")
    table.add_column("Time (s)", style="yellow")
    table.add_column("Duration (s)", style="yellow")
    table.add_column("Velocity", style="green")

    # Show notes
    for i, note in enumerate(result.notes[:30]):  # Show first 30 hits
        hit_type = "Kick" if note.pitch == 36 else "Drum"
        table.add_row(
            f"{hit_type} #{i+1}",
            f"{note.start_time:.3f}",
            f"{note.duration:.3f}",
            str(note.velocity)
        )

    console.print(table)

    if result.tempo_bpm:
        console.print(f"\n[cyan]Tempo: {result.tempo_bpm:.1f} BPM[/cyan]")
    console.print(f"[cyan]Total Hits: {len(result.notes)}[/cyan]")


def _output_json_result(result, elapsed: float, extraction_type: str) -> None:
    """Output results as JSON"""
    import json

    output_data = {
        "status": "success",
        "type": extraction_type,
        "elapsed_seconds": elapsed,
        "tempo_bpm": result.tempo_bpm,
        "confidence": result.confidence,
        "items_count": len(result.notes) if result.notes else len(result.chords),
    }

    console.print()
    console.print(utils.format_json(output_data))


def _get_note_name(midi_number: int) -> str:
    """Get note name from MIDI number"""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    note = notes[midi_number % 12]
    return f"{note}{octave}"


__all__ = ["app"]
