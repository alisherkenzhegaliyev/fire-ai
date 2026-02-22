import { useEffect, useRef } from 'react'
import { ChatMessage } from './ChatMessage'
import { ThinkingProcess } from './ThinkingProcess'
import { useAgentStore } from '../../store/agentStore'

interface ChatMessagesProps {
  onSubmit: (question: string) => void
}

const SUGGESTIONS = [
  'Show request type distribution by city',
  'Which managers have the highest workload?',
  'Show sentiment breakdown by segment',
]

export function ChatMessages({ onSubmit }: ChatMessagesProps) {
  const { messages, isLoading, thinkingSteps } = useAgentStore()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 px-6 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/15">
          <svg className="h-6 w-6 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-300">Ask anything about your data</p>
          <p className="text-xs text-gray-500 mt-1">
            Try: "Show distribution by city" or "Which office has most VIP tickets?"
          </p>
        </div>
        <div className="mt-2 space-y-1.5 w-full">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => onSubmit(suggestion)}
              disabled={isLoading}
              className="w-full rounded-lg bg-gray-700/50 border border-gray-600/40 px-3 py-2 text-xs text-gray-400 text-left hover:bg-gray-700 hover:text-gray-200 hover:border-gray-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              "{suggestion}"
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}
      {isLoading && (
        <ThinkingProcess steps={thinkingSteps} isLoading={isLoading} />
      )}
      <div ref={bottomRef} />
    </div>
  )
}
