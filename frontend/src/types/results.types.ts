/**
 * Results-related types
 */

export interface MetricScores {
  faithfulness: number
  context_recall: number
  context_precision: number
  answer_relevancy: number
  factual_correctness: number
}

export interface SystemResult {
  system_name: string
  system_type: string
  metrics: MetricScores
  average_score: number
  initialization_time: number
  evaluation_time: number
  config: Record<string, unknown>
}

export interface EvaluationResults {
  evaluation_id: string
  document_id: string
  results: Record<string, SystemResult>
  best_system?: string
  best_average_score?: number
  completed_at: string
}

export type ExportFormat = 'json' | 'csv' | 'markdown'

export interface ExportRequest {
  evaluation_id: string
  format: ExportFormat
}

export interface ExportResponse {
  success: boolean
  data: string
  filename: string
  content_type: string
  message: string
}
