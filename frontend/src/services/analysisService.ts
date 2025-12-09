/**
 * AI Analysis service for API calls
 */

import { apiClient } from './api'
import type {
  AnalysisRequest,
  AnalysisInfo,
  AnalysisResult,
  StartAnalysisResponse,
} from '@/types/analysis.types'
import type { ApiResponse } from '@/types/api.types'

export const analysisService = {
  /**
   * Start a new AI analysis
   */
  async startAnalysis(request: AnalysisRequest): Promise<StartAnalysisResponse> {
    const response = await apiClient.post<StartAnalysisResponse>(
      '/analysis/start',
      request
    )

    return response as unknown as StartAnalysisResponse
  },

  /**
   * Get analysis status
   */
  async getAnalysisStatus(analysisId: string): Promise<AnalysisInfo> {
    const response = await apiClient.get<ApiResponse<AnalysisInfo>>(
      `/analysis/${analysisId}/status`
    )

    return (response as unknown as ApiResponse<AnalysisInfo>).data!
  },

  /**
   * Get analysis results
   */
  async getAnalysisResults(analysisId: string): Promise<AnalysisResult> {
    const response = await apiClient.get<ApiResponse<AnalysisResult>>(
      `/analysis/${analysisId}/results`
    )

    return (response as unknown as ApiResponse<AnalysisResult>).data!
  },
}
