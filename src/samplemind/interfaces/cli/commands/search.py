"""
SampleMind AI - Semantic Search CLI (Phase 11)

FAISS-powered semantic search using CLAP audio+text embeddings.

Commands:
  samplemind semantic "dark trap kick" --top 20 --json
  samplemind index rebuild ./samples/
  samplemind index stats

Usage::

    samplemind semantic "ambient pad with reverb" --top 10
    samplemind semantic "808 bass" --top 5 --json
    samplemind index rebuild ~/samples/
    samplemind index stats
"""

import json
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()
app = typer.Typer(help="Semantic search + FAISS index management")


# ── samplemind semantic ───────────────────────────────────────────────────────


@app.command("query")
def semantic_query(
    query: str = typer.Argument(
        ..., help="Natural language description (e.g. 'dark trap kick')"
    ),
    top: int = typer.Option(20, "--top", "-n", help="Number of results to return"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    min_score: float = typer.Option(
        0.0, "--min-score", help="Minimum similarity score [0-1]"
    ),
) -> None:
    """Search sample library with a text description using CLAP embeddings."""
    from samplemind.core.search.faiss_index import get_index

    idx = get_index(auto_load=True)

    if idx.is_empty:
        console.print(
            "[yellow]⚠  FAISS index is empty.[/yellow] "
            "Run [bold]samplemind index rebuild <folder>[/bold] first."
        )
        raise typer.Exit(1)

    results = idx.search_text(query, top_k=top)
    filtered = [r for r in results if r.score >= min_score]

    if json_output:
        data = [
            {
                "filename": r.filename,
                "path": r.path,
                "score": round(r.score, 4),
                "bpm": r.metadata.get("bpm"),
                "key": r.metadata.get("key"),
                "energy": r.metadata.get("energy"),
                "genre_labels": r.metadata.get("genre_labels", []),
            }
            for r in filtered
        ]
        typer.echo(json.dumps(data, indent=2))
        return

    if not filtered:
        console.print(f"[yellow]No results found for:[/yellow] {query}")
        return

    table = Table(
        title=f'Search: "{query}"', show_header=True, header_style="bold cyan"
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Filename", min_width=30)
    table.add_column("Score", justify="right", width=7)
    table.add_column("BPM", justify="right", width=6)
    table.add_column("Key", width=5)
    table.add_column("Energy", width=7)
    table.add_column("Genres")

    for i, r in enumerate(filtered, 1):
        meta = r.metadata
        bpm_str = f"{meta.get('bpm'):.1f}" if meta.get("bpm") else "—"
        key_str = meta.get("key") or "—"
        energy_str = meta.get("energy") or "—"
        genres = ", ".join(meta.get("genre_labels", [])[:3]) or "—"
        score_color = (
            "green" if r.score > 0.7 else ("yellow" if r.score > 0.4 else "red")
        )
        table.add_row(
            str(i),
            r.filename,
            f"[{score_color}]{r.score:.3f}[/{score_color}]",
            bpm_str,
            key_str,
            energy_str,
            genres,
        )

    console.print(table)
    console.print(f"\n[dim]{len(filtered)} results (index size: {idx.size})[/dim]")


# ── samplemind index ──────────────────────────────────────────────────────────


index_app = typer.Typer(help="FAISS index management")


@index_app.command("rebuild")
def index_rebuild(
    folder: Path | None = typer.Argument(
        None, help="Folder to index (default: all libraries)"
    ),
    extensions: str = typer.Option(
        "wav,aiff,mp3,flac,ogg", help="Comma-separated audio extensions"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Rebuild even if index exists"
    ),
) -> None:
    """Build or rebuild the FAISS semantic index from audio files."""
    import samplemind.core.search.faiss_index as _fi
    from samplemind.core.search.faiss_index import FAISSIndex

    exts = {f".{e.strip().lstrip('.')}" for e in extensions.split(",")}

    # Find audio files
    search_dir = folder or Path.home()
    if not search_dir.exists():
        console.print(f"[red]Folder not found:[/red] {search_dir}")
        raise typer.Exit(1)

    console.print(f"[cyan]Scanning:[/cyan] {search_dir}")
    audio_paths = [
        str(p)
        for p in search_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in exts
    ]

    if not audio_paths:
        console.print(f"[yellow]No audio files found in {search_dir}[/yellow]")
        raise typer.Exit(1)

    console.print(f"[green]Found {len(audio_paths)} audio files[/green]")

    with console.status(f"Building FAISS index ({len(audio_paths)} files)..."):
        idx = FAISSIndex()
        idx.build(audio_paths=audio_paths, show_progress=True)
        idx.save()
        _fi._global_index = idx

    console.print(
        f"[bold green]✓ FAISS index built:[/bold green] "
        f"{idx.size} vectors saved to {idx._dir}"
    )


@index_app.command("stats")
def index_stats() -> None:
    """Show FAISS index statistics."""
    from samplemind.core.search.faiss_index import DEFAULT_INDEX_DIR, get_index

    idx = get_index(auto_load=True)

    console.print("\n[bold cyan]FAISS Index Statistics[/bold cyan]")
    console.print(f"  Index path:   {DEFAULT_INDEX_DIR}")
    console.print(f"  Total vectors: [bold]{idx.size}[/bold]")
    console.print("  Embedding dim: 512 (CLAP)")

    if idx.is_empty:
        console.print(
            "\n[yellow]Index is empty. Run:[/yellow] samplemind index rebuild <folder>"
        )
    else:
        console.print("\n[green]✓ Index is ready for semantic search[/green]")


# ── Register as subcommand of main app ────────────────────────────────────────

# Usage in menu.py:
#   from samplemind.interfaces.cli.commands.search import app as search_app, index_app
#   main_app.add_typer(search_app, name="semantic")
#   main_app.add_typer(index_app, name="index")
