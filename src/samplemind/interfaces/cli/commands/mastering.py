#!/usr/bin/env python3
"""
Mastering Assistant Commands

Professional mastering analysis with platform-specific loudness targets.

Usage:
    samplemind mastering:analyze <file> --platform spotify
    samplemind mastering:compare <file1> <file2>
    samplemind mastering:targets
"""

from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from samplemind.core.processing.mastering_analyzer import MasteringAnalyzer
from samplemind.core.processing.loudness_analyzer import PLATFORM_TARGETS
from samplemind.core.history.recent_files import add_recent_file

from . import utils

# Create mastering app group
app = typer.Typer(
    help="🎚️  Professional mastering assistant",
    no_args_is_help=True,
)

console = utils.console

# ============================================================================
# MAIN ANALYZE COMMAND
# ============================================================================

@app.command("analyze")
@utils.with_error_handling
@utils.async_command
async def analyze_mastering(
    file: Optional[Path] = typer.Argument(None, help="Audio file to analyze"),
    platform: str = typer.Option("spotify", "--platform", "-p", help="Target platform"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch file picker"),
    show_spectral: bool = typer.Option(True, "--spectral", help="Show spectral analysis"),
    show_stereo: bool = typer.Option(True, "--stereo", help="Show stereo analysis"),
):
    """Analyze audio for mastering readiness"""
    try:
        # Handle file selection
        if not file or interactive:
            from samplemind.utils.file_picker import select_audio_file
            console.print("[cyan]📁 Opening file picker...[/cyan]")
            selected_file = select_audio_file(title="Select Audio File for Mastering Analysis")
            if not selected_file:
                console.print("[yellow]❌ No file selected[/yellow]")
                raise typer.Exit(1)
            file = selected_file
            console.print(f"[green]✅ Selected: {file.name}[/green]")

        # Validate platform
        if platform.lower() not in PLATFORM_TARGETS:
            console.print(f"[yellow]⚠️  Unknown platform '{platform}', using 'spotify'[/yellow]")
            platform = "spotify"

        # Load audio (in production, use librosa)
        try:
            import librosa
            audio, sr = librosa.load(str(file), sr=None, mono=False)
        except ImportError:
            console.print("[yellow]⚠️  librosa not available, using placeholder analysis[/yellow]")
            return

        # Analyze
        console.print()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Analyzing audio for mastering...", total=None)
            analyzer = MasteringAnalyzer()
            analysis = analyzer.analyze(audio, sr, platform.lower())

        # Display header
        console.print()
        console.print(f"[bold cyan]🎚️  Mastering Analysis[/bold cyan]")
        console.print(f"[dim]File: {file.name} | Platform: {analysis.target_platform.title()}[/dim]\n")

        # ====================================================================
        # LOUDNESS ANALYSIS SECTION
        # ====================================================================
        console.print("[bold]📊 Loudness Analysis[/bold]")

        loudness_table = Table(show_header=False, show_lines=False, padding=(0, 2))
        loudness_table.add_column(width=25, style="cyan")
        loudness_table.add_column(width=15, style="green", justify="right")
        loudness_table.add_column(style="dim")

        # Current vs Target
        loudness_table.add_row(
            "Current Loudness:",
            f"{analysis.loudness.integrated_loudness:.1f} LUFS",
            ""
        )
        loudness_table.add_row(
            "Target Loudness:",
            f"{analysis.platform_target:.1f} LUFS",
            "[bold cyan](Spotify standard)[/bold cyan]" if platform == "spotify" else ""
        )

        # Difference indicator
        diff = analysis.loudness_headroom
        if abs(diff) < 0.2:
            diff_color = "green"
            diff_status = "✅ Perfect"
        elif abs(diff) < 1.0:
            diff_color = "cyan"
            diff_status = "✅ Good"
        elif abs(diff) < 2.0:
            diff_color = "yellow"
            diff_status = "⚠️  Adjust"
        else:
            diff_color = "red"
            diff_status = "❌ Adjust"

        loudness_table.add_row(
            "Difference:",
            f"[{diff_color}]{diff:+.1f} dB[/{diff_color}]",
            diff_status
        )

        loudness_table.add_row("", "", "")  # Separator

        # Additional loudness metrics
        loudness_table.add_row(
            "Short-Term Loudness:",
            f"{analysis.loudness.short_term_loudness:.1f} LUFS",
            ""
        )
        loudness_table.add_row(
            "Momentary Loudness:",
            f"{analysis.loudness.momentary_loudness:.1f} LUFS",
            ""
        )
        loudness_table.add_row(
            "Loudness Range:",
            f"{analysis.loudness.loudness_range:.1f} LU",
            ""
        )

        loudness_table.add_row("", "", "")  # Separator

        loudness_table.add_row(
            "True Peak:",
            f"{analysis.loudness.true_peak:.1f} dBFS",
            "✅ OK" if not analysis.has_clipping else "❌ CLIPPING"
        )
        loudness_table.add_row(
            "Headroom to -1 dBTP:",
            f"{abs(analysis.loudness.true_peak) - 1:.1f} dB",
            ""
        )

        loudness_table.add_row(
            "Dynamic Range:",
            f"{analysis.loudness.dynamic_range:.1f} dB",
            ""
        )

        console.print(loudness_table)

        # ====================================================================
        # SPECTRAL BALANCE SECTION
        # ====================================================================
        if show_spectral:
            console.print()
            console.print("[bold]📈 Spectral Balance (relative to mids)[/bold]")

            spectral_table = Table(show_header=True, header_style="bold cyan", show_lines=False)
            spectral_table.add_column("Frequency Band", style="cyan", width=15)
            spectral_table.add_column("Level", justify="right", width=12, style="green")
            spectral_table.add_column("Status", width=20)

            bands = [
                ("Sub (20-60 Hz)", "sub"),
                ("Bass (60-250 Hz)", "bass"),
                ("Mids (250-2k Hz)", "mids"),
                ("Highs (2k+ Hz)", "highs"),
            ]

            for band_name, band_key in bands:
                level = analysis.spectral_balance.get(band_key, 0)

                # Color code based on level
                if abs(level) < 2:
                    status = "✅ Balanced"
                    color = "green"
                elif abs(level) < 6:
                    status = "⚠️  Slight deviation"
                    color = "yellow"
                else:
                    status = "❌ Needs correction"
                    color = "red"

                spectral_table.add_row(
                    band_name,
                    f"[{color}]{level:+.1f} dB[/{color}]",
                    status
                )

            console.print(spectral_table)

            console.print()
            console.print(f"[dim]Estimated Brightness: {analysis.estimated_brightness:.0%}[/dim]")

        # ====================================================================
        # STEREO ANALYSIS SECTION
        # ====================================================================
        if show_stereo:
            console.print()
            console.print("[bold]🔀 Stereo Analysis[/bold]")

            stereo_table = Table(show_header=False, show_lines=False, padding=(0, 2))
            stereo_table.add_column(width=25, style="cyan")
            stereo_table.add_column(width=15, style="green", justify="right")
            stereo_table.add_column(style="dim")

            # Stereo width
            width = analysis.stereo_width
            if width < 10:
                width_status = "Nearly mono"
            elif width > 80:
                width_status = "Very wide"
            else:
                width_status = "Balanced"

            stereo_table.add_row("Stereo Width:", f"{width:.1f}%", width_status)

            # Phase correlation
            corr = analysis.phase_correlation
            if corr > 0.9:
                corr_status = "✅ Excellent"
            elif corr > 0.7:
                corr_status = "✅ Good"
            elif corr > 0.5:
                corr_status = "⚠️  Check mono"
            else:
                corr_status = "❌ Mono issues"

            stereo_table.add_row("Phase Correlation:", f"{corr:.2f}", corr_status)

            # Center energy
            center = analysis.center_energy
            stereo_table.add_row("Center Energy:", f"{center:.1f}%", "")

            console.print(stereo_table)

        # ====================================================================
        # RECOMMENDATIONS SECTION
        # ====================================================================
        console.print()
        console.print("[bold]💡 Mastering Recommendations[/bold]")

        recommendations = analyzer.get_recommendations(analysis)
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")

        # ====================================================================
        # GRADE & SUMMARY
        # ====================================================================
        console.print()

        grade = analyzer.get_mastering_grade(analysis)
        grade_emoji = {
            "A": "🌟",
            "B": "👍",
            "C": "📝",
            "D": "⚠️",
            "F": "❌"
        }.get(grade, "?")

        grade_color = {
            "A": "green",
            "B": "green",
            "C": "yellow",
            "D": "yellow",
            "F": "red"
        }.get(grade, "white")

        console.print(
            f"[bold]Mastering Grade: [{grade_color}]{grade_emoji} {grade}[/{grade_color}][/bold]"
        )

        # Save to recent files
        add_recent_file(file, "PROFESSIONAL", ["mastering", platform])

    except utils.CLIError as e:
        utils.handle_error(e, "mastering:analyze")
        raise typer.Exit(1)


# ============================================================================
# PLATFORM TARGETS COMMAND
# ============================================================================

@app.command("targets")
@utils.with_error_handling
def show_targets():
    """Show loudness targets for all platforms"""
    console.print()
    console.print("[bold cyan]🎚️  Platform Loudness Targets[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("Platform", style="cyan", width=20)
    table.add_column("Target", justify="right", width=12, style="green")
    table.add_column("True Peak", justify="right", width=12, style="green")
    table.add_column("Description", width=40)

    for platform, targets in PLATFORM_TARGETS.items():
        table.add_row(
            platform.title(),
            f"{targets['integrated_loudness']:.1f} LUFS",
            f"{targets['true_peak']:.1f} dBTP",
            targets["description"]
        )

    console.print(table)

    console.print()
    console.print("[dim]Usage:[/dim]")
    console.print("  samplemind mastering:analyze song.wav --platform spotify")
    console.print("  samplemind mastering:analyze song.wav --platform youtube")


# ============================================================================
# COMPARE COMMAND (Placeholder)
# ============================================================================

@app.command("compare")
@utils.with_error_handling
async def compare_files(
    file1: Path = typer.Argument(..., help="First audio file"),
    file2: Path = typer.Argument(..., help="Second audio file for comparison"),
):
    """Compare loudness of two files (coming soon)"""
    console.print()
    console.print("[yellow]⏳ Loudness comparison coming soon![/yellow]")
    console.print()
    console.print(f"Will compare:")
    console.print(f"  • {file1.name}")
    console.print(f"  • {file2.name}")


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = ["app"]
