# 📚 Vicinae Installation Research - Documentation Index

**Research Date:** October 6, 2025
**Software:** Vicinae v0.14.1 - Linux Alternative to Raycast
**Target Platform:** Ubuntu 22.04+
**Status:** ✅ Complete

---

## 📖 Documentation Files

This research project contains comprehensive documentation for installing and using Vicinae on Ubuntu. All files are located in the `/docs` directory.

### 1. 📋 Quick Start
- **[VICINAE_RESEARCH_SUMMARY.md](./VICINAE_RESEARCH_SUMMARY.md)**
  - Executive summary
  - Best installation method
  - Quick reference commands
  - Key findings at a glance
  - **Read this first!**

### 2. 🚀 Installation Guide
- **[VICINAE_README.md](./VICINAE_README.md)**
  - Overview of Vicinae features
  - Installation methods comparison
  - Quick start instructions
  - Post-installation setup
  - Troubleshooting tips

### 3. 📚 Complete Manual
- **[VICINAE_UBUNTU_INSTALLATION_GUIDE.md](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md)**
  - **10,000+ word comprehensive guide**
  - Detailed installation instructions
  - AppImage setup (recommended)
  - Build from source guide
  - System requirements
  - Desktop environment setup
  - Extension management
  - Known issues and solutions
  - Resources and links

### 4. 🛠️ Installation Script
- **[../scripts/install-vicinae.sh](../scripts/install-vicinae.sh)**
  - Automated installation script
  - Dependency checking
  - AppImage download
  - Desktop entry creation
  - Keyboard shortcut instructions
  - **Run with:** `bash scripts/install-vicinae.sh`

---

## 🎯 Recommended Reading Order

### For Quick Setup (5 minutes)
1. Read: [VICINAE_RESEARCH_SUMMARY.md](./VICINAE_RESEARCH_SUMMARY.md) - Get the executive summary
2. Run: `bash scripts/install-vicinae.sh` - Automated installation
3. Follow: On-screen keyboard shortcut instructions

### For Detailed Understanding (15 minutes)
1. Read: [VICINAE_README.md](./VICINAE_README.md) - Features and overview
2. Read: [VICINAE_UBUNTU_INSTALLATION_GUIDE.md](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md) - Complete guide
3. Reference: Script for automated setup if needed

### For Advanced Users / Developers
1. Read: Build from Source section in [VICINAE_UBUNTU_INSTALLATION_GUIDE.md](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md)
2. Review: Build flags and optimization options
3. Check: GitHub repository for latest development

---

## 🔍 Research Summary

### What We Found

**Best Installation Method for Ubuntu:**
- ✅ **AppImage** (recommended)
- ❌ No PPA/repository available
- ❌ No Snap/Flatpak available
- ⚙️ Build from source (for advanced users)

**Latest Version:**
- **v0.14.1** (released October 3, 2025)
- AppImage: 91.2 MB
- Tarball: 41.0 MB

**Key Requirements:**
- Ubuntu 22.04 or newer
- FUSE2 (`libfuse2` package)
- Optional: libqalculate for calculator

**Desktop Environment Support:**
- ✅ KDE Plasma - Full support
- ✅ Hyprland/Sway - Full support
- ⚠️ GNOME - Requires extension
- ✅ Other X11/Wayland - Generally works

---

## 📥 Quick Install Commands

### Method 1: Automated (Recommended)
```bash
# Run the installation script
bash scripts/install-vicinae.sh
```

### Method 2: Manual AppImage
```bash
# Install dependencies
sudo apt install fuse libfuse2 libqalculate22

# Download AppImage
wget https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage

# Make executable
chmod +x Vicinae-*.AppImage

# Run
./Vicinae-*.AppImage server
```

### Method 3: Build from Source (Advanced)
```bash
# Install build dependencies
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

## 📊 File Sizes

| File | Size | Purpose |
|------|------|---------|
| VICINAE_RESEARCH_SUMMARY.md | ~5 KB | Quick reference |
| VICINAE_README.md | ~15 KB | Overview & quick start |
| VICINAE_UBUNTU_INSTALLATION_GUIDE.md | ~50 KB | Complete manual |
| install-vicinae.sh | ~8 KB | Automated installer |
| **Total Documentation** | **~78 KB** | Complete package |

---

## 🔗 External Resources

### Official Links
- **Homepage:** https://docs.vicinae.com
- **GitHub:** https://github.com/vicinaehq/vicinae
- **Releases:** https://github.com/vicinaehq/vicinae/releases
- **Discord:** https://discord.com/invite/rP4ecD42p7

### Download Links (v0.14.1)
- **AppImage:** [Vicinae-2486a0e0d-x86_64.AppImage](https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage) (91.2 MB)
- **Tarball:** [vicinae-linux-x86_64-v0.14.1.tar.gz](https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/vicinae-linux-x86_64-v0.14.1.tar.gz) (41.0 MB)
- **Source:** [GitHub Repository](https://github.com/vicinaehq/vicinae)

### Documentation
- **Installation Guide:** https://docs.vicinae.com/repo-install
- **AppImage Guide:** https://docs.vicinae.com/appimage-install
- **Build Guide:** https://docs.vicinae.com/build
- **GNOME Setup:** https://docs.vicinae.com/gnome-support

---

## ✨ Features Overview

### Core Features
- 🚀 Native C++/Qt6 application (no Electron)
- 📋 Clipboard history with encryption
- 😀 Emoji picker
- 🧮 Calculator (with libqalculate)
- 🔍 File and application search
- 🪟 Window management
- 🎨 Themeable interface (free themes)

### Extension System
- React/TypeScript extensions (server-side)
- Compatible with many Raycast extensions
- Extension store built-in
- Easy extension development
- No browser/Electron required

### Desktop Integration
- X11 and Wayland support
- Layer-shell for wlroots compositors
- GNOME extension support
- KDE Plasma integration
- Custom keyboard shortcuts

---

## 🛠️ Troubleshooting Quick Reference

### Common Issues

**AppImage Won't Run:**
```bash
sudo apt install libfuse2
```

**Clipboard Not Working (GNOME):**
```bash
sudo apt install gnome-keyring
```

**Window Doesn't Appear (Wayland):**
```bash
export USE_LAYER_SHELL=1
vicinae server
```

**Extensions Not Loading:**
```bash
# Ensure Node.js is installed
node --version  # Should be v22+
```

---

## 📞 Support & Community

### Getting Help
1. **Documentation:** Start with this index, then read relevant docs
2. **GitHub Issues:** https://github.com/vicinaehq/vicinae/issues
3. **Discord Community:** https://discord.com/invite/rP4ecD42p7
4. **Discussions:** https://github.com/vicinaehq/vicinae/discussions

### Contributing
- Report bugs: GitHub Issues
- Suggest features: GitHub Discussions
- Contribute code: GitHub Pull Requests
- Improve docs: Fork and PR this repository

---

## 📝 Version Information

| Item | Version | Date |
|------|---------|------|
| Vicinae | v0.14.1 | October 3, 2025 |
| Documentation | 1.0.0 | October 6, 2025 |
| Ubuntu Tested | 22.04, 24.04 | October 2025 |
| Research Status | ✅ Complete | October 6, 2025 |

---

## 🎯 Next Steps

1. **Choose your installation method:**
   - Quick setup: Run `bash scripts/install-vicinae.sh`
   - Manual: Follow [VICINAE_README.md](./VICINAE_README.md)
   - Detailed: Read [VICINAE_UBUNTU_INSTALLATION_GUIDE.md](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md)

2. **Set up keyboard shortcut:**
   - GNOME: Settings → Keyboard → Custom Shortcuts
   - KDE: System Settings → Shortcuts
   - Hyprland/Sway: Edit config file

3. **Start using Vicinae:**
   - Press your keyboard shortcut
   - Explore built-in features
   - Install extensions from store
   - Customize themes and settings

4. **Join the community:**
   - Discord: https://discord.com/invite/rP4ecD42p7
   - GitHub: Star the repository
   - Share your experience

---

**Documentation Maintained By:** SampleMind AI Development Team
**Last Updated:** October 6, 2025
**Next Review:** November 2025 (or when new version released)

---

## 📄 License

This documentation is created as part of the SampleMind AI project research. Vicinae itself is licensed under GPL-3.0. See the [official repository](https://github.com/vicinaehq/vicinae) for software license details.
