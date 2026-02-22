import { useEffect } from 'react'

interface ArtifactViewerProps {
  html: string
  onClose: () => void
}

export function ArtifactViewer({ html, onClose }: ArtifactViewerProps) {
  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div className="fixed inset-0 z-[60] flex flex-col bg-gray-950 animate-fade-in">
      {/* Toolbar */}
      <div className="flex h-12 shrink-0 items-center justify-between border-b border-gray-700/50 px-5">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-500/20">
            <svg className="h-3.5 w-3.5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path strokeLinecap="round" d="M3 9h18M9 21V9" />
            </svg>
          </div>
          <span className="text-sm font-medium text-gray-200">Visualization</span>
        </div>
        <button
          onClick={onClose}
          className="flex items-center gap-1.5 rounded-lg border border-gray-700/60 px-3 py-1.5 text-xs text-gray-400 hover:bg-gray-800 hover:text-gray-200 transition-colors"
        >
          <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          Close (Esc)
        </button>
      </div>

      {/* Full-screen iframe */}
      <iframe
        srcDoc={html}
        sandbox="allow-scripts"
        className="flex-1 w-full border-0"
        title="Visualization"
      />
    </div>
  )
}
