/**
 * Document uploader component with drag-and-drop support
 */

import React, { useState, useCallback } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  Chip,
  Stack,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'
import { documentService } from '@/services/documentService'
import { useAppStore } from '@/store/useAppStore'
import type { DocumentInfo } from '@/types/document.types'

const ALLOWED_FILE_TYPES = ['pdf', 'txt', 'docx']
const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100 MB

interface DocumentUploaderProps {
  onUploadSuccess?: (document: DocumentInfo) => void
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const { currentDocument, setCurrentDocument } = useAppStore()
  const { enqueueSnackbar } = useSnackbar()

  const validateFile = (file: File): string | null => {
    const fileExtension = file.name.split('.').pop()?.toLowerCase()

    if (!fileExtension || !ALLOWED_FILE_TYPES.includes(fileExtension)) {
      return `Invalid file type. Allowed types: ${ALLOWED_FILE_TYPES.join(', ')}`
    }

    if (file.size > MAX_FILE_SIZE) {
      return `File too large. Maximum size: ${MAX_FILE_SIZE / (1024 * 1024)} MB`
    }

    return null
  }

  const handleFileSelect = useCallback(
    (file: File) => {
      const error = validateFile(file)
      if (error) {
        enqueueSnackbar(error, { variant: 'error' })
        return
      }

      setSelectedFile(file)
    },
    [enqueueSnackbar]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const file = e.dataTransfer.files[0]
      if (file) {
        handleFileSelect(file)
      }
    },
    [handleFileSelect]
  )

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        handleFileSelect(file)
      }
    },
    [handleFileSelect]
  )

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Simulate progress (since we don't have real upload progress from axios)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 200)

      const response = await documentService.uploadDocument(selectedFile)

      clearInterval(progressInterval)
      setUploadProgress(100)

      const documentInfo: DocumentInfo = {
        document_id: response.document_id,
        filename: response.filename,
        file_size: response.file_size,
        file_type: response.file_type,
        file_path: response.file_path,
        uploaded_at: response.uploaded_at,
      }

      setCurrentDocument(documentInfo)
      enqueueSnackbar('Document uploaded successfully!', { variant: 'success' })
      onUploadSuccess?.(documentInfo)

      // Reset after success
      setTimeout(() => {
        setSelectedFile(null)
        setIsUploading(false)
        setUploadProgress(0)
      }, 1000)
    } catch (error) {
      enqueueSnackbar('Failed to upload document', { variant: 'error' })
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Upload Document
        </Typography>

        {currentDocument ? (
          <Alert
            severity="success"
            icon={<SuccessIcon />}
            sx={{ mb: 2 }}
            onClose={() => setCurrentDocument(null)}
          >
            <Stack spacing={0.5}>
              <Typography variant="body2" fontWeight="bold">
                Document Uploaded: {currentDocument.filename}
              </Typography>
              <Typography variant="caption">
                Size: {formatFileSize(currentDocument.file_size)} | Type:{' '}
                {currentDocument.file_type.toUpperCase()}
              </Typography>
            </Stack>
          </Alert>
        ) : (
          <Box>
            <Box
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              sx={{
                border: 2,
                borderStyle: 'dashed',
                borderColor: isDragging ? 'primary.main' : 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                bgcolor: isDragging ? 'action.hover' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.light',
                  bgcolor: 'action.hover',
                },
              }}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Drag and drop your document here
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                or click to browse
              </Typography>
              <Stack direction="row" spacing={1} justifyContent="center" sx={{ mt: 2 }}>
                {ALLOWED_FILE_TYPES.map((type) => (
                  <Chip key={type} label={type.toUpperCase()} size="small" />
                ))}
              </Stack>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Maximum file size: {MAX_FILE_SIZE / (1024 * 1024)} MB
              </Typography>
            </Box>

            <input
              id="file-input"
              type="file"
              accept=".pdf,.txt,.docx"
              onChange={handleFileInputChange}
              style={{ display: 'none' }}
            />

            {selectedFile && (
              <Box sx={{ mt: 2 }}>
                <Alert severity="info" icon={<FileIcon />}>
                  <Stack spacing={0.5}>
                    <Typography variant="body2" fontWeight="bold">
                      Selected: {selectedFile.name}
                    </Typography>
                    <Typography variant="caption">
                      Size: {formatFileSize(selectedFile.size)} | Type:{' '}
                      {selectedFile.name.split('.').pop()?.toUpperCase()}
                    </Typography>
                  </Stack>
                </Alert>

                {isUploading && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      Uploading... {uploadProgress}%
                    </Typography>
                  </Box>
                )}

                <Button
                  variant="contained"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={handleUpload}
                  disabled={isUploading}
                >
                  {isUploading ? 'Uploading...' : 'Upload Document'}
                </Button>
              </Box>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default DocumentUploader
