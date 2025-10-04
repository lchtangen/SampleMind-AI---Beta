'use client';

import React, { useCallback, useState } from 'react';
import { cn } from '@/lib/utils';
import { Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react';

export interface FileWithPreview extends File {
  preview?: string;
}

export interface FileDropzoneProps {
  onFilesSelected: (files: File[]) => void;
  accept?: string;
  maxFiles?: number;
  maxSize?: number; // in MB
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
}

const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFilesSelected,
  accept = 'audio/*',
  maxFiles = 10,
  maxSize = 50,
  multiple = true,
  disabled = false,
  className,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileWithPreview[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const validateFiles = (files: File[]): { valid: File[]; errors: string[] } => {
    const valid: File[] = [];
    const newErrors: string[] = [];

    files.forEach((file) => {
      // Check file size
      const fileSizeMB = file.size / (1024 * 1024);
      if (fileSizeMB > maxSize) {
        newErrors.push(`${file.name} is too large (max ${maxSize}MB)`);
        return;
      }

      // Check file count
      if (!multiple && valid.length >= 1) {
        newErrors.push('Only one file is allowed');
        return;
      }

      if (selectedFiles.length + valid.length >= maxFiles) {
        newErrors.push(`Maximum ${maxFiles} files allowed`);
        return;
      }

      valid.push(file);
    });

    return { valid, errors: newErrors };
  };

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files || disabled) return;

      const fileArray = Array.from(files);
      const { valid, errors: validationErrors } = validateFiles(fileArray);

      setErrors(validationErrors);

      if (valid.length > 0) {
        const filesWithPreview = valid.map((file) => {
          const fileWithPreview = file as FileWithPreview;
          if (file.type.startsWith('image/')) {
            fileWithPreview.preview = URL.createObjectURL(file);
          }
          return fileWithPreview;
        });

        setSelectedFiles((prev) => [...prev, ...filesWithPreview]);
        onFilesSelected(valid);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [disabled, maxFiles, maxSize, multiple, onFilesSelected, selectedFiles.length]
  );

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      handleFiles(files);
    },
    [handleFiles]
  );

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(e.target.files);
      // Reset input value to allow selecting the same file again
      e.target.value = '';
    },
    [handleFiles]
  );

  const removeFile = useCallback((index: number) => {
    setSelectedFiles((prev) => {
      const newFiles = [...prev];
      const removed = newFiles.splice(index, 1)[0];
      if (removed.preview) {
        URL.revokeObjectURL(removed.preview);
      }
      return newFiles;
    });
    setErrors([]);
  }, []);

  const clearAllFiles = useCallback(() => {
    selectedFiles.forEach((file) => {
      if (file.preview) {
        URL.revokeObjectURL(file.preview);
      }
    });
    setSelectedFiles([]);
    setErrors([]);
  }, [selectedFiles]);

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'relative border-2 border-dashed rounded-lg p-8 transition-all duration-200',
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400',
          disabled && 'opacity-50 cursor-not-allowed',
          !disabled && 'cursor-pointer'
        )}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileInputChange}
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />

        <div className="flex flex-col items-center justify-center text-center gap-3">
          <div
            className={cn(
              'p-4 rounded-full',
              isDragging ? 'bg-blue-100' : 'bg-gray-100'
            )}
          >
            <Upload
              className={cn(
                'w-8 h-8',
                isDragging ? 'text-blue-600' : 'text-gray-500'
              )}
            />
          </div>

          <div>
            <p className="text-base font-medium text-gray-700">
              {isDragging ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              or click to browse
            </p>
          </div>

          <p className="text-xs text-gray-400">
            {accept.replace('audio/*', 'Audio files')} • Max {maxSize}MB
            {multiple && ` • Up to ${maxFiles} files`}
          </p>
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="mt-4 space-y-2">
          {errors.map((error, index) => (
            <div
              key={index}
              className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg"
            >
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          ))}
        </div>
      )}

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-medium text-gray-700">
              Selected Files ({selectedFiles.length})
            </p>
            <button
              type="button"
              onClick={clearAllFiles}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              Clear All
            </button>
          </div>

          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="flex-shrink-0">
                    <File className="text-blue-600" size={20} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <CheckCircle className="text-green-600 flex-shrink-0" size={20} />
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="ml-3 text-gray-400 hover:text-red-600 transition-colors flex-shrink-0"
                >
                  <X size={20} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileDropzone;
