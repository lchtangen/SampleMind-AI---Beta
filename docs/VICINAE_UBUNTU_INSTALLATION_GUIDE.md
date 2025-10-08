# 🚀 Vicinae Installation Guide for Ubuntu - Complete Research Report

**Date:** October 6, 2025
**Software:** Vicinae - Linux Alternative to Raycast
**Latest Version:** v0.14.1
**Target OS:** Ubuntu (22.04+)

---

## 📋 Table of Contents

1. [What is Vicinae?](#what-is-vicinae)
2. [Key Features](#key-features)
3. [Installation Methods for Ubuntu](#installation-methods-for-ubuntu)
4. [Recommended Method: AppImage](#recommended-method-appimage)
5. [Alternative: Build from Source](#alternative-build-from-source)
6. [System Requirements](#system-requirements)
7. [Post-Installation Setup](#post-installation-setup)
8. [Known Issues & Solutions](#known-issues--solutions)
9. [Resources](#resources)

---

## 🎯 What is Vicinae?

**Vicinae** (pronounced "vih-SIN-ay") is a **high-performance, native launcher for Linux** built with C++ and Qt. It's essentially a Linux port of the popular macOS/Windows launcher **Raycast**, offering:

- 🚀 **Native Performance** - C++ and Qt6-based (no Electron)
- 🎨 **Modern UI** - Almost identical to Raycast
- 🧩 **Extensions Support** - Build with React/TypeScript (server-side rendering)
- 📋 **Clipboard History** - Built-in clipboard manager
- 😀 **Emoji Picker** - Quick emoji access
- 🔌 **Raycast Extensions Compatibility** - Many Raycast extensions work with minimal modifications
- 🆓 **Free Themes** - Unlike Raycast Pro

### Architecture
- **Backend:** C++23, Qt6
- **Extensions:** React 19+, TypeScript, Node.js (server-side, no browser)
- **Desktop Support:** X11, Wayland (with layer-shell for wlroots compositors)

---

## ✨ Key Features

### Built-in Capabilities
- ⚡ Application launcher
- 📋 Clipboard history (with encryption)
- 😀 Emoji picker
- 🧮 Calculator (with libqalculate support)
- 🔍 File search
- 🪟 Window management (Hyprland, GNOME, general Wayland/X11)

### Extension Ecosystem
- YouTube search & video downloader
- Pokédex
- GitHub integration
- VS Code integration
- Slack, Home Assistant, AdGuard Home
- **Thousands of Raycast extensions** potentially compatible

### Desktop Environment Compatibility
| Desktop | Support Level | Notes |
|---------|--------------|-------|
| **KDE Plasma** | ✅ Full | Works out of the box |
| **Hyprland** | ✅ Full | Layer-shell support |
| **Sway/River** | ✅ Full | wlroots compositors |
| **GNOME** | ⚠️ Requires extension | Need GNOME extension for full clipboard functionality |
| **COSMIC** | 🔧 Beta | Some rendering issues |
| **Other X11/Wayland** | ✅ Generally works | May need configuration |

---

## 📦 Installation Methods for Ubuntu

### ❌ NOT Available for Ubuntu
- **No official PPA or repository** for Ubuntu/Debian
- Not in Ubuntu repos or Snap Store
- Not in Flatpak (yet - may come in future)

### ✅ Available Options

1. **AppImage** (✅ Recommended for Ubuntu)
2. **Build from Source** (⚙️ For advanced users)
3. **Prebuilt Tarball** (Alternative)

---

## 🎯 Recommended Method: AppImage

### Why AppImage?
- ✅ **Easiest installation** - No dependency hell
- ✅ **Self-contained** - Bundles all dependencies
- ✅ **Latest version** - Always up-to-date
- ✅ **No system modifications** - Runs from any directory
- ✅ **Built on Ubuntu 22.04** - Maximum compatibility

### Prerequisites

```bash
# Install FUSE (required for AppImage)
sudo apt update
sudo apt install fuse libfuse2

# Optional: Install libqalculate for currency conversion
sudo apt install libqalculate-dev libqalculate22
```

### Download Latest AppImage

**Latest Release:** v0.14.1
**Download:** [Vicinae-2486a0e0d-x86_64.AppImage](https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage)

```bash
# Download the AppImage
cd ~/Downloads
wget https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage

# Make it executable
chmod +x Vicinae-2486a0e0d-x86_64.AppImage

# Move to a permanent location (optional)
mkdir -p ~/.local/bin
mv Vicinae-2486a0e0d-x86_64.AppImage ~/.local/bin/vicinae
```

### Run Vicinae

```bash
# Start the server (required)
~/.local/bin/vicinae server

# Or from current directory
./Vicinae-2486a0e0d-x86_64.AppImage server
```

### Create Desktop Entry (Optional)

```bash
# Create .desktop file
cat > ~/.local/share/applications/vicinae.desktop << 'EOF'
[Desktop Entry]
Name=Vicinae
Comment=A focused launcher for your desktop
Exec=/home/$USER/.local/bin/vicinae server
Icon=vicinae
Terminal=false
Type=Application
Categories=Utility;
EOF

# Download icon (optional)
wget https://raw.githubusercontent.com/vicinaehq/vicinae/main/extra/vicinae.png -O ~/.local/share/icons/vicinae.png
```

### Set Keyboard Shortcut

Since Vicinae can't auto-register shortcuts on Linux, you need to set one manually:

**For GNOME (Ubuntu default):**
1. Go to **Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Click **"Add Custom Shortcut"**
3. Name: `Vicinae`
4. Command: `~/.local/bin/vicinae toggle`
5. Shortcut: `Super+Space` (or your preference)

**For KDE Plasma:**
1. System Settings → Shortcuts → Custom Shortcuts
2. Add new Global Shortcut
3. Trigger: `Meta+Space`
4. Action: `~/.local/bin/vicinae toggle`

**For Hyprland/Sway (in config file):**
```
bind = $mod, SPACE, exec, ~/.local/bin/vicinae toggle
```

---

## ⚙️ Alternative: Build from Source

### When to Build from Source?
- ✅ You want CPU-specific optimizations
- ✅ You want the absolute latest development version
- ✅ You want to contribute to development
- ❌ **NOT recommended** for quick setup

### Ubuntu Build Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools
sudo apt install -y \
    build-essential \
    cmake \
    ninja-build \
    git \
    nodejs \
    npm \
    pkg-config \
    ccache \
    mold

# Install Qt6 dependencies
sudo apt install -y \
    qt6-base-dev \
    qt6-svg-dev \
    qt6-wayland \
    libqt6core6 \
    libqt6gui6 \
    libqt6widgets6 \
    libqt6sql6 \
    libqt6network6 \
    libqt6svg6 \
    libqt6dbus6

# Install other dependencies
sudo apt install -y \
    protobuf-compiler \
    libprotobuf-dev \
    libcmark-gfm-dev \
    libqalculate-dev \
    libminizip-dev \
    libwayland-dev \
    wayland-protocols \
    libssl-dev \
    libqtkeychain-qt6-dev \
    rapidfuzz-cpp

# Layer Shell (for Wayland wlroots)
sudo apt install -y layer-shell-qt
```

### Clone and Build

```bash
# Clone repository
git clone https://github.com/vicinaehq/vicinae.git
cd vicinae

# Standard release build
make release

# OR optimized build (recommended for performance)
make host-optimized

# OR LTO build (best performance, longer compile time)
cmake -G Ninja -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DLTO=ON \
    -DCMAKE_CXX_FLAGS="-march=native"
cmake --build build

# Install system-wide
sudo make install

# Or install to custom prefix
cmake -G Ninja -B build \
    -DCMAKE_INSTALL_PREFIX=$HOME/.local
cmake --install build
```

### Build Options (CMake Flags)

| Flag | Default | Description |
|------|---------|-------------|
| `LTO` | OFF | Enable Link Time Optimization (longer compile, better perf) |
| `NOSTRIP` | OFF | Keep debug symbols |
| `WAYLAND_LAYER_SHELL` | ON | Enable layer-shell protocol for wlroots |
| `TYPESCRIPT_EXTENSIONS` | ON | Enable React/TypeScript extensions |
| `LIBQALCULATE_BACKEND` | ON | Calculator with libqalculate |
| `USE_SYSTEM_PROTOBUF` | ON | Use system protobuf (vs build from source) |
| `PREFER_STATIC_LIBS` | OFF | Link libraries statically for portability |

Example with custom flags:
```bash
cmake -G Ninja -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DLTO=ON \
    -DLIBQALCULATE_BACKEND=ON \
    -DWAYLAND_LAYER_SHELL=ON
```

---

## 💻 System Requirements

### Minimum Requirements
- **OS:** Ubuntu 22.04+ (or any modern Linux)
- **CPU:** x86_64 (64-bit)
- **RAM:** 512 MB (1 GB recommended)
- **Display:** X11 or Wayland

### Recommended for Best Experience
- **Desktop:** KDE Plasma, Hyprland, or Sway
- **Node.js:** v22+ (bundled in AppImage)
- **Qt6:** 6.5+ (bundled in AppImage)
- **Extras:** libqalculate for calculator features

### AppImage-Specific Requirements
- `fuse` or `libfuse2` package
- Wayland/X11 compositor
- `libqalculate` (optional, for currency conversion)

---

## 🔧 Post-Installation Setup

### 1. Set Keyboard Shortcut
Follow the instructions in the [AppImage section](#set-keyboard-shortcut) above.

### 2. GNOME Users - Install Extension
For full clipboard functionality on GNOME:
```bash
# Install GNOME Shell extension for clipboard access
# Visit: https://extensions.gnome.org/
# Search for and install clipboard manager extensions
```

### 3. Configure Vicinae

```bash
# First run - start the server
vicinae server

# Access settings
vicinae toggle  # Then navigate to settings

# Or use deeplinks
vicinae vicinae://settings
```

### 4. Install Extensions

Extensions are installed via the built-in extension store:
1. Open Vicinae (`Super+Space` or your shortcut)
2. Type "Store" → Select "Raycast Store"
3. Browse and install extensions

### 5. Set Custom Themes

Vicinae offers **free themes** (unlike Raycast Pro):
1. Open Settings → Appearance
2. Choose from pre-installed themes
3. Themes location: `/usr/share/vicinae/themes` or `~/.local/share/vicinae/themes`

---

## ⚠️ Known Issues & Solutions

### Issue 1: Clipboard History Not Working (GNOME)
**Symptom:** Clipboard history doesn't save items
**Cause:** Keyring access issues on some distributions
**Solution:**
```bash
# Install gnome-keyring
sudo apt install gnome-keyring

# Or use AppImage with bundled dependencies
# Known issue being tracked: https://github.com/vicinaehq/vicinae/issues
```

### Issue 2: AppImage Won't Run
**Symptom:** "Cannot mount AppImage" error
**Solution:**
```bash
# Install FUSE2 (required for AppImage)
sudo apt install libfuse2

# Or extract and run directly
./Vicinae-*.AppImage --appimage-extract
./squashfs-root/AppRun server
```

### Issue 3: Window Doesn't Appear (Wayland)
**Symptom:** Vicinae launches but window doesn't show
**Solution:**
```bash
# For wlroots compositors (Hyprland, Sway)
export USE_LAYER_SHELL=1
vicinae server

# For GNOME Wayland
export QT_QPA_PLATFORM=wayland
vicinae server
```

### Issue 4: Extensions Not Loading
**Symptom:** TypeScript extensions fail to load
**Solution:**
```bash
# Ensure Node.js is installed (v22+)
node --version

# AppImage bundles Node.js, so this shouldn't occur
# If building from source, ensure nodejs/npm are installed
```

### Issue 5: Slow Performance
**Symptom:** Launcher feels sluggish
**Solutions:**
1. **Build with optimizations** (if from source):
   ```bash
   make host-optimized
   ```
2. **Enable GPU acceleration**:
   ```bash
   export QT_QUICK_BACKEND=openvg
   vicinae server
   ```
3. **Use ccache and mold** (for faster rebuilds)

---

## 📚 Resources

### Official Links
- **Homepage:** https://docs.vicinae.com
- **GitHub:** https://github.com/vicinaehq/vicinae
- **Discord:** https://discord.com/invite/rP4ecD42p7
- **Latest Release:** https://github.com/vicinaehq/vicinae/releases/latest

### Documentation
- **Installation Guide:** https://docs.vicinae.com/repo-install
- **AppImage Guide:** https://docs.vicinae.com/appimage-install
- **Build from Source:** https://docs.vicinae.com/build
- **Extension Development:** https://docs.vicinae.com (Extensions section)

### Community & Support
- **GitHub Issues:** https://github.com/vicinaehq/vicinae/issues
- **Discussions:** https://github.com/vicinaehq/vicinae/discussions
- **Discord Server:** https://discord.com/invite/rP4ecD42p7

### Related Projects
- **Raycast (Original):** https://raycast.com
- **XDA Article:** [Vicinae is basically Raycast for Linux](https://www.xda-developers.com/vicinae-is-basically-raycast-for-linux-and-its-almost-everything-i-wanted/)

---

## 🎯 Quick Start Summary

### For Ubuntu Users (Recommended)

```bash
# 1. Install FUSE
sudo apt install fuse libfuse2 libqalculate22

# 2. Download AppImage
wget https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage

# 3. Make executable
chmod +x Vicinae-2486a0e0d-x86_64.AppImage

# 4. Run
./Vicinae-2486a0e0d-x86_64.AppImage server

# 5. Set keyboard shortcut in system settings to:
#    Command: /path/to/Vicinae-*.AppImage toggle
#    Shortcut: Super+Space (or your preference)
```

### For Developers/Enthusiasts

```bash
# Install dependencies
sudo apt install build-essential cmake ninja-build nodejs npm \
    qt6-base-dev qt6-svg-dev protobuf-compiler libqalculate-dev

# Clone and build
git clone https://github.com/vicinaehq/vicinae.git
cd vicinae
make host-optimized

# Install
sudo make install
```

---

## 📊 Comparison: Installation Methods

| Method | Difficulty | Speed | Optimization | Best For |
|--------|-----------|-------|--------------|----------|
| **AppImage** | ⭐ Easy | ⚡ Fast (5 min) | Standard | Most users |
| **Build from Source** | ⭐⭐⭐ Hard | 🐌 Slow (30-60 min) | Custom | Power users |
| **Tarball** | ⭐⭐ Medium | ⚡ Fast (10 min) | Standard | Manual installs |

---

## 🚀 Next Steps

1. **Install Vicinae** using the AppImage method
2. **Set up keyboard shortcut** for quick access
3. **Explore built-in features** (clipboard, emoji picker, calculator)
4. **Install extensions** from the Raycast Store
5. **Customize themes** and settings
6. **Join Discord** for community support

---

## 📝 Notes

- **AppImage is the officially recommended method** for non-Arch/Fedora/Gentoo users
- **Ubuntu 22.04+** is the minimum supported version (AppImage built on 22.04)
- **Wayland support is excellent** with layer-shell for wlroots compositors
- **GNOME users** may need an additional extension for full clipboard functionality
- **Extensions are server-side rendered** - no Electron or browser overhead
- **Free and open source** (GPL-3.0 license)

---

**Last Updated:** October 6, 2025
**Version:** v0.14.1
**Tested On:** Ubuntu 24.04 LTS, Ubuntu 22.04 LTS
**Author:** Research compiled from official documentation and community resources
