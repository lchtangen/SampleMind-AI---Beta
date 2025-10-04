'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/useAuthStore'
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent,
  FileDropzone,
  Button,
  ProgressBar,
  Spinner,
  Badge
} from '@/components'
import Navbar from '@/components/layout/Navbar'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'
import { CheckCircle2, AlertCircle, FileAudio, Sparkles } from 'lucide-react'

interface UploadedFile {
  file: File
  fileId?: string
  status: 'pending' | 'uploading' | 'uploaded' | 'analyzing' | 'complete' | 'error'
  progress: number
  error?: string
  taskId?: string
}

export default function UploadPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuthStore()
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  const handleFilesSelected = async (files: File[]) => {
    const newFiles: UploadedFile[] = files.map(file => ({
      file,
      status: 'pending',
      progress: 0
    }))
    
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const uploadFile = async (index: number) => {
    const file = uploadedFiles[index]
    
    try {
      // Update status to uploading
      setUploadedFiles(prev => {
        const updated = [...prev]
        updated[index] = { ...updated[index], status: 'uploading', progress: 0 }
        return updated
      })

      // Upload file
      const response = await api.uploadAudio(file.file, (progress) => {
        setUploadedFiles(prev => {
          const updated = [...prev]
          updated[index] = { ...updated[index], progress }
          return updated
        })
      })

      // Update with file ID
      setUploadedFiles(prev => {
        const updated = [...prev]
        updated[index] = { 
          ...updated[index], 
          status: 'uploaded', 
          progress: 100,
          fileId: response.file_id 
        }
        return updated
      })

      toast.success(`${file.file.name} uploaded successfully!`)
      return response.file_id
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } }
      const errorMsg = err.response?.data?.detail || 'Upload failed'
      
      setUploadedFiles(prev => {
        const updated = [...prev]
        updated[index] = { 
          ...updated[index], 
          status: 'error', 
          error: errorMsg 
        }
        return updated
      })
      
      toast.error(errorMsg)
      throw error
    }
  }

  const analyzeFile = async (index: number, fileId: string, filePath: string) => {
    try {
      // Update status to analyzing
      setUploadedFiles(prev => {
        const updated = [...prev]
        updated[index] = { ...updated[index], status: 'analyzing', progress: 0 }
        return updated
      })

      // Submit analysis task
      const response = await api.submitTask(fileId, filePath)
      
      setUploadedFiles(prev => {
        const updated = [...prev]
        updated[index] = { 
          ...updated[index], 
          taskId: response.task_id,
          progress: 50 
        }
        return updated
      })

      toast.success('Analysis started!')
      
      // Poll for completion
      let attempts = 0
      const maxAttempts = 60 // 5 minutes max
      
      const pollInterval = setInterval(async () => {
        try {
          const taskStatus = await api.getTaskStatus(response.task_id)
          
          if (taskStatus.state === 'SUCCESS') {
            clearInterval(pollInterval)
            setUploadedFiles(prev => {
              const updated = [...prev]
              updated[index] = { 
                ...updated[index], 
                status: 'complete', 
                progress: 100 
              }
              return updated
            })
            toast.success('Analysis complete!')
          } else if (taskStatus.state === 'FAILURE') {
            clearInterval(pollInterval)
            throw new Error(taskStatus.error || 'Analysis failed')
          } else if (taskStatus.progress) {
            setUploadedFiles(prev => {
              const updated = [...prev]
              updated[index] = { 
                ...updated[index], 
                progress: taskStatus.progress 
              }
              return updated
            })
          }
          
          attempts++
          if (attempts >= maxAttempts) {
            clearInterval(pollInterval)
            throw new Error('Analysis timed out')
          }
        } catch (error) {
          clearInterval(pollInterval)
          throw error
        }
      }, 5000) // Poll every 5 seconds
      
    } catch (error) {
      const err = error as { message?: string }
      const errorMsg = err.message || 'Analysis failed'
      
      setUploadedFiles(prev => {
        const updated = [...prev]
        updated[index] = { 
          ...updated[index], 
          status: 'error', 
          error: errorMsg 
        }
        return updated
      })
      
      toast.error(errorMsg)
    }
  }

  const handleProcessAll = async () => {
    setIsProcessing(true)
    
    try {
      // Upload all pending/error files
      for (let i = 0; i < uploadedFiles.length; i++) {
        const file = uploadedFiles[i]
        
        if (file.status === 'pending' || file.status === 'error') {
          const fileId = await uploadFile(i)
          
          // Start analysis
          if (fileId) {
            await analyzeFile(i, fileId, `/uploads/${file.file.name}`)
          }
        }
      }
      
      toast.success('All files processed!')
    } catch {
      // Errors already handled in individual functions
    } finally {
      setIsProcessing(false)
    }
  }

  const handleClearAll = () => {
    setUploadedFiles([])
    toast.success('Cleared all files')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" label="Loading..." />
      </div>
    )
  }

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'complete': return 'success'
      case 'error': return 'error'
      case 'uploading':
      case 'analyzing': return 'info'
      default: return 'default'
    }
  }

  const getStatusLabel = (status: UploadedFile['status']) => {
    switch (status) {
      case 'pending': return 'Pending'
      case 'uploading': return 'Uploading...'
      case 'uploaded': return 'Uploaded'
      case 'analyzing': return 'Analyzing...'
      case 'complete': return 'Complete'
      case 'error': return 'Error'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Upload Audio Files 🎵</h1>
          <p className="text-gray-600 mt-1">Upload your audio files for AI-powered analysis</p>
        </div>

        {/* Upload Section */}
        <Card variant="bordered" className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileAudio size={24} />
              Select Files
            </CardTitle>
            <CardDescription>
              Drag and drop your audio files or click to browse
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FileDropzone
              onFilesSelected={handleFilesSelected}
              accept="audio/*"
              maxFiles={10}
              maxSize={50}
              multiple={true}
              disabled={isProcessing}
            />
          </CardContent>
        </Card>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <Card variant="bordered">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles size={24} />
                    Processing Queue
                  </CardTitle>
                  <CardDescription>
                    {uploadedFiles.filter(f => f.status === 'complete').length} of {uploadedFiles.length} files completed
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleClearAll}
                    disabled={isProcessing}
                  >
                    Clear All
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleProcessAll}
                    isLoading={isProcessing}
                    disabled={uploadedFiles.every(f => f.status === 'complete')}
                  >
                    Process All
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {file.file.name}
                        </h4>
                        <p className="text-xs text-gray-500 mt-1">
                          {(file.file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={getStatusColor(file.status)} size="sm">
                          {getStatusLabel(file.status)}
                        </Badge>
                        {file.status === 'complete' && <CheckCircle2 size={20} className="text-green-600" />}
                        {file.status === 'error' && <AlertCircle size={20} className="text-red-600" />}
                      </div>
                    </div>

                    {(file.status === 'uploading' || file.status === 'analyzing') && (
                      <ProgressBar
                        value={file.progress}
                        size="sm"
                        color={file.status === 'uploading' ? 'blue' : 'purple'}
                      />
                    )}

                    {file.error && (
                      <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                        {file.error}
                      </div>
                    )}

                    {file.status === 'complete' && file.taskId && (
                      <div className="mt-3 flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => router.push(`/library?taskId=${file.taskId}`)}
                        >
                          View Results
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
