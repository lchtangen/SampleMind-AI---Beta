/**
 * SampleMind AI API Client for VSCode Extension
 */

import axios, { AxiosInstance } from 'axios';
import FormData from 'form-data';
import * as fs from 'fs';

export interface AudioAnalysisResult {
  analysis_id: string;
  file_name: string;
  features: {
    tempo: number;
    key: string;
    energy: number;
    spectral_features: any;
    rhythm_features: any;
  };
}

export interface MusicGenerationResult {
  success: boolean;
  generation_id: string;
  audio_url?: string;
  generation_time: number;
  metadata: any;
}

export class SampleMindAPI {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: `${baseUrl}/api/v1`,
      timeout: 120000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  setBaseUrl(url: string) {
    this.baseUrl = url;
    this.client.defaults.baseURL = `${url}/api/v1`;
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  async analyzeAudio(
    filePath: string,
    level: string = 'STANDARD'
  ): Promise<AudioAnalysisResult> {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('level', level);

    const response = await this.client.post('/audio/analyze', formData, {
      headers: formData.getHeaders(),
    });

    return response.data;
  }

  async getAnalysis(analysisId: string): Promise<any> {
    const response = await this.client.get(`/audio/analysis/${analysisId}`);
    return response.data;
  }

  async generateMusic(options: {
    prompt: string;
    style?: string;
    mood?: string;
    tempo?: number;
    duration?: number;
  }): Promise<MusicGenerationResult> {
    const response = await this.client.post('/generate/music', options);
    return response.data;
  }

  async getMusicStyles(): Promise<any[]> {
    const response = await this.client.get('/generate/styles');
    return response.data.styles;
  }

  async getMusicMoods(): Promise<any[]> {
    const response = await this.client.get('/generate/moods');
    return response.data.moods;
  }

  async separateStems(
    filePath: string,
    stems?: string[],
    format: string = 'wav'
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    if (stems) {
      formData.append('stems', JSON.stringify(stems));
    }
    formData.append('format', format);

    const response = await this.client.post('/stems/separate', formData, {
      headers: formData.getHeaders(),
    });

    return response.data;
  }

  async convertToMIDI(
    filePath: string,
    mode: string = 'monophonic'
  ): Promise<any> {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath));
    formData.append('mode', mode);

    const response = await this.client.post('/midi/convert', formData, {
      headers: formData.getHeaders(),
    });

    return response.data;
  }
}
