import { useState } from 'react'
import clsx from 'clsx'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { AgentChart } from './AgentChart'
import { ArtifactViewer } from './ArtifactViewer'
import type { ChatMessage as ChatMessageType } from '../../store/agentStore'
import { formatTime } from '../../utils/formatters'

interface ChatMessageProps {
  message: ChatMessageType
}

/** Markdown renderer tuned for the dark chat bubble */
function MarkdownBody({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="text-base font-bold text-white mt-3 mb-1.5 first:mt-0">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-sm font-bold text-white mt-3 mb-1.5 first:mt-0">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wide mt-2.5 mb-1 first:mt-0">{children}</h3>
        ),
        p: ({ children }) => (
          <p className="text-sm text-gray-100 leading-relaxed mb-2 last:mb-0">{children}</p>
        ),
        ul: ({ children }) => (
          <ul className="space-y-1 mb-2 pl-1">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside space-y-1 mb-2 pl-1 text-sm text-gray-100">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="flex items-start gap-1.5 text-sm text-gray-100">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400" />
            <span>{children}</span>
          </li>
        ),
        strong: ({ children }) => (
          <strong className="font-semibold text-white">{children}</strong>
        ),
        em: ({ children }) => (
          <em className="italic text-gray-300">{children}</em>
        ),
        code: ({ children, className }) => {
          const isBlock = className?.startsWith('language-')
          if (isBlock) {
            return (
              <code className="block rounded-lg bg-gray-900/80 border border-gray-700/50 px-3 py-2 text-xs font-mono text-indigo-300 whitespace-pre-wrap my-2">
                {children}
              </code>
            )
          }
          return (
            <code className="rounded px-1 py-0.5 text-xs font-mono bg-gray-900/60 text-indigo-300">
              {children}
            </code>
          )
        },
        pre: ({ children }) => <>{children}</>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-indigo-500/60 pl-3 my-2 text-sm text-gray-300 italic">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-2 rounded-lg border border-gray-600/60">
            <table className="w-full text-xs">{children}</table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-gray-900/60">{children}</thead>
        ),
        th: ({ children }) => (
          <th className="px-3 py-2 text-left font-semibold text-gray-200 border-b border-gray-600/60">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-3 py-2 text-gray-100 border-b border-gray-600/40 last:border-0">
            {children}
          </td>
        ),
        hr: () => <hr className="border-gray-500/50 my-3" />,
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const [artifactOpen, setArtifactOpen] = useState(false)
  const [stepsOpen, setStepsOpen] = useState(false)
  const steps = message.thinkingSteps ?? []
  const toolCount = steps.filter((s) => s.type === 'tool_start').length

  return (
    <>
      <div className={clsx('flex gap-2.5', isUser ? 'flex-row-reverse' : 'flex-row')}>
        <div
          className={clsx(
            'flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold mt-0.5',
            isUser ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-300'
          )}
        >
          {isUser ? 'U' : 'AI'}
        </div>

        <div className={clsx('flex flex-col gap-1.5 max-w-[85%]', isUser ? 'items-end' : 'items-start')}>
          {/* Collapsed thinking steps toggle (assistant only) */}
          {!isUser && toolCount > 0 && (
            <button
              onClick={() => setStepsOpen((v) => !v)}
              className="flex items-center gap-1.5 text-[11px] text-gray-500 hover:text-gray-300 transition-colors px-1"
            >
              <svg
                className={clsx('h-3 w-3 transition-transform', stepsOpen && 'rotate-90')}
                viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
              {toolCount} tool call{toolCount !== 1 ? 's' : ''}
            </button>
          )}

          {/* Expanded steps */}
          {!isUser && stepsOpen && steps.length > 0 && (
            <div className="w-full rounded-xl border border-gray-700/40 bg-gray-800/60 px-3 py-2.5 flex flex-col gap-1.5 animate-fade-in">
              {steps.map((step, i) => {
                const isStart = step.type === 'tool_start'
                const argsStr = isStart && step.args && Object.keys(step.args).length > 0
                  ? Object.entries(step.args).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(', ')
                  : ''
                return (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <div className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded ${isStart ? 'bg-indigo-500/20' : 'bg-emerald-500/20'}`}>
                      {isStart ? (
                        <svg className="h-2.5 w-2.5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                        </svg>
                      ) : (
                        <svg className="h-2.5 w-2.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                        </svg>
                      )}
                    </div>
                    <div className="min-w-0 flex flex-col gap-0.5">
                      <div className="flex items-baseline gap-1.5 flex-wrap">
                        <span className={`font-mono font-semibold ${isStart ? 'text-indigo-300' : 'text-emerald-300'}`}>{step.name}</span>
                        {isStart && argsStr && <span className="text-gray-500 truncate max-w-[200px]">({argsStr})</span>}
                      </div>
                      {!isStart && step.preview && <span className="text-gray-400 truncate">{step.preview}</span>}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* Message bubble */}
          <div
            className={clsx(
              'rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed',
              isUser
                ? 'bg-indigo-600 text-white rounded-tr-sm'
                : 'bg-gray-700/80 text-gray-100 rounded-tl-sm'
            )}
          >
            {isUser ? (
              <span>{message.text}</span>
            ) : (
              <MarkdownBody content={message.text} />
            )}
          </div>

          {/* HTML artifact card */}
          {message.htmlArtifact && (
            <div className="w-full rounded-xl border border-gray-700/50 bg-gray-800/60 overflow-hidden">
              <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700/40 bg-gray-800/80">
                <div className="flex items-center gap-1.5">
                  <svg className="h-3.5 w-3.5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <path strokeLinecap="round" d="M3 9h18M9 21V9" />
                  </svg>
                  <span className="text-[11px] font-medium text-gray-400">Visualization</span>
                </div>
                <button
                  onClick={() => setArtifactOpen(true)}
                  className="flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] text-indigo-400 hover:bg-indigo-500/10 hover:text-indigo-300 transition-colors"
                >
                  <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
                  </svg>
                  Fullscreen
                </button>
              </div>
              <iframe
                srcDoc={message.htmlArtifact}
                sandbox="allow-scripts"
                className="w-full border-0"
                style={{ height: '300px' }}
                title="Chart preview"
              />
            </div>
          )}

          {/* Legacy recharts fallback */}
          {!message.htmlArtifact && message.chartData && (
            <AgentChart payload={message.chartData} />
          )}

          <span className="text-[10px] text-gray-600 px-1">{formatTime(message.timestamp)}</span>
        </div>
      </div>

      {artifactOpen && message.htmlArtifact && (
        <ArtifactViewer html={message.htmlArtifact} onClose={() => setArtifactOpen(false)} />
      )}
    </>
  )
}
