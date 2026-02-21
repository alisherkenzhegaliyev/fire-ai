export interface UploadResponse {
  sessionId: string
  ticketCount: number
  managerCount: number
  status: 'success' | 'partial' | 'failed'
  message?: string
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}
