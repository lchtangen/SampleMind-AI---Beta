import { NeuroplasticLearning } from '../core/NeuroplasticLearning';
export declare const useAudioLearning: () => {
    isInitialized: boolean;
    isPlaying: any;
    isLearning: boolean;
    error: string | null;
    toggleAudio: () => Promise<void>;
    getStyleVector: () => Promise<number | number[] | number[][] | number[][][] | number[][][][] | number[][][][][] | number[][][][][][] | null>;
    predictNextPattern: () => Promise<{
        bpm: number;
        key: string;
        scale: string;
        timbreProfile: number[];
        rhythmPattern: number[];
    } | null>;
    audioEngine: any;
    learningEngine: NeuroplasticLearning | null;
};
export default useAudioLearning;
//# sourceMappingURL=useAudioLearning.d.ts.map