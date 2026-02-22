import { useQuery } from '@tanstack/react-query'
import { fetchTickets } from '../api/tickets.api'
import { fetchDbTickets } from '../api/db.api'
import { useAppStore } from '../store/appStore'

export function useTickets() {
  const { phase, sessionId, dbMode } = useAppStore()

  return useQuery({
    queryKey: ['tickets', dbMode ? '__db__' : sessionId],
    queryFn: () => (dbMode ? fetchDbTickets() : fetchTickets(sessionId!)),
    enabled: phase === 'dashboard' && (dbMode || sessionId != null),
    staleTime: Infinity,
  })
}
