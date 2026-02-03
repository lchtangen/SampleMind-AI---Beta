"""
SampleMind AI - DAW Integration Command Group

Commands for interacting with Digital Audio Workstations.

Commands:
- daw:status           - Show DAW connection status
- daw:export:flp       - Export samples as FL Studio project
- daw:analyze          - Analyze samples for DAW compatibility
- daw:sync             - Sync sample library with DAW browser

Usage:
    samplemind daw:status                              # Check DAW status
    samplemind daw:export:flp kick.wav snare.wav      # Export as FL Studio project
    samplemind daw:analyze kick.wav --target-bpm 128  # Analyze for DAW use
"""

import json
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import utils

app = typer.Typer(help="🎹 DAW integration (4 commands)", no_args_is_help=True)
console = utils.console


@app.command("server")
@utils.with_error_handling
def daw_server(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host address"),
):
    """Start the DAW Bridge WebSocket Server"""
    try:
        from samplemind.server.bridge import run_server

        console.print(f"[bold green]🎹 Starting SampleMind DAW Bridge on ws://{host}:{port}/ws[/bold green]")
        console.print("Press Ctrl+C to stop.")

        run_server(host=host, port=port)

    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")
    except Exception as e:
        utils.handle_error(e, "daw:server")
        raise typer.Exit(1)

@app.command("status")
@utils.with_error_handling
def daw_status():
    """Show DAW integration status and available plugins"""
    try:
        from ....integrations.daw import (
            DAWType,
            FLStudioPlugin,
        )

        console.print("[bold cyan]DAW Integration Status[/bold cyan]")
        console.print()

        # FL Studio
        fl_plugin = FLStudioPlugin()
        fl_info = fl_plugin.get_plugin_info()

        table = Table(title="Available DAW Integrations")
        table.add_column("DAW", style="cyan")
        table.add_column("Plugin", style="green")
        table.add_column("Version")
        table.add_column("Status")

        table.add_row(
            "FL Studio",
            fl_info["name"],
            fl_info["version"],
            "[green]Available[/green]" if fl_info["version"] else "[dim]N/A[/dim]",
        )
        table.add_row(
            "Ableton Live",
            "SampleMind Control Surface",
            "2.1.0-beta",
            "[yellow]Experimental[/yellow]",
        )
        table.add_row(
            "Logic Pro",
            "SampleMind AU Plugin",
            "2.1.0-beta",
            "[yellow]Experimental[/yellow]",
        )
        table.add_row(
            "VST3 (Generic)",
            "SampleMind VST3",
            "2.1.0-beta",
            "[yellow]Planned[/yellow]",
        )

        console.print(table)

        # Usage hints
        console.print()
        console.print("[bold]Quick Start:[/bold]")
        console.print("  1. Use [cyan]daw:export:flp[/cyan] to create FL Studio projects")
        console.print("  2. Use [cyan]daw:analyze[/cyan] to analyze samples for DAW use")
        console.print("  3. Drag analyzed samples into your DAW")

    except Exception as e:
        utils.handle_error(e, "daw:status")
        raise typer.Exit(1)


@app.command("export:flp")
@utils.with_error_handling
def daw_export_flp(
    files: List[Path] = typer.Argument(..., help="Audio files to include"),
    output: Path = typer.Option(None, "--output", "-o", help="Output .flp file"),
    template: Optional[Path] = typer.Option(None, "--template", "-t", help="Template project"),
    bpm: Optional[float] = typer.Option(None, "--bpm", help="Project BPM"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Project key"),
):
    """Export samples as FL Studio project (.flp format)"""
    try:
        if not files:
            console.print("[red]Error: No files specified[/red]")
            raise typer.Exit(1)

        # Validate files
        valid_files = []
        for f in files:
            f = Path(f).expanduser().resolve()
            if f.exists():
                valid_files.append(f)
            else:
                console.print(f"[yellow]Warning: File not found: {f}[/yellow]")

        if not valid_files:
            console.print("[red]Error: No valid files found[/red]")
            raise typer.Exit(1)

        # Determine output path
        if output is None:
            output = Path.cwd() / "samplemind_project.json"  # Use JSON for now
        else:
            output = Path(output).expanduser().resolve()

        console.print(f"[bold cyan]Creating FL Studio Project[/bold cyan]")
        console.print(f"  Files: [green]{len(valid_files)}[/green]")
        console.print(f"  Output: [cyan]{output}[/cyan]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing samples...", total=None)

            # Analyze each file
            from ....integrations.daw import FLStudioPlugin

            plugin = FLStudioPlugin()
            samples_data = []

            detected_bpm = None
            detected_key = None

            for f in valid_files:
                progress.update(task, description=f"Analyzing {f.name}...")

                metadata = plugin._analyze_sample(str(f))
                if metadata:
                    samples_data.append({
                        "file_path": str(f),
                        "file_name": f.name,
                        "bpm": metadata.bpm,
                        "key": metadata.key,
                        "genre": metadata.genre,
                        "mood": metadata.mood,
                        "duration": metadata.duration,
                    })

                    # Use first detected BPM/key as project defaults
                    if detected_bpm is None and metadata.bpm:
                        detected_bpm = metadata.bpm
                    if detected_key is None and metadata.key:
                        detected_key = metadata.key

            progress.update(task, description="Creating project file...")

            # Create project data
            project_data = {
                "name": "SampleMind Generated Project",
                "version": "2.1.0-beta",
                "tempo": bpm or detected_bpm or 120.0,
                "key": key or detected_key or "C",
                "time_signature": "4/4",
                "samples": samples_data,
                "channels": [
                    {
                        "index": i,
                        "name": f"Sample {i+1}",
                        "sample": s["file_name"],
                        "volume": 0.8,
                        "pan": 0.0,
                    }
                    for i, s in enumerate(samples_data)
                ],
                "notes": [
                    f"Generated by SampleMind AI",
                    f"Contains {len(samples_data)} samples",
                    f"Import into FL Studio and drag samples to channels",
                ],
            }

            # Save project file
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, 'w') as f:
                json.dump(project_data, f, indent=2)

            progress.update(task, completed=True)

        console.print()
        console.print(f"[green]✓ Project created: {output}[/green]")
        console.print()
        console.print("[bold]Project Details:[/bold]")
        console.print(f"  Tempo: [cyan]{project_data['tempo']:.0f} BPM[/cyan]")
        console.print(f"  Key: [cyan]{project_data['key']}[/cyan]")
        console.print(f"  Samples: [cyan]{len(samples_data)}[/cyan]")
        console.print()
        console.print("[dim]Note: This creates a JSON project file.[/dim]")
        console.print("[dim]For native .flp support, use the FL Studio plugin.[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        utils.handle_error(e, "daw:export:flp")
        raise typer.Exit(1)


@app.command("analyze")
@utils.with_error_handling
def daw_analyze(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    target_bpm: Optional[float] = typer.Option(None, "--target-bpm", help="Target BPM for time-stretching"),
    target_key: Optional[str] = typer.Option(None, "--target-key", help="Target key for pitch-shifting"),
):
    """Analyze a sample for DAW compatibility"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]DAW Compatibility Analysis[/bold cyan]")
        console.print(f"  File: [green]{file.name}[/green]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing for DAW use...", total=None)

            from ....integrations.daw import FLStudioPlugin
            plugin = FLStudioPlugin()
            metadata = plugin._analyze_sample(str(file))

            progress.update(task, completed=True)

        if not metadata:
            console.print("[red]Error: Could not analyze file[/red]")
            raise typer.Exit(1)

        # Display analysis
        table = Table(title="Sample Analysis")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("DAW Recommendation", style="yellow")

        # BPM
        if metadata.bpm:
            bpm_rec = ""
            if target_bpm:
                ratio = target_bpm / metadata.bpm
                if 0.95 <= ratio <= 1.05:
                    bpm_rec = "No adjustment needed"
                else:
                    bpm_rec = f"Time-stretch by {ratio:.2f}x"
            table.add_row("BPM", f"{metadata.bpm:.1f}", bpm_rec)

        # Key
        if metadata.key:
            key_rec = ""
            if target_key:
                if target_key.lower() == metadata.key.lower():
                    key_rec = "No pitch shift needed"
                else:
                    key_rec = f"Pitch shift from {metadata.key} to {target_key}"
            table.add_row("Key", metadata.key, key_rec)

        # Other properties
        table.add_row("Genre", metadata.genre or "Unknown", "")
        table.add_row("Mood", metadata.mood or "Unknown", "")
        table.add_row("Duration", f"{metadata.duration:.2f}s" if metadata.duration else "N/A", "")
        table.add_row("Sample Rate", f"{metadata.sample_rate} Hz" if metadata.sample_rate else "N/A", "")
        table.add_row("Bit Depth", f"{metadata.bit_depth}-bit", "")
        table.add_row("Channels", "Stereo" if metadata.channels == 2 else "Mono", "")

        console.print(table)

        # AI Tags
        if metadata.ai_tags:
            console.print()
            console.print(f"[bold]AI Tags:[/bold] [cyan]{', '.join(metadata.ai_tags)}[/cyan]")

        # Recommendations
        console.print()
        console.print("[bold]DAW Workflow Recommendations:[/bold]")

        if metadata.bpm and 60 <= metadata.bpm <= 200:
            console.print(f"  • Sample is loop-friendly at {metadata.bpm:.0f} BPM")
        if metadata.key:
            console.print(f"  • Use in {metadata.key} projects or transpose as needed")
        if metadata.channels == 1:
            console.print("  • Consider stereo widening in the DAW mixer")
        if metadata.bit_depth and metadata.bit_depth < 24:
            console.print(f"  • Consider upsampling to 24-bit for better headroom")

    except typer.Exit:
        raise
    except Exception as e:
        utils.handle_error(e, "daw:analyze")
        raise typer.Exit(1)


@app.command("sync")
@utils.with_error_handling
def daw_sync(
    folder: Path = typer.Argument(..., help="Sample library folder to sync"),
    daw: str = typer.Option("flstudio", "--daw", "-d", help="Target DAW (flstudio, ableton, logic)"),
    export_metadata: bool = typer.Option(True, "--metadata/--no-metadata", help="Export metadata files"),
):
    """Sync sample library with DAW browser"""
    try:
        folder = Path(folder).expanduser().resolve()
        if not folder.is_dir():
            console.print(f"[red]Error: Not a directory: {folder}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]Syncing Library with DAW[/bold cyan]")
        console.print(f"  Folder: [green]{folder}[/green]")
        console.print(f"  Target DAW: [yellow]{daw}[/yellow]")
        console.print()

        # Find audio files
        extensions = ['.wav', '.mp3', '.flac', '.aiff', '.m4a', '.ogg']
        audio_files = [f for f in folder.rglob('*') if f.suffix.lower() in extensions]

        if not audio_files:
            console.print("[yellow]No audio files found in folder[/yellow]")
            raise typer.Exit(0)

        console.print(f"  Found: [cyan]{len(audio_files)}[/cyan] audio files")
        console.print()

        from ....integrations.daw import FLStudioPlugin
        plugin = FLStudioPlugin()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing and syncing...", total=len(audio_files))

            synced = 0
            metadata_files = []

            for i, audio_file in enumerate(audio_files):
                progress.update(task, description=f"Processing {audio_file.name}...", completed=i)

                try:
                    metadata = plugin._analyze_sample(str(audio_file))
                    if metadata and export_metadata:
                        # Create metadata sidecar file
                        meta_file = audio_file.with_suffix(audio_file.suffix + ".samplemind.json")
                        meta_data = metadata.to_fl_format()
                        with open(meta_file, 'w') as f:
                            json.dump(meta_data, f, indent=2)
                        metadata_files.append(meta_file)
                    synced += 1
                except Exception as e:
                    console.print(f"  [red]Failed: {audio_file.name}[/red]")

            progress.update(task, completed=len(audio_files))

        console.print()
        console.print(f"[green]✓ Synced {synced}/{len(audio_files)} files[/green]")

        if export_metadata and metadata_files:
            console.print(f"[cyan]  Created {len(metadata_files)} metadata files[/cyan]")
            console.print()
            console.print("[dim]Metadata files contain BPM, key, and other analysis.[/dim]")
            console.print("[dim]Some DAWs can read these for smart browsing.[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        utils.handle_error(e, "daw:sync")
        raise typer.Exit(1)
