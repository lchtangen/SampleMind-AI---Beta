# 🚀 Vicinae - Complete Installation Resources

This directory contains complete research and installation resources for **Vicinae**, a high-performance Linux alternative to Raycast.

## 📋 What's Included

### 1. **Complete Installation Guide**
- **File:** [`VICINAE_UBUNTU_INSTALLATION_GUIDE.md`](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md)
- Comprehensive 10,000+ word guide covering:
  - What Vicinae is and its features
  - Installation methods (AppImage, build from source)
  - System requirements
  - Post-installation setup
  - Troubleshooting
  - Resources and documentation

### 2. **Automated Installation Script**
- **File:** [`../scripts/install-vicinae.sh`](../scripts/install-vicinae.sh)
- One-command installation for Ubuntu:
  ```bash
  bash scripts/install-vicinae.sh
  ```
- Features:
  - ✅ Dependency installation (FUSE, libqalculate)
  - ✅ AppImage download (latest v0.14.1)
  - ✅ Desktop entry creation
  - ✅ Icon setup
  - ✅ Desktop environment detection
  - ✅ Keyboard shortcut instructions

## 🎯 Quick Start (Ubuntu)

### Option 1: Automated Installation (Recommended)

```bash
# Run the installation script
bash scripts/install-vicinae.sh
```

### Option 2: Manual Installation

```bash
# 1. Install dependencies
sudo apt install fuse libfuse2 libqalculate22

# 2. Download AppImage
wget https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage

# 3. Make executable and run
chmod +x Vicinae-2486a0e0d-x86_64.AppImage
./Vicinae-2486a0e0d-x86_64.AppImage server

# 4. Set keyboard shortcut (System Settings → Keyboard)
#    Command: /path/to/Vicinae-*.AppImage toggle
#    Shortcut: Super+Space
```

## 📚 What is Vicinae?

**Vicinae** (pronounced "vih-SIN-ay") is a **native, high-performance launcher for Linux** - essentially a Linux port of the popular macOS/Windows tool Raycast.

### Key Features
- 🚀 **Native C++/Qt6** - No Electron bloat
- 🎨 **Modern UI** - Almost identical to Raycast
- 📋 **Clipboard History** - Built-in with encryption
- 😀 **Emoji Picker** - Quick emoji access
- 🧩 **Extensions** - React/TypeScript (server-side)
- 🔌 **Raycast Compatible** - Many extensions work
- 🆓 **Free Themes** - Unlike Raycast Pro

### Supported Desktop Environments
- ✅ **KDE Plasma** - Full support
- ✅ **Hyprland/Sway** - Full support (layer-shell)
- ⚠️ **GNOME** - Requires extension for clipboard
- ✅ **Other X11/Wayland** - Generally works

## 📖 Documentation

### Included Docs
- **[Full Installation Guide](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md)** - Complete 10K+ word guide
- **[Installation Script](../scripts/install-vicinae.sh)** - Automated installer

### Official Resources
- **Homepage:** https://docs.vicinae.com
- **GitHub:** https://github.com/vicinaehq/vicinae
- **Discord:** https://discord.com/invite/rP4ecD42p7
- **Latest Release:** https://github.com/vicinaehq/vicinae/releases/latest

### Installation Methods by Distro

| Distribution | Method | Link |
|--------------|--------|------|
| **Ubuntu** | AppImage (recommended) | [Guide](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md#recommended-method-appimage) |
| **Arch Linux** | AUR (`vicinae`, `vicinae-bin`, `vicinae-git`) | [AUR](https://aur.archlinux.org/packages/vicinae) |
| **Fedora** | COPR (`gvalkov/vicinae`) | [COPR](https://copr.fedorainfracloud.org/coprs/gvalkov/vicinae/) |
| **Gentoo** | Overlay (`jaredallard/overlay`) | [Overlay](https://github.com/jaredallard/overlay) |
| **NixOS** | Nix package | `nix-shell -p vicinae` |

## 🔧 System Requirements

### Minimum
- **OS:** Ubuntu 22.04+ (or any modern Linux)
- **CPU:** x86_64 (64-bit)
- **RAM:** 512 MB (1 GB recommended)
- **Display:** X11 or Wayland

### Required Packages (AppImage)
- `fuse` or `libfuse2`
- `libqalculate22` (optional, for calculator)

## 🚀 Post-Installation

### 1. Start the Server
```bash
vicinae server
```

### 2. Set Keyboard Shortcut
**GNOME/Ubuntu:**
- Settings → Keyboard → Keyboard Shortcuts
- Add Custom: `vicinae toggle` → `Super+Space`

**KDE Plasma:**
- System Settings → Shortcuts → Custom Shortcuts
- Add: `vicinae toggle` → `Meta+Space`

**Hyprland/Sway:**
```
bind = $mod, SPACE, exec, vicinae toggle
```

### 3. Explore Features
- Open launcher: `Super+Space`
- Clipboard history: Type "clipboard"
- Emoji picker: Type "emoji"
- Extension store: Type "store"
- Settings: Type "settings"

## ⚠️ Known Issues

### Issue: Clipboard Not Working (GNOME)
**Solution:** Install GNOME keyring
```bash
sudo apt install gnome-keyring
```

### Issue: AppImage Won't Run
**Solution:** Install FUSE2
```bash
sudo apt install libfuse2
```

### Issue: Window Doesn't Appear (Wayland)
**Solution:** Set environment variable
```bash
export USE_LAYER_SHELL=1
vicinae server
```

## 🛠️ Development & Building

### Build from Source (Ubuntu)

```bash
# Install dependencies
sudo apt install build-essential cmake ninja-build nodejs npm \
    qt6-base-dev qt6-svg-dev protobuf-compiler libqalculate-dev \
    libcmark-gfm-dev libminizip-dev libwayland-dev libqtkeychain-qt6-dev

# Clone and build
git clone https://github.com/vicinaehq/vicinae.git
cd vicinae
make release  # or 'make host-optimized' for best performance

# Install
sudo make install
```

### Build Options
- `make release` - Standard release build
- `make host-optimized` - CPU-optimized build
- `make debug` - Debug build with symbols
- `make portable` - Portable build (static libs)

## 📊 Installation Method Comparison

| Method | Difficulty | Speed | Optimization | Best For |
|--------|-----------|-------|--------------|----------|
| **AppImage** | ⭐ Easy | ⚡ 5 min | Standard | Most users |
| **Build from Source** | ⭐⭐⭐ Hard | 🐌 30-60 min | Custom | Power users |
| **Script (Automated)** | ⭐ Easy | ⚡ 5 min | Standard | Ubuntu users |

## 🎯 Research Summary

### What We Researched
1. ✅ **Official Documentation** - docs.vicinae.com
2. ✅ **GitHub Repository** - vicinaehq/vicinae
3. ✅ **Latest Release** - v0.14.1 (Oct 3, 2025)
4. ✅ **XDA Article** - In-depth review
5. ✅ **Build Instructions** - CMake, dependencies
6. ✅ **Desktop Environment Support** - KDE, GNOME, Hyprland, etc.

### Key Findings
- **Best Method for Ubuntu:** AppImage (self-contained, no dependency hell)
- **Latest Version:** v0.14.1 (released Oct 3, 2025)
- **Ubuntu Support:** 22.04+ via AppImage, no official PPA
- **Dependencies:** FUSE2 required, libqalculate optional
- **Desktop Support:** Excellent on KDE/Hyprland, requires extension on GNOME
- **Extension Ecosystem:** Compatible with many Raycast extensions
- **Performance:** Native C++/Qt6, significantly faster than Electron alternatives

## 📝 Quick Reference Commands

```bash
# Installation (automated)
bash scripts/install-vicinae.sh

# Manual AppImage installation
wget https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage
chmod +x Vicinae-*.AppImage
./Vicinae-*.AppImage server

# Usage
vicinae server           # Start server
vicinae toggle           # Toggle launcher
vicinae --help          # Show help
vicinae --version       # Show version

# Troubleshooting
vicinae doctor          # Check system compatibility
```

## 🌟 Why Vicinae?

- ✅ **Free and Open Source** (GPL-3.0)
- ✅ **Native Linux Performance** (C++/Qt6)
- ✅ **No Electron Bloat** (unlike many alternatives)
- ✅ **Raycast-Compatible Extensions** (huge ecosystem)
- ✅ **Active Development** (regular releases)
- ✅ **Free Themes** (no paid features)
- ✅ **Privacy-Focused** (local-first, encrypted clipboard)

## 📧 Support

- **Documentation:** https://docs.vicinae.com
- **GitHub Issues:** https://github.com/vicinaehq/vicinae/issues
- **Discord Community:** https://discord.com/invite/rP4ecD42p7
- **Discussions:** https://github.com/vicinaehq/vicinae/discussions

---

**Last Updated:** October 6, 2025
**Vicinae Version:** v0.14.1
**Documentation Version:** 1.0.0
**Tested On:** Ubuntu 24.04 LTS, Ubuntu 22.04 LTS
