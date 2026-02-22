import { useRef } from 'react'
import { useAgentStore } from '../store/agentStore'
import { useAppStore } from '../store/appStore'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export function useStreamingAgent() {
  const { addMessage, setLoading, addThinkingStep, clearThinkingSteps } = useAgentStore()
  const { sessionId } = useAppStore()
  const abortRef = useRef<AbortController | null>(null)

  const submit = async (question: string) => {
    // Cancel any in-flight request
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setLoading(true)
    clearThinkingSteps()

    try {
      const res = await fetch(`${BASE_URL}/api/agent/query/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId ?? null }),
        signal: controller.signal,
      })

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        // SSE lines are separated by \n\n; process complete events
        const parts = buffer.split('\n\n')
        buffer = parts.pop() ?? ''

        for (const part of parts) {
          const line = part.trim()
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6)
          let event: Record<string, unknown>
          try { event = JSON.parse(raw) } catch { continue }

          if (event.type === 'tool_start' || event.type === 'tool_result') {
            addThinkingStep({
              type: event.type as 'tool_start' | 'tool_result',
              name: String(event.name ?? ''),
              args: event.args as Record<string, unknown> | undefined,
              preview: event.preview as string | undefined,
              timestamp: Date.now(),
            })
          } else if (event.type === 'done') {
            // Grab the completed thinking steps before clearing
            const completedSteps = useAgentStore.getState().thinkingSteps
            clearThinkingSteps()
            addMessage({
              id: crypto.randomUUID(),
              role: 'assistant',
              text: String(event.answer ?? ''),
              htmlArtifact: event.html_artifact as string | undefined,
              thinkingSteps: completedSteps,
              timestamp: Date.now(),
            })
          } else if (event.type === 'error') {
            clearThinkingSteps()
            addMessage({
              id: crypto.randomUUID(),
              role: 'assistant',
              text: `Error: ${event.message}`,
              timestamp: Date.now(),
            })
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      clearThinkingSteps()
      addMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        text: 'Sorry, I could not reach the server. Please try again.',
        timestamp: Date.now(),
      })
    } finally {
      setLoading(false)
    }
  }

  return { submit }
}
