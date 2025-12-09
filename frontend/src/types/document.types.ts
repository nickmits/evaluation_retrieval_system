/**
 * Document-related types
 */

export interface DocumentInfo {
  document_id: string
  filename: string
  file_size: number
  file_type: string
  file_path: string
  uploaded_at: string
}

export interface DocumentUploadResponse {
  success: boolean
  document_id: string
  filename: string
  file_size: number
  file_type: string
  file_path: string
  uploaded_at: string
  message: string
}
