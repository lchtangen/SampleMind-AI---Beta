# 🎨 SampleMind AI - Design Inspiration Analysis

## Dribbble LEARNme Education Platform + Wavesurfer.js Integration

**Created:** October 7, 2025
**Source:** [LEARNme Education Website](https://dribbble.com/shots/22092052-LEARNme-Education-Website-Web-Design-for-Learning-Platform)
**Technology:** React 19+, wavesurfer.js 7+, Framer Motion 12.23+, TypeScript 5.9+
**Design System:** SampleMind Glassmorphism + Neon Cyberpunk Aesthetic

---

## 📊 Executive Summary

This document analyzes the LEARNme education platform design and adapts its UI/UX patterns to SampleMind AI's music production interface. The goal is to integrate **wavesurfer.js** for professional audio waveform visualization while maintaining our cyberpunk aesthetic and enhancing user experience with modern interaction patterns.

### Key Takeaways from LEARNme Design

1. **Clean, Modern Layout** - Spacious cards with clear hierarchy
2. **Gradient Accents** - Strategic use of gradients for CTAs and highlights
3. **Card-Based Architecture** - Modular content sections with hover states
4. **Interactive Elements** - Smooth transitions and micro-interactions
5. **Visual Hierarchy** - Clear separation between primary and secondary content
6. **Accessible Design** - High contrast, readable typography, clear affordances

### Integration with SampleMind AI

- ✅ **Existing:** Glassmorphic cards, neon gradients, waveform visualizers
- 🚀 **New:** wavesurfer.js integration for professional audio playback
- 🎯 **Enhanced:** Card-based sample library, interactive waveforms, AI analysis panels

---

## 🎵 Wavesurfer.js Integration Plan

### 1. Install wavesurfer.js

```bash
npm install wavesurfer.js@7.8.13
npm install --save-dev @types/wavesurfer.js
```

### 2. Core Implementation Strategy

**Component Architecture:**

```
/src/components/audio/
├── WaveformPlayer/          # Main wavesurfer.js player component
│   ├── WaveformPlayer.tsx   # Core player logic
│   ├── WaveformControls.tsx # Play/pause, seek, volume controls
│   ├── WaveformTimeline.tsx # Timeline with time markers
│   └── types.ts             # TypeScript interfaces
├── Spectrogram/             # FFT visualization
│   ├── Spectrogram.tsx      # Real-time frequency display
│   └── useAudioAnalyser.ts  # Web Audio API hook
├── BeatGrid/                # BPM-based beat markers
│   └── BeatGrid.tsx         # Visual beat grid overlay
└── AIRegions/               # AI-detected structure segments
    └── AIRegions.tsx        # Song structure visualization
```

---

## 🎨 Design Pattern Adaptations

### Pattern 1: Card-Based Sample Library (from LEARNme)

**LEARNme Pattern:**

- Clean white cards with subtle shadows
- Hover effects with scale transformation
- Clear typography hierarchy
- Icon + text combinations

**SampleMind Adaptation:**

```tsx
// GlassmorphicSampleCard.tsx
export interface SampleCardProps {
  sampleId: string;
  filename: string;
  duration: number;
  bpm: number;
  key: string;
  waveformUrl: string;
  thumbnailUrl?: string;
  tags: string[];
  onPlay: (id: string) => void;
  onAnalyze: (id: string) => void;
}

export function GlassmorphicSampleCard({
  sampleId,
  filename,
  duration,
  bpm,
  key,
  waveformUrl,
  tags,
  onPlay,
  onAnalyze,
}: SampleCardProps) {
  return (
    <motion.div
      className="glass-card rounded-xl p-6 cursor-pointer group"
      whileHover={{
        scale: 1.02,
        boxShadow: "0 0 40px rgba(139, 92, 246, 0.4)",
      }}
      transition={{ duration: 0.3 }}
    >
      {/* Mini Waveform Preview */}
      <div className="h-20 mb-4 bg-black/30 rounded-lg overflow-hidden">
        <MiniWaveform url={waveformUrl} height={80} />
      </div>

      {/* Sample Info */}
      <div className="space-y-3">
        <h3 className="font-heading text-lg font-semibold text-text-primary truncate">
          {filename}
        </h3>

        <div className="flex items-center gap-4 text-sm text-text-secondary">
          <span className="font-mono">{formatDuration(duration)}</span>
          <span className="font-mono text-cyan-400">{bpm} BPM</span>
          <span className="font-mono text-purple-400">{key}</span>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 text-xs font-semibold bg-purple-500/20
                         text-purple-300 rounded-full border border-purple-500/30"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-3 border-t border-white/10">
          <button
            onClick={() => onPlay(sampleId)}
            className="flex-1 bg-gradient-purple rounded-lg py-2 px-4
                       font-semibold text-sm shadow-glow-purple
                       hover:shadow-glow-cyan transition-all"
          >
            ▶ Play
          </button>
          <button
            onClick={() => onAnalyze(sampleId)}
            className="flex-1 bg-white/10 rounded-lg py-2 px-4
                       font-semibold text-sm border border-white/20
                       hover:bg-white/15 hover:border-purple-400/40 transition-all"
          >
            🧠 Analyze
          </button>
        </div>
      </div>
    </motion.div>
  );
}
```

---

### Pattern 2: Hero Section with Interactive Waveform

**LEARNme Pattern:**

- Large hero area with engaging visuals
- Clear call-to-action
- Animated elements on load

**SampleMind Adaptation:**

```tsx
// AudioHeroSection.tsx
export function AudioHeroSection() {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  return (
    <section className="relative min-h-[500px] glass-card rounded-2xl p-8">
      {/* Background Gradient */}
      <div
        className="absolute inset-0 bg-gradient-to-br from-purple-500/10
                      via-transparent to-cyan-500/10 rounded-2xl"
      />

      {/* Content */}
      <div className="relative z-10 space-y-6">
        <motion.h1
          className="font-heading text-5xl font-bold bg-gradient-to-r
                     from-purple-400 via-pink-400 to-cyan-400
                     bg-clip-text text-transparent"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          AI-Powered Music Production
        </motion.h1>

        <motion.p
          className="text-xl text-text-secondary max-w-2xl"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Upload, analyze, and transform your audio with cutting-edge AI
        </motion.p>

        {/* Main Waveform Player */}
        {audioUrl ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <WaveformPlayer
              audioUrl={audioUrl}
              height={200}
              waveColor="#8B5CF6"
              progressColor="#06B6D4"
              cursorColor="#EC4899"
            />
          </motion.div>
        ) : (
          <FileDropzone
            onFileUpload={(file) => {
              const url = URL.createObjectURL(file);
              setAudioUrl(url);
            }}
          />
        )}
      </div>
    </section>
  );
}
```

---

### Pattern 3: Feature Grid (from LEARNme)

**LEARNme Pattern:**

- 3-column grid of feature cards
- Icon + title + description
- Consistent spacing and alignment

**SampleMind Adaptation:**

```tsx
// FeatureGrid.tsx
const features = [
  {
    icon: "🎵",
    title: "Waveform Analysis",
    description: "Real-time audio visualization with wavesurfer.js",
    gradient: "from-purple-500 to-purple-600",
  },
  {
    icon: "🧠",
    title: "AI Classification",
    description: "Genre, BPM, key detection with Gemini & Claude",
    gradient: "from-cyan-500 to-cyan-600",
  },
  {
    icon: "📊",
    title: "Structure Detection",
    description: "Automatic song structure analysis (Intro, Drop, etc.)",
    gradient: "from-pink-500 to-pink-600",
  },
];

export function FeatureGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {features.map((feature, index) => (
        <motion.div
          key={feature.title}
          className="glass-card rounded-xl p-6 hover:shadow-glow-purple
                     transition-all duration-300"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
        >
          <div
            className={`w-16 h-16 rounded-full bg-gradient-to-br ${feature.gradient}
                          flex items-center justify-center text-3xl mb-4
                          shadow-[0_0_30px_rgba(139,92,246,0.4)]`}
          >
            {feature.icon}
          </div>

          <h3 className="font-heading text-xl font-semibold text-text-primary mb-2">
            {feature.title}
          </h3>

          <p className="text-text-secondary">{feature.description}</p>
        </motion.div>
      ))}
    </div>
  );
}
```

---

## 🎛️ Wavesurfer.js Component Implementation

### Core WaveformPlayer Component

```tsx
// /src/components/audio/WaveformPlayer/WaveformPlayer.tsx
import React, { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import { motion } from "framer-motion";
import { PlayIcon, PauseIcon, SkipForward, SkipBack } from "lucide-react";

export interface WaveformPlayerProps {
  audioUrl: string;
  title?: string;
  height?: number;
  waveColor?: string;
  progressColor?: string;
  cursorColor?: string;
  onReady?: (wavesurfer: WaveSurfer) => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
  onTimeUpdate?: (currentTime: number) => void;
}

export function WaveformPlayer({
  audioUrl,
  title,
  height = 150,
  waveColor = "#8B5CF6",
  progressColor = "#06B6D4",
  cursorColor = "#EC4899",
  onReady,
  onPlay,
  onPause,
  onFinish,
  onTimeUpdate,
}: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);

  // Initialize WaveSurfer
  useEffect(() => {
    if (!containerRef.current) return;

    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      height,
      waveColor,
      progressColor,
      cursorColor,
      cursorWidth: 2,
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      responsive: true,
      normalize: true,
      backend: "WebAudio",
      hideScrollbar: true,
    });

    // Load audio
    wavesurfer.load(audioUrl);

    // Event listeners
    wavesurfer.on("ready", () => {
      setIsLoading(false);
      setDuration(wavesurfer.getDuration());
      wavesurfer.setVolume(volume);
      onReady?.(wavesurfer);
    });

    wavesurfer.on("play", () => {
      setIsPlaying(true);
      onPlay?.();
    });

    wavesurfer.on("pause", () => {
      setIsPlaying(false);
      onPause?.();
    });

    wavesurfer.on("finish", () => {
      setIsPlaying(false);
      onFinish?.();
    });

    wavesurfer.on("audioprocess", (time) => {
      setCurrentTime(time);
      onTimeUpdate?.(time);
    });

    wavesurferRef.current = wavesurfer;

    return () => {
      wavesurfer.destroy();
    };
  }, [audioUrl, height, waveColor, progressColor, cursorColor]);

  // Volume control
  useEffect(() => {
    wavesurferRef.current?.setVolume(volume);
  }, [volume]);

  const togglePlayPause = () => {
    wavesurferRef.current?.playPause();
  };

  const skip = (seconds: number) => {
    if (!wavesurferRef.current) return;
    const newTime = currentTime + seconds;
    wavesurferRef.current.seekTo(newTime / duration);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <motion.div
      className="glass-card rounded-xl p-6 space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Title & Time */}
      {title && (
        <div className="flex items-center justify-between">
          <h3 className="font-heading text-xl font-semibold text-text-primary">
            {title}
          </h3>
          <span className="text-sm font-mono text-cyan-400">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>
      )}

      {/* Waveform Container */}
      <div className="relative">
        {isLoading && (
          <div
            className="absolute inset-0 flex items-center justify-center
                          bg-black/30 rounded-lg z-10"
          >
            <div
              className="animate-spin rounded-full h-8 w-8 border-t-2
                            border-b-2 border-purple-500"
            />
          </div>
        )}

        <div
          ref={containerRef}
          className="bg-black/30 rounded-lg border border-white/10 overflow-hidden"
        />
      </div>

      {/* Playback Controls */}
      <div className="flex items-center gap-4">
        {/* Skip Back */}
        <button
          onClick={() => skip(-10)}
          className="p-2 rounded-lg bg-white/10 hover:bg-white/15
                     transition-all text-text-primary"
          aria-label="Skip back 10 seconds"
        >
          <SkipBack size={20} />
        </button>

        {/* Play/Pause */}
        <button
          onClick={togglePlayPause}
          disabled={isLoading}
          className="p-4 rounded-full bg-gradient-purple shadow-glow-purple
                     hover:shadow-glow-cyan hover:scale-110 active:scale-95
                     transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? <PauseIcon size={24} /> : <PlayIcon size={24} />}
        </button>

        {/* Skip Forward */}
        <button
          onClick={() => skip(10)}
          className="p-2 rounded-lg bg-white/10 hover:bg-white/15
                     transition-all text-text-primary"
          aria-label="Skip forward 10 seconds"
        >
          <SkipForward size={20} />
        </button>

        {/* Volume Control */}
        <div className="flex-1 flex items-center gap-3 ml-4">
          <span className="text-xs font-semibold text-text-secondary uppercase">
            Volume
          </span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            className="flex-1 h-2 bg-white/10 rounded-full appearance-none
                       cursor-pointer [&::-webkit-slider-thumb]:appearance-none
                       [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                       [&::-webkit-slider-thumb]:bg-cyan-400
                       [&::-webkit-slider-thumb]:rounded-full
                       [&::-webkit-slider-thumb]:shadow-glow-cyan"
            aria-label="Volume control"
          />
          <span className="text-sm font-mono font-bold text-cyan-400 w-12 text-right">
            {Math.round(volume * 100)}%
          </span>
        </div>
      </div>
    </motion.div>
  );
}
```

---

## 📐 Layout Integration

### Dashboard Layout (3-Column Grid)

```tsx
// /src/pages/Dashboard.tsx
export function Dashboard() {
  const [selectedSample, setSelectedSample] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      {/* Hero Section */}
      <AudioHeroSection />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-8">
        {/* Left Sidebar - Sample Library */}
        <div className="lg:col-span-3 space-y-4">
          <h2 className="font-heading text-2xl font-bold text-text-primary">
            Sample Library
          </h2>
          <div className="space-y-3">
            {samples.map((sample) => (
              <GlassmorphicSampleCard
                key={sample.id}
                {...sample}
                onPlay={(id) => setSelectedSample(id)}
                onAnalyze={(id) => console.log("Analyze", id)}
              />
            ))}
          </div>
        </div>

        {/* Center - Main Visualizer */}
        <div className="lg:col-span-6 space-y-4">
          {selectedSample && (
            <>
              <WaveformPlayer
                audioUrl={`/samples/${selectedSample}.wav`}
                title={selectedSample}
                height={180}
              />

              <Spectrogram
                audioContext={audioContext}
                analyserNode={analyser}
                height={200}
              />

              <AIRegions regions={detectedRegions} duration={180} />

              <BeatGrid bpm={128} duration={180} />
            </>
          )}
        </div>

        {/* Right Sidebar - AI Analysis */}
        <div className="lg:col-span-3">
          <AIAnalysisPanel
            genres={[
              { genre: "Electronic", confidence: 0.87 },
              { genre: "House", confidence: 0.65 },
            ]}
            features={{
              bpm: 128.4,
              bpmConfidence: 0.2,
              key: "C Minor",
              keyConfidence: 0.97,
              energy: 82,
              danceability: 75,
              valence: 62,
            }}
            structure={[
              { label: "Intro", startTime: 0, endTime: 30 },
              { label: "Drop", startTime: 30, endTime: 75 },
            ]}
          />
        </div>
      </div>

      {/* Feature Grid */}
      <div className="mt-12">
        <FeatureGrid />
      </div>
    </div>
  );
}
```

---

## 🎯 Implementation Checklist

### Phase 1: Setup & Foundation (Week 1)

- [x] Analyze design inspiration from Dribbble
- [ ] Install wavesurfer.js and types
- [ ] Create base WaveformPlayer component
- [ ] Implement loading states and error handling
- [ ] Add TypeScript interfaces for all audio components

### Phase 2: Core Components (Week 2)

- [ ] Build GlassmorphicSampleCard
- [ ] Implement AudioHeroSection
- [ ] Create FeatureGrid layout
- [ ] Add Spectrogram visualization
- [ ] Implement BeatGrid overlay
- [ ] Build AIRegions component

### Phase 3: Integration (Week 3)

- [ ] Connect WaveformPlayer to backend API
- [ ] Integrate AI analysis data
- [ ] Add real-time audio analysis with Web Audio API
- [ ] Implement waveform caching for performance
- [ ] Add keyboard shortcuts (Space = play/pause, arrows = seek)

### Phase 4: Polish & Optimization (Week 4)

- [ ] Add animations with Framer Motion
- [ ] Implement responsive breakpoints
- [ ] Add accessibility features (ARIA labels, keyboard nav)
- [ ] Optimize waveform rendering performance
- [ ] Write unit tests with Vitest
- [ ] Write E2E tests with Playwright

---

## 🔗 Design Resources

### Color Palette (from SampleMind Design System)

- **Primary Purple:** `#8B5CF6`
- **Accent Cyan:** `#06B6D4`
- **Accent Pink:** `#EC4899`
- **Background:** `#0A0A0F`
- **Glass Surface:** `rgba(26, 26, 36, 0.5)`

### Typography

- **Heading:** Rajdhani (semibold 600, bold 700)
- **Body:** Inter (regular 400, medium 500)
- **Mono:** JetBrains Mono (for BPM, time, values)

### Spacing (8pt Grid)

- Small: `16px` (p-4)
- Medium: `24px` (p-6)
- Large: `32px` (p-8)

### Shadows (Neon Glow)

```css
.shadow-glow-purple {
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
}

.shadow-glow-cyan {
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.6);
}

.shadow-glow-pink {
  box-shadow: 0 0 20px rgba(236, 72, 153, 0.6);
}
```

---

## 📚 References

1. **Dribbble Design:** [LEARNme Education Platform](https://dribbble.com/shots/22092052-LEARNme-Education-Website-Web-Design-for-Learning-Platform)
2. **wavesurfer.js Docs:** https://wavesurfer.xyz/
3. **SampleMind Design System:** `/web-app/src/design-system/tokens.ts`
4. **Component Guide:** `/web-app/SAMPLEMIND_COMPONENT_GUIDE.md`
5. **Design Research:** `/web-app/SAMPLEMIND_DESIGN_RESEARCH_REPORT.md`

---

**Document Version:** 1.0.0
**Status:** Design Analysis Complete
**Next Steps:** Begin wavesurfer.js integration (Phase 1)
