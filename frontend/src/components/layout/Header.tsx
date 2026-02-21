import { useAppStore } from '../../store/appStore'

export function Header() {
  const { phase, agentPanelOpen, openAgentPanel, closeAgentPanel } = useAppStore()

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-gray-700/50 bg-gray-900/80 px-6 backdrop-blur">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
          <svg className="h-5 w-5 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M13.5 2.5l-8.25 14.25h6.75l-1.5 4.75 8.25-14.25h-6.75l1.5-4.75z" />
          </svg>
        </div>
        <div>
          <span className="text-sm font-semibold text-white tracking-wide">FIRE</span>
          <span className="ml-2 text-xs text-gray-400 hidden sm:inline">
            Freedom Intelligent Routing Engine
          </span>
        </div>
      </div>

      {phase === 'dashboard' && (
        <button
          onClick={agentPanelOpen ? closeAgentPanel : openAgentPanel}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
          {agentPanelOpen ? 'Close AI' : 'AI Analyze'}
        </button>
      )}
    </header>
  )
}
