#!/usr/bin/env python3
"""Sample Pack Creator Commands - Create and manage professional sample packs"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from samplemind.core.library.pack_creator import (
    SamplePackCreator,
    PackTemplate,
)
from . import utils

app = typer.Typer(help="📦 Sample Pack Creator - Organize samples into professional packs", no_args_is_help=True)
console = utils.console


@app.command("create")
@utils.with_error_handling
def create_pack(
    name: str = typer.Argument(..., help="Pack name"),
    template: str = typer.Option(
        "custom",
        "--template", "-t",
        help="Pack template: custom, drums, melodic, effects, loops"
    ),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Pack author name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Pack description"),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for pack"
    ),
) -> None:
    """
    Create a new sample pack.

    Available templates:
    - custom: User-defined structure
    - drums: Organized drum samples (kicks, snares, hihats, etc.)
    - melodic: Melodic samples (synths, leads, pads, bass)
    - effects: Sound effects (transitions, impacts, risers, drops)
    - loops: Music loops (drums, music, bass, melody, grooves)
    """
    try:
        # Validate template
        template_lower = template.lower()
        valid_templates = [t.value for t in PackTemplate]
        if template_lower not in valid_templates:
            console.print(f"[red]✗ Invalid template. Use: {', '.join(valid_templates)}[/red]")
            raise typer.Exit(1)

        # Display header
        console.print()
        console.print(f"[bold cyan]📦 Create Sample Pack[/bold cyan]")
        console.print(f"[cyan]Name: {name}[/cyan]")
        console.print(f"[cyan]Template: {template_lower}[/cyan]")
        if author:
            console.print(f"[cyan]Author: {author}[/cyan]")
        console.print()

        # Create pack
        creator = SamplePackCreator()
        pack = creator.create_pack(
            name=name,
            template=PackTemplate[template_lower.upper()],
            author=author or "Unknown",
            description=description or "",
            output_dir=output
        )

        # Display results
        console.print(f"[green]✓ Pack created successfully![/green]")
        console.print()

        # Show summary
        summary = pack.get_summary()
        summary_table = Table(show_header=False, show_lines=False, padding=(0, 2))
        summary_table.add_column(width=20, style="cyan")
        summary_table.add_column()
        for key, value in summary.items():
            summary_table.add_row(f"{key}:", str(value))

        console.print(summary_table)
        console.print()
        console.print(f"[dim]Use: samplemind pack:add <pack_dir> <sample_file> to add samples[/dim]")
        console.print(f"[dim]Use: samplemind pack:export <pack_dir> to export the pack[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "pack:create")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("add")
@utils.with_error_handling
def add_samples(
    pack_dir: Optional[Path] = typer.Argument(None, help="Sample pack directory"),
    source: Optional[Path] = typer.Option(
        None,
        "--source", "-s",
        help="Audio file or folder to add"
    ),
    organize: bool = typer.Option(
        True,
        "--organize",
        help="Organize samples by template folders"
    ),
) -> None:
    """
    Add samples to an existing pack.

    Samples can be added from:
    - Single files: samplemind pack:add <pack> --source sample.wav
    - Folders: samplemind pack:add <pack> --source ./samples
    """
    try:
        # Pack directory selection
        if not pack_dir:
            from samplemind.utils.file_picker import select_folder
            pack_dir = select_folder(title="Select sample pack directory")
            if not pack_dir:
                raise typer.Exit(1)

        pack_dir = Path(pack_dir).resolve()
        if not pack_dir.exists():
            console.print(f"[red]✗ Pack directory not found: {pack_dir}[/red]")
            raise typer.Exit(1)

        # Source selection
        if not source:
            from samplemind.utils.file_picker import select_audio_file
            source = select_audio_file(title="Select samples to add")
            if not source:
                raise typer.Exit(1)

        source = Path(source).resolve()

        console.print()
        console.print(f"[bold cyan]📦 Add Samples to Pack[/bold cyan]")
        console.print(f"[cyan]Pack: {pack_dir.name}[/cyan]")
        console.print(f"[cyan]Source: {source.name}[/cyan]\n")

        # Load pack
        from samplemind.core.library.pack_creator import SamplePack, PackMetadata

        # Try to load existing pack metadata
        metadata_file = pack_dir / "pack.json"
        if metadata_file.exists():
            import json
            with open(metadata_file) as f:
                data = json.load(f)
            # Create metadata from JSON (simplified)
            from samplemind.core.library.pack_creator import PackMetadata
            metadata = PackMetadata(**data)
        else:
            metadata = PackMetadata(name=pack_dir.name)

        pack = SamplePack(
            name=pack_dir.name,
            pack_dir=pack_dir,
            template=None,  # Detect from structure
            metadata=metadata
        )

        # Add samples
        if source.is_file():
            # Single file
            success = pack.add_sample(source)
            if success:
                console.print(f"[green]✓ Added 1 sample[/green]")
            else:
                console.print(f"[red]✗ Failed to add sample[/red]")
                raise typer.Exit(1)
        else:
            # Folder
            count = pack.add_samples_from_folder(source, organize_by_type=organize)
            if count > 0:
                console.print(f"[green]✓ Added {count} samples[/green]")
            else:
                console.print(f"[red]✗ No samples added[/red]")
                raise typer.Exit(1)

        # Save metadata
        pack.save_metadata()
        console.print(f"\n[dim]Pack now contains {pack.metadata.sample_count} samples ({pack.metadata.total_size_mb:.1f} MB)[/dim]")

    except utils.CLIError as e:
        utils.handle_error(e, "pack:add")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("export")
@utils.with_error_handling
def export_pack(
    pack_dir: Optional[Path] = typer.Argument(None, help="Sample pack directory"),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for export"
    ),
    format_type: str = typer.Option(
        "zip",
        "--format", "-f",
        help="Export format: zip, tar, dir"
    ),
) -> None:
    """
    Export a sample pack to a file.

    Supported formats:
    - zip: Compressed ZIP archive (recommended)
    - tar: TAR.GZ compressed archive
    - dir: Copy to directory
    """
    try:
        # Pack directory selection
        if not pack_dir:
            from samplemind.utils.file_picker import select_folder
            pack_dir = select_folder(title="Select sample pack directory")
            if not pack_dir:
                raise typer.Exit(1)

        pack_dir = Path(pack_dir).resolve()
        if not pack_dir.exists():
            console.print(f"[red]✗ Pack directory not found: {pack_dir}[/red]")
            raise typer.Exit(1)

        # Output directory
        if not output:
            output = Path.cwd() / "exported_packs"

        console.print()
        console.print(f"[bold cyan]📦 Export Sample Pack[/bold cyan]")
        console.print(f"[cyan]Pack: {pack_dir.name}[/cyan]")
        console.print(f"[cyan]Format: {format_type.lower()}[/cyan]\n")

        # Load pack
        from samplemind.core.library.pack_creator import SamplePack, PackMetadata
        import json

        metadata_file = pack_dir / "pack.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                data = json.load(f)
            metadata = PackMetadata(**data)
        else:
            metadata = PackMetadata(name=pack_dir.name)

        pack = SamplePack(
            name=pack_dir.name,
            pack_dir=pack_dir,
            template=None,
            metadata=metadata
        )

        # Export
        export_path = pack.export(output, format=format_type.lower())

        console.print(f"[green]✓ Pack exported successfully![/green]")
        console.print()

        export_table = Table(show_header=False, show_lines=False, padding=(0, 2))
        export_table.add_column(width=20, style="cyan")
        export_table.add_column()
        export_table.add_row("Output:", str(export_path))
        export_table.add_row("Format:", format_type.lower())
        export_table.add_row("Samples:", str(len(pack.samples)))
        export_table.add_row("Size:", f"{pack.metadata.total_size_mb:.1f} MB")

        console.print(export_table)

    except utils.CLIError as e:
        utils.handle_error(e, "pack:export")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("info")
@utils.with_error_handling
def pack_info(
    pack_dir: Optional[Path] = typer.Argument(None, help="Sample pack directory"),
) -> None:
    """
    Display information about a sample pack.
    """
    try:
        # Pack directory selection
        if not pack_dir:
            from samplemind.utils.file_picker import select_folder
            pack_dir = select_folder(title="Select sample pack directory")
            if not pack_dir:
                raise typer.Exit(1)

        pack_dir = Path(pack_dir).resolve()
        if not pack_dir.exists():
            console.print(f"[red]✗ Pack directory not found: {pack_dir}[/red]")
            raise typer.Exit(1)

        console.print()
        console.print(f"[bold cyan]📦 Pack Information[/bold cyan]\n")

        # Load pack metadata
        from samplemind.core.library.pack_creator import SamplePack, PackMetadata
        import json

        metadata_file = pack_dir / "pack.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                data = json.load(f)
            metadata = PackMetadata(**data)
        else:
            metadata = PackMetadata(name=pack_dir.name)

        pack = SamplePack(
            name=pack_dir.name,
            pack_dir=pack_dir,
            template=None,
            metadata=metadata
        )

        # Display info
        info_table = Table(show_header=False, show_lines=False, padding=(0, 2))
        info_table.add_column(width=20, style="cyan")
        info_table.add_column()
        info_table.add_row("Pack Name:", metadata.name)
        info_table.add_row("Version:", metadata.version)
        info_table.add_row("Author:", metadata.author)
        info_table.add_row("Description:", metadata.description or "(none)")
        info_table.add_row("Samples:", str(metadata.sample_count))
        info_table.add_row("Total Size:", f"{metadata.total_size_mb:.1f} MB")
        info_table.add_row("Created:", metadata.created_date)
        info_table.add_row("Updated:", metadata.updated_date)
        info_table.add_row("License:", metadata.license)

        console.print(info_table)

        # Show sample list if not too many
        if 0 < metadata.sample_count <= 50:
            console.print()
            console.print("[bold cyan]Samples:[/bold cyan]")
            samples_table = Table(show_header=True, header_style="bold cyan")
            samples_table.add_column("Filename", style="cyan")
            samples_table.add_column("Duration (s)", justify="right", style="yellow")
            samples_table.add_column("Size (MB)", justify="right", style="yellow")
            samples_table.add_column("BPM", justify="right", style="green")

            for filename, sample_info in sorted(pack.samples.items()):
                bpm_str = f"{sample_info.bpm:.0f}" if sample_info.bpm else "-"
                samples_table.add_row(
                    filename,
                    f"{sample_info.duration_seconds:.2f}",
                    f"{sample_info.file_size_mb:.1f}",
                    bpm_str
                )

            console.print(samples_table)

    except utils.CLIError as e:
        utils.handle_error(e, "pack:info")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list-templates")
@utils.with_error_handling
def list_templates() -> None:
    """
    Show available pack templates.
    """
    console.print()
    console.print("[bold cyan]📦 Available Sample Pack Templates[/bold cyan]\n")

    templates_table = Table(show_header=True, header_style="bold cyan")
    templates_table.add_column("Template", style="cyan")
    templates_table.add_column("Description")
    templates_table.add_column("Folders")

    for template in PackTemplate:
        if template == PackTemplate.CUSTOM:
            folders = "User-defined"
        else:
            config = SamplePackCreator.TEMPLATE_STRUCTURE[template]
            folders = ", ".join(config["folders"][:3])
            if len(config["folders"]) > 3:
                folders += ", ..."

        templates_table.add_row(
            template.value,
            SamplePackCreator.TEMPLATE_STRUCTURE[template]["description"],
            folders
        )

    console.print(templates_table)


__all__ = ["app"]
