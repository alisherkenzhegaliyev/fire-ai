import { useState, useCallback } from 'react'
import { DropZone } from './DropZone'
import { UploadProgress } from './UploadProgress'
import { UploadSuccess } from './UploadSuccess'
import { ErrorBanner } from '../shared/ErrorBanner'
import { uploadCSV } from '../../api/upload.api'
import { useAppStore } from '../../store/appStore'

export function UploadScreen() {
  const {
    uploadStatus,
    uploadProgress,
    uploadError,
    setUploadStatus,
    setUploadProgress,
    setUploadError,
    setSessionId,
    setPhase,
    resetUpload,
  } = useAppStore()

  const [fileName, setFileName] = useState('')
  const [successData, setSuccessData] = useState<{ ticketCount: number; managerCount: number } | null>(null)

  const handleFile = useCallback(
    async (file: File) => {
      setFileName(file.name)
      setUploadStatus('uploading')
      setUploadError(null)
      setUploadProgress(0)

      try {
        const result = await uploadCSV(file, setUploadProgress)
        setSessionId(result.sessionId)
        setSuccessData({ ticketCount: result.ticketCount, managerCount: result.managerCount })
        setUploadStatus('success')

        setTimeout(() => {
          setPhase('dashboard')
        }, 1800)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Upload failed'
        setUploadError(message)
        setUploadStatus('error')
      }
    },
    [setUploadStatus, setUploadProgress, setUploadError, setSessionId, setPhase]
  )

  return (
    <div className="flex h-full flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg space-y-8">
        {/* Title */}
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-white">
            Upload Ticket Data
          </h1>
          <p className="text-sm text-gray-400">
            Upload your CSV file containing tickets, managers, and business units.
            The system will analyze and assign each request automatically.
          </p>
        </div>

        {/* Main content area */}
        <div className="rounded-2xl border border-gray-700/50 bg-gray-800/40 p-8">
          {uploadStatus === 'idle' || uploadStatus === 'error' ? (
            <div className="space-y-4">
              <DropZone onFile={handleFile} disabled={uploadStatus === 'uploading'} />
              {uploadStatus === 'error' && uploadError && (
                <ErrorBanner
                  message={uploadError}
                  onDismiss={resetUpload}
                />
              )}
            </div>
          ) : uploadStatus === 'uploading' ? (
            <div className="flex items-center justify-center py-4">
              <UploadProgress percentage={uploadProgress} fileName={fileName} />
            </div>
          ) : uploadStatus === 'success' && successData ? (
            <div className="flex items-center justify-center py-4">
              <UploadSuccess
                ticketCount={successData.ticketCount}
                managerCount={successData.managerCount}
              />
            </div>
          ) : null}
        </div>

        {/* Feature hints */}
        {(uploadStatus === 'idle' || uploadStatus === 'error') && (
          <div className="grid grid-cols-3 gap-4">
            {[
              { icon: '🧠', label: 'AI Analysis', desc: 'NLP classifies each request' },
              { icon: '📍', label: 'Geo Routing', desc: 'Assigned to nearest office' },
              { icon: '⚖️', label: 'Load Balance', desc: 'Round-robin distribution' },
            ].map((item) => (
              <div key={item.label} className="rounded-xl bg-gray-800/60 border border-gray-700/40 p-3 text-center">
                <div className="text-2xl mb-1">{item.icon}</div>
                <p className="text-xs font-medium text-gray-300">{item.label}</p>
                <p className="text-xs text-gray-500 mt-0.5">{item.desc}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
