import { EventEmitter } from 'events';
/**
 * NeurologicAudioEngine - Core audio processing engine for SampleMind AI
 * Implements bio-inspired signal processing based on neural oscillation patterns
 */
export declare class NeurologicAudioEngine extends EventEmitter {
    private context;
    private analyser;
    private processor;
    private source;
    private isPlaying;
    readonly neuralBands: {
        delta: {
            min: number;
            max: number;
        };
        theta: {
            min: number;
            max: number;
        };
        alpha: {
            min: number;
            max: number;
        };
        beta: {
            min: number;
            max: number;
        };
        gamma: {
            min: number;
            max: number;
        };
        ultra: {
            min: number;
            max: number;
        };
    };
    constructor();
    /**
     * Initialize the audio engine
     */
    initialize(): Promise<void>;
    /**
     * Load audio from various sources
     */
    loadAudio(source: string | ArrayBuffer | AudioBuffer): Promise<AudioBuffer>;
    /**
     * Play loaded audio
     */
    play(buffer: AudioBuffer): void;
    /**
     * Stop audio playback
     */
    stop(): void;
    /**
     * Get frequency data for visualization
     */
    getFrequencyData(): Uint8Array;
    /**
     * Get time domain data for visualization
     */
    getTimeDomainData(): Uint8Array;
    /**
     * Analyze audio for neural patterns
     */
    analyzeNeuralPatterns(): Record<string, number>;
    /**
     * Clean up resources
     */
    dispose(): void;
}
//# sourceMappingURL=NeurologicAudioEngine.d.ts.map