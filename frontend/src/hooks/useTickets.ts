import { useQuery } from '@tanstack/react-query'
import { fetchTickets } from '../api/tickets.api'
import { useAppStore } from '../store/appStore'

export function useTickets() {
  const { phase, sessionId } = useAppStore()

  return useQuery({
    queryKey: ['tickets', sessionId],
    queryFn: () => fetchTickets(sessionId!),
    enabled: phase === 'dashboard' && sessionId != null,
    staleTime: Infinity,
  })
}
