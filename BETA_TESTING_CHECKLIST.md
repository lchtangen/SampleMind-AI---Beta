# SampleMind AI v6 - Beta Testing Checklist

**Version:** 0.6.0 (Beta)
**Date:** 2025-10-04
**Status:** Ready for Beta Testing

---

## 🎯 Beta Testing Goals

1. Validate core functionality works on all platforms
2. Identify bugs and usability issues
3. Test AI integration with real music
4. Verify performance and speed
5. Collect user feedback

---

## 📋 Pre-Testing Setup

### Environment Setup
- [ ] Python 3.11+ installed
- [ ] Git repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed (`make setup`)
- [ ] Docker installed (for databases)
- [ ] Services running (MongoDB, Redis, ChromaDB)

### Configuration
- [ ] `.env` file created from `.env.example`
- [ ] API keys added (optional but recommended)
- [ ] Database URLs configured
- [ ] JWT secret set

### Verification
- [ ] Run `python --version` (should be 3.11+)
- [ ] Run `docker ps` (should show 3 containers)
- [ ] Run `pytest tests/unit/core/ -v` (23/23 should pass)

---

## 🧪 Feature Testing

### 1. Audio Engine Tests

#### Basic Analysis
- [ ] **Test:** Run `python scripts/demo_audio_analysis.py`
- [ ] Select a WAV file
- [ ] Verify tempo is detected
- [ ] Verify key is detected
- [ ] Check energy value (0.0-1.0)
- [ ] Check mood description
- [ ] **Expected:** Analysis completes in < 5 seconds

#### File Format Support
- [ ] Test with .wav file
- [ ] Test with .mp3 file
- [ ] Test with .flac file
- [ ] Test with .aiff file
- [ ] Test with .m4a file
- [ ] **Expected:** All formats load successfully

#### Analysis Levels
- [ ] BASIC analysis (tempo, key only)
- [ ] STANDARD analysis (+ energy, mood)
- [ ] DETAILED analysis (+ spectral features)
- [ ] **Expected:** Each level provides more details

#### Caching
- [ ] Analyze same file twice
- [ ] Note second analysis time
- [ ] **Expected:** Second analysis is much faster (~10x)

---

### 2. File Picker Tests

#### Ubuntu/Linux Testing
- [ ] Run `python test_file_picker_beta.py`
- [ ] Choice dialog appears (Zenity)
- [ ] Select "File"
- [ ] File picker appears (Zenity)
- [ ] Select an audio file
- [ ] **Expected:** 2 dialogs total, no duplicates

- [ ] Run again
- [ ] Select "Folder"
- [ ] Folder picker appears
- [ ] **Expected:** 2 dialogs total, no duplicates

#### macOS Testing (if available)
- [ ] Run `python test_file_picker_beta.py`
- [ ] AppleScript choice list appears
- [ ] Select "Select a File"
- [ ] Finder dialog appears
- [ ] Select file
- [ ] **Expected:** Native macOS experience

#### Windows Testing (if available)
- [ ] Run `python test_file_picker_beta.py`
- [ ] Terminal menu appears
- [ ] Type "1" for file
- [ ] Windows file dialog appears
- [ ] Select file
- [ ] **Expected:** Native Windows dialog

---

### 3. AI Integration Tests

#### Google Gemini Testing
- [ ] **Setup:** Add `GOOGLE_AI_API_KEY` to `.env`
- [ ] Run `python scripts/demo_ai_integration.py`
- [ ] Select audio file
- [ ] Wait for AI analysis
- [ ] Check genre detection
- [ ] Check mood analysis
- [ ] Check creative suggestions
- [ ] **Expected:** Completes in < 30 seconds

#### OpenAI Testing
- [ ] **Setup:** Add `OPENAI_API_KEY` to `.env`
- [ ] Comment out Google key temporarily
- [ ] Run `python scripts/demo_ai_integration.py`
- [ ] Select audio file
- [ ] Verify OpenAI is used
- [ ] Check analysis quality
- [ ] **Expected:** Falls back to OpenAI correctly

#### AI Manager (Auto-selection)
- [ ] **Setup:** Both API keys configured
- [ ] Run demo script
- [ ] Check which provider is used
- [ ] **Expected:** Google (primary) is used first

---

### 4. Batch Processing Tests

#### Small Batch (< 10 files)
- [ ] Run `python scripts/demo_batch_processing.py`
- [ ] Select folder with 5-10 audio files
- [ ] Watch progress
- [ ] Check all files processed
- [ ] Verify summary statistics
- [ ] **Expected:** Completes quickly, all files analyzed

#### Medium Batch (10-50 files)
- [ ] Select folder with 10-50 audio files
- [ ] Monitor processing time
- [ ] Check cache is working
- [ ] **Expected:** Fast processing due to caching

#### Large Batch (50+ files)
- [ ] Select folder with 50+ audio files
- [ ] Note processing time
- [ ] Verify all completed
- [ ] Check memory usage
- [ ] **Expected:** Stable, no crashes

---

### 5. API Server Tests

#### Server Startup
- [ ] Run `make dev`
- [ ] Check server starts
- [ ] Visit `http://localhost:8000`
- [ ] **Expected:** Welcome page appears

#### API Documentation
- [ ] Visit `http://localhost:8000/docs`
- [ ] Check Swagger UI loads
- [ ] Browse available endpoints
- [ ] **Expected:** Interactive API docs work

#### File Upload Endpoint
- [ ] In Swagger UI, find `/api/v1/analyze`
- [ ] Click "Try it out"
- [ ] Upload audio file
- [ ] Execute request
- [ ] Check response
- [ ] **Expected:** Analysis results returned

---

### 6. Database Integration Tests

#### MongoDB Connection
- [ ] Services running: `docker ps`
- [ ] Check MongoDB container is up
- [ ] Run: `docker exec -it samplemind-mongodb mongosh`
- [ ] Run: `show dbs`
- [ ] **Expected:** MongoDB accessible

#### Redis Connection
- [ ] Check Redis container is up
- [ ] Run: `docker exec -it samplemind-redis redis-cli PING`
- [ ] **Expected:** Response "PONG"

#### ChromaDB Connection
- [ ] Check ChromaDB container is up
- [ ] Visit: `http://localhost:8002/api/v1/heartbeat`
- [ ] **Expected:** JSON response with version

---

## 🐛 Bug Reporting

### When You Find a Bug

1. **Reproduce** - Can you make it happen again?
2. **Document:**
   - What did you do?
   - What happened?
   - What should have happened?
   - Error messages (if any)
   - Screenshots (if relevant)

3. **Environment Info:**
   ```bash
   python --version
   uname -a  # Linux/Mac
   # or
   ver  # Windows
   ```

4. **Report:**
   - File a GitHub issue
   - Include all info above
   - Label as "beta-testing"

---

## 📊 Performance Testing

### Speed Benchmarks

#### Single File Analysis
- [ ] Analyze 1 file (first time)
- [ ] Note time: _______ seconds
- [ ] Analyze same file again (cached)
- [ ] Note time: _______ seconds
- [ ] **Target:** First < 5s, Cached < 0.5s

#### Batch Processing
- [ ] Process 10 files
- [ ] Note total time: _______ seconds
- [ ] Calculate avg per file: _______ seconds
- [ ] **Target:** < 2s per file average

#### AI Analysis
- [ ] Single AI analysis
- [ ] Note time: _______ seconds
- [ ] **Target:** < 30s for comprehensive

### Resource Usage

#### Memory
- [ ] Check memory before: _______ MB
- [ ] Run batch processing (50 files)
- [ ] Check memory after: _______ MB
- [ ] **Target:** < 500MB increase

#### CPU
- [ ] Monitor CPU during batch processing
- [ ] Note peak usage: _______  %
- [ ] **Target:** < 80% sustained

---

## 🎨 User Experience Testing

### Ease of Use
- [ ] Setup was straightforward
- [ ] Demos easy to run
- [ ] File picker intuitive
- [ ] Results clear and useful
- [ ] Errors are understandable

### Documentation
- [ ] README is clear
- [ ] QUICKSTART_BETA.md is helpful
- [ ] Error messages guide to solution
- [ ] Examples are working

---

## 🔒 Security Testing (Optional)

- [ ] JWT tokens expire correctly
- [ ] Invalid API keys are rejected
- [ ] File uploads validate file types
- [ ] No sensitive data in logs
- [ ] Database credentials not exposed

---

## 📱 Platform-Specific Tests

### Ubuntu/Linux
- [ ] All features work
- [ ] Zenity dialogs appear
- [ ] No permission issues
- [ ] Audio file support complete

### macOS
- [ ] All features work
- [ ] Native dialogs work
- [ ] Security prompts handled
- [ ] Performance is good

### Windows
- [ ] All features work
- [ ] File dialogs work
- [ ] Paths handled correctly
- [ ] No encoding issues

---

## ✅ Beta Acceptance Criteria

### Must Pass (Blockers)
- [ ] Core audio analysis works
- [ ] File picker works on main platform
- [ ] No crashes during normal use
- [ ] At least 1 AI provider works
- [ ] Batch processing completes

### Should Pass (Important)
- [ ] All demo scripts work
- [ ] API server starts
- [ ] Tests pass (90%+)
- [ ] Performance acceptable
- [ ] Documentation accurate

### Nice to Have (Enhancements)
- [ ] Works on all platforms
- [ ] Both AI providers work
- [ ] Advanced features tested
- [ ] Edge cases handled
- [ ] UI/UX polished

---

## 📝 Feedback Form

### Overall Experience
- [ ] Excellent
- [ ] Good
- [ ] Fair
- [ ] Needs Improvement

### Most Useful Feature
- ___________________________________________

### Biggest Issue/Bug
- ___________________________________________

### Feature Requests
- ___________________________________________
- ___________________________________________
- ___________________________________________

### Would You Use This?
- [ ] Definitely
- [ ] Probably
- [ ] Maybe
- [ ] No

### Additional Comments
```
___________________________________________
___________________________________________
___________________________________________
```

---

## 🎯 Beta Testing Completion

### Sign Off

- **Tester Name:** ___________________________________________
- **Date Tested:** ___________________________________________
- **Platform:** ___________________________________________
- **Version:** ___________________________________________

### Summary
- Tests Passed: _____ / _____
- Bugs Found: _____
- Critical Issues: _____
- Performance: _____/10
- Usability: _____/10

### Recommendation
- [ ] **Ready for Production** - No critical issues
- [ ] **Ready with Fixes** - Minor issues to address
- [ ] **Needs Work** - Major issues found
- [ ] **Not Ready** - Critical problems

---

## 🚀 Next Steps After Beta

1. **Address Critical Bugs** - Fix any blockers
2. **Implement Top Feedback** - User-requested features
3. **Performance Optimization** - If needed
4. **Documentation Updates** - Based on feedback
5. **Production Deployment** - When ready

---

**Thank you for beta testing SampleMind AI!** 🎵

Your feedback helps make this better for everyone.
