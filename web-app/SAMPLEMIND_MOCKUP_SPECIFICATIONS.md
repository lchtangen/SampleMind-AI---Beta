# 🎨 SAMPLEMIND AI - High-Fidelity Mockup Specifications

**Project:** AI Music Production Tool Web Interface
**Design Theme:** Glassmorphism + Neon Cyberpunk
**Resolution:** 1920x1080 (Desktop), Responsive down to 1366x768
**Created:** October 7, 2025

---

## 🖼️ Mockup 1: Main Dashboard View

### Layout Specifications

**Dimensions:** 1920px × 1080px
**Grid System:** 24-column grid (80px per column)
**Gutter:** 16px between columns

### Component Breakdown

#### 1. **Top Navigation Bar** (1920px × 60px)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  🎵 SAMPLEMIND AI    [Dashboard] [Library] [Projects]    [@user] [⚙️] [?] [↗] │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Styling:**

```css
.top-navbar {
  background: linear-gradient(
    to right,
    rgba(10, 10, 15, 0.95),
    rgba(26, 26, 46, 0.9)
  );
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(139, 92, 246, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 40px rgba(139, 92, 246, 0.15);
  height: 60px;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-family: "Orbitron", sans-serif;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #8b5cf6, #ec4899, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
}

.nav-links a {
  color: #a0a0b0;
  font-size: 14px;
  font-weight: 500;
  margin: 0 16px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-links a:hover {
  color: #ffffff;
  background: rgba(139, 92, 246, 0.1);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.nav-links a.active {
  color: #ffffff;
  background: rgba(139, 92, 246, 0.2);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
}
```

---

#### 2. **Left Sidebar: Sample Library** (400px × 1020px)

```
┌────────────────────────────────────┐
│  📁 Sample Library                 │
│  ┌──────────────────────────────┐ │
│  │ 🔍 Search samples...         │ │
│  └──────────────────────────────┘ │
│                                    │
│  Filters ▼                         │
│  ┌──────────────────────────────┐ │
│  │ Genre:  ☑ Electronic         │ │
│  │         ☑ House              │ │
│  │         □ Techno             │ │
│  │                              │ │
│  │ BPM:    [120] ──●── [130]   │ │
│  │ Key:    [C Minor ▼]          │ │
│  │                              │ │
│  │ Type:   □ Kicks              │ │
│  │         ☑ Basslines          │ │
│  │         □ Pads               │ │
│  └──────────────────────────────┘ │
│                                    │
│  Results (23 samples)              │
│  ┌────────┬────────┬────────┐     │
│  │ 🔊 bass│ 🔊 bass│ 🔊 bass│     │
│  │ -1.wav │ -2.wav │ -3.wav │     │
│  │ 128 BPM│ 125 BPM│ 130 BPM│     │
│  │ C Minor│ A Minor│ D Minor│     │
│  │ ▁▂▃▅█▅▃│ ▁▃█▃▁  │ ▁▂▃█▃▂▁│     │
│  └────────┴────────┴────────┘     │
│  ┌────────┬────────┬────────┐     │
│  │ 🔊 kick│ 🔊 snar│ 🔊 hi-h│     │
│  │ -hard  │ e-tight│ at-cris│     │
│  └────────┴────────┴────────┘     │
│                                    │
│  [Load More]                       │
└────────────────────────────────────┘
```

**Sample Card Styling:**

```css
.sample-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.08),
    rgba(255, 255, 255, 0.03)
  );
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 12px;
  width: 120px;
  height: 160px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sample-card:hover {
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.15),
    rgba(139, 92, 246, 0.05)
  );
  border-color: rgba(139, 92, 246, 0.4);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 40px rgba(139, 92, 246, 0.3);
  transform: translateY(-4px);
}

.sample-card-waveform {
  width: 100%;
  height: 40px;
  margin: 8px 0;
  background: linear-gradient(
    to right,
    rgba(139, 92, 246, 0.3),
    rgba(236, 72, 153, 0.3)
  );
  border-radius: 4px;
}

.sample-card-metadata {
  font-size: 11px;
  color: #06b6d4;
  font-weight: 600;
  line-height: 1.4;
  margin-top: 4px;
}

.sample-card-filename {
  font-size: 12px;
  color: #ffffff;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

---

#### 3. **Center: Main Visualizer** (1200px × 1020px)

```
┌──────────────────────────────────────────────────────────────┐
│  sample-bassline-128.wav - C Minor - 128 BPM     [⚙️] [↗]   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ WAVEFORM                                  [zoom ▼]     │ │
│  │ ▁▂▃▅▇█▇▅▃▂▁ ▁▂▃▅▇█▇▅▃▂▁ ▁▂▃▅▇█▇▅▃▂▁ ▁▂▃▅▇█▇▅▃▂▁       │ │  150px
│  │                 ▲ playhead (cyan glow)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ SPECTROGRAM (Real-time FFT)                           │ │
│  │ ████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░   │ │
│  │ ████████████████████████████████░░░░░░░░░░░░░░░░░░░   │ │  200px
│  │ ████████████████████████████████████░░░░░░░░░░░░░░░   │ │
│  │ ████████████████████████████████████████░░░░░░░░░░░   │ │
│  │ (Pink→Cyan gradient, GPU-accelerated)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ AI DETECTED REGIONS                                    │ │
│  │ ┌───────┐ ┌────────────────┐ ┌──────┐ ┌────────────┐ │ │  80px
│  │ │ Intro │ │   Build-up     │ │ Drop │ │   Outro    │ │ │
│  │ └───────┘ └────────────────┘ └──────┘ └────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ BEAT GRID (Auto-detected)                              │ │
│  │ │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │ │ │  60px
│  │ 1  2  3  4  1  2  3  4  1  2  3  4  1  2  3  4  1  2 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  [◄◄ -10s] [  ▶ PLAY  ] [+10s ►►]   2:34 / 4:18      │ │  80px
│  │                                                         │ │
│  │  ═══════════════●═══════════════════  Volume: 80%     │ │
│  │  Loop: [ ] Region  Snap: [✓] Beat Grid               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Waveform Styling:**

```css
.waveform-container {
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.05),
    rgba(6, 182, 212, 0.05)
  );
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 16px;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3), 0 8px 32px rgba(0, 0, 0, 0.4);
}

.waveform-title {
  font-family: "Orbitron", sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: #8b5cf6;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
}

/* wavesurfer.js custom styling */
wave {
  cursor: pointer;
}

wave canvas {
  border-radius: 4px;
}

/* Spectrogram styling */
.spectrogram-canvas {
  width: 100%;
  height: 200px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  image-rendering: pixelated; /* Sharp pixels for FFT */
}

/* AI Region segments */
.ai-region {
  background: linear-gradient(
    to bottom,
    rgba(236, 72, 153, 0.3),
    rgba(236, 72, 153, 0.1)
  );
  border: 2px solid rgba(236, 72, 153, 0.6);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ai-region:hover {
  background: linear-gradient(
    to bottom,
    rgba(236, 72, 153, 0.5),
    rgba(236, 72, 153, 0.2)
  );
  box-shadow: 0 0 20px rgba(236, 72, 153, 0.6);
  transform: scale(1.05);
}

/* Beat grid markers */
.beat-marker {
  width: 2px;
  height: 40px;
  background: rgba(6, 182, 212, 0.6);
  box-shadow: 0 0 8px rgba(6, 182, 212, 0.8);
}

.beat-marker.downbeat {
  height: 60px;
  background: rgba(6, 182, 212, 0.9);
  box-shadow: 0 0 12px rgba(6, 182, 212, 1);
}
```

**Playback Controls Styling:**

```css
.playback-controls {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.06),
    rgba(255, 255, 255, 0.02)
  );
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.play-button {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.5), 0 0 40px rgba(139, 92, 246, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.play-button:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 32px rgba(139, 92, 246, 0.7), 0 0 60px rgba(139, 92, 246, 0.5);
}

.play-button:active {
  transform: scale(0.95);
}

.timeline-slider {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  cursor: pointer;
  position: relative;
}

.timeline-progress {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #06b6d4);
  border-radius: 4px;
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.6);
}

.timeline-thumb {
  width: 16px;
  height: 16px;
  background: #ffffff;
  border-radius: 50%;
  position: absolute;
  top: -4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 0 12px rgba(6, 182, 212, 0.8);
  cursor: grab;
}

.timeline-thumb:active {
  cursor: grabbing;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5), 0 0 20px rgba(6, 182, 212, 1);
}
```

---

#### 4. **Right Sidebar: AI Analysis Panel** (320px × 1020px)

```
┌────────────────────────────────┐
│  🧠 AI Analysis                │
├────────────────────────────────┤
│                                │
│  Genre Classification          │
│  ┌──────────────────────────┐ │
│  │ Electronic   ████████░░  │ │
│  │              87%         │ │
│  │                          │ │
│  │ House        ██████░░░░  │ │
│  │              65%         │ │
│  │                          │ │
│  │ Techno       ████░░░░░░  │ │
│  │              43%         │ │
│  │                          │ │
│  │ Drum & Bass  ██░░░░░░░░  │ │
│  │              23%         │ │
│  └──────────────────────────┘ │
│                                │
│  Audio Features                │
│  ┌──────────────────────────┐ │
│  │  BPM                     │ │
│  │  128.4 ±0.2              │ │
│  │  ████████████████░░░░    │ │
│  │                          │ │
│  │  Key                     │ │
│  │  C Minor (97%)           │ │
│  │                          │ │
│  │  Energy                  │ │
│  │  82/100                  │ │
│  │  ████████░░              │ │
│  │                          │ │
│  │  Danceability            │ │
│  │  75/100                  │ │
│  │  ███████░░░              │ │
│  └──────────────────────────┘ │
│                                │
│  Structure Detection           │
│  ┌──────────────────────────┐ │
│  │ ┌────────────────────┐   │ │
│  │ │ 0:00 - 0:30 Intro  │   │ │
│  │ └────────────────────┘   │ │
│  │ ┌────────────────────┐   │ │
│  │ │ 0:30 - 1:15 Build  │   │ │
│  │ └────────────────────┘   │ │
│  │ ┌────────────────────┐   │ │
│  │ │ 1:15 - 2:30 Drop   │   │ │
│  │ └────────────────────┘   │ │
│  │ ┌────────────────────┐   │ │
│  │ │ 2:30 - 3:00 Break  │   │ │
│  │ └────────────────────┘   │ │
│  │ ┌────────────────────┐   │ │
│  │ │ 3:00 - 4:18 Outro  │   │ │
│  │ └────────────────────┘   │ │
│  └──────────────────────────┘ │
│                                │
│  ┌──────────────────────────┐ │
│  │  [📊 Export Metadata]    │ │
│  │  [🔄 Retrain Model]      │ │
│  │  [⚙️ Advanced Settings]  │ │
│  └──────────────────────────┘ │
│                                │
└────────────────────────────────┘
```

**AI Panel Styling:**

```css
.ai-panel {
  background: linear-gradient(
    180deg,
    rgba(10, 10, 15, 0.95),
    rgba(26, 26, 46, 0.9)
  );
  backdrop-filter: blur(16px);
  border-left: 1px solid rgba(139, 92, 246, 0.3);
  padding: 24px;
  overflow-y: auto;
}

.ai-section-title {
  font-family: "Orbitron", sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: #8b5cf6;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-section-title::before {
  content: "";
  width: 4px;
  height: 16px;
  background: linear-gradient(to bottom, #8b5cf6, #ec4899);
  border-radius: 2px;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.6);
}

/* Genre bars */
.genre-bar-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.genre-name {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 6px;
}

.genre-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.genre-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #06b6d4);
  border-radius: 4px;
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.6), inset 0 1px 2px rgba(255, 255, 255, 0.3);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.genre-confidence {
  font-size: 12px;
  font-weight: 700;
  color: #06b6d4;
  margin-top: 4px;
  text-align: right;
}

/* Audio feature cards */
.feature-card {
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.08),
    rgba(255, 255, 255, 0.03)
  );
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.feature-label {
  font-size: 11px;
  font-weight: 700;
  color: #a0a0b0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.feature-value {
  font-size: 24px;
  font-weight: 900;
  font-family: "JetBrains Mono", monospace;
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
}

/* Structure timeline */
.structure-segment {
  background: linear-gradient(
    to right,
    rgba(236, 72, 153, 0.2),
    rgba(236, 72, 153, 0.05)
  );
  border-left: 3px solid #ec4899;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.structure-segment:hover {
  background: linear-gradient(
    to right,
    rgba(236, 72, 153, 0.3),
    rgba(236, 72, 153, 0.1)
  );
  border-left-color: #f97316;
  box-shadow: 0 4px 16px rgba(236, 72, 153, 0.4);
  transform: translateX(4px);
}

.structure-time {
  font-size: 11px;
  font-family: "JetBrains Mono", monospace;
  color: #06b6d4;
  font-weight: 700;
}

.structure-label {
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  margin-left: 8px;
}
```

---

## 🖼️ Mockup 2: Sample Upload & Processing View

### Upload Modal (800px × 600px)

```
┌────────────────────────────────────────────────────────────┐
│  Upload Audio Sample                             [✕ Close] │
├────────────────────────────────────────────────────────────┤
│                                                            │
│              ┌────────────────────────────┐               │
│              │                            │               │
│              │      📁 Drop files here    │               │
│              │           or               │               │
│              │    [Browse Files]          │               │
│              │                            │               │
│              │  Supported: WAV, MP3, FLAC │               │
│              │  Max size: 100 MB          │               │
│              │                            │               │
│              └────────────────────────────┘               │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  🎵 bassline-128.wav                                 │ │
│  │  Size: 8.4 MB • Duration: 2:34 • Sample Rate: 44.1  │ │
│  │  ▁▂▃▅█▅▃▂▁ ▁▂▃▅█▅▃▂▁ ▁▂▃▅█▅▃▂▁                      │ │
│  │                                                      │ │
│  │  Processing:  ████████████████░░░░ 78%              │ │
│  │               ↳ Running AI classification...        │ │
│  │                                                      │ │
│  │  [✓] Waveform generated                             │ │
│  │  [✓] BPM detected (128.4 BPM)                       │ │
│  │  [⏳] Genre classification (78%)                     │ │
│  │  [  ] Key detection                                 │ │
│  │  [  ] Structure analysis                            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  [Cancel] [Skip AI] [Continue →]                          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Upload Modal Styling:**

```css
.upload-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  background: linear-gradient(
    135deg,
    rgba(26, 26, 46, 0.98),
    rgba(10, 10, 15, 0.95)
  );
  backdrop-filter: blur(32px);
  border: 2px solid rgba(139, 92, 246, 0.4);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.8), 0 0 80px rgba(139, 92, 246, 0.3);
  animation: fadeInScale 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

.dropzone {
  border: 2px dashed rgba(139, 92, 246, 0.5);
  border-radius: 16px;
  padding: 64px;
  text-align: center;
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.05),
    rgba(6, 182, 212, 0.05)
  );
  cursor: pointer;
  transition: all 0.3s ease;
}

.dropzone:hover {
  border-color: rgba(139, 92, 246, 0.8);
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.1),
    rgba(6, 182, 212, 0.1)
  );
  box-shadow: inset 0 0 40px rgba(139, 92, 246, 0.2);
}

.dropzone.active {
  border-color: rgba(6, 182, 212, 1);
  background: linear-gradient(
    135deg,
    rgba(6, 182, 212, 0.2),
    rgba(139, 92, 246, 0.1)
  );
  box-shadow: inset 0 0 60px rgba(6, 182, 212, 0.3), 0 0 40px rgba(6, 182, 212, 0.5);
}

.processing-progress {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 16px 0;
}

.processing-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #06b6d4, #ec4899);
  background-size: 200% 100%;
  border-radius: 4px;
  animation: progressGradient 2s ease infinite;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
}

@keyframes progressGradient {
  0% {
    background-position: 0% 0%;
  }
  50% {
    background-position: 100% 0%;
  }
  100% {
    background-position: 0% 0%;
  }
}

.processing-step {
  font-size: 12px;
  color: #a0a0b0;
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.processing-step.complete {
  color: #06b6d4;
}

.processing-step.active {
  color: #8b5cf6;
  animation: pulse 1.5s ease infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.processing-step-icon {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid currentColor;
  display: flex;
  align-items: center;
  justify-content: center;
}

.processing-step-icon.complete::after {
  content: "✓";
  font-size: 10px;
  font-weight: 900;
}
```

---

## 🎨 Color Palette Reference

### Primary Colors

```
Purple:  #8B5CF6 (Primary UI, buttons, highlights)
Cyan:    #06B6D4 (Playback cursor, active waveform)
Pink:    #EC4899 (AI highlights, beat markers)
Yellow:  #F59E0B (Warnings, transient detection)
```

### Background Colors

```
Primary:   #0A0A0F (Main background, near-black)
Secondary: #1A1A2E (Card backgrounds)
Tertiary:  #2A2A3E (Elevated elements)
```

### Text Colors

```
Primary:   #FFFFFF (Main text)
Secondary: #A0A0B0 (Metadata, labels)
Muted:     #606070 (Disabled text)
```

### Glassmorphism Layers

```
Light:  rgba(255, 255, 255, 0.05)
Medium: rgba(255, 255, 255, 0.10)
Heavy:  rgba(255, 255, 255, 0.15)
```

### Neon Glows (Box Shadows)

```
Purple: 0 0 20px rgba(139, 92, 246, 0.5)
Cyan:   0 0 20px rgba(6, 182, 212, 0.5)
Pink:   0 0 20px rgba(236, 72, 153, 0.5)
```

---

## 📐 Component Dimensions Reference

### Navigation

- Top navbar: 60px height
- Logo: 24px font size
- Nav links: 14px font size

### Sidebars

- Left (Library): 400px width
- Right (AI Panel): 320px width

### Main Visualizer

- Width: 1200px
- Waveform track: 150px height
- Spectrogram: 200px height
- AI regions: 80px height
- Beat grid: 60px height
- Controls: 80px height

### Cards & Components

- Border radius: 12-16px (glassmorphic cards)
- Padding: 16-24px (standard cards)
- Border width: 1px (standard), 2px (focused)
- Blur: 16px (standard glass), 24px (heavy glass)

### Typography

- Headers: 24-48px (Orbitron, bold)
- Body: 14-16px (Inter, regular)
- Metadata: 11-12px (Inter, semibold)
- Code/data: 11-14px (JetBrains Mono, monospace)

---

**Document Version:** 1.0.0
**Status:** High-Fidelity Mockup Specifications Complete
**Next:** Implementation with React + TypeScript + wavesurfer.js
