import { useState, type KeyboardEvent } from 'react'
import { useAgentStore } from '../../store/agentStore'

interface ChatInputProps {
  onSubmit: (question: string) => void
}

export function ChatInput({ onSubmit }: ChatInputProps) {
  const [value, setValue] = useState('')
  const { isLoading } = useAgentStore()

  const submit = () => {
    const question = value.trim()
    if (!question || isLoading) return
    setValue('')
    onSubmit(question)
  }

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="border-t border-gray-700/50 p-3">
      <div className="flex gap-2 items-end rounded-xl border border-gray-600/60 bg-gray-800 px-3 py-2 focus-within:border-indigo-500 transition-colors">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask about your data… (Enter to send)"
          disabled={isLoading}
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-200 placeholder-gray-500 focus:outline-none disabled:opacity-50 max-h-28 leading-relaxed"
          style={{ minHeight: '24px' }}
        />
        <button
          onClick={submit}
          disabled={!value.trim() || isLoading}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="h-4 w-4 rotate-90" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
          </svg>
        </button>
      </div>
      <p className="mt-1.5 text-center text-[10px] text-gray-600">
        Shift+Enter for new line
      </p>
    </div>
  )
}
