import client from './client'
import type { UploadResponse } from '../types/upload'

export async function uploadCSV(
  file: File,
  onProgress?: (percentage: number) => void
): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await client.post<UploadResponse>('/api/upload', formData, {
    // Do NOT set Content-Type manually — Axios sets it with the correct multipart boundary
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(pct)
      }
    },
  })

  return response.data
}
