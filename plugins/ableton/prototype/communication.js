/**
 * SampleMind AI - HTML Prototype Communication Layer
 * HTTP/Fetch API client for backend integration
 *
 * Handles:
 * - HTTP communication with Python backend
 * - FormData for file uploads
 * - JSON request/response handling
 * - Error handling and retry logic
 * - Caching
 */

class SampleMindAPIClient {
    constructor(baseUrl = 'http://localhost:8001') {
        this.baseUrl = baseUrl;
        this.timeout = 30000;  // 30 second timeout
        this.maxRetries = 3;
        this.cache = new Map();
        this.cacheEnabled = true;

        console.log('[SampleMind] API Client initialized:', this.baseUrl);
    }

    /**
     * Make HTTP request to backend
     * @param {string} method - HTTP method
     * @param {string} endpoint - API endpoint
     * @param {object|FormData} data - Request data
     * @param {object} options - Additional options
     * @returns {Promise} Response data
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = this.baseUrl + endpoint;
        const cacheKey = `${method}:${endpoint}`;

        // Check cache for GET requests
        if (method === 'GET' && this.cacheEnabled && this.cache.has(cacheKey)) {
            console.log('[SampleMind] Cache hit:', endpoint);
            return this.cache.get(cacheKey);
        }

        const fetchOptions = {
            method: method,
            timeout: this.timeout,
            ...options
        };

        // Only set Content-Type for JSON, not for FormData
        if (!options.headers || !options['Content-Type']) {
            if (!(data instanceof FormData)) {
                if (!fetchOptions.headers) fetchOptions.headers = {};
                fetchOptions.headers['Content-Type'] = 'application/json';
            }
        }

        if (data) {
            if (data instanceof FormData) {
                fetchOptions.body = data;
            } else {
                fetchOptions.body = JSON.stringify(data);
            }
        }

        let lastError = null;

        // Retry logic
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                console.log(`[SampleMind] Request: ${method} ${endpoint} (attempt ${attempt}/${this.maxRetries})`);

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const response = await fetch(url, {
                    ...fetchOptions,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();

                // Cache successful GET requests
                if (method === 'GET' && this.cacheEnabled) {
                    this.cache.set(cacheKey, result);
                }

                return result;

            } catch (error) {
                lastError = error;
                console.log(`[SampleMind] Attempt ${attempt} failed:`, error.message);

                if (attempt < this.maxRetries) {
                    // Wait before retry (exponential backoff)
                    await this.sleep(Math.pow(2, attempt - 1) * 100);
                }
            }
        }

        throw new Error(`Failed after ${this.maxRetries} attempts: ${lastError.message}`);
    }

    /**
     * Sleep for specified milliseconds
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check API health
     * @returns {Promise} Health status
     */
    async health() {
        try {
            const response = await this.request('GET', '/health');
            console.log('[SampleMind] Health check: OK');
            return response;
        } catch (error) {
            console.error('[SampleMind] Health check failed:', error.message);
            throw error;
        }
    }

    /**
     * Analyze audio file
     * @param {File} file - Audio file from HTML input
     * @param {string} analysisLevel - Analysis level (BASIC, STANDARD, DETAILED, PROFESSIONAL)
     * @returns {Promise} Analysis result
     */
    async analyzeAudio(file, analysisLevel = 'STANDARD') {
        try {
            console.log(`[SampleMind] Analyzing: ${file.name} (${analysisLevel})`);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('analysis_level', analysisLevel);

            const response = await this.request('POST', '/api/analyze', formData);

            console.log('[SampleMind] Analysis complete');
            return response;

        } catch (error) {
            console.error('[SampleMind] Analysis failed:', error.message);
            throw error;
        }
    }

    /**
     * Find similar samples
     * @param {File} file - Reference audio file
     * @param {number} limit - Maximum results
     * @returns {Promise} Similar samples
     */
    async findSimilar(file, limit = 10) {
        try {
            console.log(`[SampleMind] Finding similar samples for: ${file.name}`);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('limit', limit);

            const response = await this.request('POST', '/api/similar', formData);

            console.log(`[SampleMind] Found ${response.similar_samples?.length || 0} similar samples`);
            return response.similar_samples || [];

        } catch (error) {
            console.error('[SampleMind] Similar search failed:', error.message);
            throw error;
        }
    }

    /**
     * Semantic search in library
     * @param {string} query - Search query
     * @param {number} limit - Maximum results
     * @returns {Promise} Search results
     */
    async search(query, limit = 10) {
        try {
            console.log(`[SampleMind] Searching: ${query}`);

            const response = await this.request(
                'GET',
                `/api/search?query=${encodeURIComponent(query)}&limit=${limit}`
            );

            console.log(`[SampleMind] Found ${response.results?.length || 0} results`);
            return response.results || [];

        } catch (error) {
            console.error('[SampleMind] Search failed:', error.message);
            throw error;
        }
    }

    /**
     * Get project sync recommendations
     * @param {number} projectBPM - Project BPM
     * @param {string} projectKey - Project key
     * @param {number} limit - Maximum results
     * @returns {Promise} Recommendations
     */
    async projectSync(projectBPM, projectKey, limit = 10) {
        try {
            console.log(`[SampleMind] Project sync: BPM=${projectBPM}, Key=${projectKey}`);

            const response = await this.request('POST', '/api/project-sync', {
                project_bpm: projectBPM,
                project_key: projectKey,
                limit: limit
            });

            console.log(`[SampleMind] Found ${response.matched_samples?.length || 0} recommendations`);
            return response.matched_samples || [];

        } catch (error) {
            console.error('[SampleMind] Project sync failed:', error.message);
            throw error;
        }
    }

    /**
     * Generate MIDI from audio
     * @param {File} file - Audio file
     * @param {string} extractionType - Type: melody, harmony, drums, bass_line
     * @returns {Promise} MIDI generation result
     */
    async generateMIDI(file, extractionType = 'melody') {
        try {
            console.log(`[SampleMind] Generating ${extractionType} MIDI from: ${file.name}`);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('extraction_type', extractionType);

            const response = await this.request('POST', '/api/generate-midi', formData);

            console.log(`[SampleMind] Generated MIDI with ${response.note_count || 0} notes`);
            return response;

        } catch (error) {
            console.error('[SampleMind] MIDI generation failed:', error.message);
            throw error;
        }
    }

    /**
     * Get library statistics
     * @returns {Promise} Library stats
     */
    async libraryStats() {
        try {
            console.log('[SampleMind] Fetching library statistics');

            const response = await this.request('GET', '/api/library/stats');

            console.log('[SampleMind] Library stats retrieved');
            return response;

        } catch (error) {
            console.error('[SampleMind] Failed to get library stats:', error.message);
            throw error;
        }
    }

    /**
     * Get available keys
     * @returns {Promise} Available keys
     */
    async availableKeys() {
        try {
            const response = await this.request('GET', '/api/project-sync/available-keys');
            return response.keys || [];

        } catch (error) {
            console.error('[SampleMind] Failed to get available keys:', error.message);
            throw error;
        }
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        console.log('[SampleMind] API cache cleared');
    }
}

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SampleMindAPIClient };
}
