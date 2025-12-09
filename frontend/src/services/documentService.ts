/**
 * Document service for API calls
 */

import { apiClient } from './api'
import type { DocumentInfo, DocumentUploadResponse } from '@/types/document.types'
import type { ApiResponse } from '@/types/api.types'

export const documentService = {
  /**
   * Upload a document file
   */
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<DocumentUploadResponse>(
      '/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response as unknown as DocumentUploadResponse
  },

  /**
   * Get document information by ID
   */
  async getDocument(documentId: string): Promise<DocumentInfo> {
    const response = await apiClient.get<ApiResponse<DocumentInfo>>(
      `/documents/${documentId}`
    )

    return (response as unknown as ApiResponse<DocumentInfo>).data!
  },

  /**
   * Delete a document by ID
   */
  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/documents/${documentId}`)
  },
}
