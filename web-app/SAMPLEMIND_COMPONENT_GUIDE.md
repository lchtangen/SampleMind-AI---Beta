# 🧩 SAMPLEMIND AI - Component Implementation Guide

**Project:** AI Music Production Tool - React Component Library
**Tech Stack:** React 19+, TypeScript 5.9+, Tailwind CSS 4.1+, wavesurfer.js 7.x
**Design System:** Glassmorphism + Neon Cyberpunk
**Created:** October 7, 2025

---

## 📁 Component Architecture

```
/src/components/
├── ui/                       # Primitive UI components
│   ├── Button.tsx
│   ├── Card.tsx
│   ├── Input.tsx
│   ├── Slider.tsx
│   ├── Progress.tsx
│   └── Badge.tsx
├── layout/                   # Layout components
│   ├── Navbar.tsx
│   ├── Sidebar.tsx
│   ├── Container.tsx
│   └── Grid.tsx
├── audio/                    # Audio-specific components
│   ├── WaveformPlayer.tsx
│   ├── Spectrogram.tsx
│   ├── BeatGrid.tsx
│   ├── AIRegions.tsx
│   └── AudioControls.tsx
└── features/                 # Feature components
    ├── SampleLibrary.tsx
    ├── AIAnalysisPanel.tsx
    ├── UploadModal.tsx
    └── Dashboard.tsx
```

---

## 🎨 1. UI Components

### Button.tsx

```typescript
import React from "react";
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  // Base styles - always applied
  "inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-300 ease-out focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary: [
          "bg-gradient-to-r from-purple-500 to-purple-600",
          "hover:from-purple-600 hover:to-purple-700",
          "shadow-[0_8px_24px_rgba(139,92,246,0.5)]",
          "hover:shadow-[0_12px_32px_rgba(139,92,246,0.7)]",
          "hover:scale-105 active:scale-95",
          "text-white",
        ],
        secondary: [
          "bg-white/10 backdrop-blur-md",
          "border border-white/20",
          "hover:bg-white/15 hover:border-purple-400/40",
          "hover:shadow-[0_0_20px_rgba(139,92,246,0.3)]",
          "text-white",
        ],
        ghost: [
          "bg-transparent",
          "hover:bg-white/10",
          "text-text-secondary",
          "hover:text-text-primary",
        ],
        neon: [
          "bg-gradient-to-r from-cyan-500 to-purple-500",
          "hover:from-cyan-400 hover:to-purple-400",
          "shadow-[0_0_20px_rgba(6,182,212,0.5)]",
          "hover:shadow-[0_0_40px_rgba(6,182,212,0.8)]",
          "hover:scale-110 active:scale-95",
          "text-white font-bold",
        ],
      },
      size: {
        sm: "px-3 py-1.5 text-sm",
        md: "px-6 py-3 text-base",
        lg: "px-8 py-4 text-lg",
        icon: "p-3 w-12 h-12",
      },
      glow: {
        true: "animate-pulse",
        false: "",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
      glow: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
}

export function Button({
  variant,
  size,
  glow,
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={buttonVariants({ variant, size, glow, className })}
      {...props}
    >
      {children}
    </button>
  );
}
```

**Usage Example:**

```tsx
<Button variant="primary" size="lg">
  Play Track
</Button>

<Button variant="neon" glow>
  🔥 Export
</Button>

<Button variant="ghost" size="icon">
  <SettingsIcon />
</Button>
```

---

### Card.tsx

```typescript
import React from "react";
import { cva, type VariantProps } from "class-variance-authority";

const cardVariants = cva(
  "backdrop-blur-md border transition-all duration-300",
  {
    variants: {
      variant: {
        glass: [
          "bg-white/5",
          "border-white/10",
          "hover:bg-white/8",
          "hover:border-purple-400/30",
        ],
        glassHeavy: [
          "bg-white/10",
          "border-white/15",
          "hover:bg-white/12",
          "hover:border-purple-400/40",
        ],
        neon: [
          "bg-gradient-to-br from-purple-500/10 to-cyan-500/10",
          "border-purple-400/40",
          "shadow-[0_0_40px_rgba(139,92,246,0.3)]",
          "hover:shadow-[0_0_60px_rgba(139,92,246,0.5)]",
        ],
      },
      rounded: {
        sm: "rounded-lg",
        md: "rounded-xl",
        lg: "rounded-2xl",
      },
      padding: {
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
      },
      clickable: {
        true: "cursor-pointer hover:scale-105",
        false: "",
      },
    },
    defaultVariants: {
      variant: "glass",
      rounded: "md",
      padding: "md",
      clickable: false,
    },
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  children: React.ReactNode;
  title?: string;
  icon?: React.ReactNode;
}

export function Card({
  variant,
  rounded,
  padding,
  clickable,
  className,
  children,
  title,
  icon,
  ...props
}: CardProps) {
  return (
    <div
      className={cardVariants({
        variant,
        rounded,
        padding,
        clickable,
        className,
      })}
      {...props}
    >
      {title && (
        <div className="flex items-center gap-3 mb-4 pb-3 border-b border-white/10">
          {icon && <div className="text-purple-400">{icon}</div>}
          <h3 className="font-heading text-lg font-semibold text-text-primary">
            {title}
          </h3>
        </div>
      )}
      {children}
    </div>
  );
}
```

**Usage Example:**

```tsx
<Card variant="glassHeavy" title="AI Analysis" icon={<BrainIcon />}>
  <p className="text-text-secondary">Content goes here</p>
</Card>

<Card variant="neon" clickable onClick={handleClick}>
  <h4>Special Feature</h4>
</Card>
```

---

### Slider.tsx (Custom Range Input)

```typescript
import React, { useState } from "react";

export interface SliderProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  label?: string;
  showValue?: boolean;
  variant?: "purple" | "cyan" | "gradient";
}

export function Slider({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  label,
  showValue = true,
  variant = "gradient",
}: SliderProps) {
  const [isDragging, setIsDragging] = useState(false);

  const percentage = ((value - min) / (max - min)) * 100;

  const gradientColors = {
    purple: "from-purple-500 to-purple-600",
    cyan: "from-cyan-500 to-cyan-600",
    gradient: "from-purple-500 via-pink-500 to-cyan-500",
  };

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-semibold text-text-secondary uppercase tracking-wide">
            {label}
          </label>
          {showValue && (
            <span className="text-sm font-mono font-bold text-cyan-400">
              {value}
            </span>
          )}
        </div>
      )}

      <div className="relative h-10 flex items-center">
        {/* Track */}
        <div className="absolute inset-0 h-2 bg-white/10 rounded-full" />

        {/* Filled track */}
        <div
          className={`absolute left-0 h-2 rounded-full bg-gradient-to-r ${gradientColors[variant]} shadow-[0_0_12px_rgba(139,92,246,0.6)] transition-all duration-200`}
          style={{ width: `${percentage}%` }}
        />

        {/* Thumb */}
        <div
          className={`absolute w-5 h-5 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.4),0_0_12px_rgba(6,182,212,0.8)] cursor-grab transition-transform ${
            isDragging ? "scale-125 cursor-grabbing" : "hover:scale-110"
          }`}
          style={{ left: `calc(${percentage}% - 10px)` }}
        />

        {/* Input overlay */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          onMouseDown={() => setIsDragging(true)}
          onMouseUp={() => setIsDragging(false)}
          onTouchStart={() => setIsDragging(true)}
          onTouchEnd={() => setIsDragging(false)}
          className="absolute inset-0 w-full opacity-0 cursor-pointer"
        />
      </div>
    </div>
  );
}
```

**Usage Example:**

```tsx
const [volume, setVolume] = useState(80);

<Slider
  value={volume}
  onChange={setVolume}
  min={0}
  max={100}
  step={1}
  label="Volume"
  variant="gradient"
/>;
```

---

## 🎵 2. Audio Components

### WaveformPlayer.tsx

```typescript
import React, { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { PlayIcon, PauseIcon } from "lucide-react";

export interface WaveformPlayerProps {
  audioUrl: string;
  title?: string;
  height?: number;
  waveColor?: string;
  progressColor?: string;
  cursorColor?: string;
  onReady?: (wavesurfer: WaveSurfer) => void;
}

export function WaveformPlayer({
  audioUrl,
  title,
  height = 150,
  waveColor = "#8B5CF6",
  progressColor = "#06B6D4",
  cursorColor = "#06B6D4",
  onReady,
}: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize WaveSurfer
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
    });

    // Load audio
    wavesurfer.load(audioUrl);

    // Event listeners
    wavesurfer.on("ready", () => {
      setDuration(wavesurfer.getDuration());
      onReady?.(wavesurfer);
    });

    wavesurfer.on("play", () => setIsPlaying(true));
    wavesurfer.on("pause", () => setIsPlaying(false));
    wavesurfer.on("audioprocess", (time) => setCurrentTime(time));

    wavesurferRef.current = wavesurfer;

    return () => {
      wavesurfer.destroy();
    };
  }, [audioUrl, height, waveColor, progressColor, cursorColor, onReady]);

  const togglePlayPause = () => {
    wavesurferRef.current?.playPause();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Card variant="glass" className="space-y-4">
      {/* Title */}
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

      {/* Waveform container */}
      <div
        ref={containerRef}
        className="bg-black/30 rounded-lg p-2 border border-white/10"
      />

      {/* Playback controls */}
      <div className="flex items-center gap-4">
        <Button
          variant="neon"
          size="icon"
          onClick={togglePlayPause}
          aria-label={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? <PauseIcon size={24} /> : <PlayIcon size={24} />}
        </Button>

        <div className="flex-1">
          <input
            type="range"
            min={0}
            max={duration}
            step={0.1}
            value={currentTime}
            onChange={(e) => {
              wavesurferRef.current?.seekTo(Number(e.target.value) / duration);
            }}
            className="w-full"
          />
        </div>

        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => wavesurferRef.current?.skip(-10)}
          >
            -10s
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => wavesurferRef.current?.skip(10)}
          >
            +10s
          </Button>
        </div>
      </div>
    </Card>
  );
}
```

**Usage Example:**

```tsx
<WaveformPlayer
  audioUrl="/samples/bassline-128.wav"
  title="bassline-128.wav"
  height={150}
  onReady={(ws) => console.log("Waveform ready", ws)}
/>
```

---

### Spectrogram.tsx (Real-time FFT Visualization)

```typescript
import React, { useEffect, useRef } from "react";
import { Card } from "@/components/ui/Card";

export interface SpectrogramProps {
  audioContext: AudioContext;
  analyserNode: AnalyserNode;
  width?: number;
  height?: number;
  fftSize?: number;
  smoothingTimeConstant?: number;
}

export function Spectrogram({
  audioContext,
  analyserNode,
  width = 1200,
  height = 200,
  fftSize = 2048,
  smoothingTimeConstant = 0.8,
}: SpectrogramProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Configure analyser
    analyserNode.fftSize = fftSize;
    analyserNode.smoothingTimeConstant = smoothingTimeConstant;

    const bufferLength = analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    // Create gradient (purple → pink → cyan)
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, "#06B6D4"); // Cyan (high freq)
    gradient.addColorStop(0.5, "#EC4899"); // Pink (mid freq)
    gradient.addColorStop(1, "#8B5CF6"); // Purple (low freq)

    const draw = () => {
      analyserNode.getByteFrequencyData(dataArray);

      // Shift existing pixels to the left
      const imageData = ctx.getImageData(1, 0, width - 1, height);
      ctx.putImageData(imageData, 0, 0);

      // Draw new column on the right
      const barWidth = height / bufferLength;

      for (let i = 0; i < bufferLength; i++) {
        const value = dataArray[i];
        const percent = value / 255;
        const y = height - i * barWidth;

        // Color intensity based on amplitude
        const alpha = Math.max(percent, 0.1);

        ctx.fillStyle = gradient;
        ctx.globalAlpha = alpha;
        ctx.fillRect(width - 1, y - barWidth, 1, barWidth);
      }

      ctx.globalAlpha = 1;

      animationFrameRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [
    audioContext,
    analyserNode,
    width,
    height,
    fftSize,
    smoothingTimeConstant,
  ]);

  return (
    <Card variant="glass">
      <div className="space-y-2">
        <h4 className="font-heading text-sm font-semibold text-purple-400 uppercase tracking-wide">
          Spectrogram (Real-time FFT)
        </h4>
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          className="w-full rounded-lg bg-black/30 border border-white/10"
          style={{ imageRendering: "pixelated" }}
        />
      </div>
    </Card>
  );
}
```

**Usage Example:**

```tsx
const audioContext = new AudioContext();
const analyser = audioContext.createAnalyser();

<Spectrogram
  audioContext={audioContext}
  analyserNode={analyser}
  width={1200}
  height={200}
  fftSize={2048}
/>;
```

---

### BeatGrid.tsx

```typescript
import React from "react";

export interface BeatGridProps {
  bpm: number;
  duration: number; // Total audio duration in seconds
  timeSignature?: [number, number]; // e.g., [4, 4]
  currentTime?: number;
  onBeatClick?: (beatIndex: number, timestamp: number) => void;
}

export function BeatGrid({
  bpm,
  duration,
  timeSignature = [4, 4],
  currentTime = 0,
  onBeatClick,
}: BeatGridProps) {
  const [beatsPerBar, noteValue] = timeSignature;
  const secondsPerBeat = 60 / bpm;
  const totalBeats = Math.floor(duration / secondsPerBeat);

  const beats = Array.from({ length: totalBeats }, (_, i) => ({
    index: i,
    timestamp: i * secondsPerBeat,
    isDownbeat: i % beatsPerBar === 0,
  }));

  return (
    <div className="relative h-16 bg-black/30 rounded-lg border border-white/10 overflow-x-auto">
      <div className="absolute inset-0 flex items-center px-2 gap-1">
        {beats.map((beat) => {
          const isActive =
            currentTime >= beat.timestamp &&
            currentTime < beat.timestamp + secondsPerBeat;

          return (
            <div
              key={beat.index}
              className={`
                flex-shrink-0 w-1 rounded-full transition-all duration-150 cursor-pointer
                ${beat.isDownbeat ? "h-12 bg-cyan-500" : "h-8 bg-cyan-400/60"}
                ${
                  isActive
                    ? "shadow-[0_0_16px_rgba(6,182,212,1)] scale-110"
                    : "shadow-[0_0_8px_rgba(6,182,212,0.6)]"
                }
                hover:bg-cyan-300 hover:scale-125
              `}
              onClick={() => onBeatClick?.(beat.index, beat.timestamp)}
              title={`Beat ${
                (beat.index % beatsPerBar) + 1
              } | ${beat.timestamp.toFixed(2)}s`}
            />
          );
        })}
      </div>

      {/* Beat numbers overlay */}
      <div className="absolute inset-0 flex items-end px-2 gap-1 pointer-events-none">
        {beats
          .filter((beat) => beat.isDownbeat)
          .map((beat) => (
            <span
              key={beat.index}
              className="text-[10px] font-mono font-bold text-cyan-400/80"
              style={{ marginLeft: `${beat.index * 6}px` }}
            >
              {Math.floor(beat.index / beatsPerBar) + 1}
            </span>
          ))}
      </div>
    </div>
  );
}
```

**Usage Example:**

```tsx
<BeatGrid
  bpm={128}
  duration={180} // 3 minutes
  timeSignature={[4, 4]}
  currentTime={currentPlaybackTime}
  onBeatClick={(beatIndex, timestamp) => {
    console.log(`Beat ${beatIndex} at ${timestamp}s`);
  }}
/>
```

---

### AIRegions.tsx (AI-Detected Structure Segments)

```typescript
import React from "react";

export interface AIRegion {
  id: string;
  start: number; // seconds
  end: number; // seconds
  label: string; // "Intro", "Build-up", "Drop", etc.
  confidence: number; // 0-1
  color?: string;
}

export interface AIRegionsProps {
  regions: AIRegion[];
  duration: number;
  currentTime?: number;
  onRegionClick?: (region: AIRegion) => void;
}

export function AIRegions({
  regions,
  duration,
  currentTime = 0,
  onRegionClick,
}: AIRegionsProps) {
  const regionColors: Record<string, string> = {
    Intro: "from-purple-500/30 to-purple-500/10 border-purple-400",
    "Build-up": "from-pink-500/30 to-pink-500/10 border-pink-400",
    Drop: "from-cyan-500/30 to-cyan-500/10 border-cyan-400",
    Break: "from-yellow-500/30 to-yellow-500/10 border-yellow-400",
    Outro: "from-purple-500/30 to-purple-500/10 border-purple-400",
  };

  return (
    <div className="relative h-20 bg-black/30 rounded-lg border border-white/10 overflow-hidden">
      <div className="absolute inset-0 flex gap-1 p-2">
        {regions.map((region) => {
          const widthPercent = ((region.end - region.start) / duration) * 100;
          const leftPercent = (region.start / duration) * 100;
          const isActive =
            currentTime >= region.start && currentTime < region.end;

          const colorClasses =
            region.color || regionColors[region.label] || regionColors.Intro;

          return (
            <div
              key={region.id}
              className={`
                absolute h-full rounded-lg bg-gradient-to-b ${colorClasses}
                border-2 cursor-pointer transition-all duration-300
                ${
                  isActive
                    ? "ring-2 ring-white/60 shadow-[0_4px_20px_rgba(255,255,255,0.4)]"
                    : "shadow-[0_2px_12px_rgba(0,0,0,0.3)]"
                }
                hover:scale-105 hover:shadow-[0_6px_24px_rgba(236,72,153,0.6)]
              `}
              style={{
                width: `${widthPercent}%`,
                left: `${leftPercent}%`,
              }}
              onClick={() => onRegionClick?.(region)}
            >
              <div className="absolute inset-0 flex flex-col justify-center items-center p-2">
                <span className="text-xs font-bold text-white uppercase tracking-wide drop-shadow-md">
                  {region.label}
                </span>
                <span className="text-[10px] font-mono text-white/80 drop-shadow-md">
                  {region.start.toFixed(1)}s - {region.end.toFixed(1)}s
                </span>
                <span className="text-[10px] font-mono text-cyan-300 drop-shadow-md">
                  {(region.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Playhead indicator */}
      {currentTime > 0 && (
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-cyan-400 shadow-[0_0_12px_rgba(6,182,212,1)] pointer-events-none z-10"
          style={{ left: `${(currentTime / duration) * 100}%` }}
        />
      )}
    </div>
  );
}
```

**Usage Example:**

```tsx
const regions: AIRegion[] = [
  { id: "1", start: 0, end: 30, label: "Intro", confidence: 0.95 },
  { id: "2", start: 30, end: 75, label: "Build-up", confidence: 0.88 },
  { id: "3", start: 75, end: 150, label: "Drop", confidence: 0.92 },
  { id: "4", start: 150, end: 180, label: "Break", confidence: 0.84 },
  { id: "5", start: 180, end: 258, label: "Outro", confidence: 0.89 },
];

<AIRegions
  regions={regions}
  duration={258}
  currentTime={currentPlaybackTime}
  onRegionClick={(region) => {
    console.log("Clicked region:", region.label);
    wavesurfer.seekTo(region.start / 258);
  }}
/>;
```

---

## 🧠 3. Feature Components

### AIAnalysisPanel.tsx

```typescript
import React from "react";
import { Card } from "@/components/ui/Card";
import { Progress } from "@/components/ui/Progress";
import { Badge } from "@/components/ui/Badge";

export interface GenreConfidence {
  genre: string;
  confidence: number; // 0-1
}

export interface AudioFeatures {
  bpm: number;
  bpmConfidence: number;
  key: string;
  keyConfidence: number;
  energy: number; // 0-100
  danceability: number; // 0-100
  valence: number; // 0-100 (musical positivity)
}

export interface StructureSegment {
  label: string;
  startTime: number;
  endTime: number;
}

export interface AIAnalysisPanelProps {
  genres: GenreConfidence[];
  features: AudioFeatures;
  structure: StructureSegment[];
  onExport?: () => void;
  onRetrain?: () => void;
}

export function AIAnalysisPanel({
  genres,
  features,
  structure,
  onExport,
  onRetrain,
}: AIAnalysisPanelProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-6">
      {/* Genre Classification */}
      <Card variant="glassHeavy" title="🧠 AI Analysis" icon={null}>
        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-purple-400 uppercase tracking-wide">
            Genre Classification
          </h4>

          {genres.map((genre) => (
            <div key={genre.genre} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-white">
                  {genre.genre}
                </span>
                <span className="text-sm font-mono font-bold text-cyan-400">
                  {(genre.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <Progress value={genre.confidence * 100} variant="gradient" />
            </div>
          ))}
        </div>
      </Card>

      {/* Audio Features */}
      <Card variant="glass">
        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-purple-400 uppercase tracking-wide">
            Audio Features
          </h4>

          {/* BPM */}
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">
              BPM
            </div>
            <div className="text-3xl font-black font-mono bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
              {features.bpm.toFixed(1)} ±{features.bpmConfidence.toFixed(1)}
            </div>
            <Progress
              value={features.bpmConfidence * 100}
              variant="cyan"
              className="mt-2"
            />
          </div>

          {/* Key */}
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">
              Key
            </div>
            <div className="text-2xl font-black font-mono text-cyan-400">
              {features.key} ({(features.keyConfidence * 100).toFixed(0)}%)
            </div>
          </div>

          {/* Energy */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs font-bold text-gray-400 uppercase">
                Energy
              </span>
              <span className="text-xs font-mono font-bold text-pink-400">
                {features.energy}/100
              </span>
            </div>
            <Progress value={features.energy} variant="pink" />
          </div>

          {/* Danceability */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs font-bold text-gray-400 uppercase">
                Danceability
              </span>
              <span className="text-xs font-mono font-bold text-purple-400">
                {features.danceability}/100
              </span>
            </div>
            <Progress value={features.danceability} variant="purple" />
          </div>

          {/* Valence */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs font-bold text-gray-400 uppercase">
                Valence
              </span>
              <span className="text-xs font-mono font-bold text-cyan-400">
                {features.valence}/100
              </span>
            </div>
            <Progress value={features.valence} variant="cyan" />
          </div>
        </div>
      </Card>

      {/* Structure Detection */}
      <Card variant="glass">
        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-purple-400 uppercase tracking-wide">
            Structure Detection
          </h4>

          <div className="space-y-2">
            {structure.map((segment, index) => (
              <div
                key={index}
                className="bg-gradient-to-r from-pink-500/20 to-pink-500/5 border-l-4 border-pink-500 rounded-lg p-3 cursor-pointer hover:from-pink-500/30 hover:to-pink-500/10 hover:border-pink-400 hover:shadow-[0_4px_16px_rgba(236,72,153,0.4)] transition-all"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-xs font-mono font-bold text-cyan-400">
                      {formatTime(segment.startTime)} -{" "}
                      {formatTime(segment.endTime)}
                    </span>
                    <span className="ml-2 text-sm font-bold text-white">
                      {segment.label}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Action buttons */}
      <div className="space-y-2">
        <button
          onClick={onExport}
          className="w-full bg-gradient-to-r from-purple-500 to-cyan-500 hover:from-purple-600 hover:to-cyan-600 text-white font-semibold py-3 rounded-lg transition-all shadow-[0_0_20px_rgba(139,92,246,0.5)] hover:shadow-[0_0_40px_rgba(139,92,246,0.8)]"
        >
          📊 Export Metadata
        </button>
        <button
          onClick={onRetrain}
          className="w-full bg-white/10 hover:bg-white/15 border border-white/20 hover:border-purple-400/40 text-white font-semibold py-3 rounded-lg transition-all"
        >
          🔄 Retrain Model
        </button>
      </div>
    </div>
  );
}
```

**Usage Example:**

```tsx
const genres: GenreConfidence[] = [
  { genre: "Electronic", confidence: 0.87 },
  { genre: "House", confidence: 0.65 },
  { genre: "Techno", confidence: 0.43 },
];

const features: AudioFeatures = {
  bpm: 128.4,
  bpmConfidence: 0.2,
  key: "C Minor",
  keyConfidence: 0.97,
  energy: 82,
  danceability: 75,
  valence: 62,
};

const structure: StructureSegment[] = [
  { label: "Intro", startTime: 0, endTime: 30 },
  { label: "Build-up", startTime: 30, endTime: 75 },
  { label: "Drop", startTime: 75, endTime: 150 },
];

<AIAnalysisPanel
  genres={genres}
  features={features}
  structure={structure}
  onExport={() => console.log("Export metadata")}
  onRetrain={() => console.log("Retrain AI model")}
/>;
```

---

## 🎯 4. Integration Example: Complete Dashboard

```typescript
import React, { useState } from "react";
import { WaveformPlayer } from "@/components/audio/WaveformPlayer";
import { Spectrogram } from "@/components/audio/Spectrogram";
import { BeatGrid } from "@/components/audio/BeatGrid";
import { AIRegions } from "@/components/audio/AIRegions";
import { AIAnalysisPanel } from "@/components/features/AIAnalysisPanel";

export function Dashboard() {
  const [currentTime, setCurrentTime] = useState(0);
  const audioContext = new AudioContext();
  const analyser = audioContext.createAnalyser();

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="grid grid-cols-[400px_1fr_320px] gap-6">
        {/* Left: Sample Library */}
        <div className="space-y-4">
          <h2 className="font-heading text-2xl font-bold text-text-primary">
            Sample Library
          </h2>
          {/* Sample cards here */}
        </div>

        {/* Center: Main Visualizer */}
        <div className="space-y-4">
          <WaveformPlayer
            audioUrl="/samples/bassline-128.wav"
            title="bassline-128.wav - C Minor - 128 BPM"
            height={150}
          />

          <Spectrogram
            audioContext={audioContext}
            analyserNode={analyser}
            height={200}
          />

          <AIRegions
            regions={[
              { id: "1", start: 0, end: 30, label: "Intro", confidence: 0.95 },
              {
                id: "2",
                start: 30,
                end: 75,
                label: "Build-up",
                confidence: 0.88,
              },
            ]}
            duration={180}
            currentTime={currentTime}
          />

          <BeatGrid bpm={128} duration={180} currentTime={currentTime} />
        </div>

        {/* Right: AI Analysis */}
        <div>
          <AIAnalysisPanel
            genres={[{ genre: "Electronic", confidence: 0.87 }]}
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
    </div>
  );
}
```

---

**Document Version:** 1.0.0
**Status:** Complete Component Implementation Guide
**Next Steps:** Implement components in React, integrate with backend API
