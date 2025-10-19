'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Upload, File, X, CheckCircle, AlertCircle, LogOut, User } from 'lucide-react';
import { useAuthContext } from '@/contexts/AuthContext';
import { useAudio } from '@/hooks/useAudio';
import { useNotification } from '@/contexts/NotificationContext';
import ProtectedRoute from '@/components/ProtectedRoute';

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
    <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)]">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-md bg-black/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <h1 className="text-2xl font-bold text-[hsl(0,0%,98%)]">
                SampleMind AI
              </h1>
            </Link>
            
            <nav className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Dashboard
              </Link>
              <Link href="/upload" className="text-[hsl(220,90%,60%)] font-medium">
                Upload
              </Link>
              <Link href="/library" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Library
              </Link>
              <Link href="/gallery" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Gallery
              </Link>
              
              <div className="flex items-center space-x-3 ml-6 pl-6 border-l border-white/10">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-[hsl(220,10%,65%)]" />
                  <span className="text-[hsl(220,10%,65%)] text-sm">{user?.email}</span>
                </div>
                <button
                  onClick={async () => {
                    await logout();
                    addNotification('success', 'Logged out successfully');
                    router.push('/');
                  }}
                  className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-red-500/50 hover:bg-red-500/10 transition text-sm"
                >
                  <LogOut className="h-4 w-4 text-[hsl(220,10%,65%)]" />
                  <span className="text-[hsl(220,10%,65%)]">Logout</span>
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
          <div className="mb-8">
            <h2 className="text-4xl font-bold text-[hsl(0,0%,98%)] mb-2">
              Upload Audio Files
            </h2>
            <p className="text-[hsl(220,10%,65%)]">
              Drag and drop your audio files or click to browse
            </p>
          </div>

          {/* Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`relative group cursor-pointer transition-all duration-300 ${
              isDragging ? 'scale-105' : ''
            }`}
          >
            <div className={`absolute inset-0 rounded-2xl opacity-20 transition blur-2xl ${
              isDragging
                ? 'bg-gradient-to-r from-[hsl(180,95%,55%)] to-[hsl(220,90%,60%)] opacity-40'
                : 'bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)]'
            }`}></div>
            
            <div className={`relative backdrop-blur-md bg-white/5 border-2 border-dashed rounded-2xl p-12 transition ${
              isDragging
                ? 'border-[hsl(180,95%,55%)] bg-white/10'
                : 'border-white/20 group-hover:border-[hsl(220,90%,60%)]/50'
            }`}>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="audio/*,.mp3,.wav,.flac,.aiff,.ogg"
                onChange={handleFileInput}
                className="hidden"
              />
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center h-20 w-20 rounded-full bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] mb-6">
                  <Upload className="h-10 w-10 text-white" />
                </div>
                
                <h3 className="text-2xl font-bold text-[hsl(0,0%,98%)] mb-2">
                  {isDragging ? 'Drop files here' : 'Upload your audio files'}
                </h3>
                
                <p className="text-[hsl(220,10%,65%)] mb-4">
                  Drag and drop files or click to browse
                </p>
                
                <p className="text-sm text-[hsl(220,10%,65%)]">
                  Supported formats: MP3, WAV, FLAC, AIFF, OGG (Max 100MB)
                </p>
              </div>
            </div>
          </div>

          {/* Uploaded Files List */}
          {files.length > 0 && (
            <div className="mt-8">
              <h3 className="text-2xl font-bold text-[hsl(0,0%,98%)] mb-4">
                Uploaded Files ({files.length})
              </h3>
              
              <div className="space-y-3">
                {files.map((uploadedFile) => (
                  <div
                    key={uploadedFile.id}
                    className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4 hover:border-[hsl(220,90%,60%)]/30 transition"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3 flex-1 min-w-0">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center flex-shrink-0">
                          <File className="h-5 w-5 text-white" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-[hsl(0,0%,98%)] truncate">
                            {uploadedFile.file.name}
                          </p>
                          <p className="text-sm text-[hsl(220,10%,65%)]">
                            {formatFileSize(uploadedFile.file.size)}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        {uploadedFile.status === 'uploading' && (
                          <span className="text-sm text-[hsl(220,90%,60%)]">
                            {uploadedFile.progress}%
                          </span>
                        )}
                        
                        {uploadedFile.status === 'completed' && (
                          <CheckCircle className="h-5 w-5 text-[hsl(180,95%,55%)]" />
                        )}
                        
                        {uploadedFile.status === 'error' && (
                          <AlertCircle className="h-5 w-5 text-[hsl(320,90%,60%)]" />
                        )}
                        
                        <button
                          onClick={() => removeFile(uploadedFile.id)}
                          className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(320,90%,60%)]/50 hover:bg-[hsl(320,90%,60%)]/10 flex items-center justify-center transition"
                        >
                          <X className="h-4 w-4 text-[hsl(220,10%,65%)] hover:text-[hsl(320,90%,60%)]" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    {uploadedFile.status === 'uploading' && (
                      <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] transition-all duration-300"
                          style={{ width: `${uploadedFile.progress}%` }}
                        ></div>
                      </div>
                    )}
                    
                    {uploadedFile.status === 'error' && uploadedFile.error && (
                      <p className="text-sm text-[hsl(320,90%,60%)] mt-2">
                        {uploadedFile.error}
                      </p>
                    )}
                  </div>
                ))}
              </div>
              
              {/* Actions */}
              <div className="flex justify-end space-x-4 mt-6">
                <button
                  onClick={() => setFiles([])}
                  className="px-6 py-3 rounded-lg backdrop-blur-sm bg-white/5 border border-white/10 hover:border-white/20 text-[hsl(0,0%,98%)] font-medium transition"
                >
                  Clear All
                </button>
                
                <Link
                  href="/library"
                  className="px-6 py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition inline-block"
                >
                  View Library
                </Link>
              </div>
            </div>
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
