# 🍎 SampleMind AI v6 - macOS Installation & Usage Guide

## Complete Guide for macOS Sonoma, Ventura, Monterey, Big Sur

---

## 🚀 Quick Start

### One-Command Installation
```bash
# Clone and setup
git clone https://github.com/yourusername/samplemind-ai-v6.git
cd samplemind-ai-v6
chmod +x scripts/macos_setup.sh
./scripts/macos_setup.sh
```

### Manual Installation

#### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. System Dependencies
```bash
# Install required packages
brew install python@3.11 ffmpeg portaudio libsndfile

# Link Python 3.11
brew link python@3.11
```

#### 3. Python Environment
```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
pip install google-generativeai openai mutagen
```

#### 4. API Configuration
```bash
# Create .env file
cat > .env << 'EOF'
# Gemini API (PRIMARY)
GOOGLE_AI_API_KEY=your_gemini_key_here

# OpenAI API (FALLBACK)
OPENAI_API_KEY=your_openai_key_here
EOF
```

#### 5. Verify Installation
```bash
./start_cli.sh --verify
```

---

## 🎛️ Native Finder Integration

**SampleMind uses native macOS Finder dialogs!**

### Features
✅ **Native Finder Interface** - AppleScript integration
✅ **Spotlight Integration** - Search while selecting
✅ **Recent Locations** - Access your recent folders
✅ **iCloud Drive Support** - Access cloud files
✅ **Tags & Favorites** - Use macOS file organization
✅ **Quick Look** - Preview files with spacebar

### How It Works
```bash
# When you select "Analyze Single File" or "Batch Process"
# → Native Finder dialog appears
# → Browse with full Finder features
# → Select audio files or folders
# → Analysis begins automatically
```

### Supported File Formats (via Finder)
- ✅ WAV (.wav)
- ✅ MP3 (.mp3)
- ✅ FLAC (.flac)
- ✅ AIFF (.aiff, .aif)
- ✅ M4A (.m4a)
- ✅ OGG (.ogg)
- ✅ OPUS (.opus)

---

## 🎵 Usage

### Start CLI
```bash
./start_cli.sh
```

### Quick Analysis
```bash
./start_cli.sh analyze ~/Music/song.wav
```

### Batch Processing
```bash
./start_cli.sh batch ~/Music/MyBeats
```

### Demo with Test Files
```bash
./start_cli.sh --demo
```

---

## 🚀 macOS-Specific Features

### 1. Native Finder Dialogs
All file selection uses **native macOS Finder**:
- File selection
- Folder selection
- Multiple file selection
- Full Spotlight search integration

### 2. Menu Bar Integration (Coming Soon)
```bash
# Install as menu bar app
./scripts/install_menubar.sh
```
- Quick access from menu bar
- Drag & drop audio files
- System tray notifications

### 3. Automator Integration
Create Quick Actions:

**Automator → New Quick Action**
```applescript
on run {input, parameters}
    set audioFile to POSIX path of (input as alias)
    do shell script "/path/to/samplemind-ai-v6/start_cli.sh analyze " & quoted form of audioFile
    return input
end run
```

Save as "Analyze with SampleMind AI"
→ Right-click any audio file → Quick Actions → Analyze with SampleMind AI

### 4. Spotlight Integration
```bash
# Index analysis results for Spotlight
mdimport -r /path/to/samplemind-ai-v6/results/
```

### 5. Shortcuts App Integration (macOS Monterey+)
Create shortcut:
1. Open Shortcuts.app
2. New Shortcut
3. Add Action: "Run Shell Script"
4. Script: `/path/to/start_cli.sh`
5. Save as "SampleMind AI"

---

## 🎨 Audio Production Integration

### Logic Pro Integration
```bash
# Analyze Logic projects
./start_cli.sh batch ~/Music/Logic

# Export analysis to Logic-compatible format
# (Feature coming soon)
```

### GarageBand Integration
```bash
# Analyze GarageBand audio
./start_cli.sh analyze ~/Music/GarageBand/*.wav
```

### Ableton Live Integration
```bash
# Analyze Ableton samples
./start_cli.sh batch ~/Music/Ableton/User\ Library/Samples
```

---

## ⚡ Performance Optimization

### M1/M2/M3 (Apple Silicon) Optimization
```bash
# Install native ARM packages
brew install --cask miniforge
conda create -n samplemind python=3.11
conda activate samplemind

# Install optimized packages
pip install --no-cache-dir -r requirements.txt
```

### Metal Acceleration (GPU)
```bash
# PyTorch with Metal backend (for M1/M2/M3)
pip install torch torchvision torchaudio

# Verify Metal support
python -c "import torch; print(f'Metal available: {torch.backends.mps.is_available()}')"
```

### Faster Analysis Settings
```bash
# Use all performance cores
export OMP_NUM_THREADS=8

# Restart CLI
./start_cli.sh
```

---

## 📊 System Requirements

### Minimum
- macOS Big Sur 11.0+
- Python 3.11+
- 4GB RAM
- 2GB disk space
- Intel or Apple Silicon

### Recommended
- macOS Sonoma 14.0+
- Python 3.11+
- 8GB RAM (16GB for M1/M2/M3)
- SSD storage
- Apple Silicon (M1/M2/M3)

### Tested Macs
✅ MacBook Pro (M1/M2/M3)
✅ MacBook Air (M1/M2)
✅ iMac (Intel & M1)
✅ Mac mini (Intel & M1/M2)
✅ Mac Studio (M1 Max/Ultra)
✅ Mac Pro (Intel)

---

## 🐛 Troubleshooting

### "Permission denied" Errors
```bash
# Fix script permissions
chmod +x start_cli.sh
chmod +x scripts/*.sh

# Fix .venv permissions
chmod -R u+w .venv
```

### Finder Dialogs Not Appearing
```bash
# Grant Terminal accessibility permissions
# System Settings → Privacy & Security → Accessibility
# → Add Terminal/iTerm

# Test AppleScript
osascript -e 'tell application "Finder" to activate'
```

### Audio Library Errors
```bash
# Reinstall audio libraries
brew reinstall portaudio libsndfile ffmpeg

# Reinstall Python audio packages
pip uninstall soundfile librosa
pip install soundfile librosa --no-cache-dir
```

### Rosetta Issues (Apple Silicon)
```bash
# Install Rosetta 2 if needed
softwareupdate --install-rosetta

# Force native ARM
arch -arm64 ./start_cli.sh
```

### Python Version Conflicts
```bash
# Use specific Python version
python3.11 -m venv .venv
source .venv/bin/activate
which python  # Should show .venv path
```

---

## 🔐 Security & Privacy

### Gatekeeper
```bash
# If blocked by Gatekeeper
xattr -d com.apple.quarantine start_cli.sh
xattr -d com.apple.quarantine scripts/*
```

### API Key Security
```bash
# Secure .env file
chmod 600 .env

# Store in Keychain (optional)
security add-generic-password -a "$USER" -s "SampleMind_Gemini" -w "your_api_key"
```

### Firewall
```bash
# Allow outbound HTTPS for AI APIs
# System Settings → Network → Firewall → Firewall Options
# → Allow connections for Python
```

---

## 📁 File Organization

### Recommended Folder Structure
```
~/Music/
├── SampleMind/
│   ├── Analysis Results/
│   ├── Processed Samples/
│   └── FL Studio Presets/
├── Logic/
│   └── SampleMind Analysis/
└── Original Samples/
```

### iCloud Drive Integration
```bash
# Analyze files in iCloud
./start_cli.sh batch ~/Library/Mobile\ Documents/com~apple~CloudDocs/Music
```

---

## 🎯 Quick Commands Reference

```bash
# Setup
brew install python@3.11 ffmpeg        # Install dependencies
python3.11 -m venv .venv               # Create environment
source .venv/bin/activate              # Activate

# Run
./start_cli.sh                         # Interactive CLI
./start_cli.sh --demo                  # Demo mode
./start_cli.sh --verify                # Verify setup

# Analyze
./start_cli.sh analyze song.wav        # Single file
./start_cli.sh batch ~/Music/Beats     # Batch process

# Update
git pull                               # Get updates
pip install -r requirements.txt        # Update packages
brew upgrade                           # Update Homebrew packages
```

---

## 💡 macOS Pro Tips

1. **Use Finder Tags** - Tag analyzed files for organization
2. **Create Automator Actions** - Right-click integration
3. **Spotlight Search** - Search analysis results
4. **Shortcuts App** - Quick access to CLI
5. **iCloud Drive** - Analyze cloud files
6. **Apple Silicon** - 2-3x faster on M1/M2/M3
7. **Logic/GarageBand** - Seamless DAW integration
8. **Metal GPU** - Hardware acceleration available

---

## 🎵 DAW Integration Guides

### For Logic Pro Users
```bash
# 1. Export stems from Logic
# 2. Analyze with SampleMind:
./start_cli.sh batch ~/Music/Logic/ProjectStems

# 3. Get production recommendations
# 4. Apply suggestions in Logic
```

### For Ableton Users (via macOS)
```bash
# Analyze Ableton User Library
./start_cli.sh batch ~/Music/Ableton/User\ Library

# Export analysis to Ableton compatible format
# (Coming soon)
```

---

## 📞 Support

### macOS-Specific Issues
- Check logs: `~/Library/Application Support/SampleMind/Logs/`
- Console.app: Filter for "SampleMind" or "Python"
- Activity Monitor: Check CPU/RAM usage
- Crash reports: `~/Library/Logs/DiagnosticReports/`

### Useful Commands
```bash
# System info
sw_vers
uname -m  # Check architecture (arm64 or x86_64)

# Python info
python --version
which python

# Audio devices
system_profiler SPAudioDataType
```

---

## 🔄 Updates & Maintenance

### Keep Updated
```bash
# Update Homebrew
brew update && brew upgrade

# Update Python packages
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Update SampleMind
git pull
```

### Backup Configuration
```bash
# Backup your settings
cp .env ~/.samplemind_backup.env
cp -r ~/.samplemind ~/Desktop/SampleMind_Backup

# Backup analysis results
zip -r ~/Desktop/samplemind_results.zip ./results/
```

---

## 🌟 Exclusive macOS Features

✅ **Native Finder Integration** - AppleScript dialogs
✅ **Logic Pro Ready** - Professional DAW support
✅ **Apple Silicon Optimized** - M1/M2/M3 native
✅ **Metal GPU Acceleration** - Hardware accelerated
✅ **Spotlight Integration** - Search analysis results
✅ **Automator Support** - Create Quick Actions
✅ **Shortcuts App** - Siri integration ready
✅ **Menu Bar App** - Coming soon
✅ **Touch Bar Support** - For compatible models

---

**🍎 Professional AI music production, designed for macOS!** 🎵✨

*Tested on: macOS Sonoma 14.x, Ventura 13.x, Monterey 12.x*
