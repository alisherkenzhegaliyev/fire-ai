import type { ThinkingStep } from '../../store/agentStore'

function formatArgs(args?: Record<string, unknown>): string {
  if (!args || Object.keys(args).length === 0) return ''
  return Object.entries(args)
    .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
    .join(', ')
}

interface StepRowProps {
  step: ThinkingStep
  index: number
}

function StepRow({ step, index }: StepRowProps) {
  const isStart = step.type === 'tool_start'
  const argsStr = isStart ? formatArgs(step.args) : ''

  return (
    <div
      className="flex items-start gap-2 text-xs animate-fade-in"
      style={{ animationDelay: `${index * 60}ms`, animationFillMode: 'both' }}
    >
      {/* Icon badge */}
      <div
        className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded ${
          isStart ? 'bg-indigo-500/20' : 'bg-emerald-500/20'
        }`}
      >
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

      {/* Content */}
      <div className="min-w-0 flex flex-col gap-0.5">
        <div className="flex items-baseline gap-1.5 flex-wrap">
          <span className={`font-mono font-semibold ${isStart ? 'text-indigo-300' : 'text-emerald-300'}`}>
            {step.name}
          </span>
          {isStart && argsStr && (
            <span className="text-gray-500 truncate max-w-[220px]">({argsStr})</span>
          )}
        </div>
        {!isStart && step.preview && (
          <span className="text-gray-400 truncate">{step.preview}</span>
        )}
      </div>
    </div>
  )
}

interface ThinkingProcessProps {
  steps: ThinkingStep[]
  isLoading: boolean
}

export function ThinkingProcess({ steps, isLoading }: ThinkingProcessProps) {
  return (
    <div className="flex gap-2.5">
      {/* Avatar */}
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gray-700 text-xs font-bold text-gray-300 mt-0.5">
        AI
      </div>

      {/* Bubble */}
      <div className="rounded-2xl rounded-tl-sm bg-gray-700/80 px-4 py-3 flex flex-col gap-2 max-w-[85%]">
        {/* Header row */}
        <div className="flex items-center gap-2">
          {isLoading && (
            <span className="flex gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '300ms' }} />
            </span>
          )}
          <span className="text-xs font-medium text-gray-400">
            {steps.length === 0 ? 'Thinking…' : isLoading ? 'Reasoning…' : 'Done'}
          </span>
        </div>

        {/* Step list */}
        {steps.length > 0 && (
          <div className="flex flex-col gap-1.5 border-l border-gray-600/50 pl-2.5">
            {steps.map((step, i) => (
              <StepRow key={i} step={step} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
