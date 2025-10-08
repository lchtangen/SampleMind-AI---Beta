/**
 * AudioUploader Component
 * 
 * Professional drag-and-drop audio file uploader with progress tracking
 * Uses react-dropzone for optimal file handling
 */

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Music, X, FileAudio, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface AudioFile {
  file: File;
  id: string;
  progress: number;
  status: 'pending' | 'uploading' | 'complete' | 'error';
  error?: string;
}

interface AudioUploaderProps {
  onFilesSelected?: (files: File[]) => void;
  onUploadComplete?: (files: AudioFile[]) => void;
  maxFiles?: number;
  maxSize?: number; // in MB
  allowedFormats?: string[];
}

const DEFAULT_ALLOWED_FORMATS = [
  'audio/mpeg',
  'audio/wav',
  'audio/wave',
  'audio/x-wav',
  'audio/aiff',
  'audio/x-aiff',
  'audio/flac',
  'audio/x-flac',
  'audio/ogg',
  'audio/mp4',
  'audio/m4a',
];

export function AudioUploader({
  onFilesSelected,
  onUploadComplete,
  maxFiles = 10,
  maxSize = 100, // 100MB default
  allowedFormats = DEFAULT_ALLOWED_FORMATS,
}: AudioUploaderProps) {
  const [uploadedFiles, setUploadedFiles] = useState<AudioFile[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Convert files to AudioFile objects
      const newFiles: AudioFile[] = acceptedFiles.map((file) => ({
        file,
        id: `${file.name}-${Date.now()}`,
        progress: 0,
        status: 'pending',
      }));

      setUploadedFiles((prev) => [...prev, ...newFiles]);
      onFilesSelected?.(acceptedFiles);

      // Simulate upload progress (replace with actual upload logic)
      newFiles.forEach((audioFile) => {
        simulateUpload(audioFile.id);
      });
    },
    [onFilesSelected]
  );

  const simulateUpload = (fileId: string) => {
    const interval = setInterval(() => {
      setUploadedFiles((prev) =>
        prev.map((file) => {
          if (file.id === fileId) {
            const newProgress = Math.min(file.progress + 10, 100);
            return {
              ...file,
              progress: newProgress,
              status: newProgress === 100 ? 'complete' : 'uploading',
            };
          }
          return file;
        })
      );
    }, 200);

    // Clear interval after completion
    setTimeout(() => {
      clearInterval(interval);
    }, 2200);
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: allowedFormats.reduce((acc, format) => ({ ...acc, [format]: [] }), {}),
    maxFiles,
    maxSize: maxSize * 1024 * 1024,
    multiple: true,
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <Card
        {...getRootProps()}
        className={cn(
          'cursor-pointer border-2 border-dashed transition-all duration-300',
          isDragActive && !isDragReject && 'border-cyan-500 bg-cyan-500/10 scale-105',
          isDragReject && 'border-red-500 bg-red-500/10',
          !isDragActive && 'border-white/10 bg-slate-800/50 hover:border-purple-500/50 hover:bg-slate-800/70'
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center gap-4 p-12">
          {isDragActive ? (
            <>
              <Upload className="h-16 w-16 text-cyan-400 animate-bounce" />
              <div className="text-center">
                <p className="text-lg font-semibold text-white">Drop your audio files here</p>
                <p className="text-sm text-slate-400">We'll start processing them immediately</p>
              </div>
            </>
          ) : (
            <>
              <div className="relative">
                <div className="absolute inset-0 animate-ping rounded-full bg-purple-500/20" />
                <Music className="relative h-16 w-16 text-purple-400" />
              </div>
              <div className="text-center">
                <p className="text-lg font-semibold text-white">
                  Drag & drop audio files here
                </p>
                <p className="text-sm text-slate-400">
                  or click to browse your computer
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center">
                <Badge variant="secondary" className="bg-purple-500/10 text-purple-300">
                  MP3
                </Badge>
                <Badge variant="secondary" className="bg-blue-500/10 text-blue-300">
                  WAV
                </Badge>
                <Badge variant="secondary" className="bg-cyan-500/10 text-cyan-300">
                  FLAC
                </Badge>
                <Badge variant="secondary" className="bg-indigo-500/10 text-indigo-300">
                  OGG
                </Badge>
                <Badge variant="secondary" className="bg-violet-500/10 text-violet-300">
                  M4A
                </Badge>
              </div>
              <p className="text-xs text-slate-500">
                Max {maxFiles} files • Up to {maxSize}MB per file
              </p>
            </>
          )}
        </div>
      </Card>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">
              Uploaded Files ({uploadedFiles.length})
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setUploadedFiles([])}
              className="text-slate-400 hover:text-white"
            >
              Clear All
            </Button>
          </div>

          {uploadedFiles.map((audioFile) => (
            <Card
              key={audioFile.id}
              className="border-white/10 bg-slate-800/50 p-4"
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div className="flex-shrink-0">
                  {audioFile.status === 'error' ? (
                    <AlertCircle className="h-10 w-10 text-red-400" />
                  ) : (
                    <FileAudio className="h-10 w-10 text-cyan-400" />
                  )}
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-sm font-medium text-white">
                        {audioFile.file.name}
                      </p>
                      <p className="text-xs text-slate-400">
                        {formatFileSize(audioFile.file.size)}
                      </p>
                    </div>

                    {/* Status Badge */}
                    <Badge
                      className={cn(
                        'flex-shrink-0',
                        audioFile.status === 'complete' && 'bg-green-500/10 text-green-400',
                        audioFile.status === 'uploading' && 'bg-blue-500/10 text-blue-400',
                        audioFile.status === 'error' && 'bg-red-500/10 text-red-400',
                        audioFile.status === 'pending' && 'bg-slate-500/10 text-slate-400'
                      )}
                    >
                      {audioFile.status === 'complete' && '✓ Complete'}
                      {audioFile.status === 'uploading' && 'Uploading...'}
                      {audioFile.status === 'error' && 'Error'}
                      {audioFile.status === 'pending' && 'Pending'}
                    </Badge>

                    {/* Remove Button */}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(audioFile.id)}
                      className="h-6 w-6 text-slate-400 hover:text-red-400"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Progress Bar */}
                  {audioFile.status === 'uploading' && (
                    <div className="mt-2">
                      <Progress value={audioFile.progress} className="h-1" />
                      <p className="mt-1 text-xs text-slate-400">
                        {audioFile.progress}%
                      </p>
                    </div>
                  )}

                  {/* Error Message */}
                  {audioFile.status === 'error' && audioFile.error && (
                    <p className="mt-1 text-xs text-red-400">{audioFile.error}</p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}