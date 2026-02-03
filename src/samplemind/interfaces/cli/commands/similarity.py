"""
SampleMind AI - Similarity Command Group

Find similar audio samples using vector embeddings and ChromaDB.

Commands:
- similar:find <file>     - Find similar samples to a query file
- similar:index <folder>  - Build similarity index for a folder
- similar:compare <a> <b> - Compare similarity between two files
- similar:stats           - Show database statistics
- similar:clear           - Clear the similarity database

Usage:
    samplemind similar:index ./samples          # Index a sample library
    samplemind similar:find kick.wav --count 5  # Find 5 similar samples
    samplemind similar:compare a.wav b.wav      # Compare two files
"""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from . import utils

app = typer.Typer(help="🔍 Sample similarity search (5 commands)", no_args_is_help=True)
console = utils.console


def _get_similarity_db():
    """Lazy import to avoid circular imports"""
    from ....core.similarity import SimilarityDatabase
    return SimilarityDatabase()


@app.command("find")
@utils.with_error_handling
def similar_find(
    file: Path = typer.Argument(..., help="Query audio file"),
    count: int = typer.Option(10, "--count", "-n", help="Number of results"),
    min_similarity: float = typer.Option(0.5, "--min", help="Minimum similarity (0.0-1.0)"),
    tempo_min: Optional[float] = typer.Option(None, "--tempo-min", help="Filter: minimum BPM"),
    tempo_max: Optional[float] = typer.Option(None, "--tempo-max", help="Filter: maximum BPM"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Filter: musical key (e.g., 'C', 'Am')"),
):
    """Find similar samples to a query file"""
    try:
        file = Path(file).expanduser().resolve()
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]Finding Similar Samples[/bold cyan]")
        console.print(f"  Query: [green]{file.name}[/green]")
        console.print()

        # Build filters
        filters = {}
        if tempo_min is not None or tempo_max is not None:
            filters['tempo'] = {}
            if tempo_min is not None:
                filters['tempo']['$gte'] = tempo_min
            if tempo_max is not None:
                filters['tempo']['$lte'] = tempo_max
        if key is not None:
            filters['estimated_key'] = key

        # Get similarity database
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching for similar samples...", total=None)

            db = _get_similarity_db()
            results = db.find_similar(
                query_file=file,
                n_results=count,
                min_similarity=min_similarity,
                filters=filters if filters else None,
            )

            progress.update(task, completed=True)

        if not results:
            console.print("[yellow]No similar samples found.[/yellow]")
            console.print("[dim]Try indexing your library first: samplemind similar:index <folder>[/dim]")
            return

        # Display results
        table = Table(title=f"Similar to: {file.name}")
        table.add_column("Rank", style="dim", width=4)
        table.add_column("File", style="cyan")
        table.add_column("Similarity", justify="right", style="green")
        table.add_column("Tempo", justify="right")
        table.add_column("Key", justify="center")
        table.add_column("Character")

        for i, result in enumerate(results, 1):
            tempo = result.metadata.get('tempo', '-')
            if isinstance(tempo, (int, float)):
                tempo = f"{tempo:.0f}"

            table.add_row(
                str(i),
                Path(result.file_path).name,
                f"{result.percentage:.1f}%",
                tempo,
                result.metadata.get('estimated_key', '-'),
                result.metadata.get('character', '-'),
            )

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "similar:find")
        raise typer.Exit(1)


@app.command("index")
@utils.with_error_handling
def similar_index(
    folder: Path = typer.Argument(..., help="Folder to index"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Include subdirectories"),
    extensions: str = typer.Option("wav,mp3,flac,aiff,m4a,ogg", "--ext", help="File extensions to index"),
    rebuild: bool = typer.Option(False, "--rebuild", help="Clear and rebuild entire index"),
):
    """Build similarity index for a folder of audio files"""
    try:
        folder = Path(folder).expanduser().resolve()
        if not folder.is_dir():
            console.print(f"[red]Error: Not a directory: {folder}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]Indexing Audio Library[/bold cyan]")
        console.print(f"  Folder: [green]{folder}[/green]")
        console.print(f"  Recursive: [yellow]{'Yes' if recursive else 'No'}[/yellow]")
        console.print()

        db = _get_similarity_db()

        if rebuild:
            console.print("[yellow]Clearing existing index...[/yellow]")
            db.clear()

        ext_list = [f".{e.strip().lower()}" for e in extensions.split(",")]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Indexing files...", total=100)

            def progress_callback(current: int, total: int, filename: str):
                """Update progress bar during indexing"""
                progress.update(task, completed=(current / total) * 100, description=f"Indexing {filename}...")

            indexed = db.index_library(
                folder=folder,
                extensions=ext_list,
                recursive=recursive,
                progress_callback=progress_callback,
            )

            progress.update(task, completed=100)

        console.print()
        console.print(f"[green]✓ Indexed {indexed} audio files[/green]")

        # Show stats
        stats = db.get_stats()
        console.print(f"[cyan]Total files in database:[/cyan] {stats['total_files']}")

    except Exception as e:
        utils.handle_error(e, "similar:index")
        raise typer.Exit(1)


@app.command("compare")
@utils.with_error_handling
def similar_compare(
    file1: Path = typer.Argument(..., help="First audio file"),
    file2: Path = typer.Argument(..., help="Second audio file"),
):
    """Compare similarity between two audio files"""
    try:
        file1 = Path(file1).expanduser().resolve()
        file2 = Path(file2).expanduser().resolve()

        if not file1.exists():
            console.print(f"[red]Error: File not found: {file1}[/red]")
            raise typer.Exit(1)
        if not file2.exists():
            console.print(f"[red]Error: File not found: {file2}[/red]")
            raise typer.Exit(1)

        console.print(f"[bold cyan]Comparing Audio Files[/bold cyan]")
        console.print(f"  File 1: [green]{file1.name}[/green]")
        console.print(f"  File 2: [green]{file2.name}[/green]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing files...", total=None)

            db = _get_similarity_db()
            similarity = db.compare_files(file1, file2)

            progress.update(task, completed=True)

        # Display result with visual indicator
        percentage = similarity * 100
        bar_length = 30
        filled = int(bar_length * similarity)

        if percentage >= 80:
            color = "green"
            description = "Very Similar"
        elif percentage >= 60:
            color = "yellow"
            description = "Similar"
        elif percentage >= 40:
            color = "cyan"
            description = "Somewhat Similar"
        else:
            color = "red"
            description = "Different"

        bar = "█" * filled + "░" * (bar_length - filled)

        console.print()
        console.print(f"[{color}]Similarity: {percentage:.1f}% - {description}[/{color}]")
        console.print(f"[{color}]{bar}[/{color}]")

    except Exception as e:
        utils.handle_error(e, "similar:compare")
        raise typer.Exit(1)


@app.command("stats")
@utils.with_error_handling
def similar_stats():
    """Show similarity database statistics"""
    try:
        db = _get_similarity_db()
        stats = db.get_stats()

        table = Table(title="Similarity Database Statistics")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Collection Name", stats['collection_name'])
        table.add_row("Total Indexed Files", str(stats['total_files']))
        table.add_row("Embedding Dimension", str(stats['embedding_dim']))
        table.add_row("Storage Location", stats['persist_directory'])

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "similar:stats")
        raise typer.Exit(1)


@app.command("clear")
@utils.with_error_handling
def similar_clear(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Clear the similarity database"""
    try:
        if not confirm:
            console.print("[yellow]This will delete all indexed audio embeddings.[/yellow]")
            response = typer.confirm("Are you sure you want to continue?")
            if not response:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        db = _get_similarity_db()
        db.clear()

        console.print("[green]✓ Similarity database cleared[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        utils.handle_error(e, "similar:clear")
        raise typer.Exit(1)
