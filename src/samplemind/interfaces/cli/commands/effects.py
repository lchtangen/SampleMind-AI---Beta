#!/usr/bin/env python3
"""Audio Effects Commands - Apply professional audio effects and presets"""

from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from samplemind.core.processing.audio_effects import (
    AudioEffectsProcessor,
    EffectType,
    EQSettings,
    CompressionSettings,
    DistortionSettings,
    ReverbSettings,
)
from . import utils

app = typer.Typer(help="🎛️  Audio Effects - Professional processing & presets", no_args_is_help=True)
console = utils.console


class EffectPreset(str, Enum):
    """Built-in audio effect presets"""
    VOCAL = "vocal"
    DRUMS = "drums"
    BASS = "bass"
    MASTER = "master"
    VINTAGE = "vintage"


PRESET_DESCRIPTIONS = {
    EffectPreset.VOCAL: "Boost presence, compress, add reverb for vocals",
    EffectPreset.DRUMS: "Boost low end, compress, add saturation for drums",
    EffectPreset.BASS: "Enhance sub/mid-bass, compress, limit for bass",
    EffectPreset.MASTER: "Subtle master EQ, gentle compression, final limiting",
    EffectPreset.VINTAGE: "Warm saturation, soft compression, vintage tone",
}


# ============================================================================
# SECTION 1: EFFECT PRESETS (5 commands)
# ============================================================================

@app.command("preset")
@utils.with_error_handling
def apply_preset(
    file: Path = typer.Argument(..., help="Audio file to process"),
    preset: EffectPreset = typer.Option(
        EffectPreset.MASTER,
        "--type", "-t",
        help="Preset type: vocal, drums, bass, master, vintage"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """
    Apply a built-in audio effects preset.

    Presets include:
    - vocal: Voice enhancement with presence boost and reverb
    - drums: Drum processing with compression and saturation
    - bass: Bass enhancement with limiting
    - master: Master bus chain with gentle compression
    - vintage: Warm, analog-style processing
    """
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + f"_{preset.value}")
        output_file = Path(output_file).expanduser().resolve()

        console.print()
        console.print(f"[bold cyan]🎛️  Apply Effects Preset[/bold cyan]")
        console.print(f"[cyan]Input: {file.name}[/cyan]")
        console.print(f"[cyan]Preset: {preset.value.upper()}[/cyan]")
        console.print(f"[cyan]{PRESET_DESCRIPTIONS[preset]}[/cyan]")
        console.print()

        with utils.ProgressTracker(f"Applying {preset.value} preset"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_preset(audio, preset.value)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Preset applied successfully![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")
        console.print()

    except utils.CLIError as e:
        utils.handle_error(e, "audio:preset")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("vocal")
@utils.with_error_handling
def apply_vocal_preset(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Apply vocal enhancement preset (presence boost + reverb)"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_vocal")

        with utils.ProgressTracker("Applying vocal preset"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_preset(audio, "vocal")
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Vocal preset applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:vocal")
        raise typer.Exit(1)


@app.command("drums")
@utils.with_error_handling
def apply_drums_preset(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Apply drum processing preset (compression + saturation)"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_drums")

        with utils.ProgressTracker("Applying drums preset"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_preset(audio, "drums")
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Drum preset applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:drums")
        raise typer.Exit(1)


@app.command("bass")
@utils.with_error_handling
def apply_bass_preset(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Apply bass enhancement preset (sub-boost + limiting)"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_bass")

        with utils.ProgressTracker("Applying bass preset"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_preset(audio, "bass")
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Bass preset applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:bass")
        raise typer.Exit(1)


@app.command("master")
@utils.with_error_handling
def apply_master_preset(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Apply master bus preset (gentle compression + limiting)"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_master")

        with utils.ProgressTracker("Applying master preset"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_preset(audio, "master")
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Master preset applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:master")
        raise typer.Exit(1)


@app.command("vintage")
@utils.with_error_handling
def apply_vintage_preset(
    file: Path = typer.Argument(..., help="Audio file to process"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Apply vintage/warm preset (saturation + soft compression)"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_vintage")

        with utils.ProgressTracker("Applying vintage preset"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_preset(audio, "vintage")
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Vintage preset applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:vintage")
        raise typer.Exit(1)


# ============================================================================
# SECTION 2: INDIVIDUAL EFFECTS (5 commands)
# ============================================================================

@app.command("eq")
@utils.with_error_handling
def apply_eq_effect(
    file: Path = typer.Argument(..., help="Audio file to process"),
    gains: str = typer.Option(
        "0,0,0,0,0,0,0,0,0,0",
        "--gains", "-g",
        help="10-band EQ gains in dB (comma-separated, e.g. '3,0,-2,0,0,0,0,0,0,0')"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """
    Apply 10-band parametric EQ.

    Band frequencies: 31, 63, 125, 250, 500, 1K, 2K, 4K, 8K, 16K Hz

    Examples:
    - Boost bass: samplemind audio:eq song.wav --gains "3,2,0,0,0,0,0,0,0,0"
    - Cut harshness: samplemind audio:eq song.wav --gains "0,0,0,0,0,0,-2,0,0,0"
    """
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        # Parse gains
        try:
            gains_list = [float(g.strip()) for g in gains.split(",")]
            if len(gains_list) != 10:
                console.print(f"[red]✗ Must provide exactly 10 gain values (got {len(gains_list)})[/red]")
                raise typer.Exit(1)
        except ValueError:
            console.print(f"[red]✗ Invalid gain values. Use comma-separated floats, e.g.: 3,0,-2,0,0,0,0,0,0,0[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_eq")

        console.print()
        console.print(f"[bold cyan]🎛️  10-Band Parametric EQ[/bold cyan]")
        console.print(f"[cyan]Input: {file.name}[/cyan]")
        console.print()

        # Show EQ bands
        bands = [31, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        eq_table = Table(show_header=True, header_style="bold cyan")
        eq_table.add_column("Band", style="cyan")
        eq_table.add_column("Frequency", justify="right", style="yellow")
        eq_table.add_column("Gain (dB)", justify="right", style="green")

        for band, freq, gain in zip(range(1, 11), bands, gains_list):
            gain_str = f"+{gain:.1f}" if gain > 0 else f"{gain:.1f}"
            eq_table.add_row(f"#{band}", f"{freq} Hz", gain_str)

        console.print(eq_table)
        console.print()

        with utils.ProgressTracker("Applying 10-band EQ"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_eq(audio, gains=gains_list)
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ EQ applied successfully![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:eq")
        raise typer.Exit(1)


@app.command("compress")
@utils.with_error_handling
def apply_compression_effect(
    file: Path = typer.Argument(..., help="Audio file to process"),
    ratio: float = typer.Option(4.0, "--ratio", "-r", help="Compression ratio (e.g., 4.0 = 4:1)"),
    threshold: float = typer.Option(-20.0, "--threshold", "-t", help="Threshold in dB"),
    attack: float = typer.Option(10.0, "--attack", "-a", help="Attack time in ms"),
    release: float = typer.Option(100.0, "--release", "-l", help="Release time in ms"),
    makeup: float = typer.Option(0.0, "--makeup", "-m", help="Makeup gain in dB"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """
    Apply dynamic compression.

    Examples:
    - Vocals: samplemind audio:compress vocal.wav --ratio 4 --threshold -15
    - Drums: samplemind audio:compress drums.wav --ratio 3 --threshold -18
    - Gentle: samplemind audio:compress song.wav --ratio 2 --threshold -12
    """
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_compressed")

        console.print()
        console.print(f"[bold cyan]🎛️  Dynamic Compression[/bold cyan]")
        console.print(f"[cyan]Input: {file.name}[/cyan]")
        console.print()

        comp_table = Table(show_header=False)
        comp_table.add_row("Ratio", f"{ratio}:1", style="cyan")
        comp_table.add_row("Threshold", f"{threshold} dB", style="yellow")
        comp_table.add_row("Attack", f"{attack} ms", style="yellow")
        comp_table.add_row("Release", f"{release} ms", style="yellow")
        comp_table.add_row("Makeup Gain", f"{makeup} dB", style="green")

        console.print(comp_table)
        console.print()

        with utils.ProgressTracker("Applying compression"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_compression(
                audio,
                ratio=ratio,
                threshold_db=threshold,
                attack_ms=attack,
                release_ms=release,
                makeup_gain_db=makeup
            )
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Compression applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:compress")
        raise typer.Exit(1)


@app.command("limit")
@utils.with_error_handling
def apply_limiting_effect(
    file: Path = typer.Argument(..., help="Audio file to process"),
    threshold: float = typer.Option(-3.0, "--threshold", "-t", help="Limiting threshold in dB"),
    release: float = typer.Option(50.0, "--release", "-r", help="Release time in ms"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """
    Apply hard limiter (infinite ratio compression).

    Prevents audio from exceeding threshold.

    Examples:
    - Protect from clipping: samplemind audio:limit song.wav --threshold -0.3
    - Gentle limiting: samplemind audio:limit song.wav --threshold -3
    """
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_limited")

        console.print()
        console.print(f"[bold cyan]🎛️  Hard Limiter[/bold cyan]")
        console.print(f"[cyan]Input: {file.name}[/cyan]")
        console.print(f"[cyan]Threshold: {threshold} dB[/cyan]")
        console.print()

        with utils.ProgressTracker("Applying limiter"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_limiting(
                audio,
                threshold_db=threshold,
                release_ms=release
            )
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Limiter applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:limit")
        raise typer.Exit(1)


@app.command("distort")
@utils.with_error_handling
def apply_distortion_effect(
    file: Path = typer.Argument(..., help="Audio file to process"),
    drive: float = typer.Option(1.0, "--drive", "-d", help="Drive amount (1.0=clean, >1.0=distorted)"),
    tone: float = typer.Option(0.5, "--tone", "-t", help="Tone shaping (0-1, 0=warm, 1=bright)"),
    output_gain: float = typer.Option(0.0, "--gain", "-g", help="Output gain in dB"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """
    Apply soft clipping distortion.

    Examples:
    - Light distortion: samplemind audio:distort synth.wav --drive 1.5
    - Heavy distortion: samplemind audio:distort guitar.wav --drive 3.0 --tone 0.3
    - Vintage tone: samplemind audio:distort vocal.wav --drive 1.2 --tone 0.2
    """
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_distorted")

        console.print()
        console.print(f"[bold cyan]🎛️  Soft Clipping Distortion[/bold cyan]")
        console.print(f"[cyan]Input: {file.name}[/cyan]")
        console.print()

        dist_table = Table(show_header=False)
        dist_table.add_row("Drive", f"{drive}x", style="cyan")
        dist_table.add_row("Tone", f"{tone:.1f} (0=warm, 1=bright)", style="yellow")
        dist_table.add_row("Output Gain", f"{output_gain} dB", style="green")

        console.print(dist_table)
        console.print()

        with utils.ProgressTracker("Applying distortion"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_distortion(
                audio,
                drive=drive,
                tone=tone,
                output_gain_db=output_gain
            )
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Distortion applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:distort")
        raise typer.Exit(1)


@app.command("reverb")
@utils.with_error_handling
def apply_reverb_effect(
    file: Path = typer.Argument(..., help="Audio file to process"),
    room: float = typer.Option(0.5, "--room", "-r", help="Room size (0-1)"),
    damping: float = typer.Option(0.5, "--damping", "-d", help="Damping (0-1)"),
    width: float = typer.Option(1.0, "--width", "-w", help="Stereo width (0-1)"),
    mix: float = typer.Option(0.3, "--mix", "-m", help="Dry/wet mix (0-1, 1=all wet)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """
    Apply reverb effect.

    Examples:
    - Light reverb: samplemind audio:reverb vocal.wav --room 0.3 --mix 0.15
    - Large room: samplemind audio:reverb vocal.wav --room 0.8 --mix 0.3
    - Hall reverb: samplemind audio:reverb vocal.wav --room 0.9 --damping 0.3 --mix 0.4
    """
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)

        output_file = output or file.with_stem(file.stem + "_reverb")

        console.print()
        console.print(f"[bold cyan]🎛️  Reverb Effect[/bold cyan]")
        console.print(f"[cyan]Input: {file.name}[/cyan]")
        console.print()

        reverb_table = Table(show_header=False)
        reverb_table.add_row("Room Size", f"{room:.1f}", style="cyan")
        reverb_table.add_row("Damping", f"{damping:.1f}", style="cyan")
        reverb_table.add_row("Stereo Width", f"{width:.1f}", style="cyan")
        reverb_table.add_row("Dry/Wet Mix", f"{mix:.1f}", style="yellow")

        console.print(reverb_table)
        console.print()

        with utils.ProgressTracker("Applying reverb"):
            processor = AudioEffectsProcessor()
            audio, sr = processor.load_audio(file)
            processed = processor.apply_reverb(
                audio,
                room_size=room,
                damping=damping,
                width=width,
                dry_wet_mix=mix
            )
            output_file = Path(output_file).expanduser().resolve()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(processed, output_file, sr)

        console.print(f"[green]✓ Reverb applied![/green]")
        console.print(f"[cyan]Output: {output_file.name}[/cyan]")

    except Exception as e:
        utils.handle_error(e, "audio:reverb")
        raise typer.Exit(1)


# ============================================================================
# SECTION 3: LIST & REFERENCE (1 command)
# ============================================================================

@app.command("list")
@utils.with_error_handling
def list_effects() -> None:
    """
    List available effects and presets.
    """
    console.print()
    console.print("[bold cyan]🎛️  Available Audio Effects[/bold cyan]")
    console.print()

    # Effects
    console.print("[bold yellow]Built-in Presets (5):[/bold yellow]")
    presets_table = Table(show_header=True, header_style="bold cyan")
    presets_table.add_column("Preset", style="cyan")
    presets_table.add_column("Description")

    for preset, desc in PRESET_DESCRIPTIONS.items():
        presets_table.add_row(preset.value, desc)

    console.print(presets_table)
    console.print()

    console.print("[bold yellow]Individual Effects (5):[/bold yellow]")
    effects_table = Table(show_header=True, header_style="bold cyan")
    effects_table.add_column("Effect", style="cyan")
    effects_table.add_column("Description")
    effects_table.add_column("Command")

    effects_data = [
        ("10-Band EQ", "Parametric equalization across frequency spectrum", "samplemind audio:eq"),
        ("Compression", "Dynamic range compression with adjustable ratio", "samplemind audio:compress"),
        ("Limiter", "Hard limiting to prevent clipping", "samplemind audio:limit"),
        ("Distortion", "Soft clipping distortion and saturation", "samplemind audio:distort"),
        ("Reverb", "Room modeling with adjustable parameters", "samplemind audio:reverb"),
    ]

    for effect, desc, cmd in effects_data:
        effects_table.add_row(effect, desc, f"[dim]{cmd}[/dim]")

    console.print(effects_table)
    console.print()

    # Quick examples
    console.print("[bold yellow]Quick Examples:[/bold yellow]")
    examples_panel = Panel(
        """[cyan]samplemind audio:preset vocal.wav --type vocal[/cyan]
[cyan]samplemind audio:preset drums.wav --type drums[/cyan]
[cyan]samplemind audio:eq song.wav --gains "3,2,0,0,0,0,0,0,0,0"[/cyan]
[cyan]samplemind audio:compress vocal.wav --ratio 4 --threshold -15[/cyan]
[cyan]samplemind audio:distort synth.wav --drive 2.0 --tone 0.5[/cyan]
[cyan]samplemind audio:reverb vocal.wav --room 0.8 --mix 0.3[/cyan]""",
        title="Examples",
        border_style="cyan"
    )
    console.print(examples_panel)
    console.print()


__all__ = ["app"]
