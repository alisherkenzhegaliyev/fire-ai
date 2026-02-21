import { Badge } from '../shared/Badge'
import type { Ticket } from '../../types/ticket'

interface AssignmentChainProps {
  ticket: Ticket | null
}

function ChainNode({
  label,
  title,
  subtitle,
  color,
}: {
  label: string
  title: string
  subtitle: string
  color: string
}) {
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${color}`}>{label}</div>
      <div className="rounded-xl border border-gray-700/50 bg-gray-800 px-4 py-3 text-center min-w-[120px]">
        <p className="text-sm font-semibold text-white truncate">{title}</p>
        <p className="text-xs text-gray-400 mt-0.5 truncate">{subtitle}</p>
      </div>
    </div>
  )
}

function Arrow() {
  return (
    <div className="flex items-center self-center mt-5">
      <div className="h-px w-8 bg-gray-600" />
      <svg className="h-3 w-3 text-gray-500" viewBox="0 0 12 12" fill="currentColor">
        <path d="M6.75 3.5L10.25 6l-3.5 2.5V3.5z" />
        <path d="M1.75 3.5L5.25 6l-3.5 2.5V3.5z" />
      </svg>
    </div>
  )
}

export function AssignmentChain({ ticket }: AssignmentChainProps) {
  if (!ticket) {
    return (
      <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 p-5">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-4">
          Assignment Chain
        </p>
        <p className="text-sm text-gray-500 text-center py-4">
          Click a ticket row to view its assignment chain
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 p-5">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">
          Assignment Chain
        </p>
        <div className="flex gap-1.5">
          <Badge value={ticket.segment} />
          <Badge value={ticket.requestType} />
          <Badge value={ticket.language} />
        </div>
      </div>

      <div className="flex items-start gap-1 overflow-x-auto pb-1">
        <ChainNode
          label="Customer"
          title={`${ticket.city || 'Unknown'}, ${ticket.country || '—'}`}
          subtitle={ticket.customerGuid.slice(0, 8) + '…'}
          color="bg-gray-600/50 text-gray-300"
        />
        <Arrow />
        <ChainNode
          label="AI Analysis"
          title={ticket.requestType}
          subtitle={`Priority ${ticket.priorityScore}/10 · ${ticket.sentiment}`}
          color="bg-indigo-500/20 text-indigo-300"
        />
        <Arrow />
        <ChainNode
          label="Office"
          title={ticket.assignedOfficeName ?? 'Unassigned'}
          subtitle="Nearest office"
          color="bg-amber-500/20 text-amber-300"
        />
        <Arrow />
        <ChainNode
          label="Manager"
          title={ticket.assignedManagerName ?? 'Unassigned'}
          subtitle="Round-robin assigned"
          color="bg-emerald-500/20 text-emerald-300"
        />
      </div>

      {ticket.summary && (
        <div className="mt-4 rounded-lg bg-gray-900/50 border border-gray-700/30 p-3">
          <p className="text-xs font-medium text-gray-400 mb-1">AI Summary</p>
          <p className="text-sm text-gray-300">{ticket.summary}</p>
        </div>
      )}
    </div>
  )
}
