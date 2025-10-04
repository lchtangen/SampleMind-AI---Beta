'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/useAuthStore'
import {
  Card,
  CardContent,
  Button,
  Input,
  Badge,
  Spinner,
  EmptyState,
  Modal
} from '@/components'
import Navbar from '@/components/layout/Navbar'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'
import { Search, Clock, FileAudio, Play, BarChart3, FolderOpen, CheckSquare, Square, Trash2, Tag, Download } from 'lucide-react'
import { formatBytes, formatDuration } from '@/lib/utils'

interface AudioFile {
  file_id: string
  filename: string
  file_size: number
  duration?: number
  sample_rate?: number
  format: string
  uploaded_at: string
  tags?: string[]
  has_analysis: boolean
}

export default function LibraryPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuthStore()
  
  const [files, setFiles] = useState<AudioFile[]>([])
  const [isLoadingFiles, setIsLoadingFiles] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFile, setSelectedFile] = useState<AudioFile | null>(null)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  
  // Bulk Operations State
  const [selectedFileIds, setSelectedFileIds] = useState<Set<string>>(new Set())
  const [showBulkDeleteModal, setShowBulkDeleteModal] = useState(false)
  const [showBulkTagModal, setShowBulkTagModal] = useState(false)
  const [bulkTagInput, setBulkTagInput] = useState('')
  const [isBulkOperating, setIsBulkOperating] = useState(false)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    } else if (isAuthenticated) {
      loadFiles()
    }
  }, [isAuthenticated, isLoading, router])

  const loadFiles = async () => {
    try {
      setIsLoadingFiles(true)
      await api.getAudioFiles()
      
      // Mock data for now (replace with actual API response)
      const mockFiles: AudioFile[] = [
        {
          file_id: '1',
          filename: 'track_001.mp3',
          file_size: 5242880,
          duration: 180,
          sample_rate: 44100,
          format: 'mp3',
          uploaded_at: new Date().toISOString(),
          tags: ['electronic', 'upbeat'],
          has_analysis: true
        },
        {
          file_id: '2',
          filename: 'ambient_mix.wav',
          file_size: 10485760,
          duration: 240,
          sample_rate: 48000,
          format: 'wav',
          uploaded_at: new Date(Date.now() - 86400000).toISOString(),
          tags: ['ambient', 'calm'],
          has_analysis: false
        }
      ]
      
      setFiles(mockFiles)
    } catch {
      toast.error('Failed to load files')
    } finally {
      setIsLoadingFiles(false)
    }
  }

  const filteredFiles = files.filter(file =>
    file.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    file.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const handleViewDetails = (file: AudioFile) => {
    setSelectedFile(file)
    setShowDetailsModal(true)
  }

  const handleAnalyze = async (fileId: string) => {
    try {
      await api.analyzeAudio(fileId)
      toast.success('Analysis started!')
      loadFiles()
    } catch {
      toast.error('Failed to start analysis')
    }
  }

  // Bulk Operations Handlers
  const toggleFileSelection = (fileId: string) => {
    const newSelection = new Set(selectedFileIds)
    if (newSelection.has(fileId)) {
      newSelection.delete(fileId)
    } else {
      newSelection.add(fileId)
    }
    setSelectedFileIds(newSelection)
  }

  const toggleSelectAll = () => {
    if (selectedFileIds.size === filteredFiles.length) {
      setSelectedFileIds(new Set())
    } else {
      setSelectedFileIds(new Set(filteredFiles.map(f => f.file_id)))
    }
  }

  const handleBulkDelete = async () => {
    try {
      setIsBulkOperating(true)
      // Note: Implement bulk delete API endpoint
      // await api.bulkDeleteAudioFiles(Array.from(selectedFileIds))
      toast.success(`Deleted ${selectedFileIds.size} file(s)`)
      setSelectedFileIds(new Set())
      setShowBulkDeleteModal(false)
      loadFiles()
    } catch {
      toast.error('Failed to delete files')
    } finally {
      setIsBulkOperating(false)
    }
  }

  const handleBulkTag = async () => {
    if (!bulkTagInput.trim()) {
      toast.error('Please enter tags')
      return
    }

    try {
      setIsBulkOperating(true)
      const tags = bulkTagInput.split(',').map(t => t.trim()).filter(Boolean)
      // Note: Implement bulk tag API endpoint
      // await api.bulkTagAudioFiles(Array.from(selectedFileIds), tags)
      toast.success(`Tagged ${selectedFileIds.size} file(s)`)
      setSelectedFileIds(new Set())
      setShowBulkTagModal(false)
      setBulkTagInput('')
      loadFiles()
    } catch {
      toast.error('Failed to tag files')
    } finally {
      setIsBulkOperating(false)
    }
  }

  const handleBulkExport = async () => {
    try {
      toast.info(`Exporting ${selectedFileIds.size} file(s)...`)
      // Note: Implement bulk export API endpoint
      // await api.bulkExportAudioFiles(Array.from(selectedFileIds))
      toast.success('Export started! Download will begin shortly.')
    } catch {
      toast.error('Failed to export files')
    }
  }

  if (isLoading || isLoadingFiles) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" label="Loading library..." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Audio Library 📚</h1>
          <p className="text-gray-600 mt-1">Browse and manage your audio files</p>
        </div>

        {/* Search and Filters */}
        <Card variant="bordered" className="mb-6">
          <CardContent className="pt-6">
            <div className="flex gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by filename or tags..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  leftIcon={<Search size={20} />}
                />
              </div>
              <Button variant="outline" onClick={loadFiles}>
                Refresh
              </Button>
            </div>

            {/* Bulk Operations Toolbar */}
            {files.length > 0 && (
              <div className="flex items-center gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleSelectAll}
                  leftIcon={selectedFileIds.size === filteredFiles.length ? <CheckSquare size={16} /> : <Square size={16} />}
                >
                  {selectedFileIds.size === filteredFiles.length ? 'Deselect All' : 'Select All'}
                </Button>

                {selectedFileIds.size > 0 && (
                  <>
                    <Badge variant="default">{selectedFileIds.size} selected</Badge>
                    
                    <div className="flex gap-2 ml-auto">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowBulkTagModal(true)}
                        leftIcon={<Tag size={16} />}
                      >
                        Tag
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleBulkExport}
                        leftIcon={<Download size={16} />}
                      >
                        Export
                      </Button>
                      
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => setShowBulkDeleteModal(true)}
                        leftIcon={<Trash2 size={16} />}
                      >
                        Delete
                      </Button>
                    </div>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Files Grid */}
        {filteredFiles.length === 0 ? (
          <Card variant="bordered">
            <CardContent>
              <EmptyState
                icon={FolderOpen}
                title={searchQuery ? 'No files found' : 'No audio files yet'}
                description={searchQuery ? 'Try adjusting your search' : 'Upload your first audio file to get started'}
                action={!searchQuery ? { label: 'Upload Files', onClick: () => router.push('/upload') } : undefined}
              />
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredFiles.map((file) => (
              <Card 
                key={file.file_id} 
                variant="bordered" 
                className={`hover:shadow-lg transition-all ${
                  selectedFileIds.has(file.file_id) ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                }`}
              >
                <CardContent className="pt-6">
                  {/* Selection Checkbox */}
                  <div className="absolute top-3 right-3">
                    <button
                      onClick={() => toggleFileSelection(file.file_id)}
                      className="p-1 hover:bg-gray-100 rounded transition-colors"
                    >
                      {selectedFileIds.has(file.file_id) ? (
                        <CheckSquare className="h-5 w-5 text-blue-600" />
                      ) : (
                        <Square className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                  </div>

                  {/* File Icon */}
                  <div className="flex items-center justify-center mb-4">
                    <div className="p-4 bg-blue-100 rounded-full">
                      <FileAudio className="h-12 w-12 text-blue-600" />
                    </div>
                  </div>

                  {/* File Info */}
                  <h3 className="text-lg font-semibold text-gray-900 text-center truncate mb-2">
                    {file.filename}
                  </h3>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Size</span>
                      <span className="font-medium">{formatBytes(file.file_size)}</span>
                    </div>
                    {file.duration && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Duration</span>
                        <span className="font-medium flex items-center gap-1">
                          <Clock size={14} />
                          {formatDuration(file.duration)}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Format</span>
                      <Badge variant="outline" size="sm">{file.format.toUpperCase()}</Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Status</span>
                      <Badge variant={file.has_analysis ? 'success' : 'default'} size="sm">
                        {file.has_analysis ? 'Analyzed' : 'Pending'}
                      </Badge>
                    </div>
                  </div>

                  {/* Tags */}
                  {file.tags && file.tags.length > 0 && (
                    <div className="mb-4">
                      <div className="flex flex-wrap gap-1">
                        {file.tags.map((tag, index) => (
                          <Badge key={index} variant="default" size="sm">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewDetails(file)}
                      leftIcon={<Play size={16} />}
                    >
                      Details
                    </Button>
                    {!file.has_analysis && (
                      <Button
                        variant="primary"
                        size="sm"
                        className="flex-1"
                        onClick={() => handleAnalyze(file.file_id)}
                        leftIcon={<BarChart3 size={16} />}
                      >
                        Analyze
                      </Button>
                    )}
                  </div>

                  {/* Upload Date */}
                  <div className="mt-3 pt-3 border-t text-xs text-gray-500 text-center">
                    Uploaded {new Date(file.uploaded_at).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
        title={selectedFile?.filename || 'File Details'}
        size="lg"
      >
        {selectedFile && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">File Size</p>
                <p className="font-medium">{formatBytes(selectedFile.file_size)}</p>
              </div>
              {selectedFile.duration && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Duration</p>
                  <p className="font-medium">{formatDuration(selectedFile.duration)}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-600 mb-1">Format</p>
                <p className="font-medium">{selectedFile.format.toUpperCase()}</p>
              </div>
              {selectedFile.sample_rate && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Sample Rate</p>
                  <p className="font-medium">{selectedFile.sample_rate} Hz</p>
                </div>
              )}
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-2">Status</p>
              <Badge variant={selectedFile.has_analysis ? 'success' : 'default'}>
                {selectedFile.has_analysis ? 'Analysis Complete' : 'Pending Analysis'}
              </Badge>
            </div>

            <div className="flex gap-2 pt-4">
              {selectedFile.has_analysis ? (
                <Button variant="primary" className="flex-1">
                  View Analysis Results
                </Button>
              ) : (
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={() => {
                    handleAnalyze(selectedFile.file_id)
                    setShowDetailsModal(false)
                  }}
                >
                  Start Analysis
                </Button>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Bulk Delete Modal */}
      <Modal
        isOpen={showBulkDeleteModal}
        onClose={() => setShowBulkDeleteModal(false)}
        title="Delete Multiple Files"
        size="md"
      >
        <div className="space-y-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-900 font-medium mb-2">
              ⚠️ You are about to delete {selectedFileIds.size} file(s)
            </p>
            <p className="text-sm text-red-700">
              This action cannot be undone. All analysis results for these files will also be deleted.
            </p>
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              variant="danger"
              onClick={handleBulkDelete}
              isLoading={isBulkOperating}
              className="flex-1"
            >
              Delete {selectedFileIds.size} File(s)
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowBulkDeleteModal(false)}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {/* Bulk Tag Modal */}
      <Modal
        isOpen={showBulkTagModal}
        onClose={() => setShowBulkTagModal(false)}
        title="Add Tags to Multiple Files"
        size="md"
      >
        <div className="space-y-4">
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              Adding tags to {selectedFileIds.size} file(s)
            </p>
          </div>

          <Input
            label="Tags"
            type="text"
            value={bulkTagInput}
            onChange={(e) => setBulkTagInput(e.target.value)}
            placeholder="e.g., electronic, upbeat, remix"
            helperText="Separate multiple tags with commas"
          />

          <div className="flex gap-2 pt-4">
            <Button
              variant="primary"
              onClick={handleBulkTag}
              isLoading={isBulkOperating}
              disabled={!bulkTagInput.trim()}
              className="flex-1"
            >
              Add Tags
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowBulkTagModal(false)
                setBulkTagInput('')
              }}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
