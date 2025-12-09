/**
 * Evaluation service for API calls
 */

import { apiClient } from './api'
import type {
  EvaluationRequest,
  EvaluationInfo,
  StartEvaluationResponse,
} from '@/types/evaluation.types'
import type { ApiResponse } from '@/types/api.types'

export const evaluationService = {
  /**
   * Start a new evaluation
   */
  async startEvaluation(request: EvaluationRequest): Promise<StartEvaluationResponse> {
    const response = await apiClient.post<StartEvaluationResponse>(
      '/evaluations/start',
      request
    )

    return response as unknown as StartEvaluationResponse
  },

  /**
   * Get evaluation status
   */
  async getEvaluationStatus(evaluationId: string): Promise<EvaluationInfo> {
    const response = await apiClient.get<ApiResponse<EvaluationInfo>>(
      `/evaluations/${evaluationId}/status`
    )

    return (response as unknown as ApiResponse<EvaluationInfo>).data!
  },

  /**
   * Cancel an evaluation
   */
  async cancelEvaluation(evaluationId: string): Promise<void> {
    await apiClient.post(`/evaluations/${evaluationId}/cancel`)
  },

  /**
   * Import evaluation results from JSON file
   */
  async importEvaluationResults(file: File): Promise<StartEvaluationResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<StartEvaluationResponse>(
      '/evaluations/import',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response as unknown as StartEvaluationResponse
  },
}
