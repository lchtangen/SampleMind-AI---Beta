import { NeuroplasticLearning } from '../NeuroplasticLearning';
import * as tf from '@tensorflow/tfjs';
// Mock TensorFlow.js
jest.mock('@tensorflow/tfjs', () => ({
    sequential: jest.fn(),
    train: {
        adam: jest.fn(() => 'adam-optimizer')
    },
    layers: {
        dense: jest.fn(),
        dropout: jest.fn()
    },
    tensor2d: jest.fn(),
    model: jest.fn()
}));
describe('NeuroplasticLearning', () => {
    let learning;
    beforeEach(() => {
        // Reset all mocks
        jest.clearAllMocks();
        // Setup mock model
        const mockFit = jest.fn().mockResolvedValue({});
        const mockPredict = jest.fn().mockReturnValue(tf.tensor2d([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]]));
        tf.sequential.mockReturnValue({
            add: jest.fn(),
            compile: jest.fn(),
            fit: mockFit,
            predict: mockPredict,
            layers: [
                { output: 'mock-output' },
                { output: 'mock-output' },
                { output: 'mock-output' }
            ],
            inputs: ['mock-input']
        });
        tf.model.mockReturnValue({
            predict: mockPredict
        });
        learning = new NeuroplasticLearning();
    });
    describe('initialization', () => {
        it('should initialize with default values', () => {
            expect(learning).toBeInstanceOf(NeuroplasticLearning);
            expect(tf.sequential).toHaveBeenCalled();
        });
    });
    describe('addPattern', () => {
        it('should add a pattern to memory', () => {
            const pattern = {
                bpm: 120,
                key: 'C',
                scale: 'major',
                timbreProfile: [0.1, 0.2, 0.3, 0.4, 0.5],
                rhythmPattern: [1, 0, 1, 0]
            };
            learning.addPattern(pattern);
            // Check if the pattern was added with a timestamp
            const memory = learning.memory;
            expect(memory).toHaveLength(1);
            expect(memory[0]).toMatchObject(pattern);
            expect(memory[0].timestamp).toBeDefined();
        });
        it('should maintain memory window size', () => {
            const pattern = {
                bpm: 120,
                key: 'C',
                scale: 'major',
                timbreProfile: [0.1, 0.2, 0.3, 0.4, 0.5],
                rhythmPattern: [1, 0, 1, 0]
            };
            // Add more patterns than the memory window
            for (let i = 0; i < 150; i++) {
                learning.addPattern({
                    ...pattern,
                    bpm: 120 + i
                });
            }
            const memory = learning.memory;
            expect(memory).toHaveLength(100); // Default window size
            expect(memory[0].bpm).toBe(170); // First item should be the 51st pattern (120 + 50)
            expect(memory[99].bpm).toBe(269); // Last item should be the 150th pattern
        });
    });
    describe('training', () => {
        it('should start training when enough patterns are added', async () => {
            const mockFit = jest.fn().mockResolvedValue({});
            tf.sequential.mockReturnValueOnce({
                add: jest.fn(),
                compile: jest.fn(),
                fit: mockFit,
                predict: jest.fn().mockReturnValue(tf.tensor2d([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]])),
                layers: [
                    { output: 'mock-output' },
                    { output: 'mock-output' },
                    { output: 'mock-output' }
                ],
                inputs: ['mock-input']
            });
            learning = new NeuroplasticLearning();
            // Add enough patterns to trigger training
            for (let i = 0; i < 15; i++) {
                learning.addPattern({
                    bpm: 120 + i,
                    key: 'C',
                    scale: 'major',
                    timbreProfile: [0.1, 0.2, 0.3, 0.4, 0.5],
                    rhythmPattern: [1, 0, 1, 0]
                });
            }
            // Wait for training to complete
            await new Promise(resolve => setTimeout(resolve, 100));
            // Check if training was called
            expect(mockFit).toHaveBeenCalled();
        });
    });
    describe('prediction', () => {
        it('should predict next pattern', async () => {
            const prediction = await learning.predictNextPattern({
                bpm: 120,
                key: 'C',
                scale: 'major',
                timbreProfile: [0.1, 0.2, 0.3, 0.4, 0.5],
                rhythmPattern: [1, 0, 1, 0]
            });
            expect(prediction).toBeDefined();
            expect(prediction === null || prediction === void 0 ? void 0 : prediction.bpm).toBeCloseTo(20); // 0.1 * 200 (denormalized)
        });
    });
    describe('style vector', () => {
        it('should get style vector', async () => {
            // Add a pattern first
            learning.addPattern({
                bpm: 120,
                key: 'C',
                scale: 'major',
                timbreProfile: [0.1, 0.2, 0.3, 0.4, 0.5],
                rhythmPattern: [1, 0, 1, 0]
            });
            const styleVector = await learning.getStyleVector();
            expect(styleVector).toBeDefined();
            expect(styleVector).toHaveLength(8); // 8-dimensional vector from mock
        });
    });
    describe('reset', () => {
        it('should reset the model and memory', () => {
            // Add some patterns
            learning.addPattern({
                bpm: 120,
                key: 'C',
                scale: 'major',
                timbreProfile: [0.1, 0.2, 0.3, 0.4, 0.5],
                rhythmPattern: [1, 0, 1, 0]
            });
            // Reset
            learning.reset();
            // Check if memory is cleared
            const memory = learning.memory;
            expect(memory).toHaveLength(0);
            // Check if model was reinitialized
            expect(tf.sequential).toHaveBeenCalledTimes(2); // Once in constructor, once in reset
        });
    });
});
//# sourceMappingURL=NeuroplasticLearning.test.js.map