# 🐧 SampleMind AI v6 - Linux Installation & Usage Guide

## Complete Guide for Ubuntu, Debian, Fedora, Arch Linux

---

## 🚀 Quick Start (Ubuntu/Debian)

### One-Command Installation
```bash
# Clone and setup
git clone https://github.com/yourusername/samplemind-ai-v6.git
cd samplemind-ai-v6
chmod +x scripts/linux_setup.sh
./scripts/linux_setup.sh
```

### Manual Installation

#### 1. System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    python3-tk zenity ffmpeg portaudio19-dev \
    libsndfile1 libportaudio2 libportaudiocpp0

# Fedora/RHEL
sudo dnf install -y python3.11 python3-tkinter zenity ffmpeg \
    portaudio-devel libsndfile

# Arch Linux
sudo pacman -S python python-pip tk zenity ffmpeg portaudio libsndfile
```

#### 2. Python Environment
```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
pip install google-generativeai openai mutagen
```

#### 3. API Configuration
```bash
# Create .env file
cat > .env << 'EOF'
# Gemini API (PRIMARY)
GOOGLE_AI_API_KEY=your_gemini_key_here

# OpenAI API (FALLBACK)
OPENAI_API_KEY=your_openai_key_here
EOF
```

#### 4. Verify Installation
```bash
./start_cli.sh --verify
```

---

## 🎛️ File Picker Options

SampleMind automatically detects your desktop environment and uses the best file picker:

### GNOME/Ubuntu (Zenity)
```bash
# Install zenity (usually pre-installed)
sudo apt install zenity
```
✅ Native GTK file dialogs
✅ Integrates with Files (Nautilus)

### KDE/Plasma (KDialog)
```bash
# Install kdialog (usually pre-installed on KDE)
sudo apt install kdialog
```
✅ Native Qt file dialogs
✅ Integrates with Dolphin

### XFCE/MATE/Other (Tkinter)
```bash
# Install python3-tk
sudo apt install python3-tk
```
✅ Cross-desktop compatible
✅ Lightweight fallback

### Test File Picker
```bash
source .venv/bin/activate
python -c "from src.samplemind.utils.file_picker import get_file_picker; \
           picker = get_file_picker(); \
           print(picker.get_platform_info())"
```

---

## 🎵 Usage

### Start CLI
```bash
./start_cli.sh
```

### Quick Analysis
```bash
./start_cli.sh analyze /path/to/your/audio.wav
```

### Batch Processing
```bash
./start_cli.sh batch /path/to/music/folder
```

### Demo
```bash
./start_cli.sh --demo
```

---

## 🔧 Linux-Specific Features

### Audio Backend
SampleMind uses multiple audio backends:
- **PortAudio** - Primary backend (ALSA/PulseAudio/JACK)
- **Librosa** - Audio analysis
- **FFmpeg** - Format conversion

### Check Audio System
```bash
# Check PulseAudio
pactl info

# Check ALSA
aplay -l

# Check JACK (if using)
jack_control status
```

### Audio Formats Tested on Linux
✅ WAV (PCM, 16/24/32-bit)
✅ MP3 (all bitrates)
✅ FLAC (lossless)
✅ OGG/Vorbis
✅ OPUS
✅ M4A/AAC
✅ AIFF

---

## 🎨 Desktop Integration

### GNOME Extensions
```bash
# Add to GNOME Activities
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/samplemind-ai.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=SampleMind AI
Comment=AI-Powered Music Production Assistant
Exec=/path/to/samplemind-ai-v6/start_cli.sh
Icon=/path/to/samplemind-ai-v6/assets/icon.png
Terminal=true
Categories=AudioVideo;Audio;Music;
EOF
```

### KDE Plasma Integration
```bash
# Add to Application Launcher
kmenuedit
# Add new item with command: /path/to/start_cli.sh
```

### Create Command Alias
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'alias smai="/path/to/samplemind-ai-v6/start_cli.sh"' >> ~/.bashrc
source ~/.bashrc

# Now use:
smai
smai analyze song.wav
smai --demo
```

---

## 🚀 Performance Optimization

### Faster Analysis (Linux)
```bash
# Use multiple cores
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Restart CLI
./start_cli.sh
```

### GPU Acceleration (NVIDIA)
```bash
# Install CUDA if you have NVIDIA GPU
sudo apt install nvidia-cuda-toolkit

# PyTorch will automatically use GPU for faster processing
```

---

## 📊 System Requirements

### Minimum
- Ubuntu 20.04+ / Debian 11+ / Fedora 35+ / Arch Linux
- Python 3.11+
- 4GB RAM
- 2GB disk space
- PulseAudio or ALSA

### Recommended
- Ubuntu 22.04+ / Fedora 38+ / Arch Linux
- Python 3.11+
- 8GB RAM
- SSD storage
- PulseAudio
- Zenity or KDialog
- Desktop environment (GNOME/KDE/XFCE)

---

## 🐛 Troubleshooting

### Audio Library Errors
```bash
# Reinstall audio libraries
sudo apt install --reinstall libsndfile1 portaudio19-dev

# Check for missing dependencies
ldd .venv/lib/python3.11/site-packages/_soundfile_data/libsndfile.so
```

### Zenity Not Working
```bash
# Check if zenity is installed
which zenity

# Install if missing
sudo apt install zenity

# Test zenity
zenity --file-selection
```

### Permission Errors
```bash
# Make scripts executable
chmod +x start_cli.sh
chmod +x scripts/*.sh

# Fix .venv permissions
chmod -R u+w .venv
```

### PulseAudio Issues
```bash
# Restart PulseAudio
pulseaudio --kill
pulseaudio --start

# Check for conflicts
pactl list short sinks
```

---

## 🔐 Security Notes

### API Key Storage
```bash
# Secure .env file
chmod 600 .env

# Never commit .env to git
echo '.env' >> .gitignore
```

### Firewall Configuration
```bash
# SampleMind needs HTTPS access for AI APIs
# Allow outbound connections to:
# - generativelanguage.googleapis.com (Gemini)
# - api.openai.com (OpenAI)

# UFW example (if using firewall)
sudo ufw allow out 443/tcp
```

---

## 📈 Distribution-Specific Notes

### Ubuntu/Debian
- ✅ Best tested platform
- ✅ Zenity pre-installed
- ✅ Full PulseAudio support

### Fedora/RHEL
- ✅ Fully supported
- ℹ️ Use `dnf` instead of `apt`
- ℹ️ SELinux may require policy updates

### Arch Linux
- ✅ Fully supported
- ℹ️ Use `pacman` for packages
- ℹ️ AUR packages available soon

### Other Distributions
- ✅ Should work on any Linux with Python 3.11+
- ℹ️ May need manual dependency installation
- ℹ️ Tkinter fallback always available

---

## 🎯 Quick Commands Reference

```bash
# Setup
./scripts/linux_setup.sh          # Complete setup
source .venv/bin/activate          # Activate environment

# Run
./start_cli.sh                     # Interactive CLI
./start_cli.sh --demo              # Run demo
./start_cli.sh --verify            # Verify setup

# Analyze
./start_cli.sh analyze song.wav    # Single file
./start_cli.sh batch ./music       # Batch process

# Update
git pull                           # Get latest code
pip install -r requirements.txt    # Update dependencies

# Cleanup
rm -rf ~/.samplemind/cache         # Clear cache
deactivate                         # Exit venv
```

---

## 💡 Tips for Linux Users

1. **Use Native File Pickers** - Zenity/KDialog provide better UX than Tkinter
2. **Check Desktop Environment** - KDE users get KDialog, GNOME gets Zenity
3. **PulseAudio Recommended** - Better compatibility than pure ALSA
4. **Create Alias** - Add `smai` command to your shell
5. **Batch Processing** - Linux is fastest for parallel processing
6. **SSD Recommended** - Much faster for large audio libraries

---

## 📞 Support

### Linux-Specific Issues
- Check logs: `~/.samplemind/logs/`
- Run verbose: `./start_cli.sh --verbose`
- Test audio: `aplay test.wav`
- Test Python: `python -c "import soundfile; print('OK')"`

### Community
- GitHub Issues: Report Linux-specific bugs
- Documentation: [GEMINI_CLI_GUIDE.md](GEMINI_CLI_GUIDE.md)
- Quick Start: [QUICKSTART.md](QUICKSTART.md)

---

**🐧 Enjoy AI-powered music production on Linux!** 🎵✨

*Tested on: Ubuntu 22.04, Fedora 38, Arch Linux (2024)*
