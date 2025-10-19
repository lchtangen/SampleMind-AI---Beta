interface UseAudioRecorderReturn {
    isRecording: boolean;
    audioBlob: Blob | null;
    audioUrl: string | null;
    error: string | null;
    audioData: Uint8Array;
    startRecording: () => Promise<void>;
    stopRecording: () => Promise<Blob>;
}
declare global {
    interface Window {
        webkitAudioContext: new (contextOptions?: AudioContextOptions) => AudioContext;
        webkitMediaRecorder: typeof MediaRecorder;
    }
}
declare const AudioContext: {
    new (contextOptions?: AudioContextOptions): AudioContext;
    prototype: AudioContext;
};
declare const MediaRecorder: {
    new (stream: MediaStream, options?: MediaRecorderOptions): MediaRecorder;
    isTypeSupported(type: string): boolean;
};
interface AudioContext extends BaseAudioContext {
    createMediaStreamSource(stream: MediaStream): MediaStreamAudioSourceNode;
    createAnalyser(): AnalyserNode;
    close(): Promise<void>;
    state: AudioContextState;
    resume(): Promise<void>;
    suspend(): Promise<void>;
    sampleRate: number;
}
export declare const useAudioRecorder: () => UseAudioRecorderReturn;
export {};
//# sourceMappingURL=useAudioRecorder.d.ts.map