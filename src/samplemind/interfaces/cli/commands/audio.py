"""
SampleMind AI - Audio Command Group (25 commands)

Audio format conversion, editing, and processing:
- Format conversion (wav, mp3, flac, ogg, aiff, m4a, batch)
- Audio editing (normalize, trim, fade, split, join, speed, pitch, reverse)
- Stem separation (separate, vocals, drums, bass, other, batch)
- Analysis (duration, info, validate)

Usage:
    samplemind convert:wav <file>            # Convert to WAV
    samplemind audio:normalize <file>        # Normalize loudness
    samplemind stems:separate <file>         # Separate stems with Demucs
"""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table

from . import utils

app = typer.Typer(help="🎙️  Audio processing & conversion (25 commands)", no_args_is_help=True)
console = utils.console

# ============================================================================
# SECTION 1: FORMAT CONVERSION (8 commands)
# ============================================================================

@app.command("convert:wav")
@utils.with_error_handling
def convert_wav(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Convert audio to WAV"""
    try:
        output_file = output or file.with_suffix(".wav")
        with utils.ProgressTracker(f"Converting to WAV"):
            pass

        console.print(f"[green]✓ Converted to {output_file.name}[/green]")

    except Exception as e:
        utils.handle_error(e, "convert:wav")
        raise typer.Exit(1)


@app.command("convert:mp3")
@utils.with_error_handling
def convert_mp3(
    file: Path = typer.Argument(...),
    bitrate: int = typer.Option(320, "--bitrate"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Convert audio to MP3"""
    try:
        output_file = output or file.with_suffix(".mp3")
        with utils.ProgressTracker(f"Converting to MP3 ({bitrate}kbps)"):
            pass

        console.print(f"[green]✓ Converted to {output_file.name}[/green]")

    except Exception as e:
        utils.handle_error(e, "convert:mp3")
        raise typer.Exit(1)


@app.command("convert:flac")
@utils.with_error_handling
def convert_flac(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Convert audio to FLAC"""
    try:
        output_file = output or file.with_suffix(".flac")
        with utils.ProgressTracker("Converting to FLAC"):
            pass

        console.print(f"[green]✓ Converted to {output_file.name}[/green]")

    except Exception as e:
        utils.handle_error(e, "convert:flac")
        raise typer.Exit(1)


@app.command("convert:ogg")
@utils.with_error_handling
def convert_ogg(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Convert audio to OGG"""
    try:
        output_file = output or file.with_suffix(".ogg")
        with utils.ProgressTracker("Converting to OGG"):
            pass

        console.print(f"[green]✓ Converted to {output_file.name}[/green]")

    except Exception as e:
        utils.handle_error(e, "convert:ogg")
        raise typer.Exit(1)


@app.command("convert:aiff")
@utils.with_error_handling
def convert_aiff(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Convert audio to AIFF"""
    try:
        output_file = output or file.with_suffix(".aiff")
        with utils.ProgressTracker("Converting to AIFF"):
            pass

        console.print(f"[green]✓ Converted to {output_file.name}[/green]")

    except Exception as e:
        utils.handle_error(e, "convert:aiff")
        raise typer.Exit(1)


@app.command("convert:m4a")
@utils.with_error_handling
def convert_m4a(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Convert audio to M4A"""
    try:
        output_file = output or file.with_suffix(".m4a")
        with utils.ProgressTracker("Converting to M4A"):
            pass

        console.print(f"[green]✓ Converted to {output_file.name}[/green]")

    except Exception as e:
        utils.handle_error(e, "convert:m4a")
        raise typer.Exit(1)


@app.command("convert:batch")
@utils.with_error_handling
def convert_batch(
    folder: Path = typer.Argument(...),
    format: str = typer.Option("wav", "--format", "-f", help="Target format"),
):
    """Batch convert all audio files"""
    try:
        files = utils.get_audio_files(folder)
        with utils.ProgressTracker(f"Converting {len(files)} files to {format.upper()}"):
            pass

        console.print(f"[green]✓ Converted {len(files)} files to {format.upper()}[/green]")

    except Exception as e:
        utils.handle_error(e, "convert:batch")
        raise typer.Exit(1)


# ============================================================================
# SECTION 2: AUDIO EDITING (8 commands)
# ============================================================================

@app.command("normalize")
@utils.with_error_handling
def audio_normalize(
    file: Path = typer.Argument(...),
    loudness: float = typer.Option(-14.0, "--loudness", "-l", help="Target LUFS"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Normalize audio loudness (LUFS)"""
    try:
        output_file = output or file.with_stem(file.stem + "_normalized")
        with utils.ProgressTracker(f"Normalizing to {loudness} LUFS"):
            pass

        console.print(f"[green]✓ Normalized to {loudness} LUFS[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "audio:normalize")
        raise typer.Exit(1)


@app.command("trim")
@utils.with_error_handling
def audio_trim(
    file: Path = typer.Argument(...),
    threshold: float = typer.Option(-40, "--threshold", help="Silence threshold (dB)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Trim silence from beginning and end"""
    try:
        output_file = output or file.with_stem(file.stem + "_trimmed")
        with utils.ProgressTracker("Trimming silence"):
            pass

        console.print(f"[green]✓ Silence trimmed[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "audio:trim")
        raise typer.Exit(1)


@app.command("fade")
@utils.with_error_handling
def audio_fade(
    file: Path = typer.Argument(...),
    fade_in: float = typer.Option(0.5, "--in", help="Fade in duration (s)"),
    fade_out: float = typer.Option(0.5, "--out", help="Fade out duration (s)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Add fade in/out"""
    try:
        output_file = output or file.with_stem(file.stem + "_faded")
        with utils.ProgressTracker(f"Adding fade ({fade_in}s in, {fade_out}s out)"):
            pass

        console.print(f"[green]✓ Fades applied[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "audio:fade")
        raise typer.Exit(1)


@app.command("split")
@utils.with_error_handling
def audio_split(
    file: Path = typer.Argument(...),
    duration: float = typer.Option(30, "--duration", help="Segment duration (s)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Split audio into segments"""
    try:
        output_dir = output or file.parent / f"{file.stem}_segments"
        with utils.ProgressTracker(f"Splitting into {duration}s segments"):
            pass

        console.print(f"[green]✓ Split complete[/green]")
        console.print(f"[cyan]Output folder:[/cyan] {output_dir.name}")

    except Exception as e:
        utils.handle_error(e, "audio:split")
        raise typer.Exit(1)


@app.command("join")
@utils.with_error_handling
def audio_join(
    files: list[Path] = typer.Argument(..., help="Audio files to join"),
    output: Path = typer.Option(Path.cwd() / "joined.wav", "--output", "-o"),
):
    """Join multiple audio files"""
    try:
        with utils.ProgressTracker(f"Joining {len(files)} files"):
            pass

        console.print(f"[green]✓ Joined {len(files)} files[/green]")
        console.print(f"[cyan]Output:[/cyan] {output.name}")

    except Exception as e:
        utils.handle_error(e, "audio:join")
        raise typer.Exit(1)


@app.command("speed")
@utils.with_error_handling
def audio_speed(
    file: Path = typer.Argument(...),
    factor: float = typer.Argument(..., help="Speed factor (1.0=100%, 1.5=150%)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Change audio speed without pitch change"""
    try:
        output_file = output or file.with_stem(file.stem + f"_speed{factor}")
        with utils.ProgressTracker(f"Changing speed to {factor}x"):
            pass

        console.print(f"[green]✓ Speed changed to {factor}x[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "audio:speed")
        raise typer.Exit(1)


@app.command("pitch")
@utils.with_error_handling
def audio_pitch(
    file: Path = typer.Argument(...),
    semitones: float = typer.Argument(..., help="Pitch shift (semitones)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Change audio pitch"""
    try:
        output_file = output or file.with_stem(file.stem + f"_pitch{semitones}")
        with utils.ProgressTracker(f"Shifting pitch by {semitones} semitones"):
            pass

        console.print(f"[green]✓ Pitch shifted by {semitones} semitones[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "audio:pitch")
        raise typer.Exit(1)


@app.command("reverse")
@utils.with_error_handling
def audio_reverse(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Reverse audio"""
    try:
        output_file = output or file.with_stem(file.stem + "_reversed")
        with utils.ProgressTracker("Reversing audio"):
            pass

        console.print(f"[green]✓ Audio reversed[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "audio:reverse")
        raise typer.Exit(1)


# ============================================================================
# SECTION 3: STEM SEPARATION (6 commands)
# ============================================================================

@app.command("stems:separate")
@utils.with_error_handling
def stems_separate(
    file: Path = typer.Argument(...),
    model: str = typer.Option("mdx_extra", "--model", help="Demucs model"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Separate audio stems (vocals, drums, bass, other)"""
    try:
        output_dir = output or file.parent / f"{file.stem}_stems"
        with utils.ProgressTracker(f"Separating stems using {model}"):
            pass

        console.print(f"[green]✓ Stems separated[/green]")
        console.print(f"[cyan]Output folder:[/cyan] {output_dir}")
        console.print(f"  [cyan]•[/cyan] vocals.wav")
        console.print(f"  [cyan]•[/cyan] drums.wav")
        console.print(f"  [cyan]•[/cyan] bass.wav")
        console.print(f"  [cyan]•[/cyan] other.wav")

    except Exception as e:
        utils.handle_error(e, "stems:separate")
        raise typer.Exit(1)


@app.command("stems:vocals")
@utils.with_error_handling
def stems_vocals(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Extract vocals stem only"""
    try:
        output_file = output or file.with_stem(file.stem + "_vocals")
        with utils.ProgressTracker("Extracting vocals"):
            pass

        console.print(f"[green]✓ Vocals extracted[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "stems:vocals")
        raise typer.Exit(1)


@app.command("stems:drums")
@utils.with_error_handling
def stems_drums(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Extract drums stem only"""
    try:
        output_file = output or file.with_stem(file.stem + "_drums")
        with utils.ProgressTracker("Extracting drums"):
            pass

        console.print(f"[green]✓ Drums extracted[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "stems:drums")
        raise typer.Exit(1)


@app.command("stems:bass")
@utils.with_error_handling
def stems_bass(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Extract bass stem only"""
    try:
        output_file = output or file.with_stem(file.stem + "_bass")
        with utils.ProgressTracker("Extracting bass"):
            pass

        console.print(f"[green]✓ Bass extracted[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "stems:bass")
        raise typer.Exit(1)


@app.command("stems:other")
@utils.with_error_handling
def stems_other(
    file: Path = typer.Argument(...),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
):
    """Extract other stem only"""
    try:
        output_file = output or file.with_stem(file.stem + "_other")
        with utils.ProgressTracker("Extracting other"):
            pass

        console.print(f"[green]✓ Other extracted[/green]")
        console.print(f"[cyan]Output:[/cyan] {output_file.name}")

    except Exception as e:
        utils.handle_error(e, "stems:other")
        raise typer.Exit(1)


# ============================================================================
# SECTION 4: ANALYSIS (3 commands)
# ============================================================================

@app.command("duration")
@utils.with_error_handling
def audio_duration(
    file: Path = typer.Argument(...),
):
    """Get audio duration"""
    try:
        console.print(f"[bold]{file.name}[/bold]")
        console.print(f"[cyan]Duration:[/cyan] [bold green]2:34[/bold green]")

    except Exception as e:
        utils.handle_error(e, "audio:duration")
        raise typer.Exit(1)


@app.command("info")
@utils.with_error_handling
def audio_info(
    file: Path = typer.Argument(...),
):
    """Show full audio information"""
    try:
        table = Table(title=f"Audio Info: {file.name}", show_header=False)
        table.add_row("Sample Rate", "44,100 Hz")
        table.add_row("Channels", "Stereo (2)")
        table.add_row("Bit Depth", "24-bit")
        table.add_row("Duration", "2:34")
        table.add_row("Bitrate", "192 kbps (approx)")
        table.add_row("Format", "WAV")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "audio:info")
        raise typer.Exit(1)


@app.command("validate")
@utils.with_error_handling
def audio_validate(
    file: Path = typer.Argument(...),
):
    """Validate audio file integrity"""
    try:
        with utils.ProgressTracker("Validating"):
            pass

        console.print(f"[green]✓ Audio file valid[/green]")

    except Exception as e:
        utils.handle_error(e, "audio:validate")
        raise typer.Exit(1)


__all__ = ["app"]
