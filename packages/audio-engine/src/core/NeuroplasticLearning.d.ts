import { EventEmitter } from 'events';
interface LearningPattern {
    bpm: number;
    key: string;
    scale: string;
    timbreProfile: number[];
    rhythmPattern: number[];
    timestamp: number;
}
/**
 * NeuroplasticLearning - AI system that adapts to producer's style through neuroplasticity principles
 */
export declare class NeuroplasticLearning extends EventEmitter {
    private model;
    private learningRate;
    private memoryWindow;
    private memory;
    private isTraining;
    constructor();
    private initializeModel;
    /**
     * Add a new pattern to the learning memory
     */
    addPattern(pattern: Omit<LearningPattern, 'timestamp'>): void;
    /**
     * Train the model on the current memory
     */
    private trainModel;
    /**
     * Predict the next pattern based on current style
     */
    predictNextPattern(currentPattern: Omit<LearningPattern, 'timestamp'>): Promise<{
        bpm: number;
        key: string;
        scale: string;
        timbreProfile: number[];
        rhythmPattern: number[];
    } | null>;
    /**
     * Get the current style vector
     */
    getStyleVector(): Promise<number | number[] | number[][] | number[][][] | number[][][][] | number[][][][][] | number[][][][][][] | null>;
    /**
     * Reset the learning model
     */
    reset(): void;
}
export default NeuroplasticLearning;
//# sourceMappingURL=NeuroplasticLearning.d.ts.map