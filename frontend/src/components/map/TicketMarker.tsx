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
        fillOpacity: 0.8,
        weight: 1.5,
      }}
      eventHandlers={{ click: () => onClick(ticket) }}
    >
      <Popup>
        <div className="space-y-1 text-xs min-w-[190px]">
          <div className="flex gap-1 flex-wrap mb-1.5">
            <Badge value={ticket.segment} />
            <Badge value={ticket.requestType} />
          </div>
          <p className="font-semibold text-gray-800">{ticket.city}, {ticket.country}</p>
          <p className="text-gray-600">
            Priority: <span className="font-medium text-gray-800">{ticket.priorityScore}/10</span>
          </p>
          {ticket.assignedManagerName && (
            <p className="text-gray-600">
              Manager: <span className="font-medium text-gray-800">{ticket.assignedManagerName}</span>
            </p>
          )}
          {ticket.summary && (
            <p className="text-gray-600 leading-snug mt-1 line-clamp-3">{ticket.summary}</p>
          )}
        </div>
      </Popup>
    </CircleMarker>
  )
}
