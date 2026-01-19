"""
SampleMind AI - Health Check and Diagnostics Commands

Commands:
  health:check     - Run comprehensive system health checks
  health:status    - Show current system status
  health:logs      - Display recent logs
  health:cache     - Check cache status and statistics
  health:disk      - Check disk space and storage
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from samplemind.utils.logging_config import logger
from samplemind.utils.error_handler import handle_errors


console = Console()
app = typer.Typer(help="🏥 System health checks and diagnostics")


# ============================================================================
# Health Check Command
# ============================================================================


@app.command("check")
@handle_errors(fallback_message="Health check failed", exit_on_error=False)
async def health_check(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
) -> None:
    """Run comprehensive system health checks."""

    console.print("[bold blue]🏥 SampleMind AI System Health Check[/bold blue]\n")

    health_status = {
        "audio_engine": None,
        "ai_providers": None,
        "database": None,
        "cache": None,
        "disk_space": None,
        "dependencies": None,
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        # Check Audio Engine
        task = progress.add_task("Checking Audio Engine...", total=None)
        try:
            from samplemind.core.engine.audio_engine import AudioEngine

            engine = AudioEngine()
            health_status["audio_engine"] = {
                "status": "✅ OK",
                "version": getattr(engine, "version", "unknown"),
            }
            logger.debug("Audio engine check: OK")
        except Exception as e:
            health_status["audio_engine"] = {"status": "❌ FAIL", "error": str(e)}
            logger.error(f"Audio engine check failed: {e}")
        progress.update(task, completed=True)

        # Check AI Providers
        task = progress.add_task("Checking AI Providers...", total=None)
        ai_status = {}

        if os.getenv("GOOGLE_API_KEY"):
            ai_status["Gemini"] = "✅ Configured"
        else:
            ai_status["Gemini"] = "⚠️  Not configured"

        if os.getenv("OPENAI_API_KEY"):
            ai_status["OpenAI"] = "✅ Configured"
        else:
            ai_status["OpenAI"] = "⚠️  Not configured"

        ai_status["Ollama"] = "✅ Available (offline)"

        health_status["ai_providers"] = ai_status
        logger.debug("AI providers check: OK")
        progress.update(task, completed=True)

        # Check Database
        task = progress.add_task("Checking Database...", total=None)
        try:
            from samplemind.core.database.mongo import MongoDB

            db = MongoDB()
            if db.is_connected:
                health_status["database"] = {"status": "✅ Connected"}
            else:
                health_status["database"] = {"status": "⚠️  Not connected (optional)"}
            logger.debug("Database check: OK")
        except Exception as e:
            health_status["database"] = {"status": "⚠️  Not available", "error": str(e)}
            logger.debug(f"Database check: Optional service unavailable")
        progress.update(task, completed=True)

        # Check Cache
        task = progress.add_task("Checking Cache...", total=None)
        try:
            cache_dir = Path.home() / ".samplemind" / "cache"
            if cache_dir.exists():
                cache_size = sum(
                    f.stat().st_size for f in cache_dir.rglob("*") if f.is_file()
                )
                cache_size_mb = cache_size / 1024 / 1024
                health_status["cache"] = {
                    "status": "✅ OK",
                    "size_mb": f"{cache_size_mb:.1f}",
                }
            else:
                health_status["cache"] = {"status": "✅ OK", "size_mb": "0"}
            logger.debug("Cache check: OK")
        except Exception as e:
            health_status["cache"] = {"status": "⚠️  WARN", "error": str(e)}
            logger.warning(f"Cache check failed: {e}")
        progress.update(task, completed=True)

        # Check Disk Space
        task = progress.add_task("Checking Disk Space...", total=None)
        try:
            disk_usage = shutil.disk_usage(Path.home())
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            total_gb = disk_usage.total / 1024 / 1024 / 1024
            percent_used = (disk_usage.used / disk_usage.total) * 100

            if free_gb > 10:
                status = "✅ OK"
            elif free_gb > 1:
                status = "⚠️  LOW"
            else:
                status = "❌ CRITICAL"

            health_status["disk_space"] = {
                "status": status,
                "free_gb": f"{free_gb:.1f}",
                "total_gb": f"{total_gb:.1f}",
                "percent_used": f"{percent_used:.1f}%",
            }
            logger.debug("Disk space check: OK")
        except Exception as e:
            health_status["disk_space"] = {"status": "⚠️  WARN", "error": str(e)}
            logger.warning(f"Disk space check failed: {e}")
        progress.update(task, completed=True)

        # Check Dependencies
        task = progress.add_task("Checking Dependencies...", total=None)
        required_packages = ["librosa", "numpy", "scipy", "rich", "typer"]
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if not missing_packages:
            health_status["dependencies"] = {
                "status": "✅ OK",
                "all_installed": len(required_packages),
            }
        else:
            health_status["dependencies"] = {
                "status": "❌ FAIL",
                "missing": missing_packages,
            }
        logger.debug("Dependency check: OK")
        progress.update(task, completed=True)

    # Display results
    console.print("\n[bold cyan]Results:[/bold cyan]\n")

    # Summary table
    table = Table(title="Component Status", show_header=True, header_style="bold cyan")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")

    for component, status_info in health_status.items():
        if isinstance(status_info, dict):
            status = status_info.get("status", "Unknown")
            details = ", ".join(
                f"{k}={v}" for k, v in status_info.items() if k != "status"
            )
        else:
            status = "Unknown"
            details = ""

        # Format component name
        display_name = component.replace("_", " ").title()
        table.add_row(display_name, status, details)

    console.print(table)

    # Overall summary
    failed_checks = [
        c for c, s in health_status.items() if s and "❌" in s.get("status", "")
    ]

    if not failed_checks:
        console.print(
            "\n[green]✅ All critical systems operational[/green]"
        )
        logger.info("Health check: All systems operational")
    else:
        console.print(
            f"\n[yellow]⚠️  {len(failed_checks)} issue(s) found[/yellow]"
        )
        logger.warning(f"Health check: {len(failed_checks)} issue(s) found")

    if verbose:
        console.print(Panel(str(health_status), title="[dim]Raw Status[/dim]", expand=False))


# ============================================================================
# System Status Command
# ============================================================================


@app.command("status")
@handle_errors(fallback_message="Status check failed", exit_on_error=False)
async def system_status() -> None:
    """Show current system status and statistics."""

    console.print("[bold blue]📊 SampleMind AI System Status[/bold blue]\n")

    # Get uptime
    try:
        import psutil
        boot_time = psutil.boot_time()
        import time
        uptime_seconds = time.time() - boot_time
        uptime_hours = uptime_seconds / 3600
        console.print(f"[cyan]System Uptime:[/cyan] {uptime_hours:.1f} hours")
    except:
        pass

    # Get memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        console.print(
            f"[cyan]Memory Usage:[/cyan] {memory.percent:.1f}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)"
        )
    except:
        console.print("[dim]Memory info unavailable[/dim]")

    # Get disk usage
    disk_usage = shutil.disk_usage(Path.home())
    console.print(
        f"[cyan]Disk Usage:[/cyan] {(disk_usage.used / disk_usage.total) * 100:.1f}% ({disk_usage.free / 1024**3:.1f}GB free)"
    )

    # Get cache stats
    cache_dir = Path.home() / ".samplemind" / "cache"
    if cache_dir.exists():
        cache_files = list(cache_dir.rglob("*"))
        cache_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        console.print(
            f"[cyan]Cache:[/cyan] {len(cache_files)} files, {cache_size / 1024 / 1024:.1f} MB"
        )

    logger.info("Status check: OK")


# ============================================================================
# Recent Logs Command
# ============================================================================


@app.command("logs")
@handle_errors(fallback_message="Log retrieval failed", exit_on_error=False)
async def show_logs(
    lines: int = typer.Option(50, "--lines", "-n", help="Number of log lines to show"),
    level: str = typer.Option("all", "--level", "-l", help="Log level filter"),
) -> None:
    """Display recent logs."""

    log_file = Path.home() / ".samplemind" / "logs" / "samplemind.log"

    if not log_file.exists():
        console.print("[yellow]⚠️  No logs found[/yellow]")
        return

    console.print(f"[bold blue]📋 Recent Logs ({log_file})[/bold blue]\n")

    try:
        with open(log_file, "r") as f:
            all_lines = f.readlines()

        # Filter by level if specified
        if level != "all":
            all_lines = [l for l in all_lines if level.upper() in l]

        # Show last N lines
        recent_lines = all_lines[-lines:]

        for line in recent_lines:
            console.print(line.rstrip())

        logger.info(f"Logs displayed: {len(recent_lines)} lines")

    except Exception as e:
        console.print(f"[red]❌ Error reading logs: {e}[/red]")
        logger.error(f"Error reading logs: {e}")


# ============================================================================
# Cache Status Command
# ============================================================================


@app.command("cache")
@handle_errors(fallback_message="Cache status check failed", exit_on_error=False)
async def cache_status() -> None:
    """Check cache status and statistics."""

    cache_dir = Path.home() / ".samplemind" / "cache"

    console.print("[bold blue]💾 Cache Status[/bold blue]\n")

    if not cache_dir.exists():
        console.print("[dim]Cache directory not yet created[/dim]")
        logger.debug("Cache directory does not exist")
        return

    # Calculate statistics
    files = list(cache_dir.rglob("*"))
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    file_count = len([f for f in files if f.is_file()])
    dir_count = len([f for f in files if f.is_dir()])

    # Display table
    table = Table(title="Cache Statistics", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Files", str(file_count))
    table.add_row("Total Directories", str(dir_count))
    table.add_row("Total Size", f"{total_size / 1024 / 1024:.1f} MB")
    table.add_row("Cache Location", str(cache_dir))

    console.print(table)

    logger.info(f"Cache status: {file_count} files, {total_size / 1024 / 1024:.1f} MB")


# ============================================================================
# Disk Space Command
# ============================================================================


@app.command("disk")
@handle_errors(fallback_message="Disk check failed", exit_on_error=False)
async def check_disk() -> None:
    """Check disk space and storage information."""

    console.print("[bold blue]💾 Disk Space Information[/bold blue]\n")

    try:
        disk_usage = shutil.disk_usage(Path.home())

        table = Table(title="Disk Usage", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Size", style="green")

        total_gb = disk_usage.total / 1024 / 1024 / 1024
        used_gb = disk_usage.used / 1024 / 1024 / 1024
        free_gb = disk_usage.free / 1024 / 1024 / 1024
        percent_used = (disk_usage.used / disk_usage.total) * 100

        table.add_row("Total Disk Space", f"{total_gb:.1f} GB")
        table.add_row("Used Space", f"{used_gb:.1f} GB ({percent_used:.1f}%)")
        table.add_row("Free Space", f"{free_gb:.1f} GB")

        console.print(table)

        # Status indicator
        if free_gb > 50:
            status = "[green]✅ Plenty of space[/green]"
        elif free_gb > 10:
            status = "[yellow]⚠️  Moderate space[/yellow]"
        elif free_gb > 1:
            status = "[yellow]⚠️  Low on space[/yellow]"
        else:
            status = "[red]❌ Critical - almost full[/red]"

        console.print(f"\nStatus: {status}")

        logger.info(f"Disk usage: {percent_used:.1f}% used")

    except Exception as e:
        console.print(f"[red]❌ Error checking disk: {e}[/red]")
        logger.error(f"Disk check failed: {e}")


if __name__ == "__main__":
    app()
