# SampleMind AI v2.3.0-beta - Quick Start Guide

**Your First 15 Minutes with SampleMind AI**

---

## Installation (2 minutes)

### macOS/Linux
```bash
pip install samplemind-ai==2.3.0b0
samplemind --version
```

### Windows
```powershell
pip install samplemind-ai==2.3.0b0
samplemind --version
```

✅ **Done!** You're ready to go.

---

## 5 Essential Commands for Beginners

### 1️⃣ Analyze Your First Track (2 minutes)
```bash
samplemind analyze:full song.wav
```

**Output you'll see:**
```
Analysis Results for: song.wav
════════════════════════════════════════════
Tempo:      120 BPM (±2 confidence)
Key:        C Major
Genre:      Electronic
Mood:       Energetic
Energy:     78%
Confidence: 92%
════════════════════════════════════════════
✓ Analysis complete in 1.2 seconds
```

💡 **What this tells you:**
- Your song is at 120 BPM (good for mixing with other 120 BPM tracks)
- It's in C Major (useful for finding compatible sounds)
- Electronic mood (shapes how to process it)
- High energy (great for dance/club music)

---

### 2️⃣ Find Similar Sounds (2 minutes)
```bash
samplemind similar:find song.wav --limit 5
```

**Output:**
```
Similar Samples (by sound characteristics)
════════════════════════════════════════════
1. kick_120bpm.wav        (97% match)
2. bass_c_major.wav       (94% match)
3. synth_loop_electronic.wav (91% match)
4. drum_pattern_120.wav   (88% match)
5. effect_pad_c.wav       (85% match)
════════════════════════════════════════════
✓ Found 5 matches in your library
```

💡 **Why this is useful:**
- Find samples that blend with your current track
- Discover new sounds in the same style
- Build cohesive sample packs

---

### 3️⃣ Apply a Professional Effect (3 minutes)
```bash
samplemind effects:preset-vocal song.wav -o processed.wav
```

**What happens:**
- Original file: `song.wav`
- Processed file: `processed.wav` (automatically created)
- Effect applied: Professional vocal preset (EQ + compression + reverb)

**Try different presets:**
```bash
samplemind effects:preset-drums song.wav -o drums.wav
samplemind effects:preset-bass song.wav -o bass.wav
samplemind effects:preset-master song.wav -o mastered.wav
samplemind effects:preset-vintage song.wav -o vintage.wav
```

💡 **When to use each:**
- **Vocal**: For voice recordings, singing, speech
- **Drums**: For drum loops, percussion
- **Bass**: For bass lines, sub-heavy sounds
- **Master**: Final polishing for all content
- **Vintage**: Retro/analog character

---

### 4️⃣ Generate MIDI from Audio (3 minutes)
```bash
samplemind midi:extract melody_sample.wav --type melody
```

**Output:**
```
MIDI Generation
════════════════════════════════════════════
Extraction Type: Melody
Duration:        4.2 seconds
Notes Generated: 24
Output File:     melody_sample_melody.mid
════════════════════════════════════════════
✓ MIDI generated successfully
```

**What you get:**
- A playable MIDI file containing the detected melody
- Ready to drag into your DAW
- Use as-is or edit further

**Extract different elements:**
```bash
samplemind midi:extract song.wav --type melody      # Main melody
samplemind midi:extract song.wav --type harmony     # Chord progression
samplemind midi:extract song.wav --type drums       # Drum pattern
samplemind midi:extract song.wav --type bass_line   # Bass notes
```

---

### 5️⃣ Create a Sample Pack (5 minutes)
```bash
# Create a new pack
samplemind pack:create my_collection --add *.wav

# Or create from specific files
samplemind pack:create my_drums \
  --add kick.wav \
  --add snare.wav \
  --add hihat.wav \
  --add cymbal.wav
```

**Output:**
```
Sample Pack Creation
════════════════════════════════════════════
Pack Name:        my_drums
Files Added:      4
Auto-tagged:      ✓ (genre, mood, BPM)
Export Ready:     ✓
Export Command:   samplemind pack:export my_drums
════════════════════════════════════════════
```

**Export your pack:**
```bash
samplemind pack:export my_drums --format zip
```

Result: `my_drums.zip` ready to share or backup

---

## 10 Common Workflows

### Workflow #1: Prepare Vocals for Your Mix
```bash
# 1. Analyze vocal to understand it
samplemind analyze:full vocal.wav

# 2. Check for similar vocal samples in library
samplemind similar:find vocal.wav --library vocals_folder

# 3. Apply vocal preset (with EQ + compression)
samplemind effects:preset-vocal vocal.wav -o vocal_processed.wav

# Result: vocal_processed.wav ready to add to your mix
```

### Workflow #2: Create a Drum Pack from Samples
```bash
# 1. Gather drum samples in a folder
# Place: kick.wav, snare.wav, hihat.wav, tom.wav in drums_folder/

# 2. Analyze each for metadata
samplemind analyze:full drums_folder/kick.wav
samplemind analyze:full drums_folder/snare.wav
# ... etc

# 3. Create pack
samplemind pack:create my_drum_kit --add drums_folder/*.wav

# 4. Export
samplemind pack:export my_drum_kit --format zip

# Result: my_drum_kit.zip with all metadata
```

### Workflow #3: Find Matching Samples for Your Project
```bash
# 1. Know your project's BPM and Key
# Example: 128 BPM, D Minor

# 2. Analyze reference sample
samplemind analyze:full reference_sample.wav

# 3. Find matches with same BPM and key
samplemind similar:find reference_sample.wav --limit 10

# Result: List of compatible samples
```

### Workflow #4: Extract Melody and Make MIDI Version
```bash
# 1. Load audio with melody you like
samplemind analyze:full nice_melody.wav

# 2. Extract as MIDI
samplemind midi:extract nice_melody.wav --type melody

# 3. Result: nice_melody_melody.mid
# - Open in DAW
# - Edit the MIDI notes
# - Transpose to your key
# - Use for original composition
```

### Workflow #5: Master a Remix
```bash
# 1. Analyze your final mix
samplemind analyze:full my_remix.wav

# 2. Apply master preset
samplemind effects:preset-master my_remix.wav -o my_remix_mastered.wav

# 3. Result: Ready for distribution
```

### Workflow #6: Create Vintage-Sounding Drums
```bash
# 1. Start with modern drums
# - drum_kit.wav

# 2. Apply vintage preset
samplemind effects:preset-vintage drum_kit.wav -o vintage_drums.wav

# Result: Retro character while keeping rhythm
```

### Workflow #7: Separate Vocals from Backing Track
```bash
# 1. Full song with vocals and instruments
samplemind stems:separate full_song.wav

# Result: 4 stems created
# - full_song_vocals.wav
# - full_song_drums.wav
# - full_song_bass.wav
# - full_song_other.wav

# Now you can:
# - Boost vocals independently
# - Remix without original vocals
# - Create karaoke version
```

### Workflow #8: Quick Genre Classification
```bash
# Wondering what genre a sample is?
samplemind analyze:quick sample.wav

# Output: Just the genre
# Faster than full analysis
```

### Workflow #9: Build a Reference Library
```bash
# 1. Create pack for each genre you use
samplemind pack:create house_references --add house_1.wav house_2.wav
samplemind pack:create techno_references --add techno_1.wav techno_2.wav
samplemind pack:create deep_references --add deep_1.wav deep_2.wav

# 2. Tag them
samplemind tag:auto house_references --category genre

# 3. When starting a new track:
samplemind similar:find my_new_track.wav --library house_references

# Result: Find reference tracks with similar characteristics
```

### Workflow #10: Batch Process Multiple Files
```bash
# Process entire folder of vocals with preset
for file in vocals_folder/*.wav; do
  samplemind effects:preset-vocal "$file" -o "${file%.wav}_processed.wav"
done

# Result: All vocals processed with consistent settings
```

---

## Keyboard Shortcuts & Tips

### Speed Tips
```bash
# Use shorter command names
samplemind fx:eq song.wav              # Instead of effects:eq
samplemind an:full song.wav            # Instead of analyze:full
samplemind mi:extract song.wav         # Instead of midi:extract
samplemind sim:find song.wav           # Instead of similar:find
```

### File Helpers
```bash
# Process most recent audio file
samplemind analyze:full $(ls -t *.wav | head -1)

# Process all WAV files in folder
for f in *.wav; do samplemind analyze:full "$f"; done

# Save analysis to file
samplemind analyze:full song.wav > analysis.txt
```

### Progress Tips
```bash
# Interrupt long operations
# Press: Ctrl+C (macOS/Linux) or Ctrl+C (Windows)
# System will stop and clean up

# Show what's happening
samplemind analyze:full song.wav --verbose

# Faster analysis (less detail)
samplemind analyze:basic song.wav    # Quick analysis
```

---

## Troubleshooting

### Problem: "File not found"
**Solution:** Check file path
```bash
# ❌ Wrong
samplemind analyze:full song.wav

# ✅ Correct (full path)
samplemind analyze:full /Users/name/Music/song.wav

# ✅ Also works (relative path)
samplemind analyze:full ./songs/song.wav
```

### Problem: "Unsupported audio format"
**Solution:** Use WAV or AIFF
```bash
# Supported: WAV, AIFF, MP3, FLAC
# Convert if needed:
# - ffmpeg -i song.m4a song.wav
```

### Problem: "Backend not responding"
**Solution:** This is only for plugin users
```bash
# Start backend server
python3 plugins/ableton/python_backend.py

# Leave running in background
# Then use Ableton plugin
```

### Problem: "Permission denied"
**Solution:** Check file permissions
```bash
# macOS/Linux: Add execute permission
chmod +x samplemind

# Or use full Python path
python3 -m samplemind analyze:full song.wav
```

---

## Next Steps After These 5 Commands

### Ready to go deeper? Try:

**Effects Mastery**
```bash
# Learn all 12 effects
samplemind effects:list

# Try each one
samplemind effects:eq song.wav -o eq_version.wav
samplemind effects:compress song.wav -o compressed.wav
samplemind effects:reverb song.wav -o reverb_version.wav
```

**MIDI Generation**
```bash
# Extract different elements
samplemind midi:extract song.wav --type harmony
samplemind midi:extract song.wav --type drums
samplemind midi:extract song.wav --type bass_line
```

**Sample Organization**
```bash
# Create specialized packs
samplemind pack:create reference_tracks --add references/*.wav
samplemind pack:create work_in_progress --add projects/*.wav
samplemind pack:export reference_tracks --format zip
```

---

## Getting Help

### Quick Reference
```bash
samplemind --help                      # All commands
samplemind effects --help              # Effects help
samplemind analyze --help              # Analysis help
samplemind <command> --help            # Any command help
```

### Documentation
- Full guide: Read `README.md`
- Command reference: Read `CLI_REFERENCE.md`
- Plugins: Read `PLUGIN_INSTALLATION_GUIDE.md`

### Community
- Issues: https://github.com/samplemind/samplemind-ai/issues
- Discussions: https://github.com/samplemind/samplemind-ai/discussions
- Discord: [Community Link]

---

## Pro Tips for Power Users

### Tip #1: Create Aliases
```bash
# In your ~/.bashrc or ~/.zshrc
alias smai='samplemind'
alias smai-vocal='samplemind effects:preset-vocal'
alias smai-drums='samplemind effects:preset-drums'

# Now use shorter commands
smai-vocal song.wav -o processed.wav
```

### Tip #2: Use with Other Tools
```bash
# Pipe to ffmpeg for format conversion
samplemind effects:preset-master song.wav | ffmpeg -i pipe: output.mp3

# Process and analyze
samplemind analyze:full song.wav && samplemind effects:preset-master song.wav
```

### Tip #3: Batch Processing Script
```bash
#!/bin/bash
# save as: process_folder.sh

for file in "$1"/*.wav; do
  echo "Processing: $file"
  samplemind effects:preset-master "$file" -o "${file%.wav}_mastered.wav"
done

echo "Done!"
```

Usage: `bash process_folder.sh /path/to/folder`

### Tip #4: Organize by Analysis Results
```bash
# Find all house music samples
samplemind analyze:full *.wav | grep "house" > house_samples.txt

# Find all high-energy samples (>80% energy)
samplemind analyze:full *.wav | grep "Energy: [89][0-9]" > energetic_samples.txt
```

---

## Summary

You now know:
✅ How to analyze audio
✅ How to find similar sounds
✅ How to apply professional effects
✅ How to extract MIDI from audio
✅ How to organize samples into packs
✅ 10+ professional workflows
✅ Time-saving tips and tricks

**Time spent:** 15 minutes
**Expertise gained:** Professional music production assistant

---

**Next:** Explore the full documentation or start a real project!

