/**
 * SampleMind AI API Client
 *
 * Provides typed API client for all backend endpoints:
 * - Audio analysis
 * - Music generation
 * - Stem separation
 * - MIDI conversion
 * - Real-time streaming
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { AudioAnalysis } from '../store/appStore';

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

// ============================================================================
// Request/Response Types
// ============================================================================

export interface AnalyzeAudioRequest {
  file: File;
  level?: 'BASIC' | 'STANDARD' | 'DETAILED' | 'PROFESSIONAL';
}

export interface AnalyzeAudioResponse {
  analysis_id: string;
  file_name: string;
  analysis: AudioAnalysis;
  features: {
    tempo: number;
    key: string;
    energy: number;
    spectral_features: any;
    rhythm_features: any;
  };
}

export interface GenerateMusicRequest {
  prompt: string;
  style?: string;
  mood?: string;
  tempo?: number;
  key?: string;
  duration?: number;
}

export interface GenerateMusicResponse {
  success: boolean;
  message: string;
  generation_id: string;
  audio_url?: string;
  generation_time: number;
  metadata: {
    model: string;
    prompt: string;
    style?: string;
    mood?: string;
    tempo?: number;
    key?: string;
    duration?: number;
  };
}

export interface SeparateStemsRequest {
  file: File;
  stems?: string[];
  format?: 'wav' | 'mp3' | 'flac';
}

export interface SeparateStemsResponse {
  task_id: string;
  status: string;
  stems: {
    name: string;
    path: string;
    size: number;
  }[];
}

export interface ConvertMIDIRequest {
  file: File;
  mode?: 'monophonic' | 'polyphonic' | 'percussion';
}

export interface ConvertMIDIResponse {
  task_id: string;
  status: string;
  midi_path: string;
  midi_data: any;
}

export interface MusicStyle {
  name: string;
  display_name: string;
  description: string;
  typical_tempo: string;
}

export interface MusicMood {
  name: string;
  display_name: string;
  description: string;
  emotion: string;
}

// ============================================================================
// API Client Class
// ============================================================================

class SampleMindAPIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL: baseURL + API_VERSION,
      timeout: 120000, // 2 minutes for long operations
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ==========================================================================
  // Health & Info
  // ==========================================================================

  async getHealth() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ==========================================================================
  // Audio Analysis
  // ==========================================================================

  async analyzeAudio(request: AnalyzeAudioRequest): Promise<AnalyzeAudioResponse> {
    const formData = new FormData();
    formData.append('file', request.file);
    if (request.level) {
      formData.append('level', request.level);
    }

    const response = await this.client.post('/audio/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async getAnalysis(analysisId: string) {
    const response = await this.client.get(`/audio/analysis/${analysisId}`);
    return response.data;
  }

  // ==========================================================================
  // Music Generation
  // ==========================================================================

  async generateMusic(request: GenerateMusicRequest): Promise<GenerateMusicResponse> {
    const response = await this.client.post('/generate/music', request);
    return response.data;
  }

  async generateVariations(
    prompt: string,
    count: number = 3,
    options?: { style?: string; mood?: string; tempo?: number }
  ) {
    const response = await this.client.post('/generate/variations', {
      prompt,
      count,
      ...options,
    });
    return response.data;
  }

  async getMusicStyles(): Promise<MusicStyle[]> {
    const response = await this.client.get('/generate/styles');
    return response.data.styles;
  }

  async getMusicMoods(): Promise<MusicMood[]> {
    const response = await this.client.get('/generate/moods');
    return response.data.moods;
  }

  async getGenerationExamples() {
    const response = await this.client.get('/generate/examples');
    return response.data.examples;
  }

  // ==========================================================================
  // Stem Separation
  // ==========================================================================

  async separateStems(request: SeparateStemsRequest): Promise<SeparateStemsResponse> {
    const formData = new FormData();
    formData.append('file', request.file);
    if (request.stems) {
      formData.append('stems', JSON.stringify(request.stems));
    }
    if (request.format) {
      formData.append('format', request.format);
    }

    const response = await this.client.post('/stems/separate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // ==========================================================================
  // MIDI Conversion
  // ==========================================================================

  async convertToMIDI(request: ConvertMIDIRequest): Promise<ConvertMIDIResponse> {
    const formData = new FormData();
    formData.append('file', request.file);
    if (request.mode) {
      formData.append('mode', request.mode);
    }

    const response = await this.client.post('/midi/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // ==========================================================================
  // Batch Processing
  // ==========================================================================

  async submitBatchJob(files: File[], operation: 'analyze' | 'stems' | 'midi') {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    formData.append('operation', operation);

    const response = await this.client.post('/batch/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async getBatchJobStatus(jobId: string) {
    const response = await this.client.get(`/batch/status/${jobId}`);
    return response.data;
  }

  // ==========================================================================
  // File Management
  // ==========================================================================

  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/audio/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async deleteFile(fileId: string) {
    const response = await this.client.delete(`/audio/files/${fileId}`);
    return response.data;
  }

  async listFiles() {
    const response = await this.client.get('/audio/files');
    return response.data;
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const apiClient = new SampleMindAPIClient();

// ============================================================================
// WebSocket Helper
// ============================================================================

export class AudioStreamWebSocket {
  private ws: WebSocket | null = null;
  private url: string;

  constructor(streamId: string) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.VITE_WS_URL || 'localhost:8000';
    this.url = `${wsProtocol}//${wsHost}/api/v1/stream/audio/${streamId}`;
  }

  connect(
    onAnalysis: (analysis: AudioAnalysis) => void,
    onError?: (error: Event) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        resolve();
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'analysis') {
          onAnalysis(data);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) onError(error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
    });
  }

  sendAudioChunk(audioData: Float32Array) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(audioData.buffer);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
