/**
 * AI Analysis-related types
 */

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface AnalysisRequest {
  evaluation_id: string
  analysis_query: string
  openai_api_key?: string
}

export interface AnalysisProgress {
  current_agent?: string
  total_agents: number
  completed_agents: number
  current_step: string
  progress_percentage: number
}

export interface AnalysisInfo {
  analysis_id: string
  evaluation_id: string
  status: AnalysisStatus
  query: string
  progress?: AnalysisProgress
  created_at: string
  started_at?: string
  completed_at?: string
  error?: string
}

export interface AnalysisResult {
  analysis_id: string
  evaluation_id: string
  query: string
  metrics_analysis: string
  performance_insights: string
  recommendations: string
  final_report: string
  messages: string[]
  completed_at: string
}

export interface StartAnalysisResponse {
  success: boolean
  analysis_id: string
  message: string
}
