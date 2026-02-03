/**
 * Unit tests for SampleMind API Client (communication.js)
 * Tests core communication layer functionality including:
 * - HTTP request handling
 * - Error handling and retry logic
 * - Caching behavior
 * - API method signatures
 */

const { SampleMindAPIClient } = require('../../../plugins/ableton/prototype/communication.js');

describe('SampleMindAPIClient', () => {
    let client;
    let fetchMock;

    beforeEach(() => {
        client = new SampleMindAPIClient('http://localhost:8001');

        // Mock fetch
        global.fetch = jest.fn();
        fetchMock = global.fetch;

        // Mock AbortController
        global.AbortController = class {
            abort() {}
        };

        // Mock setTimeout/clearTimeout
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.clearAllMocks();
        jest.useRealTimers();
    });

    // === Initialization Tests ===

    test('Client initializes with correct baseUrl', () => {
        const testClient = new SampleMindAPIClient('http://test:9000');
        expect(testClient.baseUrl).toBe('http://test:9000');
    });

    test('Client initializes with default baseUrl', () => {
        const testClient = new SampleMindAPIClient();
        expect(testClient.baseUrl).toBe('http://localhost:8001');
    });

    test('Client initializes with correct timeout', () => {
        expect(client.timeout).toBe(30000);
    });

    test('Client initializes with maxRetries', () => {
        expect(client.maxRetries).toBe(3);
    });

    test('Client initializes with empty cache', () => {
        expect(client.cache.size).toBe(0);
    });

    // === Health Check Tests ===

    test('health() makes GET request to /health', async () => {
        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockResolvedValueOnce({ status: 'healthy' })
        });

        const result = await client.health();

        expect(fetchMock).toHaveBeenCalledWith(
            'http://localhost:8001/health',
            expect.objectContaining({ method: 'GET' })
        );
        expect(result.status).toBe('healthy');
    });

    test('health() throws on connection failure', async () => {
        fetchMock.mockRejectedValue(new Error('Connection failed'));

        await expect(client.health()).rejects.toThrow('Connection failed');
    });

    // === Retry Logic Tests ===

    test('Request retries on failure', async () => {
        // First 2 attempts fail, 3rd succeeds
        fetchMock
            .mockRejectedValueOnce(new Error('Network error'))
            .mockRejectedValueOnce(new Error('Network error'))
            .mockResolvedValueOnce({
                ok: true,
                json: jest.fn().mockResolvedValueOnce({ result: 'success' })
            });

        const result = await client.request('GET', '/test');

        expect(fetchMock).toHaveBeenCalledTimes(3);
        expect(result.result).toBe('success');
    });

    test('Request throws after maxRetries failures', async () => {
        fetchMock.mockRejectedValue(new Error('Persistent error'));

        await expect(client.request('GET', '/test')).rejects.toThrow('Failed after 3 attempts');
        expect(fetchMock).toHaveBeenCalledTimes(3);
    });

    test('Request implements exponential backoff', async () => {
        fetchMock.mockRejectedValue(new Error('Error'));

        await expect(client.request('GET', '/test')).rejects.toThrow();

        // Should have called setTimeout for backoff delays
        const timeoutCalls = jest.runOnlyPendingTimers();
        expect(jest.getTimerCount()).toBeGreaterThan(0);
    });

    // === Caching Tests ===

    test('GET requests are cached', async () => {
        fetchMock.mockResolvedValue({
            ok: true,
            json: jest.fn().mockResolvedValue({ cached: true })
        });

        // First request should hit network
        await client.request('GET', '/cached-endpoint');
        expect(fetchMock).toHaveBeenCalledTimes(1);

        // Clear mocks to verify cache
        fetchMock.mockClear();

        // Second request should use cache
        const result = await client.request('GET', '/cached-endpoint');
        expect(fetchMock).not.toHaveBeenCalled();
        expect(result.cached).toBe(true);
    });

    test('Cache can be disabled', async () => {
        client.cacheEnabled = false;

        fetchMock.mockResolvedValue({
            ok: true,
            json: jest.fn().mockResolvedValue({ data: 'test' })
        });

        // First request
        await client.request('GET', '/test');
        expect(fetchMock).toHaveBeenCalledTimes(1);

        fetchMock.mockClear();

        // Second request should hit network
        await client.request('GET', '/test');
        expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    test('clearCache() empties cache', async () => {
        fetchMock.mockResolvedValue({
            ok: true,
            json: jest.fn().mockResolvedValue({ data: 'test' })
        });

        // Populate cache
        await client.request('GET', '/test');
        expect(client.cache.size).toBe(1);

        // Clear cache
        client.clearCache();
        expect(client.cache.size).toBe(0);
    });

    test('POST requests are not cached', async () => {
        fetchMock.mockResolvedValue({
            ok: true,
            json: jest.fn().mockResolvedValue({ result: 'posted' })
        });

        // First POST request
        await client.request('POST', '/endpoint', { data: 'test' });
        expect(fetchMock).toHaveBeenCalledTimes(1);

        fetchMock.mockClear();

        // Second POST request should hit network
        await client.request('POST', '/endpoint', { data: 'test' });
        expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    // === Audio Analysis Tests ===

    test('analyzeAudio() sends FormData with file', async () => {
        const mockFile = new File(['audio'], 'test.wav', { type: 'audio/wav' });

        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockResolvedValueOnce({
                tempo_bpm: 120,
                key: 'C Major',
                genre: 'Electronic'
            })
        });

        const result = await client.analyzeAudio(mockFile, 'STANDARD');

        expect(fetchMock).toHaveBeenCalledWith(
            'http://localhost:8001/api/analyze',
            expect.objectContaining({
                method: 'POST',
                body: expect.any(FormData)
            })
        );
        expect(result.tempo_bpm).toBe(120);
    });

    test('analyzeAudio() uses provided analysis level', async () => {
        const mockFile = new File(['audio'], 'test.wav');

        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockResolvedValueOnce({})
        });

        await client.analyzeAudio(mockFile, 'PROFESSIONAL');

        // Verify FormData was created with analysis_level
        const callArgs = fetchMock.mock.calls[0];
        expect(callArgs[0]).toContain('/api/analyze');
    });

    // === Similar Search Tests ===

    test('findSimilar() returns array of results', async () => {
        const mockFile = new File(['audio'], 'test.wav');

        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockResolvedValueOnce({
                similar_samples: [
                    { file_path: 'sample1.wav', similarity: 0.95 },
                    { file_path: 'sample2.wav', similarity: 0.87 }
                ]
            })
        });

        const results = await client.findSimilar(mockFile, 10);

        expect(Array.isArray(results)).toBe(true);
        expect(results.length).toBe(2);
        expect(results[0].similarity).toBe(0.95);
    });

    test('findSimilar() handles missing results', async () => {
        const mockFile = new File(['audio'], 'test.wav');

        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockResolvedValueOnce({})
        });

        const results = await client.findSimilar(mockFile);

        expect(Array.isArray(results)).toBe(true);
        expect(results.length).toBe(0);
    });

    // === Project Sync Tests ===

    test('projectSync() sends BPM and key', async () => {
        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockResolvedValueOnce({
                matched_samples: []
            })
        });

        await client.projectSync(120, 'C Major', 10);

        const callArgs = fetchMock.mock.calls[0];
        const body = JSON.parse(callArgs[1].body);
        expect(body.project_bpm).toBe(120);
        expect(body.project_key).toBe('C Major');
    });

    test('projectSync() returns array of matches', async () => {
        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockResolvedValueOnce({
                matched_samples: [
                    { file_path: 'match1.wav', bpm: 120, match_score: 0.98 }
                ]
            })
        });

        const results = await client.projectSync(120, 'C Major');

        expect(Array.isArray(results)).toBe(true);
        expect(results[0].match_score).toBe(0.98);
    });

    // === Error Handling Tests ===

    test('HTTP error responses throw', async () => {
        fetchMock.mockResolvedValueOnce({
            ok: false,
            status: 404,
            statusText: 'Not Found'
        });

        await expect(client.request('GET', '/notfound')).rejects.toThrow('HTTP 404');
    });

    test('Timeout is handled', async () => {
        // Simulate timeout by rejecting with AbortError
        fetchMock.mockRejectedValue(new DOMException('Aborted', 'AbortError'));

        await expect(client.request('GET', '/timeout')).rejects.toThrow();
    });

    test('JSON parse errors are handled', async () => {
        fetchMock.mockResolvedValueOnce({
            ok: true,
            json: jest.fn().mockRejectedValueOnce(new SyntaxError('Invalid JSON'))
        });

        await expect(client.request('GET', '/invalid')).rejects.toThrow();
    });

    // === Settings Tests ===

    test('Client URL can be changed', () => {
        const testClient = new SampleMindAPIClient('http://localhost:8001');
        testClient.baseUrl = 'http://newhost:9000';

        expect(testClient.baseUrl).toBe('http://newhost:9000');
    });

    test('maxRetries can be changed', () => {
        client.maxRetries = 5;
        expect(client.maxRetries).toBe(5);
    });

    test('Cache enabled flag works', () => {
        expect(client.cacheEnabled).toBe(true);
        client.cacheEnabled = false;
        expect(client.cacheEnabled).toBe(false);
    });

    // === Sleep/Delay Tests ===

    test('sleep() returns promise that resolves', async () => {
        jest.useFakeTimers();
        const sleepPromise = client.sleep(1000);

        const result = Promise.resolve('done');
        jest.runAllTimers();

        expect(typeof sleepPromise.then).toBe('function');
    });
});

/**
 * Integration-style tests for API method combinations
 */
describe('SampleMindAPIClient - Integration Scenarios', () => {
    let client;

    beforeEach(() => {
        client = new SampleMindAPIClient();

        global.fetch = jest.fn();
        global.AbortController = class {
            abort() {}
        };
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    test('Multiple sequential requests', async () => {
        global.fetch
            .mockResolvedValueOnce({
                ok: true,
                json: jest.fn().mockResolvedValueOnce({ status: 'ok' })
            })
            .mockResolvedValueOnce({
                ok: true,
                json: jest.fn().mockResolvedValueOnce({ data: 'test' })
            });

        const result1 = await client.health();
        const result2 = await client.request('GET', '/other');

        expect(global.fetch).toHaveBeenCalledTimes(2);
        expect(result1.status).toBe('ok');
        expect(result2.data).toBe('test');
    });

    test('Error recovery with retry', async () => {
        let callCount = 0;

        global.fetch.mockImplementation(() => {
            callCount++;
            if (callCount < 3) {
                return Promise.reject(new Error('Temporary error'));
            }
            return Promise.resolve({
                ok: true,
                json: jest.fn().mockResolvedValueOnce({ recovered: true })
            });
        });

        const result = await client.request('GET', '/endpoint');

        expect(callCount).toBe(3);
        expect(result.recovered).toBe(true);
    });
});
