/**
 * Results importer component for loading previous evaluation results
 */

import React, { useState, useCallback } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  Stack,
  CircularProgress,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'
import { evaluationService } from '@/services/evaluationService'

interface ResultsImporterProps {
  onImportSuccess?: (evaluationId: string) => void
}

const ResultsImporter: React.FC<ResultsImporterProps> = ({ onImportSuccess }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [importedEvaluationId, setImportedEvaluationId] = useState<string | null>(null)

  const { enqueueSnackbar } = useSnackbar()

  const validateFile = (file: File): string | null => {
    if (!file.name.endsWith('.json')) {
      return 'Invalid file type. Only JSON files are allowed'
    }

    if (file.size > 50 * 1024 * 1024) {
      // 50 MB limit
      return 'File too large. Maximum size: 50 MB'
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
      setImportedEvaluationId(null)
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

  const handleImport = async () => {
    if (!selectedFile) return

    setIsImporting(true)

    try {
      const response = await evaluationService.importEvaluationResults(selectedFile)

      enqueueSnackbar(
        `Results imported successfully! ${response.message}`,
        { variant: 'success' }
      )

      setImportedEvaluationId(response.evaluation_id)
      onImportSuccess?.(response.evaluation_id)

      // Reset after success
      setTimeout(() => {
        setSelectedFile(null)
        setIsImporting(false)
      }, 1000)
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || 'Failed to import results'
      enqueueSnackbar(errorMessage, { variant: 'error' })
      setIsImporting(false)
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
          Import Previous Results
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Upload a JSON file with evaluation results to skip re-running evaluations
        </Typography>

        {importedEvaluationId ? (
          <Alert
            severity="success"
            icon={<SuccessIcon />}
            sx={{ mb: 2 }}
            onClose={() => setImportedEvaluationId(null)}
          >
            <Stack spacing={0.5}>
              <Typography variant="body2" fontWeight="bold">
                Results Imported Successfully!
              </Typography>
              <Typography variant="caption">
                Evaluation ID: {importedEvaluationId}
              </Typography>
              <Typography variant="caption">
                You can now run AI analysis on these results
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
                p: 3,
                textAlign: 'center',
                bgcolor: isDragging ? 'action.hover' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.light',
                  bgcolor: 'action.hover',
                },
              }}
              onClick={() => document.getElementById('json-file-input')?.click()}
            >
              <UploadIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="body1" gutterBottom>
                Drag and drop JSON file here
              </Typography>
              <Typography variant="body2" color="text.secondary">
                or click to browse
              </Typography>
              <Chip label="JSON" size="small" sx={{ mt: 2 }} />
            </Box>

            <input
              id="json-file-input"
              type="file"
              accept=".json"
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
                      Size: {formatFileSize(selectedFile.size)}
                    </Typography>
                  </Stack>
                </Alert>

                <Button
                  variant="contained"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={handleImport}
                  disabled={isImporting}
                  startIcon={isImporting ? <CircularProgress size={20} /> : <UploadIcon />}
                >
                  {isImporting ? 'Importing...' : 'Import Results'}
                </Button>
              </Box>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default ResultsImporter
