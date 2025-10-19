// Type definitions for Web Audio API
declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
  }

  interface AudioContext extends BaseAudioContext {
    readonly baseLatency: number;
    close(): Promise<void>;
    createMediaElementSource(element: HTMLMediaElement): MediaElementAudioSourceNode;
    createMediaStreamDestination(): MediaStreamAudioDestinationNode;
    createMediaStreamSource(stream: MediaStream): MediaStreamAudioSourceNode;
    getOutputTimestamp(): AudioTimestamp;
    resume(): Promise<void>;
    suspend(): Promise<void>;
  }

  interface AudioContextOptions {
    latencyHint?: AudioContextLatencyCategory | number;
    sampleRate?: number;
  }

  interface AudioTimestamp {
    contextTime: number;
    performanceTime: number;
  }

  interface MediaElementAudioSourceNode extends AudioNode {
    mediaElement: HTMLMediaElement;
  }

  interface MediaStreamAudioDestinationNode extends AudioNode {
    stream: MediaStream;
  }

  interface MediaStreamAudioSourceNode extends AudioNode {
    mediaStream: MediaStream;
  }

  // Animation frame types
  type FrameRequestCallback = (time: number) => void;
  function requestAnimationFrame(callback: FrameRequestCallback): number;
  function cancelAnimationFrame(handle: number): void;
}

export {};
