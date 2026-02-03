"""
SampleMind AI - CLI Command Utilities

Shared utilities, decorators, and helpers for all CLI commands.
Provides consistent functionality across all 200+ commands:
- Output formatting (JSON, CSV, table)
- Progress tracking
- Error handling
- Audio engine integration
- Caching and performance
"""

import json
import csv
import asyncio
from typing import Any, Dict, List, Optional, Callable, TypeVar
from pathlib import Path
from functools import wraps
from dataclasses import asdict

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
import typer

# ============================================================================
# GLOBAL CONSOLE
# ============================================================================

console = Console()

# ============================================================================
# OUTPUT FORMATTERS
# ============================================================================

def format_json(data: Any, pretty: bool = True) -> str:
    """Format data as JSON"""
    if pretty:
        return json.dumps(data, indent=2, default=str)
    return json.dumps(data, default=str)


def format_csv(data: List[Dict], output_file: Optional[Path] = None) -> str:
    """Format data as CSV"""
    if not data:
        return ""

    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    result = output.getvalue()
    output.close()

    if output_file:
        output_file.write_text(result)
        console.print(f"[green]✓[/green] CSV exported to: {output_file}")

    return result


def format_table(
    title: str,
    data: List[Dict],
    columns: Optional[List[str]] = None,
) -> Table:
    """Format data as a Rich table"""
    table = Table(title=title, show_header=True, header_style="bold cyan")

    if not columns and data:
        columns = list(data[0].keys())

    for col in columns or []:
        table.add_column(col, style="cyan")

    for row in data:
        values = [str(row.get(col, "")) for col in columns or []]
        table.add_row(*values)

    return table


def format_yaml(data: Any) -> str:
    """Format data as YAML"""
    try:
        import yaml
        return yaml.dump(data, default_flow_style=False)
    except ImportError:
        console.print("[yellow]⚠ PyYAML not installed, using JSON instead[/yellow]")
        return format_json(data)


# ============================================================================
# OUTPUT HANDLERS
# ============================================================================

def output_result(
    data: Any,
    format: str = "table",
    title: str = "Result",
    output_file: Optional[Path] = None,
    quiet: bool = False,
) -> None:
    """Handle output in specified format"""
    if quiet:
        return

    if format == "json":
        result = format_json(data)
        if output_file:
            output_file.write_text(result)
            console.print(f"[green]✓[/green] JSON exported to: {output_file}")
        else:
            console.print(result)

    elif format == "csv" and isinstance(data, list):
        format_csv(data, output_file)

    elif format == "yaml":
        result = format_yaml(data)
        if output_file:
            output_file.write_text(result)
            console.print(f"[green]✓[/green] YAML exported to: {output_file}")
        else:
            console.print(result)

    elif format == "table":
        if isinstance(data, list) and data and isinstance(data[0], dict):
            table = format_table(title, data)
            console.print(table)
        else:
            # Fallback to JSON for complex structures
            console.print(format_json(data))

    else:
        console.print(format_json(data))


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

class ProgressTracker:
    """Context manager for progress tracking"""

    def __init__(self, description: str = "Processing"):
        self.description = description
        self.progress = None

    def __enter__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn(f"[progress.description]{self.description}[/progress.description]"),
            console=console,
        )
        self.progress.__enter__()
        return self.progress

    def __exit__(self, *args):
        self.progress.__exit__(*args)


def create_progress_bar(
    total: int,
    description: str = "Processing",
) -> None:
    """Create a progress bar for iterations"""
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ).add_task(description, total=total)


# ============================================================================
# ERROR HANDLING
# ============================================================================

class CLIError(Exception):
    """Base exception for CLI errors"""
    pass


class AudioFileError(CLIError):
    """Error loading or processing audio file"""
    pass


class AnalysisError(CLIError):
    """Error during audio analysis"""
    pass


class ProcessingError(CLIError):
    """Error during audio processing"""
    pass


def handle_error(error: Exception, context: str = "") -> None:
    """Handle and display error"""
    error_msg = f"{error}"
    if context:
        console.print(f"[bold red]❌ Error in {context}:[/bold red] {error_msg}")
    else:
        console.print(f"[bold red]❌ Error:[/bold red] {error_msg}")
    console.print("[dim]Use --help for command usage[/dim]")


# ============================================================================
# DECORATORS
# ============================================================================

T = TypeVar('T')


def async_command(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle async commands"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper for async command execution"""
        if asyncio.iscoroutinefunction(func):
            return asyncio.run(func(*args, **kwargs))
        return func(*args, **kwargs)
    return wrapper


def with_error_handling(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to add error handling to commands"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper with error handling"""
        try:
            return func(*args, **kwargs)
        except CLIError as e:
            handle_error(e)
            raise typer.Exit(code=1)
        except Exception as e:
            handle_error(e)
            raise typer.Exit(code=1)
    return wrapper


def with_progress(description: str = "Processing"):
    """Decorator to show progress spinner"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator wrapper"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper with progress tracking"""
            with ProgressTracker(description):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# AUDIO ENGINE INTEGRATION
# ============================================================================

async def get_audio_engine():
    """Get or create AudioEngine instance"""
    from src.samplemind.core.engine.audio_engine import AudioEngine
    return AudioEngine()


async def get_ai_manager():
    """Get or create AIManager instance"""
    from src.samplemind.integrations.ai_manager import SampleMindAIManager
    return SampleMindAIManager()


async def analyze_file_async(
    file_path: Path,
    analysis_level: str = "STANDARD",
) -> Dict[str, Any]:
    """Analyze a single file asynchronously"""
    try:
        if not file_path.exists():
            raise AudioFileError(f"File not found: {file_path}")

        engine = await get_audio_engine()

        # Get analysis level enum
        from src.samplemind.core.engine.audio_engine import AnalysisLevel
        level = getattr(AnalysisLevel, analysis_level.upper(), AnalysisLevel.STANDARD)

        # Run analysis
        features = engine.analyze_audio(file_path, analysis_level=level)

        return {
            "file": str(file_path),
            "duration": features.duration,
            "tempo": features.tempo,
            "key": features.key,
            "mode": features.mode,
            "features": asdict(features) if hasattr(features, '__dict__') else features
        }

    except Exception as e:
        raise AnalysisError(f"Analysis failed: {e}")


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def get_audio_files(directory: Path) -> List[Path]:
    """Get all audio files in directory"""
    supported_formats = {'.wav', '.mp3', '.flac', '.aiff', '.m4a', '.ogg'}

    files = []
    for file in directory.rglob("*"):
        if file.is_file() and file.suffix.lower() in supported_formats:
            files.append(file)

    return sorted(files)


def validate_audio_file(file_path: Path) -> bool:
    """Validate audio file exists and is readable"""
    return file_path.exists() and file_path.is_file()


# ============================================================================
# FORMATTING UTILITIES
# ============================================================================

def format_duration(seconds: float) -> str:
    """Format duration in seconds to MM:SS"""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def format_bpm(bpm: float) -> str:
    """Format BPM value"""
    return f"{bpm:.1f}"


def format_key(key: str, mode: str = "") -> str:
    """Format key with mode"""
    if mode:
        return f"{key} {mode}"
    return key


def format_frequency(hz: float) -> str:
    """Format frequency value"""
    if hz >= 1000:
        return f"{hz/1000:.1f}kHz"
    return f"{hz:.1f}Hz"


# ============================================================================
# BATCH PROCESSING
# ============================================================================

async def batch_analyze_files(
    files: List[Path],
    analysis_level: str = "STANDARD",
    max_workers: int = 4,
    show_progress: bool = True,
) -> List[Dict[str, Any]]:
    """Analyze multiple files concurrently"""
    import concurrent.futures

    results = []

    if show_progress:
        task_id = create_progress_bar(len(files), "Analyzing files")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(analyze_file_async, file, analysis_level)
            for file in files
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = asyncio.run(future.result())
                results.append(result)
                if show_progress:
                    console.print(f"✓ {future.result()['file']}")
            except Exception as e:
                handle_error(e)

    return results


# ============================================================================
# VALIDATION
# ============================================================================

def validate_output_format(format: str) -> bool:
    """Validate output format"""
    valid_formats = {"json", "csv", "yaml", "table"}
    return format.lower() in valid_formats


def validate_bpm_range(bpm_min: float, bpm_max: float) -> bool:
    """Validate BPM range"""
    return 0 < bpm_min <= bpm_max <= 300


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "console",
    "format_json",
    "format_csv",
    "format_table",
    "format_yaml",
    "output_result",
    "ProgressTracker",
    "create_progress_bar",
    "CLIError",
    "AudioFileError",
    "AnalysisError",
    "ProcessingError",
    "handle_error",
    "async_command",
    "with_error_handling",
    "with_progress",
    "get_audio_engine",
    "get_ai_manager",
    "analyze_file_async",
    "get_audio_files",
    "validate_audio_file",
    "format_duration",
    "format_bpm",
    "format_key",
    "format_frequency",
    "batch_analyze_files",
    "validate_output_format",
    "validate_bpm_range",
]
