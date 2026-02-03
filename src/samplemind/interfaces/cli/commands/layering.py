#!/usr/bin/env python3
"""Sample Layering Analysis Commands"""

from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from samplemind.core.processing.layering_analyzer import LayeringAnalyzer
from . import utils

app = typer.Typer(help="🔀 Sample layering & phase analysis", no_args_is_help=True)
console = utils.console

@app.command("analyze")
@utils.with_error_handling
@utils.async_command
async def analyze_layering(
    file1: Optional[Path] = typer.Argument(None, help="First audio file"),
    file2: Optional[Path] = typer.Argument(None, help="Second audio file"),
) -> None:
    """Analyze compatibility of two samples for layering"""
    try:
        if not file1:
            from samplemind.utils.file_picker import select_audio_file
            file1 = select_audio_file(title="Select first sample")
            if not file1:
                raise typer.Exit(1)

        if not file2:
            from samplemind.utils.file_picker import select_audio_file
            file2 = select_audio_file(title="Select second sample")
            if not file2:
                raise typer.Exit(1)

        # Load audio
        try:
            import librosa
            audio1, sr1 = librosa.load(str(file1), sr=None, mono=True)
            audio2, sr2 = librosa.load(str(file2), sr=None, mono=True)
            sr = sr1
        except ImportError:
            console.print("[yellow]⚠️  librosa not available[/yellow]")
            return

        console.print()
        console.print(f"[bold cyan]🔀 Layering Analysis[/bold cyan]")
        console.print(f"[cyan]Sample 1: {file1.name}[/cyan]")
        console.print(f"[cyan]Sample 2: {file2.name}[/cyan]\n")

        # Analyze
        analyzer = LayeringAnalyzer()
        analysis = analyzer.analyze(audio1, audio2, sr)

        # Display score
        grade_color = "green" if analysis.compatibility_score >= 8 else \
                     "yellow" if analysis.compatibility_score >= 6 else "red"
        console.print(f"[bold]Compatibility Score: [{grade_color}]{analysis.compatibility_score:.1f}/10[/{grade_color}][/bold]")
        console.print(f"[bold]Can Layer: {'✅ Yes' if analysis.can_layer else '❌ Not recommended'}[/bold]\n")

        # Phase analysis
        console.print("[bold]Phase Relationship:[/bold]")
        phase_table = Table(show_header=False, show_lines=False, padding=(0, 2))
        phase_table.add_column(width=20, style="cyan")
        phase_table.add_column()
        phase_table.add_row("Correlation:", f"{analysis.phase_correlation:.2f}")
        phase_table.add_row("Status:", analysis.phase_status.replace("-", " ").title())
        console.print(phase_table)

        # Frequency masking
        console.print()
        console.print("[bold]Frequency Masking:[/bold]")
        if analysis.frequency_masks:
            mask_table = Table(show_header=True, header_style="bold cyan", show_lines=False)
            mask_table.add_column("Frequency", style="cyan")
            mask_table.add_column("Power Diff", justify="right", style="green")
            mask_table.add_column("Severity", style="yellow")
            for mask in analysis.frequency_masks[:5]:
                mask_table.add_row(
                    f"{mask.frequency_hz:.0f} Hz",
                    f"{mask.power_difference_db:+.1f} dB",
                    mask.severity.upper()
                )
            console.print(mask_table)
        else:
            console.print("[green]✅ No frequency masking detected[/green]")

        # Transients
        console.print()
        console.print("[bold]Transient Analysis:[/bold]")
        console.print(f"  Onset Offset: {analysis.transient_offset_ms:.1f} ms")
        console.print(f"  Conflict: {'⚠️  Yes' if analysis.transient_conflict else '✅ No'}")

        # Loudness
        console.print()
        console.print("[bold]Loudness Balance:[/bold]")
        console.print(f"  Difference: {analysis.loudness_difference_db:+.1f} dB")
        console.print(f"  Ratio: {analysis.loudness_ratio:.2f}:1")

        # Recommendations
        console.print()
        console.print("[bold cyan]💡 Recommendations:[/bold cyan]")
        for rec in analysis.recommended_actions:
            console.print(f"  • {rec}")

    except utils.CLIError as e:
        utils.handle_error(e, "layer:analyze")
        raise typer.Exit(1)

__all__ = ["app"]
