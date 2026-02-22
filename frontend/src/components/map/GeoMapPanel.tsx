import { useMemo } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import { TicketMarker } from './TicketMarker'
import { OfficeMarker } from './OfficeMarker'
import type { Ticket } from '../../types/ticket'

// Known office locations for Astana and Almaty
const OFFICES = [
  { name: 'Astana Office', address: 'Astana, Kazakhstan', lat: 51.1801, lng: 71.446 },
  { name: 'Almaty Office', address: 'Almaty, Kazakhstan', lat: 43.238, lng: 76.889 },
]

// Geographic center of Kazakhstan — used as fallback when no ticket coords available
const KZ_CENTER: [number, number] = [48.0, 68.0]
const KZ_ZOOM = 5

interface GeoMapPanelProps {
  tickets: Ticket[]
  onTicketSelect?: (ticket: Ticket) => void
}

export function GeoMapPanel({ tickets, onTicketSelect }: GeoMapPanelProps) {
  const mappableTickets = useMemo(
    () => tickets.filter((t) => t.latitude != null && t.longitude != null),
    [tickets]
  )

  return (
    <div className="rounded-xl border border-gray-700/50 bg-gray-800/40 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700/50 flex items-center justify-between">
        <p className="text-sm font-semibold text-white">Geographic Distribution</p>
        <p className="text-xs text-gray-400">{mappableTickets.length} tickets mapped</p>
      </div>
      <div className="h-[520px]">
        <MapContainer
          center={KZ_CENTER}
          zoom={KZ_ZOOM}
          minZoom={4}
          style={{ height: '100%', width: '100%', background: '#111827' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
          {OFFICES.map((office) => (
            <OfficeMarker key={office.name} office={office} />
          ))}
          {mappableTickets.map((ticket) => (
            <TicketMarker
              key={ticket.id}
              ticket={ticket}
              onClick={onTicketSelect ?? (() => {})}
            />
          ))}
        </MapContainer>
      </div>
    </div>
  )
}
