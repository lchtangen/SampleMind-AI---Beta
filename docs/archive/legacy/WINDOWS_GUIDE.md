# 🪟 SampleMind AI v6 - Windows Installation & Usage Guide

## Complete Guide for Windows 11, Windows 10

---

## 🚀 Quick Start

### Method 1: Automated Installation (Recommended)

#### Download & Run Setup Script
```powershell
# Open PowerShell as Administrator
# Download repository
git clone https://github.com/yourusername/samplemind-ai-v6.git
cd samplemind-ai-v6

# Run Windows setup script
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\windows_setup.ps1
```

---

### Method 2: Manual Installation

#### 1. Install Python 3.11+
```powershell
# Download from python.org or use winget
winget install Python.Python.3.11

# Verify installation
python --version  # Should show Python 3.11.x
```

#### 2. Install System Dependencies

**Option A: Using Chocolatey (Recommended)**
```powershell
# Install Chocolatey if not installed
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install ffmpeg git -y
```

**Option B: Manual Downloads**
- **FFmpeg**: Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
- **Git**: Download from [git-scm.com](https://git-scm.com/download/win)

#### 3. Setup Python Environment
```powershell
# Navigate to project directory
cd samplemind-ai-v6

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
pip install google-generativeai openai mutagen
```

#### 4. Configure API Keys
```powershell
# Create .env file
@"
# Gemini API (PRIMARY)
GOOGLE_AI_API_KEY=your_gemini_key_here

# OpenAI API (FALLBACK)
OPENAI_API_KEY=your_openai_key_here

# Windows-specific settings
DEFAULT_MODEL=gemini-2.5-pro
ENVIRONMENT=production
CACHE_ENABLED=true
"@ | Out-File -FilePath .env -Encoding UTF8
```

#### 5. Verify Installation
```powershell
# Test the installation
python verify_setup.py
```

---

## 🎛️ Windows File Explorer Integration

**SampleMind uses native Windows File Explorer dialogs!**

### Features
✅ **Native Windows Explorer** - Standard file/folder selection
✅ **Quick Access** - Recent files and pinned folders
✅ **Network Drives** - Access SMB/NAS shares
✅ **OneDrive Integration** - Access cloud files
✅ **File Previews** - Preview pane support
✅ **Search Integration** - Windows Search while browsing

### How It Works
```powershell
# When you select file/folder operations in CLI:
# → Native Windows File Explorer dialog appears
# → Browse with familiar Windows interface
# → Select audio files or folders
# → Analysis begins automatically
```

### Supported Audio Formats
- ✅ WAV (.wav)
- ✅ MP3 (.mp3)
- ✅ FLAC (.flac)
- ✅ AIFF (.aiff, .aif)
- ✅ M4A (.m4a)
- ✅ WMA (.wma)
- ✅ OGG (.ogg)
- ✅ OPUS (.opus)

---

## 🎵 Usage

### Start CLI
```powershell
# Activate environment
.\.venv\Scripts\activate

# Run CLI
python main.py
```

### Quick Analysis
```powershell
python main.py analyze "C:\Users\YourName\Music\song.wav"
```

### Batch Processing
```powershell
python main.py batch "C:\Users\YourName\Music\MyBeats"
```

### Run Demo
```powershell
python demo_gemini_cli.py
```

---

## 🚀 Windows-Specific Features

### 1. Context Menu Integration (Right-Click)

**Add "Analyze with SampleMind AI" to right-click menu:**

```powershell
# Create registry file
@"
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\SystemFileAssociations\.wav\shell\SampleMind]
@="Analyze with SampleMind AI"
"Icon"="C:\\Path\\To\\samplemind-ai-v6\\assets\\icon.ico"

[HKEY_CLASSES_ROOT\SystemFileAssociations\.wav\shell\SampleMind\command]
@="\"C:\\Path\\To\\samplemind-ai-v6\\.venv\\Scripts\\python.exe\" \"C:\\Path\\To\\samplemind-ai-v6\\main.py\" analyze \"%1\""
"@ | Out-File -FilePath samplemind_context.reg -Encoding UTF8

# Import registry file
regedit /s samplemind_context.reg
```

### 2. Windows Terminal Integration

**Create Windows Terminal profile:**

```json
{
    "name": "SampleMind AI",
    "commandline": "cmd.exe /k cd /d C:\\Path\\To\\samplemind-ai-v6 && .venv\\Scripts\\activate && python main.py",
    "icon": "C:\\Path\\To\\samplemind-ai-v6\\assets\\icon.png",
    "colorScheme": "One Half Dark",
    "startingDirectory": "C:\\Path\\To\\samplemind-ai-v6"
}
```

Add to: `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_*\LocalState\settings.json`

### 3. Start Menu Shortcut

```powershell
# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\SampleMind AI.lnk")
$Shortcut.TargetPath = "C:\Path\To\samplemind-ai-v6\.venv\Scripts\python.exe"
$Shortcut.Arguments = "C:\Path\To\samplemind-ai-v6\main.py"
$Shortcut.WorkingDirectory = "C:\Path\To\samplemind-ai-v6"
$Shortcut.IconLocation = "C:\Path\To\samplemind-ai-v6\assets\icon.ico"
$Shortcut.Description = "AI-Powered Music Production Assistant"
$Shortcut.Save()

# Move to Start Menu
Move-Item "$Home\Desktop\SampleMind AI.lnk" "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\"
```

### 4. PowerShell Alias

```powershell
# Add to PowerShell profile
notepad $PROFILE

# Add these lines:
function Start-SampleMind {
    Set-Location "C:\Path\To\samplemind-ai-v6"
    .\.venv\Scripts\activate
    python main.py $args
}

Set-Alias smai Start-SampleMind

# Reload profile
. $PROFILE

# Now use:
smai
smai analyze song.wav
smai --demo
```

---

## 🎨 DAW Integration

### FL Studio Integration (Windows)
```powershell
# Analyze FL Studio samples
smai batch "C:\Program Files\Image-Line\FL Studio\Data\Patches\Packs"

# Analyze your projects
smai batch "C:\Users\YourName\Documents\Image-Line\FL Studio\Projects"
```

### Ableton Live Integration
```powershell
# Analyze Ableton samples
smai batch "C:\ProgramData\Ableton\Live 11 Suite\Resources\Core Library"
```

### Studio One Integration
```powershell
# Analyze Studio One sounds
smai batch "C:\Users\YourName\Documents\Studio One\Sounds"
```

---

## ⚡ Performance Optimization

### Windows Performance Settings
```powershell
# Set high performance power plan
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Increase process priority (run as admin)
wmic process where name="python.exe" CALL setpriority "high priority"
```

### Multi-Core Optimization
```powershell
# Set environment variables for parallel processing
$env:OMP_NUM_THREADS = "8"
$env:MKL_NUM_THREADS = "8"

# Restart CLI
python main.py
```

### GPU Acceleration (NVIDIA)
```powershell
# Install CUDA Toolkit
winget install Nvidia.CUDA

# Install PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

---

## 📊 System Requirements

### Minimum
- Windows 10 (version 1809+) / Windows 11
- Python 3.11+
- 4GB RAM
- 2GB disk space
- Internet connection for AI APIs

### Recommended
- Windows 11 (latest)
- Python 3.11+
- 8GB RAM (16GB for large batches)
- SSD storage
- NVIDIA GPU (optional, for acceleration)
- Multiple CPU cores

### Tested Systems
✅ Windows 11 Pro (22H2, 23H2)
✅ Windows 10 Pro (21H2, 22H2)
✅ Windows 11 Home
✅ Windows Server 2022

---

## 🐛 Troubleshooting

### Python Not Found
```powershell
# Add Python to PATH
$env:Path += ";C:\Users\YourName\AppData\Local\Programs\Python\Python311"
$env:Path += ";C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts"

# Verify
python --version
```

### PowerShell Execution Policy
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single script
PowerShell.exe -ExecutionPolicy Bypass -File .\scripts\windows_setup.ps1
```

### File Explorer Dialogs Not Appearing
```powershell
# Install/Repair Tkinter
pip uninstall tk
pip install tk --no-cache-dir

# Test Tkinter
python -c "import tkinter; print('Tkinter OK')"
```

### Audio Library Errors
```powershell
# Reinstall audio libraries
pip uninstall soundfile librosa
pip install soundfile librosa --no-cache-dir

# Download VC++ Redistributable if needed
winget install Microsoft.VCRedist.2015+.x64
```

### Permission Errors
```powershell
# Run PowerShell as Administrator for system-wide changes
# Or install in user directory (recommended)

# Fix .venv permissions
icacls .venv /grant:r "$($env:USERNAME):(OI)(CI)F" /T
```

### Firewall Issues
```powershell
# Add firewall rules for Python (run as admin)
New-NetFirewallRule -DisplayName "SampleMind AI - Python" `
    -Direction Outbound `
    -Program "C:\Path\To\.venv\Scripts\python.exe" `
    -Action Allow
```

---

## 🔐 Security Notes

### API Key Storage
```powershell
# Secure .env file
icacls .env /inheritance:r
icacls .env /grant:r "$($env:USERNAME):F"

# Use Windows Credential Manager (optional)
cmdkey /generic:SampleMind_Gemini /user:api /pass:your_api_key_here
```

### Antivirus Exclusions
Add to Windows Defender exclusions:
- `C:\Path\To\samplemind-ai-v6\.venv\`
- `C:\Path\To\samplemind-ai-v6\*.py`

---

## 📁 Recommended Folder Structure

```
C:\Users\YourName\
├── Music\
│   ├── SampleMind\
│   │   ├── Analysis Results\
│   │   ├── Processed Samples\
│   │   └── FL Studio Presets\
│   ├── FL Studio Projects\
│   └── Sample Library\
├── Documents\
│   └── SampleMind\
│       ├── Configs\
│       └── Logs\
└── Downloads\
    └── SampleMind Updates\
```

---

## 🎯 Quick Commands Reference

```powershell
# Setup
choco install python ffmpeg git          # Install dependencies
python -m venv .venv                      # Create environment
.\.venv\Scripts\activate                  # Activate

# Run
python main.py                            # Interactive CLI
python main.py --demo                     # Demo mode
python verify_setup.py                    # Verify setup

# Analyze
python main.py analyze song.wav           # Single file
python main.py batch .\Music\Beats        # Batch process

# Update
git pull                                  # Get updates
pip install -r requirements.txt           # Update packages
choco upgrade all                         # Update Chocolatey packages
```

---

## 💡 Windows Pro Tips

1. **Use Windows Terminal** - Better than CMD/PowerShell
2. **Pin to Taskbar** - Quick access to CLI
3. **Context Menu** - Right-click integration
4. **Scheduled Tasks** - Automate batch processing
5. **Network Drives** - Analyze files on NAS
6. **OneDrive** - Sync analysis results to cloud
7. **WSL2 Compatible** - Can run Linux version
8. **GPU Acceleration** - NVIDIA CUDA support

---

## 🔄 Windows-Specific Workflows

### Scheduled Batch Analysis
```powershell
# Create scheduled task
$Action = New-ScheduledTaskAction `
    -Execute "C:\Path\To\.venv\Scripts\python.exe" `
    -Argument "C:\Path\To\main.py batch C:\Music\NewSamples"

$Trigger = New-ScheduledTaskTrigger -Daily -At 3AM

Register-ScheduledTask `
    -TaskName "SampleMind Daily Analysis" `
    -Action $Action `
    -Trigger $Trigger
```

### Watch Folder (Auto-Analyze New Files)
```powershell
# PowerShell watcher script
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "C:\Users\YourName\Music\DropFolder"
$watcher.Filter = "*.wav"
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    python C:\Path\To\main.py analyze "$path"
}

Register-ObjectEvent $watcher "Created" -Action $action
```

---

## 📞 Support

### Windows-Specific Issues
- Check logs: `%APPDATA%\SampleMind\Logs\`
- Event Viewer: Filter Application logs
- Task Manager: Monitor CPU/RAM usage
- Resource Monitor: Check disk I/O

### Useful Commands
```powershell
# System info
systeminfo
Get-ComputerInfo

# Python info
python --version
pip list

# Audio devices
Get-PnpDevice -Class MEDIA
```

---

## 🌟 Exclusive Windows Features

✅ **Native File Explorer** - Windows 11 modern dialogs
✅ **Context Menu Integration** - Right-click analyze
✅ **Start Menu & Taskbar** - Quick access
✅ **Windows Terminal** - Modern CLI experience
✅ **Scheduled Tasks** - Automated workflows
✅ **Network Drive Support** - NAS/SMB integration
✅ **OneDrive Sync** - Cloud storage ready
✅ **CUDA GPU Acceleration** - NVIDIA graphics cards
✅ **WSL2 Compatible** - Run Linux version if needed

---

## 🎵 FL Studio Windows Integration

### Deep FL Studio Integration
```powershell
# Analyze FL Studio installation
smai batch "C:\Program Files\Image-Line\FL Studio"

# Watch FL Studio export folder
# (Auto-analyze new renders)
$watcher.Path = "C:\Users\YourName\Documents\Image-Line\FL Studio\Audio\Rendered"
```

---

**🪟 Professional AI music production on Windows!** 🎵✨

*Tested on: Windows 11 23H2, Windows 10 22H2*
