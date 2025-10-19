// Type definitions for Web Audio API
interface Window {
  AudioContext: typeof AudioContext;
  webkitAudioContext: typeof AudioContext;
}

// Extend the standard AudioContext interface if needed
interface AudioContext {
  // Add any AudioContext extensions here if needed
}

// Extend HTMLAudioElement to include the missing properties
interface HTMLAudioElement {
  volume: number;
  muted: boolean;
  currentTime: number;
  duration: number;
  play(): Promise<void>;
  pause(): void;
  addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void;
  removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void;
}

// For requestAnimationFrame and cancelAnimationFrame
declare function requestAnimationFrame(callback: FrameRequestCallback): number;
declare function cancelAnimationFrame(handle: number): void;

export {};
