/**
 * SampleMind AI - Max for Live Communication Layer
 * JavaScript/Max bridge for backend API integration
 *
 * Handles:
 * - HTTP communication with Python backend
 * - Data serialization/deserialization
 * - Error handling and retry logic
 * - Caching and request queuing
 */

// Max global object for Max integration
if (typeof max === 'undefined') {
    // For testing outside Max
    var max = {
        post: function(msg) { console.log('[MAX]', msg); },
        error: function(msg) { console.error('[MAX ERROR]', msg); }
    };
}

/**
 * SampleMind API Client for Max for Live
 */
class SampleMindAPIClient {
    constructor(host = 'localhost', port = 8001) {
        this.baseURL = `http://${host}:${port}`;
        this.timeout = 30000;  // 30 second timeout
        this.maxRetries = 3;
        this.cache = new Map();
        this.requestQueue = [];
        this.isProcessing = false;

        max.post('SampleMind API Client initialized: ' + this.baseURL);
    }

    /**
     * Make HTTP request to backend
     * @param {string} method - HTTP method (GET, POST, etc.)
     * @param {string} endpoint - API endpoint
     * @param {object} data - Request data (for POST/PUT)
     * @returns {Promise} Response data
     */
    async request(method, endpoint, data = null) {
        const url = this.baseURL + endpoint;
        const cacheKey = `${method}:${endpoint}:${JSON.stringify(data)}`;

        // Check cache for GET requests
        if (method === 'GET' && this.cache.has(cacheKey)) {
            max.post('Cache hit: ' + endpoint);
            return this.cache.get(cacheKey);
        }

        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: this.timeout,
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        let lastError = null;

        // Retry logic
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                max.post(`Request: ${method} ${endpoint} (attempt ${attempt}/${this.maxRetries})`);

                const response = await fetch(url, options);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();

                // Cache successful GET requests
                if (method === 'GET') {
                    this.cache.set(cacheKey, result);
                }

                return result;

            } catch (error) {
                lastError = error;
                max.post(`Attempt ${attempt} failed: ${error.message}`);

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
    async checkHealth() {
        try {
            const response = await this.request('GET', '/health');
            max.post('Health check: OK');
            return response;
        } catch (error) {
            max.error('Health check failed: ' + error.message);
            return null;
        }
    }

    /**
     * Analyze audio file
     * @param {string} filePath - Path to audio file
     * @param {string} analysisLevel - Analysis level (BASIC, STANDARD, DETAILED, PROFESSIONAL)
     * @returns {Promise} Analysis result
     */
    async analyzeAudio(filePath, analysisLevel = 'STANDARD') {
        try {
            max.post(`Analyzing: ${filePath} (${analysisLevel})`);

            const response = await this.request('POST', '/api/analyze', {
                file_path: filePath,
                analysis_level: analysisLevel
            });

            max.post('Analysis complete');
            return response;

        } catch (error) {
            max.error('Analysis failed: ' + error.message);
            throw error;
        }
    }

    /**
     * Find similar samples
     * @param {string} filePath - Reference audio file
     * @param {number} limit - Maximum results
     * @returns {Promise} Similar samples
     */
    async findSimilarSamples(filePath, limit = 10) {
        try {
            max.post(`Finding similar samples for: ${filePath}`);

            const response = await this.request('POST', '/api/similar', {
                file_path: filePath,
                limit: limit
            });

            max.post(`Found ${response.similar_count} similar samples`);
            return response;

        } catch (error) {
            max.error('Similar search failed: ' + error.message);
            throw error;
        }
    }

    /**
     * Semantic search in library
     * @param {string} query - Search query
     * @param {number} limit - Maximum results
     * @returns {Promise} Search results
     */
    async searchSamples(query, limit = 10) {
        try {
            max.post(`Searching: ${query}`);

            const response = await this.request('GET', `/api/search?query=${encodeURIComponent(query)}&limit=${limit}`);

            max.post(`Found ${response.results_count} results`);
            return response;

        } catch (error) {
            max.error('Search failed: ' + error.message);
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
    async getProjectSyncRecommendations(projectBPM, projectKey, limit = 10) {
        try {
            max.post(`Project sync: BPM=${projectBPM}, Key=${projectKey}`);

            const response = await this.request('POST', '/api/project-sync', {
                project_bpm: projectBPM,
                project_key: projectKey,
                limit: limit
            });

            max.post(`Found ${response.recommendations_count} recommendations`);
            return response;

        } catch (error) {
            max.error('Project sync failed: ' + error.message);
            throw error;
        }
    }

    /**
     * Generate MIDI from audio
     * @param {string} filePath - Audio file path
     * @param {string} extractionType - Type: melody, harmony, drums, bass_line
     * @returns {Promise} MIDI generation result
     */
    async generateMIDI(filePath, extractionType = 'melody') {
        try {
            max.post(`Generating ${extractionType} MIDI from: ${filePath}`);

            const response = await this.request('POST', '/api/generate-midi', {
                file_path: filePath,
                extraction_type: extractionType
            });

            max.post(`Generated MIDI with ${response.notes_count} notes`);
            return response;

        } catch (error) {
            max.error('MIDI generation failed: ' + error.message);
            throw error;
        }
    }

    /**
     * Get library statistics
     * @returns {Promise} Library stats
     */
    async getLibraryStats() {
        try {
            max.post('Fetching library statistics');

            const response = await this.request('GET', '/api/library/stats');

            max.post('Library stats retrieved');
            return response;

        } catch (error) {
            max.error('Failed to get library stats: ' + error.message);
            throw error;
        }
    }

    /**
     * Get available MIDI extraction types
     * @returns {Promise} Available types
     */
    async getMIDIExtractionTypes() {
        try {
            const response = await this.request('GET', '/api/generate-midi/types');
            return response;

        } catch (error) {
            max.error('Failed to get MIDI types: ' + error.message);
            throw error;
        }
    }

    /**
     * Get available keys in library
     * @returns {Promise} Available keys
     */
    async getAvailableKeys() {
        try {
            const response = await this.request('GET', '/api/project-sync/available-keys');
            return response;

        } catch (error) {
            max.error('Failed to get available keys: ' + error.message);
            throw error;
        }
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
        max.post('API cache cleared');
    }

    /**
     * Get API information
     * @returns {Promise} API info
     */
    async getAPIInfo() {
        try {
            const response = await this.request('GET', '/api/info');
            return response;

        } catch (error) {
            max.error('Failed to get API info: ' + error.message);
            throw error;
        }
    }
}

/**
 * Global API client instance
 */
var samplemindAPI = new SampleMindAPIClient();

/**
 * Helper function to send event from Max to API
 * Called from Max patcher messages
 * @param {string} action - Action to perform
 * @param {object} params - Action parameters
 */
async function handleMaxMessage(action, params) {
    try {
        max.post(`Handling action: ${action}`);

        switch (action) {
            case 'health':
                return await samplemindAPI.checkHealth();

            case 'analyze':
                return await samplemindAPI.analyzeAudio(
                    params.file_path,
                    params.analysis_level || 'STANDARD'
                );

            case 'similar':
                return await samplemindAPI.findSimilarSamples(
                    params.file_path,
                    params.limit || 10
                );

            case 'search':
                return await samplemindAPI.searchSamples(
                    params.query,
                    params.limit || 10
                );

            case 'project_sync':
                return await samplemindAPI.getProjectSyncRecommendations(
                    params.project_bpm,
                    params.project_key,
                    params.limit || 10
                );

            case 'generate_midi':
                return await samplemindAPI.generateMIDI(
                    params.file_path,
                    params.extraction_type || 'melody'
                );

            case 'library_stats':
                return await samplemindAPI.getLibraryStats();

            case 'midi_types':
                return await samplemindAPI.getMIDIExtractionTypes();

            case 'available_keys':
                return await samplemindAPI.getAvailableKeys();

            case 'cache_clear':
                samplemindAPI.clearCache();
                return { status: 'success', message: 'Cache cleared' };

            default:
                throw new Error(`Unknown action: ${action}`);
        }

    } catch (error) {
        max.error(`Error handling ${action}: ${error.message}`);
        return { error: error.message };
    }
}

/**
 * Max message handler
 * Called from Max patcher with: js samplemind_message action [params]
 */
function samplemind_message(action, ...args) {
    // Convert args to params object
    const params = {};

    if (args.length >= 2) {
        for (let i = 0; i < args.length - 1; i += 2) {
            params[args[i]] = args[i + 1];
        }
    }

    handleMaxMessage(action, params);
}

// Export for testing
if (typeof module !== 'undefined') {
    module.exports = { SampleMindAPIClient, handleMaxMessage };
}
