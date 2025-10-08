#!/usr/bin/env python3
"""
SampleMind AI v6 - Main CLI Entry Point

Provides both command-line interface and interactive menu system.

Usage:
    # Interactive menu
    $ samplemind

    # Direct commands
    $ samplemind analyze <file>
    $ samplemind stems separate <file>
    $ samplemind midi convert <file>
    $ samplemind tui  # Launch TUI interface
"""

import asyncio
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.table import Table
from enum import Enum

# Import core components
from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
from samplemind.core.processing.stem_separation import (
    StemSeparationEngine, StemType, StemProvider
)
from samplemind.core.processing.audio_to_midi import (
    AudioToMIDIConverter, MIDIConversionMode
)
from samplemind.utils.file_picker import select_audio_file, select_directory

console = Console()
app = typer.Typer(
    name="samplemind",
    help="🎵 SampleMind AI - Professional Music Production Suite",
    add_completion=False
)

# Create sub-apps for different feature groups
stems_app = typer.Typer(help="Stem separation commands")
midi_app = typer.Typer(help="Audio-to-MIDI conversion commands")
analyze_app = typer.Typer(help="Audio analysis commands")
generate_app = typer.Typer(help="AI music generation commands")
search_app = typer.Typer(help="Vector search and recommendations")

app.add_typer(stems_app, name="stems")
app.add_typer(midi_app, name="midi")
app.add_typer(analyze_app, name="analyze")
app.add_typer(generate_app, name="generate")
app.add_typer(search_app, name="search")


# ============================================================================
# Main Commands
# ============================================================================

@app.command()
def menu():
    """Launch interactive menu interface"""
    from samplemind.interfaces.cli.menu import main as menu_main
    menu_main()


@app.command()
def tui():
    """Launch Terminal User Interface (TUI)"""
    console.print("[cyan]Launching SampleMind TUI...[/cyan]")
    try:
        from samplemind.interfaces.tui.app import SampleMindTUI
        app = SampleMindTUI()
        app.run()
    except ImportError:
        console.print("[red]Error: TUI interface not yet implemented[/red]")
        console.print("Run: pip install textual textual-plotext")


@app.command()
def version():
    """Show version information"""
    console.print("[bold cyan]SampleMind AI v6[/bold cyan]")
    console.print("Version: 0.6.0 Beta")
    console.print("Build: 2025-10-04")


# ============================================================================
# Stem Separation Commands
# ============================================================================

@stems_app.command("separate")
def stems_separate(
    audio_file: Optional[str] = typer.Argument(
        None,
        help="Path to audio file (or use file picker if not provided)"
    ),
    stems: List[str] = typer.Option(
        ["vocals", "instrumental"],
        "--stem", "-s",
        help="Stems to extract (vocals, drums, bass, piano, guitar, synth, other, instrumental)"
    ),
    provider: str = typer.Option(
        "lalal_ai",
        "--provider", "-p",
        help="Service provider (lalal_ai, moises, local)"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key", "-k",
        help="API key for cloud service"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for stems"
    ),
):
    """
    Separate audio file into stems (vocals, drums, bass, etc.)

    Example:
        samplemind stems separate song.mp3 --stem vocals --stem drums
        samplemind stems separate  # Use file picker
    """
    # Get audio file
    if not audio_file:
        console.print("[cyan]Select audio file...[/cyan]")
        audio_file = select_audio_file("Select Audio File for Stem Separation")
        if not audio_file:
            console.print("[red]No file selected[/red]")
            raise typer.Exit(1)

    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)

    # Convert stem strings to StemType
    stem_types = [StemType(s.lower()) for s in stems]

    # Run separation
    console.print(f"\n[bold cyan]🎵 Stem Separation[/bold cyan]")
    console.print(f"File: {audio_path.name}")
    console.print(f"Provider: {provider}")
    console.print(f"Stems: {', '.join(s.value for s in stem_types)}\n")

    async def run_separation():
        engine = StemSeparationEngine(
            provider=provider,
            api_key=api_key,
            output_dir=output_dir
        )

        with console.status("[cyan]Separating stems...[/cyan]"):
            result = await engine.separate_stems(
                audio_path,
                stems=stem_types,
                quality="high"
            )

        # Display results
        table = Table(title="✅ Separation Complete")
        table.add_column("Stem", style="cyan")
        table.add_column("Output File", style="green")

        for stem_type, output_path in result.items():
            table.add_row(stem_type.value, str(output_path))

        console.print(table)

        # Show stats
        stats = engine.get_stats()
        console.print(f"\n[dim]Total separations: {stats['total_separations']}[/dim]")

    asyncio.run(run_separation())


@stems_app.command("batch")
def stems_batch(
    directory: Optional[str] = typer.Argument(
        None,
        help="Directory containing audio files"
    ),
    stems: List[str] = typer.Option(
        ["vocals", "instrumental"],
        "--stem", "-s",
        help="Stems to extract"
    ),
    provider: str = typer.Option(
        "lalal_ai",
        "--provider", "-p",
        help="Service provider"
    ),
):
    """
    Batch process multiple audio files for stem separation

    Example:
        samplemind stems batch /path/to/songs --stem vocals --stem drums
    """
    # Get directory
    if not directory:
        console.print("[cyan]Select directory...[/cyan]")
        directory = select_directory("Select Directory for Batch Processing")
        if not directory:
            console.print("[red]No directory selected[/red]")
            raise typer.Exit(1)

    dir_path = Path(directory)
    if not dir_path.is_dir():
        console.print(f"[red]Error: Not a directory: {directory}[/red]")
        raise typer.Exit(1)

    # Find audio files
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aiff', '.ogg']
    audio_files = [
        f for f in dir_path.rglob('*')
        if f.suffix.lower() in audio_extensions
    ]

    if not audio_files:
        console.print("[red]No audio files found in directory[/red]")
        raise typer.Exit(1)

    console.print(f"\n[cyan]Found {len(audio_files)} audio files[/cyan]\n")

    stem_types = [StemType(s.lower()) for s in stems]

    async def run_batch():
        engine = StemSeparationEngine(provider=provider)

        with console.status(f"[cyan]Processing {len(audio_files)} files...[/cyan]"):
            results = await engine.batch_separate(
                audio_files,
                stems=stem_types,
                max_concurrent=3
            )

        console.print(f"\n[green]✅ Processed {len(results)} files successfully[/green]")

    asyncio.run(run_batch())


# ============================================================================
# Audio-to-MIDI Commands
# ============================================================================

@midi_app.command("convert")
def midi_convert(
    audio_file: Optional[str] = typer.Argument(
        None,
        help="Path to audio file"
    ),
    mode: str = typer.Option(
        "auto",
        "--mode", "-m",
        help="Conversion mode (monophonic, polyphonic, percussion, auto)"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output MIDI file path"
    ),
):
    """
    Convert audio file to MIDI

    Example:
        samplemind midi convert melody.mp3 --mode monophonic
        samplemind midi convert drums.wav --mode percussion
    """
    # Get audio file
    if not audio_file:
        console.print("[cyan]Select audio file...[/cyan]")
        audio_file = select_audio_file("Select Audio File for MIDI Conversion")
        if not audio_file:
            console.print("[red]No file selected[/red]")
            raise typer.Exit(1)

    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)

    # Run conversion
    console.print(f"\n[bold cyan]🎹 Audio-to-MIDI Conversion[/bold cyan]")
    console.print(f"File: {audio_path.name}")
    console.print(f"Mode: {mode}\n")

    async def run_conversion():
        converter = AudioToMIDIConverter()

        with console.status("[cyan]Converting to MIDI...[/cyan]"):
            midi_path = await converter.convert_to_midi(
                audio_path,
                mode=MIDIConversionMode(mode.lower())
            )

        console.print(f"\n[green]✅ Conversion complete![/green]")
        console.print(f"MIDI file: {midi_path}")

        # Show stats
        stats = converter.get_stats()
        console.print(f"\n[dim]Total conversions: {stats['total_conversions']}[/dim]")

    asyncio.run(run_conversion())


@midi_app.command("batch")
def midi_batch(
    directory: Optional[str] = typer.Argument(
        None,
        help="Directory containing audio files"
    ),
    mode: str = typer.Option(
        "auto",
        "--mode", "-m",
        help="Conversion mode"
    ),
):
    """
    Batch convert multiple audio files to MIDI

    Example:
        samplemind midi batch /path/to/melodies --mode monophonic
    """
    # Get directory
    if not directory:
        console.print("[cyan]Select directory...[/cyan]")
        directory = select_directory("Select Directory for Batch MIDI Conversion")
        if not directory:
            console.print("[red]No directory selected[/red]")
            raise typer.Exit(1)

    dir_path = Path(directory)
    if not dir_path.is_dir():
        console.print(f"[red]Error: Not a directory: {directory}[/red]")
        raise typer.Exit(1)

    # Find audio files
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aiff']
    audio_files = [
        f for f in dir_path.rglob('*')
        if f.suffix.lower() in audio_extensions
    ]

    if not audio_files:
        console.print("[red]No audio files found in directory[/red]")
        raise typer.Exit(1)

    console.print(f"\n[cyan]Found {len(audio_files)} audio files[/cyan]\n")

    async def run_batch():
        converter = AudioToMIDIConverter()

        with console.status(f"[cyan]Converting {len(audio_files)} files...[/cyan]"):
            results = await converter.batch_convert(
                audio_files,
                mode=MIDIConversionMode(mode.lower()),
                max_concurrent=3
            )

        console.print(f"\n[green]✅ Converted {len(results)} files successfully[/green]")

    asyncio.run(run_batch())


# ============================================================================
# Analysis Commands
# ============================================================================

@analyze_app.command("file")
def analyze_file(
    audio_file: Optional[str] = typer.Argument(
        None,
        help="Path to audio file"
    ),
    level: str = typer.Option(
        "standard",
        "--level", "-l",
        help="Analysis level (basic, standard, detailed, professional)"
    ),
    ai: bool = typer.Option(
        False,
        "--ai",
        help="Include AI analysis"
    ),
):
    """
    Analyze audio file

    Example:
        samplemind analyze file song.mp3 --level detailed --ai
    """
    # Get audio file
    if not audio_file:
        console.print("[cyan]Select audio file...[/cyan]")
        audio_file = select_audio_file("Select Audio File to Analyze")
        if not audio_file:
            console.print("[red]No file selected[/red]")
            raise typer.Exit(1)

    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)

    async def run_analysis():
        from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel

        engine = AudioEngine()

        with console.status("[cyan]Analyzing audio...[/cyan]"):
            result = await engine.analyze_audio_async(
                audio_path,
                level=AnalysisLevel[level.upper()]
            )

        # Display results
        table = Table(title=f"📊 Analysis Results: {audio_path.name}")
        table.add_column("Feature", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Tempo", f"{result.tempo:.1f} BPM")
        table.add_row("Key", result.key)
        table.add_row("Energy", f"{result.energy:.2f}")
        if hasattr(result, 'mood') and result.mood:
            table.add_row("Mood", result.mood)

        console.print(table)

        if ai:
            from samplemind.integrations.ai_manager import SampleMindAIManager

            console.print("\n[cyan]Running AI analysis...[/cyan]\n")
            ai_manager = SampleMindAIManager()

            features = {
                'tempo': result.tempo,
                'key': result.key,
                'energy': result.energy,
                'mood': result.mood if hasattr(result, 'mood') else None
            }

            with console.status("[cyan]Generating AI insights...[/cyan]"):
                ai_result = await ai_manager.analyze_music(features)

            if ai_result:
                console.print(f"[bold green]AI Insights:[/bold green]")
                console.print(ai_result)

    asyncio.run(run_analysis())


# ============================================================================
# Music Generation Commands
# ============================================================================

@generate_app.command("music")
def generate_music_command(
    prompt: str = typer.Argument(..., help="Music generation prompt"),
    style: Optional[str] = typer.Option(
        None,
        "--style", "-s",
        help="Music style (electronic, ambient, orchestral, rock, jazz, etc.)"
    ),
    mood: Optional[str] = typer.Option(
        None,
        "--mood", "-m",
        help="Music mood (energetic, calm, dark, bright, etc.)"
    ),
    tempo: Optional[int] = typer.Option(
        None,
        "--tempo", "-t",
        help="Tempo in BPM"
    ),
    key: Optional[str] = typer.Option(
        None,
        "--key", "-k",
        help="Musical key (e.g., 'C major', 'A minor')"
    ),
    duration: int = typer.Option(
        30,
        "--duration", "-d",
        help="Duration in seconds"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output file path"
    ),
):
    """
    Generate AI music from text prompt

    Example:
        samplemind generate music "Upbeat electronic music" --style electronic --tempo 128
        samplemind generate music "Calm ambient soundscape" --mood calm --duration 60
    """
    console.print(f"\n[bold cyan]🎵 AI Music Generation[/bold cyan]")
    console.print(f"Prompt: {prompt}")
    if style:
        console.print(f"Style: {style}")
    if mood:
        console.print(f"Mood: {mood}")
    if tempo:
        console.print(f"Tempo: {tempo} BPM")
    if key:
        console.print(f"Key: {key}")
    console.print(f"Duration: {duration}s\n")

    async def run_generation():
        from samplemind.core.generation import LyriaRealTimeEngine, MusicGenerationRequest, MusicStyle, MusicMood

        engine = LyriaRealTimeEngine()

        # Build request
        request = MusicGenerationRequest(
            prompt=prompt,
            style=MusicStyle(style.lower()) if style else None,
            mood=MusicMood(mood.lower()) if mood else None,
            tempo=tempo,
            key=key,
            duration=duration
        )

        with console.status("[cyan]Generating music with Gemini Lyria...[/cyan]"):
            result = await engine.generate_music(request)

        if result.success:
            console.print(f"\n[green]✅ Music generated successfully![/green]")
            console.print(f"Generation time: {result.generation_time:.2f}s")

            if result.audio_path:
                console.print(f"Saved to: {result.audio_path}")

            # Show metadata
            if result.metadata:
                console.print("\n[cyan]Metadata:[/cyan]")
                for key, value in result.metadata.items():
                    console.print(f"  {key}: {value}")
        else:
            console.print(f"\n[red]❌ Generation failed[/red]")
            if "error" in result.metadata:
                console.print(f"Error: {result.metadata['error']}")

    asyncio.run(run_generation())


@generate_app.command("variations")
def generate_variations_command(
    prompt: str = typer.Argument(..., help="Music generation prompt"),
    count: int = typer.Option(
        3,
        "--count", "-n",
        help="Number of variations to generate"
    ),
    style: Optional[str] = typer.Option(None, "--style", "-s"),
    tempo: Optional[int] = typer.Option(None, "--tempo", "-t"),
):
    """
    Generate multiple variations of a music prompt

    Example:
        samplemind generate variations "Electronic beat" --count 5 --tempo 128
    """
    console.print(f"\n[bold cyan]🎵 Generating {count} Variations[/bold cyan]")
    console.print(f"Prompt: {prompt}\n")

    async def run_variations():
        from samplemind.core.generation import LyriaRealTimeEngine, MusicGenerationRequest, MusicStyle

        engine = LyriaRealTimeEngine()

        request = MusicGenerationRequest(
            prompt=prompt,
            style=MusicStyle(style.lower()) if style else None,
            tempo=tempo,
            duration=30
        )

        with console.status(f"[cyan]Generating {count} variations...[/cyan]"):
            results = await engine.generate_variations(request, num_variations=count)

        console.print(f"\n[green]✅ Generated {len(results)} variations[/green]")

        for i, result in enumerate(results, 1):
            if result.success:
                console.print(f"  Variation {i}: ✓ ({result.generation_time:.2f}s)")
            else:
                console.print(f"  Variation {i}: ✗ Failed")

    asyncio.run(run_variations())


@generate_app.command("interactive")
def interactive_generation():
    """
    Launch interactive music generation session

    Allows real-time control and modification of generation parameters.
    """
    console.print("[bold cyan]🎹 Interactive Music Generation[/bold cyan]")
    console.print("[yellow]Not yet implemented - Coming soon![/yellow]")
    console.print("\nThis feature will allow:")
    console.print("  • Real-time parameter adjustment")
    console.print("  • Live music streaming")
    console.print("  • Interactive composition")


# ============================================================================
# Phase 1 Analysis Commands
# ============================================================================

@analyze_app.command("bpm-key")
def analyze_bpm_key(
    audio_file: Optional[str] = typer.Argument(
        None,
        help="Path to audio file"
    ),
    label: bool = typer.Option(
        False,
        "--label", "-l",
        help="Generate labeled filename"
    ),
):
    """
    Detect BPM and musical key of audio file.
    
    Example:
        samplemind analyze bpm-key song.mp3
        samplemind analyze bpm-key song.mp3 --label
    """
    if not audio_file:
        console.print("[cyan]Select audio file...[/cyan]")
        audio_file = select_audio_file("Select Audio File for Analysis")
        if not audio_file:
            console.print("[red]No file selected[/red]")
            raise typer.Exit(1)
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)
    
    from samplemind.core.analysis import BPMKeyDetector
    
    with console.status("[cyan]Analyzing audio...[/cyan]"):
        detector = BPMKeyDetector()
        bpm_data = detector.detect_bpm(audio_path)
        key = detector.detect_key(audio_path)
    
    # Display results
    console.print("\n[bold green]✅ Analysis Complete[/bold green]\n")
    console.print(f"[cyan]File:[/cyan] {audio_path.name}")
    console.print(f"[cyan]BPM:[/cyan] {bpm_data['bpm']:.2f} (confidence: {bpm_data['confidence']:.0%})")
    console.print(f"[cyan]Key:[/cyan] {key}\n")
    
    if label:
        new_name = detector.label_file(audio_path)
        console.print(f"[yellow]Suggested filename:[/yellow] {new_name}")


@analyze_app.command("loops")
def analyze_loops(
    audio_file: Optional[str] = typer.Argument(
        None,
        help="Path to audio file"
    ),
    bars: int = typer.Option(
        8,
        "--bars", "-b",
        help="Bars per segment"
    ),
    save: bool = typer.Option(
        False,
        "--save", "-s",
        help="Save extracted loops"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory"
    ),
):
    """
    Extract 8-bar loops from audio file.
    
    Example:
        samplemind analyze loops song.mp3
        samplemind analyze loops song.mp3 --save --output ./loops
    """
    if not audio_file:
        console.print("[cyan]Select audio file...[/cyan]")
        audio_file = select_audio_file("Select Audio File for Loop Extraction")
        if not audio_file:
            console.print("[red]No file selected[/red]")
            raise typer.Exit(1)
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)
    
    from samplemind.core.analysis import LoopSegmenter
    
    with console.status("[cyan]Extracting loops...[/cyan]"):
        segmenter = LoopSegmenter()
        segments = segmenter.segment_8bars(audio_path, bars)
    
    if not segments:
        console.print("[red]No loops extracted[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold green]✅ Extracted {len(segments)} loops[/bold green]\n")
    
    for i, seg in enumerate(segments):
        console.print(f"Loop {i+1}: Bars {seg['start_bar']}-{seg['end_bar']}, {seg['duration']:.2f}s, {seg['bpm']:.0f} BPM")
    
    if save:
        output_dir = Path(output) if output else Path.cwd() / "loops"
        saved = segmenter.save_segments(segments, output_dir, audio_path.stem)
        console.print(f"\n[green]Saved {len(saved)} loops to {output_dir}[/green]")


@app.command("identify")
def identify_audio(
    audio_file: Optional[str] = typer.Argument(
        None,
        help="Path to audio file"
    ),
):
    """
    Identify audio file using AcoustID fingerprinting.
    
    Example:
        samplemind identify unknown.mp3
    """
    if not audio_file:
        console.print("[cyan]Select audio file...[/cyan]")
        audio_file = select_audio_file("Select Audio File to Identify")
        if not audio_file:
            console.print("[red]No file selected[/red]")
            raise typer.Exit(1)
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)
    
    from samplemind.integrations import AcoustIDClient
    
    with console.status("[cyan]Identifying audio...[/cyan]"):
        client = AcoustIDClient()
        matches = client.identify(audio_path)
    
    if not matches:
        console.print("[yellow]No matches found[/yellow]")
        return
    
    console.print(f"\n[bold green]✅ Found {len(matches)} matches[/bold green]\n")
    
    for i, match in enumerate(matches, 1):
        console.print(f"[cyan]Match {i}:[/cyan] {match['artist']} - {match['title']}")
        console.print(f"  Confidence: {match['score']:.0%}")
        if match.get('metadata') and match['metadata'].get('album'):
            console.print(f"  Album: {match['metadata']['album']}")
        console.print()


@app.command("dedupe")
def dedupe_directory(
    directory: Optional[str] = typer.Argument(
        None,
        help="Directory to scan for duplicates"
    ),
):
    """
    Find duplicate audio files using fingerprinting.
    
    Example:
        samplemind dedupe ./samples
    """
    if not directory:
        console.print("[cyan]Select directory...[/cyan]")
        directory = select_directory("Select Directory to Scan")
        if not directory:
            console.print("[red]No directory selected[/red]")
            raise typer.Exit(1)
    
    dir_path = Path(directory)
    if not dir_path.is_dir():
        console.print(f"[red]Error: Not a directory: {directory}[/red]")
        raise typer.Exit(1)
    
    from samplemind.integrations import AcoustIDClient
    
    with console.status("[cyan]Scanning for duplicates...[/cyan]"):
        client = AcoustIDClient()
        duplicates = client.find_duplicates(dir_path)
    
    if not duplicates:
        console.print("[green]No duplicates found![/green]")
        return
    
    console.print(f"\n[bold yellow]⚠️  Found {len(duplicates)} duplicate pairs[/bold yellow]\n")
    
    for file1, file2 in duplicates:
        console.print(f"[red]•[/red] {file1.name}")
        console.print(f"  [red]=[/red] {file2.name}\n")


@app.command("separate")
def separate_stems(
    audio_file: Optional[str] = typer.Argument(
        None,
        help="Path to audio file"
    ),
    model: str = typer.Option(
        "balanced",
        "--model", "-m",
        help="Model preset: fast, balanced, quality"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for stems"
    ),
):
    """
    Separate audio into stems using Demucs (4-stem or 6-stem).
    
    Models:
    - fast: Quick processing, good quality
    - balanced: Default, best speed/quality trade-off (4 stems: drums, bass, vocals, other)
    - quality: Best quality, slower (6 stems: drums, bass, vocals, other, guitar, piano)
    
    Example:
        samplemind separate song.mp3 --model quality -o ./stems
    """
    if not audio_file:
        console.print("[cyan]Select audio file...[/cyan]")
        audio_file = select_audio_file("Select Audio File for Stem Separation")
        if not audio_file:
            console.print("[red]No file selected[/red]")
            raise typer.Exit(1)
    
    audio_path = Path(audio_file)
    if not audio_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)
    
    # Determine output directory
    if output:
        output_dir = Path(output)
    else:
        output_dir = audio_path.parent / f"{audio_path.stem}_stems"
    
    from samplemind.core.analysis import MultiStemSeparator
    
    console.print(f"\n[bold cyan]🎵 Multi-Stem Separation[/bold cyan]")
    console.print(f"File: {audio_path.name}")
    console.print(f"Model: {model}")
    console.print(f"Output: {output_dir}\n")
    
    with console.status("[cyan]Loading Demucs model...[/cyan]"):
        separator = MultiStemSeparator(model_preset=model)
    
    with console.status("[cyan]Separating stems (this may take a few minutes)...[/cyan]"):
        stems = separator.separate(
            audio_path,
            output_dir=output_dir,
            save_stems=True
        )
    
    console.print(f"\n[bold green]✅ Separation complete![/bold green]\n")
    
    # Display results table
    table = Table(title="Extracted Stems")
    table.add_column("Stem", style="cyan")
    table.add_column("Duration", style="yellow")
    table.add_column("File", style="green")
    
    for stem_name, stem_result in stems.items():
        table.add_row(
            stem_name.title(),
            f"{stem_result.duration:.2f}s",
            f"{audio_path.stem}_{stem_name}.wav"
        )
    
    console.print(table)
    console.print(f"\n[dim]Saved to: {output_dir}[/dim]")


# ============================================================================
# Vector Search Commands
# ============================================================================

@search_app.command("index")
def search_index(
    path: str = typer.Argument(..., help="Audio file or directory to index"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Search directories recursively"),
    level: AnalysisLevel = typer.Option(AnalysisLevel.STANDARD, "--level", "-l", help="Analysis detail level")
):
    """Index audio files for similarity search"""
    from samplemind.ai.embedding_service import get_embedding_service

    path_obj = Path(path)

    if not path_obj.exists():
        console.print(f"[red]Error: Path not found: {path}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Indexing: {path}[/cyan]")

    embedding_service = get_embedding_service()

    with console.status("[bold cyan]Analyzing and indexing...[/bold cyan]"):
        if path_obj.is_file():
            # Index single file
            try:
                result = asyncio.run(embedding_service.index_audio_file(str(path_obj), level.value))
                console.print(f"[green]✓[/green] Indexed: {path_obj.name}")
                console.print(f"  Document ID: {result['doc_id']}")
            except Exception as e:
                console.print(f"[red]Error indexing file: {e}[/red]")
                raise typer.Exit(1)
        else:
            # Index directory
            try:
                result = asyncio.run(
                    embedding_service.index_directory(
                        str(path_obj),
                        recursive=recursive,
                        analysis_level=level.value
                    )
                )

                # Display results
                table = Table(title="Indexing Results")
                table.add_column("Metric", style="cyan")
                table.add_column("Count", style="yellow")

                table.add_row("Total Files", str(result['total_files']))
                table.add_row("Indexed", f"[green]{result['indexed']}[/green]")
                table.add_row("Failed", f"[red]{result['failed']}[/red]" if result['failed'] > 0 else "0")

                console.print(table)

                # Show failed files if any
                if result['failed'] > 0:
                    console.print("\n[yellow]Failed files:[/yellow]")
                    for file_result in result['files']:
                        if file_result['status'] == 'failed':
                            console.print(f"  [red]✗[/red] {file_result['file']}: {file_result.get('error', 'Unknown error')}")

            except Exception as e:
                console.print(f"[red]Error indexing directory: {e}[/red]")
                raise typer.Exit(1)


@search_app.command("similar")
def search_similar(
    audio_file: str = typer.Argument(..., help="Reference audio file"),
    n_results: int = typer.Option(10, "--results", "-n", help="Number of results to return"),
    exclude_self: bool = typer.Option(True, "--exclude-self/--include-self", help="Exclude the query file from results")
):
    """Find similar audio files"""
    from samplemind.ai.embedding_service import get_embedding_service

    file_path = Path(audio_file)

    if not file_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Searching for files similar to: {file_path.name}[/cyan]\n")

    embedding_service = get_embedding_service()

    with console.status("[bold cyan]Searching vector database...[/bold cyan]"):
        try:
            results = asyncio.run(
                embedding_service.find_similar(
                    str(file_path),
                    n_results=n_results,
                    exclude_self=exclude_self
                )
            )
        except Exception as e:
            console.print(f"[red]Error searching: {e}[/red]")
            raise typer.Exit(1)

    if not results:
        console.print("[yellow]No similar files found. Try indexing more files first.[/yellow]")
        return

    # Display results
    table = Table(title=f"Similar Files (Top {len(results)})")
    table.add_column("#", style="dim")
    table.add_column("File", style="cyan")
    table.add_column("Similarity", style="green")
    table.add_column("Distance", style="yellow")

    for i, result in enumerate(results, 1):
        table.add_row(
            str(i),
            Path(result['file_path']).name,
            f"{result['similarity'] * 100:.1f}%",
            f"{result['distance']:.4f}"
        )

    console.print(table)


@search_app.command("recommend")
def search_recommend(
    audio_file: str = typer.Argument(..., help="Reference audio file"),
    n_results: int = typer.Option(5, "--results", "-n", help="Number of recommendations per category")
):
    """Get smart sample recommendations"""
    from samplemind.ai.embedding_service import get_embedding_service

    file_path = Path(audio_file)

    if not file_path.exists():
        console.print(f"[red]Error: File not found: {audio_file}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Getting recommendations for: {file_path.name}[/cyan]\n")

    embedding_service = get_embedding_service()

    with console.status("[bold cyan]Generating recommendations...[/bold cyan]"):
        try:
            results = asyncio.run(
                embedding_service.get_recommendations(
                    str(file_path),
                    n_results=n_results
                )
            )
        except Exception as e:
            console.print(f"[red]Error getting recommendations: {e}[/red]")
            raise typer.Exit(1)

    # Display similar samples
    if results['similar_samples']:
        table = Table(title="Similar Samples", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Similarity", style="green")

        for sample in results['similar_samples']:
            table.add_row(
                Path(sample['file_path']).name,
                f"{sample['similarity'] * 100:.1f}%"
            )

        console.print(table)
        console.print()

    # Display complementary samples
    if results['complementary_samples']:
        table = Table(title="Complementary Samples", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Similarity", style="yellow")

        for sample in results['complementary_samples']:
            table.add_row(
                Path(sample['file_path']).name,
                f"{sample['similarity'] * 100:.1f}%"
            )

        console.print(table)
        console.print()

    # Display contrasting samples
    if results['contrasting_samples']:
        table = Table(title="Contrasting Samples", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Similarity", style="magenta")

        for sample in results['contrasting_samples']:
            table.add_row(
                Path(sample['file_path']).name,
                f"{sample['similarity'] * 100:.1f}%"
            )

        console.print(table)


@search_app.command("stats")
def search_stats():
    """Show vector database statistics"""
    from samplemind.ai.embedding_service import get_embedding_service

    embedding_service = get_embedding_service()

    with console.status("[bold cyan]Fetching statistics...[/bold cyan]"):
        try:
            stats = embedding_service.get_stats()
        except Exception as e:
            console.print(f"[red]Error fetching stats: {e}[/red]")
            raise typer.Exit(1)

    table = Table(title="Vector Database Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Indexed Audio Files", str(stats.get('audio_count', 0)))
    table.add_row("Indexed Samples", str(stats.get('sample_count', 0)))
    table.add_row("Storage Location", stats.get('persist_directory', 'N/A'))

    console.print(table)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
