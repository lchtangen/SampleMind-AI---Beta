/**
 * useAudioReactive Hook
 * Real-time audio data extraction for animations
 * Provides normalized amplitude and frequency data for audio-reactive visual effects
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface AudioReactiveData {
  amplitude: number; // 0-1 normalized amplitude
  frequency: number; // 0-1 normalized frequency
  frequencies: number[]; // Array of frequency bins (0-1)
  rms: number; // Root mean square energy
  isPlaying: boolean;
}

export interface UseAudioReactiveOptions {
  smoothing?: number; // 0-1, how much to smooth values
  fftSize?: number; // FFT size (256, 512, 1024, 2048)
  minDecibels?: number; // Minimum dB value (-100 to 0)
  maxDecibels?: number; // Maximum dB value (0 to -30)
  enabled?: boolean; // Enable/disable updates
}

/**
 * Hook to extract real-time audio data from Web Audio API
 * Can work with audio elements, microphone input, or external AudioContext
 */
export const useAudioReactive = (
  options: UseAudioReactiveOptions = {}
): AudioReactiveData => {
  const {
    smoothing = 0.85,
    fftSize = 256,
    minDecibels = -100,
    maxDecibels = -10,
    enabled = true,
  } = options;

  const [audioData, setAudioData] = useState<AudioReactiveData>({
    amplitude: 0,
    frequency: 0,
    frequencies: new Array(fftSize / 2).fill(0),
    rms: 0,
    isPlaying: false,
  });

  const contextRef = useRef<AudioContext | null>(null);
  const analyzerRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<AudioNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const smoothedAmplitudeRef = useRef(0);
  const smoothedFrequencyRef = useRef(0);

  // Initialize Web Audio API
  const initAudioContext = useCallback(() => {
    if (contextRef.current) return;

    try {
      const audioContext =
        new (window.AudioContext || (window as any).webkitAudioContext)();
      contextRef.current = audioContext;

      const analyzer = audioContext.createAnalyser();
      analyzer.fftSize = fftSize;
      analyzer.minDecibels = minDecibels;
      analyzer.maxDecibels = maxDecibels;

      analyzerRef.current = analyzer;
      dataArrayRef.current = new Uint8Array(analyzer.frequencyBinCount);
    } catch (error) {
      console.error('Failed to initialize Web Audio API:', error);
    }
  }, [fftSize, minDecibels, maxDecibels]);

  // Connect to audio element or microphone
  const connectToSource = useCallback((source: AudioNode) => {
    initAudioContext();
    if (analyzerRef.current && source) {
      source.connect(analyzerRef.current);
      sourceRef.current = source;
    }
  }, [initAudioContext]);

  // Get audio from audio element
  const connectToAudioElement = useCallback((audioElement: HTMLAudioElement) => {
    initAudioContext();
    if (!contextRef.current || !analyzerRef.current) return;

    try {
      const source = contextRef.current.createMediaElementAudioSource(audioElement);
      connectToSource(source);
    } catch (error) {
      console.error('Failed to connect to audio element:', error);
    }
  }, [initAudioContext, connectToSource]);

  // Get audio from microphone
  const connectToMicrophone = useCallback(async () => {
    initAudioContext();
    if (!contextRef.current || !analyzerRef.current) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = contextRef.current.createMediaStreamAudioSource(stream);
      connectToSource(source);
    } catch (error) {
      console.error('Failed to access microphone:', error);
    }
  }, [initAudioContext, connectToSource]);

  // Update audio data from analyzer
  const updateAudioData = useCallback(() => {
    if (!analyzerRef.current || !dataArrayRef.current || !enabled) return;

    const dataArray = dataArrayRef.current;
    analyzerRef.current.getByteFrequencyData(dataArray);

    // Calculate amplitude (average frequency value)
    const sum = dataArray.reduce((a, b) => a + b, 0);
    const amplitude = sum / dataArray.length / 255; // Normalize to 0-1

    // Find dominant frequency
    let maxValue = 0;
    let maxIndex = 0;
    for (let i = 0; i < dataArray.length; i++) {
      if (dataArray[i] > maxValue) {
        maxValue = dataArray[i];
        maxIndex = i;
      }
    }
    const frequency = maxIndex / dataArray.length;

    // Calculate RMS energy
    let rmsSum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      const normalized = dataArray[i] / 255;
      rmsSum += normalized * normalized;
    }
    const rms = Math.sqrt(rmsSum / dataArray.length);

    // Apply smoothing to avoid jitter
    smoothedAmplitudeRef.current =
      smoothedAmplitudeRef.current * smoothing + amplitude * (1 - smoothing);
    smoothedFrequencyRef.current =
      smoothedFrequencyRef.current * smoothing + frequency * (1 - smoothing);

    setAudioData({
      amplitude: smoothedAmplitudeRef.current,
      frequency: smoothedFrequencyRef.current,
      frequencies: Array.from(dataArray).map((v) => v / 255),
      rms,
      isPlaying:
        contextRef.current?.state === 'running' &&
        smoothedAmplitudeRef.current > 0.01,
    });

    if (enabled) {
      animationFrameRef.current = requestAnimationFrame(updateAudioData);
    }
  }, [enabled, smoothing]);

  // Start animation loop
  useEffect(() => {
    if (enabled) {
      initAudioContext();
      updateAudioData();
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [enabled, initAudioContext, updateAudioData]);

  return {
    ...audioData,
    connectToAudioElement,
    connectToMicrophone,
    connectToSource,
  } as AudioReactiveData & {
    connectToAudioElement: typeof connectToAudioElement;
    connectToMicrophone: typeof connectToMicrophone;
    connectToSource: typeof connectToSource;
  };
};

/**
 * Hook to create frequency spectrum visualization data
 * Returns frequency bins for bar chart style visualizations
 */
export const useFrequencySpectrum = (
  audioData: AudioReactiveData,
  barCount: number = 32
) => {
  const [spectrum, setSpectrum] = useState<number[]>(
    new Array(barCount).fill(0)
  );

  useEffect(() => {
    if (!audioData.frequencies || audioData.frequencies.length === 0) return;

    const binsPerBar = Math.floor(audioData.frequencies.length / barCount);
    const newSpectrum = new Array(barCount);

    for (let i = 0; i < barCount; i++) {
      let sum = 0;
      for (let j = 0; j < binsPerBar; j++) {
        const index = i * binsPerBar + j;
        sum += audioData.frequencies[index] || 0;
      }
      newSpectrum[i] = sum / binsPerBar;
    }

    setSpectrum(newSpectrum);
  }, [audioData.frequencies, barCount]);

  return spectrum;
};

/**
 * Hook for peak detection (hit detection)
 * Detects sudden amplitude spikes for impact animations
 */
export const useAudioPeakDetection = (
  audioData: AudioReactiveData,
  threshold: number = 0.6,
  decayRate: number = 0.95
) => {
  const [isPeak, setIsPeak] = useState(false);
  const lastValueRef = useRef(0);
  const peakTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const delta = audioData.amplitude - lastValueRef.current;
    const isPeakNow = delta > threshold && audioData.amplitude > 0.3;

    if (isPeakNow && !isPeak) {
      setIsPeak(true);

      if (peakTimeoutRef.current) {
        clearTimeout(peakTimeoutRef.current);
      }

      peakTimeoutRef.current = setTimeout(() => {
        setIsPeak(false);
      }, 150);
    }

    lastValueRef.current = audioData.amplitude * decayRate;

    return () => {
      if (peakTimeoutRef.current) {
        clearTimeout(peakTimeoutRef.current);
      }
    };
  }, [audioData.amplitude, isPeak, threshold, decayRate]);

  return isPeak;
};

/**
 * Hook for beat detection using amplitude threshold
 * Detects when audio crosses a beat threshold
 */
export const useAudioBeatDetection = (
  audioData: AudioReactiveData,
  beatThreshold: number = 0.7,
  beatCooldown: number = 200
) => {
  const [beat, setBeat] = useState(false);
  const lastBeatTimeRef = useRef(0);
  const beatTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const now = Date.now();
    const timeSinceLastBeat = now - lastBeatTimeRef.current;

    if (
      audioData.amplitude > beatThreshold &&
      timeSinceLastBeat > beatCooldown
    ) {
      setBeat(true);
      lastBeatTimeRef.current = now;

      if (beatTimeoutRef.current) {
        clearTimeout(beatTimeoutRef.current);
      }

      beatTimeoutRef.current = setTimeout(() => {
        setBeat(false);
      }, 100);
    }

    return () => {
      if (beatTimeoutRef.current) {
        clearTimeout(beatTimeoutRef.current);
      }
    };
  }, [audioData.amplitude, beatThreshold, beatCooldown]);

  return beat;
};

export default useAudioReactive;
