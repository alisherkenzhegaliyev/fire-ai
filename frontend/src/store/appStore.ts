import { create } from 'zustand'

export type AppPhase = 'upload' | 'dashboard'
export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

interface AppState {
  phase: AppPhase
  sessionId: string | null
  uploadStatus: UploadStatus
  uploadProgress: number
  uploadError: string | null
  agentPanelOpen: boolean

  setPhase: (phase: AppPhase) => void
  setSessionId: (id: string) => void
  setUploadStatus: (status: UploadStatus) => void
  setUploadProgress: (pct: number) => void
  setUploadError: (error: string | null) => void
  openAgentPanel: () => void
  closeAgentPanel: () => void
  resetUpload: () => void
}

export const useAppStore = create<AppState>((set) => ({
  phase: 'upload',
  sessionId: null,
  uploadStatus: 'idle',
  uploadProgress: 0,
  uploadError: null,
  agentPanelOpen: false,

  setPhase: (phase) => set({ phase }),
  setSessionId: (sessionId) => set({ sessionId }),
  setUploadStatus: (uploadStatus) => set({ uploadStatus }),
  setUploadProgress: (uploadProgress) => set({ uploadProgress }),
  setUploadError: (uploadError) => set({ uploadError }),
  openAgentPanel: () => set({ agentPanelOpen: true }),
  closeAgentPanel: () => set({ agentPanelOpen: false }),
  resetUpload: () =>
    set({ uploadStatus: 'idle', uploadProgress: 0, uploadError: null }),
}))
