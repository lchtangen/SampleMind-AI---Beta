# MASTER CLI Development Guide

**Complete Reference for CLI-First Development at SampleMind AI**

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Development Environment](#development-environment)
3. [CLI Architecture](#cli-architecture)
4. [Offline-First Development](#offline-first-development)
5. [AI Integration](#ai-integration)
6. [Audio Processing](#audio-processing)
7. [Performance Optimization](#performance-optimization)
8. [Modern Terminal UI](#modern-terminal-ui)
9. [Cross-Platform Development](#cross-platform-development)
10. [CLI Workflow Patterns](#cli-workflow-patterns)
11. [Testing & Quality](#testing--quality)
12. [Common Patterns](#common-patterns)
13. [Troubleshooting](#troubleshooting)

---

## Philosophy

### Why CLI First?

SampleMind AI prioritizes CLI development because:

1. **Performance** - Direct terminal interaction <100ms latency
2. **Offline-First** - Works without internet using Ollama
3. **Developer Experience** - Instant feedback during development
4. **Cross-Platform** - Single codebase for Linux, macOS, Windows
5. **Future Extensibility** - Web UI, plugins build on CLI foundation
6. **Music Production Workflow** - DAW integrations work best with CLI

### Core Principles

- **CLI is Primary Product** - Not an afterthought or secondary interface
- **Offline Capability** - Every feature works with Ollama models
- **Performance Targets** - <1 second response time for user operations
- **Modern UX** - Rich terminal UI with animations and effects
- **Gemini 3 Flash Primary** - Cloud AI with Ollama fallback

---

## Development Environment

### Setup Checklist

```bash
# 1. Environment Setup
python3 --version        # Verify 3.11+
python3 -m venv .venv   # Create virtual environment
source .venv/bin/activate

# 2. Project Setup
pip install -e .        # Install in development mode
make setup              # or: pip install -r requirements.txt

# 3. Install Ollama Models
make install-models
# Models: phi3:mini, qwen2.5:7b-instruct, gemma2:2b

# 4. Configure Gemini (Optional but recommended)
# Create .env file:
export GOOGLE_AI_API_KEY="your_key"

# 5. Verify Setup
python main.py --help   # Should show CLI interface
```

### Development Tools

```bash
# Code Quality
make quality            # Run all checks
make lint              # Ruff + MyPy
make format            # Black + isort
make security          # Bandit + Safety

# Testing
make test              # Pytest with coverage
pytest tests/ -v       # Verbose test output
pytest tests/ -k test_name  # Single test

# Database Services (optional)
make setup-db          # Start MongoDB, Redis, ChromaDB
```

### Editor Setup

```bash
# VSCode .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

---

## CLI Architecture

### Entry Point Structure

```python
# main.py
import typer
from src.samplemind.interfaces.cli import app

if __name__ == "__main__":
    app()  # Typer-based CLI entry point
```

### Typer Command Structure

```python
# src/samplemind/interfaces/cli/main.py
import typer

app = typer.Typer(
    help="SampleMind AI - CLI-first music production platform"
)

@app.command()
def analyze(
    file: str = typer.Argument(..., help="Audio file path"),
    level: str = typer.Option("STANDARD", help="Analysis level")
):
    """Analyze an audio file"""
    # Implementation
    pass

@app.command()
def recommend(file: str = typer.Argument(...)):
    """Get AI-powered sample recommendations"""
    # Implementation
    pass

@app.command()
def status():
    """Check system status and available AI models"""
    # Implementation
    pass
```

### Command Organization

```
src/samplemind/interfaces/cli/
├── __init__.py
├── main.py              # Entry point
├── commands/
│   ├── analysis.py      # Audio analysis commands
│   ├── recommend.py     # AI recommendation commands
│   ├── library.py       # Sample library commands
│   ├── config.py        # Configuration commands
│   └── utils.py         # Utility commands
└── output/
    ├── formatters.py    # Terminal output formatting
    └── animations.py    # Terminal animations
```

### Loading State Management

For long operations, show meaningful feedback:

```python
from rich.console import Console
from rich.progress import Progress

console = Console()

with Progress() as progress:
    task = progress.add_task("[cyan]Analyzing audio...", total=100)

    # Do work
    for item in items:
        # Process
        progress.update(task, advance=1)
```

---

## Offline-First Development

### Ollama Integration

Ollama provides local AI without internet. Three models for different needs:

**Model Selection:**

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| phi3:mini | 2.2B | <100ms | Fast | Quick analysis, feature extraction |
| gemma2:2b | 2B | 100-200ms | Good | Recommendations, descriptions |
| qwen2.5:7b | 7B | 500ms-1s | Excellent | Complex analysis, strategy |

**Setup:**

```bash
# Install Ollama from ollama.ai
ollama --version

# Pull models
ollama pull phi3:mini
ollama pull gemma2:2b
ollama pull qwen2.5:7b-instruct

# Launch API server
ollama serve  # Runs on localhost:11434
```

### Smart Model Routing

```python
# src/samplemind/ai/model_router.py
class ModelRouter:
    def select_model(self, task_type: str) -> str:
        """Select appropriate model based on task"""
        routing = {
            "quick_analysis": "phi3:mini",
            "recommendation": "gemma2:2b",
            "complex_analysis": "qwen2.5:7b-instruct"
        }
        return routing.get(task_type, "phi3:mini")

    def use_cloud_ai(self) -> bool:
        """Check if should use Gemini instead"""
        return (
            internet_available() and
            task_complexity == "high" and
            gemini_api_key_available()
        )
```

### Fallback Strategy

```python
class AIIntegration:
    async def analyze(self, audio_data):
        # Try offline first (always available)
        try:
            return await ollama.analyze(audio_data)
        except Exception:
            pass

        # Fall back to Gemini if available
        try:
            if self.has_gemini_key():
                return await gemini.analyze(audio_data)
        except Exception:
            pass

        # Return cached result if available
        return cache.get(audio_hash)
```

### Performance Benchmarks

**Target response times with Ollama:**
- Quick analysis (phi3): <100ms
- Feature extraction: <200ms
- Recommendation generation: <500ms
- Complex analysis: <1s

---

## AI Integration

### Gemini 3 Flash Setup

Gemini is the primary cloud AI for complex tasks:

```python
# src/samplemind/ai/gemini_integration.py
import google.generativeai as genai
from typing import Optional

class GeminiAI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_music(self, prompt: str) -> str:
        """Use Gemini for music analysis"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
```

### Prompt Engineering

Effective prompts for music analysis:

```python
MUSIC_ANALYSIS_PROMPT = """
Analyze this audio file and provide:
1. Musical key and scale
2. Estimated tempo (BPM)
3. Primary instruments/sounds
4. Genre classification
5. Mood/energy level
6. Potential use cases

Audio features:
- Tempo: {tempo}
- Key: {key}
- Spectral centroid: {spectral_centroid}
- Zero crossing rate: {zcr}
- MFCC: {mfcc}
"""
```

### Streaming Responses

For long operations, stream responses:

```python
from rich.console import Console

console = Console()

with console.status("[bold green]Analyzing...") as status:
    for chunk in gemini.stream_analyze(audio):
        console.print(chunk, end="", flush=True)
```

---

## Audio Processing

### AudioEngine Integration

```python
# src/samplemind/core/engine/audio_engine.py
from librosa import load
from src.samplemind.core.features import FeatureExtractor

class AudioEngine:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.extractor = FeatureExtractor()

    async def analyze(self, file_path: str, level: str = "STANDARD"):
        """Analyze audio file"""
        audio, sr = load(file_path, sr=None)

        features = {
            "tempo": await self.extract_tempo(audio, sr),
            "key": await self.extract_key(audio, sr),
            "spectral": await self.extract_spectral(audio, sr),
        }

        if level in ["DETAILED", "PROFESSIONAL"]:
            features.update({
                "mfcc": await self.extract_mfcc(audio, sr),
                "chroma": await self.extract_chroma(audio, sr),
            })

        return features
```

### Advanced Classification

```python
# Audio-to-MIDI (basic-pitch)
from basicpitch.inference import predict
def audio_to_midi(file_path: str) -> str:
    """Convert audio to MIDI using basic-pitch"""
    model_output, midi_data, note_events = predict(file_path)
    return midi_data

# Stem Separation (demucs)
from demucs.pretrained import get_model
def separate_stems(file_path: str) -> dict:
    """Separate audio into stems"""
    model = get_model('htdemucs')
    sources = model.separate(file_path)
    return {
        "drums": sources[0],
        "bass": sources[1],
        "other": sources[2],
        "vocals": sources[3]
    }

# Source Separation (spleeter)
from spleeter.separator import Separator
def separate_sources(file_path: str) -> dict:
    """Separate sources with spleeter"""
    separator = Separator('spleeter:2stems')
    prediction = separator.separate(file_path)
    return prediction
```

### Feature Caching

```python
import hashlib
from pathlib import Path

class FeatureCache:
    def __init__(self, cache_dir: str = ".cache/features"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_hash(self, file_path: str) -> str:
        """SHA-256 hash of file for cache key"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def get(self, file_path: str) -> Optional[dict]:
        """Get cached features"""
        file_hash = self._get_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"

        if cache_file.exists():
            return json.load(open(cache_file))
        return None

    def set(self, file_path: str, features: dict):
        """Cache features"""
        file_hash = self._get_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"

        with open(cache_file, 'w') as f:
            json.dump(features, f)
```

---

## Performance Optimization

### Response Time Targets

- **<100ms**: Quick commands (status, help)
- **<500ms**: Audio feature extraction
- **<1 second**: Basic analysis with AI
- **<3 seconds**: Complex analysis with Gemini

### Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Use async for I/O operations
async def analyze_multiple_files(files: list[str]):
    """Analyze multiple files concurrently"""
    tasks = [analyze_file(f) for f in files]
    return await asyncio.gather(*tasks)

# Use ThreadPoolExecutor for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=4)

def extract_features_parallel(files: list[str]) -> list[dict]:
    """Extract features in parallel"""
    loop = asyncio.new_event_loop()
    futures = [
        loop.run_in_executor(executor, extract_features, f)
        for f in files
    ]
    return loop.run_until_complete(asyncio.gather(*futures))
```

### Memory Optimization

```python
# Stream processing for large files
def process_large_audio(file_path: str, chunk_size: int = 65536):
    """Process audio in chunks"""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            process_chunk(chunk)
```

### Profiling

```bash
# Profile CLI performance
python -m cProfile -s cumulative main.py analyze test.wav

# Memory profiling
pip install memory-profiler
python -m memory_profiler main.py analyze test.wav
```

---

## Modern Terminal UI

### Rich Library Usage

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

# Tables
table = Table(title="Analysis Results")
table.add_column("Feature", style="cyan")
table.add_column("Value", style="magenta")
table.add_row("Tempo", "120 BPM")
table.add_row("Key", "C Major")
console.print(table)

# Progress
with Progress() as progress:
    task = progress.add_task("[cyan]Analyzing...", total=100)
    for _ in range(100):
        progress.update(task, advance=1)

# Status with spinner
with console.status("[bold green]Processing..."):
    time.sleep(3)
    console.log("✓ Complete")
```

### Animations

```python
from rich.live import Live
from rich.animation import Animation
import time

# Loading animation
animation = Animation.from_ascii("🎵 Loading", duration=3)

with Live(animation, refresh_per_second=4):
    time.sleep(3)

# Custom spinners
spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
for spinner in spinners:
    console.print(f"{spinner} Processing...")
    time.sleep(0.1)
```

### Color & Styling

```python
# Terminal color output
from rich.style import Style

success = Style(color="green", bold=True)
error = Style(color="red", bold=True)
info = Style(color="cyan")

console.print("✓ Success!", style=success)
console.print("✗ Error!", style=error)
console.print("ℹ Info", style=info)
```

### ASCII Fallback Mode

For terminals without color support:

```python
class TerminalUI:
    def __init__(self):
        self.supports_color = self._check_color_support()
        self.supports_unicode = self._check_unicode_support()

    def format_success(self, text: str) -> str:
        if self.supports_color:
            return f"\033[92m✓\033[0m {text}"  # Green checkmark
        else:
            return f"[OK] {text}"  # ASCII fallback

    def format_spinner(self):
        if self.supports_unicode:
            return ["⠋", "⠙", "⠹", "⠸"]
        else:
            return ["-", "\\", "|", "/"]
```

---

## Cross-Platform Development

### Testing Matrix

Test on all platforms before release:

| Platform | Terminal | Status |
|----------|----------|--------|
| Linux | bash, zsh, fish | Primary dev environment |
| macOS | zsh, iTerm2, Terminal.app | Test Unicode, color |
| Windows | PowerShell, cmd, Windows Terminal | Test encoding |

### Platform-Specific Code

```python
import platform
import sys

def get_venv_activation():
    """Get correct venv activation command"""
    if platform.system() == "Windows":
        return ".venv\\Scripts\\activate.bat"
    else:
        return "source .venv/bin/activate"

def get_config_dir():
    """Platform-specific config directory"""
    home = Path.home()
    if platform.system() == "Windows":
        return home / "AppData" / "Local" / "SampleMind"
    elif platform.system() == "Darwin":  # macOS
        return home / "Library" / "SampleMind"
    else:  # Linux
        return home / ".config" / "samplemind"
```

### Testing Cross-Platform

```bash
# Test in different shells
bash -c "source .venv/bin/activate && python main.py"
zsh -c "source .venv/bin/activate && python main.py"
fish -c "source .venv/bin/activate.fish && python main.py"

# Test with Windows batch
call .venv\Scripts\activate.bat && python main.py
```

---

## CLI Workflow Patterns

### Interactive Commands

```python
import typer

def create_interactive():
    """Interactive workflow"""
    name = typer.prompt("What is your name?")
    action = typer.confirm("Do you want to continue?")

    if action:
        typer.echo(f"Hello {name}!")
```

### Piping Support

```bash
# Enable piping to other commands
python main.py analyze test.wav | grep "tempo"
cat files.txt | xargs -I {} python main.py analyze {}

# JSON output for scripting
python main.py analyze test.wav --output json | jq '.tempo'
```

### Batch Processing

```python
@app.command()
def batch_analyze(
    directory: str = typer.Argument(...),
    pattern: str = typer.Option("*.wav"),
    output: str = typer.Option("results.json")
):
    """Analyze multiple files"""
    from pathlib import Path
    from rich.progress import Progress

    files = list(Path(directory).glob(pattern))
    results = {}

    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Analyzing...",
            total=len(files)
        )
        for file in files:
            results[str(file)] = analyze_file(file)
            progress.update(task, advance=1)

    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
```

---

## Testing & Quality

### Unit Tests

```python
# tests/test_audio_engine.py
import pytest
from src.samplemind.core.engine import AudioEngine

@pytest.fixture
def engine():
    return AudioEngine()

def test_audio_loading(engine, sample_audio):
    audio, sr = engine.load_audio(sample_audio)
    assert audio is not None
    assert sr > 0

@pytest.mark.asyncio
async def test_feature_extraction(engine, sample_audio):
    features = await engine.analyze(sample_audio)
    assert "tempo" in features
    assert "key" in features
```

### Integration Tests

```python
# tests/test_cli_integration.py
from typer.testing import CliRunner
from main import app

runner = CliRunner()

def test_analyze_command(sample_audio):
    result = runner.invoke(app, ["analyze", sample_audio])
    assert result.exit_code == 0
    assert "Tempo" in result.stdout
```

### Coverage Target

```bash
# Run with coverage reporting
make test

# View coverage report
coverage html
open htmlcov/index.html
```

**Target: 80%+ coverage** for Phase 1 completion

---

## Common Patterns

### Error Handling

```python
from rich.console import Console

console = Console()

try:
    result = analyze_audio(file_path)
except FileNotFoundError:
    console.print(f"[red]Error: File not found: {file_path}")
    raise typer.Exit(1)
except Exception as e:
    console.print(f"[red]Unexpected error: {e}")
    console.print(f"[dim]Use --verbose for details")
    raise typer.Exit(1)
```

### Verbose Logging

```python
import logging

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level)

@app.command()
def analyze(
    file: str,
    verbose: bool = typer.Option(False, "--verbose/-q")
):
    setup_logging(verbose)
    analyze_audio(file)
```

### Config Management

```python
from pathlib import Path
import json

class Config:
    def __init__(self, config_dir: Path):
        self.config_file = config_dir / "config.json"
        self.load()

    def load(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=2)
```

---

## Troubleshooting

### Common Issues

**Issue: "command not found: python main.py"**
```bash
# Solution: Ensure venv is activated
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

**Issue: "ModuleNotFoundError"**
```bash
# Solution: Reinstall in development mode
pip install -e .
```

**Issue: Ollama models not available**
```bash
# Solution: Check Ollama service
ollama serve  # Start Ollama
ollama list   # Verify models installed
```

**Issue: CLI response slow**
```bash
# Solution: Profile and optimize
python -m cProfile -s cumulative main.py analyze test.wav
```

---

## Quick Reference

### Development Commands

```bash
# Setup and run
make setup                # Complete setup
python main.py           # Run CLI

# Quality assurance
make quality             # All checks
make test               # Tests
make lint               # Linting
make format             # Code formatting

# Models and services
make install-models     # Ollama models
make setup-db          # Database services
```

### Key Directories

- `main.py` - CLI entry point
- `src/samplemind/interfaces/cli/` - CLI implementation
- `src/samplemind/core/engine/` - Audio processing
- `src/samplemind/ai/` - AI integrations
- `tests/` - Test suite
- `.venv/` - Virtual environment

### Essential Files

- `CLAUDE.md` - This guide (updated)
- `pyproject.toml` - Dependencies
- `.env` - Configuration (create as needed)
- `Makefile` - Development commands

---

**Ready to develop?** Start with `python main.py --help` and explore the CLI! 🎵

