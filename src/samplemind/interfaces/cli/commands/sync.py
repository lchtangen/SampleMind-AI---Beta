"""
SampleMind AI - Sync Commands
"""

from pathlib import Path

import typer

from samplemind.core.config import Settings
from samplemind.interfaces.cli.commands import utils
from samplemind.services.storage import (
    LocalStorageProvider,
    MockS3StorageProvider,
    S3StorageProvider,
)
from samplemind.services.sync import SyncManager

app = typer.Typer(
    help="☁️  Sync commands (upload/download library)",
    no_args_is_help=True,
)

console = utils.console

async def get_sync_manager():
    settings = Settings()

    if settings.storage_provider == "s3":
        provider = S3StorageProvider(settings.s3_bucket_name, settings.aws_region)
    elif settings.storage_provider == "s3-mock":
        provider = MockS3StorageProvider(settings.s3_bucket_name or "samplemind-mock")
    else:
        provider = LocalStorageProvider(Path("./data/cloud_mock"))

    return SyncManager(provider)


@app.command("up")
@utils.with_error_handling
@utils.async_command
async def sync_up(
    library_path: Path = typer.Argument(..., help="Path to local library"),
):
    """
    ☁️  Upload library to cloud
    """
    console.print("[bold cyan]Syncing UP to cloud...[/bold cyan]")

    manager = await get_sync_manager()
    await manager.enable_sync("cli_user")

    with utils.ProgressTracker("Uploading"):
        stats = await manager.sync_library(library_path, direction="up")

    console.print(f"[green]Uploaded: {stats['uploaded']} files[/green]")
    console.print(f"[red]Errors:   {stats['errors']}[/red]")


@app.command("down")
@utils.with_error_handling
@utils.async_command
async def sync_down(
    library_path: Path = typer.Argument(..., help="Path to local library"),
):
    """
    ☁️  Download library from cloud (and hydrate analysis)
    """
    console.print("[bold cyan]Syncing DOWN from cloud...[/bold cyan]")

    manager = await get_sync_manager()
    await manager.enable_sync("cli_user")

    with utils.ProgressTracker("Downloading"):
        stats = await manager.sync_library(library_path, direction="down")

    console.print(f"[green]Downloaded: {stats['downloaded']} files[/green]")
    if stats['downloaded'] > 0:
        console.print("[dim]Analysis data hydrated automatically.[/dim]")
    console.print(f"[red]Errors:     {stats['errors']}[/red]")
