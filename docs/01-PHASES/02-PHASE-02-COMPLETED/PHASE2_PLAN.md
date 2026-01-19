# Phase 2: AudioEngine Integration - Implementation Plan

**Date:** January 17, 2026
**Status:** Planning Phase (Ready to Implement)
**Duration:** Week 1-2
**Goal:** Connect Textual TUI to AudioEngine with real-time analysis and results display

---

## Executive Summary

Phase 2 integrates the production-ready AudioEngine with the Textual TUI framework, enabling:
- ✅ Real-time audio file analysis
- ✅ Live progress tracking during processing
- ✅ Beautiful results display with all audio features
- ✅ Batch file processing with parallel analysis
- ✅ Cross-platform file picker integration
- ✅ Comprehensive error handling

**Key Result:** Users can select audio files, watch analysis progress, and see detailed audio features in the terminal UI.

---

## AudioEngine API Overview (For Reference)

### Core Methods Available

1. **Single File Analysis** (Async)
   ```python
   features = await engine.analyze_audio_async(
       file_path,
       level=AnalysisLevel.STANDARD
   ) -> AudioFeatures
   ```
   Returns comprehensive audio features in ~1-2 seconds

2. **Batch Analysis** (Parallel)
   ```python
   results = engine.batch_analyze(
       file_paths,
       level=AnalysisLevel.STANDARD,
       parallel=True
   ) -> List[AudioFeatures]
   ```
   Analyzes multiple files using thread pool

3. **Performance Stats**
   ```python
   stats = engine.get_performance_stats() -> Dict
   # Returns: cache_hit_rate, avg_analysis_time, etc.
   ```

4. **Similarity Comparison**
   ```python
   similarity = engine.compare_audio_similarity(
       features1,
       features2
   ) -> float (0.0 - 1.0)
   ```

### AudioFeatures Structure

```
AudioFeatures dataclass contains:
├── Metadata (duration, sample_rate, channels, bit_depth)
├── Temporal (tempo, time_signature, beats, onset_times)
├── Tonal (key, mode, chroma_features)
├── Spectral (centroid, bandwidth, rolloff, zero_crossing_rate)
├── MFCC features (13 coefficients)
├── Rhythm (pattern, groove_template)
├── Harmonic/Percussive (if DETAILED level)
└── Performance stats (timestamp, file_hash, analysis_level)
```

---

## Implementation Plan

### Phase 2.1: Core AudioEngine Integration (Days 1-2)

#### Task 1.1: Create AudioEngine Wrapper
**File:** `src/samplemind/interfaces/tui/audio_engine_bridge.py`

Purpose: Wrap AudioEngine for TUI integration with async support

**Implementation:**
```python
class TUIAudioEngine:
    """Bridge between AudioEngine and TUI"""

    async def analyze_file(
        self,
        file_path: str,
        progress_callback: Callable[[float], None]
    ) -> AudioFeatures:
        """
        Analyze single file with progress updates
        progress_callback receives 0.0-1.0 percentage
        """
        pass

    async def analyze_batch(
        self,
        file_paths: List[str],
        progress_callback: Callable[[int, int], None]
    ) -> List[AudioFeatures]:
        """
        Analyze multiple files
        progress_callback receives (current, total) counts
        """
        pass

    def format_features_for_display(
        self,
        features: AudioFeatures
    ) -> Dict[str, str]:
        """Format audio features for nice display"""
        pass
```

**Status:** 📝 To be implemented

---

#### Task 1.2: Update AnalyzeScreen with AudioEngine
**File:** `src/samplemind/interfaces/tui/screens/analyze_screen.py`

**Changes:**
- Add progress bar widget
- Add results display area
- Connect file input to analyze button
- Show real-time analysis progress
- Display features on completion

**New methods:**
```python
async def _on_analyze_clicked(self) -> None:
    """Handle analyze button click"""
    # Get file path from input
    # Show progress bar
    # Call TUIAudioEngine.analyze_file()
    # Display results

async def _handle_analysis_progress(self, progress: float) -> None:
    """Update progress bar (0.0-1.0)"""

def _display_analysis_results(self, features: AudioFeatures) -> None:
    """Format and show results in results area"""
```

**Status:** 📝 To be implemented

---

#### Task 1.3: Create Results Display Screen
**File:** `src/samplemind/interfaces/tui/screens/results_screen.py`

**Purpose:** Beautiful display of analysis results

**Components:**
```
┌─ Results: song.wav ─────────────────────────────────────┐
│                                                          │
│ 📊 Audio Properties                                      │
│   Duration:        2:35 (155 seconds)                   │
│   Sample Rate:     44,100 Hz                            │
│   Channels:        Stereo (2)                           │
│   Bit Depth:       16-bit                               │
│                                                          │
│ 🎵 Musical Analysis                                      │
│   Tempo:           120 BPM                              │
│   Key:             C Major                              │
│   Time Signature:  4/4                                  │
│   Beats Detected:  152 beats                            │
│                                                          │
│ 📈 Spectral Features                                     │
│   Spectral Centroid:   2,450 Hz                         │
│   Spectral Rolloff:    8,200 Hz                         │
│   Zero Crossing Rate:  0.045                            │
│                                                          │
│ 🎚️ MFCC Summary                                         │
│   13 coefficients extracted ✓                           │
│                                                          │
│ Analysis Level: STANDARD | Time: 1.2s | Cache: HIT     │
│                                                          │
│ [⬅ Back] [💾 Save] [🔍 Compare]                       │
└──────────────────────────────────────────────────────────┘
```

**Status:** 📝 To be implemented

---

### Phase 2.2: File Picker Integration (Days 2-3)

#### Task 2.1: Update File Picker for TUI
**File:** `src/samplemind/utils/file_picker.py` (already exists)

**Status:** ✅ Already supports cross-platform (Finder, Zenity, KDialog, fallback)
**No changes needed** - just need to integrate into TUI

#### Task 2.2: Add File Picker to Screens
**Update both AnalyzeScreen and BatchScreen:**
- Add browse button handler
- Call existing `file_picker()` from utils
- Update input field when file selected
- Handle picker cancellation

**Code pattern:**
```python
async def _on_browse_clicked(self) -> None:
    """Open file picker"""
    from samplemind.utils.file_picker import pick_audio_file

    selected_file = await asyncio.to_thread(
        pick_audio_file  # Run in thread to avoid blocking TUI
    )

    if selected_file:
        self.query_one("#file_input", Input).value = selected_file
```

**Status:** 📝 To be implemented

---

### Phase 2.3: Batch Processing (Days 3-4)

#### Task 3.1: Enhance BatchScreen
**File:** `src/samplemind/interfaces/tui/screens/batch_screen.py`

**Current state:** Has file list table (DataTable)
**Enhancements:**
- Populate table with selected files
- Add progress indicator showing: `Processing: 3/10 files (30%)`
- Update table rows as each file completes
- Show analysis level selector (BASIC/STANDARD/DETAILED)
- Add cancel button

**New methods:**
```python
async def _on_process_clicked(self) -> None:
    """Start batch processing"""
    # Get folder from input
    # Scan for audio files
    # Populate data table
    # Call TUIAudioEngine.analyze_batch()

async def _handle_batch_progress(self, current: int, total: int) -> None:
    """Update progress label"""

def _update_file_row(self, file_index: int, features: AudioFeatures) -> None:
    """Update row with results"""
```

**Status:** 📝 To be implemented

---

### Phase 2.4: Error Handling & UI Polish (Days 4-5)

#### Task 4.1: Error Handling Dialogs
**File:** `src/samplemind/interfaces/tui/widgets/dialogs.py` (new)

**Dialog types:**
```python
async def show_error_dialog(
    parent_screen,
    title: str,
    message: str
) -> None:
    """Show error with OK button"""

async def show_info_dialog(
    parent_screen,
    title: str,
    message: str
) -> None:
    """Show info message"""

async def show_confirmation_dialog(
    parent_screen,
    title: str,
    message: str
) -> bool:
    """Show yes/no dialog"""
```

**Status:** 📝 To be implemented

---

#### Task 4.2: Notifications & Feedback
**Update MainScreen:**
- Add notification system for user feedback
- Show success messages after analysis
- Display errors clearly
- Add loading spinners during analysis

**Status:** 📝 To be implemented

---

### Phase 2.5: Testing (Days 5-6)

#### Task 5.1: Unit Tests
**File:** `tests/unit/interfaces/test_tui_audio_engine.py` (new)

**Tests needed:**
```python
test_analyze_single_file()          # Full analysis flow
test_analyze_batch_files()          # Batch processing
test_progress_callbacks()            # Progress tracking
test_error_handling()                # File not found, corrupted, etc.
test_features_formatting()           # Display formatting
test_cache_usage()                   # Verify caching works
```

**Status:** 📝 To be implemented

---

#### Task 5.2: Integration Tests
**File:** `tests/integration/test_tui_audio_workflow.py` (new)

**Scenarios:**
- Select file → Analyze → View results
- Analyze multiple files in batch
- Compare two audio files
- Error recovery (missing file, bad format)

**Status:** 📝 To be implemented

---

## Deliverables Checklist

### By End of Phase 2:

- ✅ AudioEngine bridge with async support
- ✅ Single file analysis with progress
- ✅ Results display screen with all features
- ✅ Batch processing with progress tracking
- ✅ File picker integration (all platforms)
- ✅ Error handling and user feedback
- ✅ Comprehensive test coverage
- ✅ Cross-platform validation
- ✅ Performance optimization
- ✅ Documentation and examples

---

## Testing Strategy

### Unit Tests
- TUIAudioEngine wrapper methods
- Feature formatting functions
- Progress callback handling
- Error cases

### Integration Tests
- Complete analysis workflow (select → analyze → display)
- Batch processing workflow
- Error recovery
- Cross-platform file picker

### Performance Tests
- Analysis time for various file sizes
- Memory usage during batch processing
- Cache effectiveness
- UI responsiveness during analysis

### Cross-Platform Testing
- File picker on Linux, macOS, Windows
- Analysis on all platforms
- Terminal rendering on various terminals

---

## Success Metrics

### Functionality (100%)
- ✓ Single file analysis working
- ✓ Batch processing working
- ✓ Results display complete and accurate
- ✓ File picker working on all platforms
- ✓ All errors handled gracefully

### Performance (Target)
- Single file: < 2 seconds analysis
- Batch (10 files): < 20 seconds total
- UI remains responsive during analysis
- Memory usage: < 500MB during operation
- Progress updates: 60 FPS

### Quality
- 80%+ test coverage
- All tests passing
- No critical bugs
- Clear error messages
- Professional UI/UX

---

## Files to Create/Modify

### New Files (6)
```
src/samplemind/interfaces/tui/
├── audio_engine_bridge.py          (AudioEngine wrapper)
├── screens/results_screen.py       (Results display)
├── widgets/dialogs.py              (Error/info dialogs)
├── widgets/progress_widget.py      (Progress indicators)
└── formatters/                     (new directory)
    └── feature_formatter.py        (Format features for display)

tests/
├── unit/interfaces/test_tui_audio_engine.py
└── integration/test_tui_audio_workflow.py
```

### Modified Files (4)
```
src/samplemind/interfaces/tui/
├── screens/main_screen.py          (Add error handling)
├── screens/analyze_screen.py       (Add analysis logic)
├── screens/batch_screen.py         (Add batch logic)
└── app.py                          (Register results screen)
```

---

## Timeline

| Week | Days | Phase | Deliverable |
|------|------|-------|------------|
| 1 | 1-2 | AudioEngine Integration | TUI bridge + single analysis |
| 1 | 2-3 | File Picker | Integrated on all platforms |
| 1 | 3-4 | Batch Processing | Multi-file analysis working |
| 1 | 4-5 | Error Handling | Robust error management |
| 2 | 5-6 | Testing | 80%+ coverage, all passing |
| 2 | 6-7 | Optimization | Performance targets met |
| 2 | 7 | Validation | Cross-platform tested |
| 2 | 7-8 | Release | PR ready, Phase 2 complete |

---

## Known Challenges & Solutions

### Challenge 1: Async/Await in TUI
**Problem:** Audio analysis is synchronous, TUI is async event loop
**Solution:** Use `asyncio.to_thread()` to run analysis without blocking
```python
features = await asyncio.to_thread(
    engine.analyze_audio,
    file_path,
    level
)
```

### Challenge 2: Progress Tracking
**Problem:** AudioEngine doesn't have built-in progress callbacks
**Solution:** Estimate progress based on analysis level and time elapsed
```python
# Start time + estimated duration = progress
elapsed = time.time() - start_time
estimated_duration = 2.0  # seconds for STANDARD
progress = min(elapsed / estimated_duration, 1.0)
```

### Challenge 3: Batch Processing UI
**Problem:** Multiple files need individual progress tracking
**Solution:** Update table rows as each file completes
```python
for i, file_path in enumerate(file_paths):
    features = await analyze_file(file_path)
    update_table_row(i, features)
    update_progress_label(i + 1, len(file_paths))
```

---

## Dependencies

### Existing (Already in Project)
- ✅ AudioEngine (src/samplemind/core/engine/)
- ✅ File picker utils (src/samplemind/utils/)
- ✅ Textual framework (v0.44.0+)
- ✅ Rich library (v13.7.0+)
- ✅ Audio libraries (librosa, soundfile, scipy)

### New (None needed)
All dependencies are already in pyproject.toml

---

## Next Steps

1. **Approve this plan** - Review and provide feedback
2. **Start implementation** - Begin with Task 1.1 (AudioEngine bridge)
3. **Iterative development** - Complete tasks in order
4. **Daily testing** - Verify each component works
5. **Cross-platform validation** - Test on Linux, macOS, Windows
6. **Code review** - Review before commit
7. **Create PR** - Merge to main after Phase 2 complete

---

## Phase 2 Success Criteria

### Minimum (MVP)
- ✓ Single file analysis with results display
- ✓ File picker working
- ✓ Error handling for invalid files
- ✓ Tests passing (50%+ coverage)

### Target
- ✓ Batch processing
- ✓ Progress tracking with progress bar
- ✓ Beautiful results display
- ✓ 80%+ test coverage
- ✓ Cross-platform tested

### Stretch
- ✓ File comparison feature
- ✓ Results export (JSON/CSV)
- ✓ Audio waveform visualization (simple)
- ✓ Performance optimization (<1s for standard analysis)

---

## Ready to Proceed?

This plan outlines a clear path to fully functional audio analysis in the Textual TUI. With 10 focused tasks over 1-2 weeks, we can deliver a professional audio analysis interface.

**Status:** ✅ Ready for implementation

Would you like to:
1. Start Phase 2 implementation immediately
2. Review/modify any tasks
3. Adjust timeline or scope
4. Begin with specific task

?
