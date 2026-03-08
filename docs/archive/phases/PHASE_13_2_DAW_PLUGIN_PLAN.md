# Phase 13.2: DAW Plugin Development - Comprehensive Implementation Plan

**Date**: February 3, 2026
**Status**: 35% Complete (Plugin Architecture + FL Studio Skeleton)
**Objective**: Complete DAW plugin development for FL Studio and Ableton Live
**Estimated Duration**: 10-15 days total

---

## Executive Summary

Phase 13.2 focuses on integrating SampleMind AI into professional DAW environments (FL Studio and Ableton Live) through native plugins. This enables seamless real-time audio analysis, sample management, and library integration directly within users' production workflows.

**Current State**:
- ✅ Plugin base architecture: 100% complete (300+ lines)
- ✅ FL Studio plugin skeleton: 100% complete (400+ lines)
- ⏳ FL Studio compilation: Pending (needs FL Studio SDK)
- ⏳ Ableton Live plugin: Not started
- ⏳ Plugin installer: Not started

---

## Phase 13.2.1: FL Studio Plugin Completion (5-6 days)

### Current Implementation

**File**: `plugins/fl_studio_plugin.py` (400+ lines)
- Complete Python skeleton with all methods
- Sample browser functionality
- Analysis display
- Drag-and-drop support
- State management

### Remaining Work

#### 1. C++ Plugin Wrapper (2-3 days)

**What's Needed**:
```cpp
// File: plugins/fl_studio/samplemind_wrapper.cpp (~300 lines)
// FL Studio SDK integration layer

#include "fl_sdk/flplugin.h"
#include <Python.h>

class SampleMindFLPlugin : public CPlugin {
public:
    // Plugin initialization
    void onInit();

    // Audio processing callback
    void onProcess();

    // Parameter handling
    void onParamChange(int param, float value);

    // Preset management
    void onLoadPreset(int index);
    void onSavePreset(int index);

    // UI rendering
    void onRender(HDC dc);

    // State persistence
    void onSave(FXState& state);
    void onLoad(FXState& state);

private:
    PyObject* pPythonPlugin;  // Python plugin instance
    PyObject* pPythonModule;  // SampleMind module

    // Helper methods
    void initializePython();
    void processAudioBuffer(float* buffer, int length);
    void updateParametersFromPython();
};
```

**Tasks**:
1. Create C++ project structure in `plugins/fl_studio/cpp/`
2. Implement FL SDK callbacks
3. Create Python-to-C bridge using ctypes/ctypes wrapping
4. Handle audio buffer processing
5. Implement parameter mapping (FL Studio parameters ↔ Python parameters)

#### 2. CMake Build Configuration (1 day)

**File**: `plugins/fl_studio/CMakeLists.txt` (~100 lines)

```cmake
cmake_minimum_required(VERSION 3.16)
project(SampleMind_FL_Studio_Plugin)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find FL Studio SDK
find_package(FLStudio REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Development)

# Source files
set(SOURCES
    samplemind_wrapper.cpp
    audio_processor.cpp
    parameter_handler.cpp
    ui_renderer.cpp
)

# Create plugin library
add_library(SampleMind_FL MODULE ${SOURCES})

# Link libraries
target_link_libraries(SampleMind_FL
    PRIVATE
        FLStudio::SDK
        Python3::Python
)

# Include directories
target_include_directories(SampleMind_FL
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${FL_STUDIO_SDK_PATH}/include
)

# Platform-specific configurations
if(MSVC)
    # Windows specific
    set_target_properties(SampleMind_FL PROPERTIES SUFFIX ".dll")
elseif(APPLE)
    # macOS specific
    set_target_properties(SampleMind_FL PROPERTIES SUFFIX ".component")
else()
    # Linux specific
    set_target_properties(SampleMind_FL PROPERTIES SUFFIX ".so")
endif()
```

**Tasks**:
1. Create CMakeLists.txt with proper FL SDK detection
2. Configure platform-specific build settings
3. Set up debug/release configurations
4. Create build scripts for Windows/macOS/Linux

#### 3. Audio Processing Pipeline (1 day)

**File**: `plugins/fl_studio/cpp/audio_processor.cpp` (~200 lines)

```cpp
void SampleMindFLPlugin::processAudioBuffer(float* buffer, int length) {
    // 1. Convert buffer to numpy array
    PyObject* audioArray = PyArray_SimpleNewFromData(
        1, (npy_intp*)&length, NPY_FLOAT32, buffer
    );

    // 2. Call Python processing function
    PyObject* args = PyTuple_Pack(1, audioArray);
    PyObject* result = PyObject_CallObject(pProcessFunc, args);

    // 3. Extract processed audio
    float* processedData = (float*)PyArray_DATA((PyArrayObject*)result);
    memcpy(buffer, processedData, length * sizeof(float));

    // 4. Cleanup
    Py_DECREF(audioArray);
    Py_DECREF(args);
    Py_DECREF(result);
}
```

**Tasks**:
1. Implement real-time audio buffer processing
2. Create Python-C bridge for audio data
3. Handle mono/stereo audio
4. Implement latency compensation
5. Add thread-safe operations

#### 4. Parameter & Preset System (1 day)

**File**: `plugins/fl_studio/cpp/parameter_handler.cpp` (~150 lines)

FL Studio parameter mapping:
```
FL Parameter ID → Python Parameter Name
0-7:    Analysis Level (0=BASIC, 7=PROFESSIONAL)
8-15:   Effect Select (0=None, 8=Effects)
16-23:  Library Search (string)
24-31:  Sample Browser (index)
32-39:  Analysis Display Options
40-47:  Output Format (JSON/YAML/CSV)
48-127: Reserved for future expansion
```

**Tasks**:
1. Map FL Studio parameters to Python equivalents
2. Implement preset save/load system
3. Create parameter change callbacks
4. Handle real-time parameter updates
5. Implement undo/redo support

#### 5. Testing & Compilation (1-2 days)

**Tasks**:
1. Set up FL Studio development environment
2. Compile on Windows (primary platform)
3. Test audio processing pipeline
4. Test parameter changes
5. Test preset management
6. Create installation package

---

## Phase 13.2.2: Ableton Live Plugin (5-6 days)

### Architecture Overview

Ableton Live uses Max for Live (visual programming environment) for custom plugins. We'll create a Max device that connects to SampleMind backend via REST API.

### Implementation Plan

#### 1. Max for Live Device Structure (1 day)

**File**: `plugins/ableton/SampleMind.amxd` (Max patcher file)

Components:
```
┌─────────────────────────────────────┐
│        SampleMind for Live          │
├─────────────────────────────────────┤
│ [Sample Browser Pane]               │
│  • File picker                      │
│  • Recent files                     │
│  • Search/Filter                    │
├─────────────────────────────────────┤
│ [Analysis Display Pane]             │
│  • BPM / Key / Genre / Mood         │
│  • Waveform display                 │
│  • Confidence scores                │
├─────────────────────────────────────┤
│ [Project Sync Pane]                 │
│  • Project BPM matching             │
│  • Key matching                     │
│  • Auto-recommendations             │
├─────────────────────────────────────┤
│ [MIDI Mapping Pane]                 │
│  • MIDI note assignments            │
│  • CC mappings                      │
│  • Performance controls             │
├─────────────────────────────────────┤
│ [Settings Pane]                     │
│  • API endpoint configuration       │
│  • Analysis level selection         │
│  • Output format                    │
└─────────────────────────────────────┘
```

**Max Objects Needed**:
- `fpic` - File picker
- `table` - Waveform display
- `number~` - Real-time analysis values
- `message` - API calls
- `dict` - JSON handling
- `jit.matrix` - Spectrogram visualization

**Tasks**:
1. Design Max patcher UI layout
2. Create message/data flow architecture
3. Implement sample browser pane
4. Create analysis display pane
5. Add project sync logic

#### 2. Backend REST API Integration (2 days)

**File**: `plugins/ableton/python_backend.py` (~400 lines)

```python
# Start on user's machine
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/api/analyze/{filename}")
async def analyze_sample(filename: str):
    """Analyze sample and return metadata"""
    # Call SampleMind engine
    result = audio_engine.analyze_full(filename)
    return result

@app.post("/api/find-similar")
async def find_similar(file_path: str, limit: int = 10):
    """Find similar samples in library"""
    return engine.find_similar(file_path, limit)

@app.get("/api/project-sync")
async def get_project_sync_recommendations(project_bpm: float, project_key: str):
    """Get BPM/key matching recommendations"""
    # Query library for matches
    return db.find_by_bpm_key(project_bpm, project_key)

@app.post("/api/generate-midi/{type}")
async def generate_midi(type: str, file_path: str):
    """Extract MIDI (melody/chords/drums)"""
    return midi_generator.extract(file_path, type)
```

**Tasks**:
1. Create FastAPI backend
2. Implement API endpoints
3. Handle long-running operations with background tasks
4. Implement caching and optimization
5. Error handling and logging

#### 3. Max JavaScript Communication (1 day)

**File**: `plugins/ableton/communication.js` (~200 lines)

```javascript
// Max for Live JavaScript
autowatch = 1;

var api_endpoint = "http://localhost:8000/api";

function analyze_file(filepath) {
    var url = api_endpoint + "/analyze";
    var xhr = new XMLHttpRequest();

    xhr.onload = function() {
        if (xhr.status == 200) {
            var result = JSON.parse(xhr.responseText);
            outlet(0, "analysis_result", result);
        }
    };

    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({filepath: filepath}));
}

function project_sync_recommendations() {
    var bpm = this.patcher.getattr("live_set").tempo;
    var key = get_current_key();

    var url = api_endpoint + "/project-sync";
    // Similar fetch pattern...
}
```

**Tasks**:
1. Create HTTP communication layer
2. Implement JSON parsing
3. Add error handling
4. Create callback system
5. Handle async operations

#### 4. MIDI Mapping & Control (1 day)

**File**: `plugins/ableton/midi_mapper.maxpat`

Features:
- Map MIDI notes to sample triggers
- CC assignments for parameter control
- Velocity sensitivity
- Modulation wheel mapping
- Expression pedal support

**Tasks**:
1. Create MIDI input handling
2. Implement mapping interface
3. Add preset system
4. Test with controllers

#### 5. Testing & Packaging (1 day)

**Tasks**:
1. Test in Ableton Live
2. Test project sync functionality
3. Test MIDI mapping
4. Create user documentation
5. Package for distribution

---

## Phase 13.2.3: Plugin Installer (1-2 days)

### Installation Framework

**File**: `plugins/installer.py` (~300 lines)

```python
#!/usr/bin/env python3
"""
SampleMind AI Plugin Installer
Cross-platform installation for FL Studio and Ableton Live
"""

import platform
import shutil
from pathlib import Path
import subprocess

class PluginInstaller:
    def __init__(self):
        self.system = platform.system()  # Windows, Darwin, Linux
        self.daw_paths = self.detect_daw_installations()

    def detect_daw_installations(self) -> dict:
        """Auto-detect DAW installations"""
        daws = {}

        if self.system == "Windows":
            # Check registry for FL Studio installation
            fl_path = self._find_fl_studio_windows()
            if fl_path:
                daws["fl_studio"] = fl_path

            # Check Program Files for Ableton
            ableton_path = Path("C:/Program Files/Ableton/Live 12")
            if ableton_path.exists():
                daws["ableton"] = ableton_path

        elif self.system == "Darwin":  # macOS
            fl_path = Path.home() / "Applications/FL Studio.app"
            if fl_path.exists():
                daws["fl_studio"] = fl_path

            ableton_path = Path("/Applications/Ableton Live 12.app")
            if ableton_path.exists():
                daws["ableton"] = ableton_path

        elif self.system == "Linux":
            # Check common paths
            fl_path = Path.home() / ".local/share/FL Studio"
            ableton_path = Path.home() / ".config/Ableton"

            if fl_path.exists():
                daws["fl_studio"] = fl_path
            if ableton_path.exists():
                daws["ableton"] = ableton_path

        return daws

    def install_fl_studio_plugin(self):
        """Install FL Studio plugin"""
        if "fl_studio" not in self.daw_paths:
            print("❌ FL Studio not found. Please specify installation path.")
            return False

        fl_path = self.daw_paths["fl_studio"]
        plugin_path = fl_path / "Plugins" / "Fruity" / "Generators"

        # Copy DLL/SO/dylib
        plugin_files = list(Path("plugins/fl_studio/build").glob("SampleMind*"))

        for plugin_file in plugin_files:
            shutil.copy2(plugin_file, plugin_path / plugin_file.name)
            print(f"✓ Installed {plugin_file.name}")

        # Register plugin
        self._register_fl_plugin(plugin_path)
        print("✓ FL Studio plugin installed successfully!")
        return True

    def install_ableton_plugin(self):
        """Install Ableton Live plugin"""
        if "ableton" not in self.daw_paths:
            print("❌ Ableton Live not found.")
            return False

        ableton_path = self.daw_paths["ableton"]
        max_patches_path = ableton_path / "Max Patches" / "Instruments"

        # Copy Max device
        device_file = Path("plugins/ableton/SampleMind.amxd")
        shutil.copy2(device_file, max_patches_path / device_file.name)

        # Install Python backend
        backend_path = Path.home() / ".samplemind" / "ableton_backend"
        backend_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2("plugins/ableton/python_backend.py", backend_path)

        print("✓ Ableton Live plugin installed successfully!")
        return True

    def verify_installation(self):
        """Verify plugins are installed correctly"""
        results = {}

        # Check FL Studio
        if "fl_studio" in self.daw_paths:
            results["fl_studio"] = self._verify_fl_installation()

        # Check Ableton
        if "ableton" in self.daw_paths:
            results["ableton"] = self._verify_ableton_installation()

        return results

def main():
    """Main installation routine"""
    installer = PluginInstaller()

    print("🎛️  SampleMind AI Plugin Installer")
    print("=" * 50)

    daws_found = installer.detect_daw_installations()
    if not daws_found:
        print("❌ No supported DAWs found on your system.")
        return

    print(f"Found {len(daws_found)} DAW(s):")
    for daw, path in daws_found.items():
        print(f"  • {daw}: {path}")
    print()

    # Ask which to install
    print("Which plugins to install?")
    install_fl = input("Install FL Studio plugin? (y/n) ").lower() == 'y'
    install_ableton = input("Install Ableton Live plugin? (y/n) ").lower() == 'y'

    if install_fl:
        installer.install_fl_studio_plugin()

    if install_ableton:
        installer.install_ableton_plugin()

    # Verify
    print("\nVerifying installation...")
    results = installer.verify_installation()

    for daw, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {daw}")

    print("\n✅ Installation complete!")
```

**Tasks**:
1. Create installer framework
2. Implement DAW auto-detection
3. Create installation routines
4. Add verification checks
5. Create uninstaller

---

## Implementation Priority & Timeline

### Week 1: FL Studio Plugin (Days 1-5)

| Day | Task | Effort | Status |
|-----|------|--------|--------|
| 1 | C++ wrapper structure + CMake | 1 day | ⏳ |
| 2-3 | Audio pipeline + Parameters | 2 days | ⏳ |
| 4 | Testing & Compilation | 1 day | ⏳ |
| 5 | Packaging & Documentation | 1 day | ⏳ |

### Week 2: Ableton + Installer (Days 6-10)

| Day | Task | Effort | Status |
|-----|------|--------|--------|
| 6 | Max patcher UI design | 1 day | ⏳ |
| 7-8 | API backend + Communication | 2 days | ⏳ |
| 9 | Testing & Deployment | 1 day | ⏳ |
| 10 | Installer framework | 1 day | ⏳ |

---

## Critical Dependencies

### FL Studio Plugin
- [ ] FL Studio SDK installed and verified
- [ ] C++ compiler (MSVC on Windows, Clang on macOS, GCC on Linux)
- [ ] CMake 3.16+
- [ ] Python development headers
- [ ] ctypes or ctypes-cffi for Python-C bridge

### Ableton Live Plugin
- [ ] Ableton Live 12+ with Max for Live
- [ ] Max 8.0+
- [ ] REST API testing tools (curl, Postman)

### General
- [ ] Cross-platform testing capability
- [ ] Git for version control
- [ ] Documentation tools

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| FL Studio SDK issues | Medium | High | Start with skeleton, test incrementally |
| Python-C bridge complexity | Medium | High | Use well-tested libraries (ctypes) |
| Cross-platform compilation | High | Medium | Test early on all 3 platforms |
| Ableton API changes | Low | Medium | Monitor official documentation |
| Performance bottlenecks | Medium | Medium | Profile and optimize audio pipeline |

---

## Success Criteria

✅ **FL Studio Plugin**
- Compiles without errors on Windows/macOS/Linux
- Loads in FL Studio without crashes
- Sample browser functional
- Analysis display shows results
- Drag-and-drop works
- Presets save/load correctly

✅ **Ableton Live Plugin**
- Max device loads in Ableton Live
- REST API communication working
- Project sync recommendations appear
- MIDI mapping functional
- All features accessible from interface

✅ **Installer**
- Auto-detects DAW installations
- Installs plugins correctly
- Verification passes
- Uninstall works cleanly
- Cross-platform compatible

---

## Deliverables

By end of Phase 13.2:

1. **FL Studio Plugin** (Complete)
   - samplemind_wrapper.cpp (~300 lines)
   - audio_processor.cpp (~200 lines)
   - parameter_handler.cpp (~150 lines)
   - CMakeLists.txt (~100 lines)
   - Compiled plugin (.dll/.dylib/.so)

2. **Ableton Live Plugin** (Complete)
   - SampleMind.amxd (Max patcher)
   - python_backend.py (~400 lines)
   - communication.js (~200 lines)
   - midi_mapper.maxpat

3. **Plugin Installer** (Complete)
   - installer.py (~300 lines)
   - Installation scripts
   - Uninstaller

4. **Documentation** (Complete)
   - Plugin development guide
   - Installation instructions
   - User manual
   - API reference

---

## Next Steps

1. **Verify FL Studio SDK** - Download and verify FL Studio SDK is available
2. **Set up C++ environment** - Install compiler and build tools
3. **Create C++ wrapper** - Begin FL Studio plugin compilation
4. **Test incrementally** - Compile and test at each step
5. **Parallel Ableton development** - Max patcher design while C++ compiles

---

**Status**: Ready to begin Phase 13.2.1 (FL Studio Plugin)
**Estimated Completion**: 10-15 days total
**Quality Target**: Production-ready for beta testing
**Next Review**: Daily progress updates on compilation and testing

---

Generated: February 3, 2026
Confidence: High
Status: Planning Phase Complete → Ready for Implementation
