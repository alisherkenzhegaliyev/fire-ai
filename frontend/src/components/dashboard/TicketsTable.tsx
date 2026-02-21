import { useState } from 'react'
import { Badge } from '../shared/Badge'
import type { Ticket } from '../../types/ticket'

const PAGE_SIZE = 20

interface TicketsTableProps {
  tickets: Ticket[]
  selectedId: string | null
  onSelect: (ticket: Ticket) => void
}

export function TicketsTable({ tickets, selectedId, onSelect }: TicketsTableProps) {
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')

  const filtered = tickets.filter(
    (t) =>
      t.description.toLowerCase().includes(search.toLowerCase()) ||
      t.city.toLowerCase().includes(search.toLowerCase()) ||
      (t.assignedManagerName ?? '').toLowerCase().includes(search.toLowerCase())
  )

  const pageCount = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700/50">
        <p className="text-sm font-semibold text-white">Tickets ({filtered.length})</p>
        <input
          type="text"
          placeholder="Search tickets…"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0) }}
          className="rounded-lg bg-gray-700 border border-gray-600 px-3 py-1.5 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-indigo-500 w-48"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700/50 text-xs text-gray-400 uppercase tracking-wider">
              <th className="px-4 py-2.5 text-left font-medium">Segment</th>
              <th className="px-4 py-2.5 text-left font-medium">Type</th>
              <th className="px-4 py-2.5 text-left font-medium">Sentiment</th>
              <th className="px-4 py-2.5 text-left font-medium">Lang</th>
              <th className="px-4 py-2.5 text-left font-medium">Priority</th>
              <th className="px-4 py-2.5 text-left font-medium">City</th>
              <th className="px-4 py-2.5 text-left font-medium">Office</th>
              <th className="px-4 py-2.5 text-left font-medium">Manager</th>
            </tr>
          </thead>
          <tbody>
            {paginated.map((ticket) => (
              <tr
                key={ticket.id}
                onClick={() => onSelect(ticket)}
                className={`border-b border-gray-700/30 cursor-pointer transition-colors hover:bg-gray-700/40 ${
                  selectedId === ticket.id ? 'bg-indigo-500/10' : ''
                }`}
              >
                <td className="px-4 py-2.5">
                  <Badge value={ticket.segment} />
                </td>
                <td className="px-4 py-2.5">
                  <Badge value={ticket.requestType} />
                </td>
                <td className="px-4 py-2.5">
                  <Badge value={ticket.sentiment} />
                </td>
                <td className="px-4 py-2.5">
                  <Badge value={ticket.language} />
                </td>
                <td className="px-4 py-2.5">
                  <span className="font-mono text-amber-300">{ticket.priorityScore}/10</span>
                </td>
                <td className="px-4 py-2.5 text-gray-300">{ticket.city || '—'}</td>
                <td className="px-4 py-2.5 text-gray-300 truncate max-w-[120px]">
                  {ticket.assignedOfficeName ?? <span className="text-gray-600">—</span>}
                </td>
                <td className="px-4 py-2.5 text-gray-300 truncate max-w-[140px]">
                  {ticket.assignedManagerName ?? <span className="text-gray-600">—</span>}
                </td>
              </tr>
            ))}
            {paginated.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-sm text-gray-500">
                  No tickets found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {pageCount > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-700/50">
          <p className="text-xs text-gray-400">
            Page {page + 1} of {pageCount}
          </p>
          <div className="flex gap-1.5">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="rounded px-2 py-1 text-xs text-gray-400 hover:text-white disabled:opacity-30 hover:bg-gray-700 transition-colors"
            >
              ← Prev
            </button>
            <button
              disabled={page >= pageCount - 1}
              onClick={() => setPage((p) => p + 1)}
              className="rounded px-2 py-1 text-xs text-gray-400 hover:text-white disabled:opacity-30 hover:bg-gray-700 transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
