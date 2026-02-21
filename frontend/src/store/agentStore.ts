import { create } from 'zustand'
import type { AgentChartPayload } from '../types/agent'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  chartData?: AgentChartPayload
  timestamp: number
}

interface AgentState {
  messages: ChatMessage[]
  isLoading: boolean

  addMessage: (msg: ChatMessage) => void
  setLoading: (loading: boolean) => void
  clearMessages: () => void
}

export const useAgentStore = create<AgentState>((set) => ({
  messages: [],
  isLoading: false,

  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setLoading: (isLoading) => set({ isLoading }),
  clearMessages: () => set({ messages: [] }),
}))
