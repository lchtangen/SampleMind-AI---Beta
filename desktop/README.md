# SampleMind AI - Desktop Application

Native desktop application wrapper for SampleMind AI using Electron.

## Features

### ✅ Implemented

- **Native Window** - Platform-native window chrome
- **File System Access** - Direct file system operations
- **Native Dialogs** - File open/save dialogs
- **Notifications** - System notifications
- **Auto-Updates** - Automatic update checking
- **Recent Files** - Track recently opened files
- **Menu Bar** - Native application menu
- **Keyboard Shortcuts** - Platform-specific shortcuts
- **Multi-Platform** - macOS, Windows, Linux support

### Native Integrations

- **File Picker** - Native file/directory selection
- **Drag & Drop** - Drag files onto the app
- **Recent Files** - OS-level recent files
- **Notifications** - Native system notifications
- **Auto-Updater** - Automatic updates via GitHub releases

## Tech Stack

- **Electron 28** - Desktop framework
- **electron-store** - Persistent configuration
- **electron-updater** - Auto-update support
- **electron-builder** - Packaging and distribution

## Development

### Prerequisites

- Node.js 20+
- Built React PWA (from `../web`)

### Setup

```bash
# Install dependencies
npm install

# Build React PWA first
cd ../web
npm run build
cd ../desktop

# Run in development mode
npm run dev
```

### Development Mode

In development, the app loads from the Vite dev server at `http://localhost:5173`:

```bash
# Terminal 1: Start React dev server
cd web
npm run dev

# Terminal 2: Start Electron app
cd desktop
npm run dev
```

## Building

### Build for Current Platform

```bash
npm run build
```

### Build for Specific Platforms

```bash
# macOS
npm run build:mac

# Windows
npm run build:win

# Linux
npm run build:linux
```

### Package Without Distribution

```bash
npm run package
```

Output will be in `desktop/dist/`

## Distribution

### macOS

Builds:
- `.dmg` - Disk image installer
- `.zip` - Portable archive

Requirements:
- Code signing certificate (for distribution)
- Notarization (for macOS 10.15+)

### Windows

Builds:
- `.exe` - NSIS installer
- Portable `.exe`

Requirements:
- Code signing certificate (optional but recommended)

### Linux

Builds:
- `.AppImage` - Universal Linux package
- `.deb` - Debian/Ubuntu package
- `.rpm` - Fedora/RHEL package

## Architecture

### Main Process (`src/main.js`)

Handles:
- Window creation and management
- Application menu
- File dialogs
- System notifications
- Auto-updates
- Configuration storage
- IPC communication

### Preload Script (`src/preload.js`)

Provides secure bridge between main and renderer:
- File system operations
- Configuration management
- Native dialogs
- Event listeners

### Renderer Process

The React PWA (from `../web`) with Electron-specific enhancements.

## Configuration

Configuration is stored using `electron-store`:

**Location:**
- macOS: `~/Library/Application Support/samplemind-desktop/config.json`
- Windows: `%APPDATA%/samplemind-desktop/config.json`
- Linux: `~/.config/samplemind-desktop/config.json`

**Settings:**
```json
{
  "windowBounds": { "width": 1400, "height": 900 },
  "apiUrl": "http://localhost:8000",
  "theme": "dark",
  "recentFiles": []
}
```

## IPC API

The renderer process can access native features via `window.electron`:

### File Operations

```javascript
// Open file dialog
await window.electron.openFileDialog();

// Open directory dialog
await window.electron.openDirectoryDialog();

// Read file
const result = await window.electron.readFile('/path/to/file');

// Write file
await window.electron.writeFile('/path/to/file', base64Data);

// Save dialog
const result = await window.electron.showSaveDialog({
  defaultPath: 'output.wav',
  filters: [{ name: 'Audio', extensions: ['wav', 'mp3'] }]
});
```

### Configuration

```javascript
// Get config
const theme = await window.electron.getConfig('theme');

// Set config
await window.electron.setConfig('theme', 'dark');
```

### Notifications

```javascript
// Show notification
await window.electron.showNotification('Title', 'Message body');
```

### Event Listeners

```javascript
// Listen for file open
window.electron.onOpenFile((filePath) => {
  console.log('File opened:', filePath);
});

// Listen for directory open
window.electron.onOpenDirectory((dirPath) => {
  console.log('Directory opened:', dirPath);
});
```

### System Paths

```javascript
// Get system path
const documentsPath = await window.electron.getPath('documents');
const downloadsPath = await window.electron.getPath('downloads');
```

## Menu

### File Menu

- Open Audio File... (`Cmd/Ctrl+O`)
- Open Directory... (`Cmd/Ctrl+Shift+O`)
- Recent Files (submenu)
- Quit

### Edit Menu

Standard edit operations (Undo, Redo, Cut, Copy, Paste, Select All)

### View Menu

- Reload
- Toggle Developer Tools
- Zoom controls
- Toggle Fullscreen

### Window Menu

- Minimize
- Zoom
- Bring All to Front (macOS)

### Help Menu

- Documentation
- Report Issue
- Check for Updates
- About SampleMind AI

## Auto-Updates

The app automatically checks for updates on startup (production builds only).

Updates are fetched from GitHub Releases:
- **Repository:** `samplemind-ai/desktop`
- **Feed URL:** `https://github.com/samplemind-ai/desktop/releases/latest`

Users are notified when:
1. Update is available (notification)
2. Update is downloaded (dialog with restart option)

## Security

### Context Isolation

The app uses context isolation to prevent the renderer from directly accessing Node.js/Electron APIs.

### Preload Script

All native functionality is exposed through a secure API in the preload script.

### Content Security Policy

Web security is enabled in production to prevent loading external content.

## Icons

Place platform-specific icons in `build/`:
- `icon.icns` - macOS (1024x1024)
- `icon.ico` - Windows (256x256)
- `icon.png` - Linux (512x512)

Generate icons from a single source:
```bash
# Using electron-icon-builder
npm install -g electron-icon-builder
electron-icon-builder --input=./icon.png --output=./build
```

## Troubleshooting

### App won't start

1. Ensure React PWA is built:
   ```bash
   cd ../web && npm run build
   ```

2. Check Electron version compatibility:
   ```bash
   npm list electron
   ```

### Auto-update not working

- Only works in production builds
- Requires proper code signing
- Check GitHub releases configuration

### Native modules

If using native modules, rebuild for Electron:
```bash
npm rebuild --runtime=electron --target=28.0.0 --disturl=https://electronjs.org/headers --abi=109
```

## License

MIT
