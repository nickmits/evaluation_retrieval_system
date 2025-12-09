/**
 * Results visualization component with charts and tables
 */

import React, { useEffect, useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Grid,
  Chip,
  Button,
  Stack,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Download as DownloadIcon,
  Star as BestIcon,
} from '@mui/icons-material'
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { useSnackbar } from 'notistack'
import { resultsService } from '@/services/resultsService'
import { useAppStore } from '@/store/useAppStore'
import type { EvaluationResults, ExportFormat } from '@/types/results.types'

interface ResultsVisualizationProps {
  evaluationId: string
}

const ResultsVisualization: React.FC<ResultsVisualizationProps> = ({ evaluationId }) => {
  const [results, setResults] = useState<EvaluationResults | null>(null)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  const { setCurrentResults } = useAppStore()
  const { enqueueSnackbar } = useSnackbar()

  useEffect(() => {
    loadResults()
  }, [evaluationId])

  const loadResults = async () => {
    try {
      setLoading(true)
      const data = await resultsService.getResults(evaluationId)
      setResults(data)
      setCurrentResults(data)
    } catch (error) {
      enqueueSnackbar('Failed to load results', { variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format: ExportFormat) => {
    try {
      setExporting(true)
      const blob = await resultsService.exportResults(evaluationId, format)

      // Download file
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `evaluation_results_${evaluationId}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      enqueueSnackbar(`Results exported as ${format.toUpperCase()}`, { variant: 'success' })
    } catch (error) {
      enqueueSnackbar('Failed to export results', { variant: 'error' })
    } finally {
      setExporting(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress />
          <Typography variant="body2" sx={{ mt: 2 }}>
            Loading results...
          </Typography>
        </CardContent>
      </Card>
    )
  }

  if (!results) {
    return (
      <Alert severity="error">
        Failed to load evaluation results
      </Alert>
    )
  }

  // Prepare data for charts
  const systemNames = Object.keys(results.results)
  const metricNames = ['faithfulness', 'context_recall', 'context_precision', 'answer_relevancy', 'factual_correctness']

  // Radar chart data
  const radarData = metricNames.map((metric) => {
    const dataPoint: any = { metric: metric.replace('_', ' ') }
    systemNames.forEach((systemName) => {
      const systemResult = results.results[systemName]
      dataPoint[systemName] = systemResult.metrics[metric as keyof typeof systemResult.metrics]
    })
    return dataPoint
  })

  // Bar chart data
  const barData = systemNames.map((systemName) => ({
    name: systemName,
    average: results.results[systemName].average_score,
  }))

  const colors = ['#1976d2', '#9c27b0', '#2e7d32', '#ed6c02']

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">
              Evaluation Results
            </Typography>
            <Stack direction="row" spacing={1}>
              <Button
                size="small"
                startIcon={<DownloadIcon />}
                onClick={() => handleExport('json')}
                disabled={exporting}
              >
                JSON
              </Button>
              <Button
                size="small"
                startIcon={<DownloadIcon />}
                onClick={() => handleExport('csv')}
                disabled={exporting}
              >
                CSV
              </Button>
              <Button
                size="small"
                startIcon={<DownloadIcon />}
                onClick={() => handleExport('markdown')}
                disabled={exporting}
              >
                Markdown
              </Button>
            </Stack>
          </Stack>

          {results.best_system && (
            <Alert severity="success" icon={<BestIcon />}>
              Best System: <strong>{results.best_system}</strong> with average score of{' '}
              <strong>{results.best_average_score?.toFixed(3)}</strong>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Summary Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Summary Metrics
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>System</strong></TableCell>
                  <TableCell align="right"><strong>Average</strong></TableCell>
                  <TableCell align="right"><strong>Faithfulness</strong></TableCell>
                  <TableCell align="right"><strong>Context Recall</strong></TableCell>
                  <TableCell align="right"><strong>Context Precision</strong></TableCell>
                  <TableCell align="right"><strong>Answer Relevancy</strong></TableCell>
                  <TableCell align="right"><strong>Factual Correctness</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {systemNames.map((systemName) => {
                  const system = results.results[systemName]
                  const isBest = systemName === results.best_system
                  return (
                    <TableRow key={systemName} sx={{ bgcolor: isBest ? 'success.light' : undefined }}>
                      <TableCell>
                        {systemName} {isBest && <Chip label="Best" size="small" color="success" sx={{ ml: 1 }} />}
                      </TableCell>
                      <TableCell align="right"><strong>{system.average_score.toFixed(3)}</strong></TableCell>
                      <TableCell align="right">{system.metrics.faithfulness.toFixed(3)}</TableCell>
                      <TableCell align="right">{system.metrics.context_recall.toFixed(3)}</TableCell>
                      <TableCell align="right">{system.metrics.context_precision.toFixed(3)}</TableCell>
                      <TableCell align="right">{system.metrics.answer_relevancy.toFixed(3)}</TableCell>
                      <TableCell align="right">{system.metrics.factual_correctness.toFixed(3)}</TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Average Score Comparison
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="average" fill="#1976d2" name="Average Score" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Radar Chart Comparison
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis angle={90} domain={[0, 1]} />
                  {systemNames.map((systemName, index) => (
                    <Radar
                      key={systemName}
                      name={systemName}
                      dataKey={systemName}
                      stroke={colors[index % colors.length]}
                      fill={colors[index % colors.length]}
                      fillOpacity={0.3}
                    />
                  ))}
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default ResultsVisualization
