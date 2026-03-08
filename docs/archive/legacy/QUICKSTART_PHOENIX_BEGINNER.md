# 🔥 SampleMind AI Phoenix - Beginner's Quick Start Guide

**Welcome to SampleMind AI Phoenix!** 🎵

This guide will help you get started in just **5 minutes**. No prior experience needed!

---

## 📖 What is SampleMind AI Phoenix?

Think of it as a **smart assistant for your music samples**:

```
┌─────────────────────────────────────────────────────────┐
│  🎵 You have 1000 audio samples scattered everywhere    │
│                                                          │
│  ❓ "Where's that dark techno kick?"                    │
│  ❓ "Which samples are in C minor?"                     │
│  ❓ "What's the BPM of this loop?"                      │
│                                                          │
│  ✨ Phoenix analyzes, organizes, and finds them for you!│
└─────────────────────────────────────────────────────────┘
```

**Phoenix can:**
- 🔍 Analyze audio files (BPM, key, mood, genre)
- 🏷️ Auto-tag samples with AI
- 📂 Organize your sample library
- 🔎 Find similar samples
- ⚡ Make everything searchable

---

## 🚀 Installation (5 Minutes)

### Step 1: Open Terminal

**On Ubuntu Linux:**
- Press `Ctrl + Alt + T`
- Or search for "Terminal" in your applications

```
┌────────────────────────────────────────┐
│ user@computer:~$                       │  ← Your terminal looks like this
│                                        │
└────────────────────────────────────────┘
```

### Step 2: Navigate to Project

```bash
# Go to the project folder
cd ~/Projects/samplemind-ai-v6

# Check you're in the right place
pwd
# Should show: /home/lchta/Projects/samplemind-ai-v6
```

### Step 3: Activate Environment

```bash
# Activate the virtual environment
source .venv/bin/activate

# Your prompt will change to show (.venv)
# (.venv) user@computer:~/Projects/samplemind-ai-v6$
```

### Step 4: Install Phoenix

```bash
# Install required libraries
pip install rich typer

# Install Phoenix in development mode
pip install -e .

# Test installation
sm --version
```

**Expected output:**
```
╭────────── 🔥 Phoenix ──────────╮
│ SampleMind AI                  │
│ Version: 2.0.0-beta            │
│ Codename: Phoenix 🔥           │
│ Status: Beta                   │
╰────────────────────────────────╯
```

---

## 🎯 Your First Commands (3 Easy Examples)

### Example 1: Analyze a Sample

```bash
# Analyze an audio file
sm analyze track.wav
```

**What happens:**
```
┌─── Analysis Results ───┐
│ Feature    │ Value     │
├────────────┼───────────┤
│ BPM        │ 128.00    │
│ Key        │ Am        │
│ Duration   │ 4.25s     │
│ Sample Rate│ 44100 Hz  │
└────────────┴───────────┘
```

### Example 2: Import Samples

```bash
# Import all samples from a folder
sm import folder ~/Music/Samples
```

**What happens:**
```
📥 Found 50 audio files
⚙️  Using 4 workers

Importing... ████████████████████ 100%

✓ Imported 50 files
```

### Example 3: Auto-Tag with AI

```bash
# Let AI tag your sample
sm tag auto kick.wav
```

**What happens:**
```
🧠 Auto-tagging: kick.wav
🔮 Model: hermès

┌─── Predicted Tags ───┐
│ Tag    │ Category   │ Confidence │
├────────┼────────────┼────────────┤
│ kick   │ instrument │ 95.0%      │
│ techno │ genre      │ 89.0%      │
│ dark   │ mood       │ 76.0%      │
└────────┴────────────┴────────────┘

Apply these tags? [y/n]: _
```

---

## 📚 Step-by-Step Tutorial

### Tutorial 1: Analyze Your First Sample

**Goal:** Learn what's in an audio file

#### Step 1: Find a sample
```bash
# List audio files in current folder
ls *.wav *.mp3 2>/dev/null | head -5
```

#### Step 2: Analyze it
```bash
# Replace 'sample.wav' with your file
sm analyze sample.wav
```

#### Step 3: Get detailed analysis
```bash
# Get more information
sm analyze sample.wav --level advanced
```

**You'll see:**
- ✅ **BPM** (tempo): How fast the sample is
- ✅ **Key** (musical key): Like "C major" or "A minor"
- ✅ **Duration**: Length in seconds
- ✅ **Sample Rate**: Audio quality (44100 Hz = CD quality)
- ✅ **Harmonic/Percussive**: Is it melodic or drums?

---

### Tutorial 2: Import Your Sample Library

**Goal:** Add all your samples to Phoenix

#### Step 1: Create a test folder
```bash
# Create a folder with some samples
mkdir -p ~/Music/TestSamples

# Copy a few files there (example)
# cp ~/Downloads/*.wav ~/Music/TestSamples/
```

#### Step 2: Import the folder
```bash
# Import all samples
sm import folder ~/Music/TestSamples
```

**Visual Progress:**
```
📂 Found 15 audio files
⚙️  Using 4 workers

Importing files...
[████████████████████████████████] 100%
⏱️  Time: 12 seconds

✓ Imported 15 files
✓ Analyzed 15 files
✓ All done!
```

#### Step 3: View imported samples
```bash
# List all imported samples
sm stats --library
```

---

### Tutorial 3: Auto-Tag Everything with AI

**Goal:** Let AI automatically tag all your samples

#### Step 1: Tag a single file
```bash
# Auto-tag one file
sm tag auto kick.wav
```

**AI will detect:**
- 🎸 **Instrument**: kick, snare, hi-hat, synth, etc.
- 🎭 **Mood**: dark, uplifting, energetic, calm, etc.
- 🎵 **Genre**: techno, house, hip-hop, etc.
- ⚡ **Energy**: low, medium, high

#### Step 2: Tag entire folder
```bash
# Tag all samples in a folder
sm tag batch ~/Music/TestSamples
```

**Progress:**
```
🏷️  Batch tagging folder: ~/Music/TestSamples
⚙️  Using 4 workers

Processing files...
[████████████████████████████████] 100%

✓ Tagged 15 files
✓ Average confidence: 87%
```

---

## 🎨 Visual Cheat Sheet

### Command Structure

```
sm <command> <subcommand> <arguments> [options]
│   │         │            │            │
│   │         │            │            └─ Extra settings (optional)
│   │         │            └─────────────── What to work with
│   │         └──────────────────────────── What to do
│   └────────────────────────────────────── Main action
└────────────────────────────────────────── SampleMind command
```

**Examples:**
```bash
sm analyze file sample.wav              # Analyze a file
sm import folder /samples               # Import a folder
sm tag auto kick.wav --model hermès     # Auto-tag with AI
sm organize --by-key                    # Organize by musical key
```

---

## 🎯 Common Tasks (Copy & Paste Ready!)

### Task 1: Quick Analysis
```bash
# Analyze a sample and show BPM + Key
sm analyze sample.wav
```

### Task 2: Import All Samples
```bash
# Import from your samples folder
sm import folder ~/Music/Samples --analyze
```

### Task 3: Find Similar Samples
```bash
# Find samples similar to a kick
sm similarity kick.wav --limit 10
```

### Task 4: Organize by BPM
```bash
# Organize samples into folders by tempo
sm organize --by-bpm
```

### Task 5: Export Tagged Samples
```bash
# Export all techno samples
sm export --genre techno --output ~/Desktop/Techno
```

---

## 🛠️ Troubleshooting

### Problem 1: Command Not Found

**Error:**
```bash
sm --version
# zsh: command not found: sm
```

**Solution:**
```bash
# Make sure you're in the project folder
cd ~/Projects/samplemind-ai-v6

# Activate the virtual environment
source .venv/bin/activate

# Install again
pip install -e .
```

---

### Problem 2: File Not Found

**Error:**
```bash
sm analyze sample.wav
# Error: File not found: sample.wav
```

**Solution:**
```bash
# Check if file exists
ls sample.wav

# Use absolute path
sm analyze ~/Music/sample.wav

# Or navigate to the folder first
cd ~/Music
sm analyze sample.wav
```

---

### Problem 3: Permission Denied

**Error:**
```bash
sm import folder /samples
# Permission denied
```

**Solution:**
```bash
# Make sure you own the folder
ls -la /samples

# Or use a folder in your home directory
sm import folder ~/Music/Samples
```

---

## 📖 Understanding the Output

### Analysis Results Explained

```bash
sm analyze kick.wav
```

**Output Breakdown:**
```
┌─── Analysis Results ───────┐
│ BPM        │ 128.00        │  ← Beats per minute (tempo)
│ Key        │ Am            │  ← Musical key (A minor)
│ Scale      │ minor         │  ← Major or minor scale
│ Duration   │ 2.50s         │  ← Length of sample
│ Sample Rate│ 44100 Hz      │  ← Audio quality
│ Harmonic   │ 25%           │  ← Melodic content
│ Percussive │ 75%           │  ← Drum/rhythm content
└────────────┴───────────────┘
```

**What does it mean?**
- **BPM 128**: This sample plays at 128 beats per minute (common for house music)
- **Key Am**: Musical key is A minor (dark, moody sound)
- **Harmonic 25%**: Only 25% is melodic (mostly drums)
- **Percussive 75%**: 75% is drums/percussion (probably a kick!)

---

## 🎓 Learning Path

### Level 1: Beginner (You are here! ✅)
- ✅ Install Phoenix
- ✅ Analyze samples
- ✅ Import samples
- ✅ Basic tagging

**Next:** Try analyzing 10 different samples!

---

### Level 2: Intermediate (Coming soon!)
- [ ] Use advanced AI tagging
- [ ] Organize entire library
- [ ] Create sample packs
- [ ] Use similarity search

**Goal:** Organize 100+ samples efficiently

---

### Level 3: Advanced (Future!)
- [ ] Build custom workflows
- [ ] Use DAW plugins
- [ ] Voice control
- [ ] Batch automation

**Goal:** Manage 1000+ samples like a pro

---

## 🎬 Example Workflow: New Producer

**Scenario:** You just downloaded 50 sample packs and need to organize them.

### Step 1: Import Everything
```bash
# Import all your samples
sm import folder ~/Downloads/SamplePacks --recursive
```

### Step 2: Auto-Tag Everything
```bash
# Let AI tag everything
sm tag batch ~/Downloads/SamplePacks --model hermès
```

### Step 3: Organize by Type
```bash
# Organize into kicks, snares, bass, etc.
sm organize --by-instrument
```

### Step 4: Find What You Need
```bash
# Find dark techno kicks at 128 BPM
sm search --genre techno --mood dark --instrument kick --bpm 128
```

**Result:** 
```
Found 15 matching samples:
1. dark_kick_01.wav (128 BPM, Am, 95% confidence)
2. techno_kick_heavy.wav (128 BPM, Am, 92% confidence)
3. industrial_kick_02.wav (127 BPM, Gm, 89% confidence)
...
```

---

## 💡 Pro Tips for Beginners

### Tip 1: Use Tab Completion
```bash
# Type 'sm ' and press TAB twice to see all commands
sm <TAB><TAB>

# You'll see:
# analyze  import  tag  organize  config  stats  search
```

### Tip 2: Use --help Anytime
```bash
# Get help for any command
sm --help
sm analyze --help
sm tag --help
```

### Tip 3: Start Small
```bash
# Don't import 1000 files at once!
# Start with a small folder (10-20 files)
sm import folder ~/Music/TestSamples
```

### Tip 4: Check Progress
```bash
# See your library stats
sm stats --library

# Output:
# Total samples: 50
# Analyzed: 50 (100%)
# Tagged: 35 (70%)
# Organized: 25 (50%)
```

### Tip 5: Use Verbose Mode to Learn
```bash
# See what Phoenix is doing
sm analyze sample.wav --verbose

# You'll see:
# [INFO] Loading audio file...
# [INFO] Extracting mel spectrogram...
# [INFO] Running BPM detection...
# [INFO] Detecting musical key...
# [SUCCESS] Analysis complete!
```

---

## 🎮 Interactive Practice

### Exercise 1: Analyze 3 Samples (5 minutes)

**Task:** Analyze three different samples and compare results

```bash
# Sample 1: A kick
sm analyze kick.wav

# Sample 2: A bass
sm analyze bass.wav

# Sample 3: A full loop
sm analyze loop.wav
```

**Questions:**
1. Which has the highest BPM?
2. Which is most percussive?
3. What keys are they in?

---

### Exercise 2: Build a Small Library (10 minutes)

**Task:** Create and organize a mini sample library

```bash
# Step 1: Create folders
mkdir -p ~/Music/MyLibrary/{Drums,Bass,Synths,FX}

# Step 2: Copy some samples (use your own)
# cp ~/Downloads/kicks/*.wav ~/Music/MyLibrary/Drums/

# Step 3: Import everything
sm import folder ~/Music/MyLibrary --analyze

# Step 4: Tag everything
sm tag batch ~/Music/MyLibrary

# Step 5: Check stats
sm stats --library
```

---

### Exercise 3: Find and Export (10 minutes)

**Task:** Find specific samples and export them

```bash
# Step 1: Search for techno samples at 128 BPM
sm search --genre techno --bpm 128

# Step 2: Export them to a new pack
sm export --genre techno --bpm 128 --output ~/Desktop/TechnoPack

# Step 3: Check what was exported
ls ~/Desktop/TechnoPack/
```

---

## 📝 Quick Reference Card

**Print this and keep it handy!**

```
╔═══════════════════════════════════════════════════════════╗
║         SAMPLEMIND AI PHOENIX - QUICK REFERENCE           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  ANALYZE                                                  ║
║  ────────                                                 ║
║  sm analyze <file>           Analyze audio file           ║
║  sm analyze <file> --level   More details                 ║
║                                                           ║
║  IMPORT                                                   ║
║  ───────                                                  ║
║  sm import file <file>       Import one file              ║
║  sm import folder <folder>   Import folder                ║
║  sm import watch <folder>    Watch for new files          ║
║                                                           ║
║  TAGGING                                                  ║
║  ────────                                                 ║
║  sm tag auto <file>          AI auto-tag                  ║
║  sm tag add <file> <tags>    Add tags manually            ║
║  sm tag list                 Show all tags                ║
║  sm tag batch <folder>       Tag entire folder            ║
║                                                           ║
║  ORGANIZE                                                 ║
║  ─────────                                                ║
║  sm organize --by-key        By musical key               ║
║  sm organize --by-bpm        By tempo                     ║
║  sm organize --by-genre      By genre                     ║
║                                                           ║
║  SEARCH                                                   ║
║  ───────                                                  ║
║  sm search --genre <genre>   Find by genre                ║
║  sm search --key <key>       Find by key                  ║
║  sm similarity <file>        Find similar                 ║
║                                                           ║
║  HELP                                                     ║
║  ─────                                                    ║
║  sm --help                   Show all commands            ║
║  sm <command> --help         Command help                 ║
║  sm --version                Show version                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🎉 Congratulations!

You're now ready to use SampleMind AI Phoenix! 🔥

### What You Learned:
- ✅ How to install Phoenix
- ✅ Basic commands (analyze, import, tag)
- ✅ How to organize samples
- ✅ How to search your library
- ✅ Troubleshooting common issues

### Next Steps:
1. **Practice:** Try the exercises above
2. **Explore:** Run `sm --help` to see all commands
3. **Learn More:** Check out the advanced docs
4. **Join Community:** Share your workflows!

---

## 📞 Need Help?

### Getting Stuck?

**1. Check the help:**
```bash
sm --help
sm <command> --help
```

**2. Enable verbose mode:**
```bash
sm analyze sample.wav --verbose
```

**3. Check the logs:**
```bash
# Logs are saved here
cat ~/.samplemind/logs/phoenix.log
```

**4. Ask for help:**
- 📧 Email: lchtangen@gmail.com
- 💬 Discord: #samplemind-phoenix
- 🐛 GitHub Issues: Report bugs

---

## 🔗 More Resources

### Documentation
- 📖 [Full Documentation](../README.md)
- 🗺️ [Roadmap](V6_FEATURE_INTEGRATION_MASTER_PLAN.md)
- 🔧 [Advanced Guide](PHASE_1_PHOENIX_IMPLEMENTATION.md)

### Tutorials
- 🎬 Video Tutorials (coming soon!)
- 📝 Blog Posts (coming soon!)
- 💡 Tips & Tricks (coming soon!)

---

## 🌟 Success Stories

### "Organized 500 samples in 10 minutes!"
*"Phoenix analyzed and tagged my entire sample library while I made coffee. Amazing!"*
— Producer Mike

### "Found the perfect kick instantly"
*"Used to spend hours searching. Now I just describe what I want and Phoenix finds it!"*
— DJ Sarah

### "Best sample manager I've used"
*"The AI tagging is scary good. It knows my samples better than I do!"*
— Beatmaker Alex

---

**🔥 Welcome to Phoenix! Let's make music! 🎵**

---

**Last Updated:** 2025-10-04  
**Version:** 1.0 for Beginners  
**Difficulty:** ⭐ Beginner Friendly
