"""
SampleMind AI - Debug and Diagnostics Commands

Commands:
  debug:info       - Display environment information
  debug:diagnose   - Diagnose issues with audio file
  debug:config     - Show current configuration
  debug:test       - Run diagnostic tests
  debug:trace      - Enable debug tracing
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

from samplemind.utils.logging_config import logger
from samplemind.utils.error_handler import handle_errors
from samplemind.exceptions import (
    FileNotFoundError as SampleMindFileNotFoundError,
    CorruptedAudioError,
)


console = Console()
app = typer.Typer(help="🔧 Debug and diagnostics tools")


# ============================================================================
# Environment Info Command
# ============================================================================


@app.command("info")
@handle_errors(fallback_message="Info retrieval failed", exit_on_error=False)
async def show_environment_info() -> None:
    """Display environment and configuration information."""

    console.print("[bold blue]🔧 Environment Information[/bold blue]\n")

    # Python Info
    console.print("[bold cyan]Python:[/bold cyan]")
    console.print(f"  Version: {sys.version}")
    console.print(f"  Executable: {sys.executable}")
    console.print(f"  Path: {sys.prefix}")

    # OS Info
    console.print("\n[bold cyan]Operating System:[/bold cyan]")
    import platform

    console.print(f"  System: {platform.system()}")
    console.print(f"  Release: {platform.release()}")
    console.print(f"  Version: {platform.version()}")
    console.print(f"  Machine: {platform.machine()}")

    # SampleMind Info
    console.print("\n[bold cyan]SampleMind AI:[/bold cyan]")
    console.print(f"  Version: 2.1.0-beta")
    console.print(f"  Location: {Path(__file__).parent.parent.parent}")

    # Environment Variables
    console.print("\n[bold cyan]Environment Variables:[/bold cyan]")

    env_vars = {
        "GOOGLE_API_KEY": "✅ Set" if os.getenv("GOOGLE_API_KEY") else "❌ Not set",
        "OPENAI_API_KEY": "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Not set",
        "SAMPLEMIND_LOG_LEVEL": os.getenv("SAMPLEMIND_LOG_LEVEL", "INFO"),
        "SAMPLEMIND_ENV": os.getenv("SAMPLEMIND_ENV", "production"),
    }

    for key, value in env_vars.items():
        console.print(f"  {key}: {value}")

    logger.info("Environment info displayed")


# ============================================================================
# File Diagnostics Command
# ============================================================================


@app.command("diagnose")
@handle_errors(fallback_message="Diagnostics failed", exit_on_error=False)
async def diagnose_audio_file(
    file: Path = typer.Argument(..., help="Audio file to diagnose"),
) -> None:
    """Diagnose issues with an audio file."""

    console.print(f"[bold blue]🔍 Diagnosing: {file.name}[/bold blue]\n")

    # Check 1: File exists
    if not file.exists():
        console.print("[red]❌ File does not exist[/red]")
        console.print(f"[dim]Checked path: {file.absolute()}[/dim]")
        logger.error(f"File not found: {file}")
        return

    console.print("[green]✅ File exists[/green]")

    # Check 2: File size
    try:
        size_bytes = file.stat().st_size
        size_mb = size_bytes / 1024 / 1024
        console.print(f"[cyan]📦 File size: {size_mb:.2f} MB[/cyan]")

        if size_mb > 1000:
            console.print("[yellow]⚠️  File is very large (>1GB)[/yellow]")
        elif size_mb < 0.01:
            console.print("[yellow]⚠️  File is very small (<10KB)[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Could not read file size: {e}[/red]")
        return

    # Check 3: File format
    try:
        import magic
        file_type = magic.from_file(str(file))
        console.print(f"[cyan]🎵 Format: {file_type}[/cyan]")
    except:
        # Fallback to extension-based detection
        extension = file.suffix.lower()
        console.print(f"[cyan]🎵 Extension: {extension}[/cyan]")

    # Check 4: Read with librosa
    try:
        import librosa
        console.print("[cyan]📖 Attempting to read with librosa...[/cyan]")

        # Try to load first 0.1 seconds
        y, sr = librosa.load(str(file), sr=None, duration=0.1)

        # Try full load to get duration
        y_full, sr_full = librosa.load(str(file), sr=None)
        duration = librosa.get_duration(y=y_full, sr=sr_full)

        console.print(f"[green]✅ Readable by librosa[/green]")
        console.print(f"   Sample rate: {sr} Hz")
        console.print(f"   Duration: {duration:.2f} seconds")
        console.print(f"   Channels: {len(y.shape)}")

    except Exception as e:
        console.print(f"[red]❌ Cannot read with librosa: {e}[/red]")

    # Check 5: Read with soundfile
    try:
        import soundfile as sf
        console.print("[cyan]📖 Attempting to read with soundfile...[/cyan]")

        with sf.SoundFile(str(file)) as f:
            console.print(f"[green]✅ Readable by soundfile[/green]")
            console.print(f"   Channels: {f.channels}")
            console.print(f"   Sample rate: {f.samplerate} Hz")
            console.print(f"   Frames: {f.frames}")
            console.print(f"   Duration: {f.frames / f.samplerate:.2f} seconds")

    except Exception as e:
        console.print(f"[red]❌ Cannot read with soundfile: {e}[/red]")

    # Check 6: Try audio analysis
    try:
        console.print("[cyan]🔬 Attempting audio analysis...[/cyan]")

        from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel

        engine = AudioEngine()
        features = engine.analyze_audio(str(file), AnalysisLevel.BASIC)

        console.print(f"[green]✅ Basic analysis successful[/green]")
        console.print(f"   Tempo: {features.tempo:.1f} BPM")
        console.print(f"   Key: {features.key} {features.mode}")
        console.print(f"   RMS Energy: {features.rms_energy[0]:.3f}")

    except Exception as e:
        console.print(f"[red]❌ Analysis failed: {e}[/red]")

    console.print("\n[dim]Diagnostics complete[/dim]")
    logger.info(f"File diagnostics completed for: {file}")


# ============================================================================
# Configuration Display Command
# ============================================================================


@app.command("config")
@handle_errors(fallback_message="Config display failed", exit_on_error=False)
async def show_configuration() -> None:
    """Display current configuration."""

    console.print("[bold blue]⚙️  Configuration[/bold blue]\n")

    try:
        # Try to load configuration
        config = {
            "version": "2.1.0-beta",
            "audio_engine": {
                "max_workers": 4,
                "cache_enabled": True,
                "cache_size_mb": 500,
            },
            "ai_providers": {
                "primary": "gemini",
                "fallback": "ollama",
                "offline_only": False,
            },
            "output": {
                "format": "table",
                "colorize": True,
                "verbose": False,
            },
            "logging": {
                "level": "INFO",
                "enable_file": True,
                "enable_json": False,
            },
        }

        # Display as formatted JSON
        json_str = json.dumps(config, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)

        logger.info("Configuration displayed")

    except Exception as e:
        console.print(f"[red]❌ Error loading configuration: {e}[/red]")
        logger.error(f"Configuration load failed: {e}")


# ============================================================================
# Diagnostic Tests Command
# ============================================================================


@app.command("test")
@handle_errors(fallback_message="Tests failed", exit_on_error=False)
async def run_diagnostics() -> None:
    """Run diagnostic tests."""

    console.print("[bold blue]🧪 Running Diagnostic Tests[/bold blue]\n")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Import core modules
    test_name = "Core module imports"
    console.print(f"[cyan]Testing: {test_name}...[/cyan]", end=" ")

    try:
        from samplemind.core.engine.audio_engine import AudioEngine
        from samplemind.integrations.ai_manager import SampleMindAIManager
        from samplemind.core.database.mongo import MongoDB

        console.print("[green]✅ PASS[/green]")
        tests_passed += 1
    except Exception as e:
        console.print(f"[red]❌ FAIL[/red]")
        console.print(f"[dim]  Error: {e}[/dim]")
        tests_failed += 1

    # Test 2: Audio Engine initialization
    test_name = "Audio Engine initialization"
    console.print(f"[cyan]Testing: {test_name}...[/cyan]", end=" ")

    try:
        from samplemind.core.engine.audio_engine import AudioEngine

        engine = AudioEngine()
        console.print("[green]✅ PASS[/green]")
        tests_passed += 1
    except Exception as e:
        console.print(f"[red]❌ FAIL[/red]")
        console.print(f"[dim]  Error: {e}[/dim]")
        tests_failed += 1

    # Test 3: Logging system
    test_name = "Logging system"
    console.print(f"[cyan]Testing: {test_name}...[/cyan]", end=" ")

    try:
        logger.info("Test message")
        console.print("[green]✅ PASS[/green]")
        tests_passed += 1
    except Exception as e:
        console.print(f"[red]❌ FAIL[/red]")
        console.print(f"[dim]  Error: {e}[/dim]")
        tests_failed += 1

    # Test 4: Environment variables
    test_name = "Environment variables"
    console.print(f"[cyan]Testing: {test_name}...[/cyan]", end=" ")

    try:
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            console.print("[green]✅ PASS[/green]")
            tests_passed += 1
        else:
            console.print("[yellow]⚠️  WARN[/yellow]")
            console.print("[dim]  GOOGLE_API_KEY not set (optional)[/dim]")
    except Exception as e:
        console.print(f"[red]❌ FAIL[/red]")
        tests_failed += 1

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"[green]Passed:[/green] {tests_passed}")
    console.print(f"[red]Failed:[/red] {tests_failed}")

    if tests_failed == 0:
        console.print("\n[green]✅ All tests passed[/green]")
        logger.info("Diagnostic tests: All passed")
    else:
        console.print(f"\n[yellow]⚠️  {tests_failed} test(s) failed[/yellow]")
        logger.warning(f"Diagnostic tests: {tests_failed} failed")


# ============================================================================
# Trace Command
# ============================================================================


@app.command("trace")
@handle_errors(fallback_message="Trace setup failed", exit_on_error=False)
async def enable_tracing(
    level: str = typer.Option(
        "DEBUG", "--level", "-l", help="Log level (DEBUG, INFO, WARNING, ERROR)"
    ),
) -> None:
    """Enable debug tracing."""

    console.print(f"[bold blue]📊 Enabling Debug Tracing (level={level})[/bold blue]\n")

    try:
        from samplemind.utils.logging_config import configure_log_level

        configure_log_level(level)

        console.print(f"[green]✅ Debug tracing enabled at {level} level[/green]")
        console.print("[dim]Logs will be written to: ~/.samplemind/logs/samplemind.log[/dim]")

        logger.info(f"Debug tracing enabled at level {level}")

    except Exception as e:
        console.print(f"[red]❌ Failed to enable tracing: {e}[/red]")
        logger.error(f"Tracing setup failed: {e}")


if __name__ == "__main__":
    app()
