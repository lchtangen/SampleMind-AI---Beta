'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Upload, File, X, CheckCircle, AlertCircle, LogOut, User, HardDrive } from 'lucide-react';
import { useAuthContext } from '@/contexts/AuthContext';
import { useAudio } from '@/hooks/useAudio';
import { useNotification } from '@/contexts/NotificationContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { UploadAreaSkeleton, BatchQueueItemSkeleton } from '@/components/ui/SkeletonLoaders';

interface UploadedFile {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
}

function UploadPageContent() {
  const router = useRouter();
  const { user, logout } = useAuthContext();
  const { uploadAudio, uploadProgress } = useAudio();
  const { addNotification } = useNotification();
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      handleFiles(selectedFiles);
    }
  };

  const handleFiles = async (newFiles: File[]) => {
    const audioFiles = newFiles.filter(file => 
      file.type.startsWith('audio/') || 
      /\.(mp3|wav|flac|aiff|ogg)$/i.test(file.name)
    );

    if (audioFiles.length === 0) {
      addNotification('error', 'Please select valid audio files');
      return;
    }

    const uploadedFiles: UploadedFile[] = audioFiles.map(file => ({
      id: Math.random().toString(36).substring(7),
      file,
      progress: 0,
      status: 'uploading'
    }));

    setFiles(prev => [...prev, ...uploadedFiles]);

    // Upload files one by one
    for (const uploadedFile of uploadedFiles) {
      await uploadFile(uploadedFile);
    }
  };

  const uploadFile = async (uploadedFile: UploadedFile) => {
    try {
      const result = await uploadAudio(uploadedFile.file, (progress) => {
        setFiles(prev => prev.map(file => 
          file.id === uploadedFile.id 
            ? { ...file, progress, status: progress === 100 ? 'completed' : 'uploading' }
            : file
        ));
      });

      if (result.success) {
        setFiles(prev => prev.map(file => 
          file.id === uploadedFile.id 
            ? { ...file, status: 'completed', progress: 100 }
            : file
        ));
        addNotification('success', `${uploadedFile.file.name} uploaded successfully!`);
      } else {
        setFiles(prev => prev.map(file => 
          file.id === uploadedFile.id 
            ? { ...file, status: 'error', error: result.error }
            : file
        ));
        addNotification('error', `Failed to upload ${uploadedFile.file.name}`);
      }
    } catch (error) {
      setFiles(prev => prev.map(file => 
        file.id === uploadedFile.id 
          ? { ...file, status: 'error', error: 'Upload failed' }
          : file
      ));
      addNotification('error', `Error uploading ${uploadedFile.file.name}`);
    }
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-black">
      {/* Header */}
      <header className="border-b border-slate-700/50 backdrop-blur-md bg-slate-900/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <h1 className="text-2xl font-bold text-slate-100">SampleMind AI</h1>
            </Link>

            <nav className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-slate-400 hover:text-slate-300 transition">
                Dashboard
              </Link>
              <Link href="/upload" className="text-cyan-400 font-medium">
                Upload
              </Link>
              <Link href="/library" className="text-slate-400 hover:text-slate-300 transition">
                Library
              </Link>

              <div className="flex items-center space-x-3 ml-6 pl-6 border-l border-slate-700/50">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-slate-400" />
                  <span className="text-slate-400 text-sm">{user?.email}</span>
                </div>
                <button
                  onClick={async () => {
                    await logout();
                    addNotification('success', 'Logged out successfully');
                    router.push('/');
                  }}
                  className="flex items-center space-x-2 px-3 py-1.5 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition text-sm"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h2 className="text-4xl font-bold text-slate-100 mb-2">
              Upload Audio Files
            </h2>
            <p className="text-slate-400">
              Drag and drop your audio files or click to browse. Batch upload up to 100 files at once.
            </p>
          </motion.div>

          {/* Drop Zone */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`relative group cursor-pointer transition-all duration-300 ${
              isDragging ? 'scale-105' : ''
            }`}
          >
            <div
              className={`absolute inset-0 rounded-2xl opacity-20 transition blur-2xl ${
                isDragging
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 opacity-40'
                  : 'bg-gradient-to-r from-cyan-500 to-blue-500'
              }`}
            ></div>

            <div
              className={`relative backdrop-blur-md bg-slate-800/30 border-2 border-dashed rounded-2xl p-12 transition ${
                isDragging
                  ? 'border-cyan-400 bg-slate-800/50'
                  : 'border-slate-600 group-hover:border-cyan-500/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="audio/*,.mp3,.wav,.flac,.aiff,.ogg"
                onChange={handleFileInput}
                className="hidden"
              />

              <div className="text-center">
                <div className="inline-flex items-center justify-center h-20 w-20 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 mb-6">
                  <Upload className="h-10 w-10 text-white" />
                </div>

                <h3 className="text-2xl font-bold text-slate-100 mb-2">
                  {isDragging ? 'Drop files here' : 'Upload your audio files'}
                </h3>

                <p className="text-slate-400 mb-4">
                  Drag and drop files or click to browse
                </p>

                <p className="text-sm text-slate-500">
                  Supported: MP3, WAV, FLAC, AIFF, OGG (Max 100MB per file)
                </p>
              </div>
            </div>
          </motion.div>

          {/* Uploaded Files List */}
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-8"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-slate-100">Queue ({files.length})</h3>
                <div className="flex items-center space-x-2 text-sm text-slate-400">
                  <HardDrive className="h-4 w-4" />
                  <span>
                    {(
                      files.reduce((acc, f) => acc + f.file.size, 0) / (1024 * 1024)
                    ).toFixed(1)}{' '}
                    MB total
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                {files.map((uploadedFile, index) => (
                  <motion.div
                    key={uploadedFile.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="relative backdrop-blur-sm bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 hover:border-cyan-500/30 transition group"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3 flex-1 min-w-0">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                          <File className="h-5 w-5 text-white" />
                        </div>

                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-slate-200 truncate">
                            {uploadedFile.file.name}
                          </p>
                          <p className="text-sm text-slate-500">
                            {formatFileSize(uploadedFile.file.size)}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        {uploadedFile.status === 'uploading' && (
                          <span className="text-sm text-cyan-400 font-medium min-w-fit">
                            {uploadedFile.progress}%
                          </span>
                        )}

                        {uploadedFile.status === 'completed' && (
                          <CheckCircle className="h-5 w-5 text-green-400" />
                        )}

                        {uploadedFile.status === 'error' && (
                          <AlertCircle className="h-5 w-5 text-red-400" />
                        )}

                        <button
                          onClick={() => removeFile(uploadedFile.id)}
                          className="h-8 w-8 rounded-lg bg-slate-700/30 border border-slate-600 hover:border-red-500/50 hover:bg-red-500/10 flex items-center justify-center transition opacity-0 group-hover:opacity-100"
                        >
                          <X className="h-4 w-4 text-slate-400 hover:text-red-400" />
                        </button>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    {uploadedFile.status === 'uploading' && (
                      <div className="h-1 bg-slate-700/50 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${uploadedFile.progress}%` }}
                          className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                    )}

                    {uploadedFile.status === 'error' && uploadedFile.error && (
                      <p className="text-sm text-red-400 mt-2">{uploadedFile.error}</p>
                    )}
                  </motion.div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex justify-end space-x-4 mt-6">
                <button
                  onClick={() => setFiles([])}
                  className="px-6 py-3 rounded-lg backdrop-blur-sm bg-slate-800/30 border border-slate-700 hover:border-slate-600 text-slate-300 font-medium transition"
                >
                  Clear All
                </button>

                <Link
                  href="/library"
                  className="px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:shadow-lg hover:shadow-cyan-500/50 transition inline-block"
                >
                  View Library
                </Link>
              </div>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <UploadPageContent />
    </ProtectedRoute>
  );
}
