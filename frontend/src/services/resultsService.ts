/**
 * Results service for API calls
 */

import { apiClient } from './api'
import type { EvaluationResults, ExportFormat } from '@/types/results.types'
import type { ApiResponse } from '@/types/api.types'

export const resultsService = {
  /**
   * Get evaluation results
   */
  async getResults(evaluationId: string): Promise<EvaluationResults> {
    const response = await apiClient.get<ApiResponse<EvaluationResults>>(
      `/evaluations/${evaluationId}/results`
    )

    return (response as unknown as ApiResponse<EvaluationResults>).data!
  },

  /**
   * Export results in specified format
   */
  async exportResults(evaluationId: string, format: ExportFormat): Promise<Blob> {
    const response = await apiClient.get(
      `/results/export/${evaluationId}/${format}`,
      {
        responseType: 'blob',
      }
    )

    return response as unknown as Blob
  },
}
