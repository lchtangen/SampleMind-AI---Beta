interface Window {
  webkitAudioContext: typeof AudioContext;
  webkitMediaRecorder: typeof MediaRecorder;
}

interface MediaRecorderOptions {
  mimeType?: string;
  audioBitsPerSecond?: number;
  videoBitsPerSecond?: number;
  bitsPerSecond?: number;
}

interface MediaRecorderEventMap {
  dataavailable: BlobEvent;
  error: Event;
  pause: Event;
  resume: Event;
  start: Event;
  stop: Event;
  warning: Event;
}

declare class MediaRecorder extends EventTarget {
  readonly mimeType: string;
  readonly state: 'inactive' | 'recording' | 'paused';
  readonly stream: MediaStream;
  ignoreMutedMedia: boolean;
  videoBitsPerSecond: number;
  audioBitsPerSecond: number;

  constructor(stream: MediaStream, options?: MediaRecorderOptions);

  start(timeslice?: number): void;
  stop(): void;
  pause(): void;
  resume(): void;
  requestData(): Blob;

  ondataavailable: ((event: BlobEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  onpause: (() => void) | null;
  onresume: (() => void) | null;
  onstart: (() => void) | null;
  onstop: (() => void) | null;

  addEventListener<K extends keyof MediaRecorderEventMap>(
    type: K,
    listener: (this: MediaRecorder, ev: MediaRecorderEventMap[K]) => any,
    options?: boolean | AddEventListenerOptions
  ): void;
  addEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | AddEventListenerOptions
  ): void;
  removeEventListener<K extends keyof MediaRecorderEventMap>(
    type: K,
    listener: (this: MediaRecorder, ev: MediaRecorderEventMap[K]) => any,
    options?: boolean | EventListenerOptions
  ): void;
  removeEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | EventListenerOptions
  ): void;
}

declare var MediaRecorder: {
  prototype: MediaRecorder;
  new(stream: MediaStream, options?: MediaRecorderOptions): MediaRecorder;
  isTypeSupported(mimeType: string): boolean;
};

// Web Audio API types
interface AudioContextOptions {
  latencyHint?: AudioContextLatencyCategory | number;
  sampleRate?: number;
}

interface AudioContext extends BaseAudioContext {
  readonly baseLatency: number;
  readonly outputLatency: number;
  close(): Promise<void>;
  createMediaStreamDestination(): MediaStreamAudioDestinationNode;
  createMediaStreamSource(stream: MediaStream): MediaStreamAudioSourceNode;
  getOutputTimestamp(): AudioTimestamp;
  resume(): Promise<void>;
  suspend(): Promise<void>;
  readonly audioWorklet?: AudioWorklet;
}

interface AudioWorklet extends Worklet {}

interface AudioWorkletNode extends AudioNode {
  readonly port: MessagePort;
  onprocessorerror: ((this: AudioWorkletNode, event: Event) => any) | null;
  addEventListener(
    type: 'processorerror',
    listener: (this: AudioWorkletNode, event: Event) => any,
    options?: boolean | AddEventListenerOptions
  ): void;
  removeEventListener(
    type: 'processorerror',
    callback: (this: AudioWorkletNode, event: Event) => any,
    options?: EventListenerOptions | boolean
  ): void;
}

interface AudioTimestamp {
  contextTime: number;
  performanceTime: number;
}

// Add missing types for Web Audio API
interface AudioBufferSourceNode extends AudioScheduledSourceNode {
  buffer: AudioBuffer | null;
  detune: AudioParam;
  loop: boolean;
  loopEnd: number;
  loopStart: number;
  playbackRate: AudioParam;
  start(when?: number, offset?: number, duration?: number): void;
  stop(when?: number): void;
}

interface AudioScheduledSourceNode extends AudioNode {
  onended: ((this: AudioScheduledSourceNode, ev: Event) => any) | null;
  start(when?: number): void;
  stop(when?: number): void;
  addEventListener(
    type: 'ended',
    listener: (this: AudioScheduledSourceNode, ev: Event) => any,
    options?: boolean | AddEventListenerOptions
  ): void;
  removeEventListener(
    type: 'ended',
    callback: (this: AudioScheduledSourceNode, ev: Event) => any,
    options?: EventListenerOptions | boolean
  ): void;
}

interface AudioBuffer {
  readonly duration: number;
  readonly length: number;
  readonly numberOfChannels: number;
  readonly sampleRate: number;
  copyFromChannel(
    destination: Float32Array,
    channelNumber: number,
    startInChannel?: number
  ): void;
  copyToChannel(
    source: Float32Array,
    channelNumber: number,
    startInChannel?: number
  ): void;
  getChannelData(channel: number): Float32Array;
}

interface AudioParam {
  defaultValue: number;
  readonly maxValue: number;
  readonly minValue: number;
  value: number;
  cancelAndHoldAtTime(cancelTime: number): AudioParam;
  cancelScheduledValues(cancelTime: number): AudioParam;
  exponentialRampToValueAtTime(value: number, endTime: number): AudioParam;
  linearRampToValueAtTime(value: number, endTime: number): AudioParam;
  setTargetAtTime(
    target: number,
    startTime: number,
    timeConstant: number
  ): AudioParam;
  setValueAtTime(value: number, startTime: number): AudioParam;
  setValueCurveAtTime(
    values: Float32Array | number[],
    startTime: number,
    duration: number
  ): AudioParam;
}

interface AudioNode extends EventTarget {
  readonly context: BaseAudioContext;
  readonly numberOfInputs: number;
  readonly numberOfOutputs: number;
  channelCount: number;
  channelCountMode: ChannelCountMode;
  channelInterpretation: ChannelInterpretation;
  connect(destinationNode: AudioNode, output?: number, input?: number): AudioNode;
  connect(destinationParam: AudioParam, output?: number): void;
  disconnect(): void;
  disconnect(output: number): void;
  disconnect(destinationNode: AudioNode): void;
  disconnect(destinationNode: AudioNode, output: number): void;
  disconnect(destinationNode: AudioNode, output: number, input: number): void;
  disconnect(destinationParam: AudioParam): void;
  disconnect(destinationParam: AudioParam, output: number): void;
}

type ChannelCountMode = 'max' | 'clamped-max' | 'explicit';
type ChannelInterpretation = 'speakers' | 'discrete';

interface BaseAudioContext extends EventTarget {
  readonly audioWorklet?: AudioWorklet;
  readonly currentTime: number;
  readonly destination: AudioDestinationNode;
  readonly listener: AudioListener;
  readonly sampleRate: number;
  readonly state: AudioContextState;
  onstatechange: ((this: BaseAudioContext, ev: Event) => any) | null;
  createAnalyser(): AnalyserNode;
  createBiquadFilter(): BiquadFilterNode;
  createBuffer(
    numberOfChannels: number,
    length: number,
    sampleRate: number
  ): AudioBuffer;
  createBufferSource(): AudioBufferSourceNode;
  createChannelMerger(numberOfInputs?: number): ChannelMergerNode;
  createChannelSplitter(numberOfOutputs?: number): ChannelSplitterNode;
  createConstantSource(): ConstantSourceNode;
  createDelay(maxDelayTime?: number): DelayNode;
  createGain(): GainNode;
  createIIRFilter(feedforward: number[], feedback: number[]): IIRFilterNode;
  createOscillator(): OscillatorNode;
  createPanner(): PannerNode;
  createPeriodicWave(
    real: Float32Array,
    imag: Float32Array,
    constraints?: PeriodicWaveConstraints
  ): PeriodicWave;
  createScriptProcessor(
    bufferSize?: number,
    numberOfInputChannels?: number,
    numberOfOutputChannels?: number
  ): ScriptProcessorNode;
  createStereoPanner(): StereoPannerNode;
  createWaveShaper(): WaveShaperNode;
  decodeAudioData(
    audioData: ArrayBuffer,
    successCallback?: DecodeSuccessCallback,
    errorCallback?: DecodeErrorCallback
  ): Promise<AudioBuffer>;
  resume(): Promise<void>;
  suspend(): Promise<void>;
  close(): Promise<void>;
}

type AudioContextState = 'suspended' | 'running' | 'closed';

type DecodeSuccessCallback = (decodedData: AudioBuffer) => void;
type DecodeErrorCallback = (error: DOMException) => void;

interface AudioDestinationNode extends AudioNode {
  readonly maxChannelCount: number;
}

interface AudioListener {
  forwardX: AudioParam;
  forwardY: AudioParam;
  forwardZ: AudioParam;
  positionX: AudioParam;
  positionY: AudioParam;
  positionZ: AudioParam;
  upX: AudioParam;
  upY: AudioParam;
  upZ: AudioParam;
  setOrientation(
    x: number,
    y: number,
    z: number,
    xUp: number,
    yUp: number,
    zUp: number
  ): void;
  setPosition(x: number, y: number, z: number): void;
}

interface AnalyserNode extends AudioNode {
  fftSize: number;
  frequencyBinCount: number;
  maxDecibels: number;
  minDecibels: number;
  smoothingTimeConstant: number;
  getByteFrequencyData(array: Uint8Array): void;
  getByteTimeDomainData(array: Uint8Array): void;
  getFloatFrequencyData(array: Float32Array): void;
  getFloatTimeDomainData(array: Float32Array): void;
}

// Add missing event types
declare class BlobEvent extends Event {
  constructor(type: string, eventInitDict: BlobEventInit);
  readonly data: Blob;
  readonly timecode: DOMHighResTimeStamp;
}

interface BlobEventInit extends EventInit {
  data: Blob;
  timecode?: DOMHighResTimeStamp;
}

// Add MediaStream types
interface MediaStreamTrack extends EventTarget {
  readonly enabled: boolean;
  readonly id: string;
  readonly kind: string;
  readonly label: string;
  readonly muted: boolean;
  readonly readyState: MediaStreamTrackState;
  readonly remote: boolean;
  onended: ((this: MediaStreamTrack, ev: Event) => any) | null;
  onmute: ((this: MediaStreamTrack, ev: Event) => any) | null;
  onunmute: ((this: MediaStreamTrack, ev: Event) => any) | null;
  clone(): MediaStreamTrack;
  getCapabilities(): MediaTrackCapabilities;
  getConstraints(): MediaTrackConstraints;
  getSettings(): MediaTrackSettings;
  applyConstraints(constraints?: MediaTrackConstraints): Promise<void>;
  stop(): void;
  addEventListener(
    type: string,
    listener: EventListenerOrEventListenerObject | null,
    options?: boolean | AddEventListenerOptions
  ): void;
  removeEventListener(
    type: string,
    callback: EventListenerOrEventListenerObject | null,
    options?: EventListenerOptions | boolean
  ): void;
}

type MediaStreamTrackState = 'live' | 'ended';

interface MediaTrackCapabilities {
  width?: { min: number; max: number };
  height?: { min: number; max: number };
  aspectRatio?: { min: number; max: number };
  frameRate?: { min: number; max: number };
  facingMode?: string[];
  resizeMode?: string[];
  sampleRate?: { min: number; max: number };
  sampleSize?: { min: number; max: number };
  echoCancellation?: boolean[];
  autoGainControl?: boolean[];
  noiseSuppression?: boolean[];
  latency?: { min: number; max: number };
  channelCount?: { min: number; max: number };
  deviceId?: string;
  groupId?: string;
}

interface MediaTrackConstraints extends MediaTrackConstraintSet {
  advanced?: MediaTrackConstraintSet[];
}

interface MediaTrackConstraintSet {
  width?: ConstrainULong;
  height?: ConstrainULong;
  aspectRatio?: ConstrainDouble;
  frameRate?: ConstrainDouble;
  facingMode?: ConstrainDOMString;
  resizeMode?: ConstrainDOMString;
  volume?: ConstrainDouble;
  sampleRate?: ConstrainULong;
  sampleSize?: ConstrainULong;
  echoCancellation?: ConstrainBoolean;
  autoGainControl?: ConstrainBoolean;
  noiseSuppression?: ConstrainBoolean;
  latency?: ConstrainDouble;
  channelCount?: ConstrainULong;
  deviceId?: ConstrainDOMString;
  groupId?: ConstrainDOMString;
}

type ConstrainBoolean = boolean | { exact?: boolean; ideal?: boolean };
type ConstrainDOMString = string | string[] | { exact?: string | string[]; ideal?: string | string[] };
type ConstrainDouble = number | { exact?: number; ideal?: number; min?: number; max?: number };
type ConstrainULong = number | { exact?: number; ideal?: number; min?: number; max?: number };

interface MediaTrackSettings {
  width?: number;
  height?: number;
  aspectRatio?: number;
  frameRate?: number;
  facingMode?: string;
  resizeMode?: string;
  volume?: number;
  sampleRate?: number;
  sampleSize?: number;
  echoCancellation?: boolean;
  autoGainControl?: boolean;
  noiseSuppression?: boolean;
  latency?: number;
  channelCount?: number;
  deviceId?: string;
  groupId?: string;
}

// Add MediaStream interface
declare class MediaStream extends EventTarget {
  constructor();
  constructor(stream: MediaStream);
  constructor(tracks: MediaStreamTrack[]);
  readonly active: boolean;
  readonly id: string;
  onaddtrack: ((this: MediaStream, ev: MediaStreamTrackEvent) => any) | null;
  onremovetrack: ((this: MediaStream, ev: MediaStreamTrackEvent) => any) | null;
  addTrack(track: MediaStreamTrack): void;
  clone(): MediaStream;
  getAudioTracks(): MediaStreamTrack[];
  getTrackById(trackId: string): MediaStreamTrack | null;
  getTracks(): MediaStreamTrack[];
  getVideoTracks(): MediaStreamTrack[];
  removeTrack(track: MediaStreamTrack): void;
  addEventListener(
    type: 'addtrack' | 'removetrack',
    listener: (this: MediaStream, ev: MediaStreamTrackEvent) => any,
    options?: boolean | AddEventListenerOptions
  ): void;
  removeEventListener(
    type: 'addtrack' | 'removetrack',
    callback: (this: MediaStream, ev: MediaStreamTrackEvent) => any,
    options?: EventListenerOptions | boolean
  ): void;
}

interface MediaStreamTrackEvent extends Event {
  readonly track: MediaStreamTrack;
}

// Add MediaStreamConstraints interface
interface MediaStreamConstraints {
  video?: boolean | MediaTrackConstraints;
  audio?: boolean | MediaTrackConstraints;
  peerIdentity?: string;
}

// Add MediaDevices interface
interface MediaDevices extends EventTarget {
  ondevicechange: ((this: MediaDevices, ev: Event) => any) | null;
  enumerateDevices(): Promise<MediaDeviceInfo[]>;
  getSupportedConstraints(): MediaTrackSupportedConstraints;
  getUserMedia(constraints?: MediaStreamConstraints): Promise<MediaStream>;
  getDisplayMedia(constraints?: MediaStreamConstraints): Promise<MediaStream>;
  addEventListener(
    type: 'devicechange',
    listener: (this: MediaDevices, ev: Event) => any,
    options?: boolean | AddEventListenerOptions
  ): void;
  removeEventListener(
    type: 'devicechange',
    callback: (this: MediaDevices, ev: Event) => any,
    options?: EventListenerOptions | boolean
  ): void;
}

interface MediaDeviceInfo {
  readonly deviceId: string;
  readonly groupId: string;
  readonly kind: 'audioinput' | 'audiooutput' | 'videoinput';
  readonly label: string;
  toJSON(): any;
}

interface MediaTrackSupportedConstraints {
  width?: boolean;
  height?: boolean;
  aspectRatio?: boolean;
  frameRate?: boolean;
  facingMode?: boolean;
  resizeMode?: boolean;
  volume?: boolean;
  sampleRate?: boolean;
  sampleSize?: boolean;
  echoCancellation?: boolean;
  autoGainControl?: boolean;
  noiseSuppression?: boolean;
  latency?: boolean;
  channelCount?: boolean;
  deviceId?: boolean;
  groupId?: boolean;
}

// Add to Window interface
declare var MediaRecorder: {
  prototype: MediaRecorder;
  new(stream: MediaStream, options?: MediaRecorderOptions): MediaRecorder;
  isTypeSupported(mimeType: string): boolean;
};

declare var AudioContext: {
  prototype: AudioContext;
  new(contextOptions?: AudioContextOptions): AudioContext;
};

declare var webkitAudioContext: {
  prototype: AudioContext;
  new(contextOptions?: AudioContextOptions): AudioContext;
};

// Add to global scope
declare const navigator: Navigator & {
  mediaDevices: MediaDevices;
  webkitGetUserMedia?: (
    constraints: MediaStreamConstraints,
    success: (stream: MediaStream) => void,
    error: (error: Error) => void
  ) => void;
  mozGetUserMedia?: (
    constraints: MediaStreamConstraints,
    success: (stream: MediaStream) => void,
    error: (error: Error) => void
  ) => void;
  msGetUserMedia?: (
    constraints: MediaStreamConstraints,
    success: (stream: MediaStream) => void,
    error: (error: Error) => void
  ) => void;
};

// Add URL.createObjectURL
declare var URL: {
  createObjectURL(blob: Blob): string;
  revokeObjectURL(url: string): void;
};

// Add missing types for requestAnimationFrame
declare function requestAnimationFrame(callback: FrameRequestCallback): number;
declare function cancelAnimationFrame(handle: number): void;

type FrameRequestCallback = (time: number) => void;
