import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

interface Office {
  name: string
  address: string
  lat: number
  lng: number
  ticketCount?: number
}

interface OfficeMarkerProps {
  office: Office
}

const officeIcon = L.divIcon({
  html: `<div style="
    background: #6366f1;
    border: 2px solid #818cf8;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    width: 20px;
    height: 20px;
  "></div>`,
  className: '',
  iconSize: [20, 20],
  iconAnchor: [10, 20],
  popupAnchor: [0, -20],
})

export function OfficeMarker({ office }: OfficeMarkerProps) {
  return (
    <Marker position={[office.lat, office.lng]} icon={officeIcon}>
      <Popup>
        <div className="text-xs space-y-1 min-w-[150px]">
          <p className="font-semibold text-gray-800">{office.name}</p>
          <p className="text-gray-500">{office.address}</p>
          {office.ticketCount != null && (
            <p className="text-indigo-600 font-medium">{office.ticketCount} tickets assigned</p>
          )}
        </div>
      </Popup>
    </Marker>
  )
}
