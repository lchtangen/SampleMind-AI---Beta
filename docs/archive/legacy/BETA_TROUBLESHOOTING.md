# SampleMind AI Beta - Troubleshooting Guide

**Version**: 1.0
**Last Updated**: February 4, 2026
**For Issues**: Report in [GitHub Discussions 🐛 Troubleshooting](../../discussions?discussions_q=category%3ATroubleshooting)

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Launch & Startup Problems](#launch--startup-problems)
3. [Audio Analysis Issues](#audio-analysis-issues)
4. [DAW Integration Problems](#daw-integration-problems)
5. [Performance & Speed](#performance--speed)
6. [Data & Files](#data--files)
7. [Network & Cloud Issues](#network--cloud-issues)
8. [Error Messages](#error-messages)
9. [When to Get Help](#when-to-get-help)

---

## Installation Issues

### Problem: "ModuleNotFoundError: No module named 'samplemind'"

**Cause**: SampleMind not properly installed

**Solutions**:

1. **Verify Python version** (must be 3.11+)
   ```bash
   python --version
   ```
   If < 3.11: Download Python 3.11+ from python.org

2. **Reinstall SampleMind**
   ```bash
   pip install --upgrade samplemind-ai
   ```

3. **Verify installation**
   ```bash
   python -c "import samplemind; print(samplemind.__version__)"
   ```
   Should print version number

4. **Virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   pip install samplemind-ai
   ```

**If still failing**: File an issue with output of `pip show samplemind-ai`

---

### Problem: "Permission denied" during installation

**Cause**: Admin/sudo rights needed

**Solutions**:

**Windows**:
1. Run PowerShell as Administrator
2. Run installation command again

**macOS/Linux**:
1. Use `sudo`:
   ```bash
   sudo pip install samplemind-ai
   ```

2. Or better, use venv (no sudo needed):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install samplemind-ai
   ```

---

### Problem: "No space left on device"

**Cause**: Disk space full

**Solutions**:

1. **Check disk space**
   ```bash
   # macOS/Linux
   df -h

   # Windows (PowerShell)
   Get-Volume
   ```

2. **Free up space**
   - Delete old files
   - Empty trash/recycle bin
   - Move files to external drive

3. **Clean pip cache**
   ```bash
   pip cache purge
   ```

4. **Retry installation**
   ```bash
   pip install samplemind-ai
   ```

**Minimum required**: 2GB free disk space

---

### Problem: "Dependency version conflict"

**Cause**: Incompatible package versions

**Solutions**:

1. **Create fresh virtual environment**
   ```bash
   python -m venv samplemind-env
   source samplemind-env/bin/activate
   pip install samplemind-ai
   ```

2. **Update pip, setuptools, wheel**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install samplemind-ai
   ```

3. **Install specific version**
   ```bash
   pip install samplemind-ai==1.0.0
   ```

4. **Check for conflicting packages**
   ```bash
   pip list
   ```
   Look for old versions of related packages

---

## Launch & Startup Problems

### Problem: "Application won't start"

**Cause**: Various startup issues

**Troubleshooting steps**:

1. **Check Python**
   ```bash
   python --version  # Must be 3.11+
   ```

2. **Run with verbose output**
   ```bash
   python -m samplemind --verbose
   # or
   smai --debug
   ```

3. **Check error message** in console output
   - Look for specific error
   - Search for error message in troubleshooting

4. **Try different launch method**
   ```bash
   # Method 1: Direct Python
   python -m samplemind

   # Method 2: CLI command
   smai

   # Method 3: Long form
   samplemind-ai
   ```

5. **Clear cache and retry**
   ```bash
   rm -rf ~/.samplemind/cache  # macOS/Linux
   rmdir %AppData%\.samplemind\cache  # Windows
   smai
   ```

**Get help**: Report error message to support

---

### Problem: "Backend server failed to start"

**Cause**: API server port already in use or other issue

**Solutions**:

1. **Check if port 8000 is available**
   ```bash
   # macOS/Linux
   lsof -i :8000

   # Windows (PowerShell)
   Get-NetTCPConnection -LocalPort 8000
   ```

2. **Kill process on port 8000** (if needed)
   ```bash
   # macOS/Linux
   kill -9 $(lsof -t -i :8000)

   # Windows (PowerShell)
   Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force
   ```

3. **Use different port**
   ```bash
   export SAMPLEMIND_PORT=8001
   smai
   ```

4. **Restart computer**
   - Nuclear option, but often fixes port issues

---

### Problem: "Frontend not loading" or "Blank page"

**Cause**: Web app failed to start

**Solutions**:

1. **Check browser console**
   - Press F12 → Console tab
   - Look for error messages
   - Screenshot error and report

2. **Try different browser**
   - Use Chrome, Firefox, Safari, or Edge
   - Clear browser cache (Ctrl+Shift+Delete)

3. **Check localhost access**
   ```bash
   curl http://localhost:3000
   # Should show HTML, not connection error
   ```

4. **Restart web server**
   - Close terminal running SampleMind
   - Kill any existing processes:
     ```bash
     pkill -f samplemind
     pkill -f node
     ```
   - Start fresh

5. **Check port 3000**
   ```bash
   lsof -i :3000  # macOS/Linux
   # Kill if needed: kill -9 <PID>
   ```

**Last resort**: Restart computer and try again

---

## Audio Analysis Issues

### Problem: "No audio detected in file"

**Cause**: File is silent or not audio

**Solutions**:

1. **Verify file is audio**
   - Play in media player first
   - Check file extension (.wav, .mp3, etc.)
   - Check file is not corrupted

2. **Check file bitrate**
   ```bash
   # macOS/Linux (requires ffprobe)
   ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate file.mp3
   ```
   Should show non-zero bitrate

3. **Re-encode file**
   - Use Audacity or ffmpeg
   - Export as WAV (uncompressed)
   - Retry analysis

4. **Try example file**
   - Use sample audio from SampleMind
   - If works, your file might be corrupted

---

### Problem: "Unsupported file format"

**Cause**: File format not supported

**Solutions**:

1. **Check file format** - Supported formats:
   - ✅ WAV
   - ✅ MP3
   - ✅ FLAC
   - ✅ AIFF
   - ✅ OGG
   - ✅ M4A
   - ❌ WMA, AAC (not directly supported)

2. **Convert to WAV**
   ```bash
   # Using ffmpeg
   ffmpeg -i input.wma output.wav

   # Using Audacity
   # Open file → Export → WAV
   ```

3. **Check file extension**
   - Sometimes wrong extension causes issue
   - Verify extension matches actual format
   - Rename if needed

4. **Re-encode audio**
   - Use Audacity: File → Export → WAV
   - Use ffmpeg: `ffmpeg -i input.mp3 -c:a pcm_s16le output.wav`

---

### Problem: "Analysis taking forever" or "Stuck"

**Cause**: Slow analysis or system issue

**Solutions**:

1. **Check system resources**
   ```bash
   # macOS/Linux
   top  # Press 'q' to quit

   # Windows (Task Manager)
   Ctrl+Shift+Esc
   ```
   Look for:
   - High CPU (>90%): Normal during analysis
   - Low RAM (<500MB free): Close other apps
   - High disk activity: Wait for completion

2. **Check file size**
   - Larger files take longer (normal)
   - Try smaller section of file
   - Limit to 5-10 minutes of audio

3. **Try different analysis level**
   - Click "Analysis Level" → "BASIC"
   - BASIC is fastest (5-15 seconds)
   - STANDARD is good balance (15-30 seconds)

4. **Close other applications**
   - Browser, editors, other apps consume CPU
   - Close everything except SampleMind
   - Retry analysis

5. **Restart SampleMind**
   - Close app completely
   - Wait 10 seconds
   - Restart and try again

**If still slow** (>5 minutes):
- Check system specs (see [Installation Issues](#installation-issues))
- Consider upgrading RAM or using faster disk
- Report as potential bug

---

### Problem: "Analysis failed with error"

**Cause**: Various issues

**Solutions**:

1. **Read error message**
   - Most errors are self-explanatory
   - Search error in troubleshooting guide
   - Search in [GitHub Discussions](../../discussions)

2. **Try different file**
   - Use sample audio file
   - If works, your file might be problematic
   - Try re-encoding problematic file

3. **Try BASIC analysis level**
   - Some files fail on DETAILED
   - BASIC is more robust
   - Upgrade to STANDARD if BASIC works

4. **Check audio quality**
   - Very low bitrate might fail
   - MP3 320kbps or WAV recommended
   - Re-encode if needed

5. **Restart and retry**
   - Close app completely
   - Restart computer
   - Try again

**For specific errors**: See [Error Messages](#error-messages) section

---

### Problem: "Results look wrong/inaccurate"

**Cause**: Analysis incorrect or unusual

**Solutions**:

1. **Check audio quality**
   - Heavy processing can affect accuracy
   - Effects (reverb, compression) change results
   - Original unprocessed version more accurate

2. **Check file format**
   - Use WAV instead of MP3
   - MP3 compression loses harmonic content
   - Re-analyze with WAV version

3. **Manual correction**
   - Edit results before saving
   - Your judgment > AI judgment
   - Feedback helps improve accuracy

4. **Compare with other tools**
   - Ableton: Right-click → Detected Tempo
   - Music theory: Determine key yourself
   - Verify against your knowledge

5. **Check for edge cases**
   - Unusual genres: Accuracy decreases
   - Very slow/fast tempos: May confuse algorithm
   - Atonal music: Key detection very difficult

**This is normal**: AI analysis isn't perfect - use as suggestion

---

## DAW Integration Problems

### Problem: "Ableton plugin won't install"

**Cause**: Installation issue or wrong path

**Solutions**:

1. **Check OS** - Plugin version must match OS:
   - Windows: Install Windows version
   - macOS: Install macOS version
   - Linux: Install Linux version

2. **Verify Ableton version**
   - Requires Ableton 12+ with Max for Live
   - Older versions not supported
   - Upgrade if needed

3. **Admin rights**
   - Run installer as Administrator (Windows)
   - Use sudo if needed (macOS/Linux)

4. **Correct installation folder**
   - Windows: `C:\Program Files\Ableton\Live 12\Plugins\...`
   - macOS: `~/Library/Application Support/Ableton/Live/Plugins/...`
   - Linux: `~/.config/Ableton/Live/Plugins/...`

5. **Restart Ableton**
   - Close completely
   - Wait 10 seconds
   - Reopen
   - Plugin should appear in Max for Live

---

### Problem: "Plugin doesn't appear in Ableton"

**Cause**: Installation not completed or Ableton not restarted

**Solutions**:

1. **Restart Ableton** (properly)
   - Close Ableton completely
   - Close terminal/command prompt
   - Open Task Manager/Activity Monitor
   - Kill any Ableton processes
   - Wait 10 seconds
   - Reopen Ableton

2. **Check installation**
   - Verify files exist in plugin directory
   - Files should be: `SampleMind.amxd` and supporting files
   - If missing, reinstall

3. **Enable Max for Live**
   - Click Help → Max License Info
   - Verify Max for Live is activated
   - Activate if needed (free with Live 12+)

4. **Rebuild plugin cache**
   - In Ableton: Preferences → Library
   - Click "Rescan Library"
   - Wait for completion
   - Restart Ableton

5. **Reinstall plugin**
   ```bash
   # Windows
   samplemind-installer.exe --reinstall

   # macOS/Linux
   sudo ./install-plugin.sh --reinstall
   ```

---

### Problem: "Plugin crashes when opening"

**Cause**: Plugin initialization error

**Solutions**:

1. **Check Max for Live**
   - Plugin requires Max for Live
   - Help → Max License Info
   - Activate if not already

2. **Check Python**
   - Plugin requires Python 3.11+
   - Check: `python --version`
   - Upgrade if needed

3. **Check SampleMind installation**
   ```bash
   python -c "import samplemind; print('OK')"
   ```
   If error: Reinstall SampleMind

4. **Reinstall plugin**
   - Uninstall plugin completely
   - Delete plugin folder
   - Reinstall fresh

5. **Use stand-alone app**
   - Plugin is optional
   - Can use file export/import instead
   - Still fully functional

**If persists**: File issue on [GitHub Issues](../../issues)

---

## Performance & Speed

### Problem: "App is slow/laggy"

**Cause**: System resources or inefficient processing

**Solutions**:

1. **Check system resources**
   ```bash
   # macOS/Linux
   top

   # Windows (PowerShell)
   Get-Process | Sort-Object CPU -Descending | Select -First 10
   ```
   Close CPU-heavy applications

2. **Close other applications**
   - Browsers, editors, etc. use RAM
   - Close everything except SampleMind
   - Close browser tabs

3. **Check disk space**
   ```bash
   df -h  # macOS/Linux
   ```
   Need at least 1GB free

4. **Reduce analysis level**
   - PROFESSIONAL → DETAILED → STANDARD → BASIC
   - Use BASIC for faster results
   - Lower quality = lower latency

5. **Smaller files**
   - Large files take longer to process
   - Try 5-minute clips instead of 30-min songs
   - Batch process in chunks

6. **Restart application**
   - Memory leaks possible
   - Close and restart helps
   - Restart computer if persists

---

### Problem: "Network is slow"

**Cause**: Cloud AI features use network

**Solutions**:

1. **Check internet speed**
   ```bash
   # Download speedtest-cli
   pip install speedtest-cli
   speedtest
   ```
   Need at least 2 Mbps for cloud AI

2. **Improve connection**
   - Use Ethernet instead of WiFi
   - Move closer to router
   - Restart router
   - Check for interference

3. **Use local analysis only**
   - Uncheck "Use Cloud AI"
   - Analysis will be slower but work offline
   - Reduces network dependency

4. **Analyze during off-peak**
   - Network slower during peak hours
   - Try early morning or late night
   - Reduces server load

---

## Data & Files

### Problem: "Can't find my samples"

**Cause**: Sample library location issue

**Solutions**:

1. **Check library location**
   - Settings → Library
   - Note the location path
   - Verify path exists on disk

2. **Rescan library**
   - Settings → Library → Rescan
   - Wait for completion
   - Samples should appear

3. **Move samples to library**
   - Drag files into library folder
   - Or use Import → Add Folder
   - Wait for indexing

4. **Check permissions**
   - Verify folder is readable
   - Check file permissions: `chmod 755 folder`
   - Try different location if needed

---

### Problem: "Lost analysis results"

**Cause**: Data not saved or database issue

**Solutions**:

1. **Check auto-save**
   - Results should auto-save
   - Verify data folder exists: `~/.samplemind/data`
   - Check folder has space

2. **Recover from backup**
   - If backup exists, restore it
   - Previous versions might have data

3. **Re-analyze files**
   - Re-import audio files
   - Re-run analysis
   - Should be faster this time (caching)

4. **Export before losing**
   - Always export important results
   - Save CSV, PDF, or JSON
   - Prevents total data loss

---

### Problem: "Can't export results"

**Cause**: File write issue

**Solutions**:

1. **Check export location**
   - Verify folder exists
   - Verify you have write permissions
   - Try different folder

2. **Check disk space**
   - Export requires disk space
   - Delete unused files if needed
   - Try external drive if needed

3. **Check file format**
   - Supported: PDF, CSV, JSON, MIDI
   - Not all analysis levels support all formats
   - Try different format

4. **File already exists**
   - Delete existing file
   - Or use different filename
   - Retry export

---

## Network & Cloud Issues

### Problem: "Cloud AI features unavailable"

**Cause**: Network or API issue

**Solutions**:

1. **Check internet connection**
   ```bash
   ping google.com
   ```
   Should respond with times

2. **Check firewall/proxy**
   - SampleMind may be blocked
   - Check firewall settings
   - Add SampleMind to allowed apps
   - Ask IT if corporate network

3. **Check API service status**
   - Visit status.samplemind.ai
   - Might have temporary outage
   - Wait for service to be restored

4. **Use local analysis**
   - Uncheck "Cloud AI"
   - Local models still work
   - Offline-first approach

5. **Check credentials**
   - Verify API key is correct
   - Regenerate if needed
   - Settings → Cloud → API Key

---

### Problem: "API key error" or "Authentication failed"

**Cause**: Invalid or expired API key

**Solutions**:

1. **Check API key**
   - Settings → Cloud → API Key
   - Should start with `samplemind_`
   - Verify complete without typos

2. **Regenerate API key**
   - Go to Dashboard
   - Account → API Keys
   - Click "Generate New Key"
   - Copy and paste into settings
   - Delete old key

3. **Check account status**
   - Login to samplemind.ai
   - Verify account is active
   - Check for billing issues
   - Check email for notices

4. **Disable and re-enable**
   - Turn off cloud AI
   - Restart app
   - Turn back on
   - Re-enter API key

---

## Error Messages

### "CUDA out of memory"

**Meaning**: GPU ran out of memory

**Solutions**:
1. Close other GPU-intensive apps (games, video editors)
2. Use CPU analysis (uncheck GPU in settings)
3. Analyze smaller files
4. Upgrade GPU (if serious issue)

---

### "Connection refused"

**Meaning**: Backend server not running or port blocked

**Solutions**:
1. Restart SampleMind
2. Check port is not in use: `lsof -i :8000`
3. Check firewall allows localhost
4. Try different port: `export SAMPLEMIND_PORT=8001`

---

### "File not found"

**Meaning**: Audio file path invalid

**Solutions**:
1. Verify file exists and path is correct
2. Avoid spaces/special characters in path
3. Use absolute path instead of relative
4. Check file hasn't been moved/deleted

---

### "Segmentation fault"

**Meaning**: Program crashed (C++ issue)

**Solutions**:
1. Restart app and retry
2. Restart computer
3. Update all packages: `pip install --upgrade samplemind-ai`
4. Report issue with full error details

---

### "TorchMUX not found"

**Meaning**: PyTorch not installed correctly

**Solutions**:
1. Reinstall PyTorch:
   ```bash
   pip install torch --upgrade
   ```
2. Reinstall SampleMind:
   ```bash
   pip install samplemind-ai --upgrade --force-reinstall
   ```

---

## When to Get Help

### Self-help first (check these):
1. ✅ This troubleshooting guide
2. ✅ [BETA_FAQ.md](./BETA_FAQ.md)
3. ✅ Search [GitHub Discussions](../../discussions)
4. ✅ Restart computer and retry

### Then ask for help:
1. **GitHub Discussions** - [🐛 Troubleshooting](../../discussions?discussions_q=category%3ATroubleshooting)
   - Best for community help
   - Fast responses (usually <24h)
   - Share error messages

2. **GitHub Issues** - [Report bug](../../issues)
   - For confirmed bugs
   - Include reproduction steps
   - Attach error logs

3. **Email Support** - support@samplemind.ai
   - For urgent issues
   - Non-technical problems
   - Account/license issues
   - Response time: 24-48 hours

### When reporting, include:
- **Error message** (full text, not screenshot)
- **Steps to reproduce** (exact steps)
- **OS and version** (`uname -a` or Windows version)
- **SampleMind version** (`smai --version`)
- **Python version** (`python --version`)
- **System specs** (RAM, CPU, disk space)
- **Sample file** (or similar file to test with)

---

## Quick Reference

| Issue | First Try | Second Try |
|-------|-----------|-----------|
| App won't start | Restart app | Restart computer |
| Analysis slow | Close other apps | Try BASIC level |
| Wrong results | Use WAV file | Manual correction |
| Plugin won't appear | Restart Ableton | Reinstall plugin |
| Network error | Check internet | Use offline mode |

---

## Getting Better Help

**When reporting issues, help us help you**:
- ✅ Be specific (not "it doesn't work")
- ✅ Include error messages (exact text)
- ✅ Provide steps to reproduce
- ✅ Include system information
- ✅ One issue per report
- ✅ Search existing issues first

**Example of good report**:
```
Title: Analysis fails with "CUDA out of memory" on 100MB WAV

Environment:
- OS: Windows 11 21H2
- Python: 3.11.6
- SampleMind: 1.0.0
- GPU: RTX 2060 (6GB)

Steps:
1. Load 100MB WAV file
2. Select PROFESSIONAL analysis
3. Click Analyze
4. Get error: "CUDA out of memory"

Expected: Analysis completes
Actual: Error and freeze

Works: STANDARD analysis or smaller files
```

---

**Last Updated**: February 4, 2026
**Version**: 1.0 (Beta)
**Status**: Complete - Ready for Beta

**Still need help?** Post in [🙏 Q&A](../../discussions?discussions_q=category%3AQ%26A) - community and team are here to help!
