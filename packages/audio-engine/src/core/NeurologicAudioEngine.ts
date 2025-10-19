import { EventEmitter } from 'events';
import * as Tone from 'tone';

/**
 * NeurologicAudioEngine - Core audio processing engine for SampleMind AI
 * Implements bio-inspired signal processing based on neural oscillation patterns
 */
export class NeurologicAudioEngine extends EventEmitter {
  private context: AudioContext;
  private analyser: AnalyserNode;
  private processor: ScriptProcessorNode | null = null;
  private source: AudioBufferSourceNode | null = null;
  private isPlaying: boolean = false;
  
  // Neural oscillation bands (in Hz)
  public readonly neuralBands = {
    delta: { min: 0.5, max: 4 },     // Deep bass, sub-bass
    theta: { min: 4, max: 8 },       // Bass fundamentals
    alpha: { min: 8, max: 13 },      // Low-mid frequencies
    beta: { min: 13, max: 30 },      // Mid-high frequencies
    gamma: { min: 30, max: 100 },    // High frequencies, transients
    ultra: { min: 100, max: 500 }    // Ultra-high, harmonics
  };

  constructor() {
    super();
    this.context = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.analyser = this.context.createAnalyser();
    this.analyser.fftSize = 2048;
  }

  /**
   * Initialize the audio engine
   */
  public async initialize(): Promise<void> {
    try {
      // Set up audio processing
      this.processor = this.context.createScriptProcessor(4096, 1, 1);
      this.processor.connect(this.context.destination);
      
      // Set up analyzer
      this.analyser.connect(this.context.destination);
      
      this.emit('initialized');
    } catch (error) {
      console.error('Error initializing audio engine:', error);
      throw error;
    }
  }

  /**
   * Load audio from various sources
   */
  public async loadAudio(source: string | ArrayBuffer | AudioBuffer): Promise<AudioBuffer> {
    try {
      let audioBuffer: AudioBuffer;
      
      if (source instanceof AudioBuffer) {
        audioBuffer = source;
      } else if (source instanceof ArrayBuffer) {
        audioBuffer = await this.context.decodeAudioData(source);
      } else if (typeof source === 'string') {
        const response = await fetch(source);
        const arrayBuffer = await response.arrayBuffer();
        audioBuffer = await this.context.decodeAudioData(arrayBuffer);
      } else {
        throw new Error('Unsupported audio source type');
      }
      
      this.emit('audioLoaded', audioBuffer);
      return audioBuffer;
    } catch (error) {
      console.error('Error loading audio:', error);
      throw error;
    }
  }

  /**
   * Play loaded audio
   */
  public play(buffer: AudioBuffer): void {
    if (this.isPlaying) {
      this.stop();
    }

    this.source = this.context.createBufferSource();
    this.source.buffer = buffer;
    this.source.connect(this.analyser);
    this.source.connect(this.context.destination);
    
    this.source.onended = () => {
      this.isPlaying = false;
      this.emit('playbackEnded');
    };
    
    this.source.start(0);
    this.isPlaying = true;
    this.emit('playbackStarted');
  }

  /**
   * Stop audio playback
   */
  public stop(): void {
    if (this.source) {
      this.source.stop();
      this.source.disconnect();
      this.source = null;
    }
    this.isPlaying = false;
    this.emit('playbackStopped');
  }

  /**
   * Get frequency data for visualization
   */
  public getFrequencyData(): Uint8Array {
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);
    return dataArray;
  }

  /**
   * Get time domain data for visualization
   */
  public getTimeDomainData(): Uint8Array {
    const bufferLength = this.analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteTimeDomainData(dataArray);
    return dataArray;
  }

  /**
   * Analyze audio for neural patterns
   */
  public analyzeNeuralPatterns(): Record<string, number> {
    const frequencyData = this.getFrequencyData();
    const sampleRate = this.context.sampleRate;
    const results: Record<string, number> = {};
    
    // Calculate energy in each neural band
    Object.entries(this.neuralBands).forEach(([band, { min, max }]) => {
      const startIndex = Math.floor((min / (sampleRate / 2)) * frequencyData.length);
      const endIndex = Math.min(
        Math.ceil((max / (sampleRate / 2)) * frequencyData.length),
        frequencyData.length - 1
      );
      
      let sum = 0;
      for (let i = startIndex; i <= endIndex; i++) {
        sum += frequencyData[i];
      }
      
      results[band] = sum / (endIndex - startIndex + 1);
    });
    
    return results;
  }

  /**
   * Clean up resources
   */
  public dispose(): void {
    this.stop();
    
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    
    this.analyser.disconnect();
    
    if (this.context.state !== 'closed') {
      this.context.close();
    }
    
    this.removeAllListeners();
  }
}
