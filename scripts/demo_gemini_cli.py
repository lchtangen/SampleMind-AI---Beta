#!/usr/bin/env python3
"""
SampleMind AI v6 - Gemini-Powered CLI Demo
Complete demonstration of audio classification and analysis with Gemini API
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
from samplemind.core.loader import AdvancedAudioLoader, LoadingStrategy
from samplemind.integrations.ai_manager import SampleMindAIManager, AnalysisType, AIProvider
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

async def demo_audio_classification():
    """Demonstrate Gemini-powered audio classification"""

    console.print("\n[bold blue]🎵 SampleMind AI v6 - Gemini Audio Classification Demo[/bold blue]\n")

    # Initialize components
    console.print("[cyan]Initializing components...[/cyan]")
    audio_engine = AudioEngine(max_workers=4)
    audio_loader = AdvancedAudioLoader()
    ai_manager = SampleMindAIManager()

    # Check AI providers
    provider_status = ai_manager.get_provider_status()

    providers_table = Table(title="🤖 AI Providers")
    providers_table.add_column("Provider", style="cyan")
    providers_table.add_column("Status", style="green")
    providers_table.add_column("Priority", style="yellow")

    for provider, status in provider_status.items():
        status_icon = "✅" if status['enabled'] else "❌"
        providers_table.add_row(
            provider,
            status_icon,
            str(status['priority'])
        )

    console.print(providers_table)

    # Test audio files
    test_files = [
        "test_audio_samples/test_chord_120bpm.wav",
        "test_audio_samples/test_minor_140bpm.wav"
    ]

    for audio_file in test_files:
        if not Path(audio_file).exists():
            console.print(f"[yellow]⚠️ {audio_file} not found, skipping...[/yellow]")
            continue

        console.print(f"\n[bold green]📊 Analyzing: {Path(audio_file).name}[/bold green]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            # Load audio
            task1 = progress.add_task("Loading audio...", total=None)
            loaded_audio = audio_loader.load_audio(Path(audio_file))
            progress.remove_task(task1)

            # Extract features
            task2 = progress.add_task("Extracting audio features...", total=None)
            features = audio_engine.analyze_audio(Path(audio_file), level=AnalysisLevel.DETAILED)
            progress.remove_task(task2)

            # AI Analysis with Gemini (PRIMARY)
            task3 = progress.add_task("🤖 Gemini AI analysis...", total=None)
            ai_result = await ai_manager.analyze_music(
                features.to_dict(),
                AnalysisType.COMPREHENSIVE_ANALYSIS,
                preferred_provider=AIProvider.GOOGLE_AI  # Force Gemini
            )
            progress.remove_task(task3)

        # Display results
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("📁 File", Path(audio_file).name)
        info_table.add_row("⏱️ Duration", f"{loaded_audio.get_duration_seconds():.2f}s")
        info_table.add_row("🎵 Tempo", f"{features.tempo:.1f} BPM")
        info_table.add_row("🎼 Key", f"{features.key} {features.mode}")
        info_table.add_row("🤖 AI Provider", ai_result.provider.value)
        info_table.add_row("⚡ Model", ai_result.model_used)
        info_table.add_row("⏱️ Processing", f"{ai_result.processing_time:.2f}s")

        console.print(Panel(info_table, title="📋 File Information", border_style="blue"))

        # AI Analysis
        console.print(Panel(
            ai_result.summary[:500] + "..." if len(ai_result.summary) > 500 else ai_result.summary,
            title="🤖 Gemini AI Analysis",
            border_style="green"
        ))

        # Production Tips
        if ai_result.production_tips:
            tips_text = "\n".join([f"• {tip}" for tip in ai_result.production_tips[:5]])
            console.print(Panel(tips_text, title="💡 Production Tips", border_style="yellow"))

        # FL Studio Recommendations
        if ai_result.fl_studio_recommendations:
            fl_text = "\n".join([f"• {rec}" for rec in ai_result.fl_studio_recommendations[:5]])
            console.print(Panel(fl_text, title="🎛️ FL Studio Recommendations", border_style="magenta"))

        # Scores
        scores_table = Table(title="🏆 Quality Scores")
        scores_table.add_column("Aspect", style="cyan")
        scores_table.add_column("Score", style="green")

        scores_table.add_row("Creativity", f"{ai_result.creativity_score:.2f}")
        scores_table.add_row("Production Quality", f"{ai_result.production_quality_score:.2f}")
        scores_table.add_row("Commercial Potential", f"{ai_result.commercial_potential_score:.2f}")

        console.print(scores_table)

    # Global stats
    stats = ai_manager.get_global_stats()

    stats_table = Table(title="📈 Session Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")

    stats_table.add_row("Total Requests", str(stats['total_requests']))
    stats_table.add_row("Total Tokens", str(stats['total_tokens']))
    stats_table.add_row("Total Cost", f"${stats['total_cost']:.4f}")
    stats_table.add_row("Providers Used", str(stats['providers_enabled']))

    console.print("\n")
    console.print(stats_table)

    console.print("\n[bold green]✅ Demo Complete! Gemini is powering your audio analysis.[/bold green]")
    console.print("[cyan]Run 'python main.py' to start the full interactive CLI[/cyan]\n")

if __name__ == "__main__":
    asyncio.run(demo_audio_classification())
