/**
 * File Upload Component with Drag & Drop
 *
 * Upload audio files with drag-and-drop support
 */

import { useState, useRef } from 'react';
import type { DragEvent } from 'react';
import { useAppStore } from '../store/appStore';
import { apiClient } from '../services/api';
import { useElectronFileEvents } from '../hooks/useElectron';

interface FileUploadProps {
  onUploadComplete?: (fileId: string) => void;
  accept?: string;
  multiple?: boolean;
}

export default function FileUpload({
  onUploadComplete,
  accept = 'audio/*,.mp3,.wav,.flac,.m4a,.aac,.ogg',
  multiple = true,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addAudioFile = useAppStore((state) => state.addAudioFile);
  // const { isElectron } = useElectronFiles();  // Reserved for future use

  // Handle file opens from Electron menu
  useElectronFileEvents(
    undefined,
    async (filePaths) => {
      // Convert file paths to File objects
      const files: File[] = [];
      for (const filePath of filePaths) {
        try {
          const response = await fetch(`file://${filePath}`);
          const blob = await response.blob();
          const file = new File([blob], filePath.split('/').pop() || 'file', {
            type: 'audio/*',
          });
          files.push(file);
        } catch (error) {
          console.error('Failed to load file:', error);
        }
      }
      if (files.length > 0) {
        await handleFiles(files);
      }
    }
  );

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    await handleFiles(files);
  };

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      await handleFiles(files);
    }
  };

  const handleFiles = async (files: File[]) => {
    setUploading(true);

    for (const file of files) {
      try {
        // Validate file type
        if (!file.type.startsWith('audio/')) {
          console.warn(`Skipping non-audio file: ${file.name}`);
          continue;
        }

        // Create file ID
        const fileId = `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Update progress
        setUploadProgress((prev) => ({ ...prev, [fileId]: 0 }));

        // Get audio duration using FileReader and Audio element
        const duration = await getAudioDuration(file);

        // Upload file
        const response = await apiClient.uploadFile(file);

        // Add to store
        addAudioFile({
          id: fileId,
          name: file.name,
          path: response.file_path || URL.createObjectURL(file),
          size: file.size,
          duration: duration,
          uploadedAt: new Date(),
          analyzed: false,
        });

        // Update progress
        setUploadProgress((prev) => ({ ...prev, [fileId]: 100 }));

        // Callback
        if (onUploadComplete) {
          onUploadComplete(fileId);
        }

        // Auto-analyze
        setTimeout(async () => {
          try {
            const analysisResponse = await apiClient.analyzeAudio({
              file,
              level: 'STANDARD',
            });

            // Update store with analysis
            const updateFileAnalysis = useAppStore.getState().updateFileAnalysis;
            updateFileAnalysis(fileId, {
              tempo: analysisResponse.features.tempo,
              key: analysisResponse.features.key,
              energy: analysisResponse.features.energy,
              spectralCentroid: analysisResponse.features.spectral_features?.centroid || 0,
              onsets: [],
              timestamp: Date.now(),
            });
          } catch (error) {
            console.error('Auto-analysis failed:', error);
          }
        }, 1000);
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error);
      }
    }

    setUploading(false);
    setUploadProgress({});

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getAudioDuration = (file: File): Promise<number> => {
    return new Promise((resolve) => {
      const audio = new Audio();
      const url = URL.createObjectURL(file);

      audio.addEventListener('loadedmetadata', () => {
        URL.revokeObjectURL(url);
        resolve(audio.duration);
      });

      audio.addEventListener('error', () => {
        URL.revokeObjectURL(url);
        resolve(0);
      });

      audio.src = url;
    });
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload">
      <div
        className={`upload-dropzone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />

        <div className="upload-content">
          {uploading ? (
            <>
              <div className="upload-icon uploading">⏳</div>
              <p className="upload-text">Uploading files...</p>
              <div className="upload-progress-list">
                {Object.entries(uploadProgress).map(([id, progress]) => (
                  <div key={id} className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                ))}
              </div>
            </>
          ) : isDragging ? (
            <>
              <div className="upload-icon dragging">📂</div>
              <p className="upload-text">Drop files here</p>
            </>
          ) : (
            <>
              <div className="upload-icon">📁</div>
              <p className="upload-text">
                Drag & drop audio files here or click to browse
              </p>
              <p className="upload-hint">
                Supports MP3, WAV, FLAC, M4A, AAC, OGG
              </p>
              <button className="upload-btn" type="button">
                Select Files
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
