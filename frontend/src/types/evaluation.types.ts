/**
 * Evaluation-related types
 */

export type EvaluationStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export type SystemType = 'simple_recursive' | 'simple_semantic' | 'advanced_recursive' | 'advanced_semantic' | 'parent_document' | 'advanced_parent_document'

export interface EmbeddingConfig {
  provider: 'openai' | 'cohere' | 'huggingface'
  model: string
  dimensions?: number
}

export interface RetrievalConfig {
  base_k: number
  bm25_k: number
  multi_query_k: number
  final_k: number
}

export interface EnsembleWeights {
  bm25_weight: number
  vector_weight: number
  multi_query_weight: number
  reranking_weight: number
}

export interface SystemConfig {
  chunk_size?: number
  chunk_overlap?: number
  threshold_type?: string
  threshold_amount?: number
  parent_chunk_size?: number
  parent_chunk_overlap?: number
  child_chunk_size?: number
  child_chunk_overlap?: number
  embedding_config?: EmbeddingConfig
  retrieval_config?: RetrievalConfig
  ensemble_weights?: EnsembleWeights
}

export interface SystemSelection {
  name: string
  type: SystemType
  config: SystemConfig
}

export interface EvaluationRequest {
  document_id: string
  systems: SystemSelection[]
  num_test_questions: number
  use_multihop: boolean
  openai_api_key?: string
  cohere_api_key?: string
}

export interface EvaluationProgress {
  current_system?: string
  total_systems: number
  completed_systems: number
  current_step: string
  progress_percentage: number
}

export interface EvaluationInfo {
  evaluation_id: string
  document_id: string
  status: EvaluationStatus
  systems: SystemSelection[]
  num_test_questions: number
  progress?: EvaluationProgress
  created_at: string
  started_at?: string
  completed_at?: string
  error?: string
}

export interface StartEvaluationResponse {
  success: boolean
  evaluation_id: string
  message: string
}
