# 📊 Vicinae Research Summary - Quick Reference

**Date:** October 6, 2025
**Research Topic:** Best Vicinae installation method for Ubuntu
**Latest Version:** v0.14.1 (released Oct 3, 2025)
**Status:** ✅ Research Complete

---

## 🎯 Executive Summary

**Vicinae** is a high-performance, native Linux launcher (Raycast alternative) built with C++ and Qt6. For **Ubuntu users**, the **AppImage method is the best and recommended installation option**.

---

## ✅ Best Solution for Ubuntu

### Recommended: AppImage Installation

**Why AppImage?**
- ✅ **Easiest installation** (no dependency conflicts)
- ✅ **Self-contained** (bundles all dependencies)
- ✅ **Latest version** available
- ✅ **No system modifications** required
- ✅ **Works on Ubuntu 22.04+**

### Quick Install (3 Commands)

```bash
# 1. Install FUSE (AppImage requirement)
sudo apt install fuse libfuse2 libqalculate22

# 2. Download and make executable
wget https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage
chmod +x Vicinae-*.AppImage

# 3. Run
./Vicinae-*.AppImage server
```

### Or Use Automated Script

```bash
# One-command installation
bash scripts/install-vicinae.sh
```

---

## 📦 Installation Options Comparison

| Method | Ubuntu Support | Difficulty | Time | Recommended |
|--------|---------------|-----------|------|------------|
| **AppImage** | ✅ Yes (22.04+) | ⭐ Easy | 5 min | ✅ **YES** |
| **Build from Source** | ✅ Yes | ⭐⭐⭐ Hard | 30-60 min | For developers only |
| **PPA/Repository** | ❌ Not available | N/A | N/A | ❌ No |
| **Snap** | ❌ Not available | N/A | N/A | ❌ No |
| **Flatpak** | ❌ Not available | N/A | N/A | ❌ No |

---

## 🔍 Research Findings

### What is Vicinae?
- **Native Linux launcher** (C++23 + Qt6)
- **Raycast alternative** with similar UI/UX
- **Extension support** (React/TypeScript, server-side)
- **Built-in features:** clipboard history, emoji picker, calculator
- **Open source:** GPL-3.0 license

### Key Features
- 🚀 **Native performance** (no Electron)
- 📋 **Clipboard history** with encryption
- 😀 **Emoji picker**
- 🧮 **Calculator** (libqalculate)
- 🔌 **Raycast extensions** compatibility
- 🎨 **Free themes** (unlike Raycast Pro)
- 🪟 **Window management** (Hyprland, GNOME, etc.)

### Desktop Environment Support
| DE | Support | Notes |
|----|---------|-------|
| KDE Plasma | ✅ Full | Works out of box |
| Hyprland/Sway | ✅ Full | Layer-shell support |
| GNOME | ⚠️ Partial | Needs extension for clipboard |
| Other X11/Wayland | ✅ Good | Generally compatible |

---

## 📋 System Requirements

### Minimum (AppImage)
- **OS:** Ubuntu 22.04+
- **CPU:** x86_64 (64-bit)
- **RAM:** 512 MB
- **Required:** `fuse` or `libfuse2`
- **Optional:** `libqalculate22` (for calculator)

---

## 🚀 Post-Installation Setup

### 1. Set Keyboard Shortcut (Required)

**GNOME/Ubuntu:**
```
Settings → Keyboard → Keyboard Shortcuts
→ Add Custom Shortcut
→ Command: /path/to/Vicinae-*.AppImage toggle
→ Shortcut: Super+Space
```

**KDE Plasma:**
```
System Settings → Shortcuts → Custom Shortcuts
→ Add Global Shortcut
→ Action: /path/to/vicinae toggle
→ Trigger: Meta+Space
```

**Hyprland/Sway:**
```bash
bind = $mod, SPACE, exec, /path/to/vicinae toggle
```

### 2. First Run

```bash
# Start the server
vicinae server

# Toggle launcher (after setting shortcut)
Super+Space  # or your configured shortcut
```

---

## ⚠️ Known Issues & Solutions

### Issue 1: Clipboard Not Working (GNOME)
```bash
# Solution: Install GNOME keyring
sudo apt install gnome-keyring
```

### Issue 2: AppImage Won't Run
```bash
# Solution: Install FUSE2
sudo apt install libfuse2
```

### Issue 3: Window Doesn't Show (Wayland)
```bash
# Solution: Enable layer shell
export USE_LAYER_SHELL=1
vicinae server
```

---

## 📚 Documentation Created

### 1. **Complete Installation Guide**
- **File:** [`docs/VICINAE_UBUNTU_INSTALLATION_GUIDE.md`](./VICINAE_UBUNTU_INSTALLATION_GUIDE.md)
- **Length:** 10,000+ words
- **Covers:** Installation, troubleshooting, features, setup

### 2. **Automated Installation Script**
- **File:** [`scripts/install-vicinae.sh`](../scripts/install-vicinae.sh)
- **Features:** Auto-install, dependency check, desktop entry creation

### 3. **Quick Reference README**
- **File:** [`docs/VICINAE_README.md`](./VICINAE_README.md)
- **Purpose:** Quick start guide and resources

---

## 🔗 Resources

### Official Links
- **Homepage:** https://docs.vicinae.com
- **GitHub:** https://github.com/vicinaehq/vicinae
- **Latest Release:** https://github.com/vicinaehq/vicinae/releases/tag/v0.14.1
- **Discord:** https://discord.com/invite/rP4ecD42p7

### Download Links
- **AppImage (v0.14.1):** [Download](https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage)
- **Source Tarball:** [Download](https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/vicinae-linux-x86_64-v0.14.1.tar.gz)

### Community
- **GitHub Issues:** https://github.com/vicinaehq/vicinae/issues
- **Discussions:** https://github.com/vicinaehq/vicinae/discussions
- **Discord Community:** https://discord.com/invite/rP4ecD42p7

---

## 🎯 Final Recommendation

**For Ubuntu users, use the AppImage method:**

```bash
# Quick Install (Automated)
bash scripts/install-vicinae.sh

# Or Manual Install
sudo apt install fuse libfuse2 libqalculate22
wget https://github.com/vicinaehq/vicinae/releases/download/v0.14.1/Vicinae-2486a0e0d-x86_64.AppImage
chmod +x Vicinae-*.AppImage
./Vicinae-*.AppImage server
```

**Then set keyboard shortcut in System Settings:**
- Command: `/path/to/Vicinae-*.AppImage toggle`
- Shortcut: `Super+Space`

---

## 📊 Research Methodology

### Sources Used
1. ✅ **Official Documentation** (docs.vicinae.com)
2. ✅ **GitHub Repository** (vicinaehq/vicinae)
3. ✅ **Latest Release Info** (v0.14.1)
4. ✅ **XDA Developer Article** (detailed review)
5. ✅ **Build Instructions** (CMakeLists.txt, Makefile)
6. ✅ **Community Feedback** (GitHub issues/discussions)

### Tools Used
- GitHub MCP (repository search, code analysis)
- Brave Search MCP (web research)
- Web scraping (official documentation)
- Repository code analysis

---

## ✨ Key Takeaways

1. **AppImage is the best method** for Ubuntu (no PPA available)
2. **v0.14.1 is the latest stable** (released Oct 3, 2025)
3. **FUSE2 is required** for AppImage to work
4. **Keyboard shortcut must be set manually** (Linux limitation)
5. **GNOME users may need extra setup** (keyring for clipboard)
6. **Excellent Wayland support** (especially Hyprland/Sway)
7. **Free and open source** (GPL-3.0)
8. **Active development** (regular updates)

---

**Research Completed:** October 6, 2025
**Next Action:** Run `bash scripts/install-vicinae.sh` to install Vicinae
**Documentation:** All guides saved in `/docs` directory
