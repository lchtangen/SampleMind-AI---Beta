# Ableton Live Max Device Specification

**Project:** SampleMind AI - Ableton Live Integration
**Component:** Max for Live Device Interface
**Version:** 1.0.0-spec
**Status:** Design Specification (Implementation Pending Max/MSP)
**Date:** February 3, 2026

---

## Overview

The SampleMind AI Max Device is a Max for Live instrument that provides real-time audio analysis and intelligent sample recommendations directly within Ableton Live. It communicates with the Python backend REST API to deliver professional-grade music production features.

**Requirements:**
- Max 8.0 or later
- Max for Live (installed and enabled in Ableton Live)
- Python backend running (see `python_backend.py`)
- Network connectivity to localhost:8001

---

## Architecture

### Component Hierarchy

```
SampleMind.maxpat (Main Device)
│
├─ UI Layer
│  ├─ Sample Browser Pane
│  ├─ Analysis Display Pane
│  ├─ Project Sync Pane
│  ├─ MIDI Mapping Pane
│  └─ Settings Pane
│
├─ Communication Layer
│  └─ communication.js (JavaScript bridge)
│
├─ Data Processing Layer
│  ├─ Analysis Result Parser
│  ├─ MIDI Generator
│  └─ Recommendation Engine
│
└─ Ableton Integration Layer
   ├─ Live API Connection
   ├─ Track Selection Handler
   └─ MIDI Output Router
```

### Data Flow

```
Ableton Live Session
        ↓
   Max Device
        ↓
JavaScript (communication.js)
        ↓
HTTP Request
        ↓
Python Backend (FastAPI)
        ↓
SampleMind AI Core
        ↓
Analysis Results
        ↓
JSON Response
        ↓
JavaScript Parser
        ↓
Max Objects (display, store)
        ↓
Ableton Live UI Update
```

---

## User Interface Layout

### Main Window (1000px width × 600px height)

```
┌─────────────────────────────────────────────────────────────────────┐
│ SampleMind AI v1.0.0                                    [_][≡][✕]  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┬────────────────────────────────────────┐ │
│  │  SAMPLE BROWSER      │      ANALYSIS RESULTS                 │ │
│  │  ─────────────────── │      ──────────────────────────────  │ │
│  │                      │                                        │ │
│  │  🔍 Browse Samples   │      BPM: 120 ±2                     │ │
│  │  📁 Recent Files     │      Key: C Major                     │ │
│  │  [        Browse ]   │      Genre: Electronic                │ │
│  │                      │      Mood: Energetic                  │ │
│  │  Loaded Sample:      │      Energy: 78%                      │ │
│  │  drum_loop_120.wav   │      Confidence: 92%                  │ │
│  │                      │                                        │ │
│  │  [Load Sample] [✓]   │      ┌──────────────────────────────┐ │ │
│  │                      │      │ Analysis in Progress...   ░░  │ │ │
│  │                      │      └──────────────────────────────┘ │ │
│  │                      │                                        │ │
│  └──────────────────────┴────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────┬────────────────────────────────────────┐ │
│  │  PROJECT SYNC        │      MIDI MAPPING                     │ │
│  │  ─────────────────── │      ──────────────────────────────  │ │
│  │                      │                                        │ │
│  │  Project BPM: [120]  │      Extract Type: [Melody ▼]        │ │
│  │  Project Key: [C ▼]  │      [Generate MIDI]                 │ │
│  │  [Find Matches]      │                                        │ │
│  │                      │      Note Range: C2 to C6             │ │
│  │  Matching Samples:   │      Velocity: 100%                   │ │
│  │  ────────────────    │      [Apply to Track]                │ │
│  │  1. kick_c_120.wav   │                                        │ │
│  │  2. bass_c_120.wav   │                                        │ │
│  │  3. synth_c_120.wav  │                                        │ │
│  │                      │                                        │ │
│  └──────────────────────┴────────────────────────────────────────┘ │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Status: Ready      Backend: ✓ Connected      Settings [⚙]      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Pane Specifications

### 1. Sample Browser Pane

**Location:** Left side, top half

**Components:**
- **Browse Button**
  - Opens file browser dialog
  - Filters for audio files (.wav, .aif, .mp3, .flac)
  - Returns full file path

- **Recent Files List**
  - Displays last 20 loaded samples
  - Double-click to load
  - Sorted by most recent first
  - Clear button to reset history

- **Current Sample Display**
  - Shows full path of loaded file
  - File size and duration
  - Status: "Ready", "Loading", "Error"

- **Load Button**
  - Sends sample path to backend for analysis
  - Disables until analysis completes
  - Shows spinner during loading

**Max Objects:**
```maxpat
[message]      → [udpsend] (send path to Python)
[prepend open] → [dialog] (file browser)
[textedit]     (display file path)
[button]       (load sample)
```

**Data Received:**
```json
{
  "file_path": "/path/to/sample.wav",
  "file_size": 2048000,
  "duration": 5.2
}
```

### 2. Analysis Display Pane

**Location:** Right side, top half

**Components:**

- **BPM Display**
  - Large number display: "120"
  - Subtitle: "±2 BPM" (confidence margin)
  - Color: Green (confident) to Red (uncertain)
  - Tap Tempo button (manual correction)

- **Key Display**
  - Text: "C Major" or "A Minor"
  - Icon showing key wheel position
  - Camelot wheel position (if applicable)

- **Genre Display**
  - Primary: "Electronic"
  - Secondary: "Techno" (optional)
  - Icon for genre type

- **Mood Display**
  - Text: "Energetic", "Dark", "Uplifting", etc.
  - Emoji: 🎉 ⚡ 😈 😌 🚀
  - Multiple mood tags possible

- **Energy Level**
  - Horizontal slider: 0-100%
  - Visual bar representation
  - Numerical percentage

- **Confidence Score**
  - Percentage: "92%"
  - Color-coded: Green ≥80%, Yellow 60-80%, Red <60%
  - Tooltip shows which models were used

- **Analysis Progress**
  - Status text: "Analyzing audio...", "Extracting features...", "Complete"
  - Progress bar: 0-100%
  - Cancel button (stops current analysis)

**Max Objects:**
```maxpat
[number]       → (display BPM, energy, confidence)
[textedit]     → (display key, genre, mood)
[slider]       → (energy level visualization)
[fpic]         → (display analysis icons/colors)
[progressbar]  → (show analysis progress)
```

**Data Received:**
```json
{
  "tempo_bpm": 120.0,
  "tempo_confidence": 0.95,
  "key": "C Major",
  "primary_genre": "Electronic",
  "secondary_genre": "Techno",
  "mood": "Energetic",
  "mood_tags": ["rhythmic", "percussive", "bright"],
  "energy_level": 0.78,
  "confidence_score": 0.92
}
```

### 3. Project Sync Pane

**Location:** Left side, bottom half

**Components:**

- **Project Settings**
  - BPM Dropdown: [120 ▼] - populated with common tempos
  - Key Dropdown: [C ▼] - populated with all keys
  - Manual input fields for custom values

- **Find Matches Button**
  - Queries backend with project settings
  - Disables during search
  - Shows result count when complete

- **Results List**
  - Scrollable list of matching samples
  - Display format: "filename | BPM | Key | Genre"
  - Sort by: Similarity, BPM, Key
  - Double-click to load

- **Similarity Indicators**
  - Visual match percentage (0-100%)
  - Color coding (green = high match)
  - Star rating (1-5 stars)

**Max Objects:**
```maxpat
[number]       → (BPM input)
[textedit]     → (key selector)
[button]       → (find matches)
[umenu]        → (dropdown for presets)
[textedit]     → (results display list)
[mouse events] → (handle clicks on results)
```

**Data Sent:**
```json
{
  "project_bpm": 120,
  "project_key": "C Major",
  "limit": 10
}
```

**Data Received:**
```json
{
  "matches": [
    {
      "file_path": "/path/to/kick.wav",
      "filename": "kick_c_120.wav",
      "tempo_bpm": 120.0,
      "key": "C Major",
      "similarity": 0.95,
      "genre": "Electronic"
    }
  ],
  "match_count": 12
}
```

### 4. MIDI Mapping Pane

**Location:** Right side, bottom half

**Components:**

- **Extraction Type Dropdown**
  - Options: "Melody", "Harmony", "Drums", "Bass Line"
  - Visual icon for each type
  - Description tooltip

- **Note Range Selector**
  - Min Note: [C2 ▼]
  - Max Note: [C6 ▼]
  - Visual piano keyboard representation
  - Default range: C2-C6

- **Velocity Control**
  - Slider: 0-127
  - Label: "Velocity: 100%"
  - Options: Fixed, Humanized, Dynamic

- **Quantization**
  - Dropdown: "Off", "1/4", "1/8", "1/16"
  - Lock to project tempo checkbox
  - Swing amount slider (0-100%)

- **Generate Button**
  - Sends request to backend
  - Progress indicator
  - Status message: "Generating MIDI..."

- **Apply to Track Button**
  - Creates new MIDI track in Ableton
  - Inserts generated notes into clip
  - Auto-selects generated track

- **Export Button**
  - Exports MIDI file (.mid)
  - File dialog for save location
  - Success/error notification

**Max Objects:**
```maxpat
[menu]         → (extraction type)
[number]       → (note range min/max)
[slider]       → (velocity, quantization, swing)
[button]       → (generate, apply, export)
[dropdown]     → (quantization options)
```

**Data Sent:**
```json
{
  "file_path": "/path/to/sample.wav",
  "extraction_type": "melody",
  "note_range": {
    "min": "C2",
    "max": "C6"
  },
  "velocity": 100,
  "quantization": "1/16",
  "swing": 0.0
}
```

**Data Received:**
```json
{
  "midi_file": "/tmp/generated_melody.mid",
  "midi_data": "base64_encoded_midi",
  "notes_count": 24,
  "duration": 4.0,
  "success": true
}
```

### 5. Settings Pane

**Location:** Overlay dialog or separate tab

**Components:**

- **Backend Connection**
  - Host: [localhost ▼]
  - Port: [8001]
  - Status: "✓ Connected" or "✗ Disconnected"
  - Test Connection button
  - Auto-reconnect checkbox

- **Analysis Settings**
  - Level: [STANDARD ▼]
    - Options: BASIC, STANDARD, DETAILED, PROFESSIONAL
  - Cache enabled checkbox
  - Auto-sync checkbox

- **UI Settings**
  - Theme: [Dark ▼]
  - Font size: [12pt ▼]
  - Show tips checkbox
  - Sound notifications checkbox

- **Storage**
  - Library path: [/path/to/library]
  - Browse button
  - Cache size indicator
  - Clear cache button

- **About**
  - Version: SampleMind AI v1.0.0
  - Backend version display
  - License information
  - Links to docs/support

**Max Objects:**
```maxpat
[textedit]     → (host, port, library path)
[menu]         → (analysis level, theme)
[checkbox]     → (various toggles)
[button]       → (test connection, browse, clear)
```

---

## Message Protocol

### Incoming Messages (from communication.js)

**Format:** Max messages received via `samplemind_message` handler

```
samplemind_message analysis_complete BPM Key Genre Mood Energy Confidence

samplemind_message project_sync_complete filename BPM Key similarity

samplemind_message midi_generated success midi_file notes_count

samplemind_message error error_type error_message

samplemind_message backend_status connected version
```

### Outgoing Messages (to communication.js)

```
analyze_sample /path/to/file.wav

find_matches project_bpm project_key

generate_midi /path/to/file.wav extraction_type note_min note_max

test_backend

get_library_stats
```

### JavaScript Bridge Methods

```javascript
// In communication.js
class SampleMindAPIClient {
  // Already implemented - see plugins/ableton/communication.js

  // Called from Max
  async analyzeAudio(filePath)
  async findSimilarSamples(filePath, limit)
  async getProjectSyncRecommendations(bpm, key, limit)
  async generateMIDI(filePath, extractionType, options)
  async checkHealth()
  async getLibraryStats()
}

// Max message handler
async function samplemind_message(msg_type, ...args) {
  const client = new SampleMindAPIClient()

  switch(msg_type) {
    case 'analyze':
      return await client.analyzeAudio(args[0])
    case 'sync':
      return await client.getProjectSyncRecommendations(args[0], args[1])
    case 'midi':
      return await client.generateMIDI(args[0], args[1])
    // ... etc
  }
}
```

---

## Integration Points

### Ableton Live API Integration

```maxpat
[live.thisdevice]  → Get this device
[live.track]       → Get current track
[live.bank]        → Get device parameters
[live.observer]    → Watch for parameter changes
[live.menu]        → Trigger Ableton menus
```

**Example: Get current BPM**
```maxpat
[live.thisdevice]
[live.observer tempo]
→ Update UI when tempo changes
```

**Example: Create MIDI track and insert notes**
```maxpat
[live.thistrack]
[live.clip]
[insert_note velocity pitch duration]
→ Add generated notes to clip
```

### Audio File Handling

**Supported Formats:**
- WAV (.wav)
- AIFF (.aif, .aiff)
- MP3 (.mp3)
- FLAC (.flac)
- AAC (.m4a)

**File Dialog:**
```maxpat
[prepend read]
[dialog]
→ Get file from user
→ Send to backend
```

### MIDI Output

**Route generated MIDI:**
```maxpat
[midiformat]  → Format MIDI data
[makenote]    → Create note on/off pairs
[noteout]     → Send to track
```

---

## State Management

### Device State Variables

```json
{
  "current_sample": {
    "path": "/path/to/file.wav",
    "duration": 5.2,
    "loaded_at": 1707024000
  },
  "last_analysis": {
    "tempo_bpm": 120.0,
    "key": "C Major",
    "genre": "Electronic",
    "mood": "Energetic",
    "energy": 0.78,
    "confidence": 0.92
  },
  "project_settings": {
    "bpm": 120,
    "key": "C Major"
  },
  "ui_state": {
    "active_tab": "analysis",
    "show_settings": false,
    "last_backend_check": 1707024000
  }
}
```

### State Persistence

Save/load device state in Ableton:
```maxpat
[pattrstorage @autorename 1]
→ Saves all object states
→ Restored when loading patch
```

---

## Error Handling

### Error Types

**Backend Errors:**
- Connection timeout: "Could not connect to backend. Is python_backend.py running?"
- Invalid file: "Audio file not found or unsupported format"
- Analysis failed: "Analysis failed. Try with a shorter sample"
- API error: "Backend error: [specific error message]"

**User Errors:**
- No sample loaded: "Load a sample first"
- No matches found: "No samples match project settings"
- Invalid MIDI range: "Note range invalid. Max > Min required"

### Error Display

```maxpat
[textedit @readonly 1]  → Display error messages
[bg @color red]        → Color-coded notifications
[text "✗ Error"]       → Status indicator icon
```

**Error Recovery:**
- Auto-retry with exponential backoff (see communication.js)
- Retry button for manual retries
- Suggestion for resolution

---

## Performance Considerations

### Optimization Guidelines

1. **Responsive UI**
   - Analysis runs in background thread
   - UI remains responsive during operations
   - Progress indicator prevents user frustration

2. **Caching**
   - Cache analysis results (see communication.js)
   - Avoid redundant API calls
   - Clear cache on manual refresh

3. **Network**
   - Timeout: 30 seconds for API calls
   - Retry: 3 attempts with exponential backoff
   - Queue requests during network downtime

4. **Memory**
   - Don't load entire audio files into memory
   - Use file paths for backend processing
   - Stream MIDI data instead of buffering

### Performance Targets

- UI response time: <50ms
- File load: <1 second
- Analysis display: <2 seconds (from backend response)
- MIDI generation: 2-5 seconds
- UI thread blocking: Never

---

## Testing Strategy

### Unit Tests (in Max)

```maxpat
Test: UI Element Creation
  → Create each UI element (button, slider, etc.)
  → Verify appearance and function

Test: Message Passing
  → Send messages to JavaScript
  → Verify correct routing

Test: State Management
  → Change state values
  → Verify persistence
```

### Integration Tests

```
Test: Full Workflow
  1. Load sample → Verify analysis display
  2. Set project settings → Verify matches found
  3. Generate MIDI → Verify track created
  4. Backend offline → Verify error handling
```

### User Acceptance Tests

- [ ] Sample loading and analysis works in Ableton
- [ ] All analysis fields display correctly
- [ ] Project sync finds matching samples
- [ ] MIDI generation creates playable notes
- [ ] Settings persist between sessions
- [ ] Error messages are helpful
- [ ] UI is responsive (no freezing)
- [ ] Visual design is professional

---

## Implementation Checklist

### Phase 1: Core UI (Days 1-2)

- [ ] Create main patcher file: `SampleMind.maxpat`
- [ ] Implement Sample Browser pane
- [ ] Implement Analysis Display pane
- [ ] Setup communication.js integration
- [ ] Connect to Python backend

### Phase 2: Features (Days 2-3)

- [ ] Implement Project Sync pane
- [ ] Implement MIDI Mapping pane
- [ ] Add Ableton Live API integration
- [ ] Create MIDI track insertion logic
- [ ] Add state persistence

### Phase 3: Polish (Day 4)

- [ ] Implement Settings pane
- [ ] Add error handling throughout
- [ ] Optimize performance
- [ ] Create user documentation
- [ ] Test all workflows

### Phase 4: Testing & Deployment (Day 5)

- [ ] Cross-platform testing (macOS, Windows)
- [ ] Ableton Live compatibility testing
- [ ] User acceptance testing
- [ ] Create installation package
- [ ] Prepare release notes

---

## File Structure

```
plugins/ableton/
├── SampleMind.maxpat          (Main device - to be created)
├── midi_mapper.maxpat         (MIDI configuration - to be created)
├── communication.js           (✅ Already created)
├── python_backend.py          (✅ Already created)
├── README.md                  (✅ Already created)
├── MAX_DEVICE_SPECIFICATION.md (This file)
└── max_ui_resources/
    ├── icons/                 (UI icons)
    ├── presets/               (Default settings)
    └── help/                  (Help files)
```

---

## Deployment

### Package Creation

1. **Create amxd file**
   - Open SampleMind.maxpat in Max
   - File → Save As → Format: "Max Compiled"
   - Output: `SampleMind.amxd`

2. **Verify Installation**
   ```bash
   ls ~/Music/Ableton\ User\ Library/Presets/Instruments/Max\ Instrument/SampleMind.amxd
   ```

3. **Test in Ableton**
   - Create MIDI track
   - Add Max Instrument
   - Select SampleMind device
   - Load sample and test

### Distribution

- Package SampleMind.amxd with communication.js and python_backend.py
- Include README.md and installation guide
- Create installer using `plugins/installer.py`

---

## Future Enhancements

### Planned Features

1. **Batch Processing**
   - Analyze multiple files at once
   - Generate MIDI for entire folder
   - Bulk project sync

2. **Advanced MIDI**
   - Polyphonic extraction
   - MIDI humanization controls
   - Velocity mapping options

3. **Visualization**
   - Waveform display with markers
   - Spectrogram visualization
   - Key/BPM confidence meters

4. **Collaboration**
   - Share analysis results
   - Collaborative MIDI editing
   - Cloud library sync

5. **Learning**
   - Custom model training
   - Genre/mood fine-tuning
   - User preference learning

---

## Support & Documentation

### Resources for Developers

- Max for Live documentation: https://www.ableton.com/en/live/max-for-live/
- Max/MSP tutorials: https://www.youtube.com/user/AbletonLive
- Python backend API: See `plugins/ableton/README.md`
- JavaScript bridge: See `plugins/ableton/communication.js`

### Getting Help

- Check troubleshooting section in README.md
- Review error messages in device
- Check Python backend logs
- Consult Max for Live documentation

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 1.0.0-spec | 2026-02-03 | Design Specification | Complete specification ready for implementation |

---

## Conclusion

This specification provides a comprehensive blueprint for implementing the SampleMind AI Max device. The design balances feature richness with user experience, providing professional music production tools within Ableton Live's familiar interface.

**Implementation Status:** ✅ Specification Complete
**Ready For:** Max/MSP Developer Implementation
**Est. Dev Time:** 4-5 days for experienced Max developer

---

**Document Status:** ✅ SPECIFICATION COMPLETE
**Next Step:** Hand to Max/MSP developer for implementation
**Date:** February 3, 2026

