import { create } from 'zustand'

export type AppPhase = 'upload' | 'dashboard'
export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

export interface NlpTiming {
  totalTime: number
  avgTime: number
}

interface AppState {
  phase: AppPhase
  sessionId: string | null
  dbMode: boolean                // true when viewing data from DB without a session
  uploadStatus: UploadStatus
  uploadProgress: number
  uploadError: string | null
  agentPanelOpen: boolean
  nlpTiming: NlpTiming | null

  setPhase: (phase: AppPhase) => void
  setSessionId: (id: string) => void
  enterDbMode: () => void        // switch to dashboard from DB directly
  setUploadStatus: (status: UploadStatus) => void
  setUploadProgress: (pct: number) => void
  setUploadError: (error: string | null) => void
  openAgentPanel: () => void
  closeAgentPanel: () => void
  resetUpload: () => void
  setNlpTiming: (timing: NlpTiming) => void
}

export const useAppStore = create<AppState>((set) => ({
  phase: 'upload',
  sessionId: null,
  dbMode: false,
  uploadStatus: 'idle',
  uploadProgress: 0,
  uploadError: null,
  agentPanelOpen: false,
  nlpTiming: null,

  setPhase: (phase) => set({ phase }),
  setSessionId: (sessionId) => set({ sessionId }),
  enterDbMode: () => set({ phase: 'dashboard', dbMode: true, sessionId: null }),
  setUploadStatus: (uploadStatus) => set({ uploadStatus }),
  setUploadProgress: (uploadProgress) => set({ uploadProgress }),
  setUploadError: (uploadError) => set({ uploadError }),
  openAgentPanel: () => set({ agentPanelOpen: true }),
  closeAgentPanel: () => set({ agentPanelOpen: false }),
  resetUpload: () =>
    set({ uploadStatus: 'idle', uploadProgress: 0, uploadError: null }),
  setNlpTiming: (nlpTiming) => set({ nlpTiming }),
}))
