# SampleMind Max Device Prototype

HTML prototype for validating the SampleMind Ableton Live integration without requiring Max/MSP software ($399).

## Overview

This prototype demonstrates the complete UX/UI for the SampleMind Max device including:
- **Audio Analysis** - Analyze files for tempo, key, genre, energy
- **Similar Sample Search** - Find similar samples in library
- **Project Sync** - Get BPM/key matching recommendations
- **Real Backend Integration** - Connects to FastAPI backend at `localhost:8001`

**Device Size**: 500x300px (Max device standard)
**Browser**: Chrome, Firefox, Safari (modern versions)

## Files

- `samplemind_ui.html` - Main prototype interface (500x300px Max device)
- `styles.css` - Styling and theming
- `communication.js` - API client for backend communication
- `README.md` - This file

## Getting Started

### 1. Start the Backend

```bash
# Terminal 1 - Start Python backend
cd /home/lchtangen/Documents/SampleMind-AI-DEV/SampleMind-AI---Beta
python plugins/ableton/python_backend.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 2. Open the Prototype

```bash
# Terminal 2 - Open in browser
firefox plugins/ableton/prototype/samplemind_ui.html
# or
google-chrome plugins/ableton/prototype/samplemind_ui.html
# or
open plugins/ableton/prototype/samplemind_ui.html  # macOS
```

### 3. Test the Features

#### Audio Analysis Tab
1. Click **Select File** and choose an audio file (MP3, WAV, etc.)
2. Select analysis level: Basic, Standard, Detailed, or Professional
3. Click **Analyze**
4. View results: Tempo, Key, Genre, Energy, Confidence

#### Similar Samples Tab
1. Click **Select Query File** and choose a reference audio
2. Set number of results (1-20)
3. Click **Search Similar**
4. View similarity scores with progress bars

#### Project Sync Tab
1. Set project BPM (40-300)
2. Select project key (C Major through B Minor)
3. Set number of suggestions (1-20)
4. Click **Get Recommendations**
5. View matched samples with BPM and match scores

## Features

### Header
- **Status Indicator** - Shows current operation status
  - Ready (default)
  - Analyzing/Searching/Syncing (processing)
  - Success (green) or Error (red)

### Server Connection
- **Connection Indicator** (bottom left)
  - Green dot = Connected
  - Red dot = Disconnected
- Auto-reconnects every 5 seconds

### Settings
- **Backend URL** - Change API endpoint (default: `http://localhost:8001`)
- **Retry Attempts** - Configure retry logic (1-10, default: 3)
- **Result Caching** - Enable/disable response caching

### Error Handling
- Displays specific error messages for each operation
- Graceful fallback when backend is offline
- Retry logic with exponential backoff

### Loading States
- Animated spinner during operations
- Disabled buttons while processing
- Operation status updates in header

## API Integration

The prototype uses `communication.js` which implements:

### Health Check
```javascript
const health = await api.health();
// Returns: { status: "healthy", version: "1.0.0" }
```

### Audio Analysis
```javascript
const file = document.getElementById('audio-file').files[0];
const result = await api.analyzeAudio(file, 'STANDARD');
// Returns: {
//   tempo_bpm: 120,
//   key: "C Major",
//   genre: "Electronic",
//   energy: 0.75,
//   confidence: 0.92
// }
```

### Similar Search
```javascript
const results = await api.findSimilar(file, 10);
// Returns: [{
//   file_path: "/path/to/sample.wav",
//   similarity: 0.95
// }, ...]
```

### Project Sync
```javascript
const results = await api.projectSync(120, 'C Major', 10);
// Returns: [{
//   file_path: "/path/to/sample.wav",
//   bpm: 120,
//   key: "C Major",
//   match_score: 0.98
// }, ...]
```

## Testing

### Manual Testing Checklist

- [ ] **Connection** - Server indicator shows green when backend running
- [ ] **Analysis** - Upload file, get tempo/key/genre results
- [ ] **Search** - Find similar samples with confidence scores
- [ ] **Sync** - Get BPM/key matching recommendations
- [ ] **Caching** - Second search for same file loads from cache
- [ ] **Error Handling** - Friendly error messages for failures
- [ ] **Offline** - Server indicator turns red when backend stops
- [ ] **Settings** - Change backend URL and see it reconnect
- [ ] **Responsiveness** - All interactions feel responsive (<100ms)

### Unit Tests

JavaScript unit tests are in `tests/unit/plugins/test_communication.js`:

```bash
cd /home/lchtangen/Documents/SampleMind-AI-DEV/SampleMind-AI---Beta

# Run tests
npm install  # if needed
npm test tests/unit/plugins/test_communication.js

# Expected: 40+ tests passing
```

Tests cover:
- Client initialization and configuration
- HTTP request handling with retries
- Caching behavior
- Error handling and recovery
- API method signatures
- Integration scenarios

## UI Design Details

### Color Scheme
- **Primary**: Cyan (#00d9ff) - Highlights, active state
- **Success**: Green (#4caf50) - Successful operations
- **Error**: Red (#f44336) - Failures and problems
- **Neutral**: Dark grays - Background and text
- **Accent**: Lime green (#00ff88) - Energy/progress meters

### Layout
- **Header** (50px) - Title, status
- **Tabs** (40px) - Navigation
- **Content** (200px) - Main content area with scrolling
- **Footer** (30px) - Server status, settings

### Typography
- **Headings**: 14px, bold
- **Labels**: 11px, medium weight
- **Values**: 11px, cyan color for emphasis
- **Status**: 12px, color-coded

### Interactions
- **Keyboard**: Tab to navigate, Enter to submit
- **Mouse**: Click tabs, buttons, links
- **Touchscreen**: Tap buttons and inputs (tested on iPad)

## Performance

Target performance metrics:
- **Load Time**: <500ms
- **Tab Switch**: <50ms
- **Status Update**: <100ms
- **Backend Request**: <2s (analysis), <1s (search/sync)

Current performance:
- HTML prototype: ~2.5 KB
- CSS styling: ~12 KB
- JavaScript client: ~7 KB
- **Total**: ~21 KB uncompressed

## Browser Compatibility

Tested and working on:
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

Requires:
- ES6+ JavaScript support
- Fetch API
- FormData API
- CSS Grid

## Troubleshooting

### "Disconnected" Status
1. Verify backend is running: `python plugins/ableton/python_backend.py`
2. Check port 8001 is not in use: `lsof -i :8001`
3. Try changing backend URL in Settings

### Analysis Fails with "Failed to analyze"
1. Ensure audio file is valid (MP3, WAV, AIFF, OGG)
2. Check backend logs for errors
3. Try a different file
4. Verify analysis level selection

### Search Returns Empty Results
1. Ensure samples exist in backend library
2. Try selecting different analysis level
3. Check backend is connected (green indicator)

### Settings Won't Save
1. Check browser console for errors (F12)
2. Ensure JavaScript is enabled
3. Try reloading page

## Development Notes

### Adding New Features
1. Add UI elements to `samplemind_ui.html`
2. Add styling to `styles.css`
3. Add API methods to `communication.js`
4. Add event handlers in HTML script section
5. Test manually and with unit tests

### Modifying Backend URL
Change default in HTML prototype:
```javascript
const api = new SampleMindAPIClient('http://your-host:port');
```

Or use Settings dialog at runtime.

### Customizing Colors
Edit CSS variables in `styles.css`:
```css
--primary-color: #00d9ff;
--success-color: #4caf50;
--error-color: #f44336;
```

## Future Enhancements

- [ ] Playlist analysis (batch mode)
- [ ] Export results as JSON/CSV
- [ ] Waveform visualization
- [ ] Real-time spectrogram display
- [ ] Drag-and-drop file support
- [ ] History/recent searches
- [ ] Keyboard shortcuts
- [ ] Dark/light theme toggle

## Credits

SampleMind AI - Ableton Live Plugin Prototype
Created: February 2026
Backend: FastAPI Python
Frontend: HTML5 + CSS3 + JavaScript ES6

## License

Part of SampleMind AI - See main project LICENSE file
