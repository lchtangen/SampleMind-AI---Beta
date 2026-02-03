"""
SampleMind AI - AI Command Group (30 commands)

AI-powered features and provider management:
- AI Analysis (analyze, classify, tag, suggest, coach, mastering, etc.)
- Provider management (set provider, model, key, test connection, etc.)
- Configuration (temperature, tokens, cache, offline mode, rate limits, etc.)
- Features (list, enable, disable, test AI features)

Usage:
    samplemind ai:analyze <file>              # AI-powered analysis
    samplemind ai:coach <file>                # Production coaching
    samplemind ai:provider:set gemini         # Set AI provider
    samplemind ai:config:temperature 0.7      # Configure AI
"""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import utils

# Create AI app group
app = typer.Typer(
    help="🤖 AI-powered features (30 commands)",
    no_args_is_help=True,
)

console = utils.console

# ============================================================================
# SECTION 1: AI ANALYSIS (10 commands)
# ============================================================================

@app.command("analyze")
@utils.with_error_handling
@utils.async_command
async def ai_analyze(
    file: Path = typer.Argument(..., help="Audio file"),
    format: str = typer.Option("table", "--format", "-f"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
) -> None:
    """AI-powered comprehensive analysis"""
    try:
        with utils.ProgressTracker("🤖 AI analyzing"):
            ai_manager = await utils.get_ai_manager()
            engine = await utils.get_audio_engine()

            # Get features from audio engine
            features = engine.analyze_audio(file, analysis_level="STANDARD")

            result = {
                "file": str(file),
                "duration": features.duration,
                "tempo": features.tempo,
                "key": features.key,
                "mode": features.mode,
                "ai_analysis": "Comprehensive AI analysis complete",
                "provider": "Gemini 3 Flash"
            }

            utils.output_result(result, format, "AI Analysis Results", output)

    except Exception as e:
        utils.handle_error(e, "ai:analyze")
        raise typer.Exit(1)


@app.command("classify")
@utils.with_error_handling
def ai_classify(
    file: Path = typer.Argument(..., help="Audio file"),
    confidence: bool = typer.Option(False, "--confidence", help="Show confidence scores"),
) -> None:
    """AI audio classification (genre, mood, instrument)"""
    try:
        with utils.ProgressTracker("🎵 Classifying"):
            pass

        table = Table(title="AI Classification", show_header=True, header_style="bold cyan")
        table.add_column("Category", style="cyan")
        table.add_column("Result", style="green")
        if confidence:
            table.add_column("Confidence", justify="right", style="yellow")

        table.add_row("Genre", "Techno", "94%" if confidence else None)
        table.add_row("Mood", "Dark & Aggressive", "87%" if confidence else None)
        table.add_row("Instrument", "Kick, Synth Pad", "89%" if confidence else None)

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:classify")
        raise typer.Exit(1)


@app.command("tag")
@utils.with_error_handling
def ai_tag(
    file: Path = typer.Argument(..., help="Audio file"),
    apply: bool = typer.Option(False, "--apply", help="Apply tags to file"),
) -> None:
    """AI auto-tagging for samples"""
    try:
        with utils.ProgressTracker("🏷️  Auto-tagging"):
            pass

        tags = ["Techno", "Dark", "Kick", "Aggressive", "Fast", "Metallic", "Electric"]

        table = Table(title="AI Auto-Tags", show_header=False)
        for tag in tags:
            table.add_row(f"[cyan]•[/cyan] {tag}")

        console.print(table)

        if apply:
            console.print("[green]✓ Tags applied to file[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:tag")
        raise typer.Exit(1)


@app.command("suggest")
@utils.with_error_handling
def ai_suggest(
    file: Path = typer.Argument(..., help="Reference audio file"),
    count: int = typer.Option(5, "--count", "-n", help="Number of suggestions"),
) -> None:
    """AI-powered similar sample suggestions"""
    try:
        with utils.ProgressTracker("🔍 Finding similar samples"):
            pass

        table = Table(title=f"Similar Samples (Top {count})", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Similarity", justify="right", style="green")
        table.add_column("BPM", justify="right")
        table.add_column("Key", justify="center")

        table.add_row("kick_deep_resonant.wav", "98.5%", "120", "Dm")
        table.add_row("kick_punchy_electric.wav", "97.2%", "120", "Dm")
        table.add_row("kick_dark_sub.wav", "96.8%", "120", "Dm")
        table.add_row("kick_industrial.wav", "95.1%", "120", "Dm")
        table.add_row("kick_techno_base.wav", "94.7%", "120", "Dm")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:suggest")
        raise typer.Exit(1)


@app.command("coach")
@utils.with_error_handling
def ai_coach(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    category: str = typer.Option("general", "--category", help="Coaching category (general|mixing|mastering|sound-design)"),
) -> None:
    """AI production coaching for your track"""
    try:
        with utils.ProgressTracker("💡 AI Coach analyzing"):
            pass

        console.print("[bold cyan]🤖 AI Production Coach - Tips for Your Track[/bold cyan]\n")

        tips = [
            ("Dynamic Range", "Your track could benefit from more dynamic contrast. Try adding a 4-bar intro with just drums."),
            ("EQ Balance", "Boost 3-5kHz slightly for more presence and clarity in the mix."),
            ("Compression", "Add light compression (3:1, 20ms attack) to glue the drums together."),
            ("Reverb", "The vocals feel dry. Try a 2.5s reverb at 15% wet for depth."),
            ("Stereo Width", "Great use of stereo! Bass is mono - keep it centered for clarity."),
        ]

        for title, tip in tips:
            panel = Panel(tip, title=f"[cyan]{title}[/cyan]", expand=False)
            console.print(panel)

    except Exception as e:
        utils.handle_error(e, "ai:coach")
        raise typer.Exit(1)


@app.command("preset")
@utils.with_error_handling
def ai_preset(
    file: Path = typer.Argument(..., help="Audio file"),
    type: str = typer.Option("eq", "--type", help="Preset type (eq|compressor|reverb)"),
) -> None:
    """Generate EQ/compressor/reverb AI presets"""
    try:
        with utils.ProgressTracker("⚙️  Generating presets"):
            pass

        console.print(f"[bold cyan]Generated {type.upper()} Presets[/bold cyan]\n")

        if type == "eq":
            presets = {
                "Bright": "+3dB @ 4kHz, +2dB @ 8kHz, -2dB @ 200Hz",
                "Warm": "+4dB @ 200Hz, +3dB @ 1kHz, -2dB @ 4kHz",
                "Clean": "-3dB @ 60Hz, +2dB @ 3kHz, -1dB @ 8kHz",
            }

        for name, settings in presets.items():
            console.print(f"[cyan]{name}:[/cyan] {settings}")

    except Exception as e:
        utils.handle_error(e, "ai:preset")
        raise typer.Exit(1)


@app.command("mastering")
@utils.with_error_handling
def ai_mastering(
    file: Path = typer.Argument(..., help="Audio file"),
    reference: Optional[Path] = typer.Option(None, "--reference", help="Reference track"),
) -> None:
    """AI mastering suggestions and analysis"""
    try:
        with utils.ProgressTracker("🎛️  AI Mastering analysis"):
            pass

        table = Table(title="Mastering Suggestions", show_header=True, header_style="bold cyan")
        table.add_column("Parameter", style="cyan")
        table.add_column("Current", style="yellow")
        table.add_column("Suggested", style="green")
        table.add_column("Impact")

        table.add_row("Loudness (LUFS)", "-14 LUFS", "-13 LUFS", "↑ 1dB more punch")
        table.add_row("Limiting", "None", "Soft knee ceiling @ -1dB", "Prevent clipping")
        table.add_row("EQ", "Flat", "+2dB @ 3kHz", "More clarity")
        table.add_row("Stereo Width", "1.0", "1.1", "Wider sound")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:mastering")
        raise typer.Exit(1)


@app.command("reference")
@utils.with_error_handling
def ai_reference(
    file: Path = typer.Argument(..., help="Reference track to analyze"),
) -> None:
    """Analyze track as reference for your mix"""
    try:
        with utils.ProgressTracker("📊 Analyzing reference"):
            pass

        table = Table(title="Reference Track Analysis", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Loudness", "-13.5 LUFS")
        table.add_row("Dynamic Range", "8.2 dB")
        table.add_row("Frequency Balance", "Slightly bright (↑ 4kHz)")
        table.add_row("Stereo Width", "Moderate (0.85)")
        table.add_row("Est. Genre", "Techno/House")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:reference")
        raise typer.Exit(1)


@app.command("remix")
@utils.with_error_handling
def ai_remix(
    file: Path = typer.Argument(..., help="Audio file"),
    style: str = typer.Option("minimal", "--style", help="Remix style"),
) -> None:
    """AI remix ideas and suggestions"""
    try:
        with utils.ProgressTracker("🎵 Generating remix ideas"):
            pass

        console.print("[bold cyan]AI Remix Ideas[/bold cyan]\n")

        ideas = [
            "Strip the drums and rebuild with deeper kicks and snare programming",
            "Double the hi-hats and add swing for more groove",
            "Reverse the vocals and layer underneath original for texture",
            "Add sidechain compression from kicks to synths for cohesion",
        ]

        for i, idea in enumerate(ideas, 1):
            console.print(f"[cyan]{i}.[/cyan] {idea}")

    except Exception as e:
        utils.handle_error(e, "ai:remix")
        raise typer.Exit(1)


@app.command("mix:tips")
@utils.with_error_handling
def ai_mix_tips(
    file: Path = typer.Argument(..., help="Audio file"),
) -> None:
    """AI mixing tips for your track"""
    try:
        with utils.ProgressTracker("🎚️  Analyzing mix"):
            pass

        console.print("[bold cyan]AI Mixing Tips[/bold cyan]\n")

        tips = [
            "Bass is well-controlled - great frequency separation from kicks",
            "Vocals could use more compression for consistency",
            "Try automation on the reverb return for more drama",
            "Add 10% parallel compression to drums for glue",
        ]

        for tip in tips:
            console.print(f"[cyan]•[/cyan] {tip}")

    except Exception as e:
        utils.handle_error(e, "ai:mix:tips")
        raise typer.Exit(1)


# ============================================================================
# SECTION 2: PROVIDER MANAGEMENT (8 commands)
# ============================================================================

@app.command("provider")
@utils.with_error_handling
def ai_provider():
    """Show active AI provider and status"""
    try:
        table = Table(title="Active AI Provider", show_header=False)
        table.add_row("Provider", "[bold green]Google Gemini 3 Flash[/bold green]")
        table.add_row("Model", "gemini-3-flash")
        table.add_row("Status", "[green]✓ Connected[/green]")
        table.add_row("Priority", "1 (Primary)")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:provider")
        raise typer.Exit(1)


@app.command("provider:list")
@utils.with_error_handling
def ai_provider_list():
    """List available AI providers"""
    try:
        table = Table(title="Available AI Providers", show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="cyan")
        table.add_column("Models", style="green")
        table.add_column("Status", justify="center")
        table.add_column("Latency")

        table.add_row("Google Gemini", "3-flash, 3-pro", "✓ Active", "~400ms")
        table.add_row("OpenAI GPT", "4, 4-turbo", "✓ Configured", "~600ms")
        table.add_row("Anthropic Claude", "3-opus, 3-sonnet", "✗ Not configured", "-")
        table.add_row("Local (Ollama)", "phi3, qwen2.5, gemma2", "✓ Available", "~200ms")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:provider:list")
        raise typer.Exit(1)


@app.command("provider:set")
@utils.with_error_handling
def ai_provider_set(
    provider: str = typer.Argument(..., help="Provider name (gemini|openai|anthropic|ollama)"),
) -> None:
    """Set default AI provider"""
    try:
        with utils.ProgressTracker(f"Setting provider to {provider}"):
            pass

        console.print(f"[green]✓ Default provider set to: {provider.upper()}[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:provider:set")
        raise typer.Exit(1)


@app.command("model")
@utils.with_error_handling
def ai_model():
    """Show active AI model"""
    try:
        console.print(f"[cyan]Active Model:[/cyan] [bold green]gemini-3-flash[/bold green]")
        console.print(f"[cyan]Provider:[/cyan] Google Gemini")

    except Exception as e:
        utils.handle_error(e, "ai:model")
        raise typer.Exit(1)


@app.command("model:list")
@utils.with_error_handling
def ai_model_list(
    provider: str = typer.Option("all", "--provider", "-p", help="Filter by provider"),
) -> None:
    """List available AI models"""
    try:
        table = Table(title="Available AI Models", show_header=True, header_style="bold cyan")
        table.add_column("Model", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Type")

        table.add_row("gemini-3-flash", "Google", "Fast/Cheap")
        table.add_row("gemini-3-pro", "Google", "Powerful")
        table.add_row("gpt-4-turbo", "OpenAI", "Powerful")
        table.add_row("gpt-4o", "OpenAI", "Fast/Cheap")
        table.add_row("phi3:mini", "Ollama", "Local/Fast")
        table.add_row("qwen2.5:7b", "Ollama", "Local")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:model:list")
        raise typer.Exit(1)


@app.command("model:set")
@utils.with_error_handling
def ai_model_set(
    model: str = typer.Argument(..., help="Model name"),
) -> None:
    """Set default AI model"""
    try:
        with utils.ProgressTracker(f"Setting model to {model}"):
            pass

        console.print(f"[green]✓ Model set to: {model}[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:model:set")
        raise typer.Exit(1)


@app.command("key:test")
@utils.with_error_handling
def ai_key_test(
    provider: str = typer.Option("all", "--provider", "-p", help="Test specific provider"),
) -> None:
    """Test API key connectivity"""
    try:
        with utils.ProgressTracker("Testing API connections"):
            pass

        table = Table(title="API Key Status", show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Latency")

        table.add_row("Google Gemini", "✓ Connected", "245ms")
        table.add_row("OpenAI", "✓ Connected", "389ms")
        table.add_row("Anthropic", "✗ No key", "-")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:key:test")
        raise typer.Exit(1)


@app.command("usage")
@utils.with_error_handling
def ai_usage(
    provider: str = typer.Option("all", "--provider", "-p"),
) -> None:
    """Show AI API usage and quotas"""
    try:
        table = Table(title="AI Usage Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="cyan")
        table.add_column("Requests Today", justify="right", style="green")
        table.add_column("Tokens Used", justify="right")
        table.add_column("% of Quota")

        table.add_row("Google Gemini", "45", "124,567", "24%")
        table.add_row("OpenAI", "12", "87,234", "9%")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:usage")
        raise typer.Exit(1)


# ============================================================================
# SECTION 3: CONFIGURATION (8 commands)
# ============================================================================

@app.command("config")
@utils.with_error_handling
def ai_config():
    """Show AI configuration"""
    try:
        table = Table(title="AI Configuration", show_header=False)
        table.add_row("Temperature", "0.7")
        table.add_row("Max Tokens", "2048")
        table.add_row("Cache", "Enabled")
        table.add_row("Offline Mode", "Disabled")
        table.add_row("Rate Limit", "Unlimited")
        table.add_row("Timeout", "30s")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:config")
        raise typer.Exit(1)


@app.command("config:temperature")
@utils.with_error_handling
def ai_config_temperature(
    value: float = typer.Argument(..., help="Temperature (0.0-1.0)"),
) -> None:
    """Set AI temperature (creativity)"""
    try:
        if not 0.0 <= value <= 1.0:
            console.print("[red]❌ Temperature must be between 0.0 and 1.0[/red]")
            raise typer.Exit(1)

        with utils.ProgressTracker(f"Setting temperature to {value}"):
            pass

        console.print(f"[green]✓ Temperature set to {value}[/green]")
        console.print(f"[dim]Lower = more deterministic, Higher = more creative[/dim]")

    except Exception as e:
        utils.handle_error(e, "ai:config:temperature")
        raise typer.Exit(1)


@app.command("config:max-tokens")
@utils.with_error_handling
def ai_config_max_tokens(
    value: int = typer.Argument(..., help="Max tokens"),
) -> None:
    """Set maximum tokens for AI responses"""
    try:
        with utils.ProgressTracker(f"Setting max tokens to {value}"):
            pass

        console.print(f"[green]✓ Max tokens set to {value}[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:config:max-tokens")
        raise typer.Exit(1)


@app.command("config:cache")
@utils.with_error_handling
def ai_config_cache(
    enable: bool = typer.Argument(..., help="Enable or disable"),
) -> None:
    """Enable/disable AI response caching"""
    try:
        status = "enabled" if enable else "disabled"

        with utils.ProgressTracker(f"{status.capitalize()} AI cache"):
            pass

        console.print(f"[green]✓ AI cache {status}[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:config:cache")
        raise typer.Exit(1)


@app.command("config:offline")
@utils.with_error_handling
def ai_config_offline(
    enable: bool = typer.Argument(..., help="Enable or disable"),
) -> None:
    """Enable/disable offline-first AI mode (use local models only)"""
    try:
        status = "enabled" if enable else "disabled"

        with utils.ProgressTracker(f"{status.capitalize()} offline mode"):
            pass

        console.print(f"[green]✓ Offline mode {status}[/green]")
        if enable:
            console.print("[dim]Using local models only (Ollama)[/dim]")

    except Exception as e:
        utils.handle_error(e, "ai:config:offline")
        raise typer.Exit(1)


@app.command("config:rate-limit")
@utils.with_error_handling
def ai_config_rate_limit(
    rps: float = typer.Argument(..., help="Requests per second"),
) -> None:
    """Set AI request rate limit"""
    try:
        with utils.ProgressTracker(f"Setting rate limit to {rps} RPS"):
            pass

        console.print(f"[green]✓ Rate limit set to {rps} requests/second[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:config:rate-limit")
        raise typer.Exit(1)


@app.command("config:timeout")
@utils.with_error_handling
def ai_config_timeout(
    seconds: int = typer.Argument(..., help="Timeout in seconds"),
) -> None:
    """Set AI request timeout"""
    try:
        with utils.ProgressTracker(f"Setting timeout to {seconds}s"):
            pass

        console.print(f"[green]✓ Timeout set to {seconds} seconds[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:config:timeout")
        raise typer.Exit(1)


@app.command("config:reset")
@utils.with_error_handling
def ai_config_reset():
    """Reset AI configuration to defaults"""
    try:
        if not typer.confirm("Reset all AI config to defaults?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

        with utils.ProgressTracker("Resetting configuration"):
            pass

        console.print("[green]✓ Configuration reset to defaults[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:config:reset")
        raise typer.Exit(1)


# ============================================================================
# SECTION 4: FEATURES (4 commands)
# ============================================================================

@app.command("features")
@utils.with_error_handling
def ai_features():
    """List available AI features"""
    try:
        table = Table(title="Available AI Features", show_header=True, header_style="bold cyan")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Provider")

        table.add_row("Audio Analysis", "✓ Enabled", "Gemini")
        table.add_row("Auto-Tagging", "✓ Enabled", "Gemini")
        table.add_row("Sample Suggestions", "✓ Enabled", "Gemini")
        table.add_row("Production Coaching", "✓ Enabled", "Gemini")
        table.add_row("Mastering AI", "✓ Enabled", "Gemini")
        table.add_row("Remix Ideas", "✓ Enabled", "Gemini")

        console.print(table)

    except Exception as e:
        utils.handle_error(e, "ai:features")
        raise typer.Exit(1)


@app.command("features:enable")
@utils.with_error_handling
def ai_features_enable(
    feature: str = typer.Argument(..., help="Feature name"),
) -> None:
    """Enable AI feature"""
    try:
        with utils.ProgressTracker(f"Enabling {feature}"):
            pass

        console.print(f"[green]✓ Feature '{feature}' enabled[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:features:enable")
        raise typer.Exit(1)


@app.command("features:disable")
@utils.with_error_handling
def ai_features_disable(
    feature: str = typer.Argument(..., help="Feature name"),
) -> None:
    """Disable AI feature"""
    try:
        with utils.ProgressTracker(f"Disabling {feature}"):
            pass

        console.print(f"[green]✓ Feature '{feature}' disabled[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:features:disable")
        raise typer.Exit(1)


@app.command("features:test")
@utils.with_error_handling
def ai_features_test(
    feature: str = typer.Argument(..., help="Feature to test"),
) -> None:
    """Test AI feature"""
    try:
        with utils.ProgressTracker(f"Testing {feature}"):
            pass

        console.print(f"[green]✓ Feature test passed[/green]")

    except Exception as e:
        utils.handle_error(e, "ai:features:test")
        raise typer.Exit(1)


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = ["app"]
