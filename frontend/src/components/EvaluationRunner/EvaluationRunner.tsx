/**
 * Evaluation runner component - Streamlit-style (no WebSockets)
 */

import React, { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  CircularProgress,
  Stack,
} from '@mui/material'
import {
  PlayArrow as StartIcon,
  CheckCircle as CompleteIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'
import { evaluationService } from '@/services/evaluationService'
import { useAppStore } from '@/store/useAppStore'
import type { SystemSelection } from '@/types/evaluation.types'

interface EvaluationRunnerProps {
  documentId: string
  selectedSystems: SystemSelection[]
  onComplete?: (evaluationId: string) => void
}

const EvaluationRunner: React.FC<EvaluationRunnerProps> = ({
  documentId,
  selectedSystems,
  onComplete,
}) => {
  const [isRunning, setIsRunning] = useState(false)
  const [evaluationId, setEvaluationId] = useState<string | null>(null)
  const [statusMessage, setStatusMessage] = useState('Ready to start evaluation')
  const [isComplete, setIsComplete] = useState(false)

  const { setCurrentEvaluation } = useAppStore()
  const { enqueueSnackbar } = useSnackbar()

  // Check for ongoing evaluation on mount
  useEffect(() => {
    const checkOngoingEvaluation = async () => {
      const storedEvaluationId = localStorage.getItem('current_evaluation_id')
      if (storedEvaluationId) {
        try {
          const status = await evaluationService.getEvaluationStatus(storedEvaluationId)

          if (status.status === 'pending' || status.status === 'running') {
            // Resume tracking this evaluation
            setEvaluationId(storedEvaluationId)
            setIsRunning(true)
            setStatusMessage(status.message || 'Evaluation in progress...')
          } else if (status.status === 'completed') {
            // Evaluation completed while user was away
            setEvaluationId(storedEvaluationId)
            setIsComplete(true)
            setStatusMessage('Evaluation completed successfully!')
            localStorage.removeItem('current_evaluation_id')
          } else {
            // Failed or cancelled
            localStorage.removeItem('current_evaluation_id')
          }
        } catch (error) {
          // Evaluation not found or error
          localStorage.removeItem('current_evaluation_id')
        }
      }
    }

    checkOngoingEvaluation()
  }, [])

  // Poll for evaluation status
  useEffect(() => {
    if (!evaluationId || !isRunning) return

    const pollInterval = setInterval(async () => {
      try {
        const status = await evaluationService.getEvaluationStatus(evaluationId)

        setStatusMessage(status.message || 'Processing...')

        if (status.status === 'completed') {
          setIsRunning(false)
          setIsComplete(true)
          setStatusMessage('Evaluation completed successfully!')
          enqueueSnackbar('Evaluation completed!', { variant: 'success' })
          localStorage.removeItem('current_evaluation_id') // Clean up
          clearInterval(pollInterval)
          onComplete?.(evaluationId)
        } else if (status.status === 'failed') {
          setIsRunning(false)
          setStatusMessage('Evaluation failed')
          enqueueSnackbar(`Evaluation failed: ${status.error || 'Unknown error'}`, { variant: 'error' })
          localStorage.removeItem('current_evaluation_id') // Clean up
          clearInterval(pollInterval)
        }
      } catch (error) {
        console.error('Error polling status:', error)
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(pollInterval)
  }, [evaluationId, isRunning, enqueueSnackbar, onComplete])

  const handleStartEvaluation = async () => {
    if (selectedSystems.length === 0) {
      enqueueSnackbar('Please select at least one retrieval system', { variant: 'warning' })
      return
    }

    try {
      setIsRunning(true)
      setIsComplete(false)
      setStatusMessage('Starting evaluation...')

      const response = await evaluationService.startEvaluation({
        document_id: documentId,
        systems: selectedSystems,
        num_test_questions: 5,
        use_multihop: false,
      })

      setEvaluationId(response.evaluation_id)
      localStorage.setItem('current_evaluation_id', response.evaluation_id) // Store for persistence
      setCurrentEvaluation({
        evaluation_id: response.evaluation_id,
        document_id: documentId,
        status: 'running',
        created_at: new Date().toISOString(),
      })

      enqueueSnackbar('Evaluation started', { variant: 'info' })
      setStatusMessage('Evaluation in progress... This may take several minutes.')
    } catch (error: any) {
      setIsRunning(false)
      const errorMessage = error?.response?.data?.error || error.message || 'Failed to start evaluation'
      enqueueSnackbar(errorMessage, { variant: 'error' })
      setStatusMessage('Failed to start evaluation')
      console.error('Error starting evaluation:', error)
    }
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Run Evaluation
        </Typography>

        <Stack spacing={3}>
          {/* Status Display */}
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Status
            </Typography>
            <Alert
              severity={isComplete ? 'success' : isRunning ? 'info' : 'default'}
              icon={isComplete ? <CompleteIcon /> : isRunning ? <CircularProgress size={20} /> : undefined}
            >
              {statusMessage}
            </Alert>
          </Box>

          {/* Progress Indicator */}
          {isRunning && (
            <Box>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Evaluating {selectedSystems.length} system(s)... Please wait.
              </Typography>
              <LinearProgress />
            </Box>
          )}

          {/* Selected Systems */}
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Selected Systems ({selectedSystems.length})
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {selectedSystems.map((system) => (
                <Alert key={system.type} severity="info" sx={{ mb: 1 }}>
                  {system.name}
                </Alert>
              ))}
            </Stack>
          </Box>

          {/* Start Button */}
          <Button
            variant="contained"
            size="large"
            startIcon={<StartIcon />}
            onClick={handleStartEvaluation}
            disabled={isRunning || selectedSystems.length === 0}
            fullWidth
          >
            {isRunning ? 'Evaluation Running...' : 'Start Evaluation'}
          </Button>

          {isComplete && (
            <Alert severity="success">
              Evaluation completed! View results in the &quot;Results & Export&quot; tab.
            </Alert>
          )}
        </Stack>
      </CardContent>
    </Card>
  )
}

export default EvaluationRunner
