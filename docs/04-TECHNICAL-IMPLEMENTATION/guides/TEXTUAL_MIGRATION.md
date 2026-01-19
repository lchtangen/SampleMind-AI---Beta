# Textual TUI Migration Guide

**Status:** Phase 1 - Foundation Complete ✅
**Date:** January 17, 2026
**Version:** 1.0.0 (Alpha)

## Overview

SampleMind AI is migrating from a custom Rich-based menu system to the **Textual framework** - a modern Python TUI framework offering world-class terminal UI capabilities.

### Why Textual?

- **Already installed** in project (v0.44.0+)
- **60 FPS smooth animations** with GPU-accelerated rendering
- **React-like component model** for intuitive development
- **CSS-like styling** for declarative UI design
- **Full mouse support** and keyboard shortcuts
- **Built on Rich** - preserves existing Rich code
- **Async/await native** - matches current architecture
- **Cross-platform** - Linux, macOS, Windows + web browser

### Alternative Considered: Rust Rewrite

❌ **NOT recommended** because:
- 6-12 month rewrite effort (vs. 2-3 weeks for Textual)
- Loss of entire Python audio stack (librosa, demucs, spleeter)
- Loss of AI SDK integrations (Google, OpenAI, Anthropic)
- Rust team ramp-up time
- Performance gains not the bottleneck (audio/AI processing are)

**Decision: ADOPT TEXTUAL** ✅

---

## Project Structure

```
src/samplemind/interfaces/tui/
├── __init__.py                 # Package initialization
├── app.py                      # Main Textual application class
├── main.py                     # Async entry point
├── widgets/                    # Reusable Textual widgets
│   ├── __init__.py
│   ├── menu.py                 # Main menu widget
│   └── status_bar.py           # Status bar with real-time updates
├── screens/                    # Individual application screens
│   ├── __init__.py
│   ├── main_screen.py          # Home screen with menu
│   ├── analyze_screen.py       # Single file analysis
│   └── batch_screen.py         # Batch processing
└── styles.css                  # TUI styling (future)

tests/unit/interfaces/
├── __init__.py
└── test_tui_app.py             # TUI unit tests

test_tui_standalone.py          # Quick validation tests (no pytest needed)
```

---

## Current Status: Phase 1 - Foundation ✅

### Completed Tasks

1. ✅ **TUI Directory Structure**
   - Created `/src/samplemind/interfaces/tui/`
   - Organized widgets, screens, app modules

2. ✅ **Core Application**
   - `SampleMindTUI` - Main Textual application class
   - Header/Footer support
   - Keyboard bindings (Q=quit, A=analyze, B=batch, H=help)

3. ✅ **Widgets**
   - `MainMenu` - Interactive 5-option menu with rich styling
   - `StatusBar` - Real-time session stats display
   - Both support reactive data updates

4. ✅ **Screens**
   - `MainScreen` - Home screen with menu and status
   - `AnalyzeScreen` - Single file analysis interface
   - `BatchScreen` - Folder batch processing interface
   - All have keyboard shortcuts and back navigation

5. ✅ **Testing**
   - Unit tests: `tests/unit/interfaces/test_tui_app.py`
   - Standalone validation: `test_tui_standalone.py`
   - All tests passing: ✅ 5/5

### Test Results

```
✅ TUI Imports - All modules import successfully
✅ TUI App Instantiation - App creates properly
✅ Screens Instantiation - All screens create properly
✅ Widgets Instantiation - All widgets create properly
✅ Keyboard Bindings - All shortcuts configured
```

**Summary:** TUI foundation is solid and ready for Phase 2

---

## Running the TUI

### Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Run TUI application
python -m samplemind.interfaces.tui.main

# Or with asyncio
python src/samplemind/interfaces/tui/app.py
```

### Keyboard Shortcuts

#### Main Application
- `Q` - Quit application
- `H` - Help information

#### Main Screen
- `A` - Analyze single file
- `B` - Batch process folder
- `↑/↓` - Navigate menu
- `Enter` - Select menu item

#### Analyze/Batch Screens
- `Escape` - Back to main screen
- `Enter` - Execute action (analyze/process)

---

## Architecture

### Component Hierarchy

```
SampleMindTUI (App)
├── MainScreen (Screen)
│   ├── Header
│   ├── MainMenu (Widget)
│   │   └── Label (menu options)
│   ├── StatusBar (Widget)
│   │   └── Reactive stats display
│   └── Footer
├── AnalyzeScreen (Screen)
│   ├── Header
│   ├── Input (file path)
│   ├── Buttons
│   ├── Results area
│   └── Footer
└── BatchScreen (Screen)
    ├── Header
    ├── Input (folder path)
    ├── DataTable (file list)
    ├── Progress indicator
    └── Footer
```

### Key Design Patterns

1. **Screen-based Navigation**
   - Screens push/pop from stack
   - Smooth transitions between screens

2. **Reactive Data**
   - `@reactive` decorator for auto-updating UI
   - StatusBar updates dynamically

3. **Message System**
   - Custom message classes for inter-component communication
   - `MainMenuOption` message for menu selection

4. **Keyboard Shortcuts**
   - Defined in `BINDINGS` tuple
   - Action methods prefixed with `action_`

---

## Next Steps: Phase 2 (Week 1-2)

### Priority Tasks

1. **AudioEngine Integration**
   - Connect TUI screens to AudioEngine
   - Show real-time analysis progress
   - Display audio features (tempo, key, etc.)

2. **File Picker Integration**
   - Reuse existing cross-platform file picker
   - Integration in AnalyzeScreen and BatchScreen

3. **Progress Indicators**
   - Add ProgressBar widget to analysis screen
   - Real-time progress updates during processing
   - Cancel operation support

4. **Results Display**
   - Create ResultsScreen for analysis results
   - Display audio features in formatted table
   - Show AI-generated coaching tips

5. **Batch Processing**
   - Parallel file processing with progress tracking
   - Summary statistics (files processed, time elapsed)
   - Error handling and recovery

### Expected Deliverables (Phase 2)

- ✅ Audio analysis working from TUI
- ✅ File picker integrated
- ✅ Results displayed beautifully
- ✅ Basic test coverage >50%
- ✅ Cross-platform validation (Linux, macOS, Windows)

---

## Development Guidelines

### Adding New Screens

```python
# 1. Create screen class
from textual.screen import Screen
from textual.widgets import Header, Footer

class NewScreen(Screen):
    BINDINGS = [("escape", "back", "Back")]

    def compose(self):
        yield Header()
        # Your widgets here
        yield Footer()

    def action_back(self):
        self.app.pop_screen()

# 2. Add to screens/__init__.py
from .new_screen import NewScreen

# 3. Use in app
await self.app.push_screen(NewScreen())
```

### Adding New Widgets

```python
# 1. Create widget class
from textual.widget import Widget
from textual.reactive import reactive

class NewWidget(Widget):
    value: reactive[str] = reactive("")

    def render(self):
        return f"Value: {self.value}"

    def update_value(self, new_value):
        self.value = new_value

# 2. Add to widgets/__init__.py
from .new_widget import NewWidget

# 3. Use in screens
yield NewWidget()
```

### Testing

```python
# Test in test_tui_app.py
def test_new_screen():
    from samplemind.interfaces.tui.screens import NewScreen
    screen = NewScreen()
    assert screen is not None
```

---

## Performance Targets

- **App startup:** < 500ms
- **Screen transitions:** < 200ms (60 FPS)
- **File analysis:** < 1s per file
- **Batch processing:** < 5s per 10 files
- **Memory usage:** < 500MB

---

## Known Limitations (Phase 1)

1. ⚠️ No AudioEngine integration yet (Phase 2)
2. ⚠️ File picker not integrated (Phase 2)
3. ⚠️ Results display not implemented (Phase 2)
4. ⚠️ AI features not connected (Phase 3)
5. ⚠️ Batch processing not functional (Phase 2)

---

## Troubleshooting

### Issue: Import errors when running TUI

**Solution:** Ensure `src` is in Python path:
```python
import sys
sys.path.insert(0, 'src')
```

### Issue: Textual not found

**Solution:** Install Textual:
```bash
pip install textual>=0.44.0
```

### Issue: Screen doesn't appear

**Solution:** Check that screen is yielded in `compose()` and added to app

### Issue: Keyboard shortcuts not working

**Solution:** Verify `BINDINGS` tuple format and action methods exist

---

## Resources

- **Textual Official:** https://textual.textualize.io/
- **Textual Tutorial:** https://textual.textualize.io/tutorial/
- **Widget Gallery:** https://textual.textualize.io/widget_gallery/
- **Rich Library:** https://rich.readthedocs.io/

---

## Migration Timeline

| Phase | Timeline | Focus | Status |
|-------|----------|-------|--------|
| 1 | Week 1 | Foundation, basic UI | ✅ COMPLETE |
| 2 | Week 1-2 | AudioEngine, file picker, results | 🔄 IN PROGRESS |
| 3 | Week 2 | AI integration, coaching tips | ⏳ PENDING |
| 4 | Week 2-3 | Advanced features, tagging, search | ⏳ PENDING |
| 5 | Week 3 | Performance optimization | ⏳ PENDING |
| 6 | Week 3-4 | Cross-platform testing | ⏳ PENDING |
| 7 | Week 4-5 | Quality, testing, documentation | ⏳ PENDING |
| 8 | Week 5-6 | Polish, beta testing, release | ⏳ PENDING |

---

## Success Criteria

### Phase 1 ✅ (ACHIEVED)
- ✅ TUI app launches
- ✅ Menu navigation works
- ✅ Keyboard shortcuts configured
- ✅ All tests passing

### Phase 2 🔄 (CURRENT)
- Audio analysis from TUI
- File picker integrated
- Progress tracking working
- Results displayed

### Final (Phase 6)
- 100% feature parity with old menu
- 80%+ test coverage
- Cross-platform tested
- <1s response times

---

## Questions?

Refer to CLAUDE.md for project context or check Textual documentation for framework details.

**Next:** Start Phase 2 with AudioEngine integration!
