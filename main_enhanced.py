#!/usr/bin/env python3
"""
SampleMind AI v6 - Enhanced Main Entry Point
Professional AI-powered music production suite with improved error handling

Version: 2.1.0-beta (Enhanced)
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional, NoReturn

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


class SampleMindCLIError(Exception):
    """Base exception for CLI errors"""
    pass


class SetupError(SampleMindCLIError):
    """Raised when setup fails"""
    pass


class AnalysisError(SampleMindCLIError):
    """Raised when analysis fails"""
    pass


def display_banner() -> None:
    """Display SampleMind AI banner"""
    banner = Text()
    banner.append("🎵 ", style="bold cyan")
    banner.append("SampleMind AI v6", style="bold white")
    banner.append(" - Professional Music Production Suite\n", style="bold cyan")
    banner.append("Version: 2.1.0-beta | Status: Beta | Codename: Phoenix", style="dim")
    
    console.print(Panel(banner, border_style="cyan", padding=(1, 2)))


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments with comprehensive help.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="🎵 SampleMind AI v6 - Professional Music Production Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Start interactive menu
  python main.py analyze song.wav         # Analyze single file
  python main.py batch ./music_folder     # Process directory
  python main.py --setup-openai          # Setup OpenAI API
  python main.py --setup-google          # Setup Google AI API
  python main.py --version               # Show version info

For more information, visit: https://docs.samplemind.ai
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["analyze", "batch", "scan", "status", "info"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        help="File or directory path"
    )
    
    parser.add_argument(
        "--setup-openai",
        action="store_true",
        help="Run OpenAI API setup wizard"
    )
    
    parser.add_argument(
        "--setup-google",
        action="store_true",
        help="Run Google AI API setup wizard"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="SampleMind AI v6.0.0-beta (Phoenix)"
    )
    
    return parser.parse_args()


async def quick_analyze(file_path: str, verbose: bool = False) -> None:
    """
    Quick file analysis without interactive menu.
    
    Args:
        file_path: Path to audio file
        verbose: Enable verbose output
        
    Raises:
        AnalysisError: If analysis fails
        FileNotFoundError: If file doesn't exist
    """
    from src.samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
    from src.samplemind.core.loader import AdvancedAudioLoader, LoadingStrategy
    from src.samplemind.integrations.ai_manager import SampleMindAIManager, AnalysisType
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    
    file_path = Path(file_path)
    
    # Validate file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Validate file is readable
    if not file_path.is_file():
        raise AnalysisError(f"Path is not a file: {file_path}")
    
    try:
        console.print(f"\n[bold blue]🎵 Analyzing: {file_path.name}[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
            transient=True
        ) as progress:
            
            # Initialize components
            task1 = progress.add_task("Initializing audio engine...", total=None)
            audio_engine = AudioEngine()
            audio_loader = AdvancedAudioLoader()
            ai_manager = SampleMindAIManager()
            progress.update(task1, completed=True)
            
            # Load audio
            task2 = progress.add_task("Loading audio file...", total=None)
            loaded_audio = audio_loader.load_audio(
                file_path,
                strategy=LoadingStrategy.MEMORY_EFFICIENT
            )
            progress.update(task2, completed=True)
            
            # Extract features
            task3 = progress.add_task("Extracting audio features...", total=None)
            features = audio_engine.analyze_audio(
                file_path,
                level=AnalysisLevel.COMPREHENSIVE
            )
            progress.update(task3, completed=True)
            
            # AI analysis
            task4 = progress.add_task("Running AI analysis...", total=None)
            ai_result = await ai_manager.analyze_music(
                features.to_dict(),
                AnalysisType.COMPREHENSIVE_ANALYSIS
            )
            progress.update(task4, completed=True)
        
        # Display results in a beautiful table
        console.print(f"\n[bold green]✅ Analysis Complete[/bold green]\n")
        
        # Basic info table
        info_table = Table(title="Audio Information", show_header=False, border_style="cyan")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("File", file_path.name)
        info_table.add_row("Duration", f"{loaded_audio.get_duration_seconds():.2f}s")
        info_table.add_row("Sample Rate", f"{loaded_audio.sample_rate} Hz")
        info_table.add_row("Channels", str(loaded_audio.channels))
        info_table.add_row("Tempo", f"{features.tempo:.1f} BPM")
        info_table.add_row("Key", f"{features.key} {features.mode}")
        info_table.add_row("AI Provider", ai_result.provider.value)
        
        console.print(info_table)
        
        # AI Summary
        console.print(f"\n[bold blue]🤖 AI Analysis Summary:[/bold blue]")
        console.print(Panel(ai_result.summary, border_style="blue", padding=(1, 2)))
        
        if verbose and hasattr(ai_result, 'detailed_analysis'):
            console.print(f"\n[bold yellow]📊 Detailed Analysis:[/bold yellow]")
            console.print(ai_result.detailed_analysis)
        
    except FileNotFoundError:
        raise
    except Exception as e:
        raise AnalysisError(f"Analysis failed: {str(e)}") from e


def run_setup_script(script_name: str) -> None:
    """
    Run setup script with error handling.
    
    Args:
        script_name: Name of setup script to run
        
    Raises:
        SetupError: If setup fails
    """
    import subprocess
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        raise SetupError(f"Setup script not found: {script_path}")
    
    try:
        console.print(f"[bold blue]🚀 Running {script_name}...[/bold blue]")
        result = subprocess.run(
            ["bash", str(script_path)],
            check=True,
            capture_output=True,
            text=True
        )
        console.print(f"[bold green]✅ Setup completed successfully[/bold green]")
        if result.stdout:
            console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        raise SetupError(f"Setup failed: {e.stderr}") from e
    except Exception as e:
        raise SetupError(f"Unexpected error during setup: {str(e)}") from e


async def main() -> None:
    """
    Main entry point with comprehensive error handling.
    
    Raises:
        SystemExit: On fatal errors
    """
    try:
        args = parse_args()
        
        # Display banner
        display_banner()
        
        # Configure logging based on verbosity
        if args.debug:
            import logging
            logging.basicConfig(level=logging.DEBUG)
        elif args.verbose:
            import logging
            logging.basicConfig(level=logging.INFO)
        
        # Handle setup commands
        if args.setup_openai:
            run_setup_script("setup_openai_api.sh")
            return
        
        if args.setup_google:
            run_setup_script("setup_google_ai_api.sh")
            return
        
        # Handle quick commands
        if args.command == "analyze" and args.path:
            await quick_analyze(args.path, verbose=args.verbose)
            return
        
        if args.command == "info":
            from src.samplemind import get_info
            info = get_info()
            console.print(Panel.fit(
                f"[cyan]Name:[/cyan] {info['name']}\n"
                f"[cyan]Version:[/cyan] {info['version']}\n"
                f"[cyan]Description:[/cyan] {info['description']}\n"
                f"[cyan]Author:[/cyan] {info['author']}",
                title="SampleMind AI Information",
                border_style="cyan"
            ))
            return
        
        # For other commands or no command, start interactive CLI
        from src.samplemind.interfaces.cli.menu import main as cli_main
        await cli_main()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(0)
    except FileNotFoundError as e:
        console.print(f"[bold red]❌ File Error:[/bold red] {e}")
        sys.exit(1)
    except (AnalysisError, SetupError) as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Unexpected Error:[/bold red] {e}")
        if args.debug if 'args' in locals() else False:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
