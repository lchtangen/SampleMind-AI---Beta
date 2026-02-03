"""
SampleMind AI - Music Theory Command Group

Analyze harmonic content of audio files including chord progressions,
key detection, and Roman numeral analysis.

Commands:
- theory:chords <file>  - Detect chord progression
- theory:key <file>     - Detect key and mode
- theory:harmony <file> - Full harmonic analysis
- theory:scale <key>    - Show scale notes

Usage:
    samplemind theory:key song.wav               # Detect key
    samplemind theory:chords song.wav            # Show chord progression
    samplemind theory:harmony song.wav --roman   # Full analysis with Roman numerals
    samplemind theory:scale "C major"            # Show C major scale
"""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import utils

app = typer.Typer(help="🎼 Music theory analysis (4 commands)", no_args_is_help=True)
console = utils.console


def _get_analyzer():
    """Lazy import to avoid circular imports"""
    from ....core.analysis import MusicTheoryAnalyzer
    return MusicTheoryAnalyzer()


@app.command("key")
@utils.with_error_handling
def theory_key(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed analysis with modulations"),
) -> None:
    """Detect the musical key of an audio file"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]Key Detection[/bold cyan]")
        console.print(f"  File: [green]{file.name}[/green]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing key...", total=None)

            if detail:
                analyzer = _get_analyzer()
                analysis = analyzer.analyze(file)
                key_name = analysis.key
                confidence = analysis.key_confidence
                modulations = analysis.modulations
            else:
                analyzer = _get_analyzer()
                key_name, confidence = analyzer.detect_key(file)
                modulations = []

            progress.update(task, completed=True)

        # Display key
        confidence_pct = confidence * 100
        if confidence_pct >= 80:
            confidence_color = "green"
        elif confidence_pct >= 60:
            confidence_color = "yellow"
        else:
            confidence_color = "red"

        console.print(f"[bold]Detected Key:[/bold] [cyan]{key_name}[/cyan]")
        console.print(f"[bold]Confidence:[/bold] [{confidence_color}]{confidence_pct:.1f}%[/{confidence_color}]")

        if detail and modulations:
            console.print()
            console.print("[bold]Key Modulations:[/bold]")
            for mod in modulations:
                time_str = f"{int(mod.time // 60)}:{mod.time % 60:05.2f}"
                console.print(f"  [{time_str}] {mod.from_key} → {mod.to_key}")

    except Exception as e:
        utils.handle_error(e, "theory:key")
        raise typer.Exit(1)


@app.command("chords")
@utils.with_error_handling
def theory_chords(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, timeline, list)"),
    roman: bool = typer.Option(False, "--roman", "-r", help="Include Roman numeral analysis"),
    min_duration: float = typer.Option(0.25, "--min-duration", help="Minimum chord duration (seconds)"),
) -> None:
    """Detect chord progression in an audio file"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]Chord Progression Analysis[/bold cyan]")
        console.print(f"  File: [green]{file.name}[/green]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Detecting chords...", total=None)

            from ....core.analysis import MusicTheoryAnalyzer
            analyzer = MusicTheoryAnalyzer(min_chord_duration=min_duration)
            analysis = analyzer.analyze(file)

            progress.update(task, completed=True)

        chords = analysis.chord_progression

        if not chords:
            console.print("[yellow]No chords detected.[/yellow]")
            return

        console.print(f"[bold]Key:[/bold] [cyan]{analysis.key}[/cyan]")
        console.print(f"[bold]Chords detected:[/bold] {len(chords)}")
        console.print()

        if format == "table":
            # Table format
            table = Table(title="Chord Progression")
            table.add_column("Time", style="dim")
            table.add_column("Chord", style="cyan")
            if roman:
                table.add_column("Function", style="yellow")
            table.add_column("Duration", justify="right")
            table.add_column("Confidence", justify="right", style="green")

            for chord in chords:
                time_str = f"{chord.start_time:.2f}s"
                duration_str = f"{chord.duration:.2f}s"
                confidence_str = f"{chord.confidence * 100:.0f}%"

                if roman:
                    table.add_row(
                        time_str, chord.chord, chord.roman_numeral,
                        duration_str, confidence_str
                    )
                else:
                    table.add_row(time_str, chord.chord, duration_str, confidence_str)

            console.print(table)

        elif format == "timeline":
            # Timeline format
            console.print("[bold]Timeline:[/bold]")
            for chord in chords:
                time_str = f"{chord.start_time:6.2f}s"
                bar_width = min(int(chord.duration * 10), 40)
                bar = "█" * bar_width

                if roman:
                    console.print(f"  {time_str} [cyan]{chord.chord:6}[/cyan] [yellow]{chord.roman_numeral:5}[/yellow] {bar}")
                else:
                    console.print(f"  {time_str} [cyan]{chord.chord:6}[/cyan] {bar}")

        else:  # list format
            # Simple list format
            chord_str = " | ".join([c.chord for c in chords])
            console.print(f"[cyan]{chord_str}[/cyan]")

            if roman:
                roman_str = " | ".join([c.roman_numeral for c in chords])
                console.print(f"[yellow]{roman_str}[/yellow]")

    except Exception as e:
        utils.handle_error(e, "theory:chords")
        raise typer.Exit(1)


@app.command("harmony")
@utils.with_error_handling
def theory_harmony(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    roman: bool = typer.Option(True, "--roman/--no-roman", help="Show Roman numeral analysis"),
) -> None:
    """Perform full harmonic analysis on an audio file"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]Full Harmonic Analysis[/bold cyan]")
        console.print(f"  File: [green]{file.name}[/green]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Performing harmonic analysis...", total=None)

            analyzer = _get_analyzer()
            analysis = analyzer.analyze(file)

            progress.update(task, completed=True)

        # Summary table
        summary_table = Table(title="Harmonic Analysis Summary", show_header=False)
        summary_table.add_column("Property", style="bold")
        summary_table.add_column("Value", style="cyan")

        summary_table.add_row("Key", analysis.key)
        summary_table.add_row("Key Confidence", f"{analysis.key_confidence * 100:.1f}%")
        summary_table.add_row("Duration", f"{analysis.duration:.2f}s")
        summary_table.add_row("Chord Changes", str(len(analysis.chord_progression)))
        summary_table.add_row("Harmonic Rhythm", f"{analysis.harmonic_rhythm:.2f} changes/bar")
        summary_table.add_row("Modulations", str(len(analysis.modulations)))

        console.print(summary_table)

        # Chord progression
        if analysis.chord_progression:
            console.print()
            console.print("[bold]Chord Progression:[/bold]")

            if roman:
                # Show with Roman numerals
                chord_pairs = [f"{c.chord} ({c.roman_numeral})" for c in analysis.chord_progression[:12]]
            else:
                chord_pairs = [c.chord for c in analysis.chord_progression[:12]]

            progression_str = " → ".join(chord_pairs)
            console.print(f"  [cyan]{progression_str}[/cyan]")

            if len(analysis.chord_progression) > 12:
                console.print(f"  [dim]... and {len(analysis.chord_progression) - 12} more[/dim]")

        # Modulations
        if analysis.modulations:
            console.print()
            console.print("[bold]Key Modulations:[/bold]")
            for mod in analysis.modulations:
                time_str = f"{int(mod.time // 60)}:{mod.time % 60:05.2f}"
                console.print(f"  [dim]{time_str}[/dim] {mod.from_key} → [yellow]{mod.to_key}[/yellow]")

        # Scale notes
        console.print()
        scale_notes = analyzer.get_scale_notes(analysis.key_root, analysis.key_mode)
        console.print(f"[bold]Scale Notes:[/bold] [cyan]{' '.join(scale_notes)}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "theory:harmony")
        raise typer.Exit(1)


@app.command("scale")
@utils.with_error_handling
def theory_scale(
    key: str = typer.Argument(..., help="Key name (e.g., 'C major', 'Am', 'F# minor')"),
) -> None:
    """Show scale notes for a given key"""
    try:
        from ....core.analysis.chord_templates import NOTE_NAMES, NOTE_TO_PC

        # Parse key
        key = key.strip()
        parts = key.replace('-', ' ').split()

        if len(parts) == 1:
            # Single word: "Am" or "C"
            note = parts[0]
            if note.endswith('m') or note.endswith('min'):
                mode = 'minor'
                note = note.rstrip('m').rstrip('in')
            else:
                mode = 'major'
        elif len(parts) == 2:
            note = parts[0]
            mode_str = parts[1].lower()
            mode = 'minor' if mode_str in ['minor', 'min', 'm'] else 'major'
        else:
            console.print(f"[red]Error: Invalid key format. Use 'C major' or 'Am'[/red]")
            raise typer.Exit(1)

        # Get root pitch class
        note = note[0].upper() + note[1:] if len(note) > 1 else note.upper()
        if note not in NOTE_TO_PC:
            console.print(f"[red]Error: Unknown note: {note}[/red]")
            raise typer.Exit(1)

        root_pc = NOTE_TO_PC[note]
        key_name = f"{note} {mode}"

        # Get scale notes
        analyzer = _get_analyzer()
        scale_notes = analyzer.get_scale_notes(root_pc, mode)

        console.print(f"[bold cyan]{key_name} Scale[/bold cyan]")
        console.print()

        # Show scale degrees
        if mode == 'major':
            degrees = ['1', '2', '3', '4', '5', '6', '7']
        else:
            degrees = ['1', '2', 'b3', '4', '5', 'b6', 'b7']

        table = Table(show_header=True)
        table.add_column("Degree", style="dim")
        table.add_column("Note", style="cyan")

        for degree, note in zip(degrees, scale_notes):
            table.add_row(degree, note)

        console.print(table)

        # Show scale as single line
        console.print()
        console.print(f"[bold]Scale:[/bold] [cyan]{' - '.join(scale_notes)}[/cyan]")

        # Show common chords
        console.print()
        console.print("[bold]Common Chords in Key:[/bold]")
        if mode == 'major':
            console.print(f"  I    : [cyan]{scale_notes[0]}[/cyan] major")
            console.print(f"  ii   : [cyan]{scale_notes[1]}[/cyan] minor")
            console.print(f"  iii  : [cyan]{scale_notes[2]}[/cyan] minor")
            console.print(f"  IV   : [cyan]{scale_notes[3]}[/cyan] major")
            console.print(f"  V    : [cyan]{scale_notes[4]}[/cyan] major")
            console.print(f"  vi   : [cyan]{scale_notes[5]}[/cyan] minor")
            console.print(f"  vii° : [cyan]{scale_notes[6]}[/cyan] diminished")
        else:
            console.print(f"  i    : [cyan]{scale_notes[0]}[/cyan] minor")
            console.print(f"  ii°  : [cyan]{scale_notes[1]}[/cyan] diminished")
            console.print(f"  III  : [cyan]{scale_notes[2]}[/cyan] major")
            console.print(f"  iv   : [cyan]{scale_notes[3]}[/cyan] minor")
            console.print(f"  v    : [cyan]{scale_notes[4]}[/cyan] minor")
            console.print(f"  VI   : [cyan]{scale_notes[5]}[/cyan] major")
            console.print(f"  VII  : [cyan]{scale_notes[6]}[/cyan] major")

    except typer.Exit:
        raise
    except Exception as e:
        utils.handle_error(e, "theory:scale")
        raise typer.Exit(1)
