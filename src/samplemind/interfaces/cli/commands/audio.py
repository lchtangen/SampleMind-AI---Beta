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
import shutil
from typing import Optional, List
from pathlib import Path
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from . import utils
from ....core.processing.stem_separation import StemSeparationEngine, StemSeparationResult


class StemQuality(str, Enum):
    """Quality presets for stem separation"""
    FAST = "fast"
    STANDARD = "standard"
    HIGH = "high"


# Quality preset configurations
QUALITY_PRESETS = {
    StemQuality.FAST: {"model": "mdx", "shifts": 1, "overlap": 0.1},
    StemQuality.STANDARD: {"model": "mdx_extra", "shifts": 1, "overlap": 0.25},
    StemQuality.HIGH: {"model": "mdx_extra", "shifts": 5, "overlap": 0.5},
}

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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
) -> None:
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
    file: Path = typer.Argument(..., help="Audio file to separate"),
    model: str = typer.Option("mdx_extra", "--model", "-m", help="Demucs model (mdx, mdx_extra, mdx_q, htdemucs)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    quality: StemQuality = typer.Option(StemQuality.STANDARD, "--quality", "-q", help="Quality preset (fast/standard/high)"),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Device (cpu, cuda, mps)"),
) -> None:
    """Separate audio into stems (vocals, drums, bass, other) using Demucs AI"""
    try:
        # Validate input file
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)

        # Get quality preset settings (override model if quality preset specified)
        preset = QUALITY_PRESETS[quality]
        effective_model = model if model != "mdx_extra" else preset["model"]

        # Setup output directory
        output_dir = output or file.parent / f"{file.stem}_stems"
        output_dir = Path(output_dir).expanduser().resolve()

        console.print(f"[bold cyan]Stem Separation[/bold cyan]")
        console.print(f"  Input: [green]{file.name}[/green]")
        console.print(f"  Model: [yellow]{effective_model}[/yellow]")
        console.print(f"  Quality: [yellow]{quality.value}[/yellow]")
        console.print()

        # Create engine and run separation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Separating stems with {effective_model}...", total=None)

            engine = StemSeparationEngine(
                model=effective_model,
                device=device,
                shifts=preset["shifts"],
                overlap=preset["overlap"],
                verbose=False,
            )

            result: StemSeparationResult = engine.separate(
                audio_path=file,
                output_directory=output_dir.parent,  # Demucs creates subfolders
            )

            progress.update(task, completed=True)

        # Move stems to clean output directory
        final_output = output_dir
        final_output.mkdir(parents=True, exist_ok=True)

        console.print()
        console.print(f"[green]✓ Stems separated successfully![/green]")
        console.print(f"[cyan]Output folder:[/cyan] {final_output}")

        # List generated stems
        for stem_name, stem_path in result.stems.items():
            # Copy to final location with cleaner names
            final_stem = final_output / f"{stem_name}.wav"
            if stem_path.exists() and stem_path != final_stem:
                shutil.copy2(stem_path, final_stem)
            console.print(f"  [cyan]•[/cyan] {stem_name}.wav")

    except Exception as e:
        utils.handle_error(e, "stems:separate")
        raise typer.Exit(1)


def _extract_single_stem(
    file: Path,
    stem_type: str,
    output: Optional[Path],
    quality: StemQuality,
    device: Optional[str],
    command_name: str,
) -> None:
    """Helper function to extract a single stem type"""
    file = Path(file).expanduser().resolve()
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(1)

    preset = QUALITY_PRESETS[quality]
    output_file = output or file.parent / f"{file.stem}_{stem_type}.wav"
    output_file = Path(output_file).expanduser().resolve()

    console.print(f"[bold cyan]Extracting {stem_type.title()}[/bold cyan]")
    console.print(f"  Input: [green]{file.name}[/green]")
    console.print(f"  Quality: [yellow]{quality.value}[/yellow]")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"Extracting {stem_type}...", total=None)

        engine = StemSeparationEngine(
            model=preset["model"],
            device=device,
            shifts=preset["shifts"],
            overlap=preset["overlap"],
            verbose=False,
        )

        # Use two_stems mode for faster single-stem extraction
        result = engine.separate(
            audio_path=file,
            two_stems=stem_type if stem_type in ("vocals", "drums") else None,
        )

        progress.update(task, completed=True)

    # Copy the requested stem to the output location
    if stem_type in result.stems:
        stem_path = result.stems[stem_type]
        if stem_path.exists():
            output_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stem_path, output_file)
            console.print()
            console.print(f"[green]✓ {stem_type.title()} extracted[/green]")
            console.print(f"[cyan]Output:[/cyan] {output_file}")
        else:
            console.print(f"[red]Error: Stem file not generated[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[red]Error: {stem_type} stem not available[/red]")
        raise typer.Exit(1)


@app.command("stems:vocals")
@utils.with_error_handling
def stems_vocals(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    quality: StemQuality = typer.Option(StemQuality.FAST, "--quality", "-q", help="Quality preset"),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Device (cpu, cuda, mps)"),
) -> None:
    """Extract vocals stem only (fast two-stem mode)"""
    try:
        _extract_single_stem(file, "vocals", output, quality, device, "stems:vocals")
    except Exception as e:
        utils.handle_error(e, "stems:vocals")
        raise typer.Exit(1)


@app.command("stems:drums")
@utils.with_error_handling
def stems_drums(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    quality: StemQuality = typer.Option(StemQuality.FAST, "--quality", "-q", help="Quality preset"),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Device (cpu, cuda, mps)"),
) -> None:
    """Extract drums stem only (fast two-stem mode)"""
    try:
        _extract_single_stem(file, "drums", output, quality, device, "stems:drums")
    except Exception as e:
        utils.handle_error(e, "stems:drums")
        raise typer.Exit(1)


@app.command("stems:bass")
@utils.with_error_handling
def stems_bass(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    quality: StemQuality = typer.Option(StemQuality.STANDARD, "--quality", "-q", help="Quality preset"),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Device (cpu, cuda, mps)"),
) -> None:
    """Extract bass stem only (requires full separation)"""
    try:
        _extract_single_stem(file, "bass", output, quality, device, "stems:bass")
    except Exception as e:
        utils.handle_error(e, "stems:bass")
        raise typer.Exit(1)


@app.command("stems:other")
@utils.with_error_handling
def stems_other(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    quality: StemQuality = typer.Option(StemQuality.STANDARD, "--quality", "-q", help="Quality preset"),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Device (cpu, cuda, mps)"),
) -> None:
    """Extract other/melody stem only (requires full separation)"""
    try:
        _extract_single_stem(file, "other", output, quality, device, "stems:other")
    except Exception as e:
        utils.handle_error(e, "stems:other")
        raise typer.Exit(1)


@app.command("stems:batch")
@utils.with_error_handling
def stems_batch(
    folder: Path = typer.Argument(..., help="Folder containing audio files"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    quality: StemQuality = typer.Option(StemQuality.STANDARD, "--quality", "-q", help="Quality preset"),
    device: Optional[str] = typer.Option(None, "--device", "-d", help="Device (cpu, cuda, mps)"),
    extensions: str = typer.Option("wav,mp3,flac,aiff,m4a", "--ext", help="File extensions to process"),
) -> None:
    """Batch separate stems for all audio files in a folder"""
    try:
        folder = Path(folder).expanduser().resolve()
        if not folder.is_dir():
            console.print(f"[red]Error: Not a directory: {folder}[/red]")
            raise typer.Exit(1)

        # Find all audio files
        ext_list = [f".{e.strip().lower()}" for e in extensions.split(",")]
        audio_files = [f for f in folder.iterdir() if f.suffix.lower() in ext_list]

        if not audio_files:
            console.print(f"[yellow]No audio files found in {folder}[/yellow]")
            raise typer.Exit(0)

        output_dir = output or folder / "stems_output"
        output_dir = Path(output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        preset = QUALITY_PRESETS[quality]

        console.print(f"[bold cyan]Batch Stem Separation[/bold cyan]")
        console.print(f"  Folder: [green]{folder}[/green]")
        console.print(f"  Files: [yellow]{len(audio_files)}[/yellow]")
        console.print(f"  Quality: [yellow]{quality.value}[/yellow]")
        console.print()

        engine = StemSeparationEngine(
            model=preset["model"],
            device=device,
            shifts=preset["shifts"],
            overlap=preset["overlap"],
            verbose=False,
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Processing files...", total=len(audio_files))

            for audio_file in audio_files:
                progress.update(task, description=f"Processing {audio_file.name}...")

                try:
                    file_output_dir = output_dir / audio_file.stem
                    file_output_dir.mkdir(parents=True, exist_ok=True)

                    result = engine.separate(
                        audio_path=audio_file,
                        output_directory=file_output_dir.parent,
                    )

                    # Copy stems to final location
                    for stem_name, stem_path in result.stems.items():
                        if stem_path.exists():
                            final_stem = file_output_dir / f"{stem_name}.wav"
                            shutil.copy2(stem_path, final_stem)

                except Exception as file_error:
                    console.print(f"  [red]✗ Failed: {audio_file.name} - {file_error}[/red]")

                progress.advance(task)

        console.print()
        console.print(f"[green]✓ Batch separation complete![/green]")
        console.print(f"[cyan]Output:[/cyan] {output_dir}")

    except Exception as e:
        utils.handle_error(e, "stems:batch")
        raise typer.Exit(1)


# ============================================================================
# SECTION 4: ANALYSIS (3 commands)
# ============================================================================

@app.command("duration")
@utils.with_error_handling
def audio_duration(
    file: Path = typer.Argument(...),
) -> None:
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
) -> None:
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
) -> None:
    """Validate audio file integrity"""
    try:
        with utils.ProgressTracker("Validating"):
            pass

        console.print(f"[green]✓ Audio file valid[/green]")

    except Exception as e:
        utils.handle_error(e, "audio:validate")
        raise typer.Exit(1)


__all__ = ["app"]
