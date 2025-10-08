# 🎵 Wavesurfer.js Implementation Guide for SampleMind AI

**Technology Stack:** React 19+, TypeScript 5.9+, wavesurfer.js 7.8+
**Design System:** Glassmorphism + Neon Cyberpunk
**Created:** October 7, 2025

---

## 📋 Quick Start

### 1. Installation

```bash
cd /home/lchta/Projects/Samplemind-AI/web-app

# Install wavesurfer.js
npm install wavesurfer.js@7.8.13

# Install types (if available)
npm install --save-dev @types/wavesurfer.js
```

### 2. Project Structure

```
/src/components/audio/
├── WaveformPlayer/
│   ├── WaveformPlayer.tsx          # Main player component
│   ├── WaveformControls.tsx        # Play/pause/seek controls
│   ├── WaveformTimeline.tsx        # Timeline with markers
│   ├── useWavesurfer.ts           # Custom hook
│   ├── types.ts                    # TypeScript interfaces
│   └── index.ts                    # Exports
├── Spectrogram/
│   ├── Spectrogram.tsx             # FFT visualization
│   ├── useAudioAnalyser.ts        # Web Audio API hook
│   └── index.ts
├── BeatGrid/
│   ├── BeatGrid.tsx                # BPM grid overlay
│   └── index.ts
└── AIRegions/
    ├── AIRegions.tsx               # AI-detected segments
    └── index.ts
```

---

## 🛠️ Step-by-Step Implementation

### Step 1: Create Custom Hook `useWavesurfer.ts`

```typescript
// /src/components/audio/WaveformPlayer/useWavesurfer.ts

import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";

export interface UseWavesurferOptions {
  audioUrl: string;
  waveColor?: string;
  progressColor?: string;
  cursorColor?: string;
  height?: number;
  barWidth?: number;
  barGap?: number;
  barRadius?: number;
  normalize?: boolean;
  onReady?: (wavesurfer: WaveSurfer) => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
  onTimeUpdate?: (currentTime: number) => void;
}

export function useWavesurfer({
  audioUrl,
  waveColor = "#8B5CF6",
  progressColor = "#06B6D4",
  cursorColor = "#EC4899",
  height = 150,
  barWidth = 2,
  barGap = 1,
  barRadius = 2,
  normalize = true,
  onReady,
  onPlay,
  onPause,
  onFinish,
  onTimeUpdate,
}: UseWavesurferOptions) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);

  useEffect(() => {
    if (!containerRef.current) return;

    // Destroy existing instance
    if (wavesurferRef.current) {
      wavesurferRef.current.destroy();
    }

    // Create new WaveSurfer instance
    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      height,
      waveColor,
      progressColor,
      cursorColor,
      cursorWidth: 2,
      barWidth,
      barGap,
      barRadius,
      responsive: true,
      normalize,
      backend: "WebAudio",
      hideScrollbar: true,
      interact: true,
    });

    // Load audio file
    wavesurfer.load(audioUrl);

    // Event listeners
    wavesurfer.on("ready", () => {
      setIsLoading(false);
      setDuration(wavesurfer.getDuration());
      wavesurfer.setVolume(volume);
      onReady?.(wavesurfer);
    });

    wavesurfer.on("loading", (percent) => {
      console.log(`Loading: ${percent}%`);
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

    wavesurfer.on("seeking", (progress) => {
      const time = progress * wavesurfer.getDuration();
      setCurrentTime(time);
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

  return {
    containerRef,
    wavesurfer: wavesurferRef.current,
    isPlaying,
    isLoading,
    currentTime,
    duration,
    volume,
    setVolume,
    togglePlayPause: () => wavesurferRef.current?.playPause(),
    play: () => wavesurferRef.current?.play(),
    pause: () => wavesurferRef.current?.pause(),
    stop: () => wavesurferRef.current?.stop(),
    seekTo: (progress: number) => wavesurferRef.current?.seekTo(progress),
    skip: (seconds: number) => {
      if (!wavesurferRef.current) return;
      const newTime = currentTime + seconds;
      wavesurferRef.current.seekTo(newTime / duration);
    },
  };
}
```

---

### Step 2: Create Main Component `WaveformPlayer.tsx`

```typescript
// /src/components/audio/WaveformPlayer/WaveformPlayer.tsx

import React from "react";
import { motion } from "framer-motion";
import {
  PlayIcon,
  PauseIcon,
  SkipForward,
  SkipBack,
  Volume2,
} from "lucide-react";
import { useWavesurfer } from "./useWavesurfer";
import { designTokens } from "@/design-system/tokens";

export interface WaveformPlayerProps {
  audioUrl: string;
  title?: string;
  artist?: string;
  height?: number;
  waveColor?: string;
  progressColor?: string;
  cursorColor?: string;
  showControls?: boolean;
  showTimeline?: boolean;
  className?: string;
}

export function WaveformPlayer({
  audioUrl,
  title,
  artist,
  height = 150,
  waveColor = designTokens.colors.primary.purple,
  progressColor = designTokens.colors.accent.cyan,
  cursorColor = designTokens.colors.accent.pink,
  showControls = true,
  showTimeline = true,
  className = "",
}: WaveformPlayerProps) {
  const {
    containerRef,
    isPlaying,
    isLoading,
    currentTime,
    duration,
    volume,
    setVolume,
    togglePlayPause,
    skip,
  } = useWavesurfer({
    audioUrl,
    waveColor,
    progressColor,
    cursorColor,
    height,
    barWidth: 2,
    barGap: 1,
    barRadius: 2,
  });

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <motion.div
      className={`glass-card rounded-xl p-6 space-y-4 ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      {(title || artist) && (
        <div className="flex items-center justify-between">
          <div>
            {title && (
              <h3 className="font-heading text-xl font-semibold text-text-primary">
                {title}
              </h3>
            )}
            {artist && (
              <p className="text-sm text-text-secondary mt-1">{artist}</p>
            )}
          </div>

          {showTimeline && (
            <div className="text-sm font-mono text-cyan-400">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          )}
        </div>
      )}

      {/* Waveform Container */}
      <div className="relative">
        {/* Loading Spinner */}
        {isLoading && (
          <div
            className="absolute inset-0 flex items-center justify-center
                          bg-black/30 rounded-lg z-10 backdrop-blur-sm"
          >
            <div className="relative">
              <div
                className="animate-spin rounded-full h-12 w-12 border-t-2
                              border-b-2 border-purple-500"
              />
              <div
                className="absolute inset-0 rounded-full border-2
                              border-purple-500/20"
              />
            </div>
          </div>
        )}

        {/* Waveform */}
        <div
          ref={containerRef}
          className="bg-black/30 rounded-lg border border-white/10 overflow-hidden
                     hover:border-purple-400/30 transition-all duration-300"
        />
      </div>

      {/* Playback Controls */}
      {showControls && (
        <div className="flex items-center gap-4">
          {/* Skip Back */}
          <button
            onClick={() => skip(-10)}
            disabled={isLoading}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/15
                       transition-all text-text-primary disabled:opacity-50
                       disabled:cursor-not-allowed"
            aria-label="Skip back 10 seconds"
          >
            <SkipBack size={20} />
          </button>

          {/* Play/Pause */}
          <button
            onClick={togglePlayPause}
            disabled={isLoading}
            className="p-4 rounded-full bg-gradient-to-r from-purple-500 to-purple-600
                       shadow-[0_8px_24px_rgba(139,92,246,0.5)]
                       hover:shadow-[0_12px_32px_rgba(6,182,212,0.7)]
                       hover:scale-110 active:scale-95
                       transition-all disabled:opacity-50 disabled:cursor-not-allowed
                       disabled:hover:scale-100"
            aria-label={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? (
              <PauseIcon size={24} className="text-white" />
            ) : (
              <PlayIcon size={24} className="text-white ml-1" />
            )}
          </button>

          {/* Skip Forward */}
          <button
            onClick={() => skip(10)}
            disabled={isLoading}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/15
                       transition-all text-text-primary disabled:opacity-50
                       disabled:cursor-not-allowed"
            aria-label="Skip forward 10 seconds"
          >
            <SkipForward size={20} />
          </button>

          {/* Volume Control */}
          <div className="flex-1 flex items-center gap-3 ml-4">
            <Volume2 size={20} className="text-text-secondary" />

            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={volume}
              onChange={(e) => setVolume(Number(e.target.value))}
              disabled={isLoading}
              className="flex-1 h-2 bg-white/10 rounded-full appearance-none
                         cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed
                         [&::-webkit-slider-thumb]:appearance-none
                         [&::-webkit-slider-thumb]:w-4
                         [&::-webkit-slider-thumb]:h-4
                         [&::-webkit-slider-thumb]:bg-gradient-to-r
                         [&::-webkit-slider-thumb]:from-cyan-400
                         [&::-webkit-slider-thumb]:to-cyan-500
                         [&::-webkit-slider-thumb]:rounded-full
                         [&::-webkit-slider-thumb]:shadow-[0_0_12px_rgba(6,182,212,0.8)]
                         [&::-webkit-slider-thumb]:cursor-pointer
                         hover:[&::-webkit-slider-thumb]:scale-110
                         transition-transform"
              aria-label="Volume control"
            />

            <span className="text-sm font-mono font-bold text-cyan-400 w-12 text-right">
              {Math.round(volume * 100)}%
            </span>
          </div>
        </div>
      )}
    </motion.div>
  );
}
```

---

### Step 3: Create TypeScript Types

```typescript
// /src/components/audio/WaveformPlayer/types.ts

import type WaveSurfer from "wavesurfer.js";

export interface WaveformPlayerConfig {
  audioUrl: string;
  waveColor?: string;
  progressColor?: string;
  cursorColor?: string;
  height?: number;
  barWidth?: number;
  barGap?: number;
  barRadius?: number;
}

export interface WaveformPlayerState {
  isPlaying: boolean;
  isLoading: boolean;
  currentTime: number;
  duration: number;
  volume: number;
}

export interface WaveformPlayerActions {
  play: () => void;
  pause: () => void;
  stop: () => void;
  togglePlayPause: () => void;
  seekTo: (progress: number) => void;
  skip: (seconds: number) => void;
  setVolume: (volume: number) => void;
}

export interface WaveformPlayerCallbacks {
  onReady?: (wavesurfer: WaveSurfer) => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
  onTimeUpdate?: (currentTime: number) => void;
  onSeek?: (progress: number) => void;
  onVolumeChange?: (volume: number) => void;
}

export type WaveformPlayerHook = WaveformPlayerState &
  WaveformPlayerActions & {
    containerRef: React.RefObject<HTMLDivElement>;
    wavesurfer: WaveSurfer | null;
  };
```

---

### Step 4: Create Export Index

```typescript
// /src/components/audio/WaveformPlayer/index.ts

export { WaveformPlayer } from "./WaveformPlayer";
export { useWavesurfer } from "./useWavesurfer";
export type * from "./types";
```

---

## 🎨 Integration with Existing Components

### Example: Sample Library Card with Waveform Preview

```tsx
// /src/components/molecules/SampleCard.tsx

import { WaveformPlayer } from "@/components/audio/WaveformPlayer";

export function SampleCard({
  sampleId,
  filename,
  audioUrl,
  bpm,
  key,
}: SampleCardProps) {
  return (
    <div className="glass-card rounded-xl p-4">
      <WaveformPlayer
        audioUrl={audioUrl}
        title={filename}
        height={80}
        showControls={false}
        showTimeline={false}
      />

      <div className="mt-3 flex items-center gap-4 text-sm">
        <span className="font-mono text-cyan-400">{bpm} BPM</span>
        <span className="font-mono text-purple-400">{key}</span>
      </div>
    </div>
  );
}
```

---

## 🧪 Testing

### Unit Test Example

```typescript
// /src/components/audio/WaveformPlayer/__tests__/WaveformPlayer.test.tsx

import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WaveformPlayer } from "../WaveformPlayer";

describe("WaveformPlayer", () => {
  it("renders without crashing", () => {
    render(<WaveformPlayer audioUrl="/test.mp3" />);
    expect(screen.getByRole("button", { name: /play/i })).toBeInTheDocument();
  });

  it("toggles play/pause on button click", async () => {
    const user = userEvent.setup();
    render(<WaveformPlayer audioUrl="/test.mp3" />);

    const playButton = screen.getByRole("button", { name: /play/i });
    await user.click(playButton);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /pause/i })
      ).toBeInTheDocument();
    });
  });

  it("calls onPlay callback when playing", async () => {
    const onPlay = vi.fn();
    const user = userEvent.setup();

    render(<WaveformPlayer audioUrl="/test.mp3" onPlay={onPlay} />);

    await user.click(screen.getByRole("button", { name: /play/i }));

    await waitFor(() => {
      expect(onPlay).toHaveBeenCalled();
    });
  });
});
```

---

## 🚀 Advanced Features

### 1. Regions/Markers Support

```typescript
import RegionsPlugin from "wavesurfer.js/dist/plugins/regions";

const regions = wavesurfer.registerPlugin(RegionsPlugin.create());

// Add AI-detected regions
regions.addRegion({
  start: 0,
  end: 30,
  color: "rgba(139, 92, 246, 0.3)",
  drag: false,
  resize: false,
  content: "Intro",
});
```

### 2. Zoom/Pan Controls

```typescript
const zoom = wavesurfer.registerPlugin(
  ZoomPlugin.create({
    scale: 0.5,
    maxZoom: 500,
    deltaThreshold: 5,
  })
);
```

### 3. Timeline Plugin

```typescript
import TimelinePlugin from "wavesurfer.js/dist/plugins/timeline";

const timeline = wavesurfer.registerPlugin(
  TimelinePlugin.create({
    height: 20,
    timeInterval: 0.5,
    primaryLabelInterval: 5,
    secondaryLabelInterval: 1,
  })
);
```

---

## 📊 Performance Optimization

### 1. Lazy Loading

```tsx
import { lazy, Suspense } from "react";

const WaveformPlayer = lazy(() => import("./WaveformPlayer"));

function MyComponent() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <WaveformPlayer audioUrl="/audio.mp3" />
    </Suspense>
  );
}
```

### 2. Memoization

```tsx
import { memo } from "react";

export const WaveformPlayer = memo(
  ({ audioUrl, ...props }) => {
    // Component implementation
  },
  (prevProps, nextProps) => {
    return prevProps.audioUrl === nextProps.audioUrl;
  }
);
```

### 3. Debounced Volume Control

```tsx
import { debounce } from "lodash-es";

const handleVolumeChange = debounce((value: number) => {
  setVolume(value);
}, 100);
```

---

## ✅ Checklist

- [ ] Install wavesurfer.js: `npm install wavesurfer.js@7.8.13`
- [ ] Create `useWavesurfer.ts` hook
- [ ] Build `WaveformPlayer.tsx` component
- [ ] Add TypeScript types in `types.ts`
- [ ] Export from `index.ts`
- [ ] Write unit tests
- [ ] Write E2E tests
- [ ] Add to Storybook
- [ ] Update documentation
- [ ] Test with real audio files
- [ ] Optimize performance
- [ ] Add accessibility features

---

## 📚 Resources

- **wavesurfer.js Docs:** https://wavesurfer.xyz/docs/
- **GitHub Repo:** https://github.com/katspaugh/wavesurfer.js
- **Examples:** https://wavesurfer.xyz/examples/
- **Plugins:** https://wavesurfer.xyz/docs/plugins/

---

**Document Version:** 1.0.0
**Status:** Ready for Implementation
**Next Step:** Run `npm install wavesurfer.js@7.8.13` in `/web-app`
