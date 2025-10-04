# 🔥 SampleMind AI Beta v2.0 Phoenix - Phase 1 Implementation Guide

**Project Codename:** Phoenix (Rising from v6)  
**Version:** Beta v2.0  
**Phase:** 1 - Foundation Enhancement  
**Duration:** 8 weeks (Sprints 1-4)  
**Status:** 🚀 READY TO BEGIN  
**Last Updated:** 2025-10-04  

---

## 🎯 Phase 1 Overview

Transform SampleMind AI v6 into **Beta v2.0 Phoenix** - a high-performance, intelligent music production platform with:

- ✨ **200+ CLI commands** (Phase 1: 60+ commands)
- 🧠 **Hermès CNN** - Local AI classifier (offline capability)
- 🏷️ **Auto-tagging system** - Genre, mood, instrument, energy
- 🎵 **Essentia integration** - Advanced audio analysis
- 📂 **Smart organization** - Automated file management
- ⚡ **Performance optimization** - Multi-level caching, parallel processing
- 🧪 **Comprehensive testing** - 90%+ coverage

### Success Metrics
- ✅ 60+ working CLI commands
- ✅ Hermès CNN with 78%+ accuracy
- ✅ 10x faster cached analysis
- ✅ 4x faster batch processing
- ✅ 90%+ test coverage
- ✅ Complete documentation

---

## 📋 Table of Contents

1. [Phase 1 Setup: Rebranding](#phase-1-setup)
2. [Sprint 1-2: CLI Foundation (Weeks 1-4)](#sprint-1-2)
3. [Sprint 3: Local AI Integration (Weeks 5-6)](#sprint-3)
4. [Sprint 4: Auto-Tagging & Enhancement (Weeks 7-8)](#sprint-4)
5. [Testing & Quality Assurance](#testing)
6. [Deployment & Launch](#deployment)

---

## 🚀 Phase 1 Setup: Project Rebranding

### Step 1.1: Update Version Information

**Files to Update:**
```bash
# Core files
README.md
pyproject.toml (or setup.py)
package.json (if exists)
src/samplemind/__init__.py

# Documentation
docs/PROJECT_SUMMARY.md
docs/CURRENT_STATUS.md
docs/PROJECT_ROADMAP.md
```

**Changes to Make:**

```python
# src/samplemind/__init__.py
"""
SampleMind AI Beta v2.0 Phoenix
================================
AI-Powered Music Production Platform

Version: Beta 2.0 (Phoenix)
Codename: Phoenix - Rising from the ashes of v6
"""

__version__ = "2.0.0-beta"
__codename__ = "Phoenix"
__status__ = "Beta"
__release_date__ = "2025-10-04"
```

```toml
# pyproject.toml
[tool.poetry]
name = "samplemind-ai-phoenix"
version = "2.0.0-beta"
description = "SampleMind AI Beta v2.0 Phoenix - AI-Powered Music Production Platform"
authors = ["Lars Christian Tangen <lchtangen@gmail.com>"]
```

### Step 1.2: Create Phoenix Changelog

```bash
touch docs/PHOENIX_CHANGELOG.md
```

Content:
```markdown
# 🔥 Phoenix Changelog - Beta v2.0

## Evolution: v6 → Phoenix

### Why Phoenix?
Phoenix represents a complete rebirth of SampleMind AI, combining the best 
features from all previous versions (v1-v5) with cutting-edge innovations.

### Major Changes

#### New in Phoenix Beta v2.0
- 🆕 200+ CLI commands (Phase 1: 60+)
- 🆕 Hermès CNN - Local AI classifier
- 🆕 Advanced auto-tagging system
- 🆕 Essentia audio analysis integration
- 🆕 Smart file organization
- 🆕 Multi-level caching system
- 🆕 Optimized batch processing
- 🆕 Comprehensive testing (90%+ coverage)

#### Improvements from v6
- ⚡ 10x faster analysis (with caching)
- ⚡ 4x faster batch processing
- 🧠 Offline AI capability (Hermès)
- 📊 50+ new audio features (Essentia)
- 🎯 Better accuracy (key, BPM, mood detection)
- 🛠️ Professional CLI tools

#### Breaking Changes
- CLI interface completely redesigned (new command structure)
- API endpoints updated for better performance
- Configuration format changed (migration guide provided)

### Migration from v6
See: [V6_TO_PHOENIX_MIGRATION.md](V6_TO_PHOENIX_MIGRATION.md)
```

### Step 1.3: Update README.md

Update the main README with Phoenix branding:

```markdown
# 🔥 SampleMind AI Beta v2.0 Phoenix

> **The Ultimate AI-Powered Music Production Platform**
> Advanced audio analysis, intelligent organization, and creative assistance.

[![Version](https://img.shields.io/badge/version-2.0.0--beta-orange.svg)](https://github.com/lchtangen/samplemind-ai-phoenix)
[![Status](https://img.shields.io/badge/status-Beta-yellow.svg)](https://github.com/lchtangen/samplemind-ai-phoenix)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Codename:** Phoenix 🔥 - Rising from the ashes of v6  
**Phase:** 1 - Foundation Enhancement  
**Progress:** ⬛⬛⬛⬜⬜⬜⬜⬜⬜⬜ 30%

---

## 🔥 What's New in Phoenix?

### Phase 1 Features (Current)
- ✨ **60+ CLI Commands** - Professional command-line tools
- 🧠 **Hermès CNN** - Local AI classifier (offline capability)
- 🏷️ **Auto-Tagging** - Genre, mood, instrument, energy detection
- 🎵 **Essentia Integration** - Advanced audio analysis
- ⚡ **10x Faster** - Multi-level caching system
- 📂 **Smart Organization** - Automated file management

### Coming Soon (Phase 2-6)
- 🎹 **DAW Plugins** - FL Studio, Ableton, Logic Pro integration
- 🎙️ **Voice Control** - Natural language sample browsing
- 📱 **Mobile Apps** - iOS/Android companion apps
- 🔌 **Plugin Marketplace** - Community extensions
- 🎨 **AI Generation** - Text-to-audio sample creation
- 🎚️ **Stem Separation** - Spleeter & Demucs integration

[Rest of README content...]
```

---

## 🏗️ Sprint 1-2: CLI Foundation (Weeks 1-4)

### Week 1-2: Core CLI Infrastructure

#### Step 2.1: Install Required Libraries

```bash
# Activate virtual environment
source .venv/bin/activate

# Install CLI libraries
pip install rich==13.7.0
pip install typer==0.9.0
pip install click==8.1.7

# Update requirements
pip freeze > requirements.txt
```

#### Step 2.2: Create CLI Directory Structure

```bash
# Create command structure
mkdir -p src/samplemind/cli/commands
mkdir -p src/samplemind/cli/utils
mkdir -p src/samplemind/cli/templates

# Create command modules
touch src/samplemind/cli/commands/__init__.py
touch src/samplemind/cli/commands/import_cmd.py
touch src/samplemind/cli/commands/tag_cmd.py
touch src/samplemind/cli/commands/analyze_cmd.py
touch src/samplemind/cli/commands/organize_cmd.py
touch src/samplemind/cli/commands/config_cmd.py

# Create utils
touch src/samplemind/cli/utils/__init__.py
touch src/samplemind/cli/utils/console.py
touch src/samplemind/cli/utils/formatters.py
touch src/samplemind/cli/utils/validators.py
```

#### Step 2.3: Implement Base CLI Framework

Create `src/samplemind/cli/main.py`:

```python
#!/usr/bin/env python3
"""
SampleMind AI Beta v2.0 Phoenix - CLI Entry Point
Main command-line interface for SampleMind AI
"""

import typer
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

from samplemind.cli.commands import import_cmd, tag_cmd, analyze_cmd
from samplemind.cli.commands import organize_cmd, config_cmd

# Initialize CLI app
app = typer.Typer(
    name="samplemind",
    help="🔥 SampleMind AI Beta v2.0 Phoenix - AI-Powered Music Production",
    add_completion=True,
    rich_markup_mode="rich"
)

# Initialize console
console = Console()

# Add subcommands
app.add_typer(import_cmd.app, name="import", help="📥 Import audio files")
app.add_typer(tag_cmd.app, name="tag", help="🏷️  Tag management")
app.add_typer(analyze_cmd.app, name="analyze", help="🎵 Audio analysis")
app.add_typer(organize_cmd.app, name="organize", help="📂 File organization")
app.add_typer(config_cmd.app, name="config", help="⚙️  Configuration")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    """
    🔥 SampleMind AI Beta v2.0 Phoenix
    
    AI-Powered Music Production Platform
    """
    
    if version:
        from samplemind import __version__, __codename__
        console.print(Panel(
            f"[bold cyan]SampleMind AI[/bold cyan]\n"
            f"Version: [bold]{__version__}[/bold]\n"
            f"Codename: [bold orange1]{__codename__} 🔥[/bold orange1]\n"
            f"Status: [yellow]Beta[/yellow]",
            title="🔥 Phoenix",
            border_style="cyan"
        ))
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold cyan]Welcome to SampleMind AI Phoenix! 🔥[/bold cyan]\n\n"
            "Get started with:\n"
            "  [bold]sm analyze track.wav[/bold]     - Analyze audio file\n"
            "  [bold]sm import /samples[/bold]        - Import sample library\n"
            "  [bold]sm tag --auto sample.wav[/bold]  - Auto-tag with AI\n"
            "  [bold]sm organize[/bold]               - Organize your library\n\n"
            "Run [bold]sm --help[/bold] for all commands",
            title="🎵 SampleMind AI",
            border_style="cyan"
        ))


def cli_entry():
    """Entry point for console script"""
    app()


if __name__ == "__main__":
    cli_entry()
```

#### Step 2.4: Create 'sm' Entry Point

Update `pyproject.toml` or `setup.py`:

```toml
[tool.poetry.scripts]
sm = "samplemind.cli.main:cli_entry"
samplemind = "samplemind.cli.main:cli_entry"
```

Or in `setup.py`:
```python
setup(
    name="samplemind-ai-phoenix",
    version="2.0.0-beta",
    entry_points={
        'console_scripts': [
            'sm=samplemind.cli.main:cli_entry',
            'samplemind=samplemind.cli.main:cli_entry',
        ],
    },
)
```

Install in development mode:
```bash
pip install -e .
```

#### Step 2.5: Implement Import Commands

Create `src/samplemind/cli/commands/import_cmd.py`:

```python
"""Import commands for SampleMind AI Phoenix"""

import typer
from rich.console import Console
from rich.progress import track
from rich.table import Table
from pathlib import Path
from typing import Optional, List
import asyncio

from samplemind.core.engine import AudioEngine
from samplemind.integrations import SampleMindAIManager
from samplemind.core.database.repositories import AudioRepository

app = typer.Typer(help="📥 Import and process audio files")
console = Console()


@app.command()
def file(
    path: Path = typer.Argument(..., help="Audio file path"),
    analyze: bool = typer.Option(True, help="Analyze on import"),
    auto_tag: bool = typer.Option(False, help="Auto-tag with AI"),
    organize: bool = typer.Option(False, help="Auto-organize after import"),
    verbose: bool = typer.Option(False, "-v", "--verbose")
):
    """
    Import a single audio file
    
    Examples:
        sm import file track.wav
        sm import file sample.mp3 --auto-tag
        sm import file loop.wav --analyze --organize
    """
    
    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Importing:[/cyan] {path.name}")
    
    # Import file
    with console.status("[bold green]Importing file..."):
        # Add to database
        audio_repo = AudioRepository()
        audio_file = audio_repo.create(
            file_path=str(path),
            filename=path.name,
            file_size=path.stat().st_size
        )
    
    console.print(f"[green]✓ Imported:[/green] {path.name}")
    
    # Analyze if requested
    if analyze:
        console.print("[cyan]Analyzing audio...[/cyan]")
        engine = AudioEngine()
        
        with console.status("[bold green]Analyzing..."):
            result = engine.analyze_audio(str(path), level="detailed")
        
        # Display results
        table = Table(title="Analysis Results")
        table.add_column("Feature", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("BPM", f"{result.bpm:.2f}")
        table.add_row("Key", result.key or "Unknown")
        table.add_row("Duration", f"{result.duration:.2f}s")
        table.add_row("Sample Rate", f"{result.sample_rate} Hz")
        
        console.print(table)
    
    # Auto-tag if requested
    if auto_tag:
        console.print("[cyan]Auto-tagging...[/cyan]")
        # Will be implemented in Phase 1.5
        console.print("[yellow]Auto-tagging coming soon in Phase 1.5![/yellow]")
    
    # Organize if requested
    if organize:
        console.print("[cyan]Organizing...[/cyan]")
        # Will be implemented in Phase 1.7
        console.print("[yellow]Organization coming soon in Phase 1.7![/yellow]")
    
    console.print("[bold green]✓ Import complete![/bold green]")


@app.command()
def folder(
    path: Path = typer.Argument(..., help="Folder path"),
    pattern: str = typer.Option("*.*", help="File pattern (e.g., *.wav, *.mp3)"),
    recursive: bool = typer.Option(True, help="Recursive search"),
    analyze: bool = typer.Option(True, help="Analyze all files"),
    auto_tag: bool = typer.Option(False, help="Auto-tag with AI"),
    workers: int = typer.Option(4, help="Number of parallel workers")
):
    """
    Import entire folder of audio files
    
    Examples:
        sm import folder /samples
        sm import folder /loops --pattern "*.wav"
        sm import folder /drums --auto-tag --workers 8
    """
    
    if not path.exists():
        console.print(f"[red]Error:[/red] Folder not found: {path}")
        raise typer.Exit(1)
    
    # Find files
    if recursive:
        files = list(path.rglob(pattern))
    else:
        files = list(path.glob(pattern))
    
    # Filter audio files
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.aiff', '.m4a'}
    audio_files = [f for f in files if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        console.print(f"[yellow]No audio files found matching pattern:[/yellow] {pattern}")
        raise typer.Exit(0)
    
    console.print(f"[cyan]Found {len(audio_files)} audio files[/cyan]")
    console.print(f"[cyan]Using {workers} workers[/cyan]\n")
    
    # Import files with progress bar
    imported = 0
    errors = []
    
    for file in track(audio_files, description="Importing..."):
        try:
            # Import logic here
            # Will be fully implemented with multiprocessing
            imported += 1
        except Exception as e:
            errors.append((file.name, str(e)))
    
    # Summary
    console.print(f"\n[bold green]✓ Imported {imported} files[/bold green]")
    
    if errors:
        console.print(f"[yellow]⚠ {len(errors)} errors:[/yellow]")
        for filename, error in errors[:5]:  # Show first 5 errors
            console.print(f"  [red]×[/red] {filename}: {error}")


@app.command()
def watch(
    path: Path = typer.Argument(..., help="Folder to watch"),
    auto_import: bool = typer.Option(True, help="Auto-import new files"),
    auto_analyze: bool = typer.Option(True, help="Auto-analyze new files"),
    auto_tag: bool = typer.Option(False, help="Auto-tag new files")
):
    """
    Watch folder for new audio files and auto-import
    
    Examples:
        sm import watch /samples
        sm import watch /incoming --auto-tag
    
    Press Ctrl+C to stop watching
    """
    
    if not path.exists():
        console.print(f"[red]Error:[/red] Folder not found: {path}")
        raise typer.Exit(1)
    
    console.print(Panel(
        f"[cyan]Watching:[/cyan] {path}\n"
        f"[cyan]Auto-import:[/cyan] {auto_import}\n"
        f"[cyan]Auto-analyze:[/cyan] {auto_analyze}\n"
        f"[cyan]Auto-tag:[/cyan] {auto_tag}\n\n"
        f"[yellow]Press Ctrl+C to stop[/yellow]",
        title="🔍 File Watcher",
        border_style="cyan"
    ))
    
    try:
        # File watcher implementation
        # Will be implemented with watchdog library in Phase 1.7
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped watching[/yellow]")


if __name__ == "__main__":
    app()
```

### Week 3-4: Tag & Analysis Commands

#### Step 2.6: Implement Tag Commands

Create `src/samplemind/cli/commands/tag_cmd.py`:

```python
"""Tag management commands for SampleMind AI Phoenix"""

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from pathlib import Path
from typing import Optional, List
import json

app = typer.Typer(help="🏷️  Tag management and organization")
console = Console()


@app.command()
def add(
    file: Path = typer.Argument(..., help="Audio file"),
    tags: List[str] = typer.Argument(..., help="Tags to add"),
    category: Optional[str] = typer.Option(None, help="Tag category"),
):
    """
    Add tags to audio file
    
    Examples:
        sm tag add kick.wav kick drum percussive
        sm tag add synth.wav warm pad --category mood
    """
    
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Adding tags to:[/cyan] {file.name}")
    
    for tag in tags:
        # Add tag to database
        console.print(f"  [green]+ {tag}[/green]")
    
    console.print(f"[bold green]✓ Added {len(tags)} tags[/bold green]")


@app.command()
def remove(
    file: Path = typer.Argument(..., help="Audio file"),
    tags: List[str] = typer.Argument(..., help="Tags to remove"),
):
    """
    Remove tags from audio file
    
    Examples:
        sm tag remove kick.wav old-tag
    """
    
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Removing tags from:[/cyan] {file.name}")
    
    for tag in tags:
        console.print(f"  [red]- {tag}[/red]")
    
    console.print(f"[bold green]✓ Removed {len(tags)} tags[/bold green]")


@app.command()
def list(
    file: Optional[Path] = typer.Argument(None, help="Audio file (optional)"),
    category: Optional[str] = typer.Option(None, help="Filter by category"),
    format: str = typer.Option("table", help="Output format: table, json, csv")
):
    """
    List tags for file or all tags in library
    
    Examples:
        sm tag list kick.wav
        sm tag list --category genre
        sm tag list --format json
    """
    
    if file and not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    # Mock data for demonstration
    tags_data = [
        {"tag": "techno", "category": "genre", "count": 150},
        {"tag": "dark", "category": "mood", "count": 89},
        {"tag": "kick", "category": "instrument", "count": 234},
        {"tag": "energetic", "category": "mood", "count": 67},
    ]
    
    if format == "table":
        table = Table(title="Tags")
        table.add_column("Tag", style="cyan")
        table.add_column("Category", style="yellow")
        table.add_column("Count", style="green")
        
        for tag in tags_data:
            table.add_row(tag["tag"], tag["category"], str(tag["count"]))
        
        console.print(table)
    
    elif format == "json":
        console.print_json(data=tags_data)
    
    elif format == "csv":
        console.print("tag,category,count")
        for tag in tags_data:
            console.print(f"{tag['tag']},{tag['category']},{tag['count']}")


@app.command()
def auto(
    file: Path = typer.Argument(..., help="Audio file"),
    model: str = typer.Option("hermès", help="AI model: hermès, gemini, gpt4"),
    confidence: float = typer.Option(0.5, help="Minimum confidence threshold"),
    preview: bool = typer.Option(True, help="Preview tags before applying"),
):
    """
    Auto-tag file using AI
    
    Examples:
        sm tag auto kick.wav
        sm tag auto synth.wav --model gemini
        sm tag auto loop.wav --confidence 0.7 --no-preview
    """
    
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Auto-tagging:[/cyan] {file.name}")
    console.print(f"[cyan]Model:[/cyan] {model}\n")
    
    with console.status("[bold green]Analyzing with AI..."):
        # Will be implemented in Phase 1.5 with Hermès CNN
        pass
    
    # Mock tags for demonstration
    predicted_tags = [
        {"tag": "techno", "category": "genre", "confidence": 0.89},
        {"tag": "dark", "category": "mood", "confidence": 0.76},
        {"tag": "kick", "category": "instrument", "confidence": 0.95},
    ]
    
    # Display preview
    table = Table(title="Predicted Tags")
    table.add_column("Tag", style="cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Confidence", style="green")
    
    for tag in predicted_tags:
        if tag["confidence"] >= confidence:
            table.add_row(
                tag["tag"],
                tag["category"],
                f"{tag['confidence']:.2%}"
            )
    
    console.print(table)
    
    if preview:
        if Confirm.ask("\nApply these tags?"):
            console.print("[bold green]✓ Tags applied![/bold green]")
        else:
            console.print("[yellow]Cancelled[/yellow]")
    else:
        console.print("[bold green]✓ Tags applied automatically![/bold green]")


@app.command()
def batch(
    folder: Path = typer.Argument(..., help="Folder path"),
    pattern: str = typer.Option("*.*", help="File pattern"),
    model: str = typer.Option("hermès", help="AI model"),
    workers: int = typer.Option(4, help="Number of parallel workers"),
):
    """
    Batch auto-tag multiple files
    
    Examples:
        sm tag batch /samples
        sm tag batch /drums --pattern "*.wav" --workers 8
    """
    
    if not folder.exists():
        console.print(f"[red]Error:[/red] Folder not found: {folder}")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Batch tagging folder:[/cyan] {folder}")
    console.print(f"[cyan]Using {workers} workers[/cyan]\n")
    
    # Will be implemented in Phase 1.9 with multiprocessing
    console.print("[yellow]Batch tagging coming in Phase 1.9![/yellow]")


if __name__ == "__main__":
    app()
```

---

## 🧠 Sprint 3: Local AI Integration (Weeks 5-6)

### Hermès CNN Implementation

#### Step 3.1: Design CNN Architecture

Create `src/samplemind/ai/hermes_cnn.py`:

```python
"""
Hermès CNN - Local Audio Classifier
====================================
Offline AI model for genre, mood, instrument classification
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import librosa
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

class HermesCNN(nn.Module):
    """
    Hermès - Convolutional Neural Network for audio classification
    
    Architecture:
    - Input: Mel spectrogram (128x128)
    - 4 Conv blocks (32, 64, 128, 256 filters)
    - BatchNorm + Dropout for regularization
    - Multi-head output (genre, mood, instrument, energy)
    """
    
    def __init__(
        self,
        num_genres: int = 23,
        num_moods: int = 12,
        num_instruments: int = 30,
        num_energy: int = 3,
        dropout: float = 0.3
    ):
        super(HermesCNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = self._conv_block(1, 32, dropout=0.25)
        self.conv2 = self._conv_block(32, 64, dropout=0.25)
        self.conv3 = self._conv_block(64, 128, dropout=dropout)
        self.conv4 = self._conv_block(128, 256, dropout=dropout)
        
        # Fully connected
        self.fc_shared = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 8 * 8, 512),
            nn.ReLU(),
            nn.Dropout(0.5)
        )
        
        # Multi-head outputs
        self.fc_genre = nn.Linear(512, num_genres)
        self.fc_mood = nn.Linear(512, num_moods)
        self.fc_instrument = nn.Linear(512, num_instruments)
        self.fc_energy = nn.Linear(512, num_energy)
    
    def _conv_block(self, in_channels, out_channels, dropout):
        """Create a convolutional block"""
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout(dropout)
        )
    
    def forward(self, x):
        """Forward pass"""
        # Convolutional layers
        x = self.conv1(x)  # -> (batch, 32, 64, 64)
        x = self.conv2(x)  # -> (batch, 64, 32, 32)
        x = self.conv3(x)  # -> (batch, 128, 16, 16)
        x = self.conv4(x)  # -> (batch, 256, 8, 8)
        
        # Shared FC
        x = self.fc_shared(x)  # -> (batch, 512)
        
        # Multi-head outputs
        genre = self.fc_genre(x)
        mood = self.fc_mood(x)
        instrument = self.fc_instrument(x)
        energy = self.fc_energy(x)
        
        return {
            "genre": genre,
            "mood": mood,
            "instrument": instrument,
            "energy": energy
        }


class HermesClassifier:
    """Inference wrapper for Hermès CNN"""
    
    # Label mappings
    GENRE_LABELS = [
        "techno", "house", "dnb", "dubstep", "trance", "ambient",
        "hip-hop", "trap", "edm", "electro", "industrial", "minimal",
        "deep-house", "tech-house", "progressive", "psytrance",
        "hardstyle", "garage", "future-bass", "synthwave", "lo-fi",
        "experimental", "other"
    ]
    
    MOOD_LABELS = [
        "dark", "uplifting", "energetic", "calm", "aggressive",
        "happy", "sad", "mysterious", "epic", "groovy", "hypnotic", "dreamy"
    ]
    
    INSTRUMENT_LABELS = [
        "kick", "snare", "hi-hat", "clap", "percussion",
        "bass", "sub-bass", "synth-lead", "synth-pad", "synth-bass",
        "piano", "guitar", "strings", "brass", "vocal",
        "fx", "noise", "ambience", "loop", "one-shot",
        "riser", "downlifter", "sweep", "impact", "glitch",
        "bell", "pluck", "arp", "chord", "melody"
    ]
    
    ENERGY_LABELS = ["low", "medium", "high"]
    
    def __init__(
        self,
        model_path: str = "models/hermes_v1.0.pt",
        device: str = "cpu"
    ):
        """Initialize classifier"""
        self.device = torch.device(device)
        
        # Load model
        self.model = HermesCNN(
            num_genres=len(self.GENRE_LABELS),
            num_moods=len(self.MOOD_LABELS),
            num_instruments=len(self.INSTRUMENT_LABELS),
            num_energy=len(self.ENERGY_LABELS)
        )
        
        # Load weights if available
        model_path = Path(model_path)
        if model_path.exists():
            self.model.load_state_dict(
                torch.load(model_path, map_location=self.device)
            )
            print(f"✓ Loaded Hermès model from {model_path}")
        else:
            print(f"⚠ Warning: Model not found at {model_path}")
            print("  Using untrained model (will give random results)")
        
        self.model.to(self.device)
        self.model.eval()
    
    def preprocess_audio(self, file_path: str) -> torch.Tensor:
        """Convert audio to mel spectrogram"""
        # Load audio (3 seconds max)
        y, sr = librosa.load(file_path, sr=22050, duration=3.0)
        
        # Generate mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=128,
            n_fft=2048,
            hop_length=512
        )
        
        # Convert to dB scale
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize
        mel_spec_norm = (mel_spec_db - mel_spec_db.mean()) / (mel_spec_db.std() + 1e-8)
        
        # Resize to 128x128
        if mel_spec_norm.shape[1] < 128:
            # Pad if too short
            pad_width = 128 - mel_spec_norm.shape[1]
            mel_spec_norm = np.pad(
                mel_spec_norm,
                ((0, 0), (0, pad_width)),
                mode='constant'
            )
        else:
            # Truncate if too long
            mel_spec_norm = mel_spec_norm[:, :128]
        
        # Convert to tensor (batch_size=1, channels=1, height=128, width=128)
        tensor = torch.from_numpy(mel_spec_norm).float()
        tensor = tensor.unsqueeze(0).unsqueeze(0)
        
        return tensor.to(self.device)
    
    def predict(self, file_path: str, top_k: int = 3) -> Dict:
        """
        Classify audio file
        
        Args:
            file_path: Path to audio file
            top_k: Number of top predictions to return
        
        Returns:
            Dict with predictions for genre, mood, instrument, energy
        """
        # Preprocess
        input_tensor = self.preprocess_audio(file_path)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
        
        results = {}
        
        # Genre (single-label, use softmax)
        genre_probs = F.softmax(outputs["genre"], dim=1).squeeze()
        genre_top_k = torch.topk(genre_probs, k=min(top_k, len(self.GENRE_LABELS)))
        results["genre"] = [
            {
                "label": self.GENRE_LABELS[idx],
                "confidence": prob.item()
            }
            for idx, prob in zip(genre_top_k.indices, genre_top_k.values)
        ]
        
        # Mood (single-label, use softmax)
        mood_probs = F.softmax(outputs["mood"], dim=1).squeeze()
        mood_top_k = torch.topk(mood_probs, k=min(top_k, len(self.MOOD_LABELS)))
        results["mood"] = [
            {
                "label": self.MOOD_LABELS[idx],
                "confidence": prob.item()
            }
            for idx, prob in zip(mood_top_k.indices, mood_top_k.values)
        ]
        
        # Instrument (multi-label, use sigmoid)
        instrument_probs = torch.sigmoid(outputs["instrument"]).squeeze()
        instrument_top_k = torch.topk(
            instrument_probs,
            k=min(top_k, len(self.INSTRUMENT_LABELS))
        )
        results["instrument"] = [
            {
                "label": self.INSTRUMENT_LABELS[idx],
                "confidence": prob.item()
            }
            for idx, prob in zip(instrument_top_k.indices, instrument_top_k.values)
            if prob.item() > 0.3  # Threshold for multi-label
        ]
        
        # Energy (single-label, use softmax)
        energy_probs = F.softmax(outputs["energy"], dim=1).squeeze()
        energy_idx = torch.argmax(energy_probs).item()
        results["energy"] = {
            "label": self.ENERGY_LABELS[energy_idx],
            "confidence": energy_probs[energy_idx].item()
        }
        
        return results


# CLI integration example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hermes_cnn.py <audio_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print("🧠 Hermès CNN - Local Audio Classifier")
    print(f"Analyzing: {file_path}\n")
    
    classifier = HermesClassifier()
    result = classifier.predict(file_path, top_k=3)
    
    print("Genre:")
    for item in result["genre"]:
        print(f"  {item['label']}: {item['confidence']:.2%}")
    
    print("\nMood:")
    for item in result["mood"]:
        print(f"  {item['label']}: {item['confidence']:.2%}")
    
    print("\nInstrument:")
    for item in result["instrument"]:
        print(f"  {item['label']}: {item['confidence']:.2%}")
    
    print(f"\nEnergy: {result['energy']['label']} ({result['energy']['confidence']:.2%})")
```

---

## ✅ Implementation Checklist

### Week 1-2: CLI Foundation
- [ ] Install rich, typer libraries
- [ ] Create CLI directory structure
- [ ] Implement base CLI framework
- [ ] Create 'sm' entry point
- [ ] Implement import commands (3)
- [ ] Implement tag commands (5)
- [ ] Test basic CLI functionality

### Week 3-4: Expand CLI Commands
- [ ] Implement analyze commands (11)
- [ ] Implement organize commands (5)
- [ ] Implement config commands (5)
- [ ] Add shell auto-completion
- [ ] Create CLI documentation
- [ ] Test all 30+ commands

### Week 5-6: Hermès CNN
- [ ] Design CNN architecture
- [ ] Set up PyTorch environment
- [ ] Implement preprocessing pipeline
- [ ] Create training script (optional)
- [ ] Implement inference wrapper
- [ ] Integrate with CLI
- [ ] Benchmark performance
- [ ] Document model usage

### Week 7-8: Auto-Tagging & Enhancement
- [ ] Create auto-tagging module
- [ ] Implement classification pipeline
- [ ] Add API endpoints
- [ ] Integrate Essentia (optional)
- [ ] Implement caching system
- [ ] Optimize batch processing
- [ ] Complete documentation
- [ ] Run full test suite

---

## 🎯 Success Criteria

### Technical
- ✅ 60+ CLI commands working
- ✅ Hermès CNN inference <100ms
- ✅ Cache hit rate >80%
- ✅ Batch processing 4x faster
- ✅ Test coverage >90%
- ✅ Zero critical bugs

### User Experience
- ✅ Intuitive command structure
- ✅ Beautiful terminal UI (rich)
- ✅ Helpful error messages
- ✅ Comprehensive help text
- ✅ Fast response times
- ✅ Progress indicators

### Documentation
- ✅ Complete CLI reference
- ✅ Code examples for all commands
- ✅ Architecture documentation
- ✅ Migration guide from v6
- ✅ Video tutorials (optional)
- ✅ API documentation

---

## 🚀 Next Steps After Phase 1

### Phase 2 (Months 3-4): Advanced Features
- Essentia integration
- Smart file organization
- Pack builder
- Similarity search

### Phase 3 (Months 5-6): Professional Tools
- Stem separation
- Project snapshots
- AI sample generation

### Phase 4 (Months 7-9): DAW Integration
- FL Studio plugin
- VST3/AU plugin
- Ableton integration

---

## 📞 Support & Resources

- **Documentation:** `/docs/V6_FEATURE_INTEGRATION_MASTER_PLAN.md`
- **Issue Tracker:** GitHub Issues
- **Discord:** #samplemind-phoenix
- **Email:** lchtangen@gmail.com

---

**🔥 Phoenix - Rising from the ashes of v6**

**Let's build the ultimate music production platform!** 🎵🚀

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-04  
**Author:** Lars Christian Tangen  
**Status:** Ready for Implementation
