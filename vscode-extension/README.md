# SampleMind AI - VSCode Extension

AI-powered audio analysis and sample management directly in Visual Studio Code.

## Features

### ✅ Implemented

- **Audio Analysis** - Analyze audio files with AI-powered detection
- **Sample Browser** - Browse and organize audio samples in tree view
- **Music Generation** - Generate AI music using Google Gemini Lyria
- **Real-time Results** - View analysis results instantly
- **Context Menu Integration** - Right-click audio files to analyze
- **Keyboard Shortcuts** - Quick access to all features
- **Configurable Settings** - Customize API URL, analysis level, and more

### Commands

- `SampleMind: Analyze Audio File` - Analyze selected audio file
- `SampleMind: Open Sample Browser` - Open sample library view
- `SampleMind: Generate AI Music` - Generate music from text prompt
- `SampleMind: Refresh Sample Library` - Reload sample folders
- `SampleMind: Open Settings` - Configure extension settings

## Getting Started

### Prerequisites

- Visual Studio Code 1.85.0 or higher
- SampleMind AI API server running (see main project README)
- Node.js 20+ (for development)

### Installation

#### From VSIX (Recommended)

1. Download the `.vsix` file
2. In VSCode, go to Extensions (Ctrl+Shift+X)
3. Click the `...` menu → "Install from VSIX..."
4. Select the downloaded file

#### From Source

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Package extension
npm run package
```

This creates a `.vsix` file you can install.

### Configuration

1. Open VSCode Settings (Ctrl+,)
2. Search for "SampleMind"
3. Configure the following:

**Required Settings:**
- `samplemind.apiUrl` - API server URL (default: `http://localhost:8000`)

**Optional Settings:**
- `samplemind.sampleFolders` - Directories containing audio samples
- `samplemind.autoAnalyze` - Auto-analyze files when opened
- `samplemind.analysisLevel` - Analysis detail level (BASIC, STANDARD, DETAILED, PROFESSIONAL)
- `samplemind.enableNotifications` - Show completion notifications
- `samplemind.cacheResults` - Cache analysis results

## Usage

### Analyzing Audio Files

#### Method 1: Context Menu
1. Right-click any audio file in the Explorer
2. Select "Analyze Audio File"
3. View results in the SampleMind panel

#### Method 2: Command Palette
1. Open Command Palette (Ctrl+Shift+P)
2. Type "SampleMind: Analyze Audio File"
3. Select the file to analyze

#### Method 3: File Open (if auto-analyze enabled)
- Simply open an audio file
- Analysis runs automatically

### Sample Browser

1. Click the SampleMind icon in the Activity Bar
2. Add sample folders via settings or the welcome screen
3. Browse your audio library in a tree view
4. Analyzed files show tempo and key information

### Generating Music

1. Open Command Palette (Ctrl+Shift+P)
2. Run "SampleMind: Generate AI Music"
3. Enter a text prompt (e.g., "Upbeat electronic music")
4. Select style and mood
5. Wait for generation to complete

## Extension Structure

```
vscode-extension/
├── src/
│   ├── extension.ts              # Main extension entry point
│   ├── commands/                 # Command implementations
│   │   ├── analyzeAudio.ts
│   │   ├── generateMusic.ts
│   │   ├── refreshSamples.ts
│   │   └── openSampleBrowser.ts
│   ├── providers/                # Tree data providers
│   │   ├── SampleExplorerProvider.ts
│   │   └── AnalysisProvider.ts
│   └── utils/
│       └── api.ts                # API client
├── package.json                  # Extension manifest
├── tsconfig.json                 # TypeScript config
└── README.md                     # This file
```

## Tree Views

### Sample Explorer

Displays your audio library:
- 📁 **Folders** - Configured sample directories
- 🎵 **Audio Files** - Shows name, tempo, and key
- 🔍 **Search** - Quick filter

### Analysis Results

Shows analysis data for selected file:
- **File** - File name and path
- **Features** - Musical features
  - Tempo (BPM)
  - Key
  - Energy
  - Spectral Centroid
  - Spectral Rolloff
  - Brightness
  - Onset Strength
  - Beats Detected

## API Integration

The extension communicates with the SampleMind AI API:

### Endpoints Used

```
GET  /api/v1/health
POST /api/v1/audio/analyze
GET  /api/v1/audio/analysis/{id}
POST /api/v1/generate/music
GET  /api/v1/generate/styles
GET  /api/v1/generate/moods
```

### Error Handling

- Connection errors show user-friendly messages
- Retry options for failed operations
- Links to settings for configuration issues

## Development

### Setup

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode (auto-recompile on changes)
npm run watch
```

### Testing

```bash
# Run extension in debug mode
Press F5 in VSCode
```

This opens a new Extension Development Host window with the extension loaded.

### Packaging

```bash
# Create .vsix package
npm run package

# Install locally
code --install-extension samplemind-vscode-0.8.0.vsix
```

### Publishing

```bash
# Publish to VS Code Marketplace
npm run publish
```

Requires:
- Visual Studio Marketplace publisher account
- Personal Access Token (PAT)

## Features Roadmap

### Planned

- [ ] WebView for waveform visualization
- [ ] Batch analysis of multiple files
- [ ] Export analysis to JSON/CSV
- [ ] Stem separation from VSCode
- [ ] MIDI conversion integration
- [ ] Keyboard shortcuts customization
- [ ] Dark/Light theme support
- [ ] Inline hover analysis preview

## Troubleshooting

### Extension won't activate

- Check VSCode version (must be 1.85.0+)
- Reload window (Ctrl+R)
- Check Output panel for errors

### Cannot connect to API

1. Ensure API server is running:
   ```bash
   cd samplemind-ai-v6
   make dev
   ```
2. Check API URL in settings
3. Test connection: `curl http://localhost:8000/api/v1/health`

### Audio files not showing in Sample Explorer

1. Add sample folders in settings
2. Refresh the view (click refresh button)
3. Ensure folders contain audio files (.mp3, .wav, .flac, etc.)

### Analysis fails

- Check API server logs
- Verify file format is supported
- Try lower analysis level in settings
- Check file permissions

## Performance

- Analysis caching reduces repeated operations
- Tree view lazy loading for large libraries
- Async operations prevent UI blocking
- Progress indicators for long operations

## Privacy & Security

- All analysis happens on your API server
- No data sent to external services (except your configured API)
- File paths never leave your machine
- Analysis cache stored locally in VSCode

## Contributing

See main project CONTRIBUTING.md

## License

MIT
