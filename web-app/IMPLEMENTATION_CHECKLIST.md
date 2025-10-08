# ✅ Wavesurfer.js Implementation Checklist

**Project:** SampleMind AI
**Task:** Integrate wavesurfer.js for Professional Audio Playback
**Date:** October 7, 2025

---

## 🚀 Phase 1: Setup & Foundation (Week 1)

### 1.1 Install Dependencies

- [ ] Open terminal in `/web-app` directory
- [ ] Run: `npm install wavesurfer.js@7.8.13`
- [ ] Run: `npm install --save-dev @types/wavesurfer.js` (if available)
- [ ] Verify installation in `package.json`
- [ ] Run: `npm install` to ensure all dependencies are installed

### 1.2 Create Directory Structure

- [ ] Create: `src/components/audio/WaveformPlayer/`
- [ ] Create: `src/components/audio/Spectrogram/`
- [ ] Create: `src/components/audio/BeatGrid/`
- [ ] Create: `src/components/audio/AIRegions/`

### 1.3 Implement Core Hook

- [ ] Create: `src/components/audio/WaveformPlayer/useWavesurfer.ts`
- [ ] Copy implementation from `WAVESURFER_IMPLEMENTATION_GUIDE.md`
- [ ] Import WaveSurfer: `import WaveSurfer from 'wavesurfer.js'`
- [ ] Add TypeScript types
- [ ] Test hook with sample audio
- [ ] Add error handling
- [ ] Add loading states

### 1.4 Create TypeScript Types

- [ ] Create: `src/components/audio/WaveformPlayer/types.ts`
- [ ] Define `WaveformPlayerConfig` interface
- [ ] Define `WaveformPlayerState` interface
- [ ] Define `WaveformPlayerActions` interface
- [ ] Define `WaveformPlayerCallbacks` interface
- [ ] Export all types

### 1.5 Build Main Component

- [ ] Create: `src/components/audio/WaveformPlayer/WaveformPlayer.tsx`
- [ ] Import `useWavesurfer` hook
- [ ] Import design tokens from `@/design-system/tokens`
- [ ] Import Framer Motion
- [ ] Import Lucide icons (PlayIcon, PauseIcon, etc.)
- [ ] Implement component logic
- [ ] Add loading spinner
- [ ] Add playback controls
- [ ] Add volume control
- [ ] Add time display
- [ ] Style with design system tokens

### 1.6 Create Export Index

- [ ] Create: `src/components/audio/WaveformPlayer/index.ts`
- [ ] Export `WaveformPlayer` component
- [ ] Export `useWavesurfer` hook
- [ ] Export all types: `export type * from './types'`

### 1.7 Test Basic Implementation

- [ ] Create test page: `src/pages/WaveformTest.tsx`
- [ ] Import WaveformPlayer
- [ ] Add sample audio URL
- [ ] Verify component renders
- [ ] Test play/pause functionality
- [ ] Test seek functionality
- [ ] Test volume control
- [ ] Check console for errors

---

## 🎨 Phase 2: Core Components (Week 2)

### 2.1 GlassmorphicSampleCard

- [ ] Create: `src/components/molecules/GlassmorphicSampleCard/`
- [ ] Implement component with mini waveform preview
- [ ] Add sample metadata (BPM, key, duration)
- [ ] Add tags display
- [ ] Add hover effects
- [ ] Add play/analyze buttons
- [ ] Style with glassmorphism effect
- [ ] Add Framer Motion animations

### 2.2 AudioHeroSection

- [ ] Create: `src/components/organisms/AudioHeroSection/`
- [ ] Implement hero layout
- [ ] Add gradient background
- [ ] Integrate WaveformPlayer
- [ ] Add file dropzone for upload
- [ ] Add animations on mount
- [ ] Style with design system

### 2.3 FeatureGrid

- [ ] Create: `src/components/organisms/FeatureGrid/`
- [ ] Define feature data (icon, title, description)
- [ ] Implement 3-column grid layout
- [ ] Add gradient accent icons
- [ ] Add hover effects
- [ ] Add scroll-triggered animations
- [ ] Make responsive (mobile: 1 col, tablet: 2 cols, desktop: 3 cols)

### 2.4 Spectrogram Component

- [ ] Create: `src/components/audio/Spectrogram/Spectrogram.tsx`
- [ ] Create: `src/components/audio/Spectrogram/useAudioAnalyser.ts`
- [ ] Implement Web Audio API AnalyserNode hook
- [ ] Create canvas-based FFT visualization
- [ ] Add gradient colors (purple → pink → cyan)
- [ ] Add real-time animation loop
- [ ] Optimize rendering performance

### 2.5 BeatGrid Component

- [ ] Create: `src/components/audio/BeatGrid/BeatGrid.tsx`
- [ ] Calculate beats from BPM and duration
- [ ] Render beat markers
- [ ] Highlight downbeats
- [ ] Add current time playhead
- [ ] Add click handlers for seeking
- [ ] Style with neon cyan colors

### 2.6 AIRegions Component

- [ ] Create: `src/components/audio/AIRegions/AIRegions.tsx`
- [ ] Define AIRegion interface (start, end, label, confidence)
- [ ] Render region overlays
- [ ] Add region labels (Intro, Build-up, Drop, etc.)
- [ ] Add confidence percentage display
- [ ] Add hover effects
- [ ] Add click handlers for region navigation

---

## 🔌 Phase 3: Integration (Week 3)

### 3.1 Backend API Integration

- [ ] Create API client: `src/api/audioApi.ts`
- [ ] Implement `uploadAudio(file: File)` endpoint
- [ ] Implement `getAudioAnalysis(fileId: string)` endpoint
- [ ] Implement `getAudioMetadata(fileId: string)` endpoint
- [ ] Add error handling and retry logic
- [ ] Add loading states

### 3.2 State Management

- [ ] Create Zustand store: `src/stores/audioStore.ts`
- [ ] Add `selectedSample` state
- [ ] Add `isPlaying` state
- [ ] Add `currentTime` state
- [ ] Add `audioAnalysis` state
- [ ] Add actions: `setSelectedSample`, `togglePlay`, etc.

### 3.3 AI Analysis Integration

- [ ] Fetch AI analysis data from backend
- [ ] Parse genre confidence scores
- [ ] Parse audio features (BPM, key, energy, etc.)
- [ ] Parse structure segments (Intro, Drop, etc.)
- [ ] Display in AIAnalysisPanel
- [ ] Add loading/error states

### 3.4 Real-time Audio Analysis

- [ ] Connect WaveSurfer to Web Audio API
- [ ] Create AnalyserNode for FFT data
- [ ] Pass analyser to Spectrogram component
- [ ] Update visualizations in real-time
- [ ] Optimize for 60fps rendering

### 3.5 Waveform Caching

- [ ] Implement waveform pre-generation on upload
- [ ] Store waveform peaks in backend
- [ ] Cache waveform data in IndexedDB (idb-keyval)
- [ ] Load cached waveforms instantly
- [ ] Fallback to live generation if cache miss

### 3.6 Keyboard Shortcuts

- [ ] Add: `Space` = play/pause
- [ ] Add: `Left Arrow` = skip back 10s
- [ ] Add: `Right Arrow` = skip forward 10s
- [ ] Add: `Up Arrow` = volume up
- [ ] Add: `Down Arrow` = volume down
- [ ] Add: `M` = mute/unmute
- [ ] Display keyboard shortcuts in help modal

---

## ✨ Phase 4: Polish & Optimization (Week 4)

### 4.1 Animations

- [ ] Add Framer Motion to all components
- [ ] Add mount animations (fade in, slide up)
- [ ] Add hover animations (scale, glow)
- [ ] Add transition animations between states
- [ ] Optimize animation performance (use `will-change`)
- [ ] Add loading skeleton animations

### 4.2 Responsive Design

- [ ] Test on mobile (320px - 767px)
- [ ] Test on tablet (768px - 1023px)
- [ ] Test on desktop (1024px - 1439px)
- [ ] Test on wide screens (1440px+)
- [ ] Adjust grid layouts for breakpoints
- [ ] Adjust font sizes for readability
- [ ] Test touch interactions on mobile

### 4.3 Accessibility

- [ ] Add ARIA labels to all interactive elements
- [ ] Add `role` attributes (button, slider, etc.)
- [ ] Add keyboard navigation support
- [ ] Add focus indicators (ring-2 ring-purple-500)
- [ ] Add screen reader announcements
- [ ] Test with axe DevTools
- [ ] Test with keyboard only (no mouse)
- [ ] Test with screen reader (NVDA/JAWS)

### 4.4 Performance Optimization

- [ ] Lazy load WaveformPlayer component
- [ ] Memoize expensive computations
- [ ] Debounce volume slider
- [ ] Use `React.memo` for pure components
- [ ] Optimize re-renders with `useMemo`/`useCallback`
- [ ] Reduce bundle size (code splitting)
- [ ] Measure Core Web Vitals (LCP, FID, CLS)
- [ ] Achieve <100ms interaction latency

### 4.5 Unit Tests

- [ ] Install test dependencies (already installed: vitest, @testing-library/react)
- [ ] Write tests for `useWavesurfer` hook
- [ ] Write tests for `WaveformPlayer` component
- [ ] Write tests for `GlassmorphicSampleCard`
- [ ] Write tests for `AudioHeroSection`
- [ ] Write tests for `Spectrogram`
- [ ] Write tests for `BeatGrid`
- [ ] Write tests for `AIRegions`
- [ ] Achieve >80% code coverage

### 4.6 E2E Tests

- [ ] Install Playwright (already installed: @playwright/test)
- [ ] Write E2E test: Upload audio file
- [ ] Write E2E test: Play/pause audio
- [ ] Write E2E test: Seek in waveform
- [ ] Write E2E test: Adjust volume
- [ ] Write E2E test: View AI analysis
- [ ] Write E2E test: Navigate regions
- [ ] Run tests in CI/CD pipeline

### 4.7 Storybook (Optional)

- [ ] Install Storybook: `npx storybook@latest init`
- [ ] Create story: `WaveformPlayer.stories.tsx`
- [ ] Create story: `GlassmorphicSampleCard.stories.tsx`
- [ ] Create story: `Spectrogram.stories.tsx`
- [ ] Add controls for props
- [ ] Document component usage
- [ ] Deploy Storybook (Chromatic)

### 4.8 Documentation

- [ ] Write component README files
- [ ] Add JSDoc comments to all functions
- [ ] Create usage examples
- [ ] Document API endpoints
- [ ] Update main README with wavesurfer.js integration
- [ ] Create video demo
- [ ] Write migration guide (if updating existing components)

---

## 🧪 Testing Checklist

### Manual Testing

- [ ] Upload audio file (MP3, WAV, FLAC)
- [ ] Verify waveform renders correctly
- [ ] Test play/pause button
- [ ] Test seek by clicking waveform
- [ ] Test skip forward/backward buttons
- [ ] Test volume slider
- [ ] Test keyboard shortcuts
- [ ] Test on mobile device
- [ ] Test with screen reader
- [ ] Test offline functionality

### Automated Testing

- [ ] Run unit tests: `npm run test`
- [ ] Run coverage: `npm run test:coverage`
- [ ] Run E2E tests: `npm run test:visual`
- [ ] Check accessibility: `npm run test:a11y` (custom script)
- [ ] Check bundle size: `npm run build && ls -lh dist/`
- [ ] Verify no console errors
- [ ] Verify no TypeScript errors: `npx tsc --noEmit`

---

## 📊 Success Criteria

### Functionality ✅

- [ ] Audio uploads successfully
- [ ] Waveform displays correctly
- [ ] Playback controls work (play, pause, seek, volume)
- [ ] AI analysis displays correctly
- [ ] Spectrogram visualizes in real-time
- [ ] Beat grid aligns with BPM
- [ ] AI regions display structure segments

### Performance ✅

- [ ] Waveform loads in <2 seconds
- [ ] Playback starts in <500ms
- [ ] Seek latency <100ms
- [ ] 60fps visualizations
- [ ] Bundle size <500KB (gzipped)

### Design ✅

- [ ] Matches SampleMind glassmorphism aesthetic
- [ ] Uses design system tokens consistently
- [ ] Responsive across all breakpoints
- [ ] Smooth animations with Framer Motion
- [ ] Neon glow effects on hover

### Accessibility ✅

- [ ] WCAG 2.1 AA compliant
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Focus indicators visible
- [ ] Color contrast ratio >4.5:1

### Code Quality ✅

- [ ] TypeScript strict mode enabled
- [ ] No `any` types without justification
- [ ] All functions documented with JSDoc
- [ ] Unit test coverage >80%
- [ ] E2E tests cover critical paths
- [ ] No console errors or warnings

---

## 🎯 Quick Commands Reference

```bash
# Install dependencies
npm install wavesurfer.js@7.8.13

# Create directories
mkdir -p src/components/audio/{WaveformPlayer,Spectrogram,BeatGrid,AIRegions}

# Run dev server
npm run dev

# Run tests
npm run test              # Unit tests
npm run test:coverage     # Coverage report
npm run test:visual       # E2E tests

# Build for production
npm run build
npm run preview

# Type checking
npx tsc --noEmit
```

---

## 📚 Documentation References

1. **Implementation Guide:** `/web-app/WAVESURFER_IMPLEMENTATION_GUIDE.md`
2. **Design Analysis:** `/web-app/DESIGN_INSPIRATION_ANALYSIS.md`
3. **Component Guide:** `/web-app/SAMPLEMIND_COMPONENT_GUIDE.md`
4. **Design System:** `/web-app/src/design-system/tokens.ts`
5. **wavesurfer.js Docs:** https://wavesurfer.xyz/docs/

---

## 🐛 Common Issues & Solutions

### Issue: Waveform not rendering

**Solution:** Ensure container has a defined height and width

### Issue: Audio not playing

**Solution:** Check browser autoplay policy, may need user interaction first

### Issue: Poor performance

**Solution:** Reduce barWidth, enable waveform caching, use Web Workers

### Issue: TypeScript errors

**Solution:** Install `@types/wavesurfer.js` or create custom type declarations

### Issue: Glitchy animations

**Solution:** Use `will-change: transform` and `transform: translateZ(0)` for GPU acceleration

---

**Last Updated:** October 7, 2025
**Status:** Ready for Implementation
**Estimated Completion:** 4 weeks
**Priority:** HIGH

---

**Start Implementation:** ✅ Begin with Phase 1.1 - Install Dependencies
