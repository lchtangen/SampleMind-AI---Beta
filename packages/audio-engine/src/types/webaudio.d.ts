// Type definitions for Web Audio API
declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
    webkitMediaRecorder: typeof MediaRecorder;
  }

  // Extend the MediaRecorder interface to include missing properties
  interface MediaRecorder {
    readonly mimeType: string;
    readonly state: 'inactive' | 'recording' | 'paused';
    readonly stream: MediaStream;
    ondataavailable: ((event: BlobEvent) => void) | null;
    onerror: ((event: Event) => void) | null;
    onpause: (() => void) | null;
    onresume: (() => void) | null;
    onstart: (() => void) | null;
    onstop: (() => void) | null;
    pause(): void;
    requestData(): void;
    resume(): void;
    start(timeslice?: number): void;
    stop(): void;
    addEventListener(
      type: string,
      listener: EventListenerOrEventListenerObject,
      options?: boolean | AddEventListenerOptions
    ): void;
    removeEventListener(
      type: string,
      listener: EventListenerOrEventListenerObject,
      options?: boolean | EventListenerOptions
    ): void;
  }

  // Type for the AudioContext with required methods
  interface AudioContextType extends AudioContext {
    createMediaStreamSource(stream: MediaStream): MediaStreamAudioSourceNode;
    createAnalyser(): AnalyserNode;
    close(): Promise<void>;
    state: AudioContextState;
    resume(): Promise<void>;
    suspend(): Promise<void>;
  }
}

export {}; // This file needs to be a module
