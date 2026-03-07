# SampleMind AI Plugin Installation Guide

**Version:** 1.0.0
**Status:** Ready for Installation
**Last Updated:** February 3, 2026

---

## Overview

SampleMind AI provides native plugins for popular Digital Audio Workstations (DAWs):
- **FL Studio** (Version 20+)
- **Ableton Live** (Version 11+)

This guide covers installing, verifying, and managing these plugins across Windows, macOS, and Linux.

---

## System Requirements

### Prerequisites

1. **Python 3.11 or later**
   ```bash
   python3 --version
   ```

2. **Supported DAW Installed**
   - FL Studio 20+ (any edition)
   - Ableton Live 11+ (Suite or Standard)

3. **Administrator/Sudo Access** (for plugin installation)
   - Windows: Run Command Prompt as Administrator
   - macOS/Linux: Use `sudo` for installation commands

4. **Disk Space**
   - FL Studio plugin: ~5-10 MB
   - Ableton Live plugin: ~2-5 MB (plus Max for Live support)

### Supported Platforms

| Platform | Plugin Format | Status |
|----------|---------------|---------|
| Windows 10/11 | .dll (VST3) | ✅ Supported |
| macOS 10.13+ | .dylib | ✅ Supported |
| Linux (Ubuntu/Debian) | .so | ✅ Supported |

---

## Quick Installation

### Using Installation Script (Recommended)

The easiest way to install plugins:

```bash
# Navigate to project root
cd /path/to/SampleMind-AI

# Run installer script
bash scripts/install-plugins.sh --install-all
```

### Using Python Directly

If you prefer to run the installer directly:

```bash
# List detected DAWs
python3 plugins/installer.py --list

# Install all plugins
python3 plugins/installer.py --install-all

# Install specific plugin
python3 plugins/installer.py --install fl_studio
python3 plugins/installer.py --install ableton

# Verify installations
python3 plugins/installer.py --verify

# Uninstall plugins
python3 plugins/installer.py --uninstall-all
```

---

## Step-by-Step Installation

### Step 1: Detect Installed DAWs

The installer automatically detects which DAWs are installed:

```bash
bash scripts/install-plugins.sh --list
```

Output example:
```
🔍 Detecting installed DAWs...
  ✓ FL Studio: /Applications/FL Studio.app
  ✓ Ableton Live: /Applications/Ableton Live 12.app
```

### Step 2: Prepare FL Studio Plugin (Optional)

If you want to use the FL Studio plugin, you need to compile it first:

```bash
cd plugins/fl_studio

# Create build directory
mkdir -p build
cd build

# Configure with CMake (macOS example)
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DFL_STUDIO_SDK_PATH="$HOME/FL_STUDIO_SDK"

# Compile
make -j4

# Verify build output
ls -lh lib/libSampleMind_FL_Studio.dylib
```

For detailed FL Studio compilation instructions, see [plugins/fl_studio/BUILD.md](plugins/fl_studio/BUILD.md)

### Step 3: Run Installation

```bash
# Install all available plugins
bash scripts/install-plugins.sh --install-all

# Or install specific DAWs
bash scripts/install-plugins.sh --install fl_studio
bash scripts/install-plugins.sh --install ableton
```

The installer will:
1. ✓ Detect installed DAWs
2. ✓ Create plugin directories (if needed)
3. ✓ Copy plugin files to correct locations
4. ✓ Verify installation
5. ✓ Generate installation log

### Step 4: Restart Your DAW

Close and reopen your DAW for it to recognize the new plugins:

```bash
# macOS: Quit from Dock
# Windows: Alt+F4 or File → Exit
# Linux: Close window or killall [app_name]
```

### Step 5: Find the Plugin

#### FL Studio
1. Open FL Studio
2. Click "+ Mixer Track" or open Channels menu
3. Click on track → Add → Generators
4. Look for **"SampleMind AI"** in the generator list

#### Ableton Live
1. Open Ableton Live
2. Open the Browser (Ctrl+Alt+B or Cmd+Option+B)
3. Navigate to: Instruments → Max Instrument
4. Look for **"SampleMind AI"** device

---

## Verification

### Verify Plugin Installation

After installation, verify that plugins are correctly installed:

```bash
bash scripts/install-plugins.sh --verify
```

Output:
```
🔍 Verifying plugin installations...

  ✓ Installed: FL Studio
  ✓ Installed: Ableton Live
```

### Test Plugin in DAW

**FL Studio:**
1. Create new MIDI channel
2. Insert SampleMind AI generator
3. Click on the plugin to open interface
4. Load an audio sample

**Ableton Live:**
1. Create MIDI track
2. Add SampleMind AI Max device
3. Drag sample onto the device
4. Verify analysis results display

### Troubleshooting Installation

**Plugin not appearing in DAW:**
- [ ] Restart DAW completely (not just close window)
- [ ] Check file permissions (chmod +x on Linux/macOS)
- [ ] Verify installation path is correct
- [ ] Run `--verify` command again

**"Permission Denied" error:**
```bash
# macOS/Linux: Run with sudo
sudo bash scripts/install-plugins.sh --install-all

# Windows: Run Command Prompt as Administrator
python plugins/installer.py --install-all
```

**Plugin files not found:**
```bash
# If FL Studio plugin isn't compiled yet:
cd plugins/fl_studio && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
```

**DAW not detected:**
```bash
# Check if DAW is actually installed
bash scripts/install-plugins.sh --list

# Manually check installation paths:
# Windows:
#   FL Studio: C:\Program Files\Image-Line\FL Studio 21
#   Ableton: C:\Program Files\Ableton\Live 12

# macOS:
#   FL Studio: /Applications/FL Studio.app
#   Ableton: /Applications/Ableton Live 12.app

# Linux:
#   FL Studio: ~/FL_Studio or /opt/fl_studio
#   Ableton: ~/Ableton or /opt/Ableton
```

---

## Installation Paths

### FL Studio Plugin Locations

The installer automatically places the plugin in the correct location:

#### Windows
```
C:\Program Files\Image-Line\FL Studio 21\Plugins\Fruity\Generators\
```
**File:** `SampleMind_FL_Studio.dll`

#### macOS
```
~/Library/Application Support/Image-Line/FL Studio/Plugins/Fruity/Generators/
```
**File:** `libSampleMind_FL_Studio.dylib`

#### Linux
```
~/.config/Image-Line/FL Studio/Plugins/Fruity/Generators/
```
**File:** `libSampleMind_FL_Studio.so`

### Ableton Live Plugin Locations

#### Windows
```
%APPDATA%\Ableton\User Library\Presets\Instruments\Max Instrument\
```
**Files:**
- `SampleMind.amxd` (Max device)
- `communication.js` (JavaScript bridge)
- `midi_mapper.maxpat` (MIDI mapper)

#### macOS
```
~/Music/Ableton User Library/Presets/Instruments/Max Instrument/
```
**Files:**
- `SampleMind.amxd`
- `communication.js`
- `midi_mapper.maxpat`

#### Linux
```
~/.Ableton/User Library/Presets/Instruments/Max Instrument/
```
**Files:**
- `SampleMind.amxd`
- `communication.js`
- `midi_mapper.maxpat`

---

## Uninstallation

### Uninstall All Plugins

```bash
bash scripts/install-plugins.sh --uninstall-all
```

### Uninstall Specific Plugin

```bash
# Remove only FL Studio plugin
bash scripts/install-plugins.sh --uninstall fl_studio

# Remove only Ableton Live plugin
bash scripts/install-plugins.sh --uninstall ableton
```

### Manual Uninstallation

If the script fails, manually delete plugin files:

#### FL Studio (Windows)
```batch
del "C:\Program Files\Image-Line\FL Studio 21\Plugins\Fruity\Generators\SampleMind_FL_Studio.dll"
```

#### FL Studio (macOS)
```bash
rm ~/Library/Application\ Support/Image-Line/FL\ Studio/Plugins/Fruity/Generators/libSampleMind_FL_Studio.dylib
```

#### Ableton Live (macOS)
```bash
rm -r ~/Music/Ableton\ User\ Library/Presets/Instruments/Max\ Instrument/SampleMind*
rm ~/Music/Ableton\ User\ Library/Presets/Instruments/Max\ Instrument/communication.js
```

---

## Installation Logs

### View Installation Log

The installer can save a detailed log of all actions:

```bash
bash scripts/install-plugins.sh --install-all --log installation.log
```

### Sample Log Output

```
🔍 Detecting installed DAWs...
  ✓ FL Studio: /Applications/FL Studio.app
  ✓ Ableton Live: /Applications/Ableton Live 12.app

📦 Installing all available plugins...

Installing FL Studio plugin...
  ✓ Copied SampleMind_FL_Studio.dylib to /Library/Application Support/...
  ✓ Installation verified (8.45 MB)
  ✓ FL Studio plugin installed successfully

Installing Ableton Live plugin...
  ✓ Copied SampleMind.amxd to ~/Music/Ableton User Library/Presets/...
  ✓ Copied communication.js to ~/Music/Ableton User Library/Presets/...
  ✓ Ableton Live plugin installed successfully

✅ All plugins installed successfully!
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "Plugin not detected in DAW"

**Cause:** DAW hasn't scanned new plugin directory

**Solution:**
1. Completely close the DAW
2. Wait 5-10 seconds
3. Reopen the DAW
4. Force plugin rescan if available in preferences

#### Issue: "Permission Denied" during installation

**Cause:** Need administrator privileges

**Solution:**
```bash
# macOS/Linux
sudo bash scripts/install-plugins.sh --install-all

# Windows: Run Command Prompt as Administrator
# Then run: python plugins/installer.py --install-all
```

#### Issue: "FL Studio SDK not found" (if compiling)

**Cause:** FL Studio SDK not downloaded

**Solution:**
1. Request SDK from Image-Line: https://www.image-line.com/contact/
2. Extract SDK to known location
3. Recompile with correct path:
   ```bash
   cd plugins/fl_studio/build
   cmake .. -DFL_STUDIO_SDK_PATH="/path/to/fl/sdk"
   make -j4
   ```

#### Issue: Ableton Live shows "Max for Live not available"

**Cause:** Max for Live not installed or enabled

**Solution:**
1. Open Ableton Live Preferences
2. Navigate to Library tab
3. Enable "Max for Live" option
4. Restart Ableton Live
5. Re-run installer

#### Issue: "Python 3 not found"

**Cause:** Python not in system PATH

**Solution:**
```bash
# macOS/Linux
which python3
python3 --version

# If not found, install Python 3.11+
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3.11
# Windows: Download from python.org

# Then run installer with full path
/usr/bin/python3 plugins/installer.py --list
```

#### Issue: Plugin crashes when loading

**Cause:** Missing dependencies or Python environment issue

**Solution:**
1. Check if SampleMind Python package is installed:
   ```bash
   python3 -c "import samplemind; print(samplemind.__version__)"
   ```

2. If missing, install SampleMind:
   ```bash
   pip3 install samplemind-ai
   ```

3. Reinstall plugin:
   ```bash
   bash scripts/install-plugins.sh --uninstall-all
   bash scripts/install-plugins.sh --install-all
   ```

#### Issue: Slow plugin performance

**Cause:** System resources or analysis settings

**Solution:**
1. In plugin interface, reduce analysis level (BASIC instead of PROFESSIONAL)
2. Close other CPU-intensive applications
3. Check system RAM and CPU usage
4. For Ableton Live: Disable auto-sync if not needed

---

## Advanced Configuration

### Custom Installation Paths

For advanced users who want to install to custom locations:

```python
# Edit plugins/installer.py
# Modify get_fl_studio_plugin_paths() or get_ableton_plugin_paths()

from pathlib import Path

# Example: Custom FL Studio path
custom_path = Path("/custom/plugins/location")
```

### Batch Installation Across Multiple Systems

Create a deployment script:

```bash
#!/bin/bash
# deploy_plugins.sh - Install SampleMind plugins on multiple systems

for host in studio1 studio2 studio3; do
    echo "Installing plugins on $host..."
    ssh $host "cd /path/to/SampleMind && bash scripts/install-plugins.sh --install-all"
done
```

### Environment Variables

Control installation behavior via environment variables:

```bash
# Skip permission checks (use with caution)
SKIP_PERMS=1 bash scripts/install-plugins.sh --install-all

# Use specific Python version
PYTHON_BIN=/usr/bin/python3.11 bash scripts/install-plugins.sh --install-all

# Custom log directory
LOG_DIR=/var/log bash scripts/install-plugins.sh --install-all --log "$LOG_DIR/install.log"
```

---

## Platform-Specific Notes

### Windows

- **Supported Versions:** Windows 10, Windows 11
- **Compiler:** Visual Studio 2019+ (for FL Studio plugin compilation)
- **Paths:** Use `%APPDATA%` environment variable for Ableton paths
- **Admin Mode:** Right-click Command Prompt → Run as Administrator

**Example Windows Installation:**
```batch
# Open Command Prompt as Administrator
cd C:\Users\YourName\Documents\SampleMind-AI
python plugins\installer.py --install-all
```

### macOS

- **Supported Versions:** macOS 10.13 (High Sierra) or later
- **Compiler:** Xcode Command Line Tools required for compilation
- **Architecture:** Works on both Intel and Apple Silicon (arm64)
- **Notarization:** Plugins are not notarized (you may need to allow in Security & Privacy)

**Allow unsigned plugins:**
1. System Preferences → Security & Privacy
2. Click "Allow Anyway" if prompted about unsigned plugins
3. Restart DAW

**Example macOS Installation:**
```bash
bash scripts/install-plugins.sh --install-all
# Enter password when prompted for sudo
```

### Linux

- **Supported Distributions:** Ubuntu 20.04+, Debian 11+, Fedora 35+
- **Compiler:** GCC 9+ or Clang 10+
- **Paths:** Uses `~/.config/` and `~/.Ableton/` for plugin locations
- **Permissions:** May require sudo for system-wide plugin paths

**Example Linux Installation:**
```bash
sudo bash scripts/install-plugins.sh --install-all
```

---

## Uninstalling SampleMind

### Complete Uninstallation

```bash
# 1. Uninstall all plugins
bash scripts/install-plugins.sh --uninstall-all

# 2. Remove SampleMind package (optional)
pip3 uninstall samplemind-ai

# 3. Remove configuration (optional)
rm -rf ~/.samplemind/
```

### Re-installation After Uninstall

```bash
# Clean and reinstall
bash scripts/install-plugins.sh --install-all
```

---

## Support and Troubleshooting

### Getting Help

If you encounter issues:

1. **Check Installation Log**
   ```bash
   cat installation.log
   ```

2. **Run Verification**
   ```bash
   bash scripts/install-plugins.sh --verify
   ```

3. **Check System Requirements**
   - Python 3.11+ installed
   - Correct DAW version installed
   - Sufficient disk space
   - Administrator privileges

4. **Consult Documentation**
   - [FL Studio Plugin Guide](plugins/fl_studio/BUILD.md)
   - [Ableton Live Plugin Guide](plugins/ableton/README.md)
   - [Phase 13.2 DAW Plugin Plan](docs/PHASE_13_2_DAW_PLUGIN_PLAN.md)

5. **Report Issues**
   - GitHub Issues: https://github.com/samplemind/samplemind-ai/issues
   - Include installation log and system information

### System Information for Support

When reporting issues, include:

```bash
# Gather system information
bash scripts/install-plugins.sh --list > system_info.txt
python3 --version >> system_info.txt
uname -a >> system_info.txt  # macOS/Linux only

# Share system_info.txt with support
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-03 | Initial release - FL Studio & Ableton Live support |

---

## Next Steps

After successful installation:

1. **Launch Your DAW** and find the SampleMind AI plugin
2. **Load a Sample** audio file
3. **Run Analysis** to see audio intelligence features
4. **Read Plugin Guides:**
   - [FL Studio Plugin Guide](plugins/fl_studio/README.md)
   - [Ableton Live Plugin Guide](plugins/ableton/README.md)

---

**Status:** ✅ Installation Guide Complete
**Last Updated:** February 3, 2026
**License:** MIT

For more information about SampleMind AI, visit the [main README](README.md).
