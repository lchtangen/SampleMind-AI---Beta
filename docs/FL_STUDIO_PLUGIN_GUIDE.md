# 🎹 SampleMind AI - FL Studio Plugin Integration Guide

**Version:** 1.0.0 Beta  
**Last Updated:** 2025-10-05  
**Status:** Ready for Beta Testing

---

## 📋 Overview

This guide details how to integrate SampleMind AI with FL Studio for seamless workflow integration. The plugin provides real-time audio analysis, AI-powered suggestions, and direct integration with the web interface.

---

## 🎯 Features

### Core Capabilities
- ✅ **Real-time Audio Analysis** - Analyze tracks as you produce
- ✅ **AI-Powered Suggestions** - Get production tips in real-time
- ✅ **Automatic Stem Separation** - Extract stems directly in FL Studio
- ✅ **Sample Library Integration** - Browse and preview samples
- ✅ **Genre & Mood Detection** - Automatic track classification
- ✅ **BPM & Key Detection** - Sync with your project tempo

---

## 🔧 Installation Methods

### Method 1: VST3 Plugin (Recommended)
```bash
# Windows
1. Download SampleMind-AI-VST3.zip
2. Extract to: C:\Program Files\Common Files\VST3\
3. Restart FL Studio
4. Find in: Mixer → VST3 → SampleMind AI

# macOS
1. Download SampleMind-AI-VST3.pkg
2. Install to: /Library/Audio/Plug-Ins/VST3/
3. Restart FL Studio
4. Find in: Mixer → VST3 → SampleMind AI
```

### Method 2: FL Studio Native Plugin
```bash
# Windows
1. Download SampleMind-FL-Plugin.zip
2. Extract to: C:\Program Files\Image-Line\FL Studio\Plugins\Fruity\
3. Restart FL Studio
4. Find in: Add → More → SampleMind AI

# macOS
1. Download SampleMind-FL-Plugin.zip
2. Extract to: /Applications/FL Studio.app/Contents/Plugins/Fruity/
3. Restart FL Studio
4. Find in: Add → More → SampleMind AI
```

### Method 3: ReWire Integration
```bash
# Enables full bidirectional audio routing
1. Install SampleMind AI Desktop App
2. Launch FL Studio
3. Go to: Channels → Add one → More → ReWire
4. Select: SampleMind AI
5. Route audio from FL Studio to SampleMind for analysis
```

---

## 🚀 Quick Start

### Basic Workflow

#### 1. Analyze Current Project
```
1. Open your FL Studio project
2. Load SampleMind AI plugin on Master track
3. Click "Analyze Project"
4. View results in plugin window or web interface
```

#### 2. Real-time Analysis
```
1. Enable "Live Mode" in plugin
2. Play your track
3. See real-time metrics:
   - Spectral analysis
   - Energy levels
   - Frequency distribution
   - Dynamic range
```

#### 3. AI Suggestions
```
1. Select track or pattern
2. Click "Get AI Suggestions"
3. Review recommendations:
   - EQ adjustments
   - Compression settings
   - Effect suggestions
   - Arrangement tips
```

---

## 🎚️ Plugin Interface

### Main Window

```
┌─────────────────────────────────────────────────┐
│  SampleMind AI v1.0                    [_][□][×]│
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────────────┐ │
│  │  ANALYSIS   │  │   REAL-TIME METRICS      │ │
│  │             │  │                          │ │
│  │  [Analyze]  │  │   Tempo: 128 BPM        │ │
│  │  [Live]     │  │   Key: A Minor          │ │
│  │  [Suggest]  │  │   Energy: 78%           │ │
│  │             │  │   Spectral: 2.4kHz      │ │
│  └─────────────┘  └──────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │        WAVEFORM VISUALIZATION             │ │
│  │  ▁▂▃▅▆▇█▇▆▅▃▂▁▁▂▃▅▆▇█▇▆▅▃▂▁             │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  [Settings]  [Help]  [Open Web Interface]      │
└─────────────────────────────────────────────────┘
```

### Tab Structure
1. **Analysis** - Track analysis and metrics
2. **Suggestions** - AI-powered production tips
3. **Library** - Browse sample library
4. **Generate** - AI music generation
5. **Settings** - Plugin configuration

---

## ⚙️ Configuration

### Audio Routing

#### Input Configuration
```ini
# config/plugin-settings.ini

[Audio]
InputMode=Master          # Master, Track, Send
SampleRate=48000
BufferSize=512
BitDepth=24

[Analysis]
RealtimeEnabled=true
AnalysisDepth=high        # low, medium, high
UpdateInterval=100        # milliseconds
```

#### Output Configuration
```ini
[Output]
SendToWebInterface=true
SaveAnalysisLocally=true
AutoExportStems=false
```

### API Integration
```ini
[API]
ServerURL=http://localhost:8000
WebSocketURL=ws://localhost:8000/stream
APIKey=your_api_key_here
Timeout=30000
```

---

## 🎛️ Advanced Features

### 1. Stem Separation

```python
# In FL Studio Python Script
import samplemind

# Separate current track
stems = samplemind.separate_stems(
    track_id=mixer.trackNumber(),
    quality='high',
    export_path='C:/Stems/'
)

# Creates:
# - vocals.wav
# - drums.wav
# - bass.wav
# - other.wav
```

### 2. Automation Integration

```python
# Link SampleMind parameters to FL Studio automation
import samplemind.automation as auto

# Map AI energy detection to filter cutoff
auto.map_parameter(
    source='energy_level',
    target='Filter.Cutoff',
    range=(200, 20000),
    smoothing=0.5
)
```

### 3. MIDI Generation

```python
# Generate MIDI from audio
midi = samplemind.audio_to_midi(
    audio_file='pattern.wav',
    instrument='piano',
    quantize=True,
    tempo=project.tempo
)

# Import to FL Studio
midi.export_to_fl_studio()
```

---

## 🔌 API Reference

### Plugin Methods

#### Initialize
```javascript
samplemind.init({
  apiKey: 'your_key',
  serverUrl: 'http://localhost:8000',
  realtimeEnabled: true
});
```

#### Analyze Track
```javascript
const analysis = await samplemind.analyzeTrack({
  trackId: mixer.trackNumber(),
  includeSpectral: true,
  includeHarmonic: true,
  exportFormat: 'json'
});
```

#### Get Suggestions
```javascript
const suggestions = await samplemind.getSuggestions({
  trackId: mixer.trackNumber(),
  aiProvider: 'anthropic',  // or 'openai', 'google'
  suggestionTypes: ['mixing', 'arrangement', 'effects']
});
```

#### Separate Stems
```javascript
const stems = await samplemind.separateStems({
  audioFile: 'track.wav',
  quality: 'high',
  exportPath: 'C:/Stems/',
  formats: ['wav', 'mp3']
});
```

---

## 🎹 Keyboard Shortcuts

### Windows
```
Ctrl + Shift + A    - Analyze current track
Ctrl + Shift + L    - Toggle live mode
Ctrl + Shift + S    - Get AI suggestions
Ctrl + Shift + W    - Open web interface
Ctrl + Shift + E    - Export stems
```

### macOS
```
Cmd + Shift + A     - Analyze current track
Cmd + Shift + L     - Toggle live mode
Cmd + Shift + S     - Get AI suggestions
Cmd + Shift + W     - Open web interface
Cmd + Shift + E     - Export stems
```

---

## 🐛 Troubleshooting

### Common Issues

#### Plugin Not Showing in FL Studio
```
1. Verify installation path is correct
2. Check FL Studio version (21.0+ required)
3. Rescan plugins: Options → File Settings → Manage Plugins
4. Check plugin is not blocked by antivirus
```

#### Audio Routing Issues
```
1. Set plugin on Master or specific track
2. Verify audio input is enabled
3. Check sample rate matches (44.1/48 kHz)
4. Increase buffer size if crackling occurs
```

#### API Connection Failures
```
1. Verify backend server is running:
   python -m samplemind.server

2. Check firewall settings
3. Verify API key in settings
4. Test connection: http://localhost:8000/health
```

#### High CPU Usage
```
1. Reduce analysis depth in settings
2. Increase update interval (100ms → 200ms)
3. Disable real-time mode when not needed
4. Close web interface when not in use
```

---

## 📊 Performance Optimization

### Recommended Settings

#### For Real-time Production
```ini
[Performance]
AnalysisDepth=medium
UpdateInterval=200
BufferSize=512
EnableGPU=true
```

#### For Final Analysis
```ini
[Performance]
AnalysisDepth=high
UpdateInterval=50
BufferSize=256
EnableGPU=true
```

#### For Low-end Systems
```ini
[Performance]
AnalysisDepth=low
UpdateInterval=500
BufferSize=1024
EnableGPU=false
```

---

## 🔗 Integration Examples

### Example 1: Automatic Mastering Chain

```python
import samplemind

# Analyze track
analysis = samplemind.analyze()

# Get AI suggestions
suggestions = samplemind.get_suggestions()

# Apply recommended effects
for effect in suggestions['effects']:
    mixer.addEffect(effect['type'], effect['params'])
```

### Example 2: Genre-based Template

```python
# Detect genre
genre = samplemind.detect_genre()

# Load appropriate template
if genre == 'edm':
    project.loadTemplate('EDM_Master.flp')
elif genre == 'hip-hop':
    project.loadTemplate('HipHop_Master.flp')
```

### Example 3: Collaborative Production

```python
# Share analysis with collaborators
analysis_url = samplemind.share_analysis(
    track_id=current_track,
    expires_in='7d'
)

# Collaborators can view at: analysis_url
```

---

## 📱 Mobile Companion App

### iOS/Android Integration
```
1. Install SampleMind mobile app
2. Scan QR code in plugin settings
3. Control plugin from phone/tablet:
   - Start/stop analysis
   - View metrics
   - Apply suggestions
   - Browse samples
```

---

## 🚀 Future Features (Roadmap)

### Coming Soon
- [ ] **MIDI FX Plugin** - AI-powered MIDI effects
- [ ] **Automation Recorder** - Record AI suggestions as automation
- [ ] **Preset Manager** - Save and share analysis presets
- [ ] **Cloud Sync** - Sync settings across devices
- [ ] **Collaboration Tools** - Real-time co-production
- [ ] **VST2 Support** - Legacy compatibility

---

## 📚 Additional Resources

### Documentation
- [Full API Documentation](../docs/api/README.md)
- [Video Tutorials](https://youtube.com/@samplemind-ai)
- [Community Forum](https://community.samplemind.ai)

### Support
- Email: support@samplemind.ai
- Discord: discord.gg/samplemind
- GitHub Issues: github.com/samplemind-ai/issues

---

## 📄 License & Credits

- **License:** MIT License
- **Copyright:** © 2025 SampleMind AI
- **FL Studio Version:** 21.0+
- **Python Version:** 3.11+

---

## 🎉 Getting Started Checklist

- [ ] Install plugin to correct directory
- [ ] Restart FL Studio
- [ ] Verify plugin appears in list
- [ ] Load on Master track
- [ ] Run test analysis
- [ ] Configure API settings
- [ ] Test web interface connection
- [ ] Explore AI suggestions
- [ ] Join community Discord
- [ ] Check out video tutorials

---

**Ready to revolutionize your music production workflow!** 🎵🚀