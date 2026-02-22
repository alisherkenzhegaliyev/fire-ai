import { useQuery } from '@tanstack/react-query'
import { fetchAnalytics } from '../api/analytics.api'
import { fetchDbAnalytics } from '../api/db.api'
import { useAppStore } from '../store/appStore'

export function useAnalytics() {
  const { phase, sessionId, dbMode } = useAppStore()

  return useQuery({
    queryKey: ['analytics', dbMode ? '__db__' : sessionId],
    queryFn: () => (dbMode ? fetchDbAnalytics() : fetchAnalytics(sessionId!)),
    enabled: phase === 'dashboard' && (dbMode || sessionId != null),
    staleTime: Infinity,
  })
}
