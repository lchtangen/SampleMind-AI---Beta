# 📖 SampleMind AI - User Guide

**Version:** 1.0 Beta  
**Last Updated:** 2025-10-04  
**Difficulty:** Beginner-Friendly 🟢

---

## 📑 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Step-by-Step Workflows](#step-by-step-workflows)
5. [Feature Deep Dives](#feature-deep-dives)
6. [Tips & Best Practices](#tips--best-practices)
7. [FAQ](#faq)

---

## 🎯 Introduction

Welcome to **SampleMind AI** - your AI-powered music production assistant! This guide will walk you through every feature, from uploading your first audio file to analyzing complex musical patterns.

### What Can SampleMind AI Do?

```
┌─────────────────────────────────────────────────────────┐
│  🎵 Audio Analysis        │  🎹 Pattern Detection      │
│  • Tempo (BPM) Detection  │  • Key & Scale Detection   │
│  • Genre Classification   │  • Chord Progressions      │
│  • Mood Analysis          │  • Instrument Recognition  │
└─────────────────────────────────────────────────────────┘
```

### Who Is This For?

- **Music Producers** - Analyze tracks and find samples
- **DJs** - Match tempos and keys for seamless mixing
- **Audio Engineers** - Deep dive into spectral analysis
- **Musicians** - Understand your compositions better
- **Hobbyists** - Learn about music production

---

## 🚀 Getting Started

### Your First 5 Minutes

```
┌──────┐     ┌──────┐     ┌──────┐     ┌──────┐     ┌──────┐
│ Sign │ →   │ Log  │ →   │Upload│ →   │Analyze│ →  │ View │
│  Up  │     │  In  │     │File  │     │Audio │     │Results│
└──────┘     └──────┘     └──────┘     └──────┘     └──────┘
  1 min        30 sec       1 min        2 min        30 sec
```

### Step 1: Create Your Account

**URL:** `http://localhost:3000/register`

![Screenshot Placeholder: Registration Page]

1. **Enter your email** - Use a valid email address
2. **Choose a username** - 3-50 characters, letters/numbers/underscores
3. **Create a strong password** 
   - Watch the password strength meter turn green
   - Minimum 8 characters
   - Include uppercase, lowercase, numbers, and symbols
4. **Agree to Terms** - Check the Terms of Service box
5. **Click "Create account"**

**Visual Password Strength Guide:**
```
Weak      Fair       Good      Strong
  │         │          │          │
  ▓         ▓▓         ▓▓▓        ▓▓▓▓▓▓
  🔴        🟠         🟡         🟢
```

**Example Strong Password:** `MusicPro2025!`

---

### Step 2: Log In

**URL:** `http://localhost:3000/login`

![Screenshot Placeholder: Login Page]

**Features:**
- ✅ **Remember Me** - Your username will be saved for next time
- 🔑 **Forgot Password?** - Reset via email

**Tips:**
- Enable "Remember Me" on trusted devices
- Use a password manager for security
- Bookmark the login page

---

### Step 3: Dashboard Overview

**URL:** `http://localhost:3000/dashboard`

![Screenshot Placeholder: Dashboard]

**Your Dashboard Shows:**

```
┌─────────────────────────────────────────────────────────┐
│                    📊 Your Statistics                    │
├──────────────┬──────────────┬──────────────┬────────────┤
│ Total Files  │  Analyzed    │  Storage     │ This Week  │
│     12       │     8        │   156 MB     │    +3      │
└──────────────┴──────────────┴──────────────┴────────────┘

┌─────────────────────────────────────────────────────────┐
│              🎵 Recent Uploads (Latest 5)                │
├─────────────────────────────────────────────────────────┤
│ 🎧 track_001.mp3          ✅ Analyzed      2 hours ago  │
│ 🎧 ambient_mix.wav        ⏳ Pending       5 hours ago  │
│ 🎧 drum_loop.wav          ✅ Analyzed      1 day ago    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    ⚡ Quick Actions                      │
│  [Upload New File]  [View Library]  [Settings]          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 User Interface Overview

### Navigation Bar

```
┌─────────────────────────────────────────────────────────────────┐
│  🎵 SampleMind AI     [Dashboard] [Upload] [Library] [Settings] │
│                                                   [User] [Logout]│
└─────────────────────────────────────────────────────────────────┘
```

**Always Available:**
- **Dashboard** 🏠 - Your home base
- **Upload** ⬆️ - Add new audio files
- **Library** 📚 - Browse all your files
- **Settings** ⚙️ - Account preferences
- **User Menu** 👤 - Profile & logout

---

## 📋 Step-by-Step Workflows

### Workflow 1: Upload and Analyze Audio

```
┌─────────────────────────────────────────────────────────┐
│                  UPLOAD & ANALYZE WORKFLOW               │
└─────────────────────────────────────────────────────────┘

Step 1: Navigate to Upload
   │
   ├──> Click "Upload" in navigation bar
   │
   V
Step 2: Select Your File
   │
   ├──> Click "Choose File" or drag & drop
   ├──> Supported: MP3, WAV, FLAC, OGG, M4A
   ├──> Max size: 50 MB
   │
   V
Step 3: Add Metadata (Optional)
   │
   ├──> Add tags: "electronic, upbeat, 128bpm"
   ├──> Add description
   │
   V
Step 4: Upload
   │
   ├──> Click "Upload"
   ├──> Watch progress bar
   │
   V
Step 5: Start Analysis
   │
   ├──> File appears in library
   ├──> Click "Analyze" button
   ├──> AI processing begins (30 sec - 5 min)
   │
   V
Step 6: View Results
   │
   ├──> Status changes to "✅ Analyzed"
   ├──> Click "View Analysis Results"
   └──> See tempo, key, mood, and more!
```

**Upload Page Visual:**
```
┌─────────────────────────────────────────────────────────┐
│              📤 Upload Audio File                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│     ┌─────────────────────────────────────────┐        │
│     │                                          │        │
│     │        🎵  Drag & Drop File Here         │        │
│     │              or Click to Browse          │        │
│     │                                          │        │
│     └─────────────────────────────────────────┘        │
│                                                          │
│  Tags: [electronic, upbeat                   ]          │
│  Description: [My latest track...            ]          │
│                                                          │
│              [Cancel]    [Upload File]                  │
└─────────────────────────────────────────────────────────┘
```

---

### Workflow 2: Browse Your Library

```
┌─────────────────────────────────────────────────────────┐
│                   LIBRARY WORKFLOW                       │
└─────────────────────────────────────────────────────────┘

Navigate to Library
   │
   V
Search & Filter
   │
   ├──> Type in search box: "electronic"
   ├──> Filter by format: MP3, WAV, etc.
   ├──> Filter by status: Analyzed / Pending
   │
   V
Select Files (Bulk Operations)
   │
   ├──> Click checkbox on each file
   ├──> Or click "Select All"
   │
   V
Perform Actions
   │
   ├──> Tag: Add tags to multiple files
   ├──> Export: Download files
   ├──> Delete: Remove files (with confirmation)
   │
   V
View Details
   │
   └──> Click "Details" on any file
        • File size, format, duration
        • Sample rate, bit depth
        • Tags and metadata
        • Analysis status
```

**Library Grid Visual:**
```
┌─────────────────────────────────────────────────────────┐
│  📚 Audio Library                     Search: [____]🔍  │
├─────────────────────────────────────────────────────────┤
│  ☐ Select All   |   3 selected   [Tag][Export][Delete] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │☑ 🎵      │  │☐ 🎵      │  │☑ 🎵      │             │
│  │track_001 │  │ambient   │  │drum_loop │             │
│  │5.2 MB    │  │10.5 MB   │  │3.1 MB    │             │
│  │✅Analyzed│  │⏳Pending │  │✅Analyzed│             │
│  │[Details] │  │[Analyze] │  │[Details] │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

### Workflow 3: Understanding Analysis Results

```
┌─────────────────────────────────────────────────────────┐
│               ANALYSIS RESULTS BREAKDOWN                 │
└─────────────────────────────────────────────────────────┘

Basic Info
   │
   ├──> BPM (Tempo): 128 ♩ = 128 bpm (Dance/Electronic)
   ├──> Key: C Major 🎹
   ├──> Duration: 3:42
   └──> Format: WAV 44.1kHz 16-bit

Audio Characteristics
   │
   ├──> Energy Level: ▓▓▓▓▓▓▓▓░░ 82/100 (High Energy)
   ├──> Loudness: -8.3 LUFS (Professional Master)
   └──> Dynamic Range: 12 dB (Good)

Mood Analysis
   │
   ├──> Valence: 😊 75/100 (Happy/Positive)
   ├──> Arousal: ⚡ 85/100 (Energetic)
   └──> Dominance: 💪 70/100 (Confident)

Genre Predictions
   │
   ├──> 1. Electronic Dance: 89% ████████▉
   ├──> 2. House: 72% ███████▏
   └──> 3. Tech House: 54% █████▍

Instrument Detection
   │
   ├──> Kick Drum: 95% ███████████
   ├──> Synthesizer: 88% ████████▊
   ├──> Hi-Hat: 76% ███████▌
   └──> Bass: 82% ████████▏

Song Structure
   │
   ├──> 0:00-0:32 → Intro
   ├──> 0:32-1:15 → Build-up
   ├──> 1:15-2:45 → Main Drop
   ├──> 2:45-3:15 → Breakdown
   └──> 3:15-3:42 → Outro
```

---

## 🎯 Feature Deep Dives

### Feature 1: Bulk Operations

**What It Does:** Manage multiple files at once

**Use Cases:**
- Tag 20 files with "summer vibes" in one click
- Export all analyzed files for backup
- Delete old project files quickly

**How to Use:**

1. **Go to Library**
2. **Select Files**
   ```
   Method 1: Click checkbox on each file
   Method 2: Click "Select All" button
   Method 3: Click "Select All" then uncheck unwanted files
   ```

3. **Choose Operation**
   ```
   ┌─────────────────────────────────────┐
   │  3 files selected                   │
   │  [Tag 🏷️] [Export 📥] [Delete 🗑️]  │
   └─────────────────────────────────────┘
   ```

4. **Execute**
   - **Tag:** Add comma-separated tags
   - **Export:** Files download as ZIP
   - **Delete:** Confirm with warning modal

---

### Feature 2: Password Strength Meter

**Why It Matters:** Strong passwords protect your music and data

**Strength Levels:**
```
Level 1: Very Weak (Red) 🔴
├─> Only lowercase: "password"
└─> DON'T USE THIS

Level 2: Weak (Dark Red) 🟥
├─> Short + simple: "Pass123"
└─> Easily guessed

Level 3: Fair (Orange) 🟠
├─> Better length: "Password123"
└─> Minimum acceptable

Level 4: Good (Yellow) 🟡
├─> Mixed case + numbers: "Password123!"
└─> Recommended for most

Level 5: Strong (Green) 🟢
├─> Long + complex: "MusicPro2025!Secure"
└─> Best protection
```

**How to Get Green:**
- ✅ At least 12 characters
- ✅ Uppercase letters (A-Z)
- ✅ Lowercase letters (a-z)
- ✅ Numbers (0-9)
- ✅ Special characters (!@#$%^&*)

---

### Feature 3: Remember Me

**What It Does:** Saves your username for quick login

**How It Works:**
```
Login with "Remember Me" checked
         │
         ├─> Username saved to browser
         │
Close browser / Come back later
         │
         ├─> Username pre-filled
         │
Just enter password & log in!
```

**Important Notes:**
- ✅ Only saves username (not password)
- ✅ Safe for personal devices
- ⚠️ Disable on public/shared computers
- 🗑️ Clear by unchecking and logging in

---

### Feature 4: Forgot Password

**Recovery Flow:**
```
1. Click "Forgot password?" on login page
         │
         V
2. Enter your email address
         │
         V
3. Check your email inbox
         │
         V
4. Click the reset link (valid 1 hour)
         │
         V
5. Create a new password
         │
         V
6. Log in with new password
```

**Troubleshooting:**
- ❌ Email not received? Check spam folder
- ❌ Link expired? Request a new one
- ❌ Still issues? Contact support

---

## 💡 Tips & Best Practices

### Audio Upload Tips

**File Formats:**
```
✅ RECOMMENDED:
   • WAV (uncompressed, best quality)
   • FLAC (lossless compression)

✅ GOOD:
   • MP3 320kbps
   • M4A (AAC)

⚠️ ACCEPTABLE:
   • MP3 128-256kbps
   • OGG

❌ AVOID:
   • Heavily compressed files
   • Low bitrate MP3s (<128kbps)
```

**File Size:**
- Max: 50 MB per file
- Recommend: Keep under 20 MB
- Tip: Use WAV for short files, FLAC for long files

---

### Tagging Strategy

**Good Tags:**
```
✅ Genre: "house", "techno", "ambient"
✅ Mood: "energetic", "calm", "dark"
✅ BPM: "128bpm", "140bpm"
✅ Key: "c-major", "a-minor"
✅ Use: "sample", "loop", "full-track"
```

**Tag Tips:**
- Use 3-7 tags per file
- Be specific but searchable
- Use lowercase for consistency
- Separate with commas

---

### Library Organization

**Folder Mental Model:**
```
My Library
├─ By Genre
│  ├─ electronic/
│  ├─ hip-hop/
│  └─ ambient/
├─ By Project
│  ├─ album-2024/
│  └─ remix-work/
└─ By Status
   ├─ needs-analysis
   └─ ready-to-use
```

**Use tags to create virtual folders!**

---

## ❓ FAQ

### General Questions

**Q: How long does analysis take?**
```
File Length    │ Analysis Time
───────────────┼────────────────
< 1 minute     │ 10-30 seconds
1-3 minutes    │ 30-90 seconds
3-5 minutes    │ 1-3 minutes
5+ minutes     │ 3-5 minutes
```

**Q: Can I analyze the same file multiple times?**
A: Yes! Re-analysis is useful if our AI model is updated.

**Q: What audio formats are supported?**
A: MP3, WAV, FLAC, OGG, M4A, AAC

**Q: Is there a file size limit?**
A: Yes, 50 MB per file currently

**Q: Can I download my analysis results?**
A: Yes! Export as JSON or CSV (coming soon)

---

### Account Questions

**Q: Can I change my email address?**
A: Yes! Go to Settings → Security → Change Email

**Q: How do I delete my account?**
A: Settings → Danger Zone → Delete Account
   ⚠️ This action is permanent!

**Q: Can I have multiple accounts?**
A: Yes, but each needs a unique email address

---

### Analysis Questions

**Q: Why is my BPM detection wrong?**
A: Try these solutions:
- Ensure audio is clear (no excessive noise)
- Check if file has complex polyrhythms
- Manually override BPM in settings

**Q: What does "Valence" mean?**
A: Musical positivity/happiness (0-100)
   - 0-30: Sad, melancholic
   - 30-70: Neutral
   - 70-100: Happy, upbeat

**Q: How accurate is genre detection?**
A: Typically 80-90% for well-defined genres

---

## 🎓 Next Steps

### Learn More:
- 📖 [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Command cheat sheet
- 🔧 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Fix common issues
- 🏗️ [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical details
- 📡 [API_REFERENCE.md](./API_REFERENCE.md) - API documentation

### Get Help:
- 💬 Community Discord: discord.gg/samplemind
- 📧 Email Support: support@samplemind.ai
- 🐛 Report Bugs: github.com/samplemind/issues

---

**Made with ❤️ by the SampleMind Team**

*Last Updated: 2025-10-04 | Version 1.0 Beta*
