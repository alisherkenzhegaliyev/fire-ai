import { useMutation } from '@tanstack/react-query'
import { sendAgentQuery } from '../api/agent.api'
import { useAgentStore } from '../store/agentStore'
import { useAppStore } from '../store/appStore'
import type { AgentQueryRequest } from '../types/agent'

export function useAgentQuery() {
  const { addMessage, setLoading } = useAgentStore()
  const { sessionId } = useAppStore()

  return useMutation({
    mutationFn: (question: string) => {
      const payload: AgentQueryRequest = { question, sessionId: sessionId! }
      return sendAgentQuery(payload)
    },
    onMutate: () => {
      setLoading(true)
    },
    onSuccess: (data) => {
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        text: data.answer,
        chartData: data.chartData,
        timestamp: Date.now(),
      })
    },
    onSettled: () => {
      setLoading(false)
    },
  })
}
