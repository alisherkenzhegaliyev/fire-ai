import { useEffect } from 'react'
import { Badge } from '../shared/Badge'
import type { Ticket } from '../../types/ticket'

interface TicketModalProps {
  ticket: Ticket
  onClose: () => void
}

export function TicketModal({ ticket, onClose }: TicketModalProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-lg mx-4 rounded-2xl border border-gray-700/60 bg-gray-900 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-white">Original Ticket</span>
            <Badge value={ticket.requestType} />
            <Badge value={ticket.sentiment} />
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-gray-400 hover:text-white hover:bg-gray-700/60 transition-colors"
          >
            <svg className="h-4 w-4" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" d="M3 3l10 10M13 3L3 13" />
            </svg>
          </button>
        </div>

        {/* Meta row */}
        <div className="flex flex-wrap gap-x-5 gap-y-1 px-5 py-3 border-b border-gray-700/30 text-xs text-gray-400">
          <span>Priority <span className="font-mono text-amber-300">{ticket.priorityScore}/10</span></span>
          <span>Lang <span className="text-gray-200">{ticket.language}</span></span>
          {ticket.inferTimeMs > 0 && (
            <span>AI inference <span className="font-mono text-purple-300">{(ticket.inferTimeMs / 1000).toFixed(2)}s</span></span>
          )}
          {ticket.city && <span>City <span className="text-gray-200">{ticket.city}</span></span>}
          {ticket.assignedManagerName && (
            <span>Manager <span className="text-gray-200">{ticket.assignedManagerName}</span></span>
          )}
          {ticket.assignedOfficeName && (
            <span>Office <span className="text-gray-200">{ticket.assignedOfficeName}</span></span>
          )}
        </div>

        {/* Description */}
        <div className="px-5 py-4">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Description</p>
          <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto">
            {ticket.description || <span className="text-gray-500 italic">No description provided.</span>}
          </p>
        </div>

        {/* AI Summary */}
        {ticket.summary && (
          <div className="px-5 pb-4">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">AI Summary</p>
            <p className="text-sm text-gray-300 leading-relaxed">{ticket.summary}</p>
          </div>
        )}

      </div>
    </div>
  )
}
