import '@tensorflow/tfjs-backend-webgl';
declare global {
    interface Window {
        AudioContext: {
            new (contextOptions?: AudioContextOptions): AudioContext;
            prototype: AudioContext;
        };
        webkitAudioContext: {
            new (contextOptions?: AudioContextOptions): AudioContext;
            prototype: AudioContext;
        };
    }
}
interface AudioContextOptions {
    latencyHint?: 'balanced' | 'interactive' | 'playback';
    sampleRate?: number;
}
type AudioBuffer = {
    sampleRate: number;
    length: number;
    duration: number;
    numberOfChannels: number;
    getChannelData(channel: number): Float32Array;
    copyFromChannel(destination: Float32Array, channelNumber: number, startInChannel?: number): void;
    copyToChannel(source: Float32Array, channelNumber: number, startInChannel?: number): void;
};
import { NeurologicAudioEngine } from '../core/NeurologicAudioEngine';
/**
 * AudioNeuralNetwork - Handles all neural network operations for audio analysis
 */
export declare class AudioNeuralNetwork {
    private audioEngine?;
    private model;
    private isInitialized;
    private readonly config;
    constructor(audioEngine?: NeurologicAudioEngine | undefined);
    /**
     * Initialize the neural network
     */
    initialize(): Promise<void>;
    /**
     * Analyze audio features using the neural network
     */
    analyzeAudioFeatures(audioBuffer: AudioBuffer): Promise<AudioAnalysisResult>;
    /**
     * Extract features from audio buffer
     */
    private extractFeatures;
    /**
     * Compute STFT of audio signal
     */
    private computeSTFT;
    /**
     * Convert power spectrum to Mel spectrogram
     */
    private computeMelSpectrogram;
    /**
     * Create Mel filter bank
     */
    private createMelFilterbank;
    /**
     * Convert Hz to Mel
     */
    private hzToMel;
    /**
     * Convert Mel to Hz
     */
    private melToHz;
    /**
     * Process model predictions
     */
    private processPredictions;
    /**
     * Safely get a value from the predictions array
     */
    private safeGet;
    /**
     * Clean up resources
     */
    dispose(): void;
}
/**
 * Audio analysis result
 */
export interface AudioAnalysisResult {
    bpm: number;
    key: number;
    scale: number;
    energy: number;
    danceability: number;
    valence: number;
    arousal: number;
}
export {};
//# sourceMappingURL=AudioNeuralNetwork.d.ts.map