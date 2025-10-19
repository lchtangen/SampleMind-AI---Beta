/// <reference types="@types/node" />
/// <reference types="@types/react" />
/// <reference types="@types/react-dom" />

// Extend the Window interface
declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
  }

  // Extend HTMLAudioElement with missing properties
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

  // Extend HTMLInputElement for form controls
  interface HTMLInputElement {
    value: string;
    valueAsNumber: number;
    checked: boolean;
    files: FileList | null;
  }

  // Web Audio API types
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

  // Navigator media devices
  interface Navigator {
    mediaDevices: MediaDevices;
  }

  interface MediaDevices extends EventTarget {
    getUserMedia(constraints: MediaStreamConstraints): Promise<MediaStream>;
    enumerateDevices(): Promise<MediaDeviceInfo[]>;
  }

  interface MediaStreamConstraints {
    audio?: boolean | MediaTrackConstraints;
    video?: boolean | MediaTrackConstraints;
  }

  interface MediaTrackConstraints extends MediaTrackConstraintSet {
    advanced?: MediaTrackConstraintSet[];
  }

  interface MediaTrackConstraintSet {
    deviceId?: ConstrainDOMString;
    groupId?: ConstrainDOMString;
    autoGainControl?: ConstrainBoolean;
    echoCancellation?: ConstrainBoolean;
    noiseSuppression?: ConstrainBoolean;
    sampleRate?: ConstrainULong;
    sampleSize?: ConstrainULong;
    latency?: ConstrainDouble;
    channelCount?: ConstrainULong;
  }

  type ConstrainBoolean = boolean | ConstrainBooleanParameters;
  type ConstrainDOMString = string | string[] | ConstrainDOMStringParameters;
  type ConstrainDouble = number | ConstrainDoubleRange;
  type ConstrainULong = number | ConstrainULongRange;

  interface ConstrainBooleanParameters {
    exact?: boolean;
    ideal?: boolean;
  }

  interface ConstrainDOMStringParameters {
    exact?: string | string[];
    ideal?: string | string[];
  }

  interface ConstrainDoubleRange extends DoubleRange {
    exact?: number;
    ideal?: number;
  }

  interface ConstrainULongRange extends ULongRange {
    exact?: number;
    ideal?: number;
  }

  interface DoubleRange {
    max?: number;
    min?: number;
  }

  interface ULongRange {
    max?: number;
    min?: number;
  }

  interface MediaDeviceInfo {
    readonly deviceId: string;
    readonly groupId: string;
    readonly kind: MediaDeviceKind;
    readonly label: string;
    toJSON(): any;
  }

  type MediaDeviceKind = 'audioinput' | 'audiooutput' | 'videoinput';

  // For React event handlers
  interface ChangeEvent<T = Element> extends SyntheticEvent<T> {
    target: EventTarget & T;
  }
}

export {};
