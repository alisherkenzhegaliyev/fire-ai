import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAppStore } from '../../store/appStore'
import { fetchNlpSettings, updateNlpSettings } from '../../api/settings.api'

function SettingsPanel() {
  const queryClient = useQueryClient()
  const panelRef = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)

  const { data: settings } = useQuery({
    queryKey: ['nlp-settings'],
    queryFn: fetchNlpSettings,
  })

  const mutation = useMutation({
    mutationFn: ({ modelId, concurrency }: { modelId: string; concurrency: number }) =>
      updateNlpSettings(modelId, concurrency),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['nlp-settings'] }),
  })

  useEffect(() => {
    if (!open) return
    function handleClick(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  return (
    <div className="relative" ref={panelRef}>
      <button
        onClick={() => setOpen(o => !o)}
        className={`flex h-8 w-8 items-center justify-center rounded-lg transition-colors ${
          open ? 'bg-gray-700 text-white' : 'text-gray-400 hover:bg-gray-700/50 hover:text-white'
        }`}
        title="Ollama Settings"
      >
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 010-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </button>

      {open && settings && (
        <div className="absolute right-0 top-10 z-50 w-52 rounded-lg border border-gray-700 bg-gray-800 p-3 shadow-xl">
          <p className="mb-3 text-xs font-semibold text-gray-300 uppercase tracking-wider">Ollama</p>

          <label className="mb-1 block text-xs text-gray-400">Model</label>
          <select
            value={settings.modelId}
            onChange={e =>
              mutation.mutate({ modelId: e.target.value, concurrency: settings.concurrency })
            }
            className="mb-3 w-full rounded border border-gray-600 bg-gray-900 px-2 py-1.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
          >
            {settings.availableModels.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>

          <label className="mb-1 block text-xs text-gray-400">Parallel Requests</label>
          <select
            value={settings.concurrency}
            onChange={e =>
              mutation.mutate({ modelId: settings.modelId, concurrency: Number(e.target.value) })
            }
            className="w-full rounded border border-gray-600 bg-gray-900 px-2 py-1.5 text-xs text-white focus:border-indigo-500 focus:outline-none"
          >
            {settings.availableConcurrency.map(n => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>

          {mutation.isPending && (
            <p className="mt-2 text-xs text-indigo-400">Saving…</p>
          )}
          {mutation.isSuccess && (
            <p className="mt-2 text-xs text-green-400">Saved</p>
          )}
        </div>
      )}
    </div>
  )
}

export function Header() {
  const { agentPanelOpen, openAgentPanel, closeAgentPanel } = useAppStore()

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

      <div className="flex items-center gap-2">
        <SettingsPanel />

        <button
          onClick={agentPanelOpen ? closeAgentPanel : openAgentPanel}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
          {agentPanelOpen ? 'Close AI' : 'AI Analyze'}
        </button>
      </div>
    </header>
  )
}
