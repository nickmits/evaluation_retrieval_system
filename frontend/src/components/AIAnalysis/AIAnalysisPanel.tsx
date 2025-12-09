/**
 * AI Analysis panel with LangGraph agent integration - Streamlit-style (no WebSockets)
 */

import React, { useState, useEffect } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  TextField,
  Alert,
  Chip,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  CircularProgress,
} from '@mui/material'
import {
  Psychology as AIIcon,
  ExpandMore as ExpandIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'
import { analysisService } from '@/services/analysisService'
import { useAppStore } from '@/store/useAppStore'
import type { AnalysisResult } from '@/types/analysis.types'

interface AIAnalysisPanelProps {
  evaluationId: string
}

const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({ evaluationId }) => {
  const [isRunning, setIsRunning] = useState(false)
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState('Ready to analyze')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [query, setQuery] = useState(
    'Analyze the evaluation results and tell me which retrieval system performs best and why. What should I do to improve performance?'
  )
  const [openaiKey, setOpenaiKey] = useState('')

  const { setCurrentAnalysis } = useAppStore()
  const { enqueueSnackbar } = useSnackbar()

  // Poll for analysis status
  useEffect(() => {
    if (!analysisId || !isRunning) return

    const pollInterval = setInterval(async () => {
      try {
        const status = await analysisService.getAnalysisStatus(analysisId)

        // Update progress from status
        if (status.progress) {
          setProgress(status.progress.progress_percentage)
          setCurrentStep(status.progress.current_step || 'Processing...')
          if (status.progress.current_agent) {
            setCurrentAgent(status.progress.current_agent)
          }
        }

        if (status.status === 'completed') {
          setIsRunning(false)
          setProgress(100)
          setCurrentStep('Analysis completed!')
          enqueueSnackbar('AI analysis completed!', { variant: 'success' })
          clearInterval(pollInterval)
          loadAnalysisResults()
        } else if (status.status === 'failed') {
          setIsRunning(false)
          setCurrentStep('Analysis failed')
          enqueueSnackbar(status.error || 'Analysis failed', { variant: 'error' })
          clearInterval(pollInterval)
        }
      } catch (error) {
        console.error('Error polling analysis status:', error)
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(pollInterval)
  }, [analysisId, isRunning, enqueueSnackbar])

  const loadAnalysisResults = async () => {
    if (!analysisId) return

    try {
      const result = await analysisService.getAnalysisResults(analysisId)
      setAnalysisResult(result)
      setCurrentAnalysis(result)
    } catch (error) {
      enqueueSnackbar('Failed to load analysis results', { variant: 'error' })
    }
  }

  const startAnalysis = async () => {
    try {
      setIsRunning(true)
      setProgress(0)
      setCurrentStep('Starting AI analysis...')
      setAnalysisResult(null)

      const response = await analysisService.startAnalysis({
        evaluation_id: evaluationId,
        analysis_query: query,
        openai_api_key: openaiKey || undefined,
      })

      setAnalysisId(response.analysis_id)
      enqueueSnackbar('AI analysis started!', { variant: 'success' })
    } catch (error) {
      setIsRunning(false)
      enqueueSnackbar('Failed to start analysis', { variant: 'error' })
    }
  }

  const agentSteps = [
    { name: 'Metrics Analyzer', description: 'Analyzing metric scores...' },
    { name: 'Performance Analyzer', description: 'Evaluating performance patterns...' },
    { name: 'Recommendation Agent', description: 'Generating recommendations...' },
    { name: 'Report Generator', description: 'Synthesizing final report...' },
  ]

  return (
    <Card>
      <CardContent>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <AIIcon color="primary" />
          <Typography variant="h6">
            AI-Powered Analysis
          </Typography>
        </Stack>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Let AI agents analyze your evaluation results using LangGraph's multi-agent system
        </Typography>

        {!isRunning && !analysisResult && (
          <Box>
            <TextField
              label="Analysis Query"
              multiline
              rows={3}
              fullWidth
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              sx={{ mb: 2 }}
              helperText="Ask specific questions about the evaluation results"
            />

            <TextField
              label="OpenAI API Key (optional)"
              type="password"
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              helperText="Leave empty to use server-side key"
              fullWidth
              sx={{ mb: 2 }}
            />

            <Button
              variant="contained"
              fullWidth
              startIcon={<AIIcon />}
              onClick={startAnalysis}
            >
              Run AI Analysis
            </Button>
          </Box>
        )}

        {isRunning && (
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <Chip label={`${Math.round(progress)}%`} color="primary" size="small" />
            </Stack>

            <Typography variant="body2" color="text.secondary" gutterBottom>
              {currentStep}
            </Typography>

            <LinearProgress variant="determinate" value={progress} sx={{ mb: 2 }} />

            {currentAgent && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Current Agent: <strong>{currentAgent}</strong>
              </Alert>
            )}

            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Agent Progress:
              </Typography>
              {agentSteps.map((step, index) => (
                <Box key={step.name} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {progress >= (index + 1) * 25 ? (
                    <Chip label="✓" size="small" color="success" sx={{ mr: 1 }} />
                  ) : (
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                  )}
                  <Typography variant="body2">{step.name}</Typography>
                </Box>
              ))}
            </Box>
          </Box>
        )}

        {analysisResult && (
          <Box>
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="body2" fontWeight="bold">
                AI Analysis Complete!
              </Typography>
            </Alert>

            <Card variant="outlined" sx={{ mb: 2, bgcolor: 'background.default' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Final Report
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography
                  variant="body2"
                  sx={{ whiteSpace: 'pre-wrap' }}
                  dangerouslySetInnerHTML={{ __html: analysisResult.final_report.replace(/\n/g, '<br/>') }}
                />
              </CardContent>
            </Card>

            <Stack spacing={1}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandIcon />}>
                  <Typography fontWeight="bold">📊 Metrics Analysis</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography
                    variant="body2"
                    sx={{ whiteSpace: 'pre-wrap' }}
                    dangerouslySetInnerHTML={{ __html: analysisResult.metrics_analysis.replace(/\n/g, '<br/>') }}
                  />
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandIcon />}>
                  <Typography fontWeight="bold">🔍 Performance Insights</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography
                    variant="body2"
                    sx={{ whiteSpace: 'pre-wrap' }}
                    dangerouslySetInnerHTML={{ __html: analysisResult.performance_insights.replace(/\n/g, '<br/>') }}
                  />
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandIcon />}>
                  <Typography fontWeight="bold">💡 Recommendations</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography
                    variant="body2"
                    sx={{ whiteSpace: 'pre-wrap' }}
                    dangerouslySetInnerHTML={{ __html: analysisResult.recommendations.replace(/\n/g, '<br/>') }}
                  />
                </AccordionDetails>
              </Accordion>
            </Stack>

            <Button
              variant="outlined"
              fullWidth
              startIcon={<RefreshIcon />}
              sx={{ mt: 2 }}
              onClick={() => {
                setAnalysisResult(null)
                setAnalysisId(null)
                setProgress(0)
              }}
            >
              Run New Analysis
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default AIAnalysisPanel
