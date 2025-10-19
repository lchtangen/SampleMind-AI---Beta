/**
 * Audio management hook
 */

import { useState, useCallback } from 'react';
import { AudioAPI } from '@/lib/api-client';

interface AudioFile {
  id: number;
  filename: string;
  format: string;
  size: number;
  duration: number;
  status: string;
  uploaded_at: string;
}

export function useAudio() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadAudio = useCallback(async (file: File) => {
    setLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const result = await AudioAPI.upload(file, (progress) => {
        setUploadProgress(progress);
      });

      setLoading(false);
      setUploadProgress(100);
      return { success: true, data: result };
    } catch (err: any) {
      const errorMessage = err.message || 'Upload failed';
      setError(errorMessage);
      setLoading(false);
      setUploadProgress(0);
      return { success: false, error: errorMessage };
    }
  }, []);

  const analyzeAudio = useCallback(async (
    audioId: number,
    analysisType = 'full',
    extractFeatures = true,
    aiAnalysis = true
  ) => {
    setLoading(true);
    setError(null);

    try {
      const result = await AudioAPI.analyze(
        audioId,
        analysisType,
        extractFeatures,
        aiAnalysis
      );

      setLoading(false);
      return { success: true, data: result };
    } catch (err: any) {
      const errorMessage = err.message || 'Analysis failed';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, []);

  const listAudio = useCallback(async (page = 1, pageSize = 20) => {
    setLoading(true);
    setError(null);

    try {
      const result = await AudioAPI.list(page, pageSize);
      setLoading(false);
      return { success: true, data: result };
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load audio';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, []);

  const getAudio = useCallback(async (audioId: number) => {
    setLoading(true);
    setError(null);

    try {
      const result = await AudioAPI.get(audioId);
      setLoading(false);
      return { success: true, data: result };
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to load audio';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, []);

  const deleteAudio = useCallback(async (audioId: number) => {
    setLoading(true);
    setError(null);

    try {
      await AudioAPI.delete(audioId);
      setLoading(false);
      return { success: true };
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to delete audio';
      setError(errorMessage);
      setLoading(false);
      return { success: false, error: errorMessage };
    }
  }, []);

  return {
    loading,
    error,
    uploadProgress,
    uploadAudio,
    analyzeAudio,
    listAudio,
    getAudio,
    deleteAudio,
  };
}
