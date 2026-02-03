# SampleMind AI - Ableton Live Plugin

**Status**: In Development (Phase 13.2.2)
**Compatibility**: Ableton Live 12+ with Max for Live
**Python Backend**: FastAPI REST API

---

## Overview

SampleMind AI integrates with Ableton Live through a Max for Live device, providing:

- **Real-time Audio Analysis** - BPM, key, genre, mood detection
- **Intelligent Sample Browser** - Search and organize your library
- **Project Sync** - Find samples that match your project's key/tempo
- **MIDI Generation** - Extract melody, chords, drums, bass from audio
- **Semantic Search** - Find similar samples by sound characteristics

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ableton Live Session                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Max for Live Device                             │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │                                                           │  │
│  │  [Sample Browser] [Analysis Display] [MIDI Mapper]      │  │
│  │                                                           │  │
│  │          ↓           ↓           ↓                        │  │
│  │  ┌────────────────────────────────────┐                 │  │
│  │  │  JavaScript Communication Layer   │                 │  │
│  │  │  (communication.js)                │                 │  │
│  │  └────────────────────────────────────┘                 │  │
│  │                     ↓                                    │  │
│  │  ┌────────────────────────────────────┐                 │  │
│  │  │  HTTP REST API Client              │                 │  │
│  │  └────────────────────────────────────┘                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         ↓                                       │
└─────────────────────────────────────────────────────────────────┘
                         ↓
        ┌─────────────────────────────────────┐
        │  SampleMind Python Backend API      │
        │  (python_backend.py)                │
        │  http://localhost:8001              │
        └─────────────────────────────────────┘
                         ↓
        ┌─────────────────────────────────────┐
        │  SampleMind AI Core                 │
        │  • AudioEngine                      │
        │  • MIDIGenerator                    │
        │  • ChromaDB Library                 │
        └─────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites

1. **Ableton Live 12+** with Max for Live
2. **Python 3.11+** with SampleMind AI installed
3. **FastAPI** and dependencies

### Step 1: Install Backend Dependencies

```bash
pip install fastapi uvicorn samplemind-ai
```

### Step 2: Start Backend Server

```bash
python plugins/ableton/python_backend.py
```

Output should show:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### Step 3: Install Max Device

1. Copy `SampleMind.amxd` to Ableton Max for Live devices:
   - **macOS**: `~/Music/Ableton User Library/Presets/Instruments/Max Instrument/`
   - **Windows**: `%APPDATA%\Ableton\User Library\Presets\Instruments\Max Instrument\`
   - **Linux**: `~/.Ableton/User Library/Presets/Instruments/Max Instrument/`

2. Copy `communication.js` to same location

3. Restart Ableton Live

### Step 4: Add Device to Session

1. Open Ableton Live
2. Create MIDI/Audio track
3. Click "+" next to track effects
4. Select "Max Instrument" → "SampleMind AI"
5. Device will attempt to connect to backend

---

## Features

### Sample Browser

**Location**: Browser pane in device interface

**Features**:
- File picker for sample selection
- Recent files list (last 20)
- Search by keyword
- Filter by key/BPM/genre

**Usage**:
```
1. Click "Browse" button
2. Select audio file
3. Analysis results display in real-time
```

### Analysis Display

**Shows for Current Sample**:
- **BPM**: Detected tempo with ±2 accuracy
- **Key**: Musical key (e.g., "C Major", "Am")
- **Genre**: Primary genre classification
- **Mood**: Emotional character (energetic, dark, etc.)
- **Energy**: 0-100% energy level
- **Confidence**: Analysis confidence score

**Auto-Updates**: When sample changes or analysis completes

### Project Sync

**Purpose**: Find samples matching your project's key and tempo

**How to Use**:
1. Select project BPM and key from dropdowns
2. Click "Find Matches"
3. Browser shows matching samples sorted by similarity
4. Drag samples to tracks

**Auto-Detection** (optional):
- Enable "Auto Sync" to use current project settings

### MIDI Generation

**Supported Extraction Types**:
1. **Melody** - Main melodic line
2. **Harmony** - Chord progression
3. **Drums** - Drum pattern
4. **Bass Line** - Bass note sequence

**How to Use**:
1. Select extraction type from dropdown
2. Click "Generate MIDI"
3. MIDI file creates in project folder
4. Drag to MIDI track or use in sampler

**Output**: Standard MIDI file (.mid)

### MIDI Mapping

**Map Audio to MIDI**:
- Configure note assignments for sample triggers
- Set CC (control change) mappings for parameters
- Velocity sensitivity control
- Modulation wheel mapping

**File**: `midi_mapper.maxpat`

---

## API Endpoints

All endpoints return JSON responses.

### Health & Status

```
GET /health
GET /status
GET /api/info
```

### Audio Analysis

```
POST /api/analyze
{
  "file_path": "/path/to/audio.wav",
  "analysis_level": "STANDARD"  # BASIC, STANDARD, DETAILED, PROFESSIONAL
}

POST /api/analyze/batch
(multipart file upload for multiple files)
```

### Search & Discovery

```
POST /api/similar
{
  "file_path": "/path/to/reference.wav",
  "limit": 10
}

GET /api/search?query=<query>&limit=10

POST /api/project-sync
{
  "project_bpm": 120,
  "project_key": "C Major",
  "limit": 10
}
```

### MIDI Generation

```
POST /api/generate-midi
{
  "file_path": "/path/to/audio.wav",
  "extraction_type": "melody"  # melody, harmony, drums, bass_line
}

GET /api/generate-midi/types
```

### Library Management

```
GET /api/library/stats

POST /api/library/add
(multipart file upload)

GET /api/project-sync/available-keys
```

---

## Configuration

### Backend Settings

**File**: `python_backend.py`

```python
# API Server
host = "127.0.0.1"
port = 8001

# Request timeout
timeout = 30  # seconds

# Batch limits
max_batch_size = 50
analysis_chunk_size = 3
```

### Device Settings

**File**: `SampleMind.amxd`

Within Max patcher:
- API endpoint URL (default: localhost:8001)
- Analysis level (BASIC/STANDARD/DETAILED/PROFESSIONAL)
- Cache enabled (yes/no)
- Auto-sync enabled (yes/no)

---

## Troubleshooting

### Backend Not Responding

**Error**: "Failed to connect to backend"

**Solution**:
1. Ensure Python backend is running
2. Check backend is listening: `netstat -an | grep 8001`
3. Verify firewall allows localhost:8001
4. Check Python error output for exceptions

### Analysis Taking Too Long

**Error**: "Analysis timeout"

**Solution**:
1. Reduce analysis level (BASIC instead of PROFESSIONAL)
2. Disable auto-sync if enabled
3. Check system CPU/RAM usage
4. Increase timeout in settings

### MIDI Generation Fails

**Error**: "Failed to generate MIDI"

**Solution**:
1. Verify audio file is readable
2. Try different extraction type
3. Check librosa/basic-pitch installation
4. Review backend logs

### Device Not Found in Live

**Error**: "Max Instrument - SampleMind AI missing"

**Solution**:
1. Verify Max for Live is installed and enabled
2. Copy `SampleMind.amxd` to correct Presets folder
3. Restart Ableton Live
4. Check Ableton preferences → Max for Live

---

## Development

### File Structure

```
plugins/ableton/
├── README.md                    # This file
├── python_backend.py            # FastAPI server
├── communication.js             # Max<->API bridge
├── midi_mapper.maxpat          # MIDI configuration
├── SampleMind.amxd             # Max device (generated)
└── build/
    ├── compile.sh              # Build script
    └── SampleMind.amxd         # Compiled device
```

### Building the Device

```bash
cd plugins/ableton
bash build/compile.sh
```

**Requirements**:
- Max 8.0+
- Max SDK (if building from source)

### Testing Backend Independently

```bash
# Start backend
python plugins/ableton/python_backend.py

# In another terminal, test endpoint
curl http://localhost:8001/health

# Or use Python
python
>>> from plugins.ableton.python_backend import app
>>> import asyncio
>>> # Run tests...
```

---

## Performance Considerations

### Optimization Tips

1. **Caching**
   - Enable API response caching for repeated requests
   - Clear cache if library changes

2. **Analysis Level**
   - Use BASIC for quick results
   - Use PROFESSIONAL only when needed

3. **Batch Processing**
   - Process multiple samples together
   - Max 50 samples per batch

4. **Network**
   - Ensure stable localhost connection
   - Monitor network latency

### Expected Performance

| Operation | Time |
|-----------|------|
| Health check | <100ms |
| Quick analysis | 500ms - 2s |
| Detailed analysis | 3 - 10s |
| MIDI generation | 2 - 5s |
| Similar search (100 samples) | 1 - 3s |

---

## Limitations & Future Improvements

### Current Limitations
- Single user session per backend instance
- Max device requires Max for Live
- MIDI generation limited to monophonic extraction
- No real-time plugin operation (analysis only)

### Planned Features
- Multi-user support
- Real-time audio processing in tracks
- Polyphonic MIDI extraction
- MIDI velocity mapping
- Crowd-sourced sample library
- Custom AI model training

---

## Support & Contributing

For issues, feature requests, or questions:
1. Check troubleshooting section above
2. Review backend logs
3. Enable debug mode in device
4. Report to: https://github.com/samplemind/samplemind-ai/issues

---

## License

MIT License - See main repository LICENSE file

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-03 | Initial beta release |
| 0.1.0 | 2026-01-15 | Development version |

---

**Generated**: February 3, 2026
**Status**: Production Ready (Beta)
**Last Updated**: February 3, 2026
