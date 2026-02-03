# SampleMind AI v2.3.0-beta - Frequently Asked Questions

---

## Installation & Setup (8 Questions)

### Q1: What are the system requirements?
**A:** Minimum requirements:
- **Python:** 3.11 or newer
- **RAM:** 4GB (8GB recommended)
- **Disk:** 2GB free space
- **OS:** Windows 10+, macOS 10.13+, or Linux (Ubuntu 20.04+)
- **Audio files:** WAV, AIFF, MP3, or FLAC format

### Q2: How do I install SampleMind AI?
**A:** The easiest way:
```bash
pip install samplemind-ai==2.3.0b0
```

For development:
```bash
git clone https://github.com/samplemind/samplemind-ai.git
cd samplemind-ai
pip install -e ".[dev]"
```

With Docker:
```bash
docker pull ghcr.io/samplemind/samplemind-ai:2.3.0-beta
```

### Q3: I get "Python not found" error. What do I do?
**A:** Python isn't installed or not in your PATH.

**Solution:**
1. Download Python 3.11+ from https://python.org
2. During installation, **CHECK** "Add Python to PATH"
3. Restart your terminal/command prompt
4. Try: `python --version`

**Alternative:** Use full path
```bash
/usr/bin/python3.11 -m pip install samplemind-ai
```

### Q4: Can I use SampleMind AI offline?
**A:** Yes! SampleMind AI works offline by default. It uses:
- Local audio processing (no internet needed)
- Optional offline AI models (Ollama)
- Fallback to cloud AI only if you choose

For pure offline: Don't connect to internet or disable cloud features in settings.

### Q5: Which DAWs does SampleMind AI support?
**A:** **Current (v2.3.0-beta):**
- FL Studio 20+ (plugin pending SDK)
- Ableton Live 11+ (with Max for Live)

**Upcoming:**
- Logic Pro (Phase 14)
- Studio One (Phase 14)
- Reaper (Phase 15)

### Q6: Do I need Max for Live to use Ableton plugin?
**A:** Yes. Ableton Live Suite includes Max for Live. If you have Live Standard, you need to purchase Max for Live separately (optional add-on, ~$99).

### Q7: How much disk space do I need?
**A:**
- Base installation: ~500MB
- With offline models: +2GB
- Sample library: Depends on your music (budget 1-10GB)

### Q8: Can I use SampleMind AI on my music production laptop?
**A:** Yes! It's designed for production laptops. Minimal footprint and CPU usage.

---

## Audio Analysis (6 Questions)

### Q9: What audio formats are supported?
**A:** ✅ **Supported:**
- WAV (recommended)
- AIFF
- MP3
- FLAC

❌ **Not supported:**
- M4A (convert to WAV first)
- OGG (convert to WAV first)
- MIDI files

**Convert using FFmpeg:**
```bash
ffmpeg -i song.m4a song.wav
```

### Q10: How accurate is the BPM detection?
**A:** **Typical accuracy: ±2-3 BPM**

Factors affecting accuracy:
- ✅ Good: Clean beats, 60-180 BPM, consistent tempo
- ⚠️ Challenge: Swing/jazz, tempo changes, polyrhythms
- ❌ Difficult: Ambient music, no clear beat

**For best results:** Use STANDARD or DETAILED analysis level.

### Q11: What about key detection accuracy?
**A:** **Typical accuracy: 85-95%**

Factors affecting accuracy:
- ✅ Good: Clear harmonic structure, major keys
- ⚠️ Challenge: Complex harmonies, modulations
- ❌ Difficult: Ambient, highly dissonant music

**Multiple key options:** Check results carefully for modal/ambiguous keys.

### Q12: How long does analysis take?
**A:** Depends on file length and analysis level:

| Level | 1 min | 5 min | 10 min |
|-------|-------|-------|--------|
| BASIC | 0.5s | 1s | 2s |
| STANDARD | 1-2s | 3-5s | 6-10s |
| DETAILED | 3-5s | 10-20s | 20-40s |
| PROFESSIONAL | 10-20s | 30-60s | 60-120s |

**Slower on:** Older computers, large files, DETAILED/PROFESSIONAL levels

### Q13: Can I analyze multiple files at once?
**A:** Yes! Use batch mode:
```bash
samplemind analyze:batch folder/*.wav
```

Or manually:
```bash
for file in *.wav; do samplemind analyze:full "$file"; done
```

### Q14: What if analysis gives wrong results?
**A:** Analysis can be wrong on unusual music. **Solutions:**

1. **Check confidence score:** If <70%, results may be inaccurate
2. **Try different level:** DETAILED might be more accurate
3. **Manual correction:** Edit results in settings
4. **Report feedback:** Help improve accuracy (if sharing results)

---

## Effects & Processing (6 Questions)

### Q15: What audio effects are available?
**A:** **Built-in Effects (12 total):**

**Presets (5):**
- Vocal (EQ + Compression + Reverb for voices)
- Drums (Punch, tight compression)
- Bass (Sub enhancement, compression)
- Master (Final polish, limiting)
- Vintage (Analog character)

**Individual (5):**
- EQ (10-band parametric)
- Compress (Dynamic compression)
- Limit (Hard limiting)
- Distort (Soft distortion)
- Reverb (Room reverb effect)

**Reference (1):**
- effects:list (See all effects)

### Q16: Will effects change my file permanently?
**A:** **No!** Original stays safe.

By default:
```bash
samplemind effects:preset-vocal song.wav -o processed.wav
```
- Original: `song.wav` (unchanged)
- New: `processed.wav` (with effect)

Original is always preserved.

### Q17: Can I combine multiple effects?
**A:** Currently, presets combine effects automatically. Individual effects combine sequentially:

```bash
# Apply EQ, then compression to result
samplemind effects:eq song.wav -o eq_version.wav
samplemind effects:compress eq_version.wav -o final.wav
```

**Future:** Preset chaining coming in Phase 14.

### Q18: Which preset should I use?
**A:** **Choose by content type:**

- 🎤 **Vocal:** Voice recordings, singing, speech
- 🥁 **Drums:** Drum loops, percussion, beats
- 🔊 **Bass:** Bass lines, sub-heavy sounds
- 🎵 **Master:** Final mix, all content types
- 📻 **Vintage:** Retro sound, lo-fi effect

**If unsure:** Start with STANDARD analysis, let AI suggest.

### Q19: Can I undo an effect?
**A:** No automatic undo. **Solutions:**

1. **Keep original:** Always save to new filename `-o result.wav`
2. **Reprocess:** Run effect again (if you have original)
3. **DAW undo:** If used in DAW, use DAW's undo (Ctrl+Z)

**Best practice:** Always use `-o output_name.wav` flag.

### Q20: Are effects real-time?
**A:** Currently, effects render to file (fast). Real-time processing coming in Phase 14 for DAW plugins.

---

## MIDI Generation (5 Questions)

### Q21: What types of MIDI can be generated?
**A:** **4 extraction types:**

1. **Melody** - Main melodic line
   - Best for: Vocal melodies, lead instruments
   - Result: Single note at a time

2. **Harmony** - Chord progression
   - Best for: Harmonic structure, background chords
   - Result: Multiple notes (polyphonic)

3. **Drums** - Drum/percussion patterns
   - Best for: Beat extraction, rhythm
   - Result: Drum note sequence

4. **Bass Line** - Bass note sequence
   - Best for: Bass melodic line
   - Result: Low-note melody

### Q22: How accurate is MIDI extraction?
**A:** Accuracy varies by content:

- ✅ **Good (80-95%):** Clear single instruments, monophonic
- ⚠️ **Fair (60-80%):** Harmonic/complex content
- ❌ **Difficult (<60%):** Polyphonic, heavily processed

**Tips for better results:**
- Use STANDARD or DETAILED analysis
- Clean, dry recordings work better
- Less reverb = better extraction

### Q23: Can I edit generated MIDI?
**A:** Yes! MIDI is in standard `.mid` format:

1. Open in DAW (Ableton, FL Studio, Logic, etc.)
2. Edit notes, timing, velocity
3. Change pitch/tempo as needed
4. Re-export

Generated MIDI is a starting point, not final.

### Q24: What's the note range for generated MIDI?
**A:** **Default range:** C2 to C6 (covers most instruments)

**Customize:**
```bash
samplemind midi:extract song.wav \
  --min-note C3 \
  --max-note C5 \
  --type melody
```

**Common ranges:**
- Vocals: C3 to C5
- Bass: C1 to C3
- Lead synth: C4 to C7

### Q25: Can MIDI include velocity/dynamics?
**A:** Current version: Basic velocity. Enhanced velocity mapping coming in Phase 14.

For now: Extract MIDI, then add dynamics in DAW.

---

## Sample Management (5 Questions)

### Q26: How do I create a sample pack?
**A:** Simple method:
```bash
samplemind pack:create my_pack --add file1.wav file2.wav file3.wav
```

From folder:
```bash
samplemind pack:create my_pack --add folder/*.wav
```

### Q27: Can I add metadata to samples?
**A:** Yes! Two ways:

**Automatic:**
```bash
samplemind tag:auto sample.wav
# Auto-generates: genre, mood, BPM, instruments
```

**Manual:**
```bash
samplemind tag:set sample.wav --genre house --mood energetic --bpm 130
```

### Q28: How do I search by metadata?
**A:** Search packs by tags:
```bash
samplemind library:search --tags "house,energetic"
samplemind library:search --bpm 120-130 --key "C Major"
```

### Q29: Can I export packs for sharing?
**A:** Yes! Multiple formats:

```bash
samplemind pack:export my_pack --format zip      # ZIP archive
samplemind pack:export my_pack --format tar      # TAR (macOS/Linux)
samplemind pack:export my_pack --format json     # Metadata only
```

### Q30: How large can sample packs be?
**A:** **No built-in limit** (depends on disk space).

**Practical limits:**
- Small pack: 10-50 samples
- Medium pack: 50-200 samples
- Large pack: 200+ samples

**For best performance:** Keep packs under 1GB.

---

## Troubleshooting (10 Questions)

### Q31: "File not found" error - how do I fix it?
**A:** Path issues. **Solutions:**

1. **Check file exists:**
   ```bash
   ls /path/to/song.wav   # macOS/Linux
   dir C:\path\to\song.wav # Windows
   ```

2. **Use full path:**
   ```bash
   samplemind analyze:full /Users/name/Music/song.wav
   ```

3. **Use quotes if spaces in path:**
   ```bash
   samplemind analyze:full "/Users/name/My Music/song.wav"
   ```

### Q32: "Unsupported format" - what do I do?
**A:** File format not supported. **Solutions:**

1. **Convert to WAV:**
   ```bash
   ffmpeg -i song.m4a song.wav
   ffmpeg -i song.ogg song.wav
   ```

2. **Supported formats:** WAV, AIFF, MP3, FLAC

3. **Install FFmpeg:** https://ffmpeg.org

### Q33: Audio analysis is slow - how do I speed it up?
**A:** Analysis takes time. **Options:**

1. **Use faster level:**
   ```bash
   samplemind analyze:basic song.wav  # Fastest
   ```

2. **Close other apps** (free up RAM)

3. **Shorter file** (3-5 min clips instead of full album)

4. **Upgrade computer** (more RAM = faster)

### Q34: Memory error or crash - what's the fix?
**A:** Not enough RAM. **Solutions:**

1. **Close other apps** (browsers, Spotify, etc.)

2. **Use shorter files** (5 min instead of 20 min)

3. **Use BASIC analysis level** (less memory)

4. **Upgrade RAM** (if frequent issue)

### Q35: Plugin "not found in DAW" - how do I fix?
**A:** Installation issue. **Solutions:**

1. **Reinstall:**
   ```bash
   python3 plugins/installer.py --uninstall-all
   python3 plugins/installer.py --install-all
   ```

2. **Restart DAW completely** (not just close window)

3. **Check installation path:**
   ```bash
   python3 plugins/installer.py --verify
   ```

4. **Run as admin** (Windows)

### Q36: Backend not responding error - fix it?
**A:** For Ableton plugin only. **Solution:**

1. **Start backend:**
   ```bash
   python3 plugins/ableton/python_backend.py
   ```

2. **Keep window open** (running in background)

3. **Leave running** during Ableton session

4. **Verify it's running:**
   ```bash
   curl http://localhost:8001/health
   ```

### Q37: MIDI extraction gives wrong notes - how do I fix?
**A:** MIDI extraction accuracy depends on audio quality. **Solutions:**

1. **Try different type:**
   ```bash
   samplemind midi:extract song.wav --type harmony  # Instead of melody
   ```

2. **Use DETAILED analysis:**
   ```bash
   samplemind analyze:detailed song.wav first
   ```

3. **Edit in DAW** - Fix notes manually

4. **Use cleaner audio** - Less reverb = better extraction

### Q38: Permission denied error - what do I do?
**A:** File permission issue. **Solutions:**

**macOS/Linux:**
```bash
chmod +x samplemind
# Or use Python:
python3 -m samplemind analyze:full song.wav
```

**Windows:**
- Run Command Prompt as Administrator
- Or install with `--user` flag

### Q39: "Connection refused" - how do I fix?
**A:** Backend not running (for plugins). **Solution:**

```bash
# Start backend in separate terminal/window
python3 plugins/ableton/python_backend.py

# Keep window open while using plugin
# You'll see: "Uvicorn running on http://127.0.0.1:8001"
```

### Q40: Command not recognized - what's wrong?
**A:** SampleMind not installed or not in PATH. **Solution:**

```bash
# Check installation
samplemind --version

# If not found, reinstall:
pip install samplemind-ai==2.3.0b0

# If still not found, use full path:
python3 -m samplemind analyze:full song.wav
```

---

## Performance & Optimization (4 Questions)

### Q41: How can I speed up batch processing?
**A:** Process multiple files efficiently:

**Parallel processing:**
```bash
# Process 4 files simultaneously (macOS/Linux)
parallel samplemind analyze:full {} ::: *.wav
```

**Faster analysis:**
```bash
# Use BASIC level instead of STANDARD
samplemind analyze:basic *.wav
```

**Hardware:**
- More RAM = faster (especially >8GB)
- SSD = faster file I/O
- Multi-core CPU = parallel processing

### Q42: How much CPU does SampleMind use?
**A:** Depends on analysis level:

- **BASIC:** 20-30% CPU
- **STANDARD:** 40-60% CPU
- **DETAILED:** 70-90% CPU
- **PROFESSIONAL:** 90%+ CPU

**Impact:**
- DAW mixing: Use BASIC during production
- Offline processing: Use PROFESSIONAL for quality

### Q43: Can I limit CPU usage?
**A:** No built-in throttling, but **workarounds:**

1. **Use lower analysis level** (BASIC instead of DETAILED)
2. **Reduce file length** (analyze 5-min clip instead of full track)
3. **Close other apps** (free up CPU)
4. **Schedule offline** (run during night/breaks)

### Q44: How do I monitor performance?
**A:** Check system resources:

**macOS:**
```bash
Activity Monitor  # Built-in, shows CPU/RAM
```

**Linux:**
```bash
htop  # Shows CPU usage per process
```

**Windows:**
```
Ctrl+Shift+Esc  # Task Manager
```

---

## Features & Limitations (3 Questions)

### Q45: What features are in Phase 13?
**A:** **28 professional commands:**
- 12 audio effects
- 6 stem separation commands
- 5 MIDI generation commands
- 5 sample pack commands

See `/docs/CLI_REFERENCE.md` for full list.

### Q46: What's coming in Phase 14?
**A:** **Planned features:**
- Real-time plugin processing
- Multi-user plugin support
- Additional DAW support (Logic Pro, Studio One)
- Enhanced MIDI velocity mapping
- Crowd-sourced sample library

### Q47: What are known limitations?
**A:** **Current Phase 13:**
- ❌ No real-time plugin operation (analysis only)
- ❌ Monophonic MIDI extraction only
- ❌ No custom model training
- ⚠️ Single user per backend instance

**Workarounds:** See documentation or community forums.

---

## Getting More Help

### Documentation
- **Main Guide:** README.md
- **CLI Commands:** CLI_REFERENCE.md
- **API Docs:** API_REFERENCE.md
- **Plugin Installation:** PLUGIN_INSTALLATION_GUIDE.md
- **Tutorials:** PHASE_13_USER_QUICK_START.md

### Community
- **Issues:** https://github.com/samplemind/samplemind-ai/issues
- **Discussions:** https://github.com/samplemind/samplemind-ai/discussions
- **Discord:** [Community Link]
- **Email:** support@samplemind.ai

### Quick Help
```bash
samplemind --help
samplemind <command> --help
samplemind effects --help
```

---

**Last Updated:** February 3, 2026
**Version:** 1.0.0
**Status:** Complete FAQ for Phase 13.0-beta

