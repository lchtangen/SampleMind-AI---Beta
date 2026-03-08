# SampleMind AI - CLI Reference

> Complete command reference for SampleMind AI CLI with 213+ commands organized across 10 command groups.

**Version:** 2.1.0-beta
**Last Updated:** 2026-02-03

---

## Table of Contents

- [Quick Start](#quick-start)
- [Command Groups Overview](#command-groups-overview)
- [1. Analyze Commands (40 commands)](#1-analyze-commands-40-commands)
- [2. Library Commands (50 commands)](#2-library-commands-50-commands)
- [3. AI Commands (30 commands)](#3-ai-commands-30-commands)
- [4. Metadata Commands (30 commands)](#4-metadata-commands-30-commands)
- [5. Audio Commands (25 commands)](#5-audio-commands-25-commands)
- [6. Visualization Commands (15 commands)](#6-visualization-commands-15-commands)
- [7. Reporting Commands (10 commands)](#7-reporting-commands-10-commands)
- [8. Similarity Commands (5 commands)](#8-similarity-commands-5-commands)
- [9. Theory Commands (4 commands)](#9-theory-commands-4-commands)
- [10. DAW Commands (4 commands)](#10-daw-commands-4-commands)
- [Appendix](#appendix)

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/samplemind/samplemind-ai.git
cd samplemind-ai

# Setup environment
make setup

# Install offline AI models (optional)
make install-models
```

### Basic Usage

SampleMind AI can be invoked using either `samplemind` or the shorthand `smai`:

```bash
# Full command
samplemind analyze:full track.wav

# Shorthand
smai analyze:full track.wav
```

### Getting Help

```bash
# Show all command groups
smai --help

# Show commands in a group
smai analyze --help

# Show help for specific command
smai analyze:full --help
```

### Common Workflows

```bash
# Quick audio analysis
smai analyze:quick track.wav

# Organize sample library
smai library:organize ./samples --by metadata

# Find similar samples
smai similar:index ./library
smai similar:find kick.wav --count 10

# Separate stems
smai stems:separate song.wav --quality high

# Detect key and chords
smai theory:harmony song.wav --roman
```

---

## Command Groups Overview

| Group | Commands | Description | Icon |
|-------|----------|-------------|------|
| [analyze](#1-analyze-commands-40-commands) | 40 | Audio analysis & feature extraction | 🎵 |
| [library](#2-library-commands-50-commands) | 50 | Sample library management | 📁 |
| [ai](#3-ai-commands-30-commands) | 30 | AI-powered features | 🤖 |
| [metadata](#4-metadata-commands-30-commands) | 30 | Metadata operations | 📝 |
| [audio](#5-audio-commands-25-commands) | 25 | Audio processing & conversion | 🎙️ |
| [visualization](#6-visualization-commands-15-commands) | 15 | Visualizations & charts | 📊 |
| [reporting](#7-reporting-commands-10-commands) | 10 | Reports & data export | 📋 |
| [similarity](#8-similarity-commands-5-commands) | 5 | Sample similarity search | 🔍 |
| [theory](#9-theory-commands-4-commands) | 4 | Music theory analysis | 🎼 |
| [daw](#10-daw-commands-4-commands) | 4 | DAW integration | 🎹 |
| **Total** | **213+** | | |

---

## 1. Analyze Commands (40 commands)

Audio analysis and feature extraction commands for BPM, key, genre, spectral analysis, and more.

### Core Analysis (9 commands)

#### analyze:full

Run comprehensive (DETAILED level) analysis with all features.

```bash
smai analyze:full <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-f, --format FORMAT` - Output format: `json`, `csv`, `yaml`, `table` (default: `table`)
- `--profile` - Show profiling information

**Example:**
```bash
smai analyze:full track.wav -f json -o analysis.json
```

---

#### analyze:standard

Run standard analysis with core features (recommended for most use cases).

```bash
smai analyze:standard <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-f, --format FORMAT` - Output format (default: `table`)

**Example:**
```bash
smai analyze:standard kick.wav
```

---

#### analyze:basic

Run quick basic analysis (fast, minimal features).

```bash
smai analyze:basic <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai analyze:basic sample.wav
```

---

#### analyze:professional

Run professional analysis (PROFESSIONAL level - ML-optimized for production).

```bash
smai analyze:professional <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-f, --format FORMAT` - Output format (default: `json`)
- `--export-features` - Export raw feature vectors

**Example:**
```bash
smai analyze:professional master.wav --export-features -o features.json
```

---

#### analyze:quick

Ultra-fast analysis (< 1 second).

```bash
smai analyze:quick <file>
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Example:**
```bash
smai analyze:quick kick.wav
```

---

#### analyze:bpm

Extract tempo/BPM only.

```bash
smai analyze:bpm <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:bpm loop.wav
# Output: Tempo: 128.5 BPM
```

---

#### analyze:key

Extract key detection only.

```bash
smai analyze:key <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--confidence` - Show confidence score

**Example:**
```bash
smai analyze:key song.wav --confidence
# Output: Key: D Minor (Confidence: 87%)
```

---

#### analyze:mode

Extract major/minor mode only.

```bash
smai analyze:mode <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:mode track.wav
# Output: Mode: minor
```

---

#### analyze:compare

Compare two audio files.

```bash
smai analyze:compare <file1> <file2> [options]
```

**Arguments:**
- `file1` - First audio file (required)
- `file2` - Second audio file (required)

**Options:**
- `-m, --metric METRIC` - Metric to compare (default: `overall`)

**Example:**
```bash
smai analyze:compare original.wav remix.wav
```

---

### Classification (9 commands)

#### analyze:genre

Genre classification.

```bash
smai analyze:genre <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--top N` - Show top N genres (default: 3)

**Example:**
```bash
smai analyze:genre track.wav --top 5
```

---

#### analyze:mood

Mood/emotion detection.

```bash
smai analyze:mood <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:mood song.wav
# Output: Mood: Energetic, Uplifting
```

---

#### analyze:instrument

Instrument recognition.

```bash
smai analyze:instrument <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:instrument sample.wav
```

---

#### analyze:vocal

Vocal detection and characteristics.

```bash
smai analyze:vocal <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:vocal song.wav
```

---

#### analyze:quality

Quality and production score.

```bash
smai analyze:quality <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:quality master.wav
# Output: Quality Score: 87/100
```

---

#### analyze:energy

Energy level detection.

```bash
smai analyze:energy <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:energy drop.wav
```

---

#### analyze:dynamics

Dynamic range analysis.

```bash
smai analyze:dynamics <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:dynamics master.wav
```

---

#### analyze:loudness

Loudness measurement (LUFS).

```bash
smai analyze:loudness <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:loudness track.wav
# Output: Loudness: -14.2 LUFS
```

---

#### analyze:compression

Compression detection and analysis.

```bash
smai analyze:compression <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:compression master.wav
```

---

### Advanced Analysis (12 commands)

#### analyze:spectral

Spectral analysis and features.

```bash
smai analyze:spectral <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:spectral synth.wav
```

---

#### analyze:harmonic

Harmonic content analysis.

```bash
smai analyze:harmonic <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:harmonic pad.wav
```

---

#### analyze:percussive

Percussive content analysis.

```bash
smai analyze:percussive <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:percussive drums.wav
```

---

#### analyze:mfcc

Extract MFCC features.

```bash
smai analyze:mfcc <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--n-mfcc N` - Number of MFCC coefficients (default: 13)

**Example:**
```bash
smai analyze:mfcc sample.wav --n-mfcc 20
```

---

#### analyze:chroma

Extract chroma features.

```bash
smai analyze:chroma <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:chroma song.wav
```

---

#### analyze:onset

Onset (note start) detection.

```bash
smai analyze:onset <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:onset drums.wav
```

---

#### analyze:beats

Beat tracking.

```bash
smai analyze:beats <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:beats track.wav
```

---

#### analyze:segments

Segment detection (intro, verse, chorus, etc.).

```bash
smai analyze:segments <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:segments song.wav
```

---

#### analyze:tempogram

Tempogram (tempo over time).

```bash
smai analyze:tempogram <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:tempogram live_recording.wav
```

---

#### analyze:chromagram

Chromagram (chroma over time).

```bash
smai analyze:chromagram <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:chromagram song.wav
```

---

#### analyze:spectral-flux

Spectral flux (change over time).

```bash
smai analyze:spectral-flux <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:spectral-flux track.wav
```

---

#### analyze:zero-crossing

Zero-crossing rate (timbral brightness).

```bash
smai analyze:zero-crossing <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai analyze:zero-crossing hihat.wav
```

---

### Batch Processing (10 commands)

#### analyze:batch

Batch analyze all audio files in folder.

```bash
smai analyze:batch <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-f, --format FORMAT` - Output format (default: `json`)
- `-l, --level LEVEL` - Analysis level (default: `STANDARD`)

**Example:**
```bash
smai analyze:batch ./samples -f json -o batch_analysis.json
```

---

#### analyze:list

List all analyze commands.

```bash
smai analyze:list
```

**Example:**
```bash
smai analyze:list
```

---

## 2. Library Commands (50 commands)

Sample library management and organization commands.

### Library Management (15 commands)

#### library:organize

Auto-organize library by metadata (BPM, key, genre).

```bash
smai library:organize <folder> [options]
```

**Arguments:**
- `folder` - Library folder to organize (required)

**Options:**
- `--by METHOD` - Organization method: `metadata`, `genre`, `bpm`, `key` (default: `metadata`)
- `--dry-run` - Show changes without applying

**Example:**
```bash
smai library:organize ./samples --by genre --dry-run
```

---

#### library:scan

Scan and index all audio files in folder.

```bash
smai library:scan <folder> [options]
```

**Arguments:**
- `folder` - Folder to scan (required)

**Options:**
- `--index/--no-index` - Create index (default: enabled)
- `--recursive/--flat` - Scan recursively (default: recursive)

**Example:**
```bash
smai library:scan ./samples --recursive
```

---

#### library:import

Import audio files with metadata preservation.

```bash
smai library:import <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-d, --destination PATH` - Destination folder (default: `~/SampleMind/Library`)
- `--preserve/--flatten` - Preserve folder structure (default: preserve)

**Example:**
```bash
smai library:import ./new_samples -d ~/Music/Library
```

---

#### library:export

Export library metadata with files.

```bash
smai library:export <folder> [options]
```

**Arguments:**
- `folder` - Library folder (required)

**Options:**
- `-o, --output PATH` - Output path (default: `./library_export`)
- `-f, --format FORMAT` - Export format: `json`, `csv`, `yaml` (default: `json`)

**Example:**
```bash
smai library:export ./samples -f csv -o library_metadata.csv
```

---

#### library:sync

Sync library with cloud storage.

```bash
smai library:sync [options]
```

**Options:**
- `--direction DIR` - Sync direction: `up`, `down`, `both` (default: `both`)
- `--service SERVICE` - Cloud service: `cloud`, `dropbox`, `gdrive` (default: `cloud`)

**Example:**
```bash
smai library:sync --direction up --service dropbox
```

---

#### library:stats

Show library statistics.

```bash
smai library:stats [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:stats ./samples
```

---

#### library:size

Calculate total library size.

```bash
smai library:size [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:size
# Output: Total Size: 12.4 GB
```

---

#### library:list

List all samples in library.

```bash
smai library:list [folder] [options]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Options:**
- `-l, --limit N` - Max files to show (default: 20)
- `-f, --format FORMAT` - Output format (default: `table`)

**Example:**
```bash
smai library:list --limit 50
```

---

#### library:info

Show detailed file info.

```bash
smai library:info <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai library:info kick.wav
```

---

#### library:rebuild

Rebuild library index.

```bash
smai library:rebuild [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:rebuild
```

---

#### library:verify

Verify library integrity.

```bash
smai library:verify [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:verify ./samples
```

---

#### library:backup

Backup library to destination.

```bash
smai library:backup <destination> [options]
```

**Arguments:**
- `destination` - Backup destination (required)

**Options:**
- `-s, --source PATH` - Source folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:backup /backup/samples -s ./library
```

---

#### library:restore

Restore library from backup.

```bash
smai library:restore <backup_file> [options]
```

**Arguments:**
- `backup_file` - Backup file/folder (required)

**Options:**
- `-d, --destination PATH` - Destination folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:restore /backup/samples_2025.zip
```

---

#### library:update-metadata

Update all metadata from audio files.

```bash
smai library:update-metadata [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:update-metadata ./samples
```

---

#### library:refresh

Refresh library view and caches.

```bash
smai library:refresh [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:refresh
```

---

### Search & Filter (15 commands)

#### library:search

Full-text search in library.

```bash
smai library:search <query> [options]
```

**Arguments:**
- `query` - Search query (required)

**Options:**
- `-f, --folder PATH` - Library folder (default: `~/SampleMind/Library`)
- `-l, --limit N` - Max results (default: 20)

**Example:**
```bash
smai library:search "techno kick" --limit 10
```

---

#### library:find

Regex file search in library.

```bash
smai library:find <pattern> [options]
```

**Arguments:**
- `pattern` - Regex pattern (required)

**Options:**
- `-f, --folder PATH` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:find "kick_.*_120"
```

---

#### library:filter:bpm

Filter library by BPM range.

```bash
smai library:filter:bpm <min_bpm> [max_bpm] [options]
```

**Arguments:**
- `min_bpm` - Minimum BPM (required)
- `max_bpm` - Maximum BPM (optional, defaults to min_bpm + 10)

**Options:**
- `-f, --folder PATH` - Library folder

**Example:**
```bash
smai library:filter:bpm 120 130
```

---

#### library:filter:key

Filter library by musical key.

```bash
smai library:filter:key <key> [options]
```

**Arguments:**
- `key` - Musical key: `C`, `Dm`, `F#`, etc. (required)

**Options:**
- `-f, --folder PATH` - Library folder

**Example:**
```bash
smai library:filter:key "Am"
```

---

#### library:filter:genre

Filter library by genre.

```bash
smai library:filter:genre <genre> [options]
```

**Arguments:**
- `genre` - Genre: `techno`, `house`, `hiphop`, `ambient`, etc. (required)

**Options:**
- `-f, --folder PATH` - Library folder

**Example:**
```bash
smai library:filter:genre techno
```

---

#### library:filter:mood

Filter library by mood.

```bash
smai library:filter:mood <mood> [options]
```

**Arguments:**
- `mood` - Mood: `dark`, `bright`, `aggressive`, `mellow`, etc. (required)

**Options:**
- `-f, --folder PATH` - Library folder

**Example:**
```bash
smai library:filter:mood dark
```

---

#### library:filter:tag

Filter library by tag.

```bash
smai library:filter:tag <tag> [options]
```

**Arguments:**
- `tag` - Tag name (required)

**Options:**
- `-f, --folder PATH` - Library folder

**Example:**
```bash
smai library:filter:tag "808"
```

---

#### library:filter:duration

Filter library by duration.

```bash
smai library:filter:duration <min_duration> [max_duration] [options]
```

**Arguments:**
- `min_duration` - Min duration in MM:SS format (required)
- `max_duration` - Max duration in MM:SS format (optional)

**Options:**
- `-f, --folder PATH` - Library folder

**Example:**
```bash
smai library:filter:duration 0:30 2:00
```

---

#### library:filter:quality

Filter library by quality score.

```bash
smai library:filter:quality <min_quality> [options]
```

**Arguments:**
- `min_quality` - Minimum quality score 0-100 (required)

**Options:**
- `-f, --folder PATH` - Library folder

**Example:**
```bash
smai library:filter:quality 80
```

---

#### library:sort

Sort library by criteria.

```bash
smai library:sort <by> [options]
```

**Arguments:**
- `by` - Sort by: `bpm`, `key`, `name`, `date`, `quality` (required)

**Options:**
- `-f, --folder PATH` - Library folder
- `--reverse` - Reverse order

**Example:**
```bash
smai library:sort bpm --reverse
```

---

#### library:browse:random

Browse random samples from library.

```bash
smai library:browse:random [options]
```

**Options:**
- `-f, --folder PATH` - Library folder
- `-c, --count N` - Number of samples (default: 10)

**Example:**
```bash
smai library:browse:random --count 5
```

---

### Collections (12 commands)

#### collection:create

Create new collection.

```bash
smai collection:create <name>
```

**Arguments:**
- `name` - Collection name (required)

**Example:**
```bash
smai collection:create "Favorite Kicks"
```

---

#### collection:add

Add sample to collection.

```bash
smai collection:add <file_id> <collection>
```

**Arguments:**
- `file_id` - File ID or path (required)
- `collection` - Collection name (required)

**Example:**
```bash
smai collection:add kick_01.wav "Favorite Kicks"
```

---

#### collection:list

List all collections.

```bash
smai collection:list
```

**Example:**
```bash
smai collection:list
```

---

#### collection:show

Show collection contents.

```bash
smai collection:show <name>
```

**Arguments:**
- `name` - Collection name (required)

**Example:**
```bash
smai collection:show "Favorite Kicks"
```

---

#### collection:delete

Delete collection.

```bash
smai collection:delete <name> [options]
```

**Arguments:**
- `name` - Collection name (required)

**Options:**
- `-y, --confirm` - Skip confirmation

**Example:**
```bash
smai collection:delete "Old Samples" --confirm
```

---

#### collection:export

Export collection to file.

```bash
smai collection:export <name> [options]
```

**Arguments:**
- `name` - Collection name (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-f, --format FORMAT` - Export format (default: `json`)

**Example:**
```bash
smai collection:export "Kicks" -o kicks_collection.json
```

---

#### collection:import

Import collection from file.

```bash
smai collection:import <file> [options]
```

**Arguments:**
- `file` - Collection file (required)

**Options:**
- `-n, --name NAME` - Custom collection name

**Example:**
```bash
smai collection:import kicks_collection.json --name "Imported Kicks"
```

---

#### collection:merge

Merge two collections.

```bash
smai collection:merge <collection1> <collection2> [options]
```

**Arguments:**
- `collection1` - First collection (required)
- `collection2` - Second collection (required)

**Options:**
- `-o, --output NAME` - Output collection name

**Example:**
```bash
smai collection:merge "Kicks" "Bass" -o "Kicks and Bass"
```

---

#### collection:rename

Rename collection.

```bash
smai collection:rename <old_name> <new_name>
```

**Arguments:**
- `old_name` - Current name (required)
- `new_name` - New name (required)

**Example:**
```bash
smai collection:rename "Old Name" "New Name"
```

---

### Cleanup & Maintenance (8 commands)

#### library:dedupe

Find duplicate files in library.

```bash
smai library:dedupe [folder] [options]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Options:**
- `--remove` - Remove duplicates

**Example:**
```bash
smai library:dedupe ./samples --remove
```

---

#### library:cleanup

Remove broken/invalid audio files.

```bash
smai library:cleanup [folder] [options]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Options:**
- `--remove` - Remove broken files

**Example:**
```bash
smai library:cleanup --remove
```

---

#### library:orphans

Find files without metadata.

```bash
smai library:orphans [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:orphans ./samples
```

---

#### library:unused

Find unused samples (not in any collection).

```bash
smai library:unused [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:unused
```

---

#### library:prune

Remove files older than N days.

```bash
smai library:prune [days] [options]
```

**Arguments:**
- `days` - Older than N days (default: 90)

**Options:**
- `-f, --folder PATH` - Library folder
- `--remove` - Remove files

**Example:**
```bash
smai library:prune 180 --remove
```

---

#### library:optimize

Optimize library for performance.

```bash
smai library:optimize [folder]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Example:**
```bash
smai library:optimize
```

---

## 3. AI Commands (30 commands)

AI-powered features and provider management commands.

### AI Analysis (10 commands)

#### ai:analyze

AI-powered comprehensive analysis.

```bash
smai ai:analyze <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-f, --format FORMAT` - Output format (default: `table`)
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai ai:analyze track.wav -f json
```

---

#### ai:classify

AI audio classification (genre, mood, instrument).

```bash
smai ai:classify <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--confidence` - Show confidence scores

**Example:**
```bash
smai ai:classify track.wav --confidence
```

---

#### ai:tag

AI auto-tagging for samples.

```bash
smai ai:tag <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--apply` - Apply tags to file

**Example:**
```bash
smai ai:tag kick.wav --apply
```

---

#### ai:suggest

AI-powered similar sample suggestions.

```bash
smai ai:suggest <file> [options]
```

**Arguments:**
- `file` - Reference audio file (required)

**Options:**
- `-n, --count N` - Number of suggestions (default: 5)

**Example:**
```bash
smai ai:suggest kick.wav --count 10
```

---

#### ai:coach

AI production coaching for your track.

```bash
smai ai:coach <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `--category CAT` - Coaching category: `general`, `mixing`, `mastering`, `sound-design` (default: `general`)

**Example:**
```bash
smai ai:coach track.wav --category mixing
```

---

#### ai:preset

Generate EQ/compressor/reverb AI presets.

```bash
smai ai:preset <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--type TYPE` - Preset type: `eq`, `compressor`, `reverb` (default: `eq`)

**Example:**
```bash
smai ai:preset vocal.wav --type compressor
```

---

#### ai:mastering

AI mastering suggestions and analysis.

```bash
smai ai:mastering <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--reference PATH` - Reference track

**Example:**
```bash
smai ai:mastering mixdown.wav --reference reference.wav
```

---

#### ai:reference

Analyze track as reference for your mix.

```bash
smai ai:reference <file>
```

**Arguments:**
- `file` - Reference track to analyze (required)

**Example:**
```bash
smai ai:reference commercial_track.wav
```

---

#### ai:remix

AI remix ideas and suggestions.

```bash
smai ai:remix <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--style STYLE` - Remix style (default: `minimal`)

**Example:**
```bash
smai ai:remix original.wav --style techno
```

---

#### ai:mix:tips

AI mixing tips for your track.

```bash
smai ai:mix:tips <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai ai:mix:tips mixdown.wav
```

---

### Provider Management (8 commands)

#### ai:provider

Show active AI provider and status.

```bash
smai ai:provider
```

**Example:**
```bash
smai ai:provider
# Output: Provider: Google Gemini 3 Flash (Active)
```

---

#### ai:provider:list

List available AI providers.

```bash
smai ai:provider:list
```

**Example:**
```bash
smai ai:provider:list
```

---

#### ai:provider:set

Set default AI provider.

```bash
smai ai:provider:set <provider>
```

**Arguments:**
- `provider` - Provider name: `gemini`, `openai`, `anthropic`, `ollama` (required)

**Example:**
```bash
smai ai:provider:set ollama
```

---

#### ai:model

Show active AI model.

```bash
smai ai:model
```

**Example:**
```bash
smai ai:model
# Output: Active Model: gemini-3-flash
```

---

#### ai:model:list

List available AI models.

```bash
smai ai:model:list [options]
```

**Options:**
- `-p, --provider PROVIDER` - Filter by provider (default: `all`)

**Example:**
```bash
smai ai:model:list --provider ollama
```

---

#### ai:model:set

Set default AI model.

```bash
smai ai:model:set <model>
```

**Arguments:**
- `model` - Model name (required)

**Example:**
```bash
smai ai:model:set phi3:mini
```

---

#### ai:key:test

Test API key connectivity.

```bash
smai ai:key:test [options]
```

**Options:**
- `-p, --provider PROVIDER` - Test specific provider (default: `all`)

**Example:**
```bash
smai ai:key:test --provider gemini
```

---

#### ai:usage

Show AI API usage and quotas.

```bash
smai ai:usage [options]
```

**Options:**
- `-p, --provider PROVIDER` - Filter by provider (default: `all`)

**Example:**
```bash
smai ai:usage
```

---

### Configuration (8 commands)

#### ai:config

Show AI configuration.

```bash
smai ai:config
```

**Example:**
```bash
smai ai:config
```

---

#### ai:config:temperature

Set AI temperature (creativity).

```bash
smai ai:config:temperature <value>
```

**Arguments:**
- `value` - Temperature 0.0-1.0 (required)

**Example:**
```bash
smai ai:config:temperature 0.7
```

---

#### ai:config:max-tokens

Set maximum tokens for AI responses.

```bash
smai ai:config:max-tokens <value>
```

**Arguments:**
- `value` - Max tokens (required)

**Example:**
```bash
smai ai:config:max-tokens 4096
```

---

#### ai:config:cache

Enable/disable AI response caching.

```bash
smai ai:config:cache <enable>
```

**Arguments:**
- `enable` - true/false (required)

**Example:**
```bash
smai ai:config:cache true
```

---

#### ai:config:offline

Enable/disable offline-first AI mode.

```bash
smai ai:config:offline <enable>
```

**Arguments:**
- `enable` - true/false (required)

**Example:**
```bash
smai ai:config:offline true
```

---

#### ai:config:rate-limit

Set AI request rate limit.

```bash
smai ai:config:rate-limit <rps>
```

**Arguments:**
- `rps` - Requests per second (required)

**Example:**
```bash
smai ai:config:rate-limit 10
```

---

#### ai:config:timeout

Set AI request timeout.

```bash
smai ai:config:timeout <seconds>
```

**Arguments:**
- `seconds` - Timeout in seconds (required)

**Example:**
```bash
smai ai:config:timeout 60
```

---

#### ai:config:reset

Reset AI configuration to defaults.

```bash
smai ai:config:reset
```

**Example:**
```bash
smai ai:config:reset
```

---

### Features (4 commands)

#### ai:features

List available AI features.

```bash
smai ai:features
```

**Example:**
```bash
smai ai:features
```

---

#### ai:features:enable

Enable AI feature.

```bash
smai ai:features:enable <feature>
```

**Arguments:**
- `feature` - Feature name (required)

**Example:**
```bash
smai ai:features:enable auto-tagging
```

---

#### ai:features:disable

Disable AI feature.

```bash
smai ai:features:disable <feature>
```

**Arguments:**
- `feature` - Feature name (required)

**Example:**
```bash
smai ai:features:disable mastering-ai
```

---

#### ai:features:test

Test AI feature.

```bash
smai ai:features:test <feature>
```

**Arguments:**
- `feature` - Feature to test (required)

**Example:**
```bash
smai ai:features:test classification
```

---

## 4. Metadata Commands (30 commands)

Metadata viewing, editing, and batch operations.

### Metadata Viewing (8 commands)

#### meta:show

Display all metadata.

```bash
smai meta:show <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-f, --format FORMAT` - Output format (default: `table`)

**Example:**
```bash
smai meta:show kick.wav
```

---

#### meta:show:tags

Show tags only.

```bash
smai meta:show:tags <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai meta:show:tags sample.wav
```

---

#### meta:show:analysis

Show analysis results only.

```bash
smai meta:show:analysis <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai meta:show:analysis track.wav
```

---

#### meta:show:custom

Show custom metadata.

```bash
smai meta:show:custom <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai meta:show:custom sample.wav
```

---

#### meta:export

Export metadata to file.

```bash
smai meta:export <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-f, --format FORMAT` - Export format (default: `json`)

**Example:**
```bash
smai meta:export track.wav -o metadata.json
```

---

#### meta:diff

Compare metadata between two files.

```bash
smai meta:diff <file1> <file2>
```

**Arguments:**
- `file1` - First audio file (required)
- `file2` - Second audio file (required)

**Example:**
```bash
smai meta:diff original.wav copy.wav
```

---

#### meta:validate

Validate metadata integrity.

```bash
smai meta:validate <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai meta:validate sample.wav
```

---

### Metadata Editing (8 commands)

#### meta:edit

Interactive metadata editor.

```bash
smai meta:edit <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai meta:edit track.wav
```

---

#### meta:set

Set single metadata value.

```bash
smai meta:set <file> <key> <value>
```

**Arguments:**
- `file` - Audio file (required)
- `key` - Metadata key (required)
- `value` - Metadata value (required)

**Example:**
```bash
smai meta:set kick.wav bpm 128
```

---

#### meta:add:tag

Add tag to file.

```bash
smai meta:add:tag <file> <tag>
```

**Arguments:**
- `file` - Audio file (required)
- `tag` - Tag name (required)

**Example:**
```bash
smai meta:add:tag kick.wav "808"
```

---

#### meta:remove:tag

Remove tag from file.

```bash
smai meta:remove:tag <file> <tag>
```

**Arguments:**
- `file` - Audio file (required)
- `tag` - Tag name (required)

**Example:**
```bash
smai meta:remove:tag kick.wav "old"
```

---

#### meta:copy

Copy metadata from one file to another.

```bash
smai meta:copy <source> <destination>
```

**Arguments:**
- `source` - Source audio file (required)
- `destination` - Destination audio file (required)

**Example:**
```bash
smai meta:copy original.wav copy.wav
```

---

#### meta:clear

Clear all metadata.

```bash
smai meta:clear <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-y, --confirm` - Skip confirmation

**Example:**
```bash
smai meta:clear sample.wav --confirm
```

---

### Batch Operations (10 commands)

#### meta:batch:tag

Batch add tag to all files.

```bash
smai meta:batch:tag <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-t, --tag TAG` - Tag to add (required)

**Example:**
```bash
smai meta:batch:tag ./kicks --tag "Kick"
```

---

#### meta:batch:fix

Batch fix metadata issues.

```bash
smai meta:batch:fix <folder>
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Example:**
```bash
smai meta:batch:fix ./samples
```

---

#### meta:batch:sync

Batch sync metadata from AI analysis.

```bash
smai meta:batch:sync <folder>
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Example:**
```bash
smai meta:batch:sync ./library
```

---

#### meta:batch:export

Batch export metadata for all files.

```bash
smai meta:batch:export <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-o, --output PATH` - Output path

**Example:**
```bash
smai meta:batch:export ./samples -o metadata_export/
```

---

#### meta:batch:import

Batch import metadata from file.

```bash
smai meta:batch:import <folder> [options]
```

**Arguments:**
- `folder` - Target folder (required)

**Options:**
- `-s, --source PATH` - Metadata file/folder (required)

**Example:**
```bash
smai meta:batch:import ./samples --source metadata.json
```

---

#### meta:batch:clear

Batch clear metadata from all files.

```bash
smai meta:batch:clear <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-y, --confirm` - Skip confirmation

**Example:**
```bash
smai meta:batch:clear ./old_samples --confirm
```

---

#### meta:batch:validate

Batch validate metadata integrity.

```bash
smai meta:batch:validate <folder>
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Example:**
```bash
smai meta:batch:validate ./library
```

---

#### meta:batch:standardize

Batch standardize metadata format.

```bash
smai meta:batch:standardize <folder>
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Example:**
```bash
smai meta:batch:standardize ./samples
```

---

### Recovery & Snapshots (4 commands)

#### meta:recover

Recover lost metadata.

```bash
smai meta:recover <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai meta:recover corrupted.wav
```

---

#### meta:snapshot

Create metadata snapshot for backup.

```bash
smai meta:snapshot
```

**Example:**
```bash
smai meta:snapshot
# Output: Snapshot created: metadata_snapshot_2025-01-19_10-30
```

---

#### meta:snapshot:list

List available snapshots.

```bash
smai meta:snapshot:list
```

**Example:**
```bash
smai meta:snapshot:list
```

---

#### meta:restore

Restore metadata from snapshot.

```bash
smai meta:restore <snapshot_id>
```

**Arguments:**
- `snapshot_id` - Snapshot ID (required)

**Example:**
```bash
smai meta:restore metadata_snapshot_2025-01-19_10-30
```

---

## 5. Audio Commands (25 commands)

Audio format conversion, editing, and processing.

### Format Conversion (7 commands)

#### convert:wav

Convert audio to WAV.

```bash
smai convert:wav <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai convert:wav track.mp3 -o track.wav
```

---

#### convert:mp3

Convert audio to MP3.

```bash
smai convert:mp3 <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--bitrate N` - Bitrate in kbps (default: 320)
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai convert:mp3 track.wav --bitrate 256
```

---

#### convert:flac

Convert audio to FLAC.

```bash
smai convert:flac <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai convert:flac track.wav
```

---

#### convert:ogg

Convert audio to OGG.

```bash
smai convert:ogg <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai convert:ogg track.wav
```

---

#### convert:aiff

Convert audio to AIFF.

```bash
smai convert:aiff <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai convert:aiff track.wav
```

---

#### convert:m4a

Convert audio to M4A.

```bash
smai convert:m4a <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai convert:m4a track.wav
```

---

#### convert:batch

Batch convert all audio files.

```bash
smai convert:batch <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-f, --format FORMAT` - Target format (default: `wav`)

**Example:**
```bash
smai convert:batch ./mp3s -f wav
```

---

### Audio Editing (8 commands)

#### audio:normalize

Normalize audio loudness (LUFS).

```bash
smai audio:normalize <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-l, --loudness N` - Target LUFS (default: -14.0)
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai audio:normalize track.wav -l -12
```

---

#### audio:trim

Trim silence from beginning and end.

```bash
smai audio:trim <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--threshold N` - Silence threshold in dB (default: -40)
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai audio:trim vocal.wav --threshold -50
```

---

#### audio:fade

Add fade in/out.

```bash
smai audio:fade <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--in N` - Fade in duration in seconds (default: 0.5)
- `--out N` - Fade out duration in seconds (default: 0.5)
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai audio:fade track.wav --in 2 --out 3
```

---

#### audio:split

Split audio into segments.

```bash
smai audio:split <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `--duration N` - Segment duration in seconds (default: 30)
- `-o, --output PATH` - Output folder path

**Example:**
```bash
smai audio:split long_track.wav --duration 60
```

---

#### audio:join

Join multiple audio files.

```bash
smai audio:join <files...> [options]
```

**Arguments:**
- `files` - Audio files to join (required, multiple)

**Options:**
- `-o, --output PATH` - Output file path (default: `./joined.wav`)

**Example:**
```bash
smai audio:join intro.wav verse.wav chorus.wav -o song.wav
```

---

#### audio:speed

Change audio speed without pitch change.

```bash
smai audio:speed <file> <factor> [options]
```

**Arguments:**
- `file` - Audio file (required)
- `factor` - Speed factor: 1.0=100%, 1.5=150% (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai audio:speed track.wav 1.25
```

---

#### audio:pitch

Change audio pitch.

```bash
smai audio:pitch <file> <semitones> [options]
```

**Arguments:**
- `file` - Audio file (required)
- `semitones` - Pitch shift in semitones (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai audio:pitch vocal.wav -3
```

---

#### audio:reverse

Reverse audio.

```bash
smai audio:reverse <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai audio:reverse sample.wav
```

---

### Stem Separation (6 commands)

#### stems:separate

Separate audio into stems (vocals, drums, bass, other) using Demucs AI.

```bash
smai stems:separate <file> [options]
```

**Arguments:**
- `file` - Audio file to separate (required)

**Options:**
- `-m, --model MODEL` - Demucs model: `mdx`, `mdx_extra`, `mdx_q`, `htdemucs` (default: `mdx_extra`)
- `-o, --output PATH` - Output directory
- `-q, --quality QUALITY` - Quality preset: `fast`, `standard`, `high` (default: `standard`)
- `-d, --device DEVICE` - Device: `cpu`, `cuda`, `mps`

**Example:**
```bash
smai stems:separate song.wav --quality high -o ./stems
```

---

#### stems:vocals

Extract vocals stem only (fast two-stem mode).

```bash
smai stems:vocals <file> [options]
```

**Arguments:**
- `file` - Audio file to process (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-q, --quality QUALITY` - Quality preset (default: `fast`)
- `-d, --device DEVICE` - Device

**Example:**
```bash
smai stems:vocals song.wav -o vocals.wav
```

---

#### stems:drums

Extract drums stem only (fast two-stem mode).

```bash
smai stems:drums <file> [options]
```

**Arguments:**
- `file` - Audio file to process (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-q, --quality QUALITY` - Quality preset (default: `fast`)
- `-d, --device DEVICE` - Device

**Example:**
```bash
smai stems:drums song.wav -o drums.wav
```

---

#### stems:bass

Extract bass stem only (requires full separation).

```bash
smai stems:bass <file> [options]
```

**Arguments:**
- `file` - Audio file to process (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-q, --quality QUALITY` - Quality preset (default: `standard`)
- `-d, --device DEVICE` - Device

**Example:**
```bash
smai stems:bass song.wav -o bass.wav
```

---

#### stems:other

Extract other/melody stem only (requires full separation).

```bash
smai stems:other <file> [options]
```

**Arguments:**
- `file` - Audio file to process (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-q, --quality QUALITY` - Quality preset (default: `standard`)
- `-d, --device DEVICE` - Device

**Example:**
```bash
smai stems:other song.wav -o melody.wav
```

---

#### stems:batch

Batch separate stems for all audio files in a folder.

```bash
smai stems:batch <folder> [options]
```

**Arguments:**
- `folder` - Folder containing audio files (required)

**Options:**
- `-o, --output PATH` - Output directory
- `-q, --quality QUALITY` - Quality preset (default: `standard`)
- `-d, --device DEVICE` - Device
- `--ext EXTENSIONS` - File extensions to process (default: `wav,mp3,flac,aiff,m4a`)

**Example:**
```bash
smai stems:batch ./songs --quality high -o ./all_stems
```

---

### Audio Analysis (3 commands)

#### audio:duration

Get audio duration.

```bash
smai audio:duration <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai audio:duration track.wav
# Output: Duration: 3:24
```

---

#### audio:info

Show full audio information.

```bash
smai audio:info <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai audio:info track.wav
```

---

#### audio:validate

Validate audio file integrity.

```bash
smai audio:validate <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai audio:validate sample.wav
```

---

## 6. Visualization Commands (15 commands)

Generate audio visualizations and charts.

### Waveform & Spectral (8 commands)

#### viz:waveform

Generate waveform visualization.

```bash
smai viz:waveform <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path
- `--size WIDTHxHEIGHT` - Image size (default: `1920x1080`)
- `--color COLOR` - Color scheme (default: `blue`)

**Example:**
```bash
smai viz:waveform track.wav --size 1280x720 --color green
```

---

#### viz:spectrogram

Generate spectrogram visualization.

```bash
smai viz:spectrogram <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path
- `--cmap COLORMAP` - Colormap (default: `viridis`)

**Example:**
```bash
smai viz:spectrogram track.wav --cmap inferno
```

---

#### viz:chromagram

Generate chromagram (chroma over time).

```bash
smai viz:chromagram <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai viz:chromagram song.wav
```

---

#### viz:mfcc

Generate MFCC visualization.

```bash
smai viz:mfcc <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai viz:mfcc vocal.wav
```

---

#### viz:tempogram

Generate tempogram (tempo over time).

```bash
smai viz:tempogram <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai viz:tempogram track.wav
```

---

#### viz:frequency

Generate frequency response curve.

```bash
smai viz:frequency <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path
- `--scale SCALE` - Frequency scale: `linear`, `log` (default: `log`)

**Example:**
```bash
smai viz:frequency master.wav --scale linear
```

---

#### viz:phase

Generate phase visualization.

```bash
smai viz:phase <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai viz:phase stereo.wav
```

---

#### viz:stereo

Generate stereo field visualization.

```bash
smai viz:stereo <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai viz:stereo master.wav
```

---

### Export & Comparison (7 commands)

#### viz:export

Export visualization to file.

```bash
smai viz:export <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-f, --format FORMAT` - Export format: `png`, `svg`, `pdf` (default: `png`)
- `--dpi N` - DPI for export (default: 300)

**Example:**
```bash
smai viz:export track.wav -f svg --dpi 600
```

---

#### viz:compare

Compare spectrograms of two files.

```bash
smai viz:compare <file1> <file2> [options]
```

**Arguments:**
- `file1` - First audio file (required)
- `file2` - Second audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai viz:compare original.wav processed.wav
```

---

#### viz:compare:batch

Compare all samples in folder.

```bash
smai viz:compare:batch <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-o, --output PATH` - Output folder path

**Example:**
```bash
smai viz:compare:batch ./samples
```

---

#### viz:heatmap

Generate sample BPM/key/genre heatmap.

```bash
smai viz:heatmap <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `--metric METRIC` - Metric for heatmap: `bpm`, `key`, `genre` (default: `bpm`)

**Example:**
```bash
smai viz:heatmap ./library --metric key
```

---

#### viz:timeline

Generate sample timeline visualization.

```bash
smai viz:timeline <folder>
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Example:**
```bash
smai viz:timeline ./project
```

---

#### viz:interactive

Open interactive waveform viewer.

```bash
smai viz:interactive <file>
```

**Arguments:**
- `file` - Audio file (required)

**Example:**
```bash
smai viz:interactive track.wav
```

---

#### viz:export:batch

Batch export visualizations for all files.

```bash
smai viz:export:batch <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-f, --format FORMAT` - Export format (default: `png`)

**Example:**
```bash
smai viz:export:batch ./samples -f svg
```

---

## 7. Reporting Commands (10 commands)

Generate reports and export data in various formats.

### Reports (5 commands)

#### report:library

Generate library statistics report.

```bash
smai report:library [folder] [options]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai report:library ./samples -o library_stats.pdf
```

---

#### report:analysis

Generate detailed analysis report.

```bash
smai report:analysis <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path
- `-f, --format FORMAT` - Output format (default: `table`)

**Example:**
```bash
smai report:analysis track.wav -f pdf -o analysis_report.pdf
```

---

#### report:batch

Generate batch processing report.

```bash
smai report:batch <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai report:batch ./processed -o batch_report.csv
```

---

#### report:quality

Generate quality assessment report.

```bash
smai report:quality <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai report:quality ./masters
```

---

#### report:export-all

Export all reports at once.

```bash
smai report:export-all [folder] [options]
```

**Arguments:**
- `folder` - Library folder (default: `~/SampleMind/Library`)

**Options:**
- `-o, --output PATH` - Output folder path (default: `./reports`)

**Example:**
```bash
smai report:export-all ./library -o ./reports
```

---

### Export Formats (5 commands)

#### export:json

Export analysis to JSON.

```bash
smai export:json <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path
- `--pretty/--compact` - Pretty print JSON (default: pretty)

**Example:**
```bash
smai export:json track.wav -o analysis.json
```

---

#### export:csv

Export analysis to CSV.

```bash
smai export:csv <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai export:csv track.wav -o analysis.csv
```

---

#### export:yaml

Export analysis to YAML.

```bash
smai export:yaml <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path

**Example:**
```bash
smai export:yaml track.wav -o analysis.yaml
```

---

#### export:pdf

Export analysis report to PDF.

```bash
smai export:pdf <file> [options]
```

**Arguments:**
- `file` - Audio file (required)

**Options:**
- `-o, --output PATH` - Output file path
- `--with-viz/--no-viz` - Include visualizations (default: enabled)

**Example:**
```bash
smai export:pdf track.wav --with-viz -o report.pdf
```

---

#### export:batch

Batch export all files to format.

```bash
smai export:batch <folder> [options]
```

**Arguments:**
- `folder` - Folder with audio files (required)

**Options:**
- `-f, --format FORMAT` - Export format (default: `json`)
- `-o, --output PATH` - Output folder path

**Example:**
```bash
smai export:batch ./samples -f csv -o exports/
```

---

## 8. Similarity Commands (5 commands)

Find similar audio samples using vector embeddings and ChromaDB.

#### similar:find

Find similar samples to a query file.

```bash
smai similar:find <file> [options]
```

**Arguments:**
- `file` - Query audio file (required)

**Options:**
- `-n, --count N` - Number of results (default: 10)
- `--min N` - Minimum similarity 0.0-1.0 (default: 0.5)
- `--tempo-min N` - Filter: minimum BPM
- `--tempo-max N` - Filter: maximum BPM
- `-k, --key KEY` - Filter: musical key (e.g., `C`, `Am`)

**Example:**
```bash
smai similar:find kick.wav --count 5 --tempo-min 120 --tempo-max 130
```

---

#### similar:index

Build similarity index for a folder of audio files.

```bash
smai similar:index <folder> [options]
```

**Arguments:**
- `folder` - Folder to index (required)

**Options:**
- `-r, --recursive/--no-recursive` - Include subdirectories (default: recursive)
- `--ext EXTENSIONS` - File extensions to index (default: `wav,mp3,flac,aiff,m4a,ogg`)
- `--rebuild` - Clear and rebuild entire index

**Example:**
```bash
smai similar:index ./library --rebuild
```

---

#### similar:compare

Compare similarity between two audio files.

```bash
smai similar:compare <file1> <file2>
```

**Arguments:**
- `file1` - First audio file (required)
- `file2` - Second audio file (required)

**Example:**
```bash
smai similar:compare kick_a.wav kick_b.wav
# Output: Similarity: 87.3% - Very Similar
```

---

#### similar:stats

Show similarity database statistics.

```bash
smai similar:stats
```

**Example:**
```bash
smai similar:stats
```

---

#### similar:clear

Clear the similarity database.

```bash
smai similar:clear [options]
```

**Options:**
- `-y, --yes` - Skip confirmation

**Example:**
```bash
smai similar:clear --yes
```

---

## 9. Theory Commands (4 commands)

Analyze harmonic content of audio files including chord progressions, key detection, and Roman numeral analysis.

#### theory:key

Detect the musical key of an audio file.

```bash
smai theory:key <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `-d, --detail` - Show detailed analysis with modulations

**Example:**
```bash
smai theory:key song.wav --detail
# Output: Detected Key: D minor (Confidence: 87.3%)
# Key Modulations:
#   [1:24] D minor → F major
#   [2:48] F major → D minor
```

---

#### theory:chords

Detect chord progression in an audio file.

```bash
smai theory:chords <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `-f, --format FORMAT` - Output format: `table`, `timeline`, `list` (default: `table`)
- `-r, --roman` - Include Roman numeral analysis
- `--min-duration N` - Minimum chord duration in seconds (default: 0.25)

**Example:**
```bash
smai theory:chords song.wav --roman --format timeline
# Output: Key: D minor
#   0.00s Am     vi    ████
#   2.50s Dm     i     ████████
#   5.00s Bb     VI    ██████
#   7.25s C      VII   ████
```

---

#### theory:harmony

Perform full harmonic analysis on an audio file.

```bash
smai theory:harmony <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `--roman/--no-roman` - Show Roman numeral analysis (default: enabled)

**Example:**
```bash
smai theory:harmony song.wav
# Output: Harmonic Analysis Summary
#   Key: D minor
#   Key Confidence: 87.3%
#   Duration: 3:24
#   Chord Changes: 24
#   Harmonic Rhythm: 2.1 changes/bar
#   Modulations: 2
#
# Chord Progression:
#   Am (vi) → Dm (i) → Bb (VI) → C (VII) → ...
#
# Scale Notes: D E F G A Bb C
```

---

#### theory:scale

Show scale notes for a given key.

```bash
smai theory:scale <key>
```

**Arguments:**
- `key` - Key name: `C major`, `Am`, `F# minor`, etc. (required)

**Example:**
```bash
smai theory:scale "D minor"
# Output: D minor Scale
#
# Degree  Note
# 1       D
# 2       E
# b3      F
# 4       G
# 5       A
# b6      Bb
# b7      C
#
# Scale: D - E - F - G - A - Bb - C
#
# Common Chords in Key:
#   i    : D minor
#   ii°  : E diminished
#   III  : F major
#   iv   : G minor
#   v    : A minor
#   VI   : Bb major
#   VII  : C major
```

---

## 10. DAW Commands (4 commands)

Commands for interacting with Digital Audio Workstations.

#### daw:status

Show DAW integration status and available plugins.

```bash
smai daw:status
```

**Example:**
```bash
smai daw:status
# Output: Available DAW Integrations
#   DAW            Plugin                    Version      Status
#   FL Studio      SampleMind AI             2.1.0-beta   Available
#   Ableton Live   SampleMind Control        2.1.0-beta   Experimental
#   Logic Pro      SampleMind AU Plugin      2.1.0-beta   Experimental
#   VST3 (Generic) SampleMind VST3           2.1.0-beta   Planned
```

---

#### daw:export:flp

Export samples as FL Studio project (.flp format).

```bash
smai daw:export:flp <files...> [options]
```

**Arguments:**
- `files` - Audio files to include (required, multiple)

**Options:**
- `-o, --output PATH` - Output .flp file
- `-t, --template PATH` - Template project
- `--bpm N` - Project BPM
- `-k, --key KEY` - Project key

**Example:**
```bash
smai daw:export:flp kick.wav snare.wav hihat.wav -o my_project.json --bpm 128
```

---

#### daw:analyze

Analyze a sample for DAW compatibility.

```bash
smai daw:analyze <file> [options]
```

**Arguments:**
- `file` - Audio file to analyze (required)

**Options:**
- `--target-bpm N` - Target BPM for time-stretching
- `--target-key KEY` - Target key for pitch-shifting

**Example:**
```bash
smai daw:analyze loop.wav --target-bpm 128 --target-key "Am"
# Output: DAW Compatibility Analysis
#   Property       Value         DAW Recommendation
#   BPM            120.0         Time-stretch by 1.07x
#   Key            Dm            Pitch shift from Dm to Am
#   Genre          Techno
#   Duration       4.00s
#   Sample Rate    44100 Hz
#   Bit Depth      24-bit
#   Channels       Stereo
#
# DAW Workflow Recommendations:
#   • Sample is loop-friendly at 120 BPM
#   • Use in Dm projects or transpose as needed
```

---

#### daw:sync

Sync sample library with DAW browser.

```bash
smai daw:sync <folder> [options]
```

**Arguments:**
- `folder` - Sample library folder to sync (required)

**Options:**
- `-d, --daw DAW` - Target DAW: `flstudio`, `ableton`, `logic` (default: `flstudio`)
- `--metadata/--no-metadata` - Export metadata files (default: enabled)

**Example:**
```bash
smai daw:sync ./samples --daw flstudio
# Output: Syncing Library with DAW
#   Folder: ./samples
#   Target DAW: flstudio
#   Found: 156 audio files
#
# ✓ Synced 156/156 files
#   Created 156 metadata files
```

---

## Appendix

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SAMPLEMIND_HOME` | SampleMind data directory | `~/.samplemind` |
| `SAMPLEMIND_LIBRARY` | Default library path | `~/SampleMind/Library` |
| `SAMPLEMIND_AI_PROVIDER` | Default AI provider | `gemini` |
| `SAMPLEMIND_AI_MODEL` | Default AI model | `gemini-3-flash` |
| `SAMPLEMIND_OFFLINE` | Force offline mode | `false` |
| `GOOGLE_API_KEY` | Google Gemini API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |

### Configuration Files

| File | Purpose |
|------|---------|
| `~/.samplemind/config.yaml` | Main configuration |
| `~/.samplemind/ai_providers.yaml` | AI provider settings |
| `~/.samplemind/library.db` | Library database |
| `~/.samplemind/similarity/` | ChromaDB similarity index |
| `~/.samplemind/cache/` | Analysis cache |

### Shell Completion Setup

#### Bash

```bash
# Add to ~/.bashrc
eval "$(_SAMPLEMIND_COMPLETE=bash_source samplemind)"
```

#### Zsh

```bash
# Add to ~/.zshrc
eval "$(_SAMPLEMIND_COMPLETE=zsh_source samplemind)"
```

#### Fish

```bash
# Run once
_SAMPLEMIND_COMPLETE=fish_source samplemind > ~/.config/fish/completions/samplemind.fish
```

#### PowerShell

```powershell
# Add to $PROFILE
Register-ArgumentCompleter -Native -CommandName samplemind -ScriptBlock {
    param($commandName, $wordToComplete, $cursorPosition)
    $env:_SAMPLEMIND_COMPLETE = "powershell_complete"
    samplemind | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
    $env:_SAMPLEMIND_COMPLETE = ""
}
```

### Supported Audio Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| WAV | `.wav` | ✓ | ✓ | Recommended for quality |
| MP3 | `.mp3` | ✓ | ✓ | Lossy compression |
| FLAC | `.flac` | ✓ | ✓ | Lossless compression |
| OGG | `.ogg` | ✓ | ✓ | Open format |
| AIFF | `.aiff` | ✓ | ✓ | Apple format |
| M4A | `.m4a` | ✓ | ✓ | AAC container |

### Analysis Levels

| Level | Speed | Features | Use Case |
|-------|-------|----------|----------|
| `BASIC` | <1s | BPM, key, duration | Quick preview |
| `STANDARD` | 2-5s | + genre, mood, chroma | General use |
| `DETAILED` | 5-15s | + spectral, harmonic/percussive | Professional |
| `PROFESSIONAL` | 15-30s | + ML features, forensics | Production |

### Quality Presets (Stem Separation)

| Preset | Model | Shifts | Overlap | Speed | Quality |
|--------|-------|--------|---------|-------|---------|
| `fast` | mdx | 1 | 0.1 | ~30s/min | Good |
| `standard` | mdx_extra | 1 | 0.25 | ~60s/min | Better |
| `high` | mdx_extra | 5 | 0.5 | ~180s/min | Best |

---

*Generated by SampleMind AI v2.1.0-beta*
