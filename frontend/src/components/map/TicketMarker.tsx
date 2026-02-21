import { CircleMarker, Popup } from 'react-leaflet'
import { Badge } from '../shared/Badge'
import type { Ticket } from '../../types/ticket'

const SEGMENT_COLORS: Record<string, string> = {
  VIP: '#a855f7',
  Priority: '#f97316',
  Mass: '#3b82f6',
}

interface TicketMarkerProps {
  ticket: Ticket
  onClick: (ticket: Ticket) => void
}

export function TicketMarker({ ticket, onClick }: TicketMarkerProps) {
  if (ticket.latitude == null || ticket.longitude == null) return null

  return (
    <CircleMarker
      center={[ticket.latitude, ticket.longitude]}
      radius={6}
      pathOptions={{
        color: SEGMENT_COLORS[ticket.segment] ?? '#6366f1',
        fillColor: SEGMENT_COLORS[ticket.segment] ?? '#6366f1',
        fillOpacity: 0.7,
        weight: 1.5,
      }}
      eventHandlers={{ click: () => onClick(ticket) }}
    >
      <Popup>
        <div className="space-y-1 text-xs min-w-[180px]">
          <div className="flex gap-1 flex-wrap mb-1">
            <Badge value={ticket.segment} />
            <Badge value={ticket.requestType} />
          </div>
          <p className="text-gray-700 font-medium">{ticket.city}, {ticket.country}</p>
          <p className="text-gray-500">Priority: {ticket.priorityScore}/10</p>
          {ticket.assignedManagerName && (
            <p className="text-gray-600">Manager: {ticket.assignedManagerName}</p>
          )}
          <p className="text-gray-400 line-clamp-2 mt-1">{ticket.summary}</p>
        </div>
      </Popup>
    </CircleMarker>
  )
}
