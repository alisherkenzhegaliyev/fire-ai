import clsx from 'clsx'
import { AgentChart } from './AgentChart'
import type { ChatMessage as ChatMessageType } from '../../store/agentStore'
import { formatTime } from '../../utils/formatters'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={clsx('flex gap-2.5', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div
        className={clsx(
          'flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold mt-0.5',
          isUser ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300'
        )}
      >
        {isUser ? 'U' : 'AI'}
      </div>

      <div className={clsx('flex flex-col gap-1 max-w-[85%]', isUser ? 'items-end' : 'items-start')}>
        <div
          className={clsx(
            'rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed',
            isUser
              ? 'bg-indigo-600 text-white rounded-tr-sm'
              : 'bg-gray-700/80 text-gray-100 rounded-tl-sm'
          )}
        >
          {message.text}
        </div>

        {message.chartData && <AgentChart payload={message.chartData} />}

        <span className="text-[10px] text-gray-600 px-1">{formatTime(message.timestamp)}</span>
      </div>
    </div>
  )
}
