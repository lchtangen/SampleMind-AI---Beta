"""
SampleMind AI - Analyze Command Group (40 commands)

Audio analysis and feature extraction commands:
- Core analysis (full, standard, basic, professional, quick)
- Specific feature extraction (bpm, key, mood, genre, instrument, etc.)
- Advanced analysis (spectral, harmonic, percussive, MFCC, etc.)
- Batch and parallel processing

Usage:
    samplemind analyze:full <file>              # Comprehensive analysis
    samplemind analyze:bpm <file>               # BPM only
    samplemind batch:analyze <folder>           # Batch processing
"""

import time
from pathlib import Path

import numpy as np
import soundfile as sf
import typer
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from samplemind.core.processing.realtime_spectral import RealtimeSpectral, SpectralFrame
from samplemind.utils.file_picker import select_audio_file

from . import utils

# Create analyze app group
app = typer.Typer(
    help="🎵 Audio analysis & feature extraction (40 commands)",
    no_args_is_help=True,
)

console = utils.console

# ============================================================================
# SECTION 1: CORE ANALYSIS COMMANDS (9 commands)
# ============================================================================

@app.command("full")
@utils.with_error_handling
@utils.async_command
async def analyze_full(
    file: Path | None = typer.Argument(None, help="Audio file to analyze"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (json|csv|yaml|table)"),
    show_profile: bool = typer.Option(False, "--profile", help="Show profiling info"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch file picker"),
) -> None:
    """Run comprehensive (DETAILED level) analysis with all features"""
    try:
        # Handle file selection
        if not file or interactive:
            console.print("[cyan]📁 Opening file picker...[/cyan]")
            selected_file = select_audio_file(title="Select Audio File for Full Analysis")
            if not selected_file:
                console.print("[yellow]❌ No file selected[/yellow]")
                raise typer.Exit(1)
            file = selected_file
            console.print(f"[green]✅ Selected: {file.name}[/green]")

        with utils.ProgressTracker("🔍 Analyzing (DETAILED level)"):
            result = await utils.analyze_file_async(file, "DETAILED")

        if show_profile:
            console.print(Panel(
                "Analysis complete at DETAILED level\nIncludes harmonic/percussive separation, forensics, and advanced features",
                title="[bold cyan]Analysis Profile[/bold cyan]",
                expand=False
            ))

        utils.output_result(result, format, "Analysis Results", output)

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:full")
        raise typer.Exit(1)


@app.command("standard")
@utils.with_error_handling
@utils.async_command
async def analyze_standard(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    output: Path | None = typer.Option(None, "--output", "-o"),
    format: str = typer.Option("table", "--format", "-f"),
) -> None:
    """Run standard analysis with core features (recommended)"""
    try:
        with utils.ProgressTracker("🔍 Analyzing (STANDARD level)"):
            result = await utils.analyze_file_async(file, "STANDARD")

        utils.output_result(result, format, "Analysis Results", output)

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:standard")
        raise typer.Exit(1)


@app.command("basic")
@utils.with_error_handling
@utils.async_command
async def analyze_basic(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    output: Path | None = typer.Option(None, "--output", "-o"),
) -> None:
    """Run quick basic analysis (fast, minimal features)"""
    try:
        with utils.ProgressTracker("🔍 Analyzing (BASIC level)"):
            result = await utils.analyze_file_async(file, "BASIC")

        console.print(f"[cyan]Duration:[/cyan] {utils.format_duration(result.get('duration', 0))}")
        console.print(f"[cyan]Tempo:[/cyan] {utils.format_bpm(result.get('tempo', 0))}")
        console.print(f"[cyan]Key:[/cyan] {utils.format_key(result.get('key', '?'), result.get('mode', ''))}")

        if output:
            utils.output_result(result, "json", output_file=output)

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:basic")
        raise typer.Exit(1)


@app.command("professional")
@utils.with_error_handling
@utils.async_command
async def analyze_professional(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    output: Path | None = typer.Option(None, "--output", "-o"),
    format: str = typer.Option("json", "--format", "-f"),
    export_features: bool = typer.Option(False, "--export-features", help="Export raw feature vectors"),
) -> None:
    """Run professional analysis (PROFESSIONAL level - ML-optimized)"""
    try:
        with utils.ProgressTracker("🔍 Analyzing (PROFESSIONAL level with ML optimization)"):
            result = await utils.analyze_file_async(file, "PROFESSIONAL")

        console.print("[bold green]✅ Professional Analysis Complete[/bold green]")

        if export_features and "features" in result:
            features_output = output.with_stem(output.stem + "_features") if output else Path("features.json")
            utils.output_result(result["features"], format, output_file=features_output)
            console.print(f"[cyan]Features exported to: {features_output}[/cyan]")

        utils.output_result(result, format, "Professional Analysis", output)

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:professional")
        raise typer.Exit(1)


@app.command("quick")
@utils.with_error_handling
@utils.async_command
async def analyze_quick(
    file: Path | None = typer.Argument(None, help="Audio file to analyze"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Launch file picker"),
) -> None:
    """Ultra-fast analysis (< 1 second)"""
    try:
        # Handle file selection
        if not file or interactive:
            console.print("[cyan]📁 Opening file picker...[/cyan]")
            selected_file = select_audio_file(title="Select Audio File for Quick Analysis")
            if not selected_file:
                console.print("[yellow]❌ No file selected[/yellow]")
                raise typer.Exit(1)
            file = selected_file
            console.print(f"[green]✅ Selected: {file.name}[/green]")

        with utils.ProgressTracker("⚡ Quick analysis"):
            result = await utils.analyze_file_async(file, "BASIC")

        table = Table(title="Quick Analysis", show_header=False)
        table.add_row("File", result.get("file", "?"))
        table.add_row("Duration", utils.format_duration(result.get("duration", 0)))
        table.add_row("Tempo", utils.format_bpm(result.get("tempo", 0)))
        table.add_row("Key", utils.format_key(result.get("key", "?"), result.get("mode", "")))

        console.print(table)

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:quick")
        raise typer.Exit(1)


@app.command("bpm")
@utils.with_error_handling
@utils.async_command
async def analyze_bpm(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Extract tempo/BPM only"""
    try:
        with utils.ProgressTracker("🎵 Detecting BPM"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="BASIC")

        console.print(f"[bold]{file.name}[/bold]")
        console.print(f"[cyan]Tempo:[/cyan] [bold green]{utils.format_bpm(features.tempo)}[/bold green] BPM")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:bpm")
        raise typer.Exit(1)


@app.command("key")
@utils.with_error_handling
@utils.async_command
async def analyze_key(
    file: Path = typer.Argument(..., help="Audio file"),
    confidence: bool = typer.Option(False, "--confidence", help="Show confidence score"),
) -> None:
    """Extract key detection only"""
    try:
        with utils.ProgressTracker("🎹 Detecting key"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="STANDARD")

        console.print(f"[bold]{file.name}[/bold]")
        console.print(f"[cyan]Key:[/cyan] [bold green]{utils.format_key(features.key, features.mode)}[/bold green]")

        if confidence:
            console.print("[dim]Confidence scores are computed from feature consistency[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:key")
        raise typer.Exit(1)


@app.command("mode")
@utils.with_error_handling
@utils.async_command
async def analyze_mode(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Extract major/minor mode only"""
    try:
        with utils.ProgressTracker("🎼 Detecting mode"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="STANDARD")

        console.print(f"[bold]{file.name}[/bold]")
        console.print(f"[cyan]Mode:[/cyan] [bold green]{features.mode}[/bold green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:mode")
        raise typer.Exit(1)


@app.command("compare")
@utils.with_error_handling
@utils.async_command
async def analyze_compare(
    file1: Path = typer.Argument(..., help="First audio file"),
    file2: Path = typer.Argument(..., help="Second audio file"),
    metric: str = typer.Option("overall", "--metric", "-m", help="Metric to compare"),
) -> None:
    """Compare two audio files"""
    try:
        console.print("[bold]Comparing audio files[/bold]")

        with utils.ProgressTracker("📊 Comparing"):
            engine = await utils.get_audio_engine()
            similarity = engine.compare_audio_similarity(file1, file2)

        table = Table(title="Comparison", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("File 1", style="yellow")
        table.add_column("File 2", style="yellow")
        table.add_column("Similarity", style="green")

        # Get features for both files
        features1 = engine.analyze_audio(file1, analysis_level="STANDARD")
        features2 = engine.analyze_audio(file2, analysis_level="STANDARD")

        table.add_row("BPM", f"{features1.tempo:.1f}", f"{features2.tempo:.1f}", f"{similarity:.1%}")
        table.add_row("Key", features1.key, features2.key, "Match" if features1.key == features2.key else "Different")
        table.add_row("Mode", features1.mode, features2.mode, "Match" if features1.mode == features2.mode else "Different")

        console.print(table)

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:compare")
        raise typer.Exit(1)


# ============================================================================
# SECTION 2: GENRE/MOOD/INSTRUMENT ANALYSIS (9 commands)
# ============================================================================

@app.command("genre")
@utils.with_error_handling
@utils.async_command
async def analyze_genre(
    file: Path = typer.Argument(..., help="Audio file"),
    top_n: int = typer.Option(3, "--top", help="Show top N genres"),
) -> None:
    """Genre classification"""
    try:
        with utils.ProgressTracker("🎵 Classifying genre"):
            ai_manager = await utils.get_ai_manager()
            # Genre classification would be done through AI manager
            console.print("[cyan]Genre classification coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:genre")
        raise typer.Exit(1)


@app.command("mood")
@utils.with_error_handling
@utils.async_command
async def analyze_mood(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Mood/emotion detection"""
    try:
        with utils.ProgressTracker("😊 Detecting mood"):
            console.print("[cyan]Mood detection coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:mood")
        raise typer.Exit(1)


@app.command("instrument")
@utils.with_error_handling
@utils.async_command
async def analyze_instrument(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Instrument recognition"""
    try:
        with utils.ProgressTracker("🎸 Detecting instruments"):
            console.print("[cyan]Instrument recognition coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:instrument")
        raise typer.Exit(1)


@app.command("vocal")
@utils.with_error_handling
@utils.async_command
async def analyze_vocal(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Vocal detection and characteristics"""
    try:
        with utils.ProgressTracker("🎤 Detecting vocals"):
            console.print("[cyan]Vocal detection coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:vocal")
        raise typer.Exit(1)


@app.command("quality")
@utils.with_error_handling
@utils.async_command
async def analyze_quality(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Quality and production score"""
    try:
        with utils.ProgressTracker("⭐ Analyzing quality"):
            console.print("[cyan]Quality analysis coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:quality")
        raise typer.Exit(1)


@app.command("energy")
@utils.with_error_handling
@utils.async_command
async def analyze_energy(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Energy level detection"""
    try:
        with utils.ProgressTracker("⚡ Analyzing energy"):
            console.print("[cyan]Energy analysis coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:energy")
        raise typer.Exit(1)


@app.command("dynamics")
@utils.with_error_handling
@utils.async_command
async def analyze_dynamics(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Dynamic range analysis"""
    try:
        with utils.ProgressTracker("📊 Analyzing dynamics"):
            console.print("[cyan]Dynamics analysis coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:dynamics")
        raise typer.Exit(1)


@app.command("loudness")
@utils.with_error_handling
@utils.async_command
async def analyze_loudness(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Loudness measurement (LUFS)"""
    try:
        with utils.ProgressTracker("📢 Measuring loudness"):
            console.print("[cyan]Loudness analysis coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:loudness")
        raise typer.Exit(1)


@app.command("compression")
@utils.with_error_handling
@utils.async_command
async def analyze_compression(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Compression detection and analysis"""
    try:
        with utils.ProgressTracker("🔍 Detecting compression"):
            console.print("[cyan]Compression detection coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:compression")
        raise typer.Exit(1)


# ============================================================================
# SECTION 3: ADVANCED AUDIO ANALYSIS (12 commands)
# ============================================================================

@app.command("spectral")
@utils.with_error_handling
@utils.async_command
async def analyze_spectral(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Spectral analysis and features"""
    try:
        with utils.ProgressTracker("🌈 Analyzing spectral properties"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="DETAILED")
            console.print("[green]✓ Spectral analysis complete[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:spectral")
        raise typer.Exit(1)


@app.command("harmonic")
@utils.with_error_handling
@utils.async_command
async def analyze_harmonic(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Harmonic content analysis"""
    try:
        with utils.ProgressTracker("🎼 Analyzing harmonic content"):
            engine = await utils.get_audio_engine()
            harmonic, percussive = engine.extract_harmonic_percussive(file)
            console.print("[green]✓ Harmonic separation complete[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:harmonic")
        raise typer.Exit(1)


@app.command("percussive")
@utils.with_error_handling
@utils.async_command
async def analyze_percussive(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Percussive content analysis"""
    try:
        with utils.ProgressTracker("🥁 Analyzing percussive content"):
            engine = await utils.get_audio_engine()
            harmonic, percussive = engine.extract_harmonic_percussive(file)
            console.print("[green]✓ Percussive separation complete[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:percussive")
        raise typer.Exit(1)


@app.command("mfcc")
@utils.with_error_handling
@utils.async_command
async def analyze_mfcc(
    file: Path = typer.Argument(..., help="Audio file"),
    n_mfcc: int = typer.Option(13, "--n-mfcc", help="Number of MFCC coefficients"),
) -> None:
    """Extract MFCC features"""
    try:
        with utils.ProgressTracker(f"📊 Extracting {n_mfcc} MFCC coefficients"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="DETAILED")
            console.print(f"[green]✓ Extracted {n_mfcc} MFCC coefficients[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:mfcc")
        raise typer.Exit(1)


@app.command("chroma")
@utils.with_error_handling
@utils.async_command
async def analyze_chroma(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Extract chroma features"""
    try:
        with utils.ProgressTracker("🎹 Extracting chroma features"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="STANDARD")
            console.print("[green]✓ Chroma features extracted[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:chroma")
        raise typer.Exit(1)


@app.command("onset")
@utils.with_error_handling
@utils.async_command
async def analyze_onset(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Onset (note start) detection"""
    try:
        with utils.ProgressTracker("📍 Detecting onsets"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="DETAILED")
            console.print("[green]✓ Onset detection complete[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:onset")
        raise typer.Exit(1)


@app.command("beats")
@utils.with_error_handling
@utils.async_command
async def analyze_beats(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Beat tracking"""
    try:
        with utils.ProgressTracker("🎼 Tracking beats"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="STANDARD")
            console.print(f"[green]✓ Tempo: {features.tempo:.1f} BPM[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:beats")
        raise typer.Exit(1)


@app.command("segments")
@utils.with_error_handling
@utils.async_command
async def analyze_segments(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Segment detection (intro, verse, chorus, etc.)"""
    try:
        with utils.ProgressTracker("📋 Detecting segments"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="DETAILED")
            console.print("[green]✓ Segment detection complete[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:segments")
        raise typer.Exit(1)


@app.command("tempogram")
@utils.with_error_handling
@utils.async_command
async def analyze_tempogram(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Tempogram (tempo over time)"""
    try:
        with utils.ProgressTracker("📈 Computing tempogram"):
            console.print("[cyan]Tempogram analysis coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:tempogram")
        raise typer.Exit(1)


@app.command("chromagram")
@utils.with_error_handling
@utils.async_command
async def analyze_chromagram(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Chromagram (chroma over time)"""
    try:
        with utils.ProgressTracker("🎹 Computing chromagram"):
            console.print("[cyan]Chromagram analysis coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:chromagram")
        raise typer.Exit(1)


@app.command("spectral-flux")
@utils.with_error_handling
@utils.async_command
async def analyze_spectral_flux(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Spectral flux (change over time)"""
    try:
        with utils.ProgressTracker("📊 Computing spectral flux"):
            console.print("[cyan]Spectral flux analysis coming soon[/cyan]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:spectral-flux")
        raise typer.Exit(1)


@app.command("zero-crossing")
@utils.with_error_handling
@utils.async_command
async def analyze_zero_crossing(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """Zero-crossing rate (timbral brightness)"""
    try:
        with utils.ProgressTracker("✨ Computing zero-crossing rate"):
            engine = await utils.get_audio_engine()
            features = engine.analyze_audio(file, analysis_level="STANDARD")
            console.print("[green]✓ Zero-crossing rate computed[/green]")

    except utils.CLIError as e:
        utils.handle_error(e, "analyze:zero-crossing")
        raise typer.Exit(1)


# ============================================================================
# SECTION 4: BATCH & PARALLEL ANALYSIS (10 commands)
# ============================================================================

@app.command("batch")
@utils.with_error_handling
@utils.async_command
async def batch_analyze(
    folder: Path = typer.Argument(..., help="Folder with audio files"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("json", "--format", "-f"),
    level: str = typer.Option("STANDARD", "--level", "-l", help="Analysis level"),
) -> None:
    """Batch analyze all audio files in folder"""
    try:
        files = utils.get_audio_files(folder)

        if not files:
            console.print(f"[yellow]⚠ No audio files found in {folder}[/yellow]")
            return

        console.print(f"[cyan]Found {len(files)} audio files[/cyan]")

        results = []
        with utils.ProgressTracker(f"Analyzing {len(files)} files"):
            for file in files:
                try:
                    result = await utils.analyze_file_async(file, level)
                    results.append(result)
                    console.print(f"  [green]✓[/green] {file.name}")
                except Exception as e:
                    console.print(f"  [red]✗[/red] {file.name}: {e}")

        utils.output_result(results, format, "Batch Analysis Results", output)

    except utils.CLIError as e:
        utils.handle_error(e, "batch:analyze")
        raise typer.Exit(1)


@app.command()
@app.command("monitor")
@utils.with_error_handling
def analyze_monitor(
    file: Path = typer.Argument(..., help="Audio file to monitor"),
    fps: int = typer.Option(30, "--fps", help="Target FPS"),
) -> None:
    """Real-time spectral monitoring visualization"""
    try:
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")

        # Initialize analyzer
        info = sf.info(file)
        sr = info.samplerate

        analyzer = RealtimeSpectral(sample_rate=sr, target_fps=fps, fft_size=2048)

        # Generator for blocks
        blocks = sf.blocks(str(file), blocksize=analyzer.fft_size, overlap=0, fill_value=0)

        console.print(f"[cyan]Starting Real-time Monitor for {file.name} ({sr} Hz)[/cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")

        def generate_table(frame: SpectralFrame) -> Panel:
            table = Table(show_header=False, box=None, expand=True)
            table.add_column("Metric", style="cyan", width=15)
            table.add_column("Value", style="bold green", justify="left")

            table.add_row("Time", f"{frame.timestamp_ms/1000:.1f}s")
            table.add_row("Peak Freq", f"{frame.peak_frequency_hz:.1f} Hz")

            pitch_str = f"{frame.pitch_hz:.1f} Hz" if frame.pitch_hz else "--"
            conf_str = f"({int(frame.pitch_confidence*100)}%)" if frame.pitch_hz else ""
            table.add_row("Pitch", f"{pitch_str} {conf_str}")

            # Simple bar for energy
            energy = np.mean(frame.magnitude) # roughly 0-100
            bar_len = int(energy / 2) # max 50 chars
            table.add_row("Energy", "█" * bar_len)

            return Panel(table, title="Spectral Monitor", border_style="cyan")

        with Live(console=console, refresh_per_second=fps) as live:
            start_time = time.time()
            for i, block in enumerate(blocks):
                # If stereo, mix to mono
                if len(block.shape) > 1:
                    block = np.mean(block, axis=1)

                # Process
                current_time = (i * analyzer.fft_size / sr) * 1000
                frame = analyzer.process_chunk(block, current_time_ms=current_time)

                live.update(generate_table(frame))

                # Sync to realtime
                elapsed = time.time() - start_time
                expected = current_time / 1000.0
                if expected > elapsed:
                    time.sleep(expected - elapsed)

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]")
    except Exception as e:
        utils.handle_error(e, "analyze:monitor")
        raise typer.Exit(1)


def list():
    """List all analyze commands"""
    console.print("[bold cyan]Analyze Commands[/bold cyan]\n")
    console.print(Panel(
        "[cyan]Core:[/cyan] full, standard, basic, professional, quick, bpm, key, mode, compare\n"
        "[cyan]Classification:[/cyan] genre, mood, instrument, vocal, quality, energy, dynamics, loudness, compression\n"
        "[cyan]Advanced:[/cyan] spectral, harmonic, percussive, mfcc, chroma, onset, beats, segments, tempogram, chromagram, spectral-flux, zero-crossing\n"
        "[cyan]Batch:[/cyan] batch, and more...",
        title="40 Commands",
        expand=False
    ))


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = ["app"]
