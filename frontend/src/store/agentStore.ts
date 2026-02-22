import { create } from 'zustand'
import type { AgentChartPayload } from '../types/agent'

export interface ThinkingStep {
  type: 'tool_start' | 'tool_result'
  name: string
  args?: Record<string, unknown>
  preview?: string
  timestamp: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  chartData?: AgentChartPayload
  htmlArtifact?: string
  thinkingSteps?: ThinkingStep[]
  timestamp: number
}

interface AgentState {
  messages: ChatMessage[]
  thinkingSteps: ThinkingStep[]
  isLoading: boolean

  addMessage: (msg: ChatMessage) => void
  setLoading: (loading: boolean) => void
  clearMessages: () => void
  addThinkingStep: (step: ThinkingStep) => void
  clearThinkingSteps: () => void
}

export const useAgentStore = create<AgentState>((set) => ({
  messages: [],
  thinkingSteps: [],
  isLoading: false,

  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setLoading: (isLoading) => set({ isLoading }),
  clearMessages: () => set({ messages: [], thinkingSteps: [] }),
  addThinkingStep: (step) =>
    set((state) => ({ thinkingSteps: [...state.thinkingSteps, step] })),
  clearThinkingSteps: () => set({ thinkingSteps: [] }),
}))
