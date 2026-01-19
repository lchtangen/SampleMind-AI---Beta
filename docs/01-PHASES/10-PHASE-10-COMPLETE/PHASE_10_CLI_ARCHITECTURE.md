# Phase 10 CLI Expansion - Architecture & Implementation Plan

**Version:** 1.0
**Date:** January 19, 2026
**Status:** Planning Phase
**Target Completion:** 12-16 weeks

---

## Executive Summary

Phase 10 focuses on expanding SampleMind AI from a menu-driven interactive CLI to a comprehensive 200+ command system while maintaining backward compatibility. This document outlines the architecture, implementation strategy, and command specifications.

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 Hybrid CLI Approach (Option C)

**Three Entry Points:**

```
1. TYPER SUBCOMMANDS (New - Primary for scripting/automation)
   └─ samplemind analyze:bpm <file>
   └─ samplemind library:search <query>
   └─ samplemind ai:coach <file>
   └─ (200+ commands organized by namespace)

2. INTERACTIVE MENU (Existing - Maintained for compatibility)
   └─ python main.py (or samplemind --interactive)
   └─ Numeric menu (1-9, A, 0)
   └─ Rich TUI with prompts

3. TEXTUAL TUI (Modern - 13 screens)
   └─ Keyboard-driven interface
   └─ Screen-based navigation
   └─ Real-time visualization
```

### 1.2 File Structure

```
src/samplemind/interfaces/cli/
├── __init__.py
├── menu.py                          # EXISTING: Menu-driven CLI (1,925 lines)
├── typer_app.py                     # NEW: Main Typer app with command groups
│
├── commands/                        # NEW: Command modules directory
│   ├── __init__.py
│   ├── utils.py                     # Shared utilities and decorators
│   ├── analyze.py                   # 40 commands: analyze, analyze:bpm, analyze:key, etc.
│   ├── library.py                   # 50 commands: library:scan, library:search, library:filter, etc.
│   ├── ai.py                        # 30 commands: ai:analyze, ai:coach, ai:classify, etc.
│   ├── metadata.py                  # 30 commands: meta:show, meta:edit, meta:batch, etc.
│   ├── audio.py                     # 25 commands: convert:wav, audio:normalize, stems:separate, etc.
│   ├── visualization.py             # 15 commands: viz:waveform, viz:spectrogram, etc.
│   └── reporting.py                 # 10 commands: report:library, export:json, etc.
│
└── integration/                     # Integration layer with AudioEngine, AIManager
    ├── __init__.py
    ├── audio_engine_adapter.py      # Adapt AudioEngine for CLI
    ├── ai_manager_adapter.py        # Adapt AIManager for CLI
    └── library_adapter.py           # Library operations
```

### 1.3 Integration Flow

```
main.py (entry point)
  ├── Typer CLI Router (NEW)
  │   ├── --interactive flag → Menu system
  │   ├── command args → Typer handler
  │   └── command groups (analyze, library, ai, etc.)
  │
  ├── Menu System (EXISTING)
  │   └── Interactive mode with Rich TUI
  │
  └── TextualTUI (EXISTING)
      └── Modern keyboard-driven interface
```

---

## 2. TYPER COMMAND GROUPS & SPECIFICATIONS

### 2.1 GROUP 1: ANALYZE COMMANDS (40 commands)

**Namespace:** `analyze` / `analyse`
**File:** `src/samplemind/interfaces/cli/commands/analyze.py`
**Purpose:** Audio analysis and feature extraction

#### Core Analysis Commands (9 commands)
```bash
samplemind analyze:full <file>              # Comprehensive analysis (DETAILED level)
samplemind analyze:standard <file>          # Standard analysis (STANDARD level)
samplemind analyze:basic <file>             # Basic analysis (BASIC level)
samplemind analyze:professional <file>      # Professional analysis (PROFESSIONAL level)
samplemind analyze:quick <file>             # Fast analysis
samplemind analyze:bpm <file>               # BPM/tempo only
samplemind analyze:key <file>               # Key detection only
samplemind analyze:mode <file>              # Major/minor mode only
samplemind analyze:compare <file1> <file2>  # Compare two files
```

#### Genre/Mood/Instrument Analysis (9 commands)
```bash
samplemind analyze:genre <file>             # Genre classification
samplemind analyze:mood <file>              # Mood/emotion detection
samplemind analyze:instrument <file>        # Instrument recognition
samplemind analyze:vocal <file>             # Vocal detection
samplemind analyze:quality <file>           # Quality scoring
samplemind analyze:energy <file>            # Energy level
samplemind analyze:dynamics <file>          # Dynamic range
samplemind analyze:loudness <file>          # Loudness (LUFS)
samplemind analyze:compression <file>       # Compression detection
```

#### Advanced Audio Analysis (12 commands)
```bash
samplemind analyze:spectral <file>          # Spectral analysis
samplemind analyze:harmonic <file>          # Harmonic content
samplemind analyze:percussive <file>        # Percussive content
samplemind analyze:mfcc <file>              # MFCC features
samplemind analyze:chroma <file>            # Chroma features
samplemind analyze:onset <file>             # Onset detection
samplemind analyze:beats <file>             # Beat tracking
samplemind analyze:segments <file>          # Segment detection
samplemind analyze:tempogram <file>         # Tempogram
samplemind analyze:chromagram <file>        # Chromagram
samplemind analyze:spectral-flux <file>     # Spectral flux
samplemind analyze:zero-crossing <file>     # Zero-crossing rate
```

#### Batch & Parallel Analysis (10 commands)
```bash
samplemind batch:analyze <folder>           # Batch analyze all files
samplemind batch:classify <folder>          # Batch classification
samplemind batch:tag <folder>               # Batch auto-tagging
samplemind batch:compare <folder>           # Compare all against reference
samplemind batch:export <folder>            # Export all analysis
samplemind batch:report <folder>            # Generate batch report
samplemind parallel:analyze <folder> --workers 8  # Parallel with N workers
samplemind parallel:process <folder>        # Parallel advanced processing
samplemind queue:add <file>                 # Add to analysis queue
samplemind queue:process                    # Process analysis queue
```

---

### 2.2 GROUP 2: LIBRARY COMMANDS (50 commands)

**Namespace:** `library` / `lib`
**File:** `src/samplemind/interfaces/cli/commands/library.py`
**Purpose:** Sample library management and organization

#### Library Management (15 commands)
```bash
samplemind library:organize <folder>        # Auto-organize by metadata
samplemind library:scan <folder>            # Scan and index
samplemind library:import <folder>          # Import with metadata
samplemind library:export <folder>          # Export with metadata
samplemind library:sync                     # Cloud sync
samplemind library:stats                    # Library statistics
samplemind library:size                     # Calculate total size
samplemind library:list                     # List all samples
samplemind library:info <file>              # Show file info
samplemind library:rebuild                  # Rebuild index
samplemind library:verify                   # Verify integrity
samplemind library:backup <destination>     # Backup library
samplemind library:restore <backup-file>    # Restore from backup
samplemind library:update-metadata          # Update all metadata
samplemind library:refresh                  # Refresh library view
```

#### Search & Filter (15 commands)
```bash
samplemind library:search <query>           # Full-text search
samplemind library:find <pattern>           # Regex file search
samplemind library:filter:bpm <range>       # Filter by BPM (e.g., 120-130)
samplemind library:filter:key <key>         # Filter by key
samplemind library:filter:genre <genre>     # Filter by genre
samplemind library:filter:mood <mood>       # Filter by mood
samplemind library:filter:tag <tag>         # Filter by tag
samplemind library:filter:duration <range>  # Filter by duration (e.g., 0:30-2:00)
samplemind library:filter:quality <range>   # Filter by quality score
samplemind library:filter:artist <artist>   # Filter by artist
samplemind library:filter:date <range>      # Filter by upload date
samplemind library:browse:random            # Random sample browser
samplemind library:browse:trending          # Trending samples
samplemind library:browse:new               # Recently added
samplemind library:sort <criteria>          # Sort (bpm, key, name, date, etc.)
```

#### Collections (12 commands)
```bash
samplemind collection:create <name>         # Create collection
samplemind collection:add <id> <collection> # Add sample to collection
samplemind collection:remove <id>           # Remove from collection
samplemind collection:list                  # List all collections
samplemind collection:show <name>           # Show collection contents
samplemind collection:rename <old> <new>    # Rename collection
samplemind collection:delete <name>         # Delete collection
samplemind collection:merge <c1> <c2>       # Merge two collections
samplemind collection:export <name>         # Export collection
samplemind collection:import <file>         # Import collection
samplemind collection:share <name>          # Share collection (cloud)
samplemind collection:bookmark              # Create quick bookmark
```

#### Cleanup & Maintenance (8 commands)
```bash
samplemind library:dedupe                   # Find duplicate files
samplemind library:cleanup                  # Remove broken files
samplemind library:unused                   # Find unused samples
samplemind library:orphans                  # Find files without metadata
samplemind library:fix-permissions          # Fix file permissions
samplemind library:fix-encoding             # Fix metadata encoding
samplemind library:prune <days>             # Remove files older than N days
samplemind library:optimize                 # Optimize library performance
```

---

### 2.3 GROUP 3: AI COMMANDS (30 commands)

**Namespace:** `ai`
**File:** `src/samplemind/interfaces/cli/commands/ai.py`
**Purpose:** AI-powered features and analysis

#### AI Analysis (10 commands)
```bash
samplemind ai:analyze <file>                # AI-powered analysis
samplemind ai:classify <file>               # AI classification
samplemind ai:tag <file>                    # AI auto-tagging
samplemind ai:suggest <file>                # Similar samples
samplemind ai:coach <file>                  # Production coaching
samplemind ai:preset <file>                 # Generate EQ presets
samplemind ai:mastering <file>              # Mastering suggestions
samplemind ai:reference <file>              # Analyze as reference track
samplemind ai:remix:ideas <file>            # Remix ideas
samplemind ai:mix:tips <file>               # Mixing tips
```

#### AI Provider Management (8 commands)
```bash
samplemind ai:provider                      # Show active provider
samplemind ai:provider:list                 # List available providers
samplemind ai:provider:set <provider>       # Set default provider (gemini/openai/ollama)
samplemind ai:model                         # Show active model
samplemind ai:model:list                    # List available models
samplemind ai:model:set <model>             # Set model
samplemind ai:key:test                      # Test API connectivity
samplemind ai:usage                         # Show usage statistics
```

#### AI Configuration (8 commands)
```bash
samplemind ai:config                        # Show AI config
samplemind ai:config:temperature <value>    # Set temperature (0.0-1.0)
samplemind ai:config:max-tokens <value>     # Set max tokens
samplemind ai:config:cache <on|off>         # Enable/disable AI response cache
samplemind ai:config:offline <on|off>       # Enable/disable offline mode
samplemind ai:config:rate-limit <rps>       # Set rate limit
samplemind ai:config:timeout <seconds>      # Set timeout
samplemind ai:config:reset                  # Reset to defaults
```

#### AI Features (4 commands)
```bash
samplemind ai:features                      # List available AI features
samplemind ai:features:enable <feature>     # Enable AI feature
samplemind ai:features:disable <feature>    # Disable AI feature
samplemind ai:features:test <feature>       # Test AI feature
```

---

### 2.4 GROUP 4: METADATA COMMANDS (30 commands)

**Namespace:** `meta` / `metadata`
**File:** `src/samplemind/interfaces/cli/commands/metadata.py`
**Purpose:** Metadata viewing, editing, and batch operations

#### Metadata Viewing (8 commands)
```bash
samplemind meta:show <file>                 # Display all metadata
samplemind meta:show:tags <file>            # Show tags only
samplemind meta:show:analysis <file>        # Show analysis results only
samplemind meta:show:custom <file>          # Show custom metadata
samplemind meta:show:history <file>         # Show edit history
samplemind meta:export <file> [format]      # Export to JSON/YAML/CSV
samplemind meta:diff <file1> <file2>        # Compare metadata
samplemind meta:validate <file>             # Validate metadata integrity
```

#### Metadata Editing (8 commands)
```bash
samplemind meta:edit <file>                 # Interactive metadata editor
samplemind meta:set <file> <key> <value>    # Set single value
samplemind meta:add:tag <file> <tag>        # Add tag
samplemind meta:remove:tag <file> <tag>     # Remove tag
samplemind meta:copy <src> <dst>            # Copy metadata
samplemind meta:clear <file>                # Clear all metadata
samplemind meta:clear:custom <file>         # Clear custom metadata only
samplemind meta:merge <file1> <file2>       # Merge metadata from two files
```

#### Batch Metadata Operations (10 commands)
```bash
samplemind meta:batch:tag <folder>          # Batch tag update
samplemind meta:batch:fix <folder>          # Batch fix metadata
samplemind meta:batch:sync <folder>         # Batch sync from AI
samplemind meta:batch:export <folder>       # Batch export metadata
samplemind meta:batch:import <folder>       # Batch import from files
samplemind meta:batch:clear <folder>        # Batch clear metadata
samplemind meta:batch:validate <folder>     # Batch validate
samplemind meta:batch:standardize <folder>  # Batch standardize format
samplemind meta:batch:dedupe:tags <folder>  # Remove duplicate tags batch
samplemind meta:batch:migrate <folder>      # Migrate metadata format
```

#### Metadata Recovery & Snapshot (4 commands)
```bash
samplemind meta:recover <file>              # Recover lost metadata
samplemind meta:snapshot                    # Create metadata snapshot
samplemind meta:snapshot:list               # List snapshots
samplemind meta:restore <snapshot-id>       # Restore from snapshot
```

---

### 2.5 GROUP 5: AUDIO PROCESSING COMMANDS (25 commands)

**Namespace:** `audio`
**File:** `src/samplemind/interfaces/cli/commands/audio.py`
**Purpose:** Audio format conversion, editing, and processing

#### Format Conversion (8 commands)
```bash
samplemind convert:wav <file>               # Convert to WAV
samplemind convert:mp3 <file> [--bitrate 320]
samplemind convert:flac <file>              # Convert to FLAC
samplemind convert:ogg <file>               # Convert to OGG
samplemind convert:aiff <file>              # Convert to AIFF
samplemind convert:m4a <file>               # Convert to M4A
samplemind convert:batch <folder> <format>  # Batch convert
samplemind convert:normalize-sample-rate    # Normalize sample rates in folder
```

#### Audio Editing (8 commands)
```bash
samplemind audio:normalize <file>           # Normalize loudness (LUFS)
samplemind audio:trim <file>                # Trim silence
samplemind audio:fade <file> [--in 0.5] [--out 0.5]  # Add fade
samplemind audio:split <file> [--duration 30]  # Split into segments
samplemind audio:join <files...>            # Join audio files
samplemind audio:speed <file> <factor>      # Change speed (1.0=100%)
samplemind audio:pitch <file> <semitones>   # Change pitch
samplemind audio:reverse <file>             # Reverse audio
```

#### Stem Separation (6 commands)
```bash
samplemind stems:separate <file>            # Separate all stems (Demucs v4)
samplemind stems:separate:vocals <file>     # Extract vocals only
samplemind stems:separate:drums <file>      # Extract drums only
samplemind stems:separate:bass <file>       # Extract bass only
samplemind stems:separate:other <file>      # Extract other only
samplemind stems:batch <folder>             # Batch stem separation
```

#### Audio Analysis (3 commands)
```bash
samplemind audio:duration <file>            # Get duration
samplemind audio:info <file>                # Full audio info
samplemind audio:validate <file>            # Validate audio integrity
```

---

### 2.6 GROUP 6: VISUALIZATION COMMANDS (15 commands)

**Namespace:** `viz` / `visualize`
**File:** `src/samplemind/interfaces/cli/commands/visualization.py`
**Purpose:** Generate audio visualizations

#### Waveform & Spectral (8 commands)
```bash
samplemind viz:waveform <file>              # Generate waveform image (PNG)
samplemind viz:spectrogram <file>           # Generate spectrogram
samplemind viz:chromagram <file>            # Generate chromagram
samplemind viz:mfcc <file>                  # MFCC visualization
samplemind viz:tempogram <file>             # Tempogram visualization
samplemind viz:frequency <file>             # Frequency response curve
samplemind viz:phase <file>                 # Phase visualization
samplemind viz:stereo <file>                # Stereo field visualization
```

#### Interactive & Export (7 commands)
```bash
samplemind viz:interactive <file>           # Interactive waveform viewer
samplemind viz:export <file> <format>       # Export viz (PNG/SVG/PDF)
samplemind viz:export:batch <folder>        # Batch export visualizations
samplemind viz:compare <file1> <file2>      # Compare spectrograms
samplemind viz:compare:batch <folder>       # Compare all samples
samplemind viz:heatmap <folder>             # Sample BPM/key heatmap
samplemind viz:timeline <folder>            # Timeline visualization
```

---

### 2.7 GROUP 7: REPORTING & EXPORT COMMANDS (10 commands)

**Namespace:** `report` / `export`
**File:** `src/samplemind/interfaces/cli/commands/reporting.py`
**Purpose:** Generate reports and export data

#### Reports (5 commands)
```bash
samplemind report:library                   # Library statistics report
samplemind report:analysis <file>           # Detailed analysis report
samplemind report:batch <folder>            # Batch processing report
samplemind report:quality <folder>          # Quality assessment report
samplemind report:export-all                # Export all reports
```

#### Export Formats (5 commands)
```bash
samplemind export:json <file>               # Export to JSON
samplemind export:csv <file>                # Export to CSV
samplemind export:yaml <file>               # Export to YAML
samplemind export:pdf <file>                # Export report to PDF
samplemind export:batch <folder> <format>   # Batch export
```

---

## 3. COMMAND IMPLEMENTATION STRATEGY

### 3.1 Phase Timeline

**Week 1-2: Foundation**
- Create Typer app structure
- Create command group modules
- Implement utilities and helpers

**Week 3: Analyze Group (40 commands)**
- Implement all analyze subcommands
- Create result formatters
- Add filtering and options

**Week 4: Library Group (50 commands)**
- Implement library management
- Search and filter capabilities
- Collections system

**Week 5: AI/Metadata/Audio (85 commands)**
- AI commands with provider routing
- Metadata editing and batch ops
- Audio processing and conversion

**Week 6: Visualization & Reporting (25 commands)**
- Visualization generators
- Report creators
- Export formatters

**Week 7: Integration & Testing**
- Full integration testing
- Command discovery
- Help system
- Performance optimization

**Week 8: Documentation**
- CLI reference (200+ commands)
- Examples and tutorials
- Migration guide from menu to CLI

---

### 3.2 Implementation Guidelines

**Code Structure per Command Module:**

```python
# Each module follows this pattern:
# src/samplemind/interfaces/cli/commands/analyze.py

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.progress import track

app = typer.Typer(help="Audio analysis commands")
console = Console()

@app.command()
def full(
    file: Path = typer.Argument(..., help="Audio file to analyze"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
    show_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Run comprehensive (DETAILED level) analysis"""
    # Implementation
    pass

@app.command()
def bpm(file: Path = typer.Argument(...)):
    """BPM/tempo detection"""
    # Implementation
    pass

# Register with main app in typer_app.py
```

**Key Patterns:**
- All commands async-compatible
- Rich console for output
- Progress tracking for long operations
- JSON output option for all commands
- Consistent error handling
- Type hints on all parameters

---

### 3.3 Command Options/Flags (Standard Across Groups)

**Universal Flags:**
```bash
--json                          # Output as JSON
--csv                           # Output as CSV
--quiet / -q                    # Minimal output
--verbose / -v                  # Detailed output
--output / -o <path>            # Output file path
--format <format>               # Output format
--parallel / --workers <n>      # Parallel execution
--cache / --no-cache            # Cache control
--offline                       # Offline-first mode
```

---

## 4. BACKWARD COMPATIBILITY

### 4.1 Maintained Interfaces

**Interactive Menu (Unchanged)**
- Original menu system remains available
- Can be invoked with `samplemind --interactive` or `samplemind -i`
- Quick commands (`analyze`, `batch`) still work

**Entry Point Changes**
```bash
# Original (still works)
python main.py analyze <file>
python main.py batch <folder>

# New (Typer-based)
samplemind analyze:full <file>
samplemind batch:analyze <folder>

# Interactive menu (unchanged)
samplemind --interactive
python main.py
```

### 4.2 Migration Path

Users can migrate at their own pace:
- **Phase 1:** Learn Typer subcommands while menu still works
- **Phase 2:** Create scripts using `samplemind` subcommands
- **Phase 3:** Optional: Automated menu → CLI migration tool

---

## 5. SUCCESS METRICS

### Phase 10.2 Completion Criteria

**Functionality:**
- [ ] All 200+ commands implemented
- [ ] All commands tested (unit + integration)
- [ ] Command discovery working (`--help`)
- [ ] Shell completion (bash/zsh/fish)
- [ ] Backward compatibility maintained

**Quality:**
- [ ] >90% test coverage on CLI code
- [ ] Performance <500ms for all commands
- [ ] Memory usage <100MB per command
- [ ] No breaking changes to menu system
- [ ] All error messages user-friendly

**Documentation:**
- [ ] CLI reference guide (200+ commands)
- [ ] Example scripts for common workflows
- [ ] Video tutorials (5-10 workflows)
- [ ] Migration guide from menu to CLI
- [ ] API documentation for CLI functions

**Release:**
- [ ] v2.1-beta version bump
- [ ] Release notes (Phase 10.2 section)
- [ ] Community announcement
- [ ] Blog post on new CLI capabilities

---

## 6. FUTURE EXTENSIONS (Phase 10.3+)

### Planned Enhancements
- Shell completion (bash/zsh/fish/powershell)
- Configuration profiles (presets for common workflows)
- CLI plugin system
- Remote execution (SSH support)
- Scheduled tasks / cron support
- Watch mode (auto-process on file changes)

---

## References

- Typer Documentation: https://typer.tiangolo.com/
- Rich Documentation: https://rich.readthedocs.io/
- SampleMind AI Architecture: CLAUDE.md
- Phase 10 Plan: PHASE_10_PLAN.md

---

**Document Owner:** Claude Code
**Last Updated:** January 19, 2026
**Version:** 1.0 (Planning)
